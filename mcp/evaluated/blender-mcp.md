# Evaluación Técnica: Blender MCP (`sandraschi/blender-mcp`)

## 1. Resumen Ejecutivo
- **Repositorio:** [github.com/sandraschi/blender-mcp](https://github.com/sandraschi/blender-mcp)
- **Licencia:** MIT
- **Propósito:** Servidor FastMCP para control, automatización y generación 3D en Blender mediante agentes de IA y lenguaje natural.
- **Estado de Evaluación:** Aprobado e integrado en `mcp/catalog.json`.

---

## 2. Arquitectura y Capacidades
`blender-mcp` opera bajo dos modos de ejecución:
1. **Modo Headless (por defecto):**
   - Ejecuta `blender.exe --background --python` en un subproceso local.
   - Ideal para pipelines batch, CI/CD, baking de animaciones, exportación de `.glb` y procesamiento de assets sin interfaz gráfica.
2. **Modo Live Viewport (GUI interactiva):**
   - Mediante el addon oficial `addon/blender_bridge_addon.py` instalado en Blender.
   - Conexión vía socket bidireccional local que actualiza la escena en tiempo real mientras el agente opera.

### Módulos de Herramientas Destacadas (150+ Tools):
- **Rigging & Armatures (`rigging/`):** Generación de armaduras, emparejamiento con pesos automáticos, creación de restricciones (`IK`, `Copy Transform`, `Damped Track`).
- **Animation (`animation/`):** Creación de keyframes, manipulación de curvas F, baking de NLA tracks, retargeting automático.
- **Materials & Shading (`materials/`, `shader_tools.py`):** Configuración de Principled BSDF, conexión de mapas PBR (Base Color, Normal, Metallic, Roughness, Emission) y baking de texturas.
- **Mesh & Geometry (`mesh/`, `modifiers/`):** Operaciones booleanas, subdivisión, unwrap UV y deformación.
- **Export & Optimization (`export/`, `export_presets_tools.py`):** Presets de exportación para Godot 4, glTF 2.0, FBX y compresión Draco.

---

## 3. Configuración para Antigravity / Claude Desktop
```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "BLENDER_EXECUTABLE": "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"
      }
    }
  }
}
```

---

## 4. Aplicabilidad al Proyecto Actual
- Permite invocar herramientas directas de rigging, unwrap y baking sin necesidad de escribir scripts de Blender ad-hoc desde cero.
- Complementa directamente las fases de conversión Ark/Unreal -> Godot y Unity -> Godot.
