#!/usr/bin/env python3
"""
kobold_pipeline_builder.py - Blender 5.0 Headless Asset Converter & Porting Pipeline (v3.1 - MATHEMATICAL RELATIVE OFFSET RETARGETING & UPRIGHT NORMALIZATION)

Core Features:
1. PBR Materials & Shading:
   - Unlinks all LODs and temporary clutter (keeps strictly the primary high-res 'Body').
   - Calibrates BaseMap (sRGB), NormalMap (Non-Color), and MaskMap (Metallic/Roughness).
   - Enforces Emission Strength = 0.0 and Emission Color = (0,0,0) on all BSDF nodes.
2. Upright Transform Synchronization:
   - Synchronizes FBX coordinate system transforms so Kobold character stands perfectly upright (Z=1.42m height).
   - Applies rotation and scale to base armature and mesh simultaneously.
3. Mathematical Relative Offset Retargeting (Anti-Candy-Wrapper):
   - Mathematically absorbs rest pose differences (bone roll, local axis variations) using:
       R_offset = S_rest_rot^-1 @ T_rest_rot
       T_world_rot(t) = S_world_rot(t) @ R_offset
   - Completely eliminates candy-wrapper limb pinching, arm twisting, and joint collapse.
   - Bakes clean, direct quaternions onto Kobold rig in hierarchical order.
   - Preserves Hips translation (scaled appropriately from centimeter to meter space).
4. Godot 4.6 Compatible Export:
   - Pushes all baked actions to separate NLA tracks.
   - Exports GLB with full bone deform weights, animations, and PBR textures.
"""

import os
import sys
from pathlib import Path


def run_pipeline(model_fbx: str, textures_dir: str, anims_dir: str, output_glb: str):
    import bpy
    from mathutils import Matrix, Quaternion, Vector

    print("=" * 70)
    print("STARTING BLENDER 5.0 KOBOLD PIPELINE (v3.1 - RELATIVE OFFSET & UPRIGHT)")
    print(f"Model FBX:     {model_fbx}")
    print(f"Textures Dir:  {textures_dir}")
    print(f"Anims Dir:     {anims_dir}")
    print(f"Output GLB:    {output_glb}")
    print("=" * 70)

    # 1. Reset scene to empty
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Import Kobold base model
    print("\n[STEP 1/5] Importing Kobold base character model...")
    bpy.ops.import_scene.fbx(filepath=model_fbx)

    kobold_armature = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
    if not kobold_armature:
        raise RuntimeError("No armature found in base model FBX!")

    kobold_armature.name = "Kobold_Rig"

    # Remove all meshes except primary detailed 'Body'
    for obj in list(bpy.data.objects):
        if obj.type == "MESH" and obj.name != "Body":
            print(f"  Removing extra/duplicate mesh: {obj.name}")
            bpy.data.objects.remove(obj, do_unlink=True)

    # Normalize transforms and freeze in upright standing pose
    body_mesh = bpy.data.objects.get("Body")
    bpy.ops.object.select_all(action="DESELECT")
    kobold_armature.select_set(True)
    if body_mesh:
        body_mesh.select_set(True)
    bpy.context.view_layer.objects.active = kobold_armature
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    print(f"  Found Armature: '{kobold_armature.name}' with {len(kobold_armature.data.bones)} bones.")

    # 3. Configure Materials & Re-link Textures (No Emission Blowout)
    print("\n[STEP 2/5] Setting up PBR Materials with local textures (No Emission Blowout)...")
    tex_path = Path(textures_dir)

    def load_img(filename: str):
        full_p = tex_path / filename
        if full_p.is_file():
            img = bpy.data.images.load(str(full_p))
            return img
        print(f"  [WARN] Texture file not found: {full_p}")
        return None

    # KoboldBody Material
    mat_body = bpy.data.materials.get("KoboldBody")
    if mat_body and mat_body.node_tree:
        nodes = mat_body.node_tree.nodes
        links = mat_body.node_tree.links
        nodes.clear()

        node_out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.0

        bsdf.inputs["Specular IOR Level"].default_value = 0.5
        bsdf.inputs["Roughness"].default_value = 0.65
        bsdf.inputs["Metallic"].default_value = 0.0

        img_base = load_img("Kobold_low_KoboldBody_BaseMap.png")
        img_norm = load_img("Kobold_low_KoboldBody_Normal.png")
        img_mask = load_img("Kobold_low_KoboldBody_MaskMap.png")

        if img_base:
            img_base.colorspace_settings.name = "sRGB"
            node_base = nodes.new("ShaderNodeTexImage")
            node_base.image = img_base
            links.new(node_base.outputs["Color"], bsdf.inputs["Base Color"])

        if img_norm:
            img_norm.colorspace_settings.name = "Non-Color"
            node_norm = nodes.new("ShaderNodeTexImage")
            node_norm.image = img_norm
            node_normal_map = nodes.new("ShaderNodeNormalMap")
            links.new(node_norm.outputs["Color"], node_normal_map.inputs["Color"])
            links.new(node_normal_map.outputs["Normal"], bsdf.inputs["Normal"])

        if img_mask:
            img_mask.colorspace_settings.name = "Non-Color"
            node_mask = nodes.new("ShaderNodeTexImage")
            node_mask.image = img_mask
            node_sep = nodes.new("ShaderNodeSeparateColor")
            links.new(node_mask.outputs["Color"], node_sep.inputs["Color"])
            links.new(node_sep.outputs["Red"], bsdf.inputs["Metallic"])
            links.new(node_sep.outputs["Green"], bsdf.inputs["Roughness"])

        print("  Configured KoboldBody Material (Clean PBR, zero emission).")

    # KoboldEyes Material
    mat_eyes = bpy.data.materials.get("KoboldEyes")
    if mat_eyes and mat_eyes.node_tree:
        nodes = mat_eyes.node_tree.nodes
        links = mat_eyes.node_tree.links
        nodes.clear()

        node_out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.0

        bsdf.inputs["Roughness"].default_value = 0.08
        bsdf.inputs["Metallic"].default_value = 0.0

        img_eye_diff = load_img("KoboldEye_Diffuse.png")
        img_eye_norm = load_img("KoboldEye_OpenGLNormal.png")

        if img_eye_diff:
            img_eye_diff.colorspace_settings.name = "sRGB"
            node_eye_diff = nodes.new("ShaderNodeTexImage")
            node_eye_diff.image = img_eye_diff
            links.new(node_eye_diff.outputs["Color"], bsdf.inputs["Base Color"])

        if img_eye_norm:
            img_eye_norm.colorspace_settings.name = "Non-Color"
            node_eye_norm = nodes.new("ShaderNodeTexImage")
            node_eye_norm.image = img_eye_norm
            node_eye_map = nodes.new("ShaderNodeNormalMap")
            links.new(node_eye_norm.outputs["Color"], node_eye_map.inputs["Color"])
            links.new(node_eye_map.outputs["Normal"], bsdf.inputs["Normal"])

        print("  Configured KoboldEyes Material (Glossy cornea, zero emission).")

    # 4. Mathematical Relative Offset Retargeting
    print("\n[STEP 3/5] Importing & mathematical retargeting animations...")

    HUMANOID_MAP = {
        "mixamorig:Hips": "Hips",
        "mixamorig:Spine": "Spine",
        "mixamorig:Spine1": "Chest",
        "mixamorig:Neck": "Neck",
        "mixamorig:Head": "Head",
        "mixamorig:LeftShoulder": "Shoulder.L",
        "mixamorig:LeftArm": "Arm.L",
        "mixamorig:LeftForeArm": "ForeArm.L",
        "mixamorig:LeftHand": "Hand.L",
        "mixamorig:RightShoulder": "Shoulder.R",
        "mixamorig:RightArm": "Arm.R",
        "mixamorig:RightForeArm": "ForeArm.R",
        "mixamorig:RightHand": "Hand.R",
        "mixamorig:LeftUpLeg": "UpLeg.L",
        "mixamorig:LeftLeg": "Leg.L",
        "mixamorig:LeftFoot": "Foot.L",
        "mixamorig:RightUpLeg": "UpLeg.R",
        "mixamorig:RightLeg": "Leg.R",
        "mixamorig:RightFoot": "Foot.R",
    }

    # Add all finger mappings
    for side, s_code in [("Left", "L"), ("Right", "R")]:
        for digit in ["Thumb", "Index", "Middle", "Ring", "Pinky"]:
            for seg in [1, 2, 3]:
                HUMANOID_MAP[f"mixamorig:{side}Hand{digit}{seg}"] = f"Hand{digit}{seg}.{s_code}"

    anim_list = [
        ("Idle", "Standing Idle (1).fbx"),
        ("Happy", "Happy.fbx"),
        ("Bashful", "Bashful.fbx"),
        ("Run", "Running.fbx"),
        ("Walk", "Walking.fbx"),
        ("Strafe_L", "Left Strafe Walk.fbx"),
        ("Strafe_R", "Right Strafe Walk.fbx"),
        ("Fall", "FallingUpright.fbx"),
    ]

    def get_bone_depth(b):
        d = 0
        while b.parent:
            d += 1
            b = b.parent
        return d

    if not kobold_armature.animation_data:
        kobold_armature.animation_data_create()

    anims_path = Path(anims_dir)
    parent_anims_path = anims_path.parent

    for clip_name, fbx_file in anim_list:
        fbx_full = anims_path / fbx_file
        if not fbx_full.is_file():
            fbx_full = parent_anims_path / fbx_file
        if not fbx_full.is_file():
            print(f"  [WARN] File {fbx_file} not found; skipping.")
            continue

        existing_actions = set(bpy.data.actions)
        existing_objects = set(bpy.data.objects)

        bpy.ops.import_scene.fbx(filepath=str(fbx_full))

        new_actions = list(set(bpy.data.actions) - existing_actions)
        new_objects = list(set(bpy.data.objects) - existing_objects)

        if not new_actions:
            print(f"  [WARN] No action imported for {clip_name}")
            continue

        source_act = new_actions[0]
        source_arm = next((o for o in new_objects if o.type == 'ARMATURE'), None)

        if not source_arm:
            for o in new_objects:
                bpy.data.objects.remove(o, do_unlink=True)
            for a in new_actions:
                bpy.data.actions.remove(a, do_unlink=True)
            continue

        # Synchronize source transform
        bpy.ops.object.select_all(action='DESELECT')
        source_arm.select_set(True)
        bpy.context.view_layer.objects.active = source_arm
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        f_start = int(source_act.frame_range[0])
        f_end = int(source_act.frame_range[1])

        # Step A: Precompute R_offset in rest pose
        kobold_armature.data.pose_position = 'REST'
        source_arm.data.pose_position = 'REST'
        bpy.context.view_layer.update()

        r_offset = {}
        is_mixamo = any('mixamorig' in b.name for b in source_arm.data.bones)

        if is_mixamo:
            for src_name, tgt_name in HUMANOID_MAP.items():
                src_pb = source_arm.pose.bones.get(src_name)
                tgt_pb = kobold_armature.pose.bones.get(tgt_name)
                if src_pb and tgt_pb:
                    S_rest_rot = (source_arm.matrix_world @ src_pb.matrix).to_3x3()
                    T_rest_rot = (kobold_armature.matrix_world @ tgt_pb.matrix).to_3x3()
                    offset = S_rest_rot.inverted() @ T_rest_rot
                    r_offset[src_name] = (tgt_name, offset)
        else:
            for b in source_arm.data.bones:
                if b.name in kobold_armature.data.bones:
                    src_pb = source_arm.pose.bones.get(b.name)
                    tgt_pb = kobold_armature.pose.bones.get(b.name)
                    if src_pb and tgt_pb:
                        S_rest_rot = (source_arm.matrix_world @ src_pb.matrix).to_3x3()
                        T_rest_rot = (kobold_armature.matrix_world @ tgt_pb.matrix).to_3x3()
                        offset = S_rest_rot.inverted() @ T_rest_rot
                        r_offset[b.name] = (b.name, offset)

        # Step B: Return to pose mode
        kobold_armature.data.pose_position = 'POSE'
        source_arm.data.pose_position = 'POSE'
        bpy.context.view_layer.update()

        # Sort pairs from root to leaves (parents before children)
        sorted_pairs = sorted(
            r_offset.items(),
            key=lambda item: get_bone_depth(kobold_armature.data.bones[item[1][0]])
        )

        target_act = bpy.data.actions.new(name=f"Kobold_{clip_name}")
        kobold_armature.animation_data.action = target_act

        print(f"  Baking '{target_act.name}' ({f_start}-{f_end} frames, {len(sorted_pairs)} bones mapped)...")

        # Step C: Frame-by-frame retargeting & keyframing
        for f in range(f_start, f_end + 1):
            bpy.context.scene.frame_set(f)
            bpy.context.view_layer.update()

            for src_name, (tgt_name, offset) in sorted_pairs:
                src_pb = source_arm.pose.bones[src_name]
                tgt_pb = kobold_armature.pose.bones[tgt_name]

                S_rot = (source_arm.matrix_world @ src_pb.matrix).to_3x3()
                T_rot = S_rot @ offset

                curr_pos = (kobold_armature.matrix_world @ tgt_pb.matrix).to_translation()
                if tgt_name == "Hips":
                    src_pos = (source_arm.matrix_world @ src_pb.matrix).to_translation()
                    # Centimeter to meter scaling for Mixamo
                    scale = 0.01 if is_mixamo and (src_pos.z > 10.0 or abs(src_pos.y) > 10.0) else 1.0
                    curr_pos = Vector((src_pos.x * scale, src_pos.y * scale, src_pos.z * scale))

                T_world_mat = Matrix.Translation(curr_pos) @ T_rot.to_4x4()
                tgt_pb.matrix = kobold_armature.matrix_world.inverted() @ T_world_mat

                if tgt_name == "Hips":
                    tgt_pb.keyframe_insert(data_path="location", frame=f)
                tgt_pb.keyframe_insert(data_path="rotation_quaternion", frame=f)

            bpy.context.view_layer.update()

        # Step D: Push to NLA track
        track = kobold_armature.animation_data.nla_tracks.new()
        track.name = target_act.name
        track.strips.new(target_act.name, f_start, target_act)
        kobold_armature.animation_data.action = None
        print(f"  [OK] Retargeted '{target_act.name}' successfully baked.")

        # Cleanup source objects & actions
        for o in new_objects:
            bpy.data.objects.remove(o, do_unlink=True)
        for a in new_actions:
            bpy.data.actions.remove(a, do_unlink=True)

    # 5. Export to GLB
    print(f"\n[STEP 4/5] Exporting Godot 4.6-compatible GLB: {output_glb}...")
    out_dir = Path(output_glb).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="DESELECT")
    kobold_armature.select_set(True)
    bpy.context.view_layer.objects.active = kobold_armature
    for child in kobold_armature.children:
        child.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=str(output_glb),
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_nla_strips=True,
        export_def_bones=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
        export_vertex_color="NONE",
        export_yup=True,
    )

    print(f"\n[STEP 5/5] GLB Export Successful! File saved at: {output_glb}")
    print(f"File Size: {os.path.getsize(output_glb) / (1024*1024):.2f} MB")
    print("=" * 70)


if __name__ == "__main__":
    KOBOLD_FBX = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Models\Kobold.fbx"
    TEXTURES_DIR = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Textures"
    ANIMS_DIR = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Animations\AnimationIK"
    OUTPUT_GLB = r"C:\Users\cesar\Desktop\skill\export\kobold_godot_ready.glb"

    run_pipeline(KOBOLD_FBX, TEXTURES_DIR, ANIMS_DIR, OUTPUT_GLB)
