"""
Catálogo de datasets SECOP disponibles en datos.gov.co (API SODA de Socrata).

Este módulo define los datasets de contratación pública que el servidor MCP
puede consultar. Cada dataset corresponde a un recurso publicado en el portal
de datos abiertos del gobierno colombiano (datos.gov.co).

Los datasets se identifican por un ID de Socrata (ej: "f789-7hwg") que se usa
para construir la URL del endpoint de la API SODA.

Datasets disponibles:
    - secop1_procesos:    Procesos de SECOP I (sistema histórico, antes de 2020).
    - secop2_procesos:    Procesos de contratación en SECOP II (transaccional).
    - secop2_contratos:   Contratos electrónicos firmados en SECOP II.
    - secop2_proveedores: Proveedores registrados en la plataforma SECOP II.

Referencias:
    - Portal de datos abiertos: https://www.datos.gov.co/
    - Documentación API SODA: https://dev.socrata.com/docs/endpoints.html
    - SECOP I: https://www.datos.gov.co/d/f789-7hwg
    - SECOP II Procesos: https://www.datos.gov.co/d/p6dx-8zbt
    - SECOP II Contratos: https://www.datos.gov.co/d/jbjy-vk9h
    - SECOP II Proveedores: https://www.datos.gov.co/d/qmzu-gj57
"""

# URL base de la API SODA de Socrata para datos.gov.co.
# Cada dataset se accede como: {BASE_URL}/{dataset_id}.json
BASE_URL = "https://www.datos.gov.co/resource"

# Catálogo de datasets SECOP.
#
# Cada entrada contiene:
#   - id:              Identificador de Socrata (usado para construir la URL).
#   - nombre:          Nombre legible del dataset.
#   - descripcion:     Descripción breve del contenido.
#   - campos_busqueda: Lista de campos disponibles para filtrar y consultar.
#                      Estos nombres corresponden a las columnas del dataset
#                      en Socrata y se usan en las cláusulas SoQL ($where, $select, etc.).
DATASETS: dict[str, dict] = {
    "secop1_procesos": {
        "id": "f789-7hwg",
        "nombre": "SECOP I - Procesos de Compra Pública",
        "descripcion": (
            "Procesos de contratación publicados en SECOP I (histórico). "
            "Incluye contratos anteriores a la migración a SECOP II."
        ),
        "campos_busqueda": [
            "nombre_entidad",
            "nit_de_la_entidad",
            "departamento_entidad",
            "municipio_entidad",
            "modalidad_de_contratacion",
            "estado_del_proceso",
            "tipo_de_contrato",
            "nom_razon_social_contratista",
            "identificacion_del_contratista",
            "detalle_del_objeto_a_contratar",
            "numero_de_proceso",
            "numero_de_contrato",
            "cuantia_proceso",
            "cuantia_contrato",
            "fecha_de_firma_del_contrato",
            "fecha_ini_ejec_contrato",
            "fecha_fin_ejec_contrato",
        ],
    },
    "secop2_procesos": {
        "id": "p6dx-8zbt",
        "nombre": "SECOP II - Procesos de Contratación",
        "descripcion": (
            "Procesos de contratación transaccionales en SECOP II. "
            "Incluye información de entidades, proveedores y adjudicaciones."
        ),
        "campos_busqueda": [
            "entidad",
            "nit_entidad",
            "departamento",
            "ciudad",
            "fase",
            "estado_del_procedimiento",
            "modalidad_de_contratacion",
            "tipo_de_contrato",
            "nombre_del_proveedor",
            "nit_del_proveedor_adjudicado",
            "nombre_del_procedimiento",
            "descripci_n_del_procedimiento",
            "descripci_n_del_procedimiento",
            "precio_base",
            "valor_total_adjudicacion",
            "fecha_de_publicacion_del",
        ],
    },
    "secop2_contratos": {
        "id": "jbjy-vk9h",
        "nombre": "SECOP II - Contratos Electrónicos",
        "descripcion": (
            "Contratos electrónicos registrados en SECOP II. "
            "Incluye valores pagados, facturados y pendientes de pago."
        ),
        "campos_busqueda": [
            "nombre_entidad",
            "nit_entidad",
            "departamento",
            "ciudad",
            "modalidad_de_contratacion",
            "tipo_de_contrato",
            "estado_contrato",
            "proveedor_adjudicado",
            "documento_proveedor",
            "objeto_del_contrato",
            "valor_del_contrato",
            "valor_pagado",
            "valor_pendiente_de_pago",
            "valor_facturado",
            "fecha_de_firma",
            "fecha_de_inicio_del_contrato",
            "fecha_de_fin_del_contrato",
            "origen_de_los_recursos",
        ],
    },
    "secop2_proveedores": {
        "id": "qmzu-gj57",
        "nombre": "SECOP II - Proveedores Registrados",
        "descripcion": (
            "Proveedores registrados en la plataforma SECOP II. "
            "Permite buscar por nombre, NIT, departamento y ciudad."
        ),
        "campos_busqueda": [
            "nombre_proveedor",
            "nit_proveedor",
            "departamento",
            "ciudad",
            "estado",
        ],
    },
}


def get_endpoint(dataset_key: str) -> str:
    """Construye la URL completa del endpoint SODA para un dataset dado.

    Args:
        dataset_key: Clave del dataset en el catálogo DATASETS
                     (ej: "secop1_procesos", "secop2_contratos").

    Returns:
        URL completa del endpoint JSON de Socrata.

    Raises:
        KeyError: Si dataset_key no existe en DATASETS.

    Ejemplo:
        >>> get_endpoint("secop1_procesos")
        'https://www.datos.gov.co/resource/f789-7hwg.json'
    """
    return f"{BASE_URL}/{DATASETS[dataset_key]['id']}.json"
