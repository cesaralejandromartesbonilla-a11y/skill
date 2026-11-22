# Matriz de Fusión de Mecánicas y Recreación Matemática

> **Protocolo:** Recreación de mecánicas sin copiar activos comerciales (cero copyright issue).

---

## Estructura de la Matriz de Fusión

Cuando el usuario solicita fusionar o recrear mecánicas entre juegos (ej. Counter-Strike + Vholumen), estructurar el diseño directamente mediante los 4 cuadrantes:

1. **RETAIN:** Mecánicas que se conservan íntegras de la Fuente A (ej. curvas de aceleración y strafe de Source).
2. **REPLACE:** Mecánicas sustituidas por la Fuente B (ej. físicas de proyectiles balísticos en vez de hitscan instantáneo).
3. **FUSE:** Mecánicas híbridas nacidas del cruce de ambas (ej. balística de proyectiles interactuando con terreno destructible de vóxeles).
4. **DISCARD:** Elementos descartados deliberadamente para mantener el alcance bajo control.

---

## Prototipado Greybox Obligatorio
Todo controlador de juego nuevo debe validarse primero con geometrías primitivas (`CapsuleShape3D`, `BoxShape3D`) y telemetría de velocidad antes de aplicar cualquier arte visual.

---

## Validación Física Empírica con Area3D (Cero Fórmulas en Aislado)
1. **El Problema del Validador Matemático:** Un cálculo analítico no experimenta fricción, rebotes de suspensión ni deslizamiento lateral en Godot. Conducen a falsos positivos.
2. **Propuesta Colaborativa Obligatoria:** El agente debe proponer activamente al usuario crear/configurar una Escena de Test Físico Mínimo (`res://tests/physical/test_<mecanica>.tscn`).
3. **Sensores de Meta y Diagnóstico:** La escena debe integrar un `Area3D` objetivo (`physical_test_area.gd`) con condiciones cuantitativas de validez (tiempo máximo, ventana de velocidad, ángulo de roll) que imprima diagnósticos explicando **QUÉ PASÓ Y POR QUÉ PASÓ** a nivel de dinámicas de contacto.
4. Consulta técnica completa: [Docs/architecture/physical_validation_harness.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/physical_validation_harness.md).
