"""Figuras del informe (matplotlib, PNG). Un solo estilo para todas."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .analisis import MESES, VEDAS, top  # noqa: E402

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
REJILLA = "#e4e3df"
SERIE_1 = "#2a78d6"   # azul
SERIE_2 = "#eb6834"   # naranja
VEDA = "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
    "axes.edgecolor": REJILLA, "axes.labelcolor": TINTA_2, "text.color": TINTA,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "axes.grid": True, "grid.color": REJILLA,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.titlelocation": "left", "axes.titlesize": 13,
    "axes.titleweight": "bold", "font.size": 10, "legend.frameon": False, "figure.dpi": 110,
})


def _es(s: str) -> str:
    """1,234.5 -> 1.234,5 (formato colombiano)."""
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def cop(x: float, _pos=None) -> str:
    """Pesos en la escala que se lee: billones (10^12), miles de millones (mil M), millones (M)."""
    a = abs(x)
    if a >= 1e12:
        return "$" + _es(f"{x / 1e12:,.1f}") + " billones"
    if a >= 1e9:
        return "$" + _es(f"{x / 1e9:,.0f}") + " mil M"
    if a >= 1e6:
        return _es(f"${x / 1e6:,.0f} M")
    return _es(f"${x:,.0f}")


def miles(x: float, _pos=None) -> str:
    return _es(f"{x:,.0f}")


def _nota(fig, texto: str):
    fig.text(0.01, 0.01, texto, fontsize=8, color=TINTA_2, ha="left", va="bottom")


def _guardar(fig, carpeta: Path, nombre: str) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.png"
    fig.savefig(ruta, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return ruta


def _sombrear_vedas(ax, x0, x1):
    for nombre, ini, fin, _ in VEDAS:
        ini, fin = pd.Timestamp(ini), pd.Timestamp(fin)
        if fin < x0 or ini > x1:
            continue
        ax.axvspan(ini, fin, color=VEDA, alpha=0.10, lw=0)


def mensual(m: pd.DataFrame, carpeta: Path, fuente: str) -> Path:
    x = m.index.to_timestamp()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.2), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    a1.bar(x, m["contratos"], width=24, color=SERIE_1, align="edge")
    a1.set_title("Contratos firmados por mes")
    a1.yaxis.set_major_formatter(mticker.FuncFormatter(miles))
    a2.plot(x + pd.Timedelta(days=12), m["pct_directa"], color=SERIE_1, lw=2)
    a2.set_title("Porcentaje firmado por contratación directa", fontsize=11)
    a2.set_ylim(0, 100)
    a2.yaxis.set_major_formatter(mticker.PercentFormatter())
    for a in (a1, a2):
        _sombrear_vedas(a, x.min(), x.max() + pd.Timedelta(days=31))
        a.grid(axis="x", visible=False)
    vis = [v for v in VEDAS if pd.Timestamp(v[2]) >= x.min() and pd.Timestamp(v[1]) <= x.max()]
    if vis:
        a1.text(pd.Timestamp(vis[0][1]) + pd.Timedelta(days=6), a1.get_ylim()[1] * 0.93,
                "Ley de Garantías", color=TINTA_2, fontsize=9, va="top")
    _nota(fig, fuente)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _guardar(fig, carpeta, "01_contratos_por_mes")


def estacional(e: pd.DataFrame, carpeta: Path, fuente: str) -> Path:
    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(12)
    ax.bar(x, e["pct_promedio"], color=SERIE_1, width=0.65)
    ax.errorbar(x, e["pct_promedio"], yerr=[e["pct_promedio"] - e["min"], e["max"] - e["pct_promedio"]],
                fmt="none", ecolor=TINTA_2, elinewidth=1, capsize=3)
    ax.axhline(100 / 12, color=TINTA_2, lw=1, ls="--")
    ax.text(11.4, 100 / 12, " reparto parejo", va="bottom", ha="right", fontsize=8, color=TINTA_2)
    ax.set_xticks(x, MESES)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    anios = e.attrs.get("anios", [])
    ax.set_title("¿En qué mes se firma? Participación en el total del año")
    ax.grid(axis="x", visible=False)
    _nota(fig, f"{fuente} · Barras: promedio de {len(anios)} años completos ({', '.join(map(str, anios))}); "
               "líneas: mínimo y máximo.")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _guardar(fig, carpeta, "02_estacionalidad")


def modalidades(t: pd.DataFrame, carpeta: Path, fuente: str, n: int = 7) -> Path:
    t = t.copy()
    t.index = t.index.fillna("Sin dato")
    if len(t) > n:
        resto = t.iloc[n:][["contratos", "valor", "pct_contratos", "pct_valor"]].sum()
        t = pd.concat([t.iloc[:n], resto.to_frame("Otras").T])
    t = t.iloc[::-1]
    y = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(10, 0.55 * len(t) + 1.6))
    h = 0.36
    ax.barh(y + h / 2 + 0.01, t["pct_contratos"], h, color=SERIE_1, label="% de los contratos")
    ax.barh(y - h / 2 - 0.01, t["pct_valor"], h, color=SERIE_2, label="% del valor")
    for yi, (pc, pv) in enumerate(zip(t["pct_contratos"], t["pct_valor"])):
        ax.text(pc + 0.6, yi + h / 2, f"{pc:.0f}%", va="center", fontsize=8, color=TINTA_2)
        ax.text(pv + 0.6, yi - h / 2, f"{pv:.0f}%", va="center", fontsize=8, color=TINTA_2)
    ax.set_yticks(y, [str(s) for s in t.index])
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.set_title("Modalidad de contratación: cuántos contratos y cuánta plata")
    ax.legend(loc="lower right")
    ax.grid(axis="y", visible=False)
    _nota(fig, fuente)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _guardar(fig, carpeta, "03_modalidades")


def sectores(t: pd.DataFrame, carpeta: Path, fuente: str, n: int = 10) -> Path:
    s = top(t["valor"].rename(index=lambda i: "Sin dato" if pd.isna(i) else i), n, "Otros sectores").iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 0.45 * len(s) + 1.4))
    ax.barh(s.index.astype(str), s.values, color=[TINTA_2 if i == "Otros sectores" else SERIE_1 for i in s.index],
            height=0.65)
    for i, v in enumerate(s.values):
        ax.text(v, i, "  " + cop(v), va="center", fontsize=8, color=TINTA_2)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(cop))
    ax.set_xlim(0, s.max() * 1.18)
    ax.set_title(f"Valor contratado por sector (top {n})")
    ax.grid(axis="y", visible=False)
    _nota(fig, fuente)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _guardar(fig, carpeta, "04_sectores")


def concentracion(c: pd.DataFrame, carpeta: Path, fuente: str) -> Path | None:
    if c.empty:
        return None
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axhspan(2500, 10_000, color=SERIE_2, alpha=0.07, lw=0)
    ax.scatter(c["contratos"], c["hhi"], s=18, color=SERIE_1, alpha=0.75, edgecolor=SUPERFICIE, linewidth=0.6)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(miles))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(miles))
    ax.set_ylim(0, 10_200)
    for lim, txt in ((1500, "concentración moderada"), (2500, "concentración alta")):
        ax.axhline(lim, color=TINTA_2, lw=0.8, ls="--")
        ax.text(ax.get_xlim()[1], lim, txt + " ", ha="right", va="bottom", fontsize=8, color=TINTA_2)
    ax.set_xlabel("Contratos con personas jurídicas (escala log)")
    ax.set_ylabel("HHI de sus proveedores")
    ax.set_title("¿Cuánto dependen las entidades de pocos proveedores?")
    _nota(fig, f"{fuente} · Cada punto es una entidad. HHI = suma de participaciones² (0-10.000).")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _guardar(fig, carpeta, "05_concentracion")


def distribucion_valor(df: pd.DataFrame, carpeta: Path, fuente: str) -> Path:
    v = df.loc[df["valor_del_contrato"] > 0, "valor_del_contrato"]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    bins = np.logspace(np.floor(np.log10(v.min())), np.ceil(np.log10(v.max())), 60)
    ax.hist(v, bins=bins, color=SERIE_1, edgecolor=SUPERFICIE, linewidth=0.5)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(cop))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(miles))
    med = v.median()
    ax.axvline(med, color=TINTA, lw=1.2)
    ax.text(med, ax.get_ylim()[1] * 0.97, f" mediana {cop(med)} ", fontsize=9, va="top",
            bbox=dict(facecolor=SUPERFICIE, edgecolor="none", pad=1.5))
    ax.set_title("Distribución del valor de los contratos (escala logarítmica)")
    ax.set_ylabel("Contratos")
    ax.grid(axis="x", visible=False)
    _nota(fig, fuente)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _guardar(fig, carpeta, "06_distribucion_valor")


def proveedores(t: pd.DataFrame, carpeta: Path, fuente: str) -> Path:
    t = t.iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 0.42 * len(t) + 1.4))
    etiquetas = [p if len(p) <= 48 else p[:46] + "…" for p in t["proveedor"]]
    ax.barh(etiquetas, t["valor"], color=SERIE_1, height=0.65)
    for i, (v, n) in enumerate(zip(t["valor"], t["contratos"])):
        ax.text(v, i, f"  {cop(v)} · {n:,} contr.".replace(",", "."), va="center", fontsize=8, color=TINTA_2)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(cop))
    ax.set_xlim(0, t["valor"].max() * 1.3)
    ax.set_title(f"Los {len(t)} proveedores con más valor adjudicado")
    ax.grid(axis="y", visible=False)
    _nota(fig, f"{fuente} · Agrupados por documento del proveedor. Personas naturales enmascaradas.")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _guardar(fig, carpeta, "07_top_proveedores")
