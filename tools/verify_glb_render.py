import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

# Import fresh exported GLB
glb_path = r"C:\Users\cesar\Desktop\skill\export\kobold_godot_ready.glb"
bpy.ops.import_scene.gltf(filepath=glb_path)

arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
mesh = next((o for o in bpy.data.objects if o.type == 'MESH'), None)

print("Imported GLB objects:")
for o in bpy.data.objects:
    print(f"  {o.name} ({o.type})")

# Check materials
for mat in bpy.data.materials:
    print(f"Material: {mat.name}")
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        print(f"  Emission Color: {list(bsdf.inputs['Emission Color'].default_value)}")
        if 'Emission Strength' in bsdf.inputs:
            print(f"  Emission Strength: {bsdf.inputs['Emission Strength'].default_value}")
        print(f"  Base Color linked? {bsdf.inputs['Base Color'].is_linked}")

# Set animation to Kobold_Run, frame 10 (mid-stride)
print("\nActions in GLB:")
for act in bpy.data.actions:
    print(f"  {act.name}")

act_run = next((a for a in bpy.data.actions if "run" in a.name.lower()), None)
if act_run and arm:
    arm.animation_data.action = act_run
    bpy.context.scene.frame_set(10)
    bpy.context.view_layer.update()
    
    # Check bone locations
    print("\nBone locations at frame 10 of Kobold_Run:")
    for bname in ["Hips", "Arm.L", "Hand.L", "Arm.R", "Hand.R", "Foot.L", "Foot.R"]:
        pb = arm.pose.bones.get(bname)
        if pb:
            world_pos = arm.matrix_world @ pb.head
            print(f"  {bname:8s} -> X={world_pos.x:.2f}, Y={world_pos.y:.2f}, Z={world_pos.z:.2f}")

# Render to verify visual look
cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0, -2.8, 1.0)
cam_obj.rotation_euler = (1.5, 0, 0)
bpy.context.scene.camera = cam_obj

light_data = bpy.data.lights.new("Sun", type='SUN')
light_data.energy = 3.5
light_obj = bpy.data.objects.new("Sun", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (2, -3, 4)

bpy.context.scene.render.resolution_x = 720
bpy.context.scene.render.resolution_y = 720
out_img = r"C:\Users\cesar\Desktop\skill\export\verified_kobold_run.png"
bpy.context.scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"\nRendered verified image to: {out_img}")
