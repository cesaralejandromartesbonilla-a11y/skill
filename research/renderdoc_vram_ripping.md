# Guía y Workflow Operativo: Captura Directa de VRAM con RenderDoc

> **Propósito:** Procedimiento técnico definitivo para extraer modelos 3D, mapas de normales, texturas PBR y llamadas de dibujado (*draw-calls*) directamente desde la memoria de video de la GPU (VRAM) cuando los archivos del juego están cifrados, protegidos por DRM o empaquetados en formatos propietarios no soportados por descompiladores offline.
> **Fase del Proyecto:** Fase 2 (`[F2-T08]`).

---

## 1. Principio Fundamental del Ripping de VRAM

A diferencia de los extractores de archivos en disco (UModel, UnityPy, AssetRipper) que dependen de conocer la estructura binaria del contenedor (`.pak`, `.assets`, `.vpk`), **la GPU no puede renderizar datos cifrados ni comprimidos con algoritmos propietarios**.

Para dibujar un fotograma en pantalla bajo APIs gráficas modernas (DirectX 11, DirectX 12, Vulkan, OpenGL):
1. La CPU debe descomprimir la geometría en el *Input Assembler* (IA) como buffers continuos de vértices (posiciones XYZ, normales, tangentes, coordenadas UV).
2. El *Vertex Shader* (VS) procesa las transformaciones y el pesaje esquelético.
3. El *Pixel/Fragment Shader* (PS) enlaza las texturas descomprimidas en VRAM (registros `t0`, `t1`, `t2` en formato RGBA8, BC1-BC7, o ASTC) para colorear la superficie.

**RenderDoc** intercepta la capa de la API gráfica y congela el fotograma completo, permitiendo volcar la geometría exacta y sus texturas asociadas bit a bit.

```
       +-------------------------------------------------------------+
       |                     MOTOR DEL JUEGO                         |
       |     (Archivos Cifrados, Motores Propietarios, Sin SDK)      |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             RENDERDOC (Intercepción de API Gráfica)         |
       |           DirectX 11 / DirectX 12 / Vulkan / OpenGL         |
       +-------------------------------------------------------------+
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
       +-------------------+                     +-------------------+
       |   Mesh Viewer     |                     |  Texture Viewer   |
       |  Buffers VS In/Out|                     | Registros t0..t15 |
       +-------------------+                     +-------------------+
                 |                                         |
                 +--------------------+--------------------+
                                      |  (.rdc Capture File)
                                      v
       +-------------------------------------------------------------+
       |                  BLENDER 5.0 (Intermediario)                |
       |     MapsModelsImporter + blender_universal_bridge.py        |
       |     - Limpieza de Quads, Remove Doubles, Re-Normalización   |
       |     - Enlace de Material PBR                                |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                    GODOT 4.6 (Destino Final)                |
       |                   Modelo Limpio en .glb                     |
       +-------------------------------------------------------------+
```

---

## 2. Requisitos y Herramientas Necesarias

| Herramienta | Versión Recomendada | Propósito |
| :--- | :--- | :--- |
| **RenderDoc** | v1.30 a v1.34 (64-bit) | Intercepción de llamadas a la API gráfica y volcado a `.rdc`. |
| **Blender 5.0** | `"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"` | Importación, re-alineación, eliminación de duplicados y exportación. |
| **MapsModelsImporter** | Addon para Blender | Permite importar archivos `.rdc` directamente como mallas con UVs y texturas asignadas. |
| **Puente Universal** | `tools/blender_universal_bridge.py` | Normalización final de ejes, corrección de normales y exportación a GLB. |

---

## 3. Protocolo de Inyección y Captura Paso a Paso

### Paso 1: Configurar la Inyección en RenderDoc
1. Abrir **RenderDoc**.
2. Ir a la pestaña **Launch Application**:
   - **Executable Path:** Seleccionar el binario del juego (ej. `C:\Juego\Game.exe`).
   - **Working Directory:** Directorio raíz del juego.
   - **Environment Variables:** Si el juego requiere argumentos especiales (ej. forzar DirectX 11 con `-dx11` o `-force-d3d11` para mayor estabilidad en la intercepción).
3. En **Capture Options**:
   - Marcar: `Capture Child Processes` (crucial para lanzadores o ejecutables secundarios).
   - Marcar: `Save All Init Resources`.
   - Marcar: `Capture All Callstacks`.
4. Pulsar **Launch**.

### Paso 2: Congelar y Capturar el Fotograma
1. En el juego, colocar al personaje, vehículo u objeto objetivo en una zona con buena visibilidad o en el menú de inspección / modo foto (para evitar exceso de geometría de fondo).
2. Presionar la tecla de captura de RenderDoc (**`F12`** o **`PrintScreen`** por defecto).
3. La interfaz de RenderDoc confirmará la captura (`Capture #1 saved`).
4. Cerrar el juego y guardar el archivo de captura con extensión `.rdc` (ej. `captura_modelo.rdc`).

### Paso 3: Inspección en RenderDoc (Aislamiento de la Malla)
1. Abrir `captura_modelo.rdc` en RenderDoc.
2. Abrir la ventana **Event Browser**:
   - Desplegar las pasadas de renderizado (*Render Passes* / `G-Buffer`).
   - Filtrar o buscar llamadas `DrawIndexed()` o `Draw()`.
3. Al hacer click en un Draw Call, abrir la pestaña **Mesh Viewer**:
   - **VS Input:** Muestra el modelo antes de deformaciones esqueléticas (ideal para recuperar la pose de descanso o geometría pura).
   - **VS Output:** Muestra el modelo posado en el mundo 3D.
4. En **Pipeline State** $\to$ **Pixel Shader (PS)**:
   - Revisar los recursos de texturas enlazados (`Shader Resource Views`).
   - Localizar los slots de:
     - Albedo / Diffuse (slot `t0` habitualmente).
     - Normal Map (slot `t1` o `t2`).
     - Metallic / Roughness / Mask (slot `t3`).
   - Hacer click derecho en cada textura $\to$ `Save` como `.png` a disco.

---

## 4. Importación y Reconstrucción en Blender 5.0

### Paso 1: Carga del Archivo `.rdc`
Con el addon `MapsModelsImporter` habilitado en Blender:
1. `File` $\to$ `Import` $\to$ `Google Maps / RenderDoc (.rdc)`.
2. Seleccionar `captura_modelo.rdc`.
3. El importador reconstruirá automáticamente los polígonos de cada draw call junto con sus coordenadas UV y texturas embebidas.

### Paso 2: Limpieza Automatizada de Artefactos de VRAM
Los volcados directos de VRAM contienen elementos auxiliares (pantallas completas, cámaras, sombras, skybox). Se debe aplicar el siguiente script de limpieza:

```python
import bpy

# 1. Unir todas las piezas del personaje en un solo objeto
selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
if len(selected_meshes) > 1:
    bpy.context.view_layer.objects.active = selected_meshes[0]
    bpy.ops.object.join()

char_obj = bpy.context.active_object

# 2. Eliminar vértices duplicados introducidos por draw calls fragmentadas
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)

# 3. Recalcular normales hacia el exterior
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

print(f"[✓] Malla limpia: {len(char_obj.data.vertices)} vértices únicos.")
```

### Paso 3: Conversión Final a Godot 4.6 con el Orquestador
Una vez limpiada la geometría en Blender, se exporta directamente a Godot mediante nuestro orquestador:

```powershell
python tools/asset_converter.py port `
    --mesh "export/modelo_limpio.obj" `
    --albedo "export/textures/albedo.png" `
    --normal "export/textures/normal.png" `
    --invert-normal-y `
    --clean-vertex-colors `
    --output "export/modelo_vram_godot.glb"
```

---

## 5. Matriz de Ventajas y Limitaciones

| Aspecto | Ripping por VRAM (RenderDoc) | Extracción por Disco (UnityPy / UModel) |
| :--- | :--- | :--- |
| **Compatibilidad** | Universal (cualquier motor DirectX 11/12, Vulkan, OpenGL). | Específico para cada versión de motor. |
| **Resistencia a DRM** | Totalmente inmune a cifrados o empaquetados desconocidos. | Bloqueado si el archivo `.pak` o `.assets` está encriptado. |
| **Jerarquía Esquelética** | Requiere recrear o transferir el rig (los huesos se hornean en el VS). | Conserva armaduras y nombres de huesos originales. |
| **Texturas** | Idénticas a las cargadas en memoria por el juego. | Acceso a las texturas originales en disco sin mipmaps degradados. |
| **Caso de Uso Óptimo** | **Último recurso infalible** cuando fallan todos los descompiladores. | **Primera opción preferida** por retener pesos y rigs intactos. |
