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
| **[ERR-005]** | Apresuramiento en Hojas de Ruta ("Abarcar Todo") | Planificación / Roadmap | Falta de jerarquía en 3 niveles y gates intermedios | [Detalles](#err-005) |
| **[ERR-006]** | Sustitución Morfológica Absurda (Cilindro por Vertedera) | Blender / Generación 3D | Omisión de descomposición anatómica funcional | [Detalles](#err-006) |
| **[ERR-007]** | Omisión del Addon godot_ai y Desconexión MCP | Godot / MCP godot-ai | Proyecto Godot sin plugin ni configuración en project.godot | [Detalles](#err-007) |
| **[ERR-008]** | Falso Positivo por Validador Puramente Matemático | Godot / Físicas y Mecánicas | Fórmulas abstractas que ignoran fricción, masa y colisiones | [Detalles](#err-008) |

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

---

### [ERR-005] Apresuramiento en Hojas de Ruta y Falta de Jerarquía ("Abarcar Todo de Golpe")
- **Síntoma:** Los agentes generan listas planas de tareas y se apresuran a implementar interfaces o features de alto nivel antes de asentar los cimientos arquitectónicos o pruebas base.
- **Causa Raíz:** Ausencia de una jerarquía estricta y de criterios de aceptación (*Definition of Done*) por bloques interdependientes.
- **Solución Comprobada:** Aplicar la jerarquía de 3 niveles (`Etapa` $\to$ `Fase` $\to$ `Paso`) y el **Paradigma de la Torre Eiffel** (nadie construye la antena antes de cimentar y erigir minuciosamente las 4 patas independientes). Ver [Docs/architecture/hierarchical_roadmap_standard.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/hierarchical_roadmap_standard.md).

---

### [ERR-006] Sustitución Morfológica Absurda (La Herejía del Cilindro en Modelado 3D)
- **Síntoma:** Cuando se solicita modelar un componente o herramienta compleja (ejemplo: *"vertedera para campos duros"*), el agente genera un cilindro o cubo primitivo trivial sin funcionalidad física ni filo.
- **Causa Raíz:** Intentar generar geometría sin realizar primero una descomposición anatómica funcional de cada sub-pieza de ingeniería.
- **Solución Comprobada:** Aplicar el **Protocolo de 4 Puertas Anatómicas**:
  1. *Descomposición Anatómica Funcional:* Reja en cuña, vertedera alabeada de volteo, costanera/dental plano guía, cama forjada, timón y enganche tripuntal.
  2. *Perfiles Paramétricos Específicos:* Superficies alabeadas/curvadas con espesores reales de chapa.
  3. *Ensamblaje Mecánico:* Pernos de seguridad y bulones normalizados.
  4. *Verificación Dimensional y Pivote en Base $Y=0$.* Ver [Docs/architecture/functional_3d_anatomy_guide.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/functional_3d_anatomy_guide.md).

---

### [ERR-007] Omisión del Addon godot_ai y Desconexión / Evasión del Servidor MCP
- **Síntoma:** El agente evita utilizar las herramientas MCP de `godot-ai` (`editor_state`, `scene_get_hierarchy`, `node_create`, `project_run`), reporta fallos de conexión por socket o vuelve a la edición manual descontextualizada.
- **Causa Raíz:** El proyecto de Godot objetivo carece de la carpeta `addons/godot_ai` o no tiene registrados el plugin en `[editor_plugins]` y el autoload `_mcp_game_helper` en `project.godot`.
- **Solución Comprobada:** Ejecutar el aprovisionador en un solo disparo:
  `python tools/setup_godot_ai_addon.py --project <ruta_al_proyecto>`
  Ver [Docs/pipelines/godot_ai_setup.md](file:///c:/Users/cesar/Desktop/skill/Docs/pipelines/godot_ai_setup.md).

---

### [ERR-008] Falso Positivo por Validadores Puramente Matemáticos en Mecánicas Físicas
- **Síntoma:** Un script de verificación matemática en Python declara "aprobada" una mecánica (ej. aceleración o frenado de un vehículo), pero al jugar en Godot el vehículo patina, no sube rampas, vuelca en curvas o atraviesa el suelo.
- **Causa Raíz:** Las fórmulas analíticas abstractas ignoran el integrador de físicas a 60 Hz, las normales de colisión, el agarre de neumáticos, la fricción de materiales y la suspensión real.
- **Solución Comprobada:** Proponer y ejecutar una Escena de Test Físico Mínimo con sensor `Area3D` (`physical_test_area.gd`) que imprima diagnósticos descriptivos ("QUÉ PASÓ Y POR QUÉ PASÓ"). Ver [Docs/architecture/physical_validation_harness.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/physical_validation_harness.md).



