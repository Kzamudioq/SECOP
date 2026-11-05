"""Arma el informe: figuras PNG, tablas en Excel/CSV y un resumen en Markdown."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import analisis as an
from . import graficas as gr
from .limpieza import ReporteCalidad, utilizables


def _md(t: pd.DataFrame, fmt: dict | None = None, index: bool = True) -> str:
    t = t.copy()
    for c, f in (fmt or {}).items():
        if c in t:
            t[c] = t[c].map(lambda v, f=f: "" if pd.isna(v) else f(v))
    if index:
        t = t.reset_index()
    cols = [str(c) for c in t.columns]
    lineas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lineas += ["| " + " | ".join("" if pd.isna(v) else str(v) for v in fila) + " |" for fila in t.itertuples(index=False)]
    return "\n".join(lineas)


def pct(v) -> str:
    return gr._es(f"{v:.1f} %")


def generar(df: pd.DataFrame, calidad: ReporteCalidad, salida: str | Path, alcance: str) -> dict:
    salida = Path(salida)
    figs = salida / "figuras"
    fuente = f"Fuente: SECOP II, datos.gov.co ({alcance})"
    u = utilizables(df)

    r = an.resumen(df)
    mensual = an.serie_mensual(df)
    estac = an.estacionalidad(df)
    garantias = an.efecto_ley_garantias(df)
    modal = an.por_modalidad(df)
    sector = an.por_sector(df)
    conc = an.concentracion_entidades(df)
    provs = an.top_proveedores(df)
    pym = an.pymes(df)
    dur = an.duraciones(df)
    alert = an.alertas(df)
    res_alert = an.resumen_alertas(alert, len(u))

    rutas = [gr.mensual(mensual, figs, fuente), gr.modalidades(modal, figs, fuente),
             gr.sectores(sector, figs, fuente), gr.distribucion_valor(u, figs, fuente),
             gr.proveedores(provs, figs, fuente)]
    if estac["pct_promedio"].notna().any():
        rutas.append(gr.estacional(estac, figs, fuente))
    rutas.append(gr.concentracion(conc, figs, fuente))

    tablas = {"calidad": calidad.tabla(), "mensual": mensual.reset_index().assign(mes=lambda t: t["mes"].astype(str)),
              "estacionalidad": estac, "ley_garantias": garantias, "modalidad": modal.reset_index(),
              "sector": sector.reset_index(), "concentracion": conc, "top_proveedores": provs,
              "pymes": pym.reset_index(), "duracion": dur.reset_index(), "alertas": alert}
    (salida / "tablas").mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(salida / "tablas" / "secop_resultados.xlsx") as xw:
        for nombre, t in tablas.items():
            t.to_excel(xw, sheet_name=nombre[:31], index=False)
    for nombre, t in tablas.items():
        t.to_csv(salida / "tablas" / f"{nombre}.csv", index=False)

    md = [f"# Informe SECOP II · {alcance}", "",
          f"Contratos firmados entre **{r['desde']:%d/%m/%Y}** y **{r['hasta']:%d/%m/%Y}**. "
          f"Generado el {pd.Timestamp.today():%d/%m/%Y}.", "",
          "## En cifras", "",
          f"- **{gr.miles(r['contratos_utilizables'])}** contratos únicos con fecha y valor válidos "
          f"(de {gr.miles(r['contratos'])}), de **{gr.miles(r['entidades'])}** entidades y "
          f"**{gr.miles(r['proveedores'])}** proveedores.",
          f"- Valor total: **{gr.cop(r['valor_total'])}**; contrato mediano: **{gr.cop(r['valor_mediano'])}**.",
          f"- Contratación directa: **{pct(r['pct_directa_contratos'])}** de los contratos y "
          f"**{pct(r['pct_directa_valor'])}** del valor.",
          f"- Contratos con personas naturales: **{pct(r['pct_persona_natural'])}**.", "",
          "## Calidad de los datos", "", _md(calidad.tabla(), {"contratos": gr.miles, "porcentaje": pct}, index=False), ""]
    if not garantias.empty:
        md += ["## Ley de Garantías", "",
               "Contratación directa en los 30 días previos a cada veda, comparada con los mismos 30 días "
               "de otros años (razón > 1: se adelantaron contratos antes de la restricción).", "",
               _md(garantias, {"promedio_otros_anios": lambda v: gr._es(f"{v:,.0f}"),
                               "razon": lambda v: gr._es(f"{v:.2f}")}, index=False), ""]
    md += ["## Modalidades", "", _md(modal.head(8), {"contratos": gr.miles, "valor": gr.cop, "mediana": gr.cop,
                                                    "pct_contratos": pct, "pct_valor": pct}), "",
           "## Sectores (top 10 por valor)", "",
           _md(sector.head(10), {"contratos": gr.miles, "valor": gr.cop, "pct_directa": pct, "pct_valor": pct}), ""]
    if not conc.empty:
        n_alta = int((conc["nivel"] == "alta").sum())
        md += ["## Concentración de proveedores", "",
               f"{n_alta} de {len(conc)} entidades (con al menos 20 contratos con personas jurídicas) tienen "
               "concentración **alta** (HHI > 2.500). Las 10 más concentradas:", "",
               _md(conc.head(10)[["entidad", "contratos", "proveedores", "pct_mayor_proveedor", "hhi"]],
                   {"pct_mayor_proveedor": pct, "hhi": lambda v: gr.miles(v)}, index=False), ""]
    md += ["## Señales para revisión", "",
           "Una señal **no** es evidencia de irregularidad: indica contratos que vale la pena mirar. "
           "Lista completa en `tablas/alertas.csv`.", "", _md(res_alert, {"porcentaje": pct}, index=False), ""]
    md += ["## Figuras", ""] + [f"![{p.stem}](figuras/{p.name})" for p in rutas if p]
    (salida / "informe.md").write_text("\n".join(md), encoding="utf-8")
    return {"resumen": r, "figuras": [p for p in rutas if p], "tablas": tablas}
