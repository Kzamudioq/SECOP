"""Descarga de contratos SECOP II desde la API de Datos Abiertos (Socrata).

Lo que corrige frente a la versión anterior:

* El filtro de fecha se aplica **en el servidor**. Antes se pedían 100 000 filas sin
  orden y luego se filtraba desde 2021 en pandas: la API devolvía sobre todo contratos
  de 2017-2020 y después del filtro quedaban unos pocos cientos.
* Paginación estable (``$order=:id`` + ``$offset``) para traer el universo completo,
  no los primeros N registros que el servidor quiera dar.
* Solo se piden las columnas que el análisis usa. Se excluyen a propósito los datos
  personales que el dataset publica (representante legal, cuentas bancarias,
  supervisores, ordenadores del gasto).
* Reintentos con espera creciente ante 429/5xx y caché local en disco.
"""
from __future__ import annotations

import io
import os
import time
from pathlib import Path

import pandas as pd
import requests

DATASET = "jbjy-vk9h"  # SECOP II - Contratos Electrónicos
URL = f"https://www.datos.gov.co/resource/{DATASET}.csv"

COLUMNAS = [
    "id_contrato", "proceso_de_compra", "nombre_entidad", "nit_entidad", "codigo_entidad",
    "departamento", "ciudad", "orden", "sector", "rama",
    "estado_contrato", "tipo_de_contrato", "modalidad_de_contratacion", "justificacion_modalidad_de",
    "codigo_de_categoria_principal", "objeto_del_contrato",
    "fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato",
    "tipodocproveedor", "documento_proveedor", "codigo_proveedor", "proveedor_adjudicado",
    "es_grupo", "es_pyme", "origen_de_los_recursos", "destino_gasto",
    "valor_del_contrato", "valor_facturado", "valor_pagado", "valor_pendiente_de_pago",
    "dias_adicionados", "ultima_actualizacion",
]


def construir_where(departamento: str | None, desde: str | None, hasta: str | None) -> str:
    partes = []
    if departamento:
        partes.append(f"departamento = '{departamento.replace(chr(39), chr(39) * 2)}'")
    if desde:
        partes.append(f"fecha_de_firma >= '{pd.Timestamp(desde):%Y-%m-%dT%H:%M:%S}'")
    if hasta:
        partes.append(f"fecha_de_firma < '{pd.Timestamp(hasta):%Y-%m-%dT%H:%M:%S}'")
    return " AND ".join(partes)


def _pedir(session: requests.Session, params: dict, headers: dict, intentos: int = 6) -> str:
    espera = 2.0
    for intento in range(1, intentos + 1):
        try:
            r = session.get(URL, params=params, headers=headers, timeout=180)
            if r.status_code == 200:
                return r.text
            if r.status_code not in (429, 500, 502, 503, 504):
                raise RuntimeError(f"La API respondió {r.status_code}: {r.text[:300]}")
        except (requests.ConnectionError, requests.Timeout):
            if intento == intentos:
                raise
        time.sleep(espera)
        espera = min(espera * 2, 60)
    raise RuntimeError("La API no respondió después de varios intentos")


def descargar(
    departamento: str | None = "Distrito Capital de Bogotá",
    desde: str | None = "2021-01-01",
    hasta: str | None = None,
    max_registros: int | None = None,
    lote: int = 50_000,
    token: str | None = None,
    session: requests.Session | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Trae todos los contratos que cumplen el filtro, por lotes. Todo llega como texto."""
    session = session or requests.Session()
    token = token or os.environ.get("SOCRATA_APP_TOKEN")
    headers = {"X-App-Token": token} if token else {}
    where = construir_where(departamento, desde, hasta)
    partes, offset = [], 0
    while True:
        n = lote if max_registros is None else min(lote, max_registros - offset)
        if n <= 0:
            break
        params = {"$select": ",".join(COLUMNAS), "$order": ":id", "$limit": n, "$offset": offset}
        if where:
            params["$where"] = where
        texto = _pedir(session, params, headers)
        df = pd.read_csv(io.StringIO(texto), dtype="string[pyarrow]", keep_default_na=False, na_values=[""])
        partes.append(df)
        offset += len(df)
        if verbose:
            print(f"  {offset:>10,} contratos descargados", flush=True)
        if len(df) < n:
            break
    if not partes:
        return pd.DataFrame(columns=COLUMNAS)
    return pd.concat(partes, ignore_index=True)


def guardar(df: pd.DataFrame, ruta: str | Path) -> Path:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if ruta.suffix == ".parquet":
        df.to_parquet(ruta, index=False)
    else:
        df.to_csv(ruta, index=False)
    return ruta


def leer(ruta: str | Path) -> pd.DataFrame:
    ruta = Path(ruta)
    if ruta.suffix == ".parquet":
        return pd.read_parquet(ruta)
    return pd.read_csv(ruta, dtype="string[pyarrow]", keep_default_na=False, na_values=[""])
