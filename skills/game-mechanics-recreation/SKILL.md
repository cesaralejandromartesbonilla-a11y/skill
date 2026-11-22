---
name: game-mechanics-recreation
description: Ingeniería inversa matemática de mecánicas de juego (sin copiar assets) y matriz de fusión (RETAIN, REPLACE, FUSE, DISCARD).
---

# Game Mechanics Recreation & Physical Testing Protocol

Consulta las guías técnicas detalladas en:
- [Docs/game_mechanics/fusion_matrix.md](file:///c:/Users/cesar/Desktop/skill/Docs/game_mechanics/fusion_matrix.md)
- [Docs/architecture/physical_validation_harness.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/physical_validation_harness.md)

## Reglas Obligatorias

1. **Cero Copia de Assets Comerciales:** Extraer únicamente la lógica matemática, diagramas de estado, ecuaciones cinemáticas y algoritmos.
2. **Matriz de Fusión Directa:** Estructurar la discusión directamente mediante los 4 cuadrantes (`RETAIN`, `REPLACE`, `FUSE`, `DISCARD`) sin forzar al usuario a reexplicaciones.
3. **Prototipado Greybox:** Validar primero con primitivas (`CapsuleShape3D`, `BoxShape3D`) antes de integrar cualquier arte visual.
4. **Validación Física Empírica (Cero Validadores Puramente Matemáticos):**
   - Prohibido declarar mecánicas válidas basándose únicamente en fórmulas analíticas estáticas en Python o tests unitarios sin motor físico.
   - El agente DEBE proponer al usuario crear/configurar una **Escena de Test Físico Mínimo** (`res://tests/physical/test_<mecanica>.tscn`) con un sensor **`Area3D`** de meta/checkpoint.
   - Definir condiciones de validez cuantitativas (tiempo límite, rango de velocidad de entrada, límite de vuelco/roll).
   - El sensor `Area3D` debe emitir salidas diagnósticas en texto estructurado explicando **QUÉ PASÓ Y POR QUÉ PASÓ** a nivel de dinámicas de contacto y tracción.
