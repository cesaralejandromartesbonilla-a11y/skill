# HUB DE SKILLS, HERRAMIENTAS Y ECOSISTEMA MCP

> **Propósito Único y Exclusivo del Proyecto:**  
> Este espacio de trabajo está destinado **única y exclusivamente** al descubrimiento, curación, desarrollo y optimización de **skills para agentes de IA**, **servidores Model Context Protocol (MCP)**, scripts de soporte y **programas externos** que potencien y faciliten la ejecución de tareas automatizadas.

---

## 1. Visión y Alcance Fundamental

Este repositorio funciona como un **laboratorio y banco de herramientas (Tooling & Skill Hub)**. Su objetivo es convertir requerimientos y oportunidades de automatización en capacidades operativas reutilizables para agentes y flujos de trabajo inteligentes.

### Regla de No Desviación (Frontera del Proyecto)
- **Lo que SÍ pertenece aquí:**
  - Creación, prueba y documentación de nuevas *skills*.
  - Búsqueda, evaluación e integración de repositorios y servidores MCP (GitHub, npm, PyPI, Docker).
  - Desarrollo de herramientas de automatización, wrappers CLI y utilidades para interactuar con APIs o el sistema.
  - Benchmarks, comparativas y bitácoras de compatibilidad de herramientas.
- **Lo que NO pertenece aquí:**
  - Código de aplicaciones finales o proyectos de negocio que no actúen como herramientas/skills reutilizables.
  - Almacenamiento indiscriminado de datos no relacionados con el soporte y testing de herramientas.

---

## 2. Pilares de Acción

```
                               ┌─────────────────────────────────┐
                               │   HUB DE SKILLS & TOOLS (IA)   │
                               └────────────────┬────────────────┘
                                                │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
 1. GENERACIÓN DE SKILLS      2. ECOSISTEMA MCP           3. HERRAMIENTAS Y CLIs
 - Prompts estructurados      - Rastreo de repositorios   - Scripts de automatización
 - Formato SKILL.md           - Servidores locales/remotos- Utilidades del SO
 - Scripts de soporte         - Pruebas y sandboxing      - Wrappers e integraciones
```

### Pilar 1: Descubrimiento y Generación de Skills
- Diseñar skills siguiendo las mejores prácticas de la industria:
  - Archivo principal `SKILL.md` con metadata (YAML frontmatter), descripción clara y desencadenantes contextuales.
  - Directorios `scripts/`, `references/` y `examples/` para modularizar la ejecución.
- Reducir la sobrecarga cognitiva del modelo: entregar instrucciones precisas, deterministas y con manejo robusto de errores.

### Pilar 2: Ecosistema MCP (Model Context Protocol)
- Explorar y evaluar servidores MCP comunitarios y oficiales (archivos locales, bases de datos, APIs de terceros, navegadores, herramientas de depuración).
- Documentar:
  - Configuración requerida de variables de entorno y transporte (`stdio`, `sse`).
  - Herramientas (`tools`), recursos (`resources`) y prompts que expone cada servidor.
  - Riesgos de seguridad, permisos y requerimientos de red.

### Pilar 3: Programas y Herramientas Complementarias
- Localizar y adaptar software, CLIs o utilidades de desarrollador que permitan:
  - Inspección de procesos y diagnóstico de sistemas.
  - Manipulación de archivos, formatos y conversión de datos.
  - Automatización de tareas repetitivas a bajo costo computacional.

---

## 3. Estructura de Directorios del Proyecto

```text
skill/
├── README.md                 # Documento maestro de visión y registro (este archivo)
├── skills/                   # Colección de skills desarrolladas o adaptadas
│   └── [nombre-skill]/
│       ├── SKILL.md          # Especificación y prompts de la skill
│       ├── scripts/          # Scripts ejecutables (PowerShell, Python, Node, etc.)
│       └── references/       # Documentación o esquemas de apoyo
├── mcp/                      # Configuraciones y adaptadores de servidores MCP
│   ├── configs/              # Archivos de configuración de ejemplo (JSON/YAML)
│   ├── evaluated/            # Notas y auditorías de MCPs probados
│   └── custom/               # Servidores MCP desarrollados internamente
├── tools/                    # Utilidades auxiliares, scripts de búsqueda y wrappers
│   ├── scrapers/             # Búsqueda automatizada de repositorios/herramientas
│   └── utils/                # Utilidades generales de soporte
├── research/                 # Registros de investigación de repositorios y software
│   └── repos_mcp.md          # Directorio curado de repositorios MCP encontrados
└── archive/                  # Elementos descartados o versiones previas (Punto de Rollback)
```

---

## 4. Criterios de Calidad y Evaluación (Filtros de Aceptación)

Antes de incorporar permanentemente una skill, MCP o herramienta externa, debe superar los siguientes criterios:

| Criterio | Pregunta Clave | Estado Requerido |
| :--- | :--- | :---: |
| **Utilidad Práctica** | ¿Resuelve un problema recurrente o expande una capacidad crítica del agente? | Obligatorio |
| **Ergonomía de Agente** | ¿Las interfaces, parámetros y descripciones son fáciles de invocar por un LLM? | Obligatorio |
| **Seguridad y Privacidad** | ¿Ejecuta código arbitrario o expone credenciales sin aislamiento adecuado? | Seguro / Auditado |
| **Mantenibilidad** | ¿Tiene documentación, dependencias claras o posibilidad de ejecución local? | Obligatorio |
| **Impacto de Contexto** | ¿El esquema de herramientas o tamaño de prompt sobrecarga innecesariamente el contexto? | Optimizado |

---

## 5. Protocolo de Registro y Marcha Atrás (Rollback)

Este documento sirve como **ancla de intención**. Si en algún momento el repositorio comienza a acumular tareas no relacionadas o una herramienta introducida causa inestabilidad o desvío, se debe ejecutar el siguiente protocolo:

### Pasos para Dar Marcha Atrás:
1. **Verificación contra este Manifiesto:**
   - Contrastar el cambio con el *Propósito Único* (Sección 1). Si no es skill, MCP o herramienta de soporte, se rechaza o traslada fuera del workspace.
2. **Aislamiento o Archivo de Elementos Problemáticos:**
   - Mover la carpeta correspondiente hacia `archive/[YYYY-MM-DD]_[nombre_herramienta]/` documentando el motivo en un archivo `REASON.md`.
   - Si se trata de un commit de Git: utilizar `git revert` o restaurar la rama al último estado estable sin alterar la visión base.
3. **Restauración del Estado Limpio:**
   - Comprobar que el directorio raíz mantenga únicamente la estructura definida en la Sección 3.
   - Actualizar la bitácora de investigación (`research/`) para evitar reintentar herramientas o enfoques ya descartados.

---

## 6. Bitácora de Registro Rápido

| Fecha | Acción / Registro | Categoría | Estado / Notas |
| :--- | :--- | :--- | :--- |
| 2026-10-25 | Definición de visión fundacional y documento maestro | Arquitectura | Activo |
| 2026-10-25 | Auditoría y evaluación de la triada inicial (`vercel-labs/skills`, `tt-a1i/archify`, `google-research/harness2`) | Investigación | Documentado en `research/initial_repo_evaluations.md` |
| 2026-10-25 | Investigación de pipeline y herramientas para conversión de assets de motores (Unreal, Unity, etc.) a Blender 5.0 | Herramientas | Documentado en `research/game_engine_asset_converters.md` |
| 2026-10-25 | Pipeline de Unity implementado (`tools/unity_asset_extractor.py`) con UnityPy y soporte OBJ/PNG | Herramientas | Operativo |
| 2026-10-25 | Puente intermediario de Blender 5.0 (`tools/blender_universal_bridge.py`) y orquestador CLI (`tools/asset_converter.py`) | Herramientas | Operativo |
| 2026-10-25 | Creación de la skill unificada `skills/universal-asset-porter` | Skills | Operativo |
| 2026-10-25 | Auditoría y evaluación del Lote 2 (`emulate`, `ponytail`, `superpowers`, `agent-browser`) | Investigación | Documentado en `research/batch2_repo_evaluations.md` |
| 2026-10-25 | Adopción de la suite `ponytail` (6 skills YAGNI) y skills metodológicas de `superpowers` (`writing-skills`, TDD, etc.) | Skills | Operativo |
| 2026-10-25 | Creación de la skill `dual-roadmap` (hojas de ruta técnicas exhaustivas y ejecutivas resumidas) con sincronizador | Skills | Operativo en `skills/dual-roadmap` |
| 2026-10-26 | Generación y publicación de la Hoja de Ruta Dual del proyecto (`ROADMAP_DETAILED.md` y `ROADMAP_EXECUTIVE.md`) | Planificación | 50.0% completitud global |
| 2026-10-26 | Evaluación del Lote 3 (`claude-mem`, `impeccable`), adopción de la skill `impeccable` e integración nativa de `claude-mem` en Antigravity | Memoria & UI | 5 hooks y MCP configurados |
| 2026-10-26 | Cierre completo de la Fase 3: Catálogo MCP formal (`catalog.json`), auditorías de seguridad, `tools/mcp_manager.py` y runner de sandbox con `emulate` | Ecosistema MCP | Fase 3 al 100% (66.7% global) |
| 2026-10-26 | Cierre completo de la Fase 4: Auto-refinamiento recursivo de skills con Harness² (`harness2_implementation_guide.md`), validador (`tools/validate_skill.py`), benchmark de contexto (`tools/benchmark_skills.py`) y reflector continuo (`research/lessons_learned.md`) | Auto-Refinamiento | Fase 4 al 100% (80.0% global) |
| 2026-10-25 | Integración del CLI universal `skills` y adopción de la skill de producción `archify` en `skills/archify` | Skills | Operativo |
| 2026-10-25 | Creación de la herramienta de exploración de ecosistema `tools/search_ecosystem.py` | Herramientas | Operativo |

