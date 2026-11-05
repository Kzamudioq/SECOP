"""Línea de comandos.

    python -m secop descargar --departamento "Distrito Capital de Bogotá" --desde 2021-01-01
    python -m secop analizar  --datos datos/contratos.parquet
    python -m secop todo      (las dos cosas)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import descarga, informe
from .limpieza import limpiar


def _args_descarga(p):
    p.add_argument("--departamento", default="Distrito Capital de Bogotá",
                   help='Departamento de la entidad, tal como lo escribe SECOP. "" = todo el país.')
    p.add_argument("--desde", default="2021-01-01")
    p.add_argument("--hasta", default=None, help="Fecha final (exclusiva)")
    p.add_argument("--max-registros", type=int, default=None, help="Útil para pruebas rápidas")
    p.add_argument("--datos", default="datos/contratos.parquet")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="secop", description="Análisis de contratación pública SECOP II")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("descargar")
    _args_descarga(d)
    a = sub.add_parser("analizar")
    a.add_argument("--datos", default="datos/contratos.parquet")
    a.add_argument("--salida", default="salidas")
    a.add_argument("--alcance", default=None, help="Texto para títulos y fuentes")
    t = sub.add_parser("todo")
    _args_descarga(t)
    t.add_argument("--salida", default="salidas")
    t.add_argument("--alcance", default=None)
    args = ap.parse_args(argv)

    if args.cmd in ("descargar", "todo"):
        print(f"Descargando SECOP II · {args.departamento or 'Colombia'} · desde {args.desde}")
        crudo = descarga.descargar(args.departamento or None, args.desde, args.hasta, args.max_registros)
        descarga.guardar(crudo, args.datos)
        print(f"Guardado en {args.datos} ({len(crudo):,} filas)")
    if args.cmd in ("analizar", "todo"):
        crudo = descarga.leer(args.datos)
        df, cal = limpiar(crudo)
        alcance = args.alcance or (getattr(args, "departamento", None) or "contratos descargados")
        out = informe.generar(df, cal, args.salida, alcance)
        print(f"Informe en {Path(args.salida) / 'informe.md'} · {len(out['figuras'])} figuras")


if __name__ == "__main__":
    main()
