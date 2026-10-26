# CATÁLOGO FORMAL DE SERVIDORES MCP (MODEL CONTEXT PROTOCOL)

> **Propósito:** Registro centralizado, curaduría técnica, control de seguridad y configuración estandarizada de servidores MCP para agentes de IA (Google Antigravity, Claude Code, Cursor, Codex).

---

## 1. Arquitectura y Ecosistema MCP

El **Model Context Protocol (MCP)** permite a los agentes conectarse de forma bidireccional y estructurada con herramientas, recursos de datos y prompts externos:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA DE INTEGRACIÓN                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                       [ AGENTE DE IA / ANTIGRAVITY ]                   │
│                                     │                                  │
│                 Protocolo MCP (JSON-RPC 2.0 / stdio / http)            │
│                                     │                                  │
│         ┌───────────────────────────┼──────────────────────────┐       │
│         ▼                           ▼                          ▼       │
│  [ HERRAMIENTAS (Tools) ]   [ RECURSOS (Resources) ]   [ PROMPTS ]     │
│  • Ejecutar comandos         • Leer esquemas / BD       • Plantillas   │
│  • Consultar APIs externas   • Memoria contextual       • Workflows    │
│  • Depurar en navegador      • Logs y telemetría        • Formatos     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Estructura del Directorio `mcp/`

```text
mcp/
├── README.md               # Este documento maestro (normas, arquitectura, catálogo)
├── catalog.json            # Base de datos estructurada de servidores auditados
├── configs/                # Fragmentos JSON listos para importar a mcp_config.json
│   ├── claude-mem.json     # Memoria continua entre sesiones
│   ├── chrome-devtools.json# Inspección en vivo de navegador y red
│   ├── codebase-memory.json# Indexación semántica local de código
│   └── github.json         # Operaciones avanzadas de repositorios
├── evaluated/              # Bitácoras y reportes de auditoría de seguridad
│   └── [nombre-servidor].md
├── templates/              # Plantillas para auditar o crear servidores
│   ├── MCP_AUDIT.template.md
│   └── mcp_server.template.json
└── custom/                 # Servidores MCP desarrollados internamente
```

---

## 3. Protocolo de Auditoría y Seguridad (Gating)

Antes de activar un servidor MCP en el entorno global o de proyecto, debe superar los siguientes 4 filtros:

| Filtro | Pregunta Clave | Criterio de Aprobación |
| :--- | :--- | :---: |
| **1. Transporte Seguro** | ¿Utiliza `stdio` con binario conocido o `streamable_http` cifrado? | Obligatorio |
| **2. Principio de Menor Privilegio** | ¿Limita el acceso a carpetas locales o requiere permisos de administrador? | Obligatorio |
| **3. Aislamiento de Credenciales** | ¿Requiere tokens? ¿Se pueden inyectar vía variables de entorno sin guardarlas en texto plano? | Seguro / Variable |
| **4. Impacto en Contexto** | ¿El esquema JSON de sus herramientas es compacto o sobrecarga el prompt del sistema? | Optimizado (< 2k tokens) |

---

## 4. Integración en Antigravity

Antigravity lee sus servidores MCP desde:
- **Global:** `~/.gemini/config/mcp_config.json` (o `~/.gemini/antigravity/mcp_config.json`)
- **Plugin:** `plugins/<nombre_plugin>/mcp_config.json`

### Formato Estándar (`stdio`):
```json
{
  "mcpServers": {
    "servidor-ejemplo": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "ruta/a/base.db"],
      "env": {
        "DEBUG": "false"
      }
    }
  }
}
```

---

## 5. Servidores Verificados en el Catálogo

Consulta [`mcp/catalog.json`](catalog.json) para ver la lista completa actualizada.

| Identificador | Categoría | Transporte | Estado | Propósito Principal |
| :--- | :--- | :---: | :---: | :--- |
| **`claude-mem`** | Memoria / Contexto | `stdio` | 🟢 Operativo | Memoria persistente, compresión de observaciones y búsqueda semántica. |
| **`chrome-devtools`** | Depuración / Web | `stdio` | 🟡 Verificado | Control e inspección en vivo de Chrome DevTools (consola, red, DOM). |
| **`codebase-memory`** | Memoria de Código | `stdio` | 🟡 Verificado | Inteligencia de código local para indexar arquitecturas complejas. |
| **`github`** | Control de Versiones | `stdio` | 🟡 Verificado | Búsqueda, commits, issues y PRs mediante la API oficial de GitHub. |
| **`asset-porter`** | Multimedia / 3D | `stdio` | 🟢 Interno | Puente para convertir activos de Unity/Unreal a Blender 5.0 y Godot. |
