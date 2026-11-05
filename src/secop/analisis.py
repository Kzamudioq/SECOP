"""Indicadores de contratación: tiempo, modalidad, sectores, proveedores y señales de alerta.

Todas las funciones reciben el DataFrame que devuelve ``limpieza.limpiar`` y entregan
tablas pequeñas, listas para graficar o exportar.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .limpieza import etiqueta_proveedor, utilizables

# Ley 996 de 2005 (Ley de Garantías). Ventanas en que se restringe la contratación
# directa: cuatro meses antes de la elección presidencial hasta la segunda vuelta, y
# cuatro meses antes de las elecciones territoriales (para entidades territoriales).
VEDAS = [
    ("Presidencial 2022", "2022-01-29", "2022-06-19", "todas"),
    ("Territoriales 2023", "2023-06-29", "2023-10-29", "territorial"),
    ("Presidencial 2026", "2026-01-31", "2026-06-21", "todas"),
]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def resumen(df: pd.DataFrame) -> dict:
    u = utilizables(df)
    v = u["valor_del_contrato"]
    return {
        "contratos": len(df),
        "contratos_utilizables": len(u),
        "desde": u["fecha_de_firma"].min(),
        "hasta": u["fecha_de_firma"].max(),
        "entidades": u["nombre_entidad"].nunique(),
        "proveedores": u["clave_proveedor"].nunique(),
        "valor_total": float(v.sum()),
        "valor_mediano": float(v.median()) if len(v) else np.nan,
        "pct_directa_contratos": float(u["es_directa"].mean() * 100) if len(u) else np.nan,
        "pct_directa_valor": float(v[u["es_directa"]].sum() / v.sum() * 100) if v.sum() else np.nan,
        "pct_pyme_contratos": float(u["es_pyme"].mean() * 100) if u["es_pyme"].notna().any() else np.nan,
        "pct_persona_natural": float(u["persona_natural"].mean() * 100) if len(u) else np.nan,
    }


def serie_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """Contratos y valor por mes de firma, separando contratación directa."""
    u = utilizables(df)
    g = u.groupby("mes").agg(contratos=("id_contrato", "size"), valor=("valor_del_contrato", "sum"),
                             directa=("es_directa", "sum"))
    g = g.reindex(pd.period_range(g.index.min(), g.index.max(), freq="M"), fill_value=0) if len(g) else g
    g["pct_directa"] = np.where(g["contratos"] > 0, g["directa"] / g["contratos"].clip(lower=1) * 100, np.nan)
    g.index.name = "mes"
    return g


def estacionalidad(df: pd.DataFrame) -> pd.DataFrame:
    """Participación de cada mes en el total anual, promediada solo sobre años completos."""
    m = serie_mensual(df)
    if m.empty:
        return pd.DataFrame(columns=["mes", "pct_promedio", "min", "max"])
    t = m.assign(anio=m.index.year, num=m.index.month)
    completos = t.groupby("anio")["num"].nunique().loc[lambda s: s == 12].index
    t = t[t["anio"].isin(completos)]
    t["pct"] = t["contratos"] / t.groupby("anio")["contratos"].transform("sum") * 100
    e = t.groupby("num")["pct"].agg(pct_promedio="mean", min="min", max="max").reindex(range(1, 13))
    e.insert(0, "mes", MESES)
    e.attrs["anios"] = list(completos)
    return e


def efecto_ley_garantias(df: pd.DataFrame, dias: int = 30) -> pd.DataFrame:
    """Contratación directa en los ``dias`` previos a cada veda vs. el mismo tramo de días de otros años.

    La comparación con el mismo calendario de otros años aísla el efecto de la veda del
    pico normal de enero (inicio de vigencia, contratos de prestación de servicios).
    """
    u = utilizables(df)
    filas = []
    for nombre, ini, fin, alcance in VEDAS:
        ini, fin = pd.Timestamp(ini), pd.Timestamp(fin)
        sub = u if alcance == "todas" else u[u["orden"].fillna("").str.lower().str.startswith("territorial")]
        sub = sub[sub["es_directa"]]
        f = sub["fecha_de_firma"]
        if f.empty or f.min() > ini - pd.Timedelta(days=dias) or f.max() < fin:
            continue
        antes = ((f >= ini - pd.Timedelta(days=dias)) & (f < ini)).sum()
        durante = ((f >= ini) & (f <= fin)).sum()
        refs = []
        for anio in sorted(set(f.dt.year) - {ini.year}):
            try:
                ri = ini.replace(year=anio)
            except ValueError:
                continue
            if f.min() <= ri - pd.Timedelta(days=dias) and ri <= f.max():
                refs.append(((f >= ri - pd.Timedelta(days=dias)) & (f < ri)).sum())
        base = float(np.mean(refs)) if refs else np.nan
        filas.append({"veda": nombre, "inicio": ini.date(), "fin": fin.date(),
                      f"directa_{dias}d_antes": int(antes), f"promedio_otros_anios": base,
                      "razon": antes / base if base else np.nan, "directa_durante_veda": int(durante),
                      "anios_referencia": len(refs)})
    return pd.DataFrame(filas)


def por_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    u = utilizables(df)
    g = u.groupby("modalidad_de_contratacion", dropna=False)["valor_del_contrato"].agg(
        contratos="size", valor="sum", mediana="median")
    g["pct_contratos"] = g["contratos"] / g["contratos"].sum() * 100
    g["pct_valor"] = g["valor"] / g["valor"].sum() * 100
    return g.sort_values("valor", ascending=False)


def por_sector(df: pd.DataFrame) -> pd.DataFrame:
    u = utilizables(df)
    g = u.groupby("sector", dropna=False).agg(contratos=("id_contrato", "size"), valor=("valor_del_contrato", "sum"),
                                              entidades=("nombre_entidad", "nunique"),
                                              pct_directa=("es_directa", "mean"))
    g["pct_directa"] *= 100
    g["pct_valor"] = g["valor"] / g["valor"].sum() * 100
    return g.sort_values("valor", ascending=False)


def top(serie_valor: pd.Series, n: int, otros: str = "Otros") -> pd.Series:
    """Top-n y el resto agrupado, para gráficas que no se saturan."""
    s = serie_valor.sort_values(ascending=False)
    if len(s) <= n:
        return s
    return pd.concat([s.iloc[:n], pd.Series({otros: s.iloc[n:].sum()})])


def hhi(participaciones: pd.Series) -> float:
    """Índice Herfindahl-Hirschman en escala 0-10 000 (participaciones en %)."""
    p = participaciones / participaciones.sum() * 100
    return float((p ** 2).sum())


def concentracion_entidades(df: pd.DataFrame, min_contratos: int = 20) -> pd.DataFrame:
    """Por entidad: cuánto del valor se lleva su mayor proveedor y el HHI de sus proveedores.

    Solo personas jurídicas o grupos: los contratos de prestación de servicios con
    personas naturales son muchos y pequeños y diluirían la medida.
    """
    u = utilizables(df)
    u = u[~u["persona_natural"] & u["clave_proveedor"].notna()]
    filas = []
    for ent, g in u.groupby("nombre_entidad"):
        if len(g) < min_contratos:
            continue
        pv = g.groupby("clave_proveedor")["valor_del_contrato"].sum().sort_values(ascending=False)
        filas.append({"entidad": ent, "sector": g["sector"].mode().iat[0] if g["sector"].notna().any() else pd.NA,
                      "contratos": len(g), "proveedores": len(pv), "valor": g["valor_del_contrato"].sum(),
                      "pct_mayor_proveedor": pv.iat[0] / pv.sum() * 100, "hhi": hhi(pv),
                      "pct_directa": g["es_directa"].mean() * 100})
    t = pd.DataFrame(filas)
    if t.empty:
        return t
    t["nivel"] = pd.cut(t["hhi"], [-1, 1500, 2500, 10_001], labels=["baja", "moderada", "alta"])
    return t.sort_values("hhi", ascending=False).reset_index(drop=True)


def top_proveedores(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    u = utilizables(df)
    u = u[u["clave_proveedor"].notna()]
    g = u.groupby("clave_proveedor").agg(
        nombre=("proveedor_adjudicado", lambda s: s.mode().iat[0] if s.notna().any() else pd.NA),
        persona_natural=("persona_natural", "max"), contratos=("id_contrato", "size"),
        entidades=("nombre_entidad", "nunique"), valor=("valor_del_contrato", "sum"),
        pyme=("es_pyme", "max"))
    g["pct_valor"] = g["valor"] / u["valor_del_contrato"].sum() * 100
    g = g.sort_values("valor", ascending=False).head(n).reset_index()
    g["proveedor"] = [etiqueta_proveedor(r.nombre, r.persona_natural, r.clave_proveedor) for r in g.itertuples()]
    return g[["proveedor", "contratos", "entidades", "valor", "pct_valor", "pyme"]]


def pymes(df: pd.DataFrame) -> pd.DataFrame:
    """Participación de pymes por modalidad: en número de contratos y en valor."""
    u = utilizables(df)
    u = u[u["es_pyme"].notna() & ~u["persona_natural"]]
    g = u.groupby(["modalidad_de_contratacion", "es_pyme"])["valor_del_contrato"].agg(["size", "sum"]).unstack(fill_value=0)
    out = pd.DataFrame({
        "contratos": g["size"].sum(axis=1),
        "pct_pyme_contratos": g["size"].get(True, 0) / g["size"].sum(axis=1) * 100,
        "pct_pyme_valor": g["sum"].get(True, 0) / g["sum"].sum(axis=1).replace(0, np.nan) * 100,
    })
    return out.sort_values("contratos", ascending=False)


def duraciones(df: pd.DataFrame) -> pd.DataFrame:
    u = utilizables(df)
    d = u[(u["duracion_dias"] > 0) & ~u["q_duracion_extrema"]]
    return d.groupby("tipo_de_contrato")["duracion_dias"].describe(percentiles=[.25, .5, .75])[
        ["count", "25%", "50%", "75%"]].rename(columns={"count": "contratos", "50%": "mediana"}) \
        .sort_values("contratos", ascending=False)


def alertas(df: pd.DataFrame, z: float = 3.5, min_grupo: int = 30) -> pd.DataFrame:
    """Señales para revisión, contrato por contrato. **Una señal no es una irregularidad.**

    * ``valor_atipico``: el logaritmo del valor se aleja más de ``z`` desviaciones robustas
      (MAD) de la mediana de contratos del mismo tipo y modalidad.
    * ``pagado_supera_valor``: se pagó más de lo pactado.
    * ``adicion_mayor_50``: los días adicionados superan la mitad del plazo original.
    * ``inicio_antes_firma``: la ejecución empezó antes de firmar.
    """
    u = utilizables(df).copy()
    lv = np.log10(u["valor_del_contrato"])
    grupo = [u["tipo_de_contrato"].fillna("?"), u["modalidad_de_contratacion"].fillna("?")]
    med = lv.groupby(grupo).transform("median")
    mad = (lv - med).abs().groupby(grupo).transform("median") * 1.4826
    n = lv.groupby(grupo).transform("size")
    u["z_robusto"] = ((lv - med) / mad.replace(0, np.nan)).where(n >= min_grupo)
    u["valor_atipico"] = u["z_robusto"].abs() > z
    u["pagado_supera_valor"] = u["q_pagado_supera_valor"]
    plazo = u["duracion_dias"] - u["dias_adicionados"].fillna(0)
    u["adicion_mayor_50"] = (u["dias_adicionados"].fillna(0) > 0) & (u["dias_adicionados"] > 0.5 * plazo.clip(lower=1))
    u["inicio_antes_firma"] = u["q_inicio_antes_firma"]
    senales = ["valor_atipico", "pagado_supera_valor", "adicion_mayor_50", "inicio_antes_firma"]
    u["n_senales"] = u[senales].sum(axis=1)
    out = u[u["n_senales"] > 0].copy()
    out["proveedor"] = [etiqueta_proveedor(a, b, c) for a, b, c in
                        zip(out["proveedor_adjudicado"], out["persona_natural"], out["clave_proveedor"])]
    cols = ["id_contrato", "nombre_entidad", "proveedor", "modalidad_de_contratacion", "tipo_de_contrato",
            "fecha_de_firma", "valor_del_contrato", "valor_pagado", "dias_adicionados", "z_robusto", *senales, "n_senales"]
    return out[cols].sort_values(["n_senales", "valor_del_contrato"], ascending=False).reset_index(drop=True)


def resumen_alertas(a: pd.DataFrame, total: int) -> pd.DataFrame:
    s = ["valor_atipico", "pagado_supera_valor", "adicion_mayor_50", "inicio_antes_firma"]
    t = pd.DataFrame({"señal": s, "contratos": [int(a[c].sum()) for c in s]})
    t["porcentaje"] = (t["contratos"] / max(total, 1) * 100).round(2)
    return t
