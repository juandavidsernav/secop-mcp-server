"""Definición de datasets SECOP disponibles en datos.gov.co (Socrata SODA API)."""

BASE_URL = "https://www.datos.gov.co/resource"

DATASETS = {
    "secop1_procesos": {
        "id": "f789-7hwg",
        "nombre": "SECOP I - Procesos de Compra Pública",
        "descripcion": "Procesos de contratación publicados en SECOP I (histórico).",
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
        "descripcion": "Procesos de contratación transaccionales en SECOP II.",
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
            "objeto_a_contratar",
            "precio_base",
            "valor_total_adjudicacion",
            "fecha_de_publicacion_del",
        ],
    },
    "secop2_contratos": {
        "id": "jbjy-vk9h",
        "nombre": "SECOP II - Contratos Electrónicos",
        "descripcion": "Contratos electrónicos registrados en SECOP II.",
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
            "fecha_de_inicio_del_contrato",
            "fecha_de_fin_del_contrato",
            "origen_de_los_recursos",
        ],
    },
    "secop2_proveedores": {
        "id": "qmzu-gj57",
        "nombre": "SECOP II - Proveedores Registrados",
        "descripcion": "Proveedores registrados en la plataforma SECOP II.",
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
    return f"{BASE_URL}/{DATASETS[dataset_key]['id']}.json"
