# Manual de Uso: Pipeline 3D Auto-Repair & Godot Ingest

**Script:** [`tools/pipeline_3d_repair_export.py`](file:///c:/Users/cesar/Desktop/skill/tools/pipeline_3d_repair_export.py)  
**Motor Intermediario:** Blender 5.0 Headless

---

## Propósito
Sustituye 8 a 10 llamadas atómicas interactivas a `blender-mcp` (`execute_blender_code`) por **un solo comando determinista**.

---

## Sintaxis de Invocación por Agentes

```bash
python tools/pipeline_3d_repair_export.py \
       --input "ruta/modelo.fbx" \
       --project "C:/ruta/ProyectoGodot" \
       --category "props" \
       --albedo "ruta/textura_diffuse.png" \
       --normal "ruta/textura_normal.png" --invert-normal-y \
       --trigger-import
```

### Argumentos Principales
- `--input <path>`: Archivo de entrada (.fbx, .obj, .gltf, .glb, .psk, .blend).
- `--project <path>`: Ruta raíz del proyecto Godot (`res://`).
- `--category <folder>`: Subdirectorio destino dentro de `res://assets/<categoría>/` (ej. `props`, `characters`).
- `--no-normalize-pivot`: Desactiva la alineación del pivote a la base $Y=0$.
- `--orm <path>`: Textura ORM empaquetada (R=AO, G=Roughness, B=Metallic).
- `--invert-normal-y`: Inversión de canal verde para mapas DirectX.
- `--trigger-import`: Ejecuta Godot headless tras mover el GLB para forzar escaneo y UID.
