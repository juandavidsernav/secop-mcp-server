"""
Servidor MCP para consultas de contratación pública colombiana (SECOP I y II).

Este módulo define el servidor MCP (Model Context Protocol) y todas las
herramientas (tools) que expone a los modelos de lenguaje. Cada herramienta
corresponde a un tipo de consulta específico sobre los datos de contratación
pública del Estado colombiano.

Herramientas disponibles:
    - buscar_secop1:          Búsqueda en procesos históricos de SECOP I.
    - buscar_procesos_secop2: Búsqueda de procesos de contratación en SECOP II.
    - buscar_contratos_secop2: Búsqueda de contratos electrónicos en SECOP II.
    - buscar_proveedores:     Búsqueda de proveedores registrados en SECOP II.
    - buscar_por_persona:     Búsqueda cruzada en TODOS los datasets por persona/empresa.
    - consulta_libre:         Consulta SoQL avanzada sobre cualquier dataset.
    - listar_datasets:        Lista los datasets disponibles y sus campos.

Arquitectura:
    El servidor usa FastMCP (del SDK oficial de MCP) en modo stdio, lo que
    permite que Claude Desktop y Claude Code se comuniquen con él a través
    de entrada/salida estándar.

    Flujo de una consulta:
    1. El LLM invoca una herramienta (ej: buscar_contratos_secop2).
    2. La herramienta construye filtros SoQL con _build_where().
    3. Se ejecuta la consulta HTTP a datos.gov.co vía client.query_dataset().
    4. Los resultados se formatean con client.format_results() y se retornan al LLM.
"""

from __future__ import annotations

import json
import sys
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from .client import format_results, query_dataset
from .datasets import DATASETS

# Instancia del servidor MCP.
# El nombre "secop-colombia" es el identificador que los clientes MCP
# (como Claude Desktop) usan para referirse a este servidor.
mcp = FastMCP(
    "secop-colombia",
    instructions=(
        "Servidor para consultar datos de contratación pública de Colombia "
        "(SECOP I y SECOP II). Los datos provienen de datos.gov.co. "
        "Usa las herramientas disponibles para buscar contratos, procesos y proveedores."
    ),
)


# ---------------------------------------------------------------------------
# Helpers para construir cláusulas WHERE
# ---------------------------------------------------------------------------


def _build_where(filters: dict[str, str | float | None]) -> str | None:
    """Construye una cláusula $where SoQL a partir de un diccionario de filtros.

    Recorre los filtros proporcionados e ignora los que son None o cadenas
    vacías. Para cada filtro válido:
      - Si el valor es numérico, genera una comparación "campo >= valor".
      - Si el valor es texto, genera una búsqueda parcial insensible a
        mayúsculas: "upper(campo) like upper('%valor%')".

    Los valores de texto se escapan (comillas simples) para prevenir
    inyección SoQL.

    Args:
        filters: Diccionario donde las claves son nombres de columnas del
                 dataset y los valores son los criterios de búsqueda.
                 Los valores None o vacíos se ignoran.

    Returns:
        Cláusula $where combinada con AND, o None si no hay filtros activos.

    Ejemplo:
        >>> _build_where({"nombre_entidad": "Bogotá", "valor_del_contrato": 1000000})
        "upper(nombre_entidad) like upper('%Bogotá%') AND valor_del_contrato >= 1000000"
    """
    clauses: list[str] = []
    for field, value in filters.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        if isinstance(value, (int, float)):
            clauses.append(f"{field} >= {value}")
        else:
            # Escapar comillas simples para prevenir inyección SoQL
            safe = value.replace("'", "''")
            clauses.append(f"upper({field}) like upper('%{safe}%')")
    return " AND ".join(clauses) if clauses else None


# ---------------------------------------------------------------------------
# Tools - Herramientas MCP expuestas al LLM
# ---------------------------------------------------------------------------


@mcp.tool()
async def buscar_secop1(
    entidad: Annotated[str, "Nombre de la entidad contratante"] = "",
    contratista: Annotated[str, "Nombre o razón social del contratista"] = "",
    identificacion_contratista: Annotated[str, "Cédula o NIT del contratista"] = "",
    numero_proceso: Annotated[str, "Número del proceso"] = "",
    numero_contrato: Annotated[str, "Número del contrato"] = "",
    objeto: Annotated[str, "Palabras clave del objeto a contratar"] = "",
    departamento: Annotated[str, "Departamento de la entidad"] = "",
    modalidad: Annotated[str, "Modalidad de contratación"] = "",
    estado: Annotated[str, "Estado del proceso"] = "",
    cuantia_minima: Annotated[float | None, "Cuantía mínima del contrato"] = None,
    limite: Annotated[int, "Máximo de resultados (1-200)"] = 50,
    offset: Annotated[int, "Saltar N resultados (paginación)"] = 0,
) -> str:
    """Busca procesos de compra pública en SECOP I (datos históricos).

    SECOP I es el sistema de contratación anterior a SECOP II. Contiene
    registros históricos de procesos de compra pública. Todos los filtros
    son opcionales y combinables entre sí (operador AND).

    Útil para buscar contratos anteriores a ~2020 o entidades que aún
    publican en SECOP I.
    """
    where = _build_where({
        "nombre_entidad": entidad,
        "nom_razon_social_contratista": contratista,
        "identificacion_del_contratista": identificacion_contratista if identificacion_contratista else None,
        "numero_de_proceso": numero_proceso if numero_proceso else None,
        "numero_de_contrato": numero_contrato if numero_contrato else None,
        "detalle_del_objeto_a_contratar": objeto,
        "departamento_entidad": departamento,
        "modalidad_de_contratacion": modalidad,
        "estado_del_proceso": estado,
        "cuantia_contrato": cuantia_minima,
    })
    rows = await query_dataset(
        "secop1_procesos",
        where=where,
        limit=min(limite, 200),
        offset=offset,
        order="cuantia_contrato DESC",
    )
    return format_results(rows)


@mcp.tool()
async def buscar_procesos_secop2(
    entidad: Annotated[str, "Nombre de la entidad"] = "",
    proveedor: Annotated[str, "Nombre del proveedor adjudicado"] = "",
    nit_proveedor: Annotated[str, "NIT o documento del proveedor adjudicado"] = "",
    objeto: Annotated[str, "Palabras clave del objeto a contratar"] = "",
    departamento: Annotated[str, "Departamento"] = "",
    modalidad: Annotated[str, "Modalidad de contratación"] = "",
    fase: Annotated[str, "Fase del proceso (ej: 'Seleccion', 'Contrato')"] = "",
    estado: Annotated[str, "Estado del procedimiento"] = "",
    valor_minimo: Annotated[float | None, "Valor mínimo de adjudicación"] = None,
    limite: Annotated[int, "Máximo de resultados (1-200)"] = 50,
    offset: Annotated[int, "Saltar N resultados (paginación)"] = 0,
) -> str:
    """Busca procesos de contratación en SECOP II (plataforma transaccional).

    SECOP II es la plataforma vigente de contratación pública electrónica.
    Los procesos incluyen información sobre la entidad contratante, el
    proveedor seleccionado, valores y estado del procedimiento.
    """
    where = _build_where({
        "entidad": entidad,
        "nombre_del_proveedor": proveedor,
        "nit_del_proveedor_adjudicado": nit_proveedor if nit_proveedor else None,
        "objeto_a_contratar": objeto,
        "departamento": departamento,
        "modalidad_de_contratacion": modalidad,
        "fase": fase,
        "estado_del_procedimiento": estado,
        "valor_total_adjudicacion": valor_minimo,
    })
    rows = await query_dataset(
        "secop2_procesos",
        where=where,
        limit=min(limite, 200),
        offset=offset,
        order="valor_total_adjudicacion DESC",
    )
    return format_results(rows)


@mcp.tool()
async def buscar_contratos_secop2(
    entidad: Annotated[str, "Nombre de la entidad"] = "",
    proveedor: Annotated[str, "Nombre del proveedor adjudicado"] = "",
    nit_proveedor: Annotated[str, "NIT o documento del proveedor"] = "",
    objeto: Annotated[str, "Palabras clave del objeto del contrato"] = "",
    departamento: Annotated[str, "Departamento"] = "",
    modalidad: Annotated[str, "Modalidad de contratación"] = "",
    estado: Annotated[str, "Estado del contrato"] = "",
    valor_minimo: Annotated[float | None, "Valor mínimo del contrato"] = None,
    limite: Annotated[int, "Máximo de resultados (1-200)"] = 50,
    offset: Annotated[int, "Saltar N resultados (paginación)"] = 0,
) -> str:
    """Busca contratos electrónicos en SECOP II.

    Los contratos electrónicos contienen información detallada incluyendo
    valores pagados, facturados y pendientes de pago. Es el dataset más
    completo para analizar la ejecución financiera de la contratación.
    """
    where = _build_where({
        "nombre_entidad": entidad,
        "proveedor_adjudicado": proveedor,
        "documento_proveedor": nit_proveedor if nit_proveedor else None,
        "objeto_del_contrato": objeto,
        "departamento": departamento,
        "modalidad_de_contratacion": modalidad,
        "estado_contrato": estado,
        "valor_del_contrato": valor_minimo,
    })
    rows = await query_dataset(
        "secop2_contratos",
        where=where,
        limit=min(limite, 200),
        offset=offset,
        order="valor_del_contrato DESC",
    )
    return format_results(rows)


@mcp.tool()
async def buscar_proveedores(
    nombre: Annotated[str, "Nombre del proveedor"] = "",
    nit: Annotated[str, "NIT del proveedor"] = "",
    departamento: Annotated[str, "Departamento"] = "",
    ciudad: Annotated[str, "Ciudad"] = "",
    limite: Annotated[int, "Máximo de resultados (1-200)"] = 50,
    offset: Annotated[int, "Saltar N resultados (paginación)"] = 0,
) -> str:
    """Busca proveedores registrados en SECOP II.

    Permite identificar proveedores por nombre, NIT o ubicación geográfica.
    Útil para verificar el registro de un proveedor en la plataforma.
    """
    where = _build_where({
        "nombre_proveedor": nombre,
        "nit_proveedor": nit if nit else None,
        "departamento": departamento,
        "ciudad": ciudad,
    })
    rows = await query_dataset(
        "secop2_proveedores",
        where=where,
        limit=min(limite, 200),
        offset=offset,
    )
    return format_results(rows)


@mcp.tool()
async def consulta_libre(
    dataset: Annotated[
        str,
        "Dataset a consultar: 'secop1_procesos', 'secop2_procesos', 'secop2_contratos', 'secop2_proveedores'",
    ],
    where: Annotated[str, "Cláusula SoQL $where (ej: valor_del_contrato > 1000000000)"] = "",
    select: Annotated[str, "Campos a retornar separados por coma"] = "",
    order: Annotated[str, "Ordenamiento (ej: valor_del_contrato DESC)"] = "",
    busqueda_texto: Annotated[str, "Búsqueda full-text ($q de Socrata)"] = "",
    limite: Annotated[int, "Máximo de resultados (1-1000)"] = 50,
    offset: Annotated[int, "Saltar N resultados (paginación)"] = 0,
) -> str:
    """Consulta libre con SoQL sobre cualquier dataset SECOP.

    Para consultas avanzadas que las otras herramientas no cubren.
    Permite escribir cláusulas SoQL directamente, similar a SQL.

    Documentación SoQL: https://dev.socrata.com/docs/queries/

    Ejemplos de cláusulas $where:
        - "valor_del_contrato > 1000000000"
        - "departamento = 'Antioquia' AND estado_contrato = 'En ejecución'"
        - "fecha_de_firma > '2024-01-01'"
    """
    if dataset not in DATASETS:
        return f"Dataset no válido. Opciones: {', '.join(DATASETS.keys())}"
    rows = await query_dataset(
        dataset,
        where=where or None,
        select=select or None,
        order=order or None,
        q=busqueda_texto or None,
        limit=min(limite, 1000),
        offset=offset,
    )
    return format_results(rows)


@mcp.tool()
async def buscar_por_persona(
    documento: Annotated[str, "Número de documento (cédula, NIT, etc.)"] = "",
    nombre: Annotated[str, "Nombre o razón social de la persona/empresa"] = "",
    limite: Annotated[int, "Máximo de resultados por dataset (1-100)"] = 20,
) -> str:
    """Busca en TODOS los datasets de SECOP por número de documento o nombre de una persona/empresa.

    Útil para encontrar todos los contratos, procesos y registros asociados
    a un contratista o proveedor específico. Busca simultáneamente en SECOP I,
    SECOP II Procesos, SECOP II Contratos y SECOP II Proveedores.

    Esta es la herramienta más completa para investigar el historial de
    contratación de una persona natural o jurídica con el Estado colombiano.
    """
    if not documento and not nombre:
        return "Debes proporcionar al menos un documento o un nombre para buscar."

    import asyncio

    # Mapeo de campos de búsqueda por dataset.
    # Cada dataset usa nombres de columna diferentes para referirse al
    # documento y nombre del contratista/proveedor.
    searches: dict[str, dict[str, str | float | None]] = {
        "secop1_procesos": {
            "identificacion_del_contratista": documento if documento else None,
            "nom_razon_social_contratista": nombre if nombre else None,
        },
        "secop2_procesos": {
            "nit_del_proveedor_adjudicado": documento if documento else None,
            "nombre_del_proveedor": nombre if nombre else None,
        },
        "secop2_contratos": {
            "documento_proveedor": documento if documento else None,
            "proveedor_adjudicado": nombre if nombre else None,
        },
        "secop2_proveedores": {
            "nit_proveedor": documento if documento else None,
            "nombre_proveedor": nombre if nombre else None,
        },
    }

    cap = min(limite, 100)

    async def _search(ds_key: str, filters: dict) -> tuple[str, list]:
        """Ejecuta la búsqueda en un dataset individual."""
        try:
            where = _build_where(filters)
            rows = await query_dataset(ds_key, where=where, limit=cap)
            return ds_key, rows
        except Exception:
            return ds_key, []

    # Ejecutar todas las búsquedas en paralelo para minimizar latencia.
    tasks = [_search(k, v) for k, v in searches.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Consolidar resultados de todos los datasets.
    sections: list[str] = []
    total_found = 0
    for result in results:
        if isinstance(result, Exception):
            continue
        ds_key, rows = result
        ds_name = DATASETS[ds_key]["nombre"]
        if rows:
            total_found += len(rows)
            sections.append(f"## {ds_name} ({len(rows)} resultados)\n")
            sections.append(format_results(rows))
            sections.append("")

    if not sections:
        return "No se encontraron resultados en ningún dataset de SECOP."

    header = f"Total: {total_found} resultados encontrados.\n\n"
    return header + "\n".join(sections)


@mcp.tool()
async def listar_datasets() -> str:
    """Lista todos los datasets SECOP disponibles con sus campos de búsqueda.

    Útil para conocer qué datasets se pueden consultar y qué campos están
    disponibles para filtrar en cada uno. Esta información es necesaria
    para usar la herramienta consulta_libre().
    """
    lines: list[str] = []
    for key, ds in DATASETS.items():
        lines.append(f"## {ds['nombre']}")
        lines.append(f"  Clave: {key}")
        lines.append(f"  ID Socrata: {ds['id']}")
        lines.append(f"  Descripción: {ds['descripcion']}")
        lines.append(f"  Campos: {', '.join(ds['campos_busqueda'])}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main():
    """Punto de entrada principal del servidor MCP.

    Inicia el servidor en modo stdio (entrada/salida estándar), que es el
    transporte estándar para la comunicación entre clientes MCP (como
    Claude Desktop o Claude Code) y servidores MCP.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
