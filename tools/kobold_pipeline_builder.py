#!/usr/bin/env python3
"""kobold_pipeline_builder.py - Blender 5.0 Headless Asset Converter & Porting Pipeline (v2.2)

Key Fixes:
1. Material & Shading:
   - Sets Emission Strength to 0.0 and Emission Color to (0,0,0) (completely removes the fluorescent white glow).
   - Keeps strictly ONE single detailed mesh ('Body'), unlinking BodyLod1, Icosphere, and all extra meshes.
   - Restores authentic PBR material: BaseMap (sRGB), NormalMap (Non-Color), and MaskMap.
   - Calibrates eye cornea with glossy finish and zero emission.
2. Animation Retargeting & Scaling:
   - Preserves FBX import scales so Mixamo centimeters match Kobold meters (Z=0.93m hips).
   - Visual World Constraints (Copy Location for Hips, Copy Rotation for all body & finger bones).
   - Bakes clean, native F-curves directly onto Kobold_Rig for all actions.
   - Cleans up all temporary objects and foreign actions before glTF export.
"""

import os
import sys
from pathlib import Path


def run_pipeline(model_fbx: str, textures_dir: str, anims_dir: str, output_glb: str):
    import bpy

    print("=" * 70)
    print("STARTING BLENDER 5.0 KOBOLD PIPELINE (v2.2 - SCALE & VISUAL RETARGET FIX)")
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
    kobold_armature.location = (0, 0, 0)
    kobold_armature.rotation_euler = (0, 0, 0)

    print(f"  Found Armature: '{kobold_armature.name}' with {len(kobold_armature.data.bones)} bones.")

    # Remove all meshes except primary detailed 'Body'
    for obj in list(bpy.data.objects):
        if obj.type == "MESH" and obj.name != "Body":
            print(f"  Removing extra/duplicate mesh: {obj.name}")
            bpy.data.objects.remove(obj, do_unlink=True)

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

        # Crucial fix: zero emission
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

    # 4. Universal Visual World Constraint Retargeting
    print("\n[STEP 3/5] Importing & visual retargeting animations...")

    anims_path = Path(anims_dir)
    parent_anims_path = anims_path.parent

    # Base bone mapping table (Mixamo -> Kobold)
    HUMANOID_MAP = {
        "mixamorig:Hips": ("Hips", True), # Copy location + rotation in world space
        "mixamorig:Spine": ("Spine", False),
        "mixamorig:Spine1": ("Chest", False),
        "mixamorig:Neck": ("Neck", False),
        "mixamorig:Head": ("Head", False),
        "mixamorig:LeftShoulder": ("Shoulder.L", False),
        "mixamorig:LeftArm": ("Arm.L", False),
        "mixamorig:LeftForeArm": ("ForeArm.L", False),
        "mixamorig:LeftHand": ("Hand.L", False),
        "mixamorig:RightShoulder": ("Shoulder.R", False),
        "mixamorig:RightArm": ("Arm.R", False),
        "mixamorig:RightForeArm": ("ForeArm.R", False),
        "mixamorig:RightHand": ("Hand.R", False),
        "mixamorig:LeftUpLeg": ("UpLeg.L", False),
        "mixamorig:LeftLeg": ("Leg.L", False),
        "mixamorig:LeftFoot": ("Foot.L", False),
        "mixamorig:RightUpLeg": ("UpLeg.R", False),
        "mixamorig:RightLeg": ("Leg.R", False),
        "mixamorig:RightFoot": ("Foot.R", False),
        # Left Fingers
        "mixamorig:LeftHandThumb1": ("HandThumb1.L", False),
        "mixamorig:LeftHandThumb2": ("HandThumb2.L", False),
        "mixamorig:LeftHandThumb3": ("HandThumb3.L", False),
        "mixamorig:LeftHandIndex1": ("HandIndex1.L", False),
        "mixamorig:LeftHandIndex2": ("HandIndex2.L", False),
        "mixamorig:LeftHandIndex3": ("HandIndex3.L", False),
        "mixamorig:LeftHandMiddle1": ("HandMiddle1.L", False),
        "mixamorig:LeftHandMiddle2": ("HandMiddle2.L", False),
        "mixamorig:LeftHandMiddle3": ("HandMiddle3.L", False),
        "mixamorig:LeftHandRing1": ("HandRing1.L", False),
        "mixamorig:LeftHandRing2": ("HandRing2.L", False),
        "mixamorig:LeftHandRing3": ("HandRing3.L", False),
        "mixamorig:LeftHandPinky1": ("HandPinky1.L", False),
        "mixamorig:LeftHandPinky2": ("HandPinky2.L", False),
        "mixamorig:LeftHandPinky3": ("HandPinky3.L", False),
        # Right Fingers
        "mixamorig:RightHandThumb1": ("HandThumb1.R", False),
        "mixamorig:RightHandThumb2": ("HandThumb2.R", False),
        "mixamorig:RightHandThumb3": ("HandThumb3.R", False),
        "mixamorig:RightHandIndex1": ("HandIndex1.R", False),
        "mixamorig:RightHandIndex2": ("HandIndex2.R", False),
        "mixamorig:RightHandIndex3": ("HandIndex3.R", False),
        "mixamorig:RightHandMiddle1": ("HandMiddle1.R", False),
        "mixamorig:RightHandMiddle2": ("HandMiddle2.R", False),
        "mixamorig:RightHandMiddle3": ("HandMiddle3.R", False),
        "mixamorig:RightHandRing1": ("HandRing1.R", False),
        "mixamorig:RightHandRing2": ("HandRing2.R", False),
        "mixamorig:RightHandRing3": ("HandRing3.R", False),
        "mixamorig:RightHandPinky1": ("HandPinky1.R", False),
        "mixamorig:RightHandPinky2": ("HandPinky2.R", False),
        "mixamorig:RightHandPinky3": ("HandPinky3.R", False),
    }

    anim_list = [
        ("Idle", "Standing Idle (1).fbx"),
        ("Happy", "Happy.fbx"),
        ("Bashful", "Bashful.fbx"),
        ("Run", "Running.fbx"),
        ("Walk", "Walking.fbx"),
        ("Strafe_L", "Left Strafe Walk.fbx"),
        ("Strafe_R", "Right Strafe Walk.fbx"),
    ]

    if not kobold_armature.animation_data:
        kobold_armature.animation_data_create()

    baked_actions = []

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
            continue

        # Position source at origin, PRESERVING imported scale (0.01 for Mixamo)
        source_arm.location = (0, 0, 0)
        source_arm.rotation_euler = (0, 0, 0)

        # Build pair mapping for this armature
        pairs = []
        for mix_name, (kob_name, copy_loc) in HUMANOID_MAP.items():
            if mix_name in source_arm.pose.bones and kob_name in kobold_armature.pose.bones:
                pairs.append((mix_name, kob_name, copy_loc))

        # Also map identical bone names directly (e.g. Tail, Tail.1, Breast.L)
        for b in source_arm.pose.bones:
            if b.name in kobold_armature.pose.bones and not b.name.startswith("mixamorig:"):
                if b.name != "Hips":
                    pairs.append((b.name, b.name, False))

        # Add visual constraints
        for src_bone, tgt_bone, copy_loc in pairs:
            pb = kobold_armature.pose.bones.get(tgt_bone)
            if not pb:
                continue

            if copy_loc:
                c_loc = pb.constraints.new('COPY_LOCATION')
                c_loc.target = source_arm
                c_loc.subtarget = src_bone
                c_loc.target_space = 'WORLD'
                c_loc.owner_space = 'WORLD'

            c_rot = pb.constraints.new('COPY_ROTATION')
            c_rot.target = source_arm
            c_rot.subtarget = src_bone
            c_rot.target_space = 'WORLD'
            c_rot.owner_space = 'WORLD'

        # Bake action onto Kobold rig
        f_start = int(source_act.frame_range[0])
        f_end = int(source_act.frame_range[1])

        bpy.context.view_layer.objects.active = kobold_armature
        bpy.ops.object.select_all(action='DESELECT')
        kobold_armature.select_set(True)

        bpy.ops.nla.bake(
            frame_start=f_start,
            frame_end=f_end,
            only_selected=False,
            visual_keying=True,
            clear_constraints=True,
            bake_types={'POSE'}
        )

        baked_act = kobold_armature.animation_data.action
        baked_act.name = f"Kobold_{clip_name}"

        # Push baked action to dedicated NLA track
        nla_track = kobold_armature.animation_data.nla_tracks.new()
        nla_track.name = baked_act.name
        nla_track.strips.new(baked_act.name, f_start, baked_act)
        baked_actions.append(baked_act)

        print(f"  [OK] Retargeted '{baked_act.name}' ({f_start}-{f_end} frames) successfully baked.")

        # Cleanup imported source objects & actions
        for obj in new_objects:
            if obj != kobold_armature:
                bpy.data.objects.remove(obj, do_unlink=True)
        for a in new_actions:
            if a != baked_act:
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

    print(f"\n[STEP 5/5] Export complete: {output_glb}")
    file_size_mb = Path(output_glb).stat().st_size / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Total actions embedded: {len(baked_actions)}")
    print("=" * 70)


if __name__ == "__main__":
    import sys

    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
        if len(args) >= 4:
            run_pipeline(args[0], args[1], args[2], args[3])
        else:
            print("Usage: blender -b -P kobold_pipeline_builder.py -- <model_fbx> <textures_dir> <anims_dir> <output_glb>")
    else:
        model_fbx = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Models\Kobold.fbx"
        textures_dir = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Textures"
        anims_dir = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Animations\AnimationIK"
        output_glb = r"C:\Users\cesar\Desktop\skill\export\kobold_godot_ready.glb"
        run_pipeline(model_fbx, textures_dir, anims_dir, output_glb)
