---
name: universal-asset-porter
description: "Pipeline automatizado para extraer activos de motores de videojuegos (Unity, Unreal Engine, Source, etc.), procesarlos y estandarizarlos utilizando Blender 5.0 headless como intermediario, y exportarlos a Godot 4.6 (glTF/GLB), FBX o USD."
license: MIT
metadata:
  version: "1.0"
  blender_version: "5.0"
---

# Universal Asset Porter (Game Engines to Blender 5.0 / Godot / FBX)

Esta skill proporciona flujos de trabajo automatizados para extraer modelos, texturas y animaciones de diferentes motores (Unity, Unreal Engine, etc.), estandarizarlos en **Blender 5.0 headless** y exportarlos listos para su uso en **Godot 4.6**, **WebGL**, **Unity**, o **Unreal**.

---

## 1. Arquitectura del Flujo

```
[Origen: Unity / Unreal / Otros]
    ├── Unity (.assets, .bundle)     --> tools/unity_asset_extractor.py  --> .obj, .png
    ├── Unreal (.uasset / ARK)       --> UModel (-notex)                 --> .psk, .psa
    └── Unreal UE5 (IoStore / Pak)   --> FModel                          --> .uemodel, .ueanim
                                               │
                                               ▼
                              [Blender 5.0 Headless Bridge]
                              "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
                              (tools/blender_universal_bridge.py)
                              • Conversión de Normales (DirectX Y- a OpenGL Y+)
                              • Slotted Actions (Sistema Animation 2025 de Blender 5.0)
                              • Limpieza de Vertex Colors (elimina máscaras payaso)
                              • Materiales PBR y soporte de Foliage (Alpha Scissor, Double-Sided)
                                               │
                                               ▼
                                      [Destino Final]
                              • Godot 4.6 / WebGL (.glb)
                              • Unity / Unreal / DCC (.fbx)
                              • USD / Pixar Universal Scene (.usd)
```

---

## 2. Herramientas del Pipeline

| Herramienta | Ubicación / Comando | Propósito |
| :--- | :--- | :--- |
| **Blender 5.0** | `C:\Program Files\Blender Foundation\Blender 5.0\blender.exe` | Motor de procesamiento headless |
| **Unity Extractor** | `tools/unity_asset_extractor.py` | Extrae mallas (`Mesh` -> OBJ), texturas y audio de Unity |
| **Blender Bridge** | `tools/blender_universal_bridge.py` | Script Python ejecutado dentro de Blender |
| **CLI Orquestador** | `tools/asset_converter.py` | CLI unificado para operaciones en un solo paso |

---

## 3. Guía Operativa

### Caso A: Extraer e inspeccionar archivos de Unity
Para ver qué contiene un archivo `.assets`, `.unity3d` o `AssetBundle`:
```powershell
# Listar clases y activos
python tools/unity_asset_extractor.py list "ruta/al/archivo.assets"

# Extraer solo mallas y texturas
python tools/unity_asset_extractor.py extract "ruta/al/archivo.assets" --output "extracted/" --types Mesh Texture2D
```

### Caso B: Convertir modelo de Unity a Godot 4.6 (glTF/GLB) en un solo paso
```powershell
python tools/asset_converter.py unity-to-glb `
  --input "game_Data/sharedassets0.assets" `
  --mesh-name "CharacterMesh" `
  --output "godot_project/models/character.glb" `
  --albedo "extracted/Texture2D/Character_Albedo.png" `
  --normal "extracted/Texture2D/Character_Normal.png"
```

### Caso C: Procesar activos de Unreal Engine (.psk/.psa) a GLB con animaciones
```powershell
python tools/asset_converter.py port `
  --mesh "extracted/Creature.psk" `
  --anims "extracted/Creature_Walk.psa" "extracted/Creature_Attack.psa" `
  --output "godot_project/creatures/creature.glb" `
  --albedo "extracted/Creature_BaseColor.png" `
  --normal "extracted/Creature_Normal.png" `
  --invert-normal-y `
  --clean-vertex-colors
```

### Caso D: Foliage / Vegetación (Plantas, Árboles, Hojas)
Las hojas de Unreal y Unity son tarjetas de un solo polígono con texturas alfa:
```powershell
python tools/asset_converter.py port `
  --mesh "extracted/Tree_Leaves.obj" `
  --output "godot_project/props/tree_leaves.glb" `
  --albedo "extracted/Tree_Atlas.png" `
  --normal "extracted/Tree_Normal.png" `
  --two-sided `
  --alpha-scissor 0.5
```

---

## 4. Reglas Críticas del Intermediario Blender 5.0

1. **Normal Maps (DirectX vs OpenGL):**
   - Unreal Engine y ciertos juegos de Unity exportan mapas de normales con el canal verde invertido (DirectX). Al exportar hacia Godot o Blender glTF, usa siempre `--invert-normal-y` para evitar que la iluminación se vea hundida o al revés.
2. **Vertex Colors en Unreal (`--clean-vertex-colors`):**
   - Activos de juegos como ARK: Survival Evolved almacenan zonas de tinte en `COLOR_0`. Si no se limpian, el modelo se renderiza con manchas rojas, azules y verdes ("colores payaso").
3. **Slotted Actions (Blender 5.0):**
   - Blender 5.0 introdujo el nuevo sistema de animación en capas (*Slotted Actions*). Los scripts enlazan los datablocks de la armadura a través de las nuevas APIs sin romper la compatibilidad con el exportador glTF.
