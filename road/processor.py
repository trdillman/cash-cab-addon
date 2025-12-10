"""
Road Processor - Simple functions for road adaptation workflow
Handles basic road processing functionality without complex dependencies
"""

import bpy
from typing import List, Optional

# Simple functions for test compatibility
def process_roads() -> Optional[bpy.types.Object]:
    """
    Main road processing function for test compatibility

    Returns:
        Unified road mesh object or None if processing failed
    """
    from .config import AUTO_ADAPT_ROADS, ROAD_COLLECTION_NAME, UNIFIED_ROAD_MATERIAL_NAME

    if not AUTO_ADAPT_ROADS:
        return None

    try:
        # Get all road curve objects in scene
        road_objects = get_road_objects()

        if not road_objects:
            return None

        # Create unified material
        unified_material = create_unified_material()

        # Convert curves to meshes
        mesh_objects = []
        for road_obj in road_objects:
            mesh_obj = convert_curve_to_mesh(road_obj)
            if mesh_obj:
                # Apply unified material
                if mesh_obj.data.materials:
                    mesh_obj.data.materials[0] = unified_material
                else:
                    mesh_obj.data.materials.append(unified_material)
                mesh_objects.append(mesh_obj)

        if not mesh_objects:
            return None

        # Join all road objects into single mesh
        unified_road = join_road_objects(mesh_objects)

        if unified_road:
            # ENSURE CORRECT NAMING - CRITICAL FIX
            unified_road.name = "ASSET_ROADS"

            # Set visibility properties - ENSURE VISIBILITY BY DEFAULT
            unified_road.hide_viewport = False
            unified_road.hide_render = False
            unified_road.hide_set(False)

            # Also ensure object is selectable and visible in outliner
            unified_road.hide_select = False

            # Add CashCab custom property for proper asset identification
            unified_road["cashcab_asset_type"] = "roads"
            unified_road["cashcab_managed"] = True

            # Create and organize collections
            create_roads_collection()
            roads_collection = bpy.data.collections.get(ROAD_COLLECTION_NAME)
            if roads_collection:
                # Ensure the unified road is in the correct collection
                if unified_road.name not in roads_collection.objects:
                    roads_collection.objects.link(unified_road)

                # Ensure collection is visible and properly organized
                roads_collection.hide_viewport = False
                roads_collection.hide_render = False
                roads_collection.hide_select = False

                # Add collection identifier property
                roads_collection["cashcab_asset_collection"] = True

                # Remove from master collection to prevent duplication
                master_collection = bpy.context.scene.collection
                if unified_road.name in master_collection.objects:
                    master_collection.objects.unlink(unified_road)

                # Also remove from any other non-asset collections
                for coll in unified_road.users_collection:
                    if coll.name != ROAD_COLLECTION_NAME and not coll.name.startswith("ASSET_"):
                        try:
                            coll.objects.unlink(unified_road)
                        except RuntimeError:
                            pass  # Already unlinked

            # Final verification and logging
            print(f"[ROAD] Created unified road mesh: {unified_road.name}")
            print(f"[ROAD] Road mesh visibility: viewport={not unified_road.hide_viewport}, render={not unified_road.hide_render}")
            print(f"[ROAD] Road mesh in collection: {ROAD_COLLECTION_NAME}")

            return unified_road

        return None

    except Exception as e:
        print(f"[ERROR] Road processing failed: {e}")
        return None


def get_road_objects() -> List[bpy.types.Object]:
    """
    Find and collect road curve objects in the scene

    Returns:
        List of road curve objects
    """
    road_objects = []

    for obj in bpy.data.objects:
        if obj.type == 'CURVE' and obj.data:
            # Check if object name suggests it's a road
            obj_name_lower = obj.name.lower()
            if any(road_type in obj_name_lower for road_type in ['highway', 'road', 'street', 'way']):
                road_objects.append(obj)

    return road_objects


def create_unified_material() -> bpy.types.Material:
    """
    Create unified road material

    Returns:
        Material named UNIFIED_ROAD_MATERIAL_NAME
    """
    from .config import UNIFIED_ROAD_MATERIAL_NAME

    # Check if material already exists
    if UNIFIED_ROAD_MATERIAL_NAME in bpy.data.materials:
        return bpy.data.materials[UNIFIED_ROAD_MATERIAL_NAME]

    # Try to append RoadUnified material from ASSET_ROADS asset file
    try:
        from ..route import assets as route_assets
        from ..route import resolve as route_resolve
        asset_path = route_assets.ASSET_DIRECTORY / "ASSET_ROADS.blend"
        if asset_path.exists():
            # Ensure the RoadUnified material is appended from the asset file
            route_resolve.ensure_appended(str(asset_path), "materials", [UNIFIED_ROAD_MATERIAL_NAME])
            mat = bpy.data.materials.get(UNIFIED_ROAD_MATERIAL_NAME)
            if mat is not None:
                # Tag as managed asset material
                mat["cashcab_asset_type"] = "roads"
                mat["cashcab_managed"] = True
                return mat
    except Exception as exc:  # Fallback if asset loading fails
        print(f"[ROAD] WARN: failed to append RoadUnified from ASSET_ROADS.blend: {exc}")

    # Fallback: create a simple dark gray material
    material = bpy.data.materials.new(name=UNIFIED_ROAD_MATERIAL_NAME)
    material.use_nodes = True
    if material.node_tree:
        material.node_tree.nodes.clear()
        material.node_tree.links.clear()
    material.diffuse_color = (0.2, 0.2, 0.2, 1.0)
    material.roughness = 0.8
    material.metallic = 0.0
    material["cashcab_asset_type"] = "roads"
    material["cashcab_managed"] = True
    return material


def create_roads_collection():
    """Create ASSET_ROADS collection if it doesn't exist"""
    from .config import ROAD_COLLECTION_NAME

    if ROAD_COLLECTION_NAME not in bpy.data.collections:
        collection = bpy.data.collections.new(name=ROAD_COLLECTION_NAME)
        # Ensure collection is visible by default
        collection.hide_viewport = False
        collection.hide_render = False
        collection.hide_select = False

        # Add collection identifier property
        collection["cashcab_asset_collection"] = True

        bpy.context.scene.collection.children.link(collection)

        print(f"[ROAD] Created collection: {ROAD_COLLECTION_NAME}")


def convert_curve_to_mesh(curve_obj: bpy.types.Object) -> Optional[bpy.types.Object]:
    """
    Convert curve object to mesh

    Args:
        curve_obj: Curve object to convert

    Returns:
        Mesh object or None if conversion failed
    """
    try:
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')

        # Select the curve object
        curve_obj.select_set(True)
        bpy.context.view_layer.objects.active = curve_obj

        # Convert using Blender operator (works better in headless mode)
        bpy.ops.object.convert(target='MESH')

        # Get the converted mesh object
        mesh_obj = bpy.context.view_layer.objects.active

        if mesh_obj and mesh_obj.type == 'MESH':
            # Rename to indicate it's a converted mesh
            mesh_obj.name = f"Mesh_{curve_obj.name}"

            # Add temporary property for identification
            mesh_obj["cashcab_converted_from_curve"] = curve_obj.name

            return mesh_obj
        else:
            print(f"[ERROR] Conversion failed for {curve_obj.name}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to convert curve {curve_obj.name} to mesh: {e}")
        return None


def join_road_objects(mesh_objects: List[bpy.types.Object]) -> Optional[bpy.types.Object]:
    """
    Join multiple road mesh objects into single mesh

    Args:
        mesh_objects: List of mesh objects to join

    Returns:
        Unified mesh object or None if joining failed
    """
    if not mesh_objects:
        return None

    if len(mesh_objects) == 1:
        # Single object case - ensure proper naming
        mesh_objects[0].name = "ASSET_ROADS"
        return mesh_objects[0]

    try:
        # Select all objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in mesh_objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        # Join objects
        bpy.ops.object.join()

        # Get the active object (result of join)
        joined_obj = bpy.context.view_layer.objects.active

        # ENSURE PROPER NAMING - CRITICAL FIX
        if joined_obj:
            joined_obj.name = "ASSET_ROADS"

            # Add CashCab identification properties
            joined_obj["cashcab_asset_type"] = "roads"
            joined_obj["cashcab_managed"] = True
            joined_obj["cashcab_joined_from"] = len(mesh_objects)

            print(f"[ROAD] Joined {len(mesh_objects)} road objects into: {joined_obj.name}")

        return joined_obj

    except Exception as e:
        print(f"[ERROR] Failed to join road objects: {e}")
        return None


def verify_road_asset_registration():
    """
    Verify that the ASSET_ROADS object is properly registered for clean/clear functionality

    Returns:
        bool: True if asset is properly registered, False otherwise
    """
    try:
        road_obj = bpy.data.objects.get("ASSET_ROADS")
        if not road_obj:
            print("[ROAD] ERROR: ASSET_ROADS object not found")
            return False

        # Check if object has proper identification
        has_properties = (
            road_obj.get("cashcab_asset_type") == "roads" and
            road_obj.get("cashcab_managed") is True
        )

        # Check visibility
        is_visible = not road_obj.hide_viewport and not road_obj.hide_render

        # Check collection
        roads_collection = bpy.data.collections.get("ASSET_ROADS")
        in_collection = roads_collection and road_obj.name in roads_collection.objects

        print(f"[ROAD] Asset registration check:")
        print(f"  - Object exists: {road_obj is not None}")
        print(f"  - Has CashCab properties: {has_properties}")
        print(f"  - Is visible: {is_visible}")
        print(f"  - In ASSET_ROADS collection: {in_collection}")

        return road_obj is not None and is_visible and in_collection

    except Exception as e:
        print(f"[ROAD] ERROR in asset registration verification: {e}")
        return False
