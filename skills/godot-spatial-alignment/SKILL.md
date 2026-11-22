---
name: godot-spatial-alignment
description: Alineación dimensional 3D/2D, eliminación de Z-fighting, normalización de pivotes en base Y=0 y mapeo de texturas PBR/ORM.
---

# Godot Spatial Alignment & 3D Fidelity Protocol

Consulta las guías técnicas detalladas en:
- [Docs/architecture/spatial_alignment.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/spatial_alignment.md)
- [Docs/architecture/functional_3d_anatomy_guide.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/functional_3d_anatomy_guide.md)

## Principios Inmediatos

1. **Pivote en Base Inferior:** $Z = \min(Z)$ en Blender $\to Y = 0$ en Godot (`Ctrl+A -> Rotation & Scale`).
2. **Cero Z-Fighting:** Desfase mínimo de seguridad $0.001\text{m}$ a $0.003\text{m}$ o nodos `Decal`.
3. **Mapas ORM:** Rojo = AO (0), Verde = Roughness (1), Azul = Metallic (2).
4. **Fidelidad Morfológica y Anatómica:** Prohibido usar primitivas absurdas como sustitutos (ej. cilindros por vertederas agrícolas). Obligatorio aplicar el **Protocolo de 4 Puertas Anatómicas** (Despiece funcional $\to$ Perfiles alabeadas/cuñas $\to$ Ensamblaje mecánico $\to$ Métricas reales).
5. **Pipeline Automatizado:** Usa `python tools/pipeline_3d_repair_export.py` para aplicar reparación, pivote, normales y PBR en 1 solo comando.
