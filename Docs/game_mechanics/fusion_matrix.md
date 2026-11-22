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
