# Protocolo Global de Operación de Agentes Antigravity

Este archivo de reglas globales aplica a **todas las sesiones, agentes y espacios de trabajo** en este entorno. Establece los estándares arquitectónicos, metodológicos y de memoria persistente para el desarrollo de proyectos y recreación de videojuegos.

---

## 1. Reglas de Inicio y Memoria Persistente (RAG + MCP)
1. **Consulta de Memoria Cruzada (`claude-mem`)**:
   - Antes de formular preguntas al usuario sobre mecánicas previas, configuraciones de proyectos ya trabajados o soluciones a errores conocidos, el agente DEBE ejecutar una búsqueda semántica usando las herramientas MCP de `claude-mem` (`smart_search` o `query_corpus`).
   - Si una tarea implica un patrón ya resuelto (ej. curvas de fricción estilo Source, chunks de vóxeles estilo Vholumen, configuración de exportación en Blender), recupera la solución probada sin forzar al usuario a reexplicarla.
2. **Registro de Nuevos Aprendizajes**:
   - Cada solución a un bug complejo o decisión arquitectónica relevante debe persistirse en el Error Ledger y registrarse en memoria (`save_memory`).

---

## 2. Recreación de Videojuegos y Fusión de Mecánicas (`game-mechanics-recreation`)
1. **Cero Copia de Assets Comerciales**:
   - Prohibido copiar mallas 3D, texturas, audios o mapas de juegos comerciales para evitar problemas de copyright.
   - Extraer **únicamente la lógica matemática, diagramas de estado, ecuaciones de movimiento y algoritmos**.
2. **Matriz de Fusión de Mecánicas**:
   - Cuando el usuario solicite fusionar o recrear mecánicas entre juegos (ej. Counter-Strike + Vholumen), el agente NO pedirá explicaciones extensas y repetitivas.
   - El agente estructurará la discusión directamente mediante la **Matriz de Fusión**:
     - `RETAIN`: Mecánicas mantenidas de la Fuente A.
     - `REPLACE`: Mecánicas reemplazadas por la Fuente B.
     - `FUSE`: Mecánicas híbridas (ej. balística de A interactuando con terreno deformable de B).
     - `DISCARD`: Elementos descartados.
3. **Prototipado Greybox**:
   - Todo controlador de juego nuevo debe verificarse primero con geometría primitiva (`CapsuleShape3D`, `BoxShape3D`) y gráficos de velocidad en tiempo real antes de aplicar cualquier arte visual.
4. **Validación Física Empírica (Cero Validadores Puramente Matemáticos)**:
   - Queda terminantemente PROHIBIDO declarar válida una mecánica física mediante cálculos matemáticos estáticos o fórmulas abstractas que ignoran fricción, masa y colisiones reales en el motor.
   - El agente DEBE proponer activamente al usuario crear/configurar una Escena de Test Físico Mínimo (`res://tests/physical/test_<mecanica>.tscn`) con un sensor `Area3D` objetivo.
   - Dicha escena debe registrar en consola salidas de texto estructuradas que expliquen de forma inequívoca **QUÉ PASÓ Y POR QUÉ PASÓ** (evento, telemetría y causa física). Ver [Docs/architecture/physical_validation_harness.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/physical_validation_harness.md).

---

## 3. Integridad Espacial 3D/2D en Godot (`godot-spatial-alignment`)
1. **Cero Z-Fighting / Solapamiento**:
   - No colocar caras coplanares en las mismas coordenadas. Aplicar desfase mínimo de seguridad ($0.001\text{m}$ a $0.003\text{m}$) o nodos `Decal`.
2. **Normalización de Pivotes en Blender**:
   - Todo modelo exportado a Godot 4 debe tener transformaciones aplicadas (`Ctrl+A -> Rotation & Scale`).
   - El pivote debe situarse en la base inferior del objeto ($Z = \min(Z)$ en Blender, $Y = 0$ en Godot) para piezas de escenario, props y personajes.
3. **Mapeo de Canales PBR**:
   - Para mapas ORM: Rojo = AO (`ao_texture_channel = 0`), Verde = Roughness (`roughness_texture_channel = 1`), Azul = Metallic (`metallic_texture_channel = 2`).
   - Normal Maps con formato DirectX: Activar `Invert Y` en el import dock de Godot 4 para coincidir con la convención OpenGL/Vulkan.
   - Proyectos Pixel Art (2D o 3D): Fijar `Default Texture Filter` en `Nearest` para evitar desenfoque bilineal.

---

## 4. Arquitectura Modular y Control de Errores (`error-ledger-and-modular-architecture`)
1. **Desacoplamiento Estricto**:
   - Ningún script debe exceder 300 líneas si mezcla responsabilidades.
   - Separar Entrada de Usuario (Input), Lógica de Estado (State Machine), Fórmulas Físicas (Kinematics) y Representación Visual (Rendering).
2. **Comunicación por Señales**:
   - Comunicación de abajo hacia arriba mediante `signal`; llamadas directas únicamente de arriba hacia abajo (`call`).

---

## 5. Control y Depuración del Editor Godot (`godot-ai` + `GodotPrompter`)
1. **Conexión en Vivo y Verificación**:
   - Para probar proyectos, verificar errores de consola en caliente o capturar vista del viewport, usa el servidor MCP `godot-ai` (`editor_state`, `project_run`, `logs_read`, `editor_screenshot`).
2. **Inspección y Parcheo Quirúrgico**:
   - Usar `scene_get_hierarchy` para inspeccionar la escena activa y `script_patch` para aplicar cambios en caliente sin romper el estado del editor.
3. **Sinergia con GodotPrompter**:
   - GodotPrompter rige la arquitectura, el tipado estricto y los patrones (FSM, señales, recursos). `godot-ai` ejecuta y valida las mutaciones en el editor en vivo.
4. **Aprovisionamiento Obligatorio del Addon (Anti-Evasión)**:
   - Antes de realizar cualquier tarea en un proyecto de Godot, el agente DEBE verificar si `addons/godot_ai` está instalado y registrado en `project.godot` (`setup-godot-ai --project <dir> --check` o `python c:/Users/cesar/Desktop/skill/tools/setup_godot_ai_addon.py --project <dir> --check`).
   - Si no está configurado, el agente DEBE ejecutar de inmediato:
     `setup-godot-ai --project <dir_godot>`
   - Queda terminantemente PROHIBIDO evadir el uso de las herramientas MCP de `godot-ai` por omitir la instalación previa del addon. Ver [Docs/pipelines/godot_ai_setup.md](file:///c:/Users/cesar/Desktop/skill/Docs/pipelines/godot_ai_setup.md).

---

## 6. Prohibición de Micro-Llamadas Atómicas y Pipelines de Un Solo Disparo
1. **Erradicación del Trabajo Manual "Paso a Paso"**:
   - Queda terminantemente PROHIBIDO encadenar múltiples llamadas MCP atómicas (`execute_blender_code`, `node_create` x10) para tareas estándar de preparación de assets o andamiaje de escenas.
2. **Pipeline Macro 3D a Godot (`tools/pipeline_3d_repair_export.py`)**:
   - Para cualquier modelo 3D (.fbx, .obj, .gltf, .psk, .blend), el agente DEBE invocar el script unificado:
     `python tools/pipeline_3d_repair_export.py --input <malla> --project <dir_godot> --category <props|characters> --trigger-import`
   - Aplica automáticamente rotación y escala (`Ctrl+A`), normaliza el pivote a la base inferior ($Z = \min(Z)$ en Blender, $Y = 0$ en Godot), desinfecta mallas (merge doubles a 0.1mm), recalcula normales hacia el exterior, configura materiales PBR/ORM y traslada el activo a Godot registrando su UID en una sola operación.
3. **Andamiaje de Escenas en Un Disparo (`tools/godot_scene_scaffolder.py` / `batch_execute`)**:
   - Para crear jerarquías estándar de escenas (Props con colisión, CharacterBody3D con cámara o UI CanvasLayer), el agente debe ejecutar `tools/godot_scene_scaffolder.py` o emitir un único payload atómico mediante `batch_execute` de `godot-ai`.

---

## 7. Protocolo de Hojas de Ruta Jerárquicas (Etapa $\to$ Fase $\to$ Paso - Cero Prisa)
1. **El Paradigma de la Torre Eiffel**:
   - Todo proyecto o desarrollo debe estructurarse obligatoriamente en tres niveles: `Etapas` (macro-hitos estratégicos) $\to$ `Fases` (bloques modulares secuenciales con puertas de calidad / DoD) $\to$ `Pasos` (acciones atómicas `[EX-FY-PZZ]`).
   - Cero prisa: Queda terminantemente PROHIBIDO "abarcar todo de golpe" o implementar código/assets de fases superiores sin haber cerrado y validado empíricamente los prerrequisitos y cimientos de las fases previas (como construir las 4 patas independientes y cimentarlas antes de montar el tramo de unión o la antena).
2. **Dual-Track Roadmap**:
   - Mantener sincronizados siempre `ROADMAP_DETAILED.md` (exhaustivo y vivo con Gates de Fase) y `ROADMAP_EXECUTIVE.md` (resumen ejecutivo visual de alto nivel con semáforo y barras de progreso por Etapa/Fase).
   - Referencia técnica completa: [Docs/architecture/hierarchical_roadmap_standard.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/hierarchical_roadmap_standard.md).

---

## 8. Fidelidad Morfológica y Anatómica 3D (Prohibición de Primitivas Absurdas)
1. **Cero Primitivas Sustitutas**:
   - Queda terminantemente PROHIBIDO utilizar cilindros, cajas planas o primitivas geométricas no funcionales como placeholders de herramientas o componentes mecánicos complejos (ej. sustituir una vertedera de arado para campos duros por un cilindro).
2. **Protocolo de 4 Puertas Anatómicas Obligatorio**:
   - Todo modelo 3D mecánico o prop funcional debe pasar por:
     1. *Descomposición Anatómica:* Identificar cada sub-pieza funcional (reja en cuña cortante, vertedera alabeada de volteo, costanera/dental plano guía, cama forjada, timón).
     2. *Perfiles Paramétricos Específicos:* Superficies alabeadas, arcos helicoidales, biseles afilados y espesores reales de chapa.
     3. *Ensamblaje Mecánico:* Uniones con pernos de seguridad antirocas, bridas y enganche tripuntal normalizado ISO 730 Cat II/III.
     4. *Verificación Dimensional y Pivote:* Escala métrica realista y normalización del pivote en base $Y=0$.
   - Referencia técnica completa: [Docs/architecture/functional_3d_anatomy_guide.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/functional_3d_anatomy_guide.md).



