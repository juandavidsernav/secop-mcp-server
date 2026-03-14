"""Cliente HTTP para la API SODA de Socrata (datos.gov.co)."""

from __future__ import annotations

import os
import json
from typing import Any

import httpx

from .datasets import get_endpoint

_TIMEOUT = 30.0


def _app_token() -> str | None:
    return os.environ.get("SOCRATA_APP_TOKEN") or None


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    token = _app_token()
    if token:
        headers["X-App-Token"] = token
    return headers


async def query_dataset(
    dataset_key: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = 50,
    offset: int = 0,
    q: str | None = None,
) -> list[dict[str, Any]]:
    """Consulta un dataset SECOP usando SoQL."""
    url = get_endpoint(dataset_key)
    params: dict[str, str] = {"$limit": str(min(limit, 1000))}
    if offset > 0:
        params["$offset"] = str(offset)
    if where:
        params["$where"] = where
    if select:
        params["$select"] = select
    if order:
        params["$order"] = order
    if q:
        params["$q"] = q

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url, params=params, headers=_headers())
        resp.raise_for_status()
        return resp.json()


def format_results(rows: list[dict[str, Any]], max_rows: int = 20) -> str:
    """Formatea resultados para respuesta legible del LLM."""
    if not rows:
        return "No se encontraron resultados."

    total = len(rows)
    display = rows[:max_rows]
    lines: list[str] = [f"Mostrando {len(display)} de {total} resultados:\n"]

    for i, row in enumerate(display, 1):
        lines.append(f"--- Resultado {i} ---")
        for key, value in row.items():
            if value is not None and str(value).strip():
                lines.append(f"  {key}: {value}")
        lines.append("")

    if total > max_rows:
        lines.append(f"... y {total - max_rows} resultados más (usa 'offset' para paginar).")

    return "\n".join(lines)
