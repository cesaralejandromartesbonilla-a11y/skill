# Directorio de Exportación 3D (Godot / glTF / GLB)

Este directorio almacena los activos 3D convertidos y optimizados listos para su uso en Godot 4.6 u otros motores modernos.

## Activos Generados:
- **`kobold_godot_ready.glb`:** Modelo de personaje Kobold (KoboldKare) de 30.43 MB con:
  - Armadura esquelética de 70 huesos (`Kobold_Rig`).
  - Malla poligonal de alta resolución y LOD1.
  - Materiales PBR Principled BSDF configurados (`KoboldBody`, `KoboldEyes`) con texturas embebidas.
  - 7 pistas de animación esquelética horneadas (`Kobold_Idle`, `Kobold_Idle_B`, `Kobold_Walk`, `Kobold_Run`, `Kobold_Strafe_L`, `Kobold_Strafe_R`, `Kobold_Thrust`).
  - Validación estructural verificada mediante `tools/verify_glb.py`.

## Regenerar activo:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b -P tools\kobold_pipeline_builder.py
```
