"""
secop_mcp - Servidor MCP para consultar contratación pública de Colombia.

Este paquete implementa un servidor MCP (Model Context Protocol) que permite
a modelos de lenguaje (LLMs) consultar datos de contratación pública del
Estado colombiano a través de las plataformas SECOP I y SECOP II.

Los datos se obtienen en tiempo real desde la API SODA de Socrata en
datos.gov.co, el portal de datos abiertos del gobierno colombiano.

Módulos:
    server   - Definición del servidor MCP y sus herramientas (tools).
    client   - Cliente HTTP para comunicarse con la API SODA de Socrata.
    datasets - Catálogo de datasets SECOP disponibles y sus metadatos.

Ejemplo de uso:
    # Ejecutar como servidor MCP (modo stdio para Claude Desktop / Claude Code)
    $ secop-mcp

    # O directamente con Python
    $ python -m secop_mcp.server
"""
