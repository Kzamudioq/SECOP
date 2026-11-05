import io

import numpy as np
import pandas as pd
import pytest

from secop import analisis as an
from secop import descarga
from secop.cli import main
from secop.limpieza import a_numero, limpiar, normalizar_categoria, utilizables

from sintetico import SEMBRADOS, generar


@pytest.fixture(scope="module")
def datos():
    crudo = generar()
    df, cal = limpiar(crudo, hoy="2024-07-15")
    return crudo, df, cal


def test_montos():
    assert a_numero("17897916") == 17897916
    assert a_numero("$ 1.234.567,89") == pytest.approx(1234567.89)
    assert a_numero("1,234,567.5") == pytest.approx(1234567.5)
    assert np.isnan(a_numero("No Definido"))  # vacío, nunca 0
    assert np.isnan(a_numero(None))


def test_categorias_se_unifican():
    s = normalizar_categoria(pd.Series(["terminado", "Terminado", "Terminado ", "defensa", "No Definido"]))
    assert s.iloc[:3].nunique() == 1
    assert s.iloc[3] == "Defensa"
    assert pd.isna(s.iloc[4])


def test_limpieza_y_calidad(datos):
    crudo, df, cal = datos
    assert cal.duplicados_eliminados == 30
    assert df["id_contrato"].is_unique
    # se queda la versión más reciente
    assert (df.set_index("id_contrato").loc[crudo["id_contrato"].iloc[100:130], "estado_contrato"] == "Cerrado").all()
    assert set(df["sector"].dropna()) >= {"Defensa"} and "defensa" not in set(df["sector"].dropna())
    assert cal.problemas["q_valor_invalido"] >= 2
    assert cal.problemas["q_fecha_firma_invalida"] >= 1
    assert cal.problemas["q_fin_antes_inicio"] >= 1
    assert len(utilizables(df)) == len(df) - (df["q_valor_invalido"] | df["q_fecha_firma_invalida"] | df["q_valor_implausible"]).sum()
    assert np.isnan(df.loc[5, "valor_del_contrato"]) or df["valor_del_contrato"].isna().sum() >= 1


def test_valores_implausibles_no_inflan_totales(datos):
    crudo, df, cal = datos
    fila = df.set_index("id_contrato").loc[SEMBRADOS["digitacion"]]
    assert fila["q_valor_implausible"]
    assert SEMBRADOS["digitacion"] not in set(utilizables(df)["id_contrato"])
    assert an.resumen(df)["valor_total"] < 1e13  # sin el error, el total es del orden real
    assert 1 <= cal.problemas["q_valor_implausible"] <= 3
    assert an.alertas(df).set_index("id_contrato").loc[SEMBRADOS["digitacion"], "valor_atipico"]


def test_estacionalidad_y_veda(datos):
    _, df, _ = datos
    e = an.estacionalidad(df)
    assert e.attrs["anios"] == [2021, 2022, 2023]
    assert e.loc[1, "pct_promedio"] > 15  # enero sembrado x3
    g = an.efecto_ley_garantias(df).set_index("veda")
    assert g.loc["Presidencial 2022", "razon"] > 1.5  # adelanto sembrado antes de la veda
    m = an.serie_mensual(df)
    assert m.loc[pd.Period("2022-03"), "pct_directa"] < m.loc[pd.Period("2021-03"), "pct_directa"] / 2


def test_concentracion(datos):
    _, df, _ = datos
    c = an.concentracion_entidades(df).set_index("entidad")
    assert c.loc["ENTIDAD 07", "nivel"] == "alta"
    assert c["hhi"].idxmax() == "ENTIDAD 07"
    assert an.hhi(pd.Series([1, 1, 1, 1])) == pytest.approx(2500)


def test_alertas_encuentran_lo_sembrado(datos):
    _, df, _ = datos
    a = an.alertas(df).set_index("id_contrato")
    assert a.loc[SEMBRADOS["atipico"], "valor_atipico"]
    assert a.loc[SEMBRADOS["pagado"], "pagado_supera_valor"]
    assert a.loc[SEMBRADOS["adicion"], "adicion_mayor_50"]
    assert a["valor_atipico"].sum() / len(utilizables(df)) < 0.01  # no marca medio dataset


def test_personas_naturales_enmascaradas(datos):
    _, df, _ = datos
    t = an.top_proveedores(df, n=200)
    assert not t["proveedor"].str.startswith("PERSONA").any()


def test_descarga_pagina_y_filtra_en_servidor():
    filas = generar(300)[["id_contrato", "nombre_entidad", "fecha_de_firma", "valor_del_contrato"]]

    class Resp:
        def __init__(self, t): self.status_code, self.text = 200, t

    class Sesion:
        def __init__(self): self.llamadas = []

        def get(self, url, params, headers, timeout):
            self.llamadas.append(params)
            o, n = params["$offset"], params["$limit"]
            buf = io.StringIO()
            filas.iloc[o:o + n].to_csv(buf, index=False)
            return Resp(buf.getvalue())

    s = Sesion()
    df = descarga.descargar(lote=120, session=s, verbose=False)
    assert len(df) == len(filas) == 730
    assert [p["$offset"] for p in s.llamadas] == [0, 120, 240, 360, 480, 600, 720]
    w = s.llamadas[0]["$where"]
    assert "fecha_de_firma >= '2021-01-01T00:00:00'" in w and "Distrito Capital de Bogotá" in w
    assert s.llamadas[0]["$order"] == ":id"
    assert "n_mero_de_cuenta" not in s.llamadas[0]["$select"]  # sin datos bancarios ni personales
    assert "O''Brien" in descarga.construir_where("O'Brien", None, None)


def test_informe_completo(datos, tmp_path):
    crudo, _, _ = datos
    p = tmp_path / "crudo.parquet"
    descarga.guardar(crudo, p)
    main(["analizar", "--datos", str(p), "--salida", str(tmp_path / "out"), "--alcance", "Prueba"])
    out = tmp_path / "out"
    figs = sorted(f.name for f in (out / "figuras").glob("*.png"))
    assert len(figs) == 7, figs
    md = (out / "informe.md").read_text()
    assert "Ley de Garantías" in md and "Concentración" in md and "red" not in md.lower().split()
    assert (out / "tablas" / "secop_resultados.xlsx").exists()
