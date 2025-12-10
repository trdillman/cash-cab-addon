"""
CashCab Water Manager
Handles water assets, shoreline generation, and island alignment.
Replaces standard BLOSM water import with a robust Manual Workflow.
"""

import bpy
import bmesh
import os
import sys
import xml.etree.ElementTree as ET
import math # Added for math.radians
from mathutils import Vector
from pathlib import Path
from types import SimpleNamespace
from ..app import blender as blenderApp



# --- CONSTANTS ---
LAKE_CUTTER_EXTRUDE_DEPTH = 80.0
LAKE_CUTTER_Z_TRANSLATE = -20.0
WATER_PLANE_Z = -5.0 # Increased separation
GROUND_PLANE_Z = 0.0
ISLAND_THICKNESS = 10.0

# New Bevel Settings
BEVEL_WIDTH = 5.0
BEVEL_SEGS = 5
BEVEL_ANGLE = math.radians(60.0)

WATER_RUNTIME_COLLECTION = "ASSET_WATER_RESULT"
ASSET_WATER_COLLECTION_NAME = "ASSET_WATER"
CN_TOWER_LAT = 43.6425662
CN_TOWER_LON = -79.3870568
WATER_LAT_MARGIN = 0.03
WATER_LON_MARGIN = 0.04

_ASSET_WATER_MATERIAL_NAME = None
_ASSET_WATER_SURFACE_NAME = "WATER_SURFACE"
_ASSET_WATER_EMISSIVE_NAME = "WATER_EMISSIVE"
ASSET_ISLAND_BLEND_PATH = Path(__file__).resolve().parent.parent / "assets" / "ASSET_ISLAND.blend"
ASSET_WATER_BLEND_PATH = Path(__file__).resolve().parent.parent / "assets" / "ASSET_WATER.blend"
ASSET_GROUND_BLEND_PATH = Path(__file__).resolve().parent.parent / "assets" / "ASSET_GROUND.blend"
_ASSET_ISLAND_TEMPLATE = None

_DEFAULT_MIN_LAT = 51.33
_DEFAULT_MAX_LAT = 51.33721
_DEFAULT_MIN_LON = 12.36902
_DEFAULT_MAX_LON = 12.37983


def _resolve_route_properties(scene: bpy.types.Scene):
    addon = getattr(scene, "blosm", None)
    if addon is not None:
        return addon

    return SimpleNamespace(
        route_import_water=True,
        minLat=_DEFAULT_MIN_LAT,
        maxLat=_DEFAULT_MAX_LAT,
        minLon=_DEFAULT_MIN_LON,
        maxLon=_DEFAULT_MAX_LON,
    )


def _ensure_runtime_collection(scene: bpy.types.Scene) -> bpy.types.Collection:
    collection = bpy.data.collections.get(WATER_RUNTIME_COLLECTION)
    if collection is None:
        collection = bpy.data.collections.new(WATER_RUNTIME_COLLECTION)
        scene.collection.children.link(collection)
    return collection


def _clear_runtime_objects(collection: bpy.types.Collection) -> None:
    """Remove prior runtime water objects to avoid accumulating duplicates."""
    targets = {
        "Lake_Mesh_Cutter",
        "Water_Plane_Result",
        "Ground_Plane_Result",
        "Water_Plane_Emissive",
        "Islands_Mesh",
    }
    for obj in list(bpy.data.objects):
        base = obj.name.split(".")[0]
        if base in targets:
            try:
                for coll in list(getattr(obj, "users_collection", []) or []):
                    coll.objects.unlink(obj)
            except Exception:
                pass
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except Exception:
                pass


def _dedupe_runtime_objects() -> None:
    targets = (
        "Lake_Mesh_Cutter",
        "Water_Plane_Result",
        "Ground_Plane_Result",
    )
    for base in targets:
        base_obj = bpy.data.objects.get(base)
        for obj in list(bpy.data.objects):
            if obj is base_obj:
                continue
            if obj.name.startswith(base + "."):
                try:
                    for coll in list(getattr(obj, "users_collection", []) or []):
                        coll.objects.unlink(obj)
                except Exception:
                    pass
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except Exception:
                    pass


def _move_to_collection(obj: bpy.types.Object, target_col: bpy.types.Collection):
    """Ensure object is linked ONLY to the target collection."""
    if not obj or not target_col:
        return
        
    # Link to target if not already there
    if target_col not in obj.users_collection:
        target_col.objects.link(obj)
        
    # Unlink from all other collections
    for col in obj.users_collection:
        if col != target_col:
            try:
                col.objects.unlink(obj)
            except RuntimeError:
                pass


def _ensure_asset_water_material() -> bpy.types.Material | None:
    """Ensure a primary water material is available, preferring WATER_SURFACE.

    This replaces the old asset_manager-based loader with a direct append
    from ASSET_WATER.blend when needed.
    """
    global _ASSET_WATER_MATERIAL_NAME

    # 1) Cached name
    if _ASSET_WATER_MATERIAL_NAME:
        mat = bpy.data.materials.get(_ASSET_WATER_MATERIAL_NAME)
        if mat:
            return mat

    # 2) Prefer the explicit WATER_SURFACE material if already present
    surface = bpy.data.materials.get(_ASSET_WATER_SURFACE_NAME)
    if surface:
        _ASSET_WATER_MATERIAL_NAME = surface.name
        return surface

    # 3) Fallback: any existing material with 'water' in its name
    for mat in bpy.data.materials:
        if "water" in mat.name.casefold():
            _ASSET_WATER_MATERIAL_NAME = mat.name
            return mat

    # 4) Append materials from ASSET_WATER.blend if available
    if ASSET_WATER_BLEND_PATH.exists():
        try:
            with bpy.data.libraries.load(str(ASSET_WATER_BLEND_PATH), link=False) as (data_from, data_to):
                data_to.materials = list(data_from.materials or [])
        except Exception as exc:
            print(f"[BLOSM] WARN water asset append failed: {exc}")

        surface = bpy.data.materials.get(_ASSET_WATER_SURFACE_NAME)
        if surface:
            _ASSET_WATER_MATERIAL_NAME = surface.name
            return surface

    return None


def _ensure_water_materials():
    """Ensure WATER_SURFACE and WATER_EMISSIVE materials from ASSET_WATER are present in bpy.data.

    Returns a tuple: (surface_mat, emissive_mat), where either may be None if not found.
    """
    surface = bpy.data.materials.get(_ASSET_WATER_SURFACE_NAME)
    emissive = bpy.data.materials.get(_ASSET_WATER_EMISSIVE_NAME)

    if surface and emissive:
        return surface, emissive

    # Attempt to append from ASSET_WATER.blend when either material is missing.
    if ASSET_WATER_BLEND_PATH.exists():
        try:
            with bpy.data.libraries.load(str(ASSET_WATER_BLEND_PATH), link=False) as (data_from, data_to):
                # Only load materials we don't already have to keep noise down
                needed = []
                for name in (_ASSET_WATER_SURFACE_NAME, _ASSET_WATER_EMISSIVE_NAME):
                    if name in (data_from.materials or []) and bpy.data.materials.get(name) is None:
                        needed.append(name)
                if needed:
                    data_to.materials = needed
        except Exception as exc:
            print(f"[BLOSM] WARN water materials append failed: {exc}")

    # Re-resolve after potential load
    surface = bpy.data.materials.get(_ASSET_WATER_SURFACE_NAME)
    emissive = bpy.data.materials.get(_ASSET_WATER_EMISSIVE_NAME)
    return surface, emissive


def _ensure_asset_ground_material() -> bpy.types.Material | None:
    """Ensure 'ground' material from ASSET_GROUND is loaded.

    This replaces the old asset_manager-based loader with a direct append
    from ASSET_GROUND.blend when needed.
    """
    # Try to find existing first
    mat = bpy.data.materials.get("ground")
    if mat:
        return mat

    # Append materials from ASSET_GROUND.blend if available
    if ASSET_GROUND_BLEND_PATH.exists():
        try:
            with bpy.data.libraries.load(str(ASSET_GROUND_BLEND_PATH), link=False) as (data_from, data_to):
                if data_from.materials:
                    data_to.materials = list(data_from.materials)
        except Exception as exc:
            print(f"[BLOSM] WARN ground asset append failed: {exc}")

    return bpy.data.materials.get("ground")


def _ensure_asset_island_template() -> bpy.types.Object | None:
    """Append the ASSET_ISLAND template object from ASSET_ISLAND.blend (not linked to scene).

    Returns a mesh object whose materials/modifiers represent the desired island style.
    The template is cached for reuse.
    """
    global _ASSET_ISLAND_TEMPLATE

    if _ASSET_ISLAND_TEMPLATE and _ASSET_ISLAND_TEMPLATE.name in bpy.data.objects:
        return _ASSET_ISLAND_TEMPLATE

    if not ASSET_ISLAND_BLEND_PATH.exists():
        return None

    try:
        with bpy.data.libraries.load(str(ASSET_ISLAND_BLEND_PATH), link=False) as (data_from, data_to):
            if "ASSET_ISLAND" in data_from.objects:
                data_to.objects = ["ASSET_ISLAND"]
            elif data_from.objects:
                # Fallback to the first available object in the asset file
                data_to.objects = [data_from.objects[0]]
    except Exception as exc:
        print(f"[BLOSM] WARN island asset template load failed: {exc}")
        return None

    tmpl = bpy.data.objects.get("ASSET_ISLAND")
    if tmpl is None:
        # Fallback: pick any mesh that was just appended
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                tmpl = obj
                break

    if tmpl is None:
        return None

    _ASSET_ISLAND_TEMPLATE = tmpl
    return tmpl


def _apply_island_template_style(island_mesh: bpy.types.Object) -> None:
    """Apply material and modifiers from ASSET_ISLAND template to the given island mesh.

    If the template cannot be loaded, falls back to the legacy inline modifier/material setup.
    """
    tmpl = _ensure_asset_island_template()

    if tmpl is None or tmpl.type != 'MESH':
        # Fallback: legacy simple modifiers + material
        # Add Weld modifier
        mod_weld = island_mesh.modifiers.new(name="Weld", type='WELD')
        mod_weld.merge_threshold = 0.001 # Default or adjust if needed

        mod_bev = island_mesh.modifiers.new(name="Bevel", type='BEVEL')
        mod_bev.width = BEVEL_WIDTH
        mod_bev.segments = BEVEL_SEGS
        mod_bev.limit_method = 'ANGLE'
        mod_bev.angle_limit = BEVEL_ANGLE

        # Blender 4.1+ Auto Smooth Replacement
        # 1. Shade Smooth
        bpy.ops.object.shade_smooth()
        
        # 2. Add "Smooth by Angle" modifier (Geometry Nodes)
        mod_smooth = None
        try:
            # Try to add from Essentials Asset Library (standard in Blender 4.1+)
            bpy.ops.object.modifier_add_node_group(
                asset_library_type='ESSENTIALS',
                asset_library_identifier="",
                relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle"
            )
            mod_smooth = island_mesh.modifiers[-1]
        except Exception:
            # Fallback 1: Check if Node Group exists locally
            ng_name = "Smooth by Angle"
            if ng_name in bpy.data.node_groups:
                mod_smooth = island_mesh.modifiers.new(name=ng_name, type='NODES')
                mod_smooth.node_group = bpy.data.node_groups[ng_name]
                print(f"[BLOSM] Used local '{ng_name}' node group.")
            
        if mod_smooth and mod_smooth.type == 'NODES':
            # "Input_1" is standard for the angle input in this node group
            mod_smooth["Input_1"] = BEVEL_ANGLE
        else:
            print("[BLOSM] WARN: 'Smooth by Angle' modifier skipped (Essentials missing and no local group).")

        mat_iso = bpy.data.materials.new("Island_Mat")
        mat_iso.diffuse_color = (0.1, 0.5, 0.1, 1)
        island_mesh.data.materials.append(mat_iso)
        print("[BLOSM] WARN: Using legacy island material/modifiers (ASSET_ISLAND template unavailable)")
        return

    # Copy materials from template
    try:
        if getattr(tmpl.data, "materials", None):
            island_mesh.data.materials.clear()
            for mat in tmpl.data.materials:
                if mat:
                    island_mesh.data.materials.append(mat)
    except Exception as exc:
        print(f"[BLOSM] WARN island material transfer failed: {exc}")

    # Clear existing modifiers on the generated mesh
    for m in list(island_mesh.modifiers):
        try:
            island_mesh.modifiers.remove(m)
        except Exception:
            pass

    # Recreate important modifiers, ensuring Weld comes first, then Bevel
    # We also ensure new bevel settings are applied whether from template or default
    
    # Add Weld modifier first
    mod_weld = island_mesh.modifiers.new(name="Weld", type='WELD')
    mod_weld.merge_threshold = 0.001 # Default or adjust if needed
    
    has_bevel = False
    for src in tmpl.modifiers:
        if src.type in ['SOLIDIFY', 'SMOOTH', 'WELD']:
            continue
            
        try:
            new_mod = island_mesh.modifiers.new(name=src.name, type=src.type)
            if src.type == 'BEVEL':
                has_bevel = True
        except Exception as exc:
            print(f"[BLOSM] WARN island modifier create failed for {src.name}: {exc}")
            continue

        try:
            if src.type == 'BEVEL':
                new_mod.width = getattr(src, "width", BEVEL_WIDTH)
                new_mod.segments = getattr(src, "segments", BEVEL_SEGS)
                new_mod.limit_method = getattr(src, "limit_method", 'ANGLE')
                new_mod.angle_limit = getattr(src, "angle_limit", BEVEL_ANGLE)
        except Exception as exc:
            print(f"[BLOSM] WARN island modifier copy failed for {src.name}: {exc}")

    # Ensure Bevel modifier exists (user requirement) even if not in template
    if not has_bevel:
        mod_bev = island_mesh.modifiers.new(name="Bevel", type='BEVEL')
        mod_bev.width = BEVEL_WIDTH
        mod_bev.segments = BEVEL_SEGS
        mod_bev.limit_method = 'ANGLE'
        mod_bev.angle_limit = BEVEL_ANGLE

    # Blender 4.1+ Auto Smooth Replacement
    try:
        # Ensure object is active/selected for ops
        bpy.ops.object.select_all(action='DESELECT')
        island_mesh.select_set(True)
        bpy.context.view_layer.objects.active = island_mesh
        
        # 1. Shade Smooth
        bpy.ops.object.shade_smooth()
        
        # 2. Add "Smooth by Angle" modifier
        # This relies on the 'Essentials' asset library being available (standard in Blender 4.1+)
        start_mod_count = len(island_mesh.modifiers)
        try:
            bpy.ops.object.modifier_add_node_group(
                asset_library_type='ESSENTIALS',
                asset_library_identifier="",
                relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle"
            )
        except Exception:
            pass # Fallback to check if added or try local
        
        if len(island_mesh.modifiers) > start_mod_count:
            mod_smooth = island_mesh.modifiers[-1]
            if mod_smooth.type == 'NODES':
                 mod_smooth["Input_1"] = BEVEL_ANGLE
        else:
            # Fallback 1: Check if Node Group exists locally
            ng_name = "Smooth by Angle"
            if ng_name in bpy.data.node_groups:
                mod_smooth = island_mesh.modifiers.new(name=ng_name, type='NODES')
                mod_smooth.node_group = bpy.data.node_groups[ng_name]
                mod_smooth["Input_1"] = BEVEL_ANGLE
                print(f"[BLOSM] Used local '{ng_name}' node group.")
            else:
                # Fallback 2: Standard Smooth Modifier (better than nothing)
                # mod_smooth = island_mesh.modifiers.new(name="Smooth", type='SMOOTH')
                # mod_smooth.factor = 1.0
                # mod_smooth.iterations = 2
                print("[BLOSM] WARN: 'Smooth by Angle' modifier skipped (Essentials missing and no local group).")
             
    except Exception as exc:
        print(f"[BLOSM] WARN failed to apply auto smooth logic: {exc}")

    print("[BLOSM] Applied ASSET_ISLAND material and modifiers to Islands_Mesh")

def get_projected_co(lat, lon, projection):
    x, y, z = projection.fromGeographic(lat, lon)
    return Vector((x, y, 0))

def stitch_ways(ways_data):
    if not ways_data: return []
    pool = [list(w) for w in ways_data if len(w) > 1]
    chains = []
    while pool:
        chain = pool.pop(0)
        changed = True
        while changed:
            changed = False
            head = chain[0]; tail = chain[-1]; tol = 0.01
            to_remove = []
            for i, seg in enumerate(pool):
                if (tail - seg[0]).length < tol: chain.extend(seg[1:]); to_remove.append(i); changed = True; break
                elif (tail - seg[-1]).length < tol: seg.reverse(); chain.extend(seg[1:]); to_remove.append(i); changed = True; break
                elif (head - seg[-1]).length < tol: chain[0:0] = seg[:-1]; to_remove.append(i); changed = True; break
                elif (head - seg[0]).length < tol: seg.reverse(); chain[0:0] = seg[:-1]; to_remove.append(i); changed = True; break
            for i in sorted(to_remove, reverse=True): pool.pop(i)
        chains.append(chain)
    return chains

def get_raw_content_bounds():
    min_v = Vector((float('inf'), float('inf'), 0))
    max_v = Vector((float('-inf'), float('-inf'), 0))
    found = False
    for obj in bpy.data.objects:
        # Exclude generated assets/infrastructure to find the "content" (buildings, roads)
        if obj.type == 'MESH' and "ASSET" not in obj.name and "Cutter" not in obj.name and "Result" not in obj.name and "Island_Curve_Obj" not in obj.name:
            found = True
            for b in obj.bound_box:
                world_b = obj.matrix_world @ Vector(b)
                min_v.x = min(min_v.x, world_b.x)
                min_v.y = min(min_v.y, world_b.y)
                max_v.x = max(max_v.x, world_b.x)
                max_v.y = max(max_v.y, world_b.y)
    
    if not found:
        return 0, 0, 0, 0, False # default
        
    return min_v.x, min_v.y, max_v.x, max_v.y, True

def fetch_raw_water_data(minLat, minLon, maxLat, maxLon):
    print(f"[BLOSM] Fetching Raw Water Data for {minLat},{minLon} to {maxLat},{maxLon}")
    osm_file = os.path.join(bpy.app.tempdir, "water_import_raw.osm")
    
    query = f"""
    [out:xml][timeout:25];
    (
      way["natural"="water"]({minLat},{minLon},{maxLat},{maxLon});
      relation["natural"="water"]({minLat},{minLon},{maxLat},{maxLon});
      way["water"]({minLat},{minLon},{maxLat},{maxLon});
      relation["water"]({minLat},{minLon},{maxLat},{maxLon});
      way["waterway"]({minLat},{minLon},{maxLat},{maxLon});
      relation["waterway"]({minLat},{minLon},{maxLat},{maxLon});
      way["natural"="coastline"]({minLat},{minLon},{maxLat},{maxLon});
      relation["natural"="coastline"]({minLat},{minLon},{maxLat},{maxLon});
    );
    (._;>;);
    out body;
    """
    import urllib.request
    import urllib.parse
    
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({'data': query}).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            with open(osm_file, 'wb') as f: f.write(response.read())
        return osm_file
    except Exception as e:
        print(f"[BLOSM] Water Download failed: {e}")
        return None

def process(context, bounds=None):
    """Main entry point called by fetch_operator"""
    addon = _resolve_route_properties(context.scene)
    print("[BLOSM] Starting Water Manager (Manual Workflow Integration)...")

    runtime_collection = _ensure_runtime_collection(context.scene)
    _clear_runtime_objects(runtime_collection)
    
    # 1. Get Bounds
    use_route_bounds = bool(bounds)
    if use_route_bounds:
        minLat, minLon, maxLat, maxLon = bounds
    else:
        # Fallback to properties (risky if state restored)
        minLat = addon.minLat
        maxLat = addon.maxLat
        minLon = addon.minLon
        maxLon = addon.maxLon

    # Expand bounds to ensure shoreline south of CN Tower is included
    if use_route_bounds:
        if minLat > CN_TOWER_LAT - WATER_LAT_MARGIN:
            minLat = CN_TOWER_LAT - WATER_LAT_MARGIN
        if maxLat < CN_TOWER_LAT + WATER_LAT_MARGIN:
            maxLat = CN_TOWER_LAT + WATER_LAT_MARGIN
        if minLon > CN_TOWER_LON - WATER_LON_MARGIN:
            minLon = CN_TOWER_LON - WATER_LON_MARGIN
        if maxLon < CN_TOWER_LON + WATER_LON_MARGIN:
            maxLon = CN_TOWER_LON + WATER_LON_MARGIN
    
    # Ensure Projection (reuse stored origin if available for consistent XY positioning)
    stored_origin = None
    try:
        stored_origin = tuple(context.scene.get("cashcab_projection_origin", ())) if context else None
    except Exception:
        stored_origin = None
    if stored_origin and len(stored_origin) == 2:
        center_lat, center_lon = stored_origin
    else:
        center_lat = (minLat + maxLat) / 2
        center_lon = (minLon + maxLon) / 2
    blenderApp.app.setProjection(center_lat, center_lon)
    projection = blenderApp.app.projection
    
    # 2. Fetch Raw Data
    osm_file = fetch_raw_water_data(minLat, minLon, maxLat, maxLon)
    stitched_outer = []
    stitched_inner = []

    if osm_file:
        # 3. Parse
        print("[BLOSM] Parsing Water Geometry...")
        tree = ET.parse(osm_file)
        root = tree.getroot()
        
        nodes = {} 
        for node in root.findall('node'):
            nodes[node.get('id')] = (float(node.get('lat')), float(node.get('lon')))
            
        ways = {}
        for way in root.findall('way'):
            nd_refs = [nd.get('ref') for nd in way.findall('nd')]
            coords = []
            for nid in nd_refs:
                if nid in nodes:
                    coords.append(get_projected_co(nodes[nid][0], nodes[nid][1], projection))
            ways[way.get('id')] = coords
            
        outer_segments = []
        inner_segments = []
        
        for rel in root.findall('relation'):
            tags = {tag.get('k'): tag.get('v') for tag in rel.findall('tag')}
            if not any(t in tags for t in ["water", "natural", "waterway", "coastline"]):
                continue
            
            for member in rel.findall('member'):
                if member.get('type') == 'way':
                    ref = member.get('ref')
                    role = member.get('role')
                    if ref in ways:
                        if role in ['outer', '']:
                            outer_segments.append(ways[ref])
                        elif role == 'inner':
                            inner_segments.append(ways[ref])
                            
        if not outer_segments and not inner_segments:
            for w in ways.values():
                outer_segments.append(w)
                
        stitched_outer = stitch_ways(outer_segments)
        stitched_inner = stitch_ways(inner_segments)
    else:
        print("[BLOSM] Water Download failed: falling back to default water plane geometry.")
    
    print(f"[BLOSM] Found {len(stitched_outer)} Lake Loops and {len(stitched_inner)} Island Loops.")
    
    # 4. Create Geometry
    
    # A. Lake Cutter
    lake_mesh = None
    if stitched_outer:
        curve_data = bpy.data.curves.new(name="Lake_Curve", type='CURVE')
        curve_data.dimensions = '2D'
        for loop in stitched_outer:
            spline = curve_data.splines.new(type='POLY')
            spline.points.add(len(loop) - 1)
            for k, co in enumerate(loop): spline.points[k].co = (co.x, co.y, 0, 1)
            spline.use_cyclic_u = True
            
        lake_obj = bpy.data.objects.new("Lake_Curve_Obj", curve_data)
        runtime_collection.objects.link(lake_obj)
        
        # CRITICAL: Deselect before working on new objects
        bpy.ops.object.select_all(action='DESELECT')
        
        context.view_layer.objects.active = lake_obj
        lake_obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        lake_mesh = context.active_object
        lake_mesh.name = "Lake_Mesh_Cutter"
        _move_to_collection(lake_mesh, runtime_collection)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.translate(value=(0, 0, LAKE_CUTTER_Z_TRANSLATE))
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, LAKE_CUTTER_EXTRUDE_DEPTH)})
        bpy.ops.object.mode_set(mode='OBJECT')
        lake_mesh.display_type = 'WIRE'
        lake_mesh.hide_render = True
        lake_mesh.hide_viewport = True # CRITICAL: Hide from viewport
        
        # B. Planes Calculation
        min_x, min_y, max_x, max_y, found = get_raw_content_bounds()
        if not found:
            # Fallback defaults if no content
            min_x, min_y, max_x, max_y = -1000, -1000, 1000, 1000
            
        # Apply scene padding to base bounds (ensures South edge covers shoreline gap)
        padding = getattr(addon, "route_padding_m", 500.0)
        base_min_x = min_x - padding
        base_max_x = max_x + padding
        base_min_y = min_y - padding
        base_max_y = max_y + padding
        
        base_w = base_max_x - base_min_x
        base_h = base_max_y - base_min_y
        
        # Water Plane (3x base size)
        water_scale_factor = 3.0
        water_w = max(10000.0, base_w * water_scale_factor)
        water_h = max(10000.0, base_h * water_scale_factor)
        water_cx = (base_min_x + base_max_x) / 2
        water_cy = (base_min_y + base_max_y) / 2
        
        # Land Plane (Asymmetric Extension: 5x N/E/W relative to base, 0x S relative to base)
        ext_w = base_w * 5.0
        ext_h = base_h * 5.0
        
        land_min_x = base_min_x - ext_w
        land_max_x = base_max_x + ext_w
        land_min_y = base_min_y # 0x extension South (keeps padding)
        land_max_y = base_max_y + ext_h
        
        land_w = land_max_x - land_min_x
        land_h = land_max_y - land_min_y
        land_cx = (land_min_x + land_max_x) / 2
        land_cy = (land_min_y + land_max_y) / 2
        
        bpy.ops.object.select_all(action='DESELECT')
        
        # Create Water Plane
        bpy.ops.mesh.primitive_plane_add(size=1, location=(water_cx, water_cy, WATER_PLANE_Z))
        water = context.active_object
        water.name = "Water_Plane_Result"
        water.scale = (water_w, water_h, 1)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        _move_to_collection(water, runtime_collection)

        # Assign surface/emissive materials based on ASSET_WATER asset
        surface_mat, emissive_mat = _ensure_water_materials()

        # Top plane: surface material (fallback to simple blue if missing)
        water.data.materials.clear()
        if surface_mat:
            water.data.materials.append(surface_mat)
        else:
            fallback = bpy.data.materials.new("Water_Surface_Fallback")
            fallback.diffuse_color = (0.0, 0.4, 0.8, 1)
            water.data.materials.append(fallback)

        cycles_vis = getattr(water, "cycles_visibility", None)
        if cycles_vis:
            cycles_vis.diffuse = False
            cycles_vis.glossy = False

        # Duplicate emissive plane slightly below for glow
        emissive = water.copy()
        emissive.data = water.data.copy()
        emissive.name = "Water_Plane_Emissive"
        emissive.location.z = WATER_PLANE_Z - 2.0
        runtime_collection.objects.link(emissive)

        emissive.data.materials.clear()
        if emissive_mat:
            emissive.data.materials.append(emissive_mat)
        elif surface_mat:
            # As a fallback, reuse surface material; user can tweak later
            emissive.data.materials.append(surface_mat)

        # C. Ground Plane (Z=0, Boolean Diff)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(land_cx, land_cy, GROUND_PLANE_Z))
        ground = context.active_object
        ground.name = "Ground_Plane_Result"
        ground.scale = (land_w, land_h, 1)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        _move_to_collection(ground, runtime_collection)
        
        mod = ground.modifiers.new(name="LakeBool", type='BOOLEAN')
        mod.object = lake_mesh
        mod.operation = 'DIFFERENCE'
        mod.solver = 'FAST'
        
        # Apply ground material from asset
        mat_ground = _ensure_asset_ground_material()
        if mat_ground:
            ground.data.materials.append(mat_ground)
        else:
            # Fallback
            mat_ground = bpy.data.materials.new("Ground_Mat")
            mat_ground.diffuse_color = (0.2, 0.2, 0.2, 1)
            ground.data.materials.append(mat_ground)

    # D. Islands (Z=-5, Styled with ASSET_ISLAND)
    if stitched_inner:
        curve_data_iso = bpy.data.curves.new(name="Island_Curve", type='CURVE')
        curve_data_iso.dimensions = '2D'
        for loop in stitched_inner:
            spline = curve_data_iso.splines.new(type='POLY')
            spline.points.add(len(loop) - 1)
            for k, co in enumerate(loop): spline.points[k].co = (co.x, co.y, 0, 1)
            spline.use_cyclic_u = True
            
        island_obj = bpy.data.objects.new("Island_Curve_Obj", curve_data_iso)
        runtime_collection.objects.link(island_obj)
        
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = island_obj
        island_obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        island_mesh = context.active_object
        island_mesh.name = "Islands_Mesh"
        island_mesh.location.z = WATER_PLANE_Z # Anchored at Water Level
        _move_to_collection(island_mesh, runtime_collection)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.fill()
        
        # Extrude islands to give them volume (replacing Solidify modifier)
        # Use extrude_region_move for robust geometric extrusion + translation
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (0, 0, ISLAND_THICKNESS)}
        )
        
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply material and modifiers from ASSET_ISLAND template
        _apply_island_template_style(island_mesh)

    _dedupe_runtime_objects()
    print("[BLOSM] Water/Island Processing Complete")
