# Registro Histórico de Errores (Error Ledger)

Catálogo formal de errores no triviales, diagnósticos de causa raíz y soluciones probadas. Los agentes deben consultar este índice antes de intentar diagnosticar o parchear problemas similares.

---

## Índice Rápido de Casos

| Código | Título | Entorno | Causa Raíz Resumida | Enlace |
| :--- | :--- | :--- | :--- | :--- |
| **[ERR-001]** | Deformación "Candy-Wrapper" en Huesos | Blender 5.0 | Discrepancia de roll de reposo en constraints de rotación | [Detalles](#err-001) |
| **[ERR-002]** | Destello Blanco Fluorescente (Emission Blowout) | Blender / glTF | `Emission Strength` default > 0 en Principled BSDF | [Detalles](#err-002) |
| **[ERR-003]** | Desincronización de Ejes FBX | Blender / FBX | Falta de aplicación de transformaciones (`Ctrl+A`) | [Detalles](#err-003) |
| **[ERR-004]** | Fatiga por Micro-Llamadas Atómicas MCP | Antigravity / Godot | Abstracción atómica de MCPs en lugar de pipelines macro | [Detalles](#err-004) |

---

### [ERR-001] Deformación "Candy-Wrapper" en Huesos por Incompatibilidad de Roll
- **Síntoma:** Extremidades estranguladas, codos y rodillas pellizcados a radio cero al reproducir animaciones.
- **Causa Raíz:** En *Linear Blend Skinning*, forzar rotaciones globales directas (`COPY_ROTATION` en espacio `WORLD`) entre armaduras con diferente roll de reposo ($\Delta \text{Roll} \approx 180^\circ$) induce una torsión longitudinal que colapsa la sección transversal.
- **Solución Comprobada:** Retargeting por matriz de offset relativo:
  $$\mathbf{R}_{\text{offset}} = \mathbf{S}_{\text{rest}}^{-1} \cdot \mathbf{T}_{\text{rest}}$$
  $$\mathbf{T}_{\text{world}}(t) = \mathbf{S}_{\text{world}}(t) \cdot \mathbf{R}_{\text{offset}}$$

---

### [ERR-002] Destello Blanco Fluorescente (Emission Blowout) en Exportación glTF
- **Síntoma:** El modelo se visualiza completamente blanco y reflectante en Godot/visores glTF, ignorando el color de piel.
- **Causa Raíz:** El nodo Principled BSDF de Blender tiene por defecto `Emission Color = (1, 1, 1)`. Si `Emission Strength` no se fija explícitamente en `0.0`, el exportador glTF emite `emissiveFactor: [1, 1, 1]`, quemando el sombreado.
- **Solución:** Forzar explícitamente `Emission Strength = 0.0` y `Emission Color = (0.0, 0.0, 0.0, 1.0)`.

---

### [ERR-003] Desincronización de Ejes FBX por Falta de Aplicación de Transformadas
- **Síntoma:** El esqueleto se visualiza horizontal o rotado $90^\circ$ respecto a la malla.
- **Causa Raíz:** El importador de FBX asigna rotación `(1.57, 0, 0)` a la armadura y `(-1.57, 0, 0)` a la malla para adaptar ejes Y-up a Z-up. Asignar `rotation_euler = (0,0,0)` sin aplicar transformadas genera un desfase permanente.
- **Solución:** Seleccionar simultáneamente malla y esqueleto y ejecutar `bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)`.

---

### [ERR-004] Fatiga de Agente y Fallos por Micro-Llamadas Atómicas en MCPs de 3D/Godot
- **Síntoma:** Los agentes invocan herramientas MCP primitivas (`execute_blender_code`, `node_create`) de forma secuencial interactiva 8 a 10 veces para tareas comunes, provocando agotamiento de contexto y errores 503 por límite de capacidad.
- **Causa Raíz:** Falta de abstracción macro. Los servidores MCP exponen primitivas de motor en vez de pipelines compuestos deterministas.
- **Solución Comprobada:** Invocar los scripts de un solo disparo:
  - [`tools/pipeline_3d_repair_export.py`](file:///c:/Users/cesar/Desktop/skill/tools/pipeline_3d_repair_export.py)
  - [`tools/godot_scene_scaffolder.py`](file:///c:/Users/cesar/Desktop/skill/tools/godot_scene_scaffolder.py)
