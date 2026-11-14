# ESPECIFICACIÓN DE FUSIÓN DE MECÁNICAS

## 1. Identificación del Proyecto
- **Nombre del Proyecto Fusionado**: [Ej: Vholumen-Strike]
- **Juego Base A**: [Ej: Counter-Strike - Mecánicas de movimiento y disparo]
- **Juego Base B**: [Ej: Vholumen - Mecánicas de vóxeles y deformación]
- **Motor / Versión**: Godot 4.x

---

## 2. Matriz de Clasificación (Retain / Replace / Fuse / Discard)

| Subsistema | Origen A | Origen B | Acción | Justificación y Regla Técnica |
| :--- | :--- | :--- | :--- | :--- |
| **Locomoción** | | | `RETAIN A` / `RETAIN B` | |
| **Cámara y Vista** | | | `RETAIN` / `FUSE` | |
| **Física de Suelo/Aire** | | | `FUSE` | |
| **Armas / Herramientas** | | | `REPLACE` | |
| **Entorno / Terreno** | | | `RETAIN B` | |
| **Efectos / Audio** | | | `DISCARD` (Procedural) | |

---

## 3. Desglose de Fórmulas y Comportamiento Matemático
- **Tick-rate objetivo**: [Ej: 64 Hz / 128 Hz]
- **Fórmulas de aceleración**:
  - Suelo:
  - Aire:
  - Fricción:
- **Curvas de respuesta de entrada (Input Response)**:

---

## 4. Interfaces y Señales de Comunicación
- `Signal 1`:
- `Signal 2`:
- `API Pública entre módulos`:

---

## 5. Criterios de Aceptación Greybox (Zero-Asset)
- [ ] El controlador se mueve con primitivas (`CapsuleShape3D`) sin mallas comerciales.
- [ ] La velocidad máxima y aceleración coinciden con las métricas del juego original.
- [ ] Los sistemas fusionados no generan excepciones ni fugas de memoria en `_physics_process`.
