# SECOP MCP Server

<!-- mcp-name: io.github.juandavidsernav/secop-mcp-server -->

Servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) para consultar la contratación pública de Colombia a través de SECOP I y SECOP II.

Los datos se obtienen en tiempo real desde [datos.gov.co](https://www.datos.gov.co/) (API SODA de Socrata) y son 100% públicos. No se almacena ningún dato localmente.

## ¿Para qué sirve?

Este servidor permite que modelos de lenguaje como Claude consulten directamente los datos de contratación pública del Estado colombiano. Esto facilita:

- **Control político:** Investigar contratos de entidades públicas y funcionarios.
- **Transparencia:** Verificar contratistas, montos y modalidades de contratación.
- **Periodismo de datos:** Cruzar información de proveedores y entidades.
- **Veeduría ciudadana:** Cualquier persona puede consultar cómo se gastan los recursos públicos.

## Datasets disponibles

| Dataset | Descripción | Fuente |
|---|---|---|
| **SECOP I - Procesos** | Datos históricos de procesos de compra pública | [datos.gov.co](https://www.datos.gov.co/d/f789-7hwg) |
| **SECOP II - Procesos** | Procesos de contratación transaccionales | [datos.gov.co](https://www.datos.gov.co/d/p6dx-8zbt) |
| **SECOP II - Contratos** | Contratos electrónicos con valores pagados/facturados | [datos.gov.co](https://www.datos.gov.co/d/jbjy-vk9h) |
| **SECOP II - Proveedores** | Proveedores registrados en la plataforma | [datos.gov.co](https://www.datos.gov.co/d/qmzu-gj57) |

## Herramientas (Tools)

| Tool | Descripción |
|---|---|
| `buscar_secop1` | Buscar procesos en SECOP I por entidad, contratista, objeto, departamento, rango de fechas, etc. |
| `buscar_procesos_secop2` | Buscar procesos de contratación en SECOP II con filtros temporales |
| `buscar_contratos_secop2` | Buscar contratos electrónicos en SECOP II con filtros temporales |
| `buscar_proveedores` | Buscar proveedores registrados en SECOP II |
| `buscar_por_persona` | Buscar en TODOS los datasets por cédula/NIT o nombre de una persona |
| `resumen_contratacion` | Vista condensada de contratos (campos clave: entidad, proveedor, valor, estado, fecha) |
| `agregaciones_contratacion` | Totales agrupados por proveedor, entidad, departamento o modalidad |
| `consulta_libre` | Consulta SoQL avanzada sobre cualquier dataset |
| `listar_datasets` | Ver todos los datasets y sus campos disponibles |

## Instalación

### Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip

### Opción 1: Desde PyPI (recomendada)

```bash
# Con uv (más rápido)
uvx secop-mcp-server

# Con pip
pip install secop-mcp-server
```

### Opción 2: Desde GitHub

```bash
uvx --from git+https://github.com/juandavidsernav/secop-mcp-server secop-mcp
```

### Opción 3: Desde el código fuente

```bash
git clone https://github.com/juandavidsernav/secop-mcp-server.git
cd secop-mcp-server
uv sync
```

## Configuración

### Claude Code

```bash
# Instalación rápida desde PyPI
claude mcp add secop-colombia -- uvx secop-mcp-server

# O desde código fuente
claude mcp add secop-colombia -- uv run --directory /ruta/al/secop-mcp-server secop-mcp
```

### Claude Desktop

Edita el archivo de configuración:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "secop-colombia": {
      "command": "uvx",
      "args": ["secop-mcp-server"]
    }
  }
}
```

### App Token (opcional pero recomendado)

Sin token funciona, pero con rate-limiting agresivo (~60 peticiones/hora). Obtén uno gratis:

1. Regístrate en [datos.gov.co](https://www.datos.gov.co/)
2. Ve a tu perfil > Developer Settings
3. Crea un nuevo App Token

Configúralo como variable de entorno:

```json
{
  "mcpServers": {
    "secop-colombia": {
      "command": "uvx",
      "args": ["secop-mcp-server"],
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
- "¿Qué contratos tiene la persona con cédula 12345678?"
- "Muestra los procesos de licitación pública en Antioquia"
- "¿Cuáles son los contratos más grandes de SECOP II este año?"
- "Busca todos los contratos asociados a la empresa XYZ"
- "¿Cuánto ha contratado el municipio de Medellín en prestación de servicios?"
- "Dame un resumen de los contratos de EPM en 2024"
- "¿Cuáles son los proveedores con más contratos en Antioquia?"
- "Agrupa por modalidad los contratos de la Alcaldía de Medellín"
- "Muestra los contratos firmados entre enero y marzo de 2025 en el Valle del Cauca"

## Estructura del proyecto

```
secop-mcp-server/
├── secop_mcp/
│   ├── __init__.py    # Documentación del paquete
│   ├── server.py      # Servidor MCP y definición de herramientas (tools)
│   ├── client.py      # Cliente HTTP para la API SODA de Socrata
│   └── datasets.py    # Catálogo de datasets SECOP y sus metadatos
├── pyproject.toml     # Configuración del paquete Python
├── LICENSE            # Licencia MIT
└── README.md          # Este archivo
```

## ¿Cómo funciona?

```
Claude (LLM) <--MCP/stdio--> secop-mcp-server <--HTTP/SoQL--> datos.gov.co (API SODA)
```

1. Claude invoca una herramienta MCP (ej: `buscar_contratos_secop2`).
2. El servidor construye una consulta SoQL con los filtros proporcionados.
3. Se ejecuta la petición HTTP a la API de datos.gov.co.
4. Los resultados se formatean en texto legible y se retornan a Claude.
5. Claude analiza los datos y responde al usuario.

Todo corre **localmente** en tu máquina. No hay servidor intermedio ni se almacenan datos.

## Contribuir

Las contribuciones son bienvenidas:

1. Fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Ideas para contribuir

- Agregar más datasets de datos.gov.co
- Traducciones del README
- Alertas o monitoreo de nuevos contratos
- Exportación a CSV/Excel

## Licencia

[MIT](LICENSE) - Libre para uso personal, comercial, modificación y redistribución.
