#!/usr/bin/env python3
"""kobold_pipeline_builder.py - Blender 5.0 Headless Asset Converter & Porting Pipeline

Ports KoboldKare character model and skeletal animations into Godot 4.6-ready GLB:
1. Imports Kobold.fbx (70-bone rig + Body mesh).
2. Re-links and configures Principled BSDF PBR materials (BaseMap, Normal, MaskMap).
3. Imports multiple FBX animations (Idle, Walk, Run, Strafe, Thrust).
4. Retargets Mixamo bone names to Kobold rig convention.
5. In Blender 5.0 (Animation 2025), pushes retargeted actions to NLA tracks.
6. Exports an optimized, self-contained .glb for Godot 4.6.
"""

import os
import sys
from pathlib import Path

# Bone mapping dictionary from standard Mixamo to Kobold humanoid rig
BONE_MAP = {
    "mixamorig:Hips": "Hips",
    "mixamorig:Spine": "Spine",
    "mixamorig:Spine1": "Chest",
    "mixamorig:Spine2": "Chest",
    "mixamorig:Neck": "Neck",
    "mixamorig:Head": "Head",
    "mixamorig:LeftEye": "Eye.L",
    "mixamorig:RightEye": "Eye.R",
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
    # Left Fingers
    "mixamorig:LeftHandThumb1": "HandThumb1.L",
    "mixamorig:LeftHandThumb2": "HandThumb2.L",
    "mixamorig:LeftHandThumb3": "HandThumb3.L",
    "mixamorig:LeftHandIndex1": "HandIndex1.L",
    "mixamorig:LeftHandIndex2": "HandIndex2.L",
    "mixamorig:LeftHandIndex3": "HandIndex3.L",
    "mixamorig:LeftHandMiddle1": "HandMiddle1.L",
    "mixamorig:LeftHandMiddle2": "HandMiddle2.L",
    "mixamorig:LeftHandMiddle3": "HandMiddle3.L",
    "mixamorig:LeftHandRing1": "HandRing1.L",
    "mixamorig:LeftHandRing2": "HandRing2.L",
    "mixamorig:LeftHandRing3": "HandRing3.L",
    "mixamorig:LeftHandPinky1": "HandPinky1.L",
    "mixamorig:LeftHandPinky2": "HandPinky2.L",
    "mixamorig:LeftHandPinky3": "HandPinky3.L",
    # Right Fingers
    "mixamorig:RightHandThumb1": "HandThumb1.R",
    "mixamorig:RightHandThumb2": "HandThumb2.R",
    "mixamorig:RightHandThumb3": "HandThumb3.R",
    "mixamorig:RightHandIndex1": "HandIndex1.R",
    "mixamorig:RightHandIndex2": "HandIndex2.R",
    "mixamorig:RightHandIndex3": "HandIndex3.R",
    "mixamorig:RightHandMiddle1": "HandMiddle1.R",
    "mixamorig:RightHandMiddle2": "HandMiddle2.R",
    "mixamorig:RightHandMiddle3": "HandMiddle3.R",
    "mixamorig:RightHandRing1": "HandRing1.R",
    "mixamorig:RightHandRing2": "HandRing2.R",
    "mixamorig:RightHandRing3": "HandRing3.R",
    "mixamorig:RightHandPinky1": "HandPinky1.R",
    "mixamorig:RightHandPinky2": "HandPinky2.R",
    "mixamorig:RightHandPinky3": "HandPinky3.R",
}


def run_pipeline(model_fbx: str, textures_dir: str, anims_dir: str, output_glb: str):
    import bpy

    print("=" * 70)
    print("STARTING BLENDER 5.0 KOBOLD PIPELINE")
    print(f"Model FBX:     {model_fbx}")
    print(f"Textures Dir:  {textures_dir}")
    print(f"Anims Dir:     {anims_dir}")
    print(f"Output GLB:    {output_glb}")
    print("=" * 70)

    # 1. Reset scene to empty
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Import Kobold.fbx
    print("\n[STEP 1/5] Importing Kobold base character model...")
    bpy.ops.import_scene.fbx(filepath=model_fbx)

    kobold_armature = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
    if not kobold_armature:
        raise RuntimeError("No armature found in base model FBX!")

    kobold_armature.name = "Kobold_Rig"
    print(f"  Found Armature: '{kobold_armature.name}' with {len(kobold_armature.data.bones)} bones.")

    # 3. Configure Materials & Re-link Textures
    print("\n[STEP 2/5] Setting up PBR Materials with local textures...")
    tex_path = Path(textures_dir)

    def load_img(filename: str):
        full_p = tex_path / filename
        if full_p.is_file():
            img = bpy.data.images.load(str(full_p))
            return img
        print(f"  [WARN] Texture file not found: {full_p}")
        return None

    # Configure KoboldBody Material
    mat_body = bpy.data.materials.get("KoboldBody")
    if mat_body:
        nodes = mat_body.node_tree.nodes
        links = mat_body.node_tree.links
        bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)

        img_base = load_img("Kobold_low_KoboldBody_BaseMap.png")
        img_norm = load_img("Kobold_low_KoboldBody_Normal.png")
        img_mask = load_img("Kobold_low_KoboldBody_MaskMap.png")

        if bsdf:
            if img_base:
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
                # Red = Metallic, Green = Roughness in Unity MaskMap
                links.new(node_sep.outputs["Red"], bsdf.inputs["Metallic"])
                links.new(node_sep.outputs["Green"], bsdf.inputs["Roughness"])

        print("  Configured KoboldBody Principled BSDF PBR.")

    # Configure KoboldEyes Material
    mat_eyes = bpy.data.materials.get("KoboldEyes")
    if mat_eyes:
        nodes = mat_eyes.node_tree.nodes
        links = mat_eyes.node_tree.links
        bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)

        img_eye_diff = load_img("KoboldEye_Diffuse.png")
        img_eye_norm = load_img("KoboldEye_OpenGLNormal.png")

        if bsdf:
            if img_eye_diff:
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

        print("  Configured KoboldEyes Principled BSDF.")

    # 4. Import & Retarget Animations
    print("\n[STEP 3/5] Importing and retargeting skeletal animations...")
    anim_files = {
        "Idle": "Standing Idle (1).fbx",
        "Idle_B": "Standing Idle (2).fbx",
        "Walk": "Walking.fbx",
        "Run": "Running.fbx",
        "Strafe_L": "Left Strafe.fbx",
        "Strafe_R": "Right Strafe.fbx",
        "Thrust": "thrustanimations.fbx",
    }

    anims_path = Path(anims_dir)
    parent_anims_path = anims_path.parent
    retargeted_actions = []

    if not kobold_armature.animation_data:
        kobold_armature.animation_data_create()

    for clip_name, fbx_file in anim_files.items():
        fbx_full = anims_path / fbx_file
        if not fbx_full.is_file():
            fbx_full = parent_anims_path / fbx_file
        if not fbx_full.is_file():
            print(f"  [WARN] Animation file {fbx_file} not found; skipping.")
            continue

        existing_actions = set(bpy.data.actions)
        existing_objects = set(bpy.data.objects)

        bpy.ops.import_scene.fbx(filepath=str(fbx_full))

        new_actions = list(set(bpy.data.actions) - existing_actions)
        new_objects = list(set(bpy.data.objects) - existing_objects)

        if not new_actions:
            print(f"  [WARN] No action generated for {clip_name}")
            continue

        act = new_actions[0]
        act.name = f"Kobold_{clip_name}"

        # Retarget Fcurves: rename bone paths in Blender 5.0 channelbags
        remapped_curves = 0
        if hasattr(act, "layers") and act.layers:
            for layer in act.layers:
                for strip in layer.strips:
                    if hasattr(strip, "channelbags"):
                        for cb in strip.channelbags:
                            for fc in cb.fcurves:
                                for mixamo_name, kobold_name in BONE_MAP.items():
                                    if f'"{mixamo_name}"' in fc.data_path:
                                        fc.data_path = fc.data_path.replace(f'"{mixamo_name}"', f'"{kobold_name}"')
                                        remapped_curves += 1
                                        break
        elif hasattr(act, "fcurves"):
            for fc in act.fcurves:
                for mixamo_name, kobold_name in BONE_MAP.items():
                    if f'"{mixamo_name}"' in fc.data_path:
                        fc.data_path = fc.data_path.replace(f'"{mixamo_name}"', f'"{kobold_name}"')
                        remapped_curves += 1
                        break

        print(f"  [OK] Animation '{act.name}' imported ({remapped_curves} bone curves remapped to Kobold rig).")

        # Push to NLA Track on Kobold Armature so glTF exporter embeds all actions
        nla_track = kobold_armature.animation_data.nla_tracks.new()
        nla_track.name = act.name
        nla_track.strips.new(act.name, int(act.frame_range[0]), act)

        retargeted_actions.append(act)

        # Delete the temporary imported dummy armature from the anim FBX
        for obj in new_objects:
            if obj != kobold_armature:
                bpy.data.objects.remove(obj, do_unlink=True)

    # 5. Export to GLB
    print(f"\n[STEP 4/5] Exporting Godot 4.6-compatible GLB: {output_glb}...")
    out_dir = Path(output_glb).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # In Blender 5.0, select KoboldArmature and its children meshes
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
        export_vertex_color="NONE",  # Clear clown vertex colors
        export_yup=True,
    )

    print(f"\n[STEP 5/5] Export complete: {output_glb}")
    file_size_mb = Path(output_glb).stat().st_size / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
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
        # Default paths
        model_fbx = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Models\Kobold.fbx"
        textures_dir = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Textures"
        anims_dir = r"C:\Users\cesar\Downloads\KoboldKare-master\KoboldKare-master\Assets\KoboldKare\Animations\AnimationIK"
        output_glb = r"C:\Users\cesar\Desktop\skill\export\kobold_godot_ready.glb"
        run_pipeline(model_fbx, textures_dir, anims_dir, output_glb)
