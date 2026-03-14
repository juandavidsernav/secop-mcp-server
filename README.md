# SECOP MCP Server 🇨🇴

Servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) para consultar la contratación pública de Colombia a través de SECOP I y SECOP II.

Los datos provienen de [datos.gov.co](https://www.datos.gov.co/) (API SODA de Socrata) y son 100% públicos.

## Datasets disponibles

| Dataset | Descripción |
|---|---|
| **SECOP I - Procesos** | Datos históricos de procesos de compra pública |
| **SECOP II - Procesos** | Procesos de contratación transaccionales |
| **SECOP II - Contratos** | Contratos electrónicos con valores pagados/facturados |
| **SECOP II - Proveedores** | Proveedores registrados en la plataforma |

## Herramientas (Tools)

| Tool | Descripción |
|---|---|
| `buscar_secop1` | Buscar procesos en SECOP I por entidad, contratista, objeto, departamento, etc. |
| `buscar_procesos_secop2` | Buscar procesos de contratación en SECOP II |
| `buscar_contratos_secop2` | Buscar contratos electrónicos en SECOP II |
| `buscar_proveedores` | Buscar proveedores registrados en SECOP II |
| `consulta_libre` | Consulta SoQL avanzada sobre cualquier dataset |
| `listar_datasets` | Ver todos los datasets y sus campos disponibles |

## Instalación

### Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip

### Opción 1: Desde PyPI (cuando se publique)

```bash
pip install secop-mcp-server
# o
uvx secop-mcp-server
```

### Opción 2: Desde el código fuente

```bash
git clone https://github.com/juserna/secop-mcp-server.git
cd secop-mcp-server
uv sync
```

### App Token (opcional pero recomendado)

Sin token funciona, pero con rate limiting agresivo. Obtén uno gratis:

1. Regístrate en [datos.gov.co](https://www.datos.gov.co/)
2. Ve a tu perfil → Developer Settings
3. Crea un nuevo App Token

```bash
cp .env.example .env
# Edita .env con tu token
```

## Configuración

### Claude Code

```bash
claude mcp add secop-colombia -- uv run --directory /ruta/al/secop-mcp-server secop-mcp
```

O edita `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "secop-colombia": {
      "command": "uv",
      "args": ["run", "--directory", "/ruta/al/secop-mcp-server", "secop-mcp"],
      "env": {
        "SOCRATA_APP_TOKEN": "tu-token-aqui"
      }
    }
  }
}
```

### Claude Desktop

Edita `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "secop-colombia": {
      "command": "uv",
      "args": ["run", "--directory", "/ruta/al/secop-mcp-server", "secop-mcp"],
      "env": {
        "SOCRATA_APP_TOKEN": "tu-token-aqui"
      }
    }
  }
}
```

## Ejemplos de uso

Una vez configurado, puedes pedirle a Claude cosas como:

- "Busca los contratos de la Alcaldía de Bogotá por más de 1000 millones"
- "¿Qué contratos tiene el proveedor con NIT 900123456?"
- "Muestra los procesos de licitación pública en Antioquia"
- "¿Cuáles son los contratos más grandes de SECOP II este año?"
- "Busca proveedores registrados en Medellín"

## Contribuir

Las contribuciones son bienvenidas. Abre un issue o un PR.

## Apoya el proyecto

Si este proyecto te resulta útil, considera apoyarlo:

- [GitHub Sponsors](https://github.com/sponsors/juserna)
- [Buy Me a Coffee](https://buymeacoffee.com/juserna)

## Licencia

MIT
