---
name: godot-spatial-alignment
description: Alineación dimensional 3D/2D, eliminación de Z-fighting, normalización de pivotes en base Y=0 y mapeo de texturas PBR/ORM.
---

# Godot Spatial Alignment & PBR Protocol

Consulta la guía técnica detallada en:
- [Docs/architecture/spatial_alignment.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/spatial_alignment.md)

## Principios Inmediatos
1. **Pivote en Base Inferior:** $Z = \min(Z)$ en Blender $\to Y = 0$ en Godot (`Ctrl+A -> Rotation & Scale`).
2. **Cero Z-Fighting:** Desfase mínimo de seguridad $0.001\text{m}$ a $0.003\text{m}$.
3. **Mapas ORM:** Rojo = AO (0), Verde = Roughness (1), Azul = Metallic (2).
4. **Pipeline Automatizado:** Usa `python tools/pipeline_3d_repair_export.py` para aplicar estas reglas en 1 solo comando.
