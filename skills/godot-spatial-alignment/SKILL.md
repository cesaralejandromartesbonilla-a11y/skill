---
name: godot-spatial-alignment
description: >-
  Protocolo de alineación dimensional 3D/2D, eliminación de solapamiento de mallas
  (Z-fighting e interpenetración), normalización de pivotes en Blender y Godot 4,
  y mapeo correcto de texturas PBR (canales ORM, Normal Map DirectX/OpenGL y filtrado Pixel Art).
---

# Godot Spatial Alignment & Visual Integrity Protocol

Este skill define los estándares y herramientas para resolver los dos problemas visuales y dimensionales más recurrentes en Godot 4:
1. **Solapamiento de Mallas e Interpenetración (Z-fighting y Desalineación de Pivotes)**: Superficies coplanares parpadeantes, cajas de colisión desfasadas respecto a la malla y modelos que se hunden en el suelo o flotan.
2. **Desajuste de Texturas y Materiales PBR**: Inversión del canal verde en Normal Maps, empaquetado incorrecto de texturas ORM (Occlusion/Roughness/Metallic) y texturas pixel art borrosas por filtrado bilineal.

---

## 1. Reglas Contra el Solapamiento de Mallas y Z-Fighting

El Z-fighting ocurre cuando dos triángulos comparten coordenadas casi idénticas en el búfer de profundidad (depth buffer).

### Regla 1: Desfase Mínimo Controlado (Epsilon Offset)
Para calcomanías, marcas de pisadas, agujeros de bala o paneles superpuestos:
- **Distancia mínima**: Aplicar un offset de $0.001\text{m}$ a $0.003\text{m}$ ($1$ a $3\text{mm}$) en el eje normal a la superficie.
- En código GDScript:
  ```gdscript
  decal_instance.global_position = hit_point + (hit_normal * 0.002)
  ```

### Regla 2: Depth Bias en Shaders / Materiales
Si dos mallas deben coexistir en la misma superficie sin poder alterar su posición:
- En `StandardMaterial3D`: Ajustar `distance_fade_mode` o usar calcomanías nativas (`Decal` node en Godot 4), que proyectan texturas sin geometría adicional.
- En `ShaderMaterial`: Añadir offset en el vértice:
  ```glsl
  void vertex() {
      VERTEX += NORMAL * 0.001;
  }
  ```

### Regla 3: Snapping Modular y Geometría sin Caras Ocultas
- Todas las piezas de construcción modulares (paredes, suelos, vigas) deben dimensionarse en múltiplos de la cuadrícula (ej. $1.0\text{m}$, $2.0\text{m}$, $0.2\text{m}$).
- Nunca solapar dos cubos para crear una pared en "L"; las caras internas en contacto deben ser eliminadas o encajadas mediante vértices compartidos para ahorrar draw calls y evitar parpadeo.

---

## 2. Normalización de Pivotes y Orígenes (Blender -> Godot 4)

El fallo más común en el ensamblado 3D es tener el pivote de Blender en el centro de masa $(0, 0, 0)$, mientras que Godot espera que la base del objeto esté en $Y = 0$.

### Protocolo en Blender (Headless o Interactivo)
Antes de exportar cualquier archivo `.glb`:

1. **Aplicar todas las transformaciones (Freeze Transforms)**:
   ```python
   import bpy
   bpy.ops.object.select_all(action='SELECT')
   bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
   ```
2. **Posicionar el Pivote en la Base Inferior (Ground Plane)**:
   - Para piezas de entorno, enemigos o props: El origen DEBE estar en el centro inferior de la caja de límites ($Z = \min(Z)$ en Blender, que corresponde a $Y = 0$ en Godot).
   ```python
   # Script Blender para fijar origen en el piso del modelo
   import bpy
   from mathutils import Vector

   for obj in bpy.context.selected_objects:
       if obj.type == 'MESH':
           bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
           min_z = min(v.z for v in bbox)
           center_x = sum(v.x for v in bbox) / 8.0
           center_y = sum(v.y for v in bbox) / 8.0
           
           # Mover cursor al centro inferior
           bpy.context.scene.cursor.location = Vector((center_x, center_y, min_z))
           bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
   ```

### Manejo en Godot cuando la Malla no puede ser Editada
Si la malla externa tiene el pivote desfasado, crear una jerarquía de compensación:
```
Node3D (Pivote Real / Colisionador) -> global_position en (X, Y, Z)
  └── MeshInstance3D -> position = Vector3(0, -mesh_height / 2.0, 0)
  └── CollisionShape3D -> position = Vector3(0, collision_height / 2.0, 0)
```

---

## 3. Mapeo Correcto de Texturas PBR en Godot 4

Godot 4 utiliza el modelo PBR estándar metálico/rugosidad. Los fallos visuales de "material quemado", "brillo plástico descontrolado" o "luz invertida" provienen de una configuración errónea de canales:

### A. Desempaquetado de Texturas ORM
Muchos motores y bibliotecas de assets exportan una textura única "ORM" para optimizar memoria:
- **Canal Rojo (R)**: Occlusión Ambiental (AO).
- **Canal Verde (G)**: Rugosidad (Roughness).
- **Canal Azul (B)**: Metálico (Metallic).

**Configuración en `StandardMaterial3D` en Godot 4**:
1. Asignar la misma textura ORM a los 3 slots:
   - `ao_texture`: textura ORM, `ao_texture_channel = 0` (Red).
   - `roughness_texture`: textura ORM, `roughness_texture_channel = 1` (Green).
   - `metallic_texture`: textura ORM, `metallic_texture_channel = 2` (Blue).
2. Asegurarse de que `metallic = 1.0` y `roughness = 1.0` en el material base para que el mapa module el valor completo.

### B. Normal Maps: DirectX vs OpenGL ($Y-$ vs $Y+$)
- **DirectX (Unreal Engine, 3ds Max)**: Canal Verde apunta hacia abajo ($Y-$).
- **OpenGL / Vulkan (Godot 4, Blender)**: Canal Verde apunta hacia arriba ($Y+$).
- **Diagnóstico**: Si la luz en Godot viene desde arriba pero las ranuras o hendiduras parecen iluminadas por abajo, el canal verde está invertido.
- **Solución en Godot**:
  - En la pestaña **Import** de la textura de normales: Marcar `Normal Map -> Invert Y` y pulsar `Reimport`.
  - O en el material: Marcar `normal_scale = Vector3(1, -1, 1)`.

### C. Arte 2D y 3D Pixel Art: Filtrado de Texturas
- Por defecto, Godot 4 aplica filtrado bilineal con mipmaps (`TEXTURE_FILTER_LINEAR_WITH_MIPMAPS`). Esto produce bordes borrosos, pérdida de nitidez y sangrado de color en tiles.
- **Configuración Global para Proyectos Pixel Art**:
  `Project Settings -> Rendering -> Textures -> Canvas Textures -> Default Texture Filter` = `Nearest` (0).
- **Configuración por Material 3D**:
  En `StandardMaterial3D -> Flags`: Activar `texture_filter = TEXTURE_FILTER_NEAREST`.

---

## 4. Script de Auditoría de Alineación Espacial

Guarda este script como herramienta de editor en `res://addons/spatial_auditor/spatial_auditor.gd`:

```gdscript
@tool
extends EditorScript

func _run() -> void:
    print("--- INICIANDO AUDITORÍA ESPACIAL EN ESCENA ACTIVA ---")
    var root := get_scene()
    if not root:
        push_error("No hay escena abierta en el editor.")
        return
    
    var meshes: Array[MeshInstance3D] = []
    _collect_meshes(root, meshes)
    
    # 1. Verificar escalas no normalizadas
    for mesh_node in meshes:
        var s := mesh_node.scale
        if not is_equal_approx(s.x, 1.0) or not is_equal_approx(s.y, 1.0) or not is_equal_approx(s.z, 1.0):
            print_rich("[color=yellow]Aviso: %s tiene escala no unitaria %s. Aplica escala en Blender o normaliza.[/color]" % [mesh_node.name, str(s)])
        
        # 2. Verificar materiales con ORM
        var mat := mesh_node.get_active_material(0) as StandardMaterial3D
        if mat and mat.roughness_texture and not mat.ao_texture:
            print_rich("[color=cyan]Info: %s tiene roughness_texture pero no AO. Verifica si es textura ORM.[/color]" % mesh_node.name)

    print("--- AUDITORÍA ESPACIAL COMPLETADA ---")

func _collect_meshes(node: Node, list: Array[MeshInstance3D]) -> void:
    if node is MeshInstance3D:
        list.append(node)
    for child in node.get_children():
        _collect_meshes(child, list)
```
