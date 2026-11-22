# Protocolo de Integridad Espacial y Mapeo PBR en Godot

> **Norma de Referencia:** Cero Z-Fighting, Normalización de Pivotes en Blender y Mapeo PBR.

---

## 1. Cero Z-Fighting / Solapamiento Coplanar
- Prohibido situar caras coplanares en idénticas coordenadas.
- Desfase mínimo de seguridad: **0.001 m a 0.003 m** o uso de nodos `Decal`.

---

## 2. Normalización de Pivotes en Blender y Godot
- Toda malla exportada debe tener transformaciones aplicadas: `Ctrl+A -> Rotation & Scale`.
- El pivote debe situarse en la base inferior del objeto ($Z = \min(Z)$ en Blender, coincidiendo con $Y = 0$ en Godot) para props, personajes y piezas modulares.
- Esto garantiza que al instanciar un prop o personaje en coordenadas $(X, 0, Z)$, apoye exactamente en el suelo sin penetrar la geometría ni flotar.

---

## 3. Mapeo de Texturas PBR y Convenciones
- **Mapas ORM Empaquetados:**
  - Canal Rojo = Ambient Occlusion (AO, `ao_texture_channel = 0`)
  - Canal Verde = Roughness (`roughness_texture_channel = 1`)
  - Canal Azul = Metallic (`metallic_texture_channel = 2`)
- **Normal Maps DirectX:**
  - Si el normal map proviene de Unreal/DirectX (eje Y invertido), activar `Invert Y` en el import dock de Godot 4 o usar la bandera `--invert-normal-y` en `pipeline_3d_repair_export.py`.
- **Pixel Art:**
  - Fijar `Default Texture Filter` en `Nearest` para evitar desenfoque bilineal.
