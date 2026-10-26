# GUÍA Y ARQUITECTURA DE HERRAMIENTAS: CONVERSIÓN DE ASSETS (UNREAL, UNITY Y OTROS) A BLENDER 5.0

> **Fecha:** 2026-10-25  
> **Objetivo:** Establecer el catálogo de herramientas y el pipeline unificado para extraer activos de videojuegos (Unreal Engine, Unity, etc.), procesarlos mediante **Blender 5.0 headless** como intermediario central, y exportarlos de forma optimizada a cualquier destino (Godot, glTF/GLB, FBX, USD).

---

## 1. Arquitectura del Pipeline Intermediario

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CAPA 1: EXTRACTORES DE MOTOR (DUMPERS)               │
├────────────────────────┬─────────────────────────┬─────────────────────┤
│  UNREAL (UE4 / UE5)    │  UNITY (.assets/bundle) │ OTROS / PROPIETARIO │
│  • UModel (Gildor)     │  • AssetRipper          │ • SourceIO (Source) │
│  • FModel + CUE4Parse  │  • AssetStudio CLI/GUI  │ • Noesis (Exóticos) │
│  • io_scene_ueformat   │  • UnityPy (Python)     │ • RenderDoc (VRAM)  │
└───────────┬────────────┴────────────┬────────────┴──────────┬──────────┘
            │ (.psk/.psa/.uemodel)    │ (.fbx/.obj/glTF)      │ (.obj/fbx)
            └─────────────────────────┼───────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│              CAPA 2: MOTOR INTERMEDIARIO (BLENDER 5.0 HEADLESS)        │
│          "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Normalización de ejes (Y-up de Unity vs Z-up Blender vs X-forward)   │
│ 2. Corrección de canales PBR (DirectX vs OpenGL Y- en Normal Maps)     │
│ 3. Pistas de animación con Slotted Actions (Sistema Animation 2025)   │
│ 4. Limpieza de máscaras de vertex colors (evita colores payaso)        │
└─────────────────────────────────────┬──────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│              CAPA 3: DESTINO Y EXPORTACIÓN UNIVERSAL                   │
├────────────────────────────────────────────────────────────────────────┤
│ • glTF 2.0 / .glb  --> Godot 4.6, WebGL, Three.js, engines modernos    │
│ • FBX              --> Unity, Unreal Engine, Maya                      │
│ • USD / USDA       --> Omniverse, pipelines cinematográficos           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Herramientas por Motor de Origen

### A. Unreal Engine (UE4 / UE5)

| Herramienta | Formatos de Entrada | Formatos de Salida | Casos de Uso Recomendados |
| :--- | :--- | :--- | :--- |
| **UModel (UE Viewer)** | `.uasset`, `.pak` (UE1 - UE4.27) | `.psk`, `.pskx`, `.psa`, `.tga` | Juegos UE4 estables (como ARK DevKit). Extremadamente rápido para animaciones y mallas esqueléticas. |
| **FModel** | `.pak`, `.utoc`, `.ucas`, IoStore, UE5.0 - UE5.5+ | `.uemodel`, `.ueanim`, `.png` | Juegos modernos UE5 y UE4 cifrados con AES o con mappings `.usmap`. |
| **Addon `io_scene_psk_psa`** | `.psk`, `.pskx`, `.psa` | Mallas y esqueletos en Blender | Ya instalado en tu Blender 5.0. |
| **Addon `io_scene_ueformat`** | `.uemodel`, `.ueanim` | Mallas y esqueletos en Blender | Ya instalado en tu Blender 5.0 (usado con FModel). |
| **Fortnite Porting / CUE4Parse** | Live IoStore / CUE4Parse | Import directo en Blender | Addon activo en tu Blender con servidor local. |

---

### B. Unity (.unity3d, AssetBundles, .assets)

| Herramienta | Formatos de Entrada | Formatos de Salida | Casos de Uso Recomendados |
| :--- | :--- | :--- | :--- |
| **AssetRipper** | Carpetas completas de juegos Unity, `.assets`, `globalgamemanagers` | Proyecto Unity completo, `.fbx`, `.glb` | La herramienta más completa para reconstruir proyectos o volcar escenas completas con jerarquía y materiales. |
| **AssetStudio / RazTools** | `.assets`, AssetBundles | `.fbx` (con rigging), `.obj`, `.png` | Volcado rápido de modelos individuales, animaciones (`AnimationClip`) y texturas sin necesidad de instalar el editor de Unity. |
| **UnityPy (Python)** | Archivos y paquetes de Unity | Mallas brutas, texturas, scripts | Automatización sin interfaz gráfica (Headless). Permite crear scripts en Python que extraen mallas directamente para Blender. |

---

### C. Otros Motores y Formatos Exóticos

| Herramienta | Tipo | Utilidad |
| :--- | :--- | :--- |
| **SourceIO (Blender Addon)** | Addon nativo de Blender | Importa modelos (`.mdl`, `.vmdl`), materiales (`.vmt`) y mapas (`.bsp`, `.vpk`) del Source Engine y Source 2 (Valve). |
| **Noesis (Rich Whitehouse)** | Programa ejecutable + plugins Python | El "desencriptador universal" para formatos propietarios japoneses, consolas (PS2, PS3, Switch) y motores independientes. |
| **RenderDoc + Blender Importer** | GPU Frame Grabber | **Último recurso infalible:** Captura directamente las llamadas de dibujado (draw calls) de la VRAM (DirectX 11/12/Vulkan). Extrae la geometría y texturas exactas renderizadas en pantalla cuando los archivos están cifrados. |

---

## 3. Puntos Críticos al Pasar por Blender 5.0 como Intermediario

1. **Slotted Actions (Animation 2025 de Blender 5.0):**
   - A diferencia de Blender 3.x/4.x donde las fcurves se creaban libremente en `action.fcurves.new`, en Blender 5.0 las acciones tienen capas (*slots*). Para enlazar huesos:
     ```python
     # En Blender 5.0:
     slot = action.slots.new(id_type='OBJECT') # o asignación a armature
     fcurve = action.fcurve_ensure_for_datablock(armature, path, index=axis_idx)
     ```
2. **Normal Map Inversion (DirectX vs OpenGL):**
   - Unreal Engine y algunos juegos de Unity usan coordenadas **DirectX (Y-)**, mientras que Blender, Godot y el formato glTF esperan **OpenGL (Y+)**.
   - En el shader de Blender, se debe invertir el canal verde (G / Y) mediante un nodo *Invert* o *Separate Color* si la iluminación luce invertida.
3. **Máscaras de Vertex Color:**
   - Motores como Unreal suelen almacenar IDs de partes o tintes en los colores de vértice (`COLOR_0`). Si se pasan a glTF/Godot sin filtrar, el modelo aparece con colores brillantes ("payaso"). Se deben limpiar o desconectar en el material si no se usan como tinte.

---

## 4. Próximos Pasos en el Repositorio

1. **Integrar `UnityPy` y crear un extractor CLI para Unity**: Desarrollar `tools/unity_extractor.py` para poder volcar assets de Unity con la misma fluidez que se hace con Unreal.
2. **Crear una Skill unificada (`skills/universal-asset-porter`)**: Unificar las directrices de importación, limpieza y exportación en Blender 5.0 para cualquier motor.
