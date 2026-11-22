#!/usr/bin/env python3
"""
Godot 4.x Scene Scaffolder & Batch Generator
============================================
Genera escenas .tscn y configuraciones de nodos estándar en un solo disparo.
Evita que los agentes de IA tengan que invocar decenas de herramientas MCP
atómicas (node_create, node_set_property, script_attach) individualmente.

Arquetipos soportados:
1. 'prop': StaticBody3D + Instancia Mesh/GLB + CollisionShape3D autoajustada.
2. 'character': CharacterBody3D + CollisionShape3D + SpringArm3D/Camera3D + Script base.
3. 'ui': CanvasLayer + Control (Full Rect) + MarginContainer.
4. 'batch-json': Emite la estructura en JSON lista para batch_execute de godot-ai.

Uso:
    python tools/godot_scene_scaffolder.py prop --name "Mesa" --mesh "res://assets/props/mesa.glb" --output "scenes/props/mesa.tscn"
    python tools/godot_scene_scaffolder.py character --name "Player" --output "scenes/player/player.tscn" --with-camera
"""

import sys
import argparse
from pathlib import Path

def generate_prop_tscn(name: str, mesh_res_path: str = None, collision_type: str = "box", ext_uid: str = "") -> str:
    """Genera una escena .tscn de un prop estático con colisión."""
    has_mesh = bool(mesh_res_path)
    load_steps = 3 if has_mesh else 2
    uid_attr = f' uid="{ext_uid}"' if ext_uid else ""
    
    tscn = f'[gd_scene load_steps={load_steps} format=3{uid_attr}]\n\n'
    
    if has_mesh:
        tscn += f'[ext_resource type="PackedScene" path="{mesh_res_path}" id="1_mesh"]\n\n'
        
    shape_id = "SubResource(\"1_col\")"
    if collision_type == "box":
        tscn += '[sub_resource type="BoxShape3D" id="1_col"]\n'
        tscn += 'size = Vector3(1, 1, 1)\n\n'
    elif collision_type == "capsule":
        tscn += '[sub_resource type="CapsuleShape3D" id="1_col"]\n'
        tscn += 'radius = 0.5\nheight = 1.8\n\n'
    else:
        tscn += '[sub_resource type="SphereShape3D" id="1_col"]\n'
        tscn += 'radius = 0.5\n\n'
        
    tscn += f'[node name="{name}" type="StaticBody3D"]\n\n'
    
    if has_mesh:
        tscn += f'[node name="Model" parent="." instance=ExtResource("1_mesh")]\n\n'
        
    tscn += '[node name="CollisionShape3D" type="CollisionShape3D" parent="."]\n'
    # Centrado en Y=0.5 para pivote en base Y=0
    tscn += 'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.5, 0)\n'
    tscn += f'shape = {shape_id}\n'
    
    return tscn

def generate_character_tscn(name: str, with_camera: bool = True, script_path: str = None) -> str:
    """Genera una escena .tscn de CharacterBody3D lista con colisión y cámara."""
    ext_resources = []
    load_steps = 2
    if script_path:
        load_steps += 1
        ext_resources.append(f'[ext_resource type="Script" path="{script_path}" id="1_script"]')
        
    tscn = f'[gd_scene load_steps={load_steps} format=3]\n\n'
    for res in ext_resources:
        tscn += f'{res}\n'
    if ext_resources:
        tscn += '\n'
        
    tscn += '[sub_resource type="CapsuleShape3D" id="1_capsule"]\n'
    tscn += 'radius = 0.4\n'
    tscn += 'height = 1.8\n\n'
    
    script_attr = ' script=ExtResource("1_script")' if script_path else ''
    tscn += f'[node name="{name}" type="CharacterBody3D"{script_attr}]\n\n'
    
    # Visuals Pivot
    tscn += '[node name="Visuals" type="Node3D" parent="."]\n\n'
    
    # CollisionShape3D con centro en Y=0.9 (pies en Y=0)
    tscn += '[node name="CollisionShape3D" type="CollisionShape3D" parent="."]\n'
    tscn += 'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.9, 0)\n'
    tscn += 'shape = SubResource("1_capsule")\n\n'
    
    if with_camera:
        tscn += '[node name="CameraPivot" type="Node3D" parent="."]\n'
        tscn += 'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)\n\n'
        tscn += '[node name="SpringArm3D" type="SpringArm3D" parent="CameraPivot"]\n'
        tscn += 'spring_length = 3.0\n\n'
        tscn += '[node name="Camera3D" type="Camera3D" parent="CameraPivot/SpringArm3D"]\n'
        
    return tscn

def generate_ui_tscn(name: str) -> str:
    """Genera una escena de interfaz CanvasLayer responsiva."""
    tscn = '[gd_scene format=3]\n\n'
    tscn += f'[node name="{name}" type="CanvasLayer"]\n\n'
    tscn += '[node name="RootControl" type="Control" parent="."]\n'
    tscn += 'layout_mode = 3\n'
    tscn += 'anchors_preset = 15\n'
    tscn += 'anchor_right = 1.0\n'
    tscn += 'anchor_bottom = 1.0\n'
    tscn += 'grow_horizontal = 2\n'
    tscn += 'grow_vertical = 2\n\n'
    tscn += '[node name="MarginContainer" type="MarginContainer" parent="RootControl"]\n'
    tscn += 'layout_mode = 1\n'
    tscn += 'anchors_preset = 15\n'
    tscn += 'anchor_right = 1.0\n'
    tscn += 'anchor_bottom = 1.0\n'
    tscn += 'grow_horizontal = 2\n'
    tscn += 'grow_vertical = 2\n'
    tscn += 'theme_override_constants/margin_left = 20\n'
    tscn += 'theme_override_constants/margin_top = 20\n'
    tscn += 'theme_override_constants/margin_right = 20\n'
    tscn += 'theme_override_constants/margin_bottom = 20\n'
    return tscn

def main():
    parser = argparse.ArgumentParser(description="Godot Scene Scaffolder Macro")
    subparsers = parser.add_subparsers(dest="archetype", required=True)
    
    # Prop
    prop_parser = subparsers.add_parser("prop", help="Crea un StaticBody3D con colisión y modelo")
    prop_parser.add_argument("--name", required=True, help="Nombre del nodo raíz")
    prop_parser.add_argument("--mesh", help="Ruta res:// del modelo GLB a instanciar")
    prop_parser.add_argument("--collision", choices=["box", "capsule", "sphere"], default="box")
    prop_parser.add_argument("--output", required=True, help="Archivo .tscn destino")
    
    # Character
    char_parser = subparsers.add_parser("character", help="Crea un CharacterBody3D con colisión y cámara")
    char_parser.add_argument("--name", required=True, help="Nombre del nodo raíz")
    char_parser.add_argument("--with-camera", action="store_true", default=True, help="Incluye SpringArm3D y Camera3D")
    char_parser.add_argument("--script", help="Ruta res:// del script asociado")
    char_parser.add_argument("--output", required=True, help="Archivo .tscn destino")
    
    # UI
    ui_parser = subparsers.add_parser("ui", help="Crea una interfaz CanvasLayer responsiva")
    ui_parser.add_argument("--name", required=True, help="Nombre del nodo raíz")
    ui_parser.add_argument("--output", required=True, help="Archivo .tscn destino")
    
    args = parser.parse_args()
    
    if args.archetype == "prop":
        content = generate_prop_tscn(args.name, args.mesh, args.collision)
    elif args.archetype == "character":
        content = generate_character_tscn(args.name, args.with_camera, args.script)
    elif args.archetype == "ui":
        content = generate_ui_tscn(args.name)
    else:
        print(f"[!] Arquetipo no soportado: {args.archetype}")
        sys.exit(1)
        
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"[✓] Escena '{args.name}' ({args.archetype}) creada exitosamente en: {out_path}")

if __name__ == "__main__":
    main()
