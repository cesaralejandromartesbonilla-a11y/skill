# REPORTE DE AUDITORÍA DE SERVIDOR MCP: Codebase Memory MCP

> **Identificador:** `codebase-memory`  
> **Fecha de Auditoría:** 2026-10-26  
> **Auditor:** Agente Antigravity  
> **Resultado:** 🟢 Aprobado para uso local

---

## 1. Ficha Técnica

- **Repositorio:** [https://github.com/DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)
- **Organización:** DeusData
- **Transporte:** `stdio`
- **Categoría:** Inteligencia de Código y Grafos de Conocimiento (`code-intelligence`)
- **Propósito Principal:** Indexar la arquitectura, árboles sintácticos (Tree-sitter) y grafos de llamadas de un proyecto en una base SQLite local para que el agente consulte relaciones estructurales sin saturar la ventana de contexto.

---

## 2. Evaluación de Seguridad y Privacidad

| Criterio | Pregunta | Evaluación | Notas |
| :--- | :--- | :---: | :--- |
| **Aislamiento de Archivos** | ¿El servidor puede leer/escribir fuera del directorio designado? | Local | Solo indexa el workspace indicado en los argumentos de ejecución. |
| **Manejo de Credenciales** | ¿Requiere tokens o contraseñas? | Seguro | Opera 100% offline sin necesidad de API keys externas. |
| **Ejecución Arbitraria** | ¿Permite ejecución de código arbitrario (RCE)? | No detectado | Es un motor de indexación de solo lectura sobre el código fuente. |
| **Comportamiento de Red** | ¿Realiza llamadas a servidores remotos? | No | Base de datos local SQLite; el código nunca sale de la máquina. |

---

## 3. Inventario de Herramientas Expuestas

| Herramienta | Parámetros Principales | Nivel de Riesgo | Uso Permitido |
| :--- | :--- | :---: | :--- |
| `query_architecture` | `query`, `depth` | Bajo | Consulta de alto nivel sobre la relación de módulos y paquetes. |
| `find_symbol_definition` | `name`, `language` | Bajo | Localización instantánea de clases, interfaces y funciones sin grep. |
| `trace_dependencies` | `filePath`, `direction` | Bajo | Rastreo de dependencias ascendentes y descendentes (call graph). |
| `manage_adr` | `action`, `title` | Bajo | Gestión de Architecture Decision Records. |

---

## 4. Configuración Recomendada para Antigravity

```json
{
  "codebase-memory": {
    "command": "npx",
    "args": [
      "-y",
      "codebase-memory-mcp@latest"
    ],
    "env": {}
  }
}
```
