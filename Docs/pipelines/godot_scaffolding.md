# Manual de Uso: Godot Scene Scaffolder Macro

**Script:** [`tools/godot_scene_scaffolder.py`](file:///c:/Users/cesar/Desktop/skill/tools/godot_scene_scaffolder.py)

---

## Propósito
Genera escenas `.tscn` completas sin tener que llamar a `node_create`, `node_set_property` y `script_attach` paso a paso por MCP.

---

## Comandos Rápidos

### 1. Prop Estático con Colisión y Malla
```bash
python tools/godot_scene_scaffolder.py prop \
       --name "Cofre" \
       --mesh "res://assets/props/cofre.glb" \
       --collision box \
       --output "scenes/props/cofre.tscn"
```

### 2. CharacterBody3D con Cámara y Pies en Y=0
```bash
python tools/godot_scene_scaffolder.py character \
       --name "Player" \
       --output "scenes/player/player.tscn" \
       --with-camera
```

### 3. Lienzo CanvasLayer Responsivo
```bash
python tools/godot_scene_scaffolder.py ui \
       --name "HUD" \
       --output "scenes/ui/hud.tscn"
```
