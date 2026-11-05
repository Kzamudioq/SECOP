"""Datos falsos con la misma forma que devuelve la API (todo texto) y problemas conocidos sembrados."""
from __future__ import annotations

import numpy as np
import pandas as pd

SECTORES = ["Transporte", "Salud y Protección Social", "Educación Nacional", "defensa", "Defensa",
            "Tecnologías de la Información y las Comunicaciones", "Cultura", "Hacienda y Crédito Público"]
MODALIDADES = {"Contratación directa": 0.62, "Mínima cuantía": 0.12, "Selección Abreviada de Menor Cuantía": 0.08,
               "Contratación régimen especial": 0.10, "Licitación pública": 0.04, "Concurso de méritos abierto": 0.04}
TIPOS = {"Contratación directa": "Prestación de servicios", "Mínima cuantía": "Suministros",
         "Selección Abreviada de Menor Cuantía": "Compraventa", "Contratación régimen especial": "Otro",
         "Licitación pública": "Obra", "Concurso de méritos abierto": "Interventoría"}
ESCALA = {"Contratación directa": 7.5, "Mínima cuantía": 7.0, "Selección Abreviada de Menor Cuantía": 8.2,
          "Contratación régimen especial": 8.0, "Licitación pública": 9.6, "Concurso de méritos abierto": 8.9}

SEMBRADOS = {"atipico": "CO1.PCCNTR.ATIPICO", "pagado": "CO1.PCCNTR.PAGADO", "adicion": "CO1.PCCNTR.ADICION"}


def generar(n: int = 6000, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # fechas: pico en enero, adelanto de directa antes de la veda de 2022, casi nada durante la veda
    dias = pd.date_range("2021-01-01", "2024-06-30", freq="D")
    peso = np.ones(len(dias))
    peso[dias.month == 1] *= 3.0
    peso[dias.month == 12] *= 0.6
    peso = peso / peso.sum()
    firmas = pd.DatetimeIndex(rng.choice(dias, n, p=peso))
    mods = rng.choice(list(MODALIDADES), n, p=list(MODALIDADES.values()))
    en_veda = (firmas >= "2022-01-29") & (firmas <= "2022-06-19")
    mods = np.where(en_veda & (mods == "Contratación directa") & (rng.random(n) < 0.9), "Mínima cuantía", mods)
    extra = 400  # adelanto: contratos directos firmados del 1 al 28 de enero de 2022
    firmas = firmas.append(pd.DatetimeIndex(rng.choice(pd.date_range("2022-01-01", "2022-01-28"), extra)))
    mods = np.concatenate([mods, np.repeat("Contratación directa", extra)])
    n = len(firmas)

    entidades = [f"ENTIDAD {i:02d}" for i in range(40)]
    ent = rng.choice(entidades, n)
    ent_sector = {e: SECTORES[i % len(SECTORES)] for i, e in enumerate(entidades)}
    natural = (mods == "Contratación directa") & (rng.random(n) < 0.8)
    docs_nat = rng.integers(10_000_000, 1_100_000_000, 3000)
    docs_jur = rng.integers(800_000_000, 999_999_999, 300)
    doc = np.where(natural, rng.choice(docs_nat, n), rng.choice(docs_jur, n)).astype(str)
    ent_dominada = ent == "ENTIDAD 07"  # un proveedor se lleva casi todo
    doc = np.where(ent_dominada & ~natural & (rng.random(n) < 0.9), "900123456", doc)
    valor = 10 ** rng.normal([ESCALA[m] for m in mods], 0.35)
    inicio = firmas + pd.to_timedelta(rng.integers(0, 15, n), unit="D")
    fin = inicio + pd.to_timedelta(rng.integers(30, 365, n), unit="D")

    df = pd.DataFrame({
        "id_contrato": [f"CO1.PCCNTR.{i}" for i in range(n)],
        "proceso_de_compra": [f"CO1.BDOS.{i}" for i in range(n)],
        "nombre_entidad": [e.lower() if i % 17 == 0 else e for i, e in enumerate(ent)],
        "nit_entidad": [str(800_000_000 + entidades.index(e)) for e in ent],
        "departamento": "Distrito Capital de Bogotá",
        "orden": np.where(np.isin(ent, entidades[:10]), "Territorial", "Nacional"),
        "sector": [ent_sector[e] for e in ent],
        "estado_contrato": rng.choice(["terminado", "Terminado", "En ejecución", "Cerrado", "Modificado"], n),
        "tipo_de_contrato": [TIPOS[m] for m in mods],
        "modalidad_de_contratacion": mods,
        "fecha_de_firma": firmas.strftime("%Y-%m-%dT00:00:00.000"),
        "fecha_de_inicio_del_contrato": inicio.strftime("%Y-%m-%dT00:00:00.000"),
        "fecha_de_fin_del_contrato": fin.strftime("%Y-%m-%dT00:00:00.000"),
        "tipodocproveedor": np.where(natural, "Cédula de Ciudadanía", "NIT"),
        "documento_proveedor": doc,
        "proveedor_adjudicado": np.where(natural, "PERSONA " + pd.Series(doc).str[-4:], "EMPRESA " + pd.Series(doc).str[-4:] + " SAS"),
        "es_pyme": rng.choice(["Si", "No"], n, p=[0.55, 0.45]),
        "valor_del_contrato": np.round(valor).astype(int).astype(str),
        "valor_pagado": np.round(valor * rng.uniform(0, 1, n)).astype(int).astype(str),
        "valor_facturado": "0",
        "valor_pendiente_de_pago": "0",
        "dias_adicionados": "0",
        "ultima_actualizacion": "2024-07-01T00:00:00.000",
    })
    # problemas sembrados
    df.loc[5, "valor_del_contrato"] = "No Definido"
    df.loc[6, "valor_del_contrato"] = "0"
    df.loc[7, "fecha_de_fin_del_contrato"] = "2020-01-01T00:00:00.000"
    df.loc[8, "fecha_de_firma"] = ""
    df.loc[10, ["id_contrato", "modalidad_de_contratacion", "tipo_de_contrato", "valor_del_contrato"]] = \
        [SEMBRADOS["atipico"], "Mínima cuantía", "Suministros", "95000000000"]
    df.loc[11, ["id_contrato", "valor_del_contrato", "valor_pagado"]] = [SEMBRADOS["pagado"], "10000000", "25000000"]
    df.loc[12, ["id_contrato", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", "dias_adicionados"]] = \
        [SEMBRADOS["adicion"], "2023-01-10T00:00:00.000", "2023-12-31T00:00:00.000", "250"]
    dup = df.iloc[100:130].copy()
    dup["ultima_actualizacion"] = "2024-08-01T00:00:00.000"
    dup["estado_contrato"] = "Cerrado"
    return pd.concat([df, dup], ignore_index=True)
