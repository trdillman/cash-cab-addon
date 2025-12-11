import bpy

print("\n--- Inspecting Scene Safe Areas ---")
scene = bpy.context.scene
if hasattr(scene, "safe_areas"):
    sa = scene.safe_areas
    print(f"Safe Areas Type: {type(sa)}")
    print(f"Attributes: {dir(sa)}")
    try:
        print(f"title: {sa.title} (type: {type(sa.title)})")
        print(f"action: {sa.action} (type: {type(sa.action)})")
    except Exception as e:
        print(f"Error accessing title/action: {e}")
        
    try:
        print(f"title_x: {sa.title_x}")
    except AttributeError:
        print("title_x: <Not Found>")
        
else:
    print("Scene has no 'safe_areas' property")

print("--- Inspection Complete ---\n")
