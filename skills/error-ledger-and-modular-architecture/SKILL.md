---
name: error-ledger-and-modular-architecture
description: Sistema para llevar registro formal y control de errores previos con sus causas raíces, soluciones probadas y ejemplos de código antes/después, combinado con una metodología de arquitectura modular estricta para prevenir código espagueti en cualquier proyecto. Úsalo siempre al resolver bugs complejos, registrar lecciones aprendidas o diseñar/refactorizar sistemas en módulos desacoplados.
---

# Error Ledger & Modular Architecture

Esta skill establece dos pilares fundamentales de ingeniería:
1. **Error Ledger:** Registro continuo, análisis de causa raíz y catálogo de soluciones verificadas para evitar repetir errores pasados.
2. **Modular Architecture:** Diseño modular estricto y prevención activa de código espagueti mediante separación de responsabilidades e interfaces explícitas.

---

## PARTE 1: Error Ledger (Control y Registro de Errores)

Nunca intentes parches a ciegas ni asumas que un bug está resuelto sin evidencia empírica. Cada error no trivial debe documentarse siguiendo este estándar.

### Formato Estándar de Registro de Errores

```markdown
### [ERR-XXX] Nombre Descriptivo del Error
- **Fecha y Entorno:** YYYY-MM-DD | Tecnologías involucradas (ej. Blender 5.0, Godot 4.6, Python 3.11)
- **Síntoma Visible:** Qué observa el usuario o qué fallo arroja el sistema (adjuntar mensaje de error o captura).
- **Causa Raíz Real:** Explicación técnica/física/matemática exacta de por qué ocurrió el fallo (no quedarse en el síntoma superficial).
- **Solución Comprobada:** Principio o algoritmo utilizado para resolverlo definitivamente.
- **Ejemplo Antes (Código Erróneo):**
  ```python
  # Código que causó el fallo
  ```
- **Ejemplo Después (Código Corregido):**
  ```python
  # Código corregido con la técnica validada
  ```
- **Prueba de Verificación:** Comando o prueba visual ejecutada para verificar que el fallo desapareció sin efectos secundarios.
```

---

### Casos Reales Documentados

#### [ERR-001] Deformación "Candy-Wrapper" en Huesos por Incompatibilidad de Roll
- **Síntoma:** Extremidades estranguladas, codos y rodillas pellizcados a radio cero al reproducir animaciones.
- **Causa Raíz:** En *Linear Blend Skinning*, forzar rotaciones globales directas (`COPY_ROTATION` en espacio `WORLD`) entre armaduras con diferente roll de reposo ($\Delta \text{Roll} \approx 180^\circ$) induce una torsión longitudinal que colapsa la sección transversal.
- **Solución Comprobada:** Retargeting por matriz de offset relativo:
  $$\mathbf{R}_{\text{offset}} = \mathbf{S}_{\text{rest}}^{-1} \cdot \mathbf{T}_{\text{rest}}$$
  $$\mathbf{T}_{\text{world}}(t) = \mathbf{S}_{\text{world}}(t) \cdot \mathbf{R}_{\text{offset}}$$
- **Código Antes (Incorrecto):**
  ```python
  c_rot = pb.constraints.new('COPY_ROTATION')
  c_rot.target = source_arm
  c_rot.subtarget = src_bone
  c_rot.target_space = 'WORLD'
  c_rot.owner_space = 'WORLD'
  ```
- **Código Después (Correcto):**
  ```python
  # Precomputar offset angular en pose de reposo
  R_offset = S_rest_mat.to_3x3().inverted() @ T_rest_mat.to_3x3()
  # Aplicar en orden jerárquico cuadro a cuadro
  T_rot = S_current_mat.to_3x3() @ R_offset
  pb.matrix = parent_space_eval(T_rot, pb_pos)
  pb.keyframe_insert(data_path="rotation_quaternion", frame=f)
  ```

#### [ERR-002] Destello Blanco Fluorescente (Emission Blowout) en Exportación glTF
- **Síntoma:** El modelo se visualiza completamente blanco y reflectante en Godot/visores glTF, ignorando el color de piel.
- **Causa Raíz:** El nodo Principled BSDF de Blender tiene por defecto `Emission Color = (1, 1, 1)`. Si `Emission Strength` no se fija explícitamente en `0.0`, el exportador glTF emite `emissiveFactor: [1, 1, 1]`, quemando el sombreado.
- **Solución:** Forzar explícitamente `Emission Strength = 0.0` y `Emission Color = (0.0, 0.0, 0.0, 1.0)`.

#### [ERR-003] Desincronización de Ejes FBX por Falta de Aplicación de Transformadas
- **Síntoma:** El esqueleto se visualiza horizontal o rotado $90^\circ$ respecto a la malla.
- **Causa Raíz:** El importador de FBX asigna rotación `(1.57, 0, 0)` a la armadura y `(-1.57, 0, 0)` a la malla para adaptar ejes Y-up a Z-up. Asignar `rotation_euler = (0,0,0)` sin aplicar transformadas genera un desfase permanente.
- **Solución:** Seleccionar simultáneamente malla y esqueleto y ejecutar `bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)`.

---

## PARTE 2: Modular Architecture (Prevención de Código Espagueti)

El código espagueti surge cuando un solo archivo mezcla:
1. Lectura/escritura de archivos (I/O).
2. Lógica matemática o reglas de negocio.
3. Transformación de formatos o llamadas a APIs externas.
4. Parámetros de configuración en duro.

### Estructura de Directorios Modular Obligatoria

Para cualquier script o herramienta que supere las 100 líneas, organiza el código en módulos desacoplados:

```
mi_herramienta/
├── contracts/        # Interfaces, tipos de datos puros y validaciones (sin dependencias externas)
│   └── models.py
├── core/             # Lógica de cálculo, matemáticas y reglas de negocio puras (testables sin I/O)
│   └── calculator.py
├── adapters/         # Comunicación con software externo (Blender API, Godot CLI, VMware, etc.)
│   ├── blender_adapter.py
│   └── vmware_adapter.py
├── pipeline/         # Orquestador del flujo paso a paso (recibe adaptadores y coordina el proceso)
│   └── runner.py
└── cli.py            # Punto de entrada de línea de comandos (parseo de argumentos y logging)
```

### Reglas de Oro contra el Código Espagueti

1. **Límite de Longitud por Archivo:** Ningún archivo debe exceder las 250-300 líneas. Si se acerca al límite, divide en submódulos especializados.
2. **Inversión de Dependencias:** El módulo `core/` **nunca** debe importar librerías pesadas o de entorno (como `bpy`, `godot` o llamadas directas de red). Debe recibir datos limpios y devolver resultados estructurados.
3. **Funciones Puras para Cálculos:** Todas las matemáticas (retargeting de matrices, cálculo de mermas, despiece) deben estar en funciones independientes testeables sin necesidad de abrir Blender, la VM o una base de datos.
4. **Contratos de Entrada y Salida:** Define clases de datos (`@dataclass` o `TypedDict`) para el paso de información entre módulos en lugar de diccionarios anidados arbitrarios.
