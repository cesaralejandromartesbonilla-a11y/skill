#!/usr/bin/env python3
"""
Blender 5.0 Universal Intermediary Bridge
Procesa mallas, esqueletos, animaciones y materiales PBR desde cualquier motor
(Unreal Engine, Unity, Source, etc.) y los exporta a formatos modernos (glTF/GLB para Godot, FBX, USD).

Ejecución headless:
    & "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" -b --python tools/blender_universal_bridge.py -- [OPCIONES]

Opciones:
    --mesh <ruta_malla>          Archivo .obj, .fbx, .gltf, .glb, .psk, .pskx o .uemodel
    --anims <ruta1> [ruta2...]   Archivos de animación .psa, .ueanim o .fbx
    --output <ruta_salida>       Destino del modelo (ej. salida.glb, salida.fbx)
    --name <nombre>              Nombre base del modelo / colección
    --albedo <ruta_tex>          Ruta a la textura Diffuse/Albedo/BaseColor
    --normal <ruta_tex>          Ruta a la textura Normal Map
    --roughness <ruta_tex>       Ruta a la textura de Rugosidad / Mascara
    --metallic <ruta_tex>        Ruta a la textura Metálica
    --invert-normal-y            Invierte el canal verde (DirectX a OpenGL)
    --clean-vertex-colors        Elimina capas de color de vértices (evita colores payaso)
    --two-sided                  Doble cara (para follaje, plantas o tarjetas)
    --alpha-scissor <umbral>     Recorte alfa (Alpha Scissor, default 0.5)
"""

import sys
import os
import argparse
from pathlib import Path

# Asegurar entorno bpy
try:
    import bpy
    import mathutils
except ImportError:
    print("[!] Este script debe ejecutarse dentro de Blender con la bandera --python.")
    sys.exit(1)

def reset_scene():
    """Elimina todos los objetos, materiales y acciones previas para iniciar en limpio."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Limpiar datos residuales
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.armatures: bpy.data.armatures.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.actions: bpy.data.actions.remove(block)
    for block in bpy.data.images: bpy.data.images.remove(block)

def import_mesh(mesh_path: Path):
    """Importa la malla según su extensión."""
    ext = mesh_path.suffix.lower()
    print(f"[*] Importando malla ({ext}): {mesh_path}")
    
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(mesh_path))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(mesh_path))
    elif ext in [".gltf", ".glb"]:
        bpy.ops.import_scene.gltf(filepath=str(mesh_path))
    elif ext in [".psk", ".pskx"]:
        if hasattr(bpy.ops.import_scene, "psk"):
            bpy.ops.import_scene.psk(filepath=str(mesh_path))
        else:
            raise RuntimeError("El operador bpy.ops.import_scene.psk no está disponible en Blender.")
    elif ext == ".uemodel":
        if hasattr(bpy.ops.import_scene, "uemodel"):
            bpy.ops.import_scene.uemodel(filepath=str(mesh_path))
        else:
            raise RuntimeError("El operador io_scene_ueformat no está habilitado.")
    elif ext in [".smd", ".dmx"]:
        if hasattr(bpy.ops.import_scene, "smd"):
            bpy.ops.import_scene.smd(filepath=str(mesh_path))
        elif hasattr(bpy.ops.import_scene, "source_engine"):
            bpy.ops.import_scene.source_engine(filepath=str(mesh_path))
        else:
            raise RuntimeError("El operador para importar SMD/DMX (Blender Source Tools o SourceIO) no está instalado en Blender.")
    elif ext in [".mdl", ".vmdl", ".vmdl_c"]:
        if hasattr(bpy.ops, "sourceio") and hasattr(bpy.ops.sourceio, "mdl"):
            bpy.ops.sourceio.mdl(filepath=str(mesh_path))
        elif hasattr(bpy.ops.import_scene, "mdl"):
            bpy.ops.import_scene.mdl(filepath=str(mesh_path))
        else:
            raise RuntimeError(f"Para importar directamente {ext} de Valve Source, instale el addon SourceIO en Blender o descompile a .smd / .obj mediante Crowbar.")
    else:
        raise ValueError(f"Formato de malla no soportado: {ext}")

def find_armature_and_meshes():
    """Encuentra la armadura principal y las mallas importadas."""
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    armature = armatures[0] if armatures else None
    return armature, meshes

def apply_transforms(meshes, armature=None):
    """Aplica todas las transformaciones (rotación, escala, posición) para evitar deformaciones en Godot."""
    bpy.ops.object.select_all(action='DESELECT')
    if armature:
        armature.select_set(True)
    for m in meshes:
        m.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    print("[+] Transformaciones aplicadas (Ctrl+A -> Rotation, Scale, Location).")

def normalize_pivot_to_base(meshes):
    """
    Normaliza el pivote al centro de la base inferior del modelo (Z = min(Z) en Blender, Y = 0 en Godot).
    Cumple estrictamente con la regla godot-spatial-alignment.
    """
    if not meshes:
        return
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    for obj in meshes:
        for corner in obj.bound_box:
            world_coord = obj.matrix_world @ mathutils.Vector(corner)
            min_x = min(min_x, world_coord.x)
            max_x = max(max_x, world_coord.x)
            min_y = min(min_y, world_coord.y)
            max_y = max(max_y, world_coord.y)
            min_z = min(min_z, world_coord.z)
            max_z = max(max_z, world_coord.z)
            
    target_origin = mathutils.Vector(((min_x + max_x) / 2.0, (min_y + max_y) / 2.0, min_z))
    saved_cursor = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = target_origin
    
    for obj in meshes:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        # Alinear base del objeto a Z=0
        obj.location.z -= min_z
        obj.select_set(False)
        
    bpy.context.scene.cursor.location = saved_cursor
    print(f"[+] Pivote normalizado a la base inferior: Z={min_z:.4f} -> 0.0 (Y=0 en Godot)")

def sanitize_geometry(meshes):
    """Elimina vértices duplicados, caras degeneradas y recalcula normales hacia afuera."""
    for obj in meshes:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        # Merge by distance (remover dobles a 0.1mm)
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        # Recalcular normales al exterior
        bpy.ops.mesh.normals_make_consistent(inside=False)
        # Eliminar elementos sueltos
        bpy.ops.mesh.delete_loose()
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"[+] Geometría desinfectada (merge doubles, normales exteriores) para: {obj.name}")

def clean_vertex_colors(meshes):
    """Elimina las capas de colores de vértices (evita tintes y colores payaso)."""
    for mesh_obj in meshes:
        mesh_data = mesh_obj.data
        if hasattr(mesh_data, "color_attributes"):
            while mesh_data.color_attributes:
                mesh_data.color_attributes.remove(mesh_data.color_attributes[0])
            print(f"[+] Vertex colors eliminados de: {mesh_obj.name}")

def setup_pbr_material(mesh_obj, args):
    """Configura el material Principled BSDF con soporte para DirectX/OpenGL y recortes alfa."""
    mat_name = f"{mesh_obj.name}_Material"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Nodos principales
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (600, 0)
    
    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (200, 0)
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # 1. Albedo / Base Color
    if args.albedo and os.path.exists(args.albedo):
        albedo_img = bpy.data.images.load(args.albedo)
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.image = albedo_img
        tex_node.location = (-300, 200)
        links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
        
        # Conectar Alpha si se usa corte o transparencia
        if args.alpha_scissor is not None or args.two_sided:
            links.new(tex_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])
    
    # 2. Normal Map
    if args.normal and os.path.exists(args.normal):
        norm_img = bpy.data.images.load(args.normal)
        norm_img.colorspace_settings.name = 'Non-Color'
        
        norm_tex_node = nodes.new(type='ShaderNodeTexImage')
        norm_tex_node.image = norm_img
        norm_tex_node.location = (-600, -200)
        
        norm_map_node = nodes.new(type='ShaderNodeNormalMap')
        norm_map_node.location = (-100, -200)
        
        if args.invert_normal_y:
            # Separar canales RGB, invertir el canal Verde (Y), y recombinar
            sep_node = nodes.new(type='ShaderNodeSeparateColor')
            sep_node.location = (-400, -200)
            links.new(norm_tex_node.outputs['Color'], sep_node.inputs['Color'])
            
            inv_node = nodes.new(type='ShaderNodeInvert')
            inv_node.location = (-250, -220)
            links.new(sep_node.outputs['Green'], inv_node.inputs['Color'])
            
            comb_node = nodes.new(type='ShaderNodeCombineColor')
            comb_node.location = (-100, -200)
            links.new(sep_node.outputs['Red'], comb_node.inputs['Red'])
            links.new(inv_node.outputs['Color'], comb_node.inputs['Green'])
            links.new(sep_node.outputs['Blue'], comb_node.inputs['Blue'])
            
            norm_map_node.location = (50, -200)
            links.new(comb_node.outputs['Color'], norm_map_node.inputs['Color'])
        else:
            links.new(norm_tex_node.outputs['Color'], norm_map_node.inputs['Color'])
            
        links.new(norm_map_node.outputs['Normal'], bsdf_node.inputs['Normal'])
    
    # 3. Rugosidad / Metálico / ORM
    if hasattr(args, 'orm') and args.orm and os.path.exists(args.orm):
        orm_img = bpy.data.images.load(args.orm)
        orm_img.colorspace_settings.name = 'Non-Color'
        orm_node = nodes.new(type='ShaderNodeTexImage')
        orm_node.image = orm_img
        orm_node.location = (-600, -500)
        
        sep_orm = nodes.new(type='ShaderNodeSeparateColor')
        sep_orm.location = (-300, -500)
        links.new(orm_node.outputs['Color'], sep_orm.inputs['Color'])
        
        # Red = AO (ao_texture_channel = 0)
        # Green = Roughness (roughness_texture_channel = 1)
        links.new(sep_orm.outputs['Green'], bsdf_node.inputs['Roughness'])
        # Blue = Metallic (metallic_texture_channel = 2)
        links.new(sep_orm.outputs['Blue'], bsdf_node.inputs['Metallic'])
    else:
        if args.roughness and os.path.exists(args.roughness):
            rough_img = bpy.data.images.load(args.roughness)
            rough_img.colorspace_settings.name = 'Non-Color'
            rough_node = nodes.new(type='ShaderNodeTexImage')
            rough_node.image = rough_img
            rough_node.location = (-300, -500)
            links.new(rough_node.outputs['Color'], bsdf_node.inputs['Roughness'])
            
        if args.metallic and os.path.exists(args.metallic):
            metal_img = bpy.data.images.load(args.metallic)
            metal_img.colorspace_settings.name = 'Non-Color'
            metal_node = nodes.new(type='ShaderNodeTexImage')
            metal_node.image = metal_img
            metal_node.location = (-300, -700)
            links.new(metal_node.outputs['Color'], bsdf_node.inputs['Metallic'])
        
    # Configuraciones de renderizado de material
    if args.two_sided:
        mat.use_backface_culling = False
        
    if args.alpha_scissor is not None:
        if hasattr(mat, "blend_method"):
            mat.blend_method = 'CLIP'
            mat.alpha_threshold = args.alpha_scissor
            
    # Asignar a la malla
    if mesh_obj.data.materials:
        mesh_obj.data.materials[0] = mat
    else:
        mesh_obj.data.materials.append(mat)
    print(f"[+] Material PBR configurado para: {mesh_obj.name}")

def import_animations(armature, anim_paths):
    """Importa secuencias de animación en la armadura (compatible con Blender 5.0)."""
    if not armature or not anim_paths:
        return
        
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    
    for anim_file in anim_paths:
        anim_path = Path(anim_file)
        if not anim_path.exists():
            print(f"[!] Archivo de animación no encontrado: {anim_path}")
            continue
            
        ext = anim_path.suffix.lower()
        print(f"[*] Importando animación ({ext}): {anim_path.name}")
        
        if ext == ".psa":
            # Usar API interna del addon io_scene_psk_psa
            try:
                from io_scene_psk_psa.psa.importer import import_psa, PsaImportOptions
                from io_scene_psk_psa.psa.reader import PsaReader
                
                reader = PsaReader(str(anim_path))
                options = PsaImportOptions()
                options.should_use_fake_user = True
                
                # Importar todas las secuencias del archivo
                seq_names = list(reader.sequences.keys())
                options.sequence_names = seq_names
                import_psa(context=bpy.context, options=options)
                print(f"[+] Importadas {len(seq_names)} secuencias desde {anim_path.name}")
            except Exception as e:
                print(f"[!] Error importando PSA {anim_path.name}: {e}")
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=str(anim_path))

def export_model(output_path: Path, format_type: str):
    """Exporta la escena final al formato seleccionado."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_str = str(output_path.resolve())
    print(f"[*] Exportando modelo final ({format_type.upper()}) a: {out_str}")
    
    if format_type == "glb" or format_type == "gltf":
        bpy.ops.export_scene.gltf(
            filepath=out_str,
            export_format='GLB' if format_type == "glb" else 'GLTF_SEPARATE',
            export_animations=True,
            export_current_frame=False,
            export_skins=True,
            export_materials='EXPORT',
            export_image_format='AUTO',
            export_apply=True
        )
    elif format_type == "fbx":
        bpy.ops.export_scene.fbx(
            filepath=out_str,
            use_selection=False,
            add_leaf_bones=False,
            bake_anim=True
        )
    elif format_type == "usd":
        bpy.ops.wm.usd_export(filepath=out_str)
    else:
        raise ValueError(f"Formato de exportación no soportado: {format_type}")
    print(f"[✓] Proceso completado exitosamente: {out_str}")

def parse_args():
    # Obtener únicamente los argumentos pasados tras '--'
    if "--" in sys.argv:
        args_list = sys.argv[sys.argv.index("--") + 1:]
    else:
        args_list = []
        
    parser = argparse.ArgumentParser(description="Blender 5.0 Headless Asset Converter")
    parser.add_argument("--mesh", required=True, help="Ruta de la malla de entrada (.obj, .fbx, .psk, etc.)")
    parser.add_argument("--anims", nargs="+", help="Archivos de animación (.psa, .fbx, etc.)")
    parser.add_argument("--output", required=True, help="Archivo de destino (.glb, .fbx, etc.)")
    parser.add_argument("--name", help="Nombre del objeto base")
    parser.add_argument("--albedo", help="Textura Albedo/BaseColor")
    parser.add_argument("--normal", help="Textura Normal Map")
    parser.add_argument("--roughness", help="Textura Roughness/Mascara")
    parser.add_argument("--metallic", help="Textura Metallic")
    parser.add_argument("--orm", help="Textura ORM empaquetada (R=AO, G=Roughness, B=Metallic)")
    parser.add_argument("--normalize-pivot", action="store_true", help="Normaliza el pivote al centro de la base inferior (Z=min(Z) -> 0.0)")
    parser.add_argument("--apply-transforms", action="store_true", help="Aplica todas las transformaciones (rotación, escala, posición)")
    parser.add_argument("--sanitize-geometry", action="store_true", help="Elimina dobles vertices (0.1mm) y recalcula normales exteriores")
    parser.add_argument("--invert-normal-y", action="store_true", help="Invertir canal verde de Normal (DirectX a OpenGL)")
    parser.add_argument("--clean-vertex-colors", action="store_true", help="Eliminar capas de vertex colors")
    parser.add_argument("--two-sided", action="store_true", help="Desactivar backface culling (doble cara)")
    parser.add_argument("--alpha-scissor", type=float, default=None, help="Umbral de recorte alfa (Alpha Scissor)")
    parser.add_argument("--format", choices=["glb", "gltf", "fbx", "usd"], help="Formato de exportación")
    
    return parser.parse_args(args_list)

def main():
    args = parse_args()
    reset_scene()
    
    mesh_path = Path(args.mesh)
    if not mesh_path.exists():
        print(f"[!] Error: Archivo de malla no encontrado: {mesh_path}")
        sys.exit(1)
        
    output_path = Path(args.output)
    fmt = args.format
    if not fmt:
        fmt = output_path.suffix.lower().replace(".", "")
        if fmt not in ["glb", "gltf", "fbx", "usd"]:
            fmt = "glb"
            
    # 1. Importar malla
    import_mesh(mesh_path)
    armature, meshes = find_armature_and_meshes()
    
    # 2. Desinfección y normalización espacial
    if args.apply_transforms and meshes:
        apply_transforms(meshes, armature)
        
    if args.sanitize_geometry and meshes:
        sanitize_geometry(meshes)
        
    if args.normalize_pivot and meshes:
        normalize_pivot_to_base(meshes)
        if args.apply_transforms:
            apply_transforms(meshes, armature)

    # 3. Limpiar vertex colors si se solicita
    if args.clean_vertex_colors and meshes:
        clean_vertex_colors(meshes)
        
    # 4. Configurar materiales PBR
    for mesh_obj in meshes:
        setup_pbr_material(mesh_obj, args)
        
    # 5. Importar animaciones si existen
    if args.anims and armature:
        import_animations(armature, args.anims)
        
    # 6. Exportar
    export_model(output_path, fmt)

if __name__ == "__main__":
    main()
