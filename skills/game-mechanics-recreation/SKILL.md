---
name: game-mechanics-recreation
description: >-
  Protocolo integral para ingeniería inversa de mecánicas de juego, extracción
  y desacoplamiento de lógica (sin copiar assets para evitar problemas legales),
  replicación matemática exacta del comportamiento y matriz estandarizada de
  fusión/sustitución de mecánicas entre juegos (ej. Counter-Strike + Vholumen).
---

# Game Mechanics Recreation & Fusion Protocol

Este skill proporciona la metodología técnica y los estándares operativos para **recrear, extraer, desacoplar y fusionar mecánicas de videojuegos existentes** en Godot 4 (o motores afines), garantizando:
1. **Cero infracción legal**: Prohibición estricta de copiar assets propietarios (modelos 3D, texturas, sonidos, mapas). Se extrae **exclusivamente la lógica matemática, diagramas de estado y curvas de movimiento**.
2. **Eliminación de descripciones repetitivas**: Mediante la **Matriz de Fusión de Mecánicas**, el usuario define en un único documento conciso qué mecánicas se mantienen, se reemplazan o se fusionan entre dos o más juegos.
3. **Fidelidad de comportamiento (Mathematical Replication)**: Cierre de la brecha entre "encontrar/leer scripts" y "hacer que se sienta idéntico", resolviendo discrepancias de tick-rate, integración de Euler, fricción y física discreta.

---

## 1. El Flujo de Trabajo en 4 Fases

```
   [Fase 1: Búsqueda e Inspec.] -> [Fase 2: Extracción Lógica] -> [Fase 3: Matriz Fusión] -> [Fase 4: Greybox Godot 4]
   (REA / Decompiladores / SDK)   (Ecuaciones / FSM / Inputs)    (Retain / Replace / Fuse)   (Primitivas / Sub-stepping)
```

---

## 2. Fase 1: Estrategia de Búsqueda y Desensamblado (Zero-Asset)

Dependiendo de la tecnología del juego original, utiliza las herramientas autorizadas sin extraer ni transferir ningún archivo binario protegido:

| Motor / Origen | Herramienta de Inspección | Ubicación de la Lógica | Estrategia de Extracción |
| :--- | :--- | :--- | :--- |
| **Source / GoldSrc** (Counter-Strike, HL) | SDK público de Valve / Quake III GPL | `pmove.c`, `gamemovement.cpp` | Consultar la implementación matemática abierta (`PM_Accelerate`, `PM_AirAccelerate`, `PM_Friction`). No tocar `.vpk` ni `.bsp`. |
| **Unity (Mono / C#)** | `ILSpy` / `dnSpy` | `Assembly-CSharp.dll` | Cargar el DLL en desensamblador y extraer únicamente el pseudocódigo C# de los controladores de movimiento (`CharacterController`, `Rigidbody`). |
| **Unity (IL2CPP)** | `Il2CppDumper` + Ghidra / REA | `GameAssembly.dll` + `global-metadata.dat` | Recuperar firmas de métodos y estructuras de datos para reconstruir la máquina de estados. |
| **Unreal Engine** | Servidor MCP `rea` / UModel (inspección de grafos) | `UCharacterMovementComponent`, Blueprints | Inspeccionar curvas de aceleración, vectores de velocidad y sub-stepping de física. |
| **Godot Engine** | `gdre_tools` (Godot RE Tools) | Archivos `.pck` | Extraer scripts `.gd` para auditoría lógica de nodos y llamadas a `move_and_slide()`. |
| **Motores Custom / Voxel (Vholumen)** | Servidor MCP `rea` | Binario ejecutable / bibliotecas `.dll` | Inspeccionar procedimientos de modificación de chunks, algoritmos de raycast sobre grids y generación de mallas procedurales (SurfaceTool / Marching Cubes). |

> [!IMPORTANT]
> **REGLA DE ORO LEGAL:**
> NUNCA importes mallas 3D, texturas, archivos de nivel o clips de audio del juego original. Reemplaza todo con **geometría primitiva (Cylinder3D, Capsule3D, Box3D)** y shaders de depuración procedurales durante toda la fase de prototipado.

---

## 3. Fase 2: Replicación Matemática Exacta del Comportamiento

El problema clásico al leer un script original es que copiar la fórmula directamente en `_physics_process(delta)` en Godot no produce el mismo movimiento. Esto ocurre por tres factores críticos:

### A. Normalización de Tick-Rate y Discrepancias de Integración
- **Juegos clásicos (Source/GoldSrc)**: Corren a tick-rates discretos fijos (64 Hz, 128 Hz o 100 Hz).
- **Godot 4**: Corre por defecto a 60 Hz (`physics/common/physics_ticks_per_second`).
- La integración de Euler discreta:
  $$v_{next} = v \cdot (1 - \text{friction} \cdot \Delta t)$$
  produce desaceleraciones y sensaciones drásticamente distintas si el $\Delta t$ cambia.
- **Solución técnica en Godot**:
  Configurar el proyecto en `Project Settings -> Physics -> Common -> Physics Ticks Per Second` al valor exacto del juego emulado (ej. 128 para movimiento estilo CS), o desacoplar la integración mediante sub-stepping analítico.

### B. Ecuaciones Canónicas de Movimiento (Ejemplo: Bunnyhop & Air-Strafing de CS)
Para recrear con precisión de milisegundo el movimiento de Counter-Strike en GDScript:

```gdscript
class_name CSMovementController
extends CharacterBody3D

@export var max_speed: float = 7.0       # ~250 ups en Source
@export var air_max_speed: float = 0.84   # ~30 ups límite de aceleración aérea
@export var ground_accel: float = 5.5
@export var air_accel: float = 12.0
@export var friction: float = 4.0
@export var stop_speed: float = 2.5
@export var jump_impulse: float = 7.5

func _physics_process(delta: float) -> void:
    var wish_dir := _get_input_direction()
    
    if is_on_floor():
        _apply_friction(delta)
        _ground_move(wish_dir, delta)
        if Input.is_action_pressed("jump"):
            velocity.y = jump_impulse
    else:
        _air_move(wish_dir, delta)
        velocity.y -= ProjectSettings.get_setting("physics/3d/default_gravity") * delta

    move_and_slide()

func _apply_friction(delta: float) -> void:
    var speed := velocity.length()
    if speed < 0.0001:
        return
    var control := maxf(speed, stop_speed)
    var drop := control * friction * delta
    var new_speed := maxf(speed - drop, 0.0)
    velocity = velocity * (new_speed / speed)

func _ground_move(wish_dir: Vector3, delta: float) -> void:
    var current_speed := velocity.dot(wish_dir)
    var add_speed := max_speed - current_speed
    if add_speed <= 0.0:
        return
    var accel_speed := minf(ground_accel * max_speed * delta, add_speed)
    velocity += wish_dir * accel_speed

func _air_move(wish_dir: Vector3, delta: float) -> void:
    var current_speed := velocity.dot(wish_dir)
    var add_speed := air_max_speed - current_speed
    if add_speed <= 0.0:
        return
    var accel_speed := minf(air_accel * max_speed * delta, add_speed)
    velocity += wish_dir * accel_speed
```

> [!NOTE]
> Nota cómo `_air_move` restringe `add_speed` con `air_max_speed` (30 unidades/s). Al girar la cámara perpendicular a `velocity`, el producto punto `velocity.dot(wish_dir)` es cero, permitiendo que la velocidad acumulada crezca continuamente (bunnyhopping).

---

## 4. Fase 3: La Matriz de Fusión de Mecánicas (Mechanic Fusion Matrix)

Para no volver a explicar nunca qué se queda, qué se va y qué se mezcla entre dos proyectos (como Counter-Strike y Vholumen), utiliza este estándar:

### Plantilla de Especificación de Fusión (`mechanic_fusion_spec.md`)

```markdown
# ESPECIFICACIÓN DE FUSIÓN DE MECÁNICAS

## 1. Identificación de Fuentes
- **Juego Base A**: Counter-Strike (Movimiento First-Person, Guns, Recoil, Cam).
- **Juego Base B**: Vholumen (Mundo Voxel, Deformación de Terreno, Física de Partículas).
- **Motor Destino**: Godot 4.3+

## 2. Matriz de Decisiones Operativas
| Subsistema | Origen A | Origen B | Acción (RETAIN / REPLACE / FUSE) | Detalle Técnico |
| :--- | :--- | :--- | :--- | :--- |
| **Locomoción** | CS (Bhop/Air-strafe) | Vholumen (Default walk) | **RETAIN A** | Mantener 100% las ecuaciones Source de aceleración aérea y fricción. |
| **Terreno/Mundo** | CS (Malla estática) | Vholumen (Chunks voxels) | **REPLACE -> B** | Descartar niveles estáticos; usar sistema de chunks octree con SurfaceTool. |
| **Destrucción** | N/A (Impactos calcomanía) | Vholumen (Sustracción voxel) | **RETAIN B** | Cada disparo modifica el buffer de densidades del chunk impactado. |
| **Disparo/Balística** | CS (Hitscan + Spray) | Vholumen (Raycast simple) | **FUSE (A + B)** | Trayectoria de spray de CS (patrón de retroceso) resolviendo contra voxels destruibles de Vholumen. |
| **Cámara** | CS (FPS head-level) | Vholumen (Tercera persona) | **RETAIN A** | Cámara en primera persona anclada a la cabeza del kinematic body. |
| **Colisión Mundo** | CS (Polígonos fijos) | Vholumen (Malla dinámica) | **FUSE (A + B)** | `move_and_slide()` interactuando con `ConcavePolygonShape3D` generado al vuelo por el chunk. |

## 3. Puntos Críticos de Interfaz (Hooks)
- `OnBulletHit(point: Vector3, normal: Vector3, damage: float)` -> Llama a `VoxelTerrain.damage_sphere(point, radius)`.
- `CharacterBody3D.is_on_floor()` -> Debe registrar colisiones contra la superficie regenerada del chunk en el mismo tick.
```

---

## 5. Fase 4: Prototipado Greybox y Verificación en Godot

1. **Uso de Colisionadores Primitivos**:
   - `CapsuleShape3D` para el jugador (radio: $0.4\text{m}$, altura: $1.8\text{m}$).
   - `BoxShape3D` para escombros o piezas de terreno.
2. **Depuración Visual en Tiempo Real**:
   - Dibujar vectores de velocidad y `wish_dir` con `ImmediateMesh` o `MeshInstance3D` cilíndricos.
   - Monitorear `Engine.get_frames_per_second()` y `Engine.get_physics_frames()`.
3. **Cero Dependencia de Modelos Comerciales**:
   - Las armas se representan como cajas compuestas (`BoxMesh`).
   - Los objetivos se representan como prismas o esferas de colores.
   - Al terminar de ajustar la curva matemática, el sistema es 100% legal, modular y exportable a cualquier juego comercial.
