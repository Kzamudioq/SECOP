"""Limpieza y control de calidad.

Decisiones que cambian resultados (y por qué):

* Un monto ilegible queda como **vacío (NaN), no como 0**. Con ceros, la mediana y el
  promedio bajan sin que nadie lo note.
* Los duplicados de ``id_contrato`` se resuelven quedándose con la versión **más
  reciente** (``ultima_actualizacion``), no con la primera que aparece.
* Las categorías se normalizan (``terminado`` y ``Terminado`` eran dos estados;
  ``defensa`` y ``Defensa`` dos sectores).
* Nada se borra en silencio: cada problema queda marcado en una columna ``q_*`` y
  contado en el reporte de calidad.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

MONTOS = ["valor_del_contrato", "valor_facturado", "valor_pagado", "valor_pendiente_de_pago"]
FECHAS = ["fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", "ultima_actualizacion"]
CATEGORIAS = ["estado_contrato", "sector", "orden", "rama", "tipo_de_contrato", "modalidad_de_contratacion",
              "tipodocproveedor", "departamento", "destino_gasto", "origen_de_los_recursos"]
DOCS_PERSONA_NATURAL = {"cédula de ciudadanía", "cedula de ciudadania", "cédula de extranjería",
                        "cedula de extranjeria", "pasaporte", "tarjeta de identidad"}
VACIOS = {"", "no definido", "no aplica", "sin descripcion", "sin descripción", "n/a", "na", "null", "none", "nan"}


def a_numero(valor) -> float:
    """Convierte montos escritos de cualquier forma a float. Ilegible -> NaN.

    >>> a_numero("17897916"), a_numero("$ 1.234.567,89"), a_numero("1,234,567.5"), a_numero("abc")
    (17897916.0, 1234567.89, 1234567.5, nan)
    """
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return np.nan
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)
    s = re.sub(r"[^\d.,\-]", "", str(valor))
    if not re.search(r"\d", s):
        return np.nan
    if "," in s and "." in s:  # el último separador es el decimal
        dec = "," if s.rfind(",") > s.rfind(".") else "."
        mil = "." if dec == "," else ","
        s = s.replace(mil, "").replace(dec, ".")
    elif "," in s:
        partes = s.split(",")
        s = s.replace(",", ".") if len(partes) == 2 and len(partes[1]) in (1, 2) else s.replace(",", "")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


def _canon(s: str) -> str:
    """Texto comparable: sin tildes, minúsculas, espacios simples."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def normalizar_categoria(serie: pd.Series) -> pd.Series:
    """Une variantes de mayúsculas/tildes/espacios bajo la forma escrita más frecuente.

    Trabaja sobre los valores distintos (pocos), no fila por fila: rápido con millones de filas.
    """
    s = serie.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    s = s.mask(s.str.lower().isin(VACIOS))
    conteo = s.value_counts()
    if conteo.empty:
        return s
    tabla = pd.DataFrame({"forma": conteo.index, "n": conteo.values})
    tabla["canon"] = tabla["forma"].map(_canon)
    elegida = tabla.sort_values("n", ascending=False).drop_duplicates("canon").set_index("canon")["forma"]
    # si la forma más frecuente está toda en minúscula, se capitaliza ("defensa" -> "Defensa")
    elegida = elegida.map(lambda t: t[:1].upper() + t[1:] if t == t.lower() else t)
    mapa = dict(zip(tabla["forma"], tabla["canon"].map(elegida)))
    return s.map(mapa).astype("string")


@dataclass
class ReporteCalidad:
    filas_entrada: int = 0
    duplicados_eliminados: int = 0
    filas_salida: int = 0
    problemas: dict[str, int] = field(default_factory=dict)

    def tabla(self) -> pd.DataFrame:
        filas = [("Registros descargados", self.filas_entrada),
                 ("Duplicados de id_contrato eliminados", self.duplicados_eliminados),
                 ("Contratos únicos analizados", self.filas_salida)]
        filas += [(DESCRIPCION_Q.get(k, k), v) for k, v in self.problemas.items()]
        t = pd.DataFrame(filas, columns=["control", "contratos"])
        t["porcentaje"] = (t["contratos"] / max(self.filas_salida, 1) * 100).round(2)
        t.loc[:2, "porcentaje"] = np.nan
        return t


DESCRIPCION_Q = {
    "q_valor_invalido": "Valor del contrato vacío, ilegible o <= 0",
    "q_valor_implausible": "Valor implausible (error de digitación probable), excluido de los totales",
    "q_fecha_firma_invalida": "Fecha de firma vacía o fuera de rango",
    "q_fin_antes_inicio": "Fecha de fin anterior a la de inicio",
    "q_duracion_extrema": "Duración mayor a 10 años",
    "q_pagado_supera_valor": "Valor pagado mayor que el valor del contrato",
    "q_inicio_antes_firma": "Inicio de ejecución anterior a la firma",
}


def limpiar(crudo: pd.DataFrame, hoy: pd.Timestamp | None = None) -> tuple[pd.DataFrame, ReporteCalidad]:
    hoy = pd.Timestamp(hoy or pd.Timestamp.today()).normalize()
    rep = ReporteCalidad(filas_entrada=len(crudo))
    df = crudo.copy()

    for c in MONTOS:
        if c in df:
            df[c] = df[c].map(a_numero).astype(float)
    if "dias_adicionados" in df:
        df["dias_adicionados"] = pd.to_numeric(df["dias_adicionados"].map(a_numero), errors="coerce")
    for c in FECHAS:
        if c in df:
            f = pd.to_datetime(df[c], errors="coerce", format="ISO8601")
            df[c] = f.where((f >= "2000-01-01") & (f <= hoy + pd.DateOffset(years=30)))
    for c in CATEGORIAS:
        if c in df:
            df[c] = normalizar_categoria(df[c])
    for c in ("nombre_entidad", "proveedor_adjudicado", "documento_proveedor", "nit_entidad", "id_contrato"):
        if c in df:
            df[c] = df[c].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    if "nombre_entidad" in df:
        df["nombre_entidad"] = df["nombre_entidad"].str.upper()

    # duplicados: queda la versión más reciente de cada contrato
    orden = ["id_contrato"] + (["ultima_actualizacion"] if "ultima_actualizacion" in df else [])
    df = df.sort_values(orden, na_position="first")
    antes = len(df)
    df = df.drop_duplicates("id_contrato", keep="last").reset_index(drop=True)
    rep.duplicados_eliminados = antes - len(df)

    # variables derivadas
    df["anio"] = df["fecha_de_firma"].dt.year.astype("Int64")
    df["mes"] = df["fecha_de_firma"].dt.to_period("M")
    df["duracion_dias"] = (df["fecha_de_fin_del_contrato"] - df["fecha_de_inicio_del_contrato"]).dt.days
    df["es_pyme"] = df.get("es_pyme", pd.Series(index=df.index, dtype="string")).astype("string").str.strip() \
        .str.lower().map({"si": True, "sí": True, "no": False}).astype("boolean")
    mod = df["modalidad_de_contratacion"].fillna("").map(_canon)
    df["es_directa"] = mod.str.contains("contratacion directa")
    doc = df["tipodocproveedor"].fillna("").str.lower()
    df["persona_natural"] = doc.isin(DOCS_PERSONA_NATURAL) | doc.map(_canon).isin({_canon(d) for d in DOCS_PERSONA_NATURAL})
    df["clave_proveedor"] = df["documento_proveedor"].str.replace(r"[^\dA-Za-z]", "", regex=True).str.upper()
    df["clave_proveedor"] = df["clave_proveedor"].mask(df["clave_proveedor"].isin(["", "NODEFINIDO", "0"]))

    # marcas de calidad (no se borra nada)
    df["q_valor_invalido"] = ~(df["valor_del_contrato"] > 0)
    df["q_valor_implausible"] = valor_implausible(df)
    df["q_fecha_firma_invalida"] = df["fecha_de_firma"].isna()
    df["q_fin_antes_inicio"] = df["duracion_dias"] < 0
    df["q_duracion_extrema"] = df["duracion_dias"] > 3650
    df["q_pagado_supera_valor"] = df["valor_pagado"] > df["valor_del_contrato"] * 1.001
    df["q_inicio_antes_firma"] = df["fecha_de_inicio_del_contrato"] < df["fecha_de_firma"]
    rep.problemas = {c: int(df[c].sum()) for c in DESCRIPCION_Q}
    rep.filas_salida = len(df)
    return df, rep


TOPE_VALOR = 1e13            # $10 billones: por encima, ningún contrato individual es creíble
TOPE_PERSONA_NATURAL = 1e10  # $10 mil millones con persona natural...
PAGO_MINIMO = 0.01           # ...y pagado menos del 1 %: casi siempre ceros de más


def valor_implausible(df: pd.DataFrame) -> pd.Series:
    """Montos que casi seguro son errores de digitación.

    En SECOP II aparecen contratos de prestación de servicios con personas naturales por
    cientos de billones de pesos, con pagos de unos pocos millones. Dos de ellos bastan para
    que el "valor total" de Bogotá supere varias veces el presupuesto de la Nación. Se
    marcan y se excluyen de los totales; siguen visibles en la tabla de señales.
    """
    v = df["valor_del_contrato"]
    pagado = df["valor_pagado"].fillna(0) if "valor_pagado" in df else pd.Series(0.0, index=df.index)
    return (v >= TOPE_VALOR) | (df["persona_natural"] & (v >= TOPE_PERSONA_NATURAL) & (pagado < PAGO_MINIMO * v))


def utilizables(df: pd.DataFrame) -> pd.DataFrame:
    """Contratos con fecha y valor válidos y creíbles: la base de casi todos los indicadores."""
    return df[~df["q_valor_invalido"] & ~df["q_fecha_firma_invalida"] & ~df["q_valor_implausible"]]


def etiqueta_proveedor(nombre, persona_natural: bool, documento) -> str:
    """Las personas naturales se muestran enmascaradas en gráficas y tablas publicadas."""
    if persona_natural:
        doc = str(documento) if pd.notna(documento) else ""
        return f"Persona natural ···{doc[-3:]}" if doc else "Persona natural"
    return str(nombre) if pd.notna(nombre) else "Sin nombre"
