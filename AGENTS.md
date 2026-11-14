# Protocolo Global de Operación de Agentes Antigravity

Este archivo de reglas globales aplica a **todas las sesiones, agentes y espacios de trabajo** en este entorno. Establece los estándares arquitectónicos, metodológicos y de memoria persistente para el desarrollo de proyectos y recreación de videojuegos.

---

## 1. Reglas de Inicio y Memoria Persistente (RAG + MCP)
1. **Consulta de Memoria Cruzada (`claude-mem`)**:
   - Antes de formular preguntas al usuario sobre mecánicas previas, configuraciones de proyectos ya trabajados o soluciones a errores conocidos, el agente DEBE ejecutar una búsqueda semántica usando las herramientas MCP de `claude-mem` (`smart_search` o `query_corpus`).
   - Si una tarea implica un patrón ya resuelto (ej. curvas de fricción estilo Source, chunks de vóxeles estilo Vholumen, configuración de exportación en Blender), recupera la solución probada sin forzar al usuario a reexplicarla.
2. **Registro de Nuevos Aprendizajes**:
   - Cada solución a un bug complejo o decisión arquitectónica relevante debe persistirse en el Error Ledger y registrarse en memoria (`save_memory`).

---

## 2. Recreación de Videojuegos y Fusión de Mecánicas (`game-mechanics-recreation`)
1. **Cero Copia de Assets Comerciales**:
   - Prohibido copiar mallas 3D, texturas, audios o mapas de juegos comerciales para evitar problemas de copyright.
   - Extraer **únicamente la lógica matemática, diagramas de estado, ecuaciones de movimiento y algoritmos**.
2. **Matriz de Fusión de Mecánicas**:
   - Cuando el usuario solicite fusionar o recrear mecánicas entre juegos (ej. Counter-Strike + Vholumen), el agente NO pedirá explicaciones extensas y repetitivas.
   - El agente estructurará la discusión directamente mediante la **Matriz de Fusión**:
     - `RETAIN`: Mecánicas mantenidas de la Fuente A.
     - `REPLACE`: Mecánicas reemplazadas por la Fuente B.
     - `FUSE`: Mecánicas híbridas (ej. balística de A interactuando con terreno deformable de B).
     - `DISCARD`: Elementos descartados.
3. **Prototipado Greybox**:
   - Todo controlador de juego nuevo debe verificarse primero con geometría primitiva (`CapsuleShape3D`, `BoxShape3D`) y gráficos de velocidad en tiempo real antes de aplicar cualquier arte visual.

---

## 3. Integridad Espacial 3D/2D en Godot (`godot-spatial-alignment`)
1. **Cero Z-Fighting / Solapamiento**:
   - No colocar caras coplanares en las mismas coordenadas. Aplicar desfase mínimo de seguridad ($0.001\text{m}$ a $0.003\text{m}$) o nodos `Decal`.
2. **Normalización de Pivotes en Blender**:
   - Todo modelo exportado a Godot 4 debe tener transformaciones aplicadas (`Ctrl+A -> Rotation & Scale`).
   - El pivote debe situarse en la base inferior del objeto ($Z = \min(Z)$ en Blender, $Y = 0$ en Godot) para piezas de escenario, props y personajes.
3. **Mapeo de Canales PBR**:
   - Para mapas ORM: Rojo = AO (`ao_texture_channel = 0`), Verde = Roughness (`roughness_texture_channel = 1`), Azul = Metallic (`metallic_texture_channel = 2`).
   - Normal Maps con formato DirectX: Activar `Invert Y` en el import dock de Godot 4 para coincidir con la convención OpenGL/Vulkan.
   - Proyectos Pixel Art (2D o 3D): Fijar `Default Texture Filter` en `Nearest` para evitar desenfoque bilineal.

---

## 4. Arquitectura Modular y Control de Errores (`error-ledger-and-modular-architecture`)
1. **Desacoplamiento Estricto**:
   - Ningún script debe exceder 300 líneas si mezcla responsabilidades.
   - Separar Entrada de Usuario (Input), Lógica de Estado (State Machine), Fórmulas Físicas (Kinematics) y Representación Visual (Rendering).
2. **Comunicación por Señales**:
   - Comunicación de abajo hacia arriba mediante `signal`; llamadas directas únicamente de arriba hacia abajo (`call`).
