import bpy

print("\n--- Inspecting ASSET_CAMERA.blend ---")

# List all objects to find the camera
print(f"Objects in file: {[obj.name for obj in bpy.data.objects]}")

camera_obj = bpy.data.objects.get("ASSET_CAMERA")
if not camera_obj:
    # Fallback: check for any camera object
    cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
    if cameras:
        camera_obj = cameras[0]
        print(f"ASSET_CAMERA not found by name, using first found camera: {camera_obj.name}")
    else:
        print("CRITICAL: No camera object found in ASSET_CAMERA.blend")
        exit(1)

print(f"Target Camera Object: {camera_obj.name}")
print(f"Type: {camera_obj.type}")

if camera_obj.type == 'CAMERA':
    cam_data = camera_obj.data
    print(f"Camera Data Name: {cam_data.name}")
    
    # Check for show_safe_areas
    if hasattr(cam_data, 'show_safe_areas'):
        print(f"Has 'show_safe_areas': {cam_data.show_safe_areas}")
    else:
        print("Has 'show_safe_areas': False")

    # Check for safe_areas
    if hasattr(cam_data, 'safe_areas'):
        print("Has 'safe_areas': True")
        sa = cam_data.safe_areas
        print(f"  Type: {type(sa)}")
        # Try to print attributes of safe_areas
        try:
            print(f"  title: {sa.title}")
            print(f"  action: {sa.action}")
            # Also check for individual x/y if they exist directly (though usually title/action are sequences or vectors)
            # Actually in Blender API 2.8+ it is title_x, title_y, action_x, action_y on the DisplaySafeAreas object
            print(f"  title_x: {getattr(sa, 'title_x', 'N/A')}")
            print(f"  title_y: {getattr(sa, 'title_y', 'N/A')}")
            print(f"  action_x: {getattr(sa, 'action_x', 'N/A')}")
            print(f"  action_y: {getattr(sa, 'action_y', 'N/A')}")
        except Exception as e:
            print(f"  Error inspecting safe_areas contents: {e}")
            print(f"  Dir(safe_areas): {dir(sa)}")
    else:
        print("Has 'safe_areas': False")
        print("Listing available attributes on camera data:")
        print(dir(cam_data))

print("--- Inspection Complete ---\n")
