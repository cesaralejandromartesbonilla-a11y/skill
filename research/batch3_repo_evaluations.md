# EVALUACIÓN DE REPOSITORIOS: LOTE 3 (MEMORIA PERSISTENTE Y DISEÑO UI DE ÉLITE)

> **Fecha:** 2026-10-26  
> **Repositorios Evaluados:**
> 1. `thedotmack/claude-mem` (Memoria persistente entre sesiones)
> 2. `pbakaus/impeccable` (Artesanía visual, sistema de diseño y UI anti-slop)

---

## 1. Visión Global del Lote

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MAPA DE CAPACIDADES (LOTE 3)                    │
├────────────────────────────────┬───────────────────────────────────────┤
│  1. MEMORIA CONTINUA Y CONTEXTO│  2. CRAFTSMANSHIP Y DISEÑO FRONTEND   │
│     thedotmack/claude-mem      │     pbakaus/impeccable                │
│  • Persistencia entre sesiones │  • Solución al "AI design slop"       │
│  • Base vectorial + SQLite FTS5│  • Modos: Persuade, Operate, Read     │
│  • Soporte NATIVO Antigravity  │  • Suelo de calidad (Craft Floor)     │
│  • Servidor MCP + Hooks        │  • Auditoría visual y tokens DESIGN.md│
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Análisis Detallado por Repositorio

### A. `thedotmack/claude-mem`
- **URL:** [https://github.com/thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- **Autor:** Alex Newman (`thedotmack`)
- **Categoría:** Sistema de Compresión de Memoria y Contexto Persistente / Servidor MCP / Hooks de Ciclo de Vida.
- **Problema que resuelve:** Los modelos y agentes sufren de amnesia entre sesiones: cada vez que se abre un nuevo chat o se reinicia la tarea, el agente olvida decisiones pasadas, errores corregidos, arquitectura establecida y requiere re-explicar el contexto gastando miles de tokens repetidos.
- **¿Funciona en Antigravity?:** **SÍ, TIENE SOPORTE NATIVO DE PRIMERA CLASE.**
  - En su CLI incorpora el comando explícito:
    ```bash
    npx claude-mem antigravity-cli install|status|uninstall
    npx claude-mem install --ide antigravity
    ```
  - Registra hooks de ciclo de vida compatibles en `~/.gemini/config/hooks.json` (`SessionStart`, `PostToolUse`).
  - Proporciona un servidor MCP por estándar `stdio`:
    ```bash
    npx claude-mem mcp
    ```
- **Arquitectura Interna:**
  - **Worker Daemon (Bun/Node):** Servidor HTTP local en segundo plano (puerto `37700+`).
  - **Capa de Almacenamiento:** Base de datos relacional SQLite (con búsqueda por texto completo FTS5) combinada con base de datos vectorial Chroma para búsqueda híbrida semántica.
  - **Compresión Asíncrona:** Cuando el agente ejecuta herramientas y edita archivos, los eventos se comprimen mediante LLM en notas atómicas eficientes sin frenar la sesión interactiva.
- **Estado en el Hub:** Documentado e integrado mediante compatibilidad Antigravity CLI y servidor MCP.

---

### B. `pbakaus/impeccable`
- **URL:** [https://github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable)
- **Autor:** Paul Bakaus (Ex-director de Developer Experience en Google y Apple, creador de jQuery UI).
- **Categoría:** Suite de Skills y Lenguaje de Diseño Frontend para Agentes de IA (`SKILL.md`).
- **Problema que resuelve:** Los agentes de IA generan interfaces frontend predecibles, genéricas y sin contraste ("AI design slop"): botones azules genéricos, tipografía sin jerarquía, espaciados rotos en móvil y falta de pulido estético.
- **Capacidades Clave:**
  - **Craft Floor (Suelo de Calidad):** Lista estricta de prohibiciones y reflejos que impiden entregar interfaces a medio hacer o con errores de contraste/accesibilidad.
  - **Comandos Especializados:**
    - `shape`: Planificar la UX y wireframes antes de escribir una sola línea de código.
    - `document`: Analizar el código existente y extraer la identidad visual a `DESIGN.md`.
    - `extract`: Extraer tokens reutilizables y paleta a un sistema de diseño estructurado.
    - `critique`: Auditoría visual de UX con puntuación heurística.
  - **Modos de Diseño según el Propósito:**
    - *Persuade:* Landing pages y marketing (audacia visual, conversión).
    - *Operate:* Dashboards y herramientas (escaneabilidad, ergonomía y orden estricto).
    - *Read:* Blogs y documentación (legibilidad y confort visual).
    - *Experience:* Portafolios y galerías (artefacto protagónico).
- **Estado en el Hub:** Adoptado e instalado en `skills/impeccable/`.

---

## 3. Matriz de Integración en el Hub

| Elemento | Tipo | Destino | Estado |
| :--- | :--- | :--- | :---: |
| `pbakaus/impeccable` | Skill de Frontend y Diseño | `skills/impeccable/` | Instalada y Operativa |
| `thedotmack/claude-mem` | Memoria y Hooks de Antigravity | `npx claude-mem` + `hooks.json` | Configurado |
| `claude-mem mcp` | Servidor MCP Stdio | `mcp/claude-mem/` (vía `npx claude-mem mcp`) | Preparado |
