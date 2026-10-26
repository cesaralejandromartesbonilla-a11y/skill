# HOJA DE RUTA DETALLADA (LIVING TECHNICAL ROADMAP)

> **Proyecto:** Hub de Descubrimiento, Generación de Skills y Ecosistema MCP  
> **Última Actualización:** 2026-10-26  
> **Estado General:** `[En Progreso]`  
> **Versión del Plan:** v1.0.0  
> **Documento Resumido:** [Ver Hoja de Ruta Ejecutiva](ROADMAP_EXECUTIVE.md)

---

## 1. Visión y Objetivos Fundamentales

- **Misión Exclusiva:** Descubrir, evaluar, estructurar y generar *skills*, herramientas auxiliares y servidores MCP que expandan y optimicen las capacidades de agentes de IA, utilizando **Blender 5.0 headless** como intermediario para activos 3D y frameworks de calidad contrastiva (`Harness²`, `Superpowers`, `Ponytail`).
- **Entregables Principales:**
  - [X] Repositorio base con control estricto de marcha atrás (Git rollback anchor).
  - [X] Herramienta CLI de búsqueda de ecosistema (`tools/search_ecosystem.py`).
  - [X] Pipeline completo de extracción de Unity y puente con Blender 5.0 (`universal-asset-porter`).
  - [X] Suite de metodologías de ingeniería y minimalismo (`superpowers`, `ponytail`, `writing-skills`).
  - [X] Sistema de planificación dual (`skills/dual-roadmap`).
  - [ ] Catálogo curado y servidores MCP operativos en `mcp/`.
  - [ ] Framework de auto-mejora y generación de skills basado en `Harness²`.
  - [ ] Módulo de automatización web y Electron optimizado para LLMs (`agent-browser`).

---

## 2. Desglose Exhaustivo por Fases (WBS)

### Fase 1: Cimientos, Descubrimiento e Infraestructura Base `[Completada]`
> **Objetivo de la Fase:** Establecer el repositorio, las reglas inalterables de alcance, herramientas de descubrimiento de skills/MCP y adoptar las primeras referencias arquitectónicas.  
> **Progreso:** 10/10 Tareas Completadas (100%)

- [X] **[F1-T01] Manifiesto fundacional y protocolo de rollback**
  - **Descripción:** Redacción de `README.md`, configuración de `.gitignore` e inicialización de repositorio Git con commit ancla para reversión segura.
  - **Archivos:** `README.md`, `.gitignore`, `.git/`
  - **Criterio de Aceptación:** Repositorio limpio y auditable con reglas de no desviación.

- [X] **[F1-T02] Herramienta CLI de exploración de ecosistema**
  - **Descripción:** Creación de script para buscar skills comunitarias (`skills.sh`) y servidores MCP en GitHub API con soporte UTF-8 en Windows.
  - **Archivos:** `tools/search_ecosystem.py`
  - **Criterio de Aceptación:** Búsqueda funcional vía `python tools/search_ecosystem.py [skills|mcp|trending-mcp]`.

- [X] **[F1-T03] Auditoría y evaluación de la triada inicial**
  - **Descripción:** Análisis técnico y sinergia de `vercel-labs/skills`, `tt-a1i/archify` y `google-research/harness2`.
  - **Archivos:** `research/initial_repo_evaluations.md`
  - **Criterio de Aceptación:** Documento técnico con matriz de adopción y roles.

- [X] **[F1-T04] Adopción de skill de diagramación determinista**
  - **Descripción:** Instalación y adaptación de `archify` con compilador Node.js y esquemas JSON IR.
  - **Archivos:** `skills/archify/`
  - **Criterio de Aceptación:** Presencia de `SKILL.md`, `bin/archify.mjs` y esquemas.

- [X] **[F1-T05] Evaluación del Lote 2 de herramientas y frameworks**
  - **Descripción:** Investigación técnica de `vercel-labs/emulate`, `DietrichGebert/ponytail`, `obra/superpowers` y `vercel-labs/agent-browser`.
  - **Archivos:** `research/batch2_repo_evaluations.md`
  - **Criterio de Aceptación:** Matriz de 4 frentes (disciplina, YAGNI, sandbox local y navegación web).

- [X] **[F1-T06] Integración de la suite de minimalismo de código (YAGNI)**
  - **Descripción:** Incorporación de las 6 skills de `ponytail` para evitar sobre-ingeniería en tareas de desarrollo.
  - **Archivos:** `skills/ponytail*`
  - **Criterio de Aceptación:** Skills `ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, etc. operativas.

- [X] **[F1-T07] Integración de metodologías de ingeniería de software para agentes**
  - **Descripción:** Adopción de skills nucleares de `superpowers` (`writing-skills`, `test-driven-development`, `verification-before-completion`, `systematic-debugging`, `using-git-worktrees`).
  - **Archivos:** `skills/writing-skills/`, `skills/test-driven-development/`, etc.
  - **Criterio de Aceptación:** Especificaciones formales listas para guiar la creación de futuras skills.

- [X] **[F1-T08] Creación de la skill de planificación dual (`dual-roadmap`)**
  - **Descripción:** Desarrollo de la skill para mantener en paralelo una hoja técnica exhaustiva viva y un resumen ejecutivo visual, con script de cálculo Unicode.
  - **Archivos:** `skills/dual-roadmap/SKILL.md`, `templates/`, `scripts/sync_roadmaps.py`
  - **Criterio de Aceptación:** Script de sincronización funcional y plantillas normalizadas.

- [X] **[F1-T09] Integración de memoria persistente entre sesiones (`claude-mem`)**
  - **Descripción:** Integración nativa de `claude-mem` en Antigravity con 5 hooks de ciclo de vida (`SessionStart`, `PreToolUse`, `PostToolUse`, `PostInvocation`, `Stop`) y configuración de servidor MCP.
  - **Archivos:** `~/.gemini/config/hooks.json`, `~/.gemini/config/mcp_config.json`, `research/batch3_repo_evaluations.md`
  - **Criterio de Aceptación:** Estado verificado con `claude-mem antigravity-cli status` (5/5 eventos mapeados y MCP registrado).

- [X] **[F1-T10] Adopción de la suite de diseño UI y calidad artesanal (`impeccable`)**
  - **Descripción:** Incorporación del framework de Paul Bakaus para elevar el listón visual y de UX en componentes web, dashboards y landing pages, eliminando el "AI design slop".
  - **Archivos:** `skills/impeccable/` (`SKILL.md`, `reference/`, `agents/`, `scripts/`)
  - **Criterio de Aceptación:** Modos Persuade, Operate, Read y comandos `shape`, `critique`, `document`, `extract` disponibles.

---

### Fase 2: Suite de Conversión e Interoperabilidad 3D (Blender 5.0) `[Completada]`
> **Objetivo de la Fase:** Proporcionar un pipeline unificado para convertir activos de motores (Unity, Unreal Engine, Source) mediante Blender 5.0 headless y exportarlos a Godot 4.6 (glTF/GLB) y otros destinos.  
> **Progreso:** 8/8 Tareas (100%)

- [X] **[F2-T01] Investigación y arquitectura de conversión multi-motor**
  - **Descripción:** Mapeo de formatos y herramientas por motor (UModel, FModel, AssetRipper, AssetStudio, UnityPy, Noesis, RenderDoc).
  - **Archivos:** `research/game_engine_asset_converters.md`
  - **Criterio de Aceptación:** Diagnóstico del entorno local de Blender 5.0 y tabla comparativa.

- [X] **[F2-T02] Extractor headless para activos de Unity**
  - **Descripción:** Script CLI basado en `UnityPy` para extraer mallas (`Mesh` a `.obj` corregido), texturas (`Texture2D` a `.png`) y audio sin abrir Unity.
  - **Archivos:** `tools/unity_asset_extractor.py`
  - **Criterio de Aceptación:** Soporte de comandos `list` y `extract` con decodificación DXT/ASTC/ETC.

- [X] **[F2-T03] Puente intermediario de Blender 5.0 Headless**
  - **Descripción:** Script Python para ejecución headless en Blender 5.0 con soporte de mallas (.obj, .fbx, .psk, .uemodel), inversión de normales DirectX a OpenGL, eliminación de máscaras de vertex colors, materiales PBR y Slotted Actions.
  - **Archivos:** `tools/blender_universal_bridge.py`
  - **Criterio de Aceptación:** Ejecución no interactiva con `blender.exe -b --python`.

- [X] **[F2-T04] Orquestador CLI unificado de activos**
  - **Descripción:** CLI de alto nivel para ejecutar conversiones en un solo paso (`port`, `unity-dump`, `unity-to-glb`, `source-to-glb`).
  - **Archivos:** `tools/asset_converter.py`
  - **Criterio de Aceptación:** Conversión de Unity/Source a GLB en un solo comando.

- [X] **[F2-T05] Skill formal `universal-asset-porter`**
  - **Descripción:** Documentación estandarizada en formato `SKILL.md` para que cualquier agente opere el pipeline de conversión.
  - **Archivos:** `skills/universal-asset-porter/SKILL.md`
  - **Criterio de Aceptación:** Guía operativa completa con ejemplos para criaturas, foliage y props.

- [X] **[F2-T06] Banco de pruebas y validación con assets reales de Unity**
  - **Descripción:** Extracción, remapeo esquelético a rig Kobold de 70 huesos, PBR y 7 animaciones desde `C:\KoboldKare`, empaquetando en `export/kobold_godot_ready.glb`.
  - **Archivos:** `tools/kobold_pipeline_builder.py`, `tools/verify_glb.py`, `export/kobold_godot_ready.glb`
  - **Criterio de Aceptación:** Archivo `.glb` validado estructuralmente y listo para Godot 4.6.

- [X] **[F2-T07] Extensión para Valve Source / Source 2 (SourceIO)**
  - **Descripción:** Integrar el flujo de importación de modelos (`.mdl`, `.vmdl`, `.smd`, `.dmx`) al orquestador `tools/asset_converter.py` y al puente `tools/blender_universal_bridge.py`.
  - **Archivos:** `tools/asset_converter.py`, `tools/blender_universal_bridge.py`
  - **Criterio de Aceptación:** Comando `source-to-glb` y detección de operadores Valve disponible.

- [X] **[F2-T08] Guía y workflow para captura directa de VRAM (RenderDoc)**
  - **Descripción:** Documentar y automatizar el volcado de mallas cuando los archivos del juego están cifrados o en formatos propietarios desconocidos.
  - **Archivos:** `research/renderdoc_vram_ripping.md`
  - **Criterio de Aceptación:** Protocolo paso a paso probado para extraer geometría desde GPU draw-calls.

---

### Fase 3: Ecosistema y Servidores MCP (Model Context Protocol) `[Completada]`
> **Objetivo de la Fase:** Evaluar, catalogar e integrar servidores MCP locales y remotos para dotar a los agentes de capacidades de inspección de código, base de datos y depuración sin riesgo.  
> **Progreso:** 5/5 Tareas (100%)

- [X] **[F3-T01] Estructura del Catálogo MCP y Plantilla Base**
  - **Descripción:** Definición de la estructura de carpetas en `mcp/`, catálogo centralizado `mcp/catalog.json`, plantillas de auditoría y CLI `tools/mcp_manager.py`.
  - **Archivos:** `mcp/README.md`, `mcp/catalog.json`, `mcp/templates/`, `mcp/configs/`, `tools/mcp_manager.py`
  - **Criterio de Aceptación:** Estándar claro para registrar, auditar y exportar configuraciones a Antigravity.

- [X] **[F3-T02] Integración y auditoría de Chrome DevTools MCP**
  - **Descripción:** Evaluación, auditoría de seguridad y configuración de `ChromeDevTools/chrome-devtools-mcp` para inspección en tiempo real de páginas web, consolas y red con aislamiento (`--isolated`) y telemetría desactivada.
  - **Archivos:** `mcp/configs/chrome-devtools.json`, `mcp/evaluated/chrome-devtools.md`, `mcp/catalog.json`
  - **Criterio de Aceptación:** Auditoría completada, reporte técnico generado y configuración lista para importación.

- [X] **[F3-T03] Integración y auditoría de Codebase Memory MCP**
  - **Descripción:** Evaluación técnica de `DeusData/codebase-memory-mcp` para indexación de árboles sintácticos (Tree-sitter) y grafos de llamadas locales en SQLite, reduciendo el consumo de tokens en repositorios grandes.
  - **Archivos:** `mcp/configs/codebase-memory.json`, `mcp/evaluated/codebase-memory.md`, `mcp/catalog.json`
  - **Criterio de Aceptación:** Auditoría aprobada, reporte generado y configuración lista.

- [X] **[F3-T04] Sandbox y Emulación Local con `vercel-labs/emulate`**
  - **Descripción:** Herramienta de sandbox local (`tools/sandbox_runner.py`) para emular 14 servicios externos (GitHub, AWS, Stripe, Slack) con estado persistente, permitiendo probar servidores MCP sin gastar saldo ni exponer credenciales.
  - **Archivos:** `tools/sandbox_runner.py`, `research/batch2_repo_evaluations.md`
  - **Criterio de Aceptación:** Servidor mock ejecutable y verifiable con `check` y `start`.

- [X] **[F3-T05] Generador y exportador de configuraciones MCP (`tools/mcp_manager.py`)**
  - **Descripción:** Herramienta CLI para consultar el catálogo, inspeccionar esquemas y exportar automáticamente bloques consolidados `mcpServers` para Antigravity, Claude Code y Cursor.
  - **Archivos:** `tools/mcp_manager.py`, `mcp/configs/`
  - **Criterio de Aceptación:** Comando `python tools/mcp_manager.py export --target antigravity` funcional.

---

### Fase 4: Generación y Refinamiento Recursivo de Skills (Harness² Loop) `[Completada]`
> **Objetivo de la Fase:** Implementar la ciencia de arneses de `google-research/harness2` para que el hub pueda generar, probar y optimizar sus propias skills de forma semi-autónoma.  
> **Progreso:** 4/4 Tareas (100%)

- [X] **[F4-T01] Adaptación del ciclo Propose–Probe–Compose**
  - **Descripción:** Diseñar el flujo de trabajo donde el agente propone cambios en sus componentes (prompt, guardrails, scripts), los prueba contra tareas de muestra y compone la versión mejorada.
  - **Archivos:** `research/harness2_implementation_guide.md`
  - **Criterio de Aceptación:** Flujo de optimización contrastiva documentado y ejecutable.

- [X] **[F4-T02] Validador y Quality Gates para `SKILL.md`**
  - **Descripción:** Herramienta que audita automáticamente si una nueva skill cumple con: descripción tipo "Use when...", ausencia de spoilers de flujo, pruebas TDD y frontmatter YAML válido.
  - **Archivos:** `tools/validate_skill.py`, `tests/test_validate_skill.py`
  - **Criterio de Aceptación:** Script que valida sintaxis y reglas de Anthropic/Superpowers.

- [X] **[F4-T03] Banco de Pruebas de Desempeño de Skills (Benchmark)**
  - **Descripción:** Medir el impacto de las skills instaladas en consumo de tokens, número de pasos de resolución y tasa de éxito en tareas complejas.
  - **Archivos:** `tools/benchmark_skills.py`, `research/benchmarks/skills_footprint_report.md`
  - **Criterio de Aceptación:** Reporte comparativo de ahorro y precisión.

- [X] **[F4-T04] Biblioteca de Lecciones Aprendidas (Experience Reflector)**
  - **Descripción:** Registro centralizado de patrones exitosos y errores comunes observados durante el uso de herramientas en el workspace.
  - **Archivos:** `research/lessons_learned.md`
  - **Criterio de Aceptación:** Documento vivo de retroalimentación acumulativa.

---

### Fase 5: Automatización de Navegación Web y Desktop (`agent-browser`) `[Completada]`
> **Objetivo de la Fase:** Integrar capacidades de navegación ultraligera para agentes basadas en árboles de accesibilidad y control de aplicaciones Electron.  
> **Progreso:** 3/3 Tareas (100%)

- [X] **[F5-T01] Setup y Wrapper Local de `agent-browser`**
  - **Descripción:** Configurar el demonio en segundo plano de `agent-browser` y crear un wrapper de soporte para interactuar con snapshots compactos (`@e1`, `@e2`).
  - **Archivos:** `tools/agent_browser_runner.py`, `tests/test_agent_browser_runner.py`
  - **Criterio de Aceptación:** Comandos de navegación funcionando con un consumo menor al 10% de tokens frente a HTML tradicional.

- [X] **[F5-T02] Skill de Exploración y Auditoría Web (`web-dogfooding`)**
  - **Descripción:** Crear una skill para que el agente navegue sistemáticamente por una aplicación web, detecte errores de consola, enlaces rotos y problemas de UX.
  - **Archivos:** `skills/web-dogfooding/SKILL.md`, `skills/web-dogfooding/templates/dogfood_report_template.md`
  - **Criterio de Aceptación:** Flujo de prueba autónomo documentado.

- [X] **[F5-T03] Skill de Automatización de Aplicaciones Electron**
  - **Descripción:** Aprovechar el soporte de `agent-browser` para interactuar con clientes de escritorio basados en Chromium/Electron (VS Code, Discord, Slack).
  - **Archivos:** `skills/electron-automator/SKILL.md`, `skills/electron-automator/scripts/launch_electron_cdp.py`
  - **Criterio de Aceptación:** Capacidad demostrada de interacción con apps Electron.

---

## 3. Matriz de Riesgos y Mitigaciones

| ID | Riesgo Identificado | Severidad | Mitigación Planificada | Estado |
| :---: | :--- | :---: | :--- | :---: |
| **R1** | Incompatibilidad de scripts con futuras versiones de Blender (6.x o cambios de API) | Media | Uso exclusivo de APIs públicas y aislamiento de lógica en `tools/blender_universal_bridge.py`. | Controlado |
| **R2** | Desbordamiento de contexto al evaluar páginas web o repositorios masivos | Alta | Uso estricto de `agent-browser` (árbol de accesibilidad) y clonaciones superficiales (`--depth 1`). | Mitigado |
| **R3** | Alucinación o sobre-ingeniería en la generación de código | Media | Aplicación obligatoria de `skills/ponytail` (YAGNI) y `skills/verification-before-completion`. | Mitigado |
| **R4** | Falsos positivos en servidores MCP externos no auditados | Alta | Ejecución en sandbox local mediante `vercel-labs/emulate` antes de habilitar permisos del sistema. | Monitoreado |

---

## 4. Registro de Deuda Técnica y Atajos

| Fecha | Componente / Área | Atajo Tomado | Plan de Refactorización |
| :--- | :--- | :--- | :--- |
| 2026-10-25 | Unity Extractor | Exportación OBJ manual si `data.export()` falla | Añadir exportador glTF nativo directo en Python si se requiere jerarquía completa de nodos. |
| 2026-10-25 | Blender Bridge | Carga de texturas PBR basada en rutas por parámetro CLI | Implementar detección heurística automática de texturas por sufijos (`_d`, `_n`, `_m`, `_r`). |

---

## 5. Bitácora de Cambios del Plan (Change Log)

- **2026-10-26 (v2.0.0):** Fase 2 completada (100%). Validación exitosa con caso real de Unity (`tools/kobold_pipeline_builder.py`, modelo `export/kobold_godot_ready.glb` con rig de 70 huesos, PBR y 7 animaciones verificado con `tools/verify_glb.py`), integración de soporte para Valve Source Engine (`source-to-glb` y formatos `.smd`, `.dmx`, `.mdl`), y protocolo completo de ripping directo desde GPU VRAM con RenderDoc (`research/renderdoc_vram_ripping.md`). **Progreso Global del Proyecto: 100.0% (30/30 Tareas)**.
- **2026-10-26 (v1.3.0):** Fase 5 (100% completada). Creados e implementados: runner/wrapper programático de `agent-browser` (`tools/agent_browser_runner.py`), skill de auditoría web y pruebas exploratorias (`skills/web-dogfooding`), plantilla de reporte (`skills/web-dogfooding/templates/dogfood_report_template.md`), skill de control de clientes Electron (`skills/electron-automator`) y launcher CDP (`skills/electron-automator/scripts/launch_electron_cdp.py`). Progreso global alcanzado: **90.0%**.
- **2026-10-26 (v1.2.0):** Fase 4 (100% completada). Creados e implementados: guía conceptual de Harness² (`research/harness2_implementation_guide.md`), validador automático de skills (`tools/validate_skill.py`), suite de benchmark y reporte de huella de tokens (`tools/benchmark_skills.py`, `research/benchmarks/skills_footprint_report.md`), y repositorio continuo de lecciones aprendidas (`research/lessons_learned.md`).
- **2026-10-26 (v1.1.0):** Fase 3 (100% completada). Catálogo formal MCP, audits de seguridad, sandbox `emulate` y CLI `mcp_manager.py`.
- **2026-10-26 (v1.0.0):** Publicación inicial de la hoja de ruta exhaustiva. Fases 1 (100%) y 2 (62.5%) consolidadas; Fases 3, 4 y 5 formalizadas con objetivos WBS claros.
