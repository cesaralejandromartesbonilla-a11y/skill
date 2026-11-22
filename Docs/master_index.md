# Índice Maestro de Documentación y Recursos del Workspace

> **Workspace:** `c:\Users\cesar\Desktop\skill`  
> **Propósito:** Hub de arquitectura de agentes, herramientas de automatización, skills y error ledger.

---

## 1. Módulos de Documentación Rápida

| Módulo | Descripción | Ruta del Documento |
| :--- | :--- | :--- |
| **Error Ledger** | Registro formal de errores históricos, causa raíz y soluciones probadas. | [Docs/error_ledger/index.md](file:///c:/Users/cesar/Desktop/skill/Docs/error_ledger/index.md) |
| **Aprovisionamiento Godot AI** | Instalación y configuración en un solo disparo de `addons/godot_ai` en proyectos Godot. | [Docs/pipelines/godot_ai_setup.md](file:///c:/Users/cesar/Desktop/skill/Docs/pipelines/godot_ai_setup.md) |
| **Pipeline 3D Headless** | Guía de uso de `pipeline_3d_repair_export.py` (Blender 5.0 a Godot). | [Docs/pipelines/pipeline_3d.md](file:///c:/Users/cesar/Desktop/skill/Docs/pipelines/pipeline_3d.md) |
| **Andamiaje Godot** | Generación de escenas `.tscn` y plantillas de un solo disparo con `godot_scene_scaffolder.py`. | [Docs/pipelines/godot_scaffolding.md](file:///c:/Users/cesar/Desktop/skill/Docs/pipelines/godot_scaffolding.md) |
| **Arquitectura Modular** | Reglas de desacoplamiento estricto, interfaces limpias y límite de 300 líneas. | [Docs/architecture/modular_rules.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/modular_rules.md) |
| **Alineación Espacial** | Normalización de pivotes en base inferior ($Y=0$) y mapeo de canales PBR/ORM. | [Docs/architecture/spatial_alignment.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/spatial_alignment.md) |
| **Hojas de Ruta Jerárquicas** | Estándar Etapa $\to$ Fase $\to$ Paso y Paradigma de la Torre Eiffel (Cero Apresuramiento). | [Docs/architecture/hierarchical_roadmap_standard.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/hierarchical_roadmap_standard.md) |
| **Fidelidad Morfológica 3D** | Protocolo anatómico de 4 puertas y prohibición de primitivas/cilindros absurdos. | [Docs/architecture/functional_3d_anatomy_guide.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/functional_3d_anatomy_guide.md) |
| **Recreación de Mecánicas** | Protocolo matemático de ingeniería inversa y matriz de fusión (RETAIN, REPLACE, FUSE). | [Docs/game_mechanics/fusion_matrix.md](file:///c:/Users/cesar/Desktop/skill/Docs/game_mechanics/fusion_matrix.md) |

---

## 2. Scripts Clave de Automatización (`tools/`)

- [`tools/setup_godot_ai_addon.py`](file:///c:/Users/cesar/Desktop/skill/tools/setup_godot_ai_addon.py): Aprovisionador e instalador automatizado del addon `godot_ai` en `project.godot`.
- [`tools/pipeline_3d_repair_export.py`](file:///c:/Users/cesar/Desktop/skill/tools/pipeline_3d_repair_export.py): Reparación, pivote $Y=0$, normales y traslado de mallas 3D a Godot.
- [`tools/godot_scene_scaffolder.py`](file:///c:/Users/cesar/Desktop/skill/tools/godot_scene_scaffolder.py): Generador de escenas `.tscn` atómicas (props, character controller, UI).
- [`tools/blender_universal_bridge.py`](file:///c:/Users/cesar/Desktop/skill/tools/blender_universal_bridge.py): Puente headless de Blender 5.0 con soporte PBR/ORM.
