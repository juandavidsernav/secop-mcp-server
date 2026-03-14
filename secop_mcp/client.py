"""
Cliente HTTP para la API SODA de Socrata (datos.gov.co).

Este módulo maneja toda la comunicación con la API de datos abiertos del
gobierno colombiano. Construye las peticiones HTTP con los parámetros SoQL
(Socrata Query Language) y formatea las respuestas para consumo del LLM.

SoQL es el lenguaje de consulta de Socrata, similar a SQL. Soporta:
    - $where:  Filtros condicionales (ej: valor_del_contrato > 1000000)
    - $select: Campos a retornar (ej: nombre_entidad, valor_del_contrato)
    - $order:  Ordenamiento (ej: valor_del_contrato DESC)
    - $limit:  Máximo de resultados por página
    - $offset: Paginación (saltar N resultados)
    - $q:      Búsqueda full-text

Autenticación:
    La API funciona sin token, pero con rate-limiting agresivo (~60 req/hora).
    Con un App Token gratuito de datos.gov.co se obtiene un límite más alto.
    El token se lee de la variable de entorno SOCRATA_APP_TOKEN.

Referencias:
    - Documentación SoQL: https://dev.socrata.com/docs/queries/
    - Rate limits: https://dev.socrata.com/docs/app-tokens.html
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from .datasets import get_endpoint

# Timeout en segundos para las peticiones HTTP a la API de Socrata.
# Los datasets SECOP pueden ser grandes, así que se usa un valor generoso.
_TIMEOUT = 30.0


def _app_token() -> str | None:
    """Obtiene el App Token de Socrata desde variables de entorno.

    Returns:
        El token si está configurado en SOCRATA_APP_TOKEN, None en caso contrario.
    """
    return os.environ.get("SOCRATA_APP_TOKEN") or None


def _headers() -> dict[str, str]:
    """Construye los headers HTTP para la petición a Socrata.

    Siempre incluye Accept: application/json. Si hay un App Token
    configurado, lo incluye en el header X-App-Token para evitar
    rate-limiting agresivo.

    Returns:
        Diccionario de headers HTTP.
    """
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
    group: str | None = None,
) -> list[dict[str, Any]]:
    """Ejecuta una consulta SoQL contra un dataset SECOP en datos.gov.co.

    Construye los parámetros de la petición HTTP a partir de los argumentos
    y devuelve las filas resultantes como una lista de diccionarios.

    Args:
        dataset_key: Clave del dataset a consultar (ver datasets.DATASETS).
        where:       Cláusula $where SoQL para filtrar resultados.
                     Ejemplo: "valor_del_contrato > 1000000000"
        select:      Campos a retornar, separados por coma.
                     Ejemplo: "nombre_entidad, valor_del_contrato"
        order:       Ordenamiento de resultados.
                     Ejemplo: "valor_del_contrato DESC"
        limit:       Máximo de filas a retornar (tope: 1000, impuesto por Socrata).
        offset:      Número de filas a saltar (para paginación).
        q:           Búsqueda full-text ($q de Socrata).
        group:       Cláusula $group para agregaciones.
                     Ejemplo: "nombre_entidad"

    Returns:
        Lista de diccionarios, donde cada diccionario es una fila del dataset.
        Las claves son los nombres de las columnas del dataset.

    Raises:
        httpx.HTTPStatusError: Si la API retorna un código de error HTTP.
        KeyError: Si dataset_key no existe en el catálogo de datasets.
    """
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
    if group:
        params["$group"] = group

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url, params=params, headers=_headers())
        resp.raise_for_status()
        return resp.json()


def format_results(rows: list[dict[str, Any]], max_rows: int = 20) -> str:
    """Formatea filas de resultados en texto legible para el LLM.

    Convierte la lista de diccionarios en un formato de texto plano
    estructurado que es fácil de interpretar por un modelo de lenguaje.
    Limita la cantidad de filas mostradas para evitar respuestas excesivas.

    Args:
        rows:     Lista de filas (diccionarios) retornadas por query_dataset().
        max_rows: Máximo de filas a incluir en el texto formateado.
                  Las filas restantes se indican con un mensaje de paginación.

    Returns:
        Texto formateado con los resultados. Incluye conteo total,
        detalle por fila y mensaje de paginación si hay más resultados.

    Ejemplo de salida:
        Mostrando 2 de 50 resultados:

        --- Resultado 1 ---
          nombre_entidad: Alcaldía de Bogotá
          valor_del_contrato: 500000000
          ...

        --- Resultado 2 ---
          ...

        ... y 48 resultados más (usa 'offset' para paginar).
    """
    if not rows:
        return "No se encontraron resultados."

    total = len(rows)
    display = rows[:max_rows]
    lines: list[str] = [f"Mostrando {len(display)} de {total} resultados:\n"]

    for i, row in enumerate(display, 1):
        lines.append(f"--- Resultado {i} ---")
        for key, value in row.items():
            if value is not None and str(value).strip():
                if key in ("urlproceso", "ruta_proceso_en_secop_i"):
                    url = _extract_url(value)
                    if url:
                        lines.append(f"  {key}: {url}")
                else:
                    lines.append(f"  {key}: {value}")
        lines.append("")

    if total > max_rows:
        lines.append(f"... y {total - max_rows} resultados más (usa 'offset' para paginar).")

    return "\n".join(lines)


def _extract_url(value: Any) -> str:
    """Extrae la URL de un campo urlproceso de Socrata.

    El campo puede venir como dict {'url': '...'}, como string, o None.
    """
    if not value:
        return ""
    if isinstance(value, dict):
        return value.get("url", "")
    return str(value)


def format_summary(rows: list[dict[str, Any]], max_rows: int = 50) -> str:
    """Formatea resultados en vista resumida con solo campos clave.

    Muestra una línea compacta por contrato con: entidad, proveedor,
    objeto (truncado a 80 chars), valor, estado y fecha.
    """
    if not rows:
        return "No se encontraron resultados."

    total = len(rows)
    display = rows[:max_rows]
    lines: list[str] = [f"Resumen: {len(display)} de {total} resultados\n"]

    for i, row in enumerate(display, 1):
        entidad = row.get("nombre_entidad", "?")
        proveedor = row.get("proveedor_adjudicado", "?")
        doc = row.get("documento_proveedor", "")
        objeto = row.get("objeto_del_contrato", "?")
        if len(objeto) > 80:
            objeto = objeto[:77] + "..."
        valor = row.get("valor_del_contrato", "?")
        pagado = row.get("valor_pagado", "0")
        estado = row.get("estado_contrato", "?")
        fecha = row.get("fecha_de_firma", "?")
        if fecha and "T" in str(fecha):
            fecha = str(fecha).split("T")[0]
        modalidad = row.get("modalidad_de_contratacion", "?")

        try:
            valor_fmt = f"${float(valor):,.0f}"
        except (ValueError, TypeError):
            valor_fmt = str(valor)
        try:
            pagado_fmt = f"${float(pagado):,.0f}"
        except (ValueError, TypeError):
            pagado_fmt = str(pagado)

        url = _extract_url(row.get("urlproceso"))
        entry = (
            f"--- {i}. {proveedor} ({doc}) ---\n"
            f"  Entidad: {entidad}\n"
            f"  Objeto: {objeto}\n"
            f"  Valor: {valor_fmt} | Pagado: {pagado_fmt} | Estado: {estado}\n"
            f"  Fecha firma: {fecha} | Modalidad: {modalidad}"
        )
        if url:
            entry += f"\n  URL: {url}"
        lines.append(entry)

    if total > max_rows:
        lines.append(f"\n... y {total - max_rows} resultados más.")

    return "\n".join(lines)
