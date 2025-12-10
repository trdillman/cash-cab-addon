"""Asset append utilities and operators for BLOSM route import."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import bpy

from bpy.types import Operator

from . import resolve as route_resolve


ASSET_DIRECTORY = Path(__file__).resolve().parent.parent / "assets"
ROUTE_BLEND_PATH = ASSET_DIRECTORY / "ASSET_ROUTE.blend"
CAR_BLEND_PATH = ASSET_DIRECTORY / "ASSET_CAR.blend"
BUILD_BLEND_PATH = ASSET_DIRECTORY / "ASSET_BUILDINGS.blend"
BEAM_BLEND_PATH = ASSET_DIRECTORY / "ASSET_BEAM.blend"
MARKERS_BLEND_PATH = ASSET_DIRECTORY / "ASSET_MARKERS.blend"

ASSETS_COLLECTION_NAME = "BLOSM_Assets"
CAR_OBJECT = "ASSET_CAR"

_LAST_SUMMARY: Dict[str, Optional[str]] = {
    'route_mat': None,
    'route_ng': None,
    'car_obj': None,
    'bld_ng': None,
    'bld_mat': None,
    'beam_obj': None,
    'markers_coll': None,
}


class RouteAssetError(RuntimeError):
    """Raised when asset append operations cannot proceed."""


def _prefer_name(candidates: list[str], *, contains: str | None = None) -> Optional[str]:
    ordered = [name for name in candidates if name]
    if not ordered:
        return None
    if contains:
        needle = contains.casefold()
        for name in ordered:
            if needle in name.casefold():
                return name
    return ordered[0]


def _ensure_collection(context: bpy.types.Context) -> bpy.types.Collection:
    collection = bpy.data.collections.get(ASSETS_COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(ASSETS_COLLECTION_NAME)
        scene = getattr(context, 'scene', None)
        if scene:
            try:
                scene.collection.children.link(collection)
            except RuntimeError:
                pass
    collection.hide_viewport = True
    collection.hide_render = True
    return collection


def _dedupe_car(car_obj: bpy.types.Object) -> None:
    base = car_obj.name
    for other in list(bpy.data.objects):
        if other is car_obj:
            continue
        name_cf = other.name.casefold()
        if other.name == base or other.name.startswith(f"{base}.") or name_cf.startswith('routepreview'):
            try:
                bpy.data.objects.remove(other, do_unlink=True)
            except Exception:
                pass


def _configure_car_trail_modifier(context: bpy.types.Context, car_collection: bpy.types.Collection) -> None:
    """Configure CAR_TRAIL geometry nodes modifier to reference the route curve."""

    # Find CAR_TRAIL object in the collection
    car_trail_obj = None
    for obj in car_collection.objects:
        if obj.name == "CAR_TRAIL" and obj.type == 'CURVE':
            car_trail_obj = obj
            break

    if not car_trail_obj:
        print("[BLOSM] CAR_TRAIL object not found in ASSET_CAR collection")
        return

    print(f"[BLOSM] Found CAR_TRAIL object: {car_trail_obj.name}")

    # Check if CAR_TRAIL has geometry nodes modifier
    geo_modifier = None
    for modifier in car_trail_obj.modifiers:
        if modifier.type == 'NODES':
            geo_modifier = modifier
            break

    if not geo_modifier:
        print("[BLOSM] CAR_TRAIL has no geometry nodes modifier")
        return

    print(f"[BLOSM] Found geometry nodes modifier: {geo_modifier.name}")

    # Find the route curve in the scene
    route_obj = None

    # Try different possible route curve names (ROUTE is the canonical name
    # for the imported curve; keep legacy aliases for robustness)
    route_names = ["ROUTE", "Route", "RouteCurve", "RouteLine", "ASSET_RouteTrace"]

    for name in route_names:
        obj = bpy.data.objects.get(name)
        if obj and obj.type == 'CURVE':
            route_obj = obj
            break

    # If not found by name, search for curve objects with geometry nodes
    if not route_obj:
        for obj in bpy.data.objects:
            if obj.type == 'CURVE':
                # Check if it has route-related geometry nodes modifier
                for modifier in obj.modifiers:
                    if modifier.type == 'NODES' and modifier.node_group:
                        node_group_name = modifier.node_group.name.lower()
                        if 'route' in node_group_name or 'trace' in node_group_name:
                            route_obj = obj
                            break
                if route_obj:
                    break

    if not route_obj:
        print("[BLOSM] Route curve not found - CAR_TRAIL GeoNodes will not be configured")
        return

    print(f"[BLOSM] Found route curve: {route_obj.name}")

    # Configure the geometry nodes modifier object input field
    # The syntax is: modifier["Input_X"] = object_reference
    # We need to find the correct input name for the object field

    # Try common input names for object references
    # Based on testing, CAR_TRAIL uses "Socket_2" for the object input
    possible_input_names = ["Socket_2", "Object", "Object_001", "Input_5", "Input_6", "Input_7", "Curve", "Route"]

    configured = False
    for input_name in possible_input_names:
        if input_name in geo_modifier:
            try:
                geo_modifier[input_name] = route_obj
                print(f"[BLOSM] Set CAR_TRAIL GeoNodes input '{input_name}' to route curve: {route_obj.name}")
                configured = True
                break
            except Exception as e:
                print(f"[BLOSM] Failed to set input '{input_name}': {e}")

    if not configured:
        # Try to inspect the modifier's inputs more systematically
        if hasattr(geo_modifier, 'node_group') and geo_modifier.node_group:
            node_group = geo_modifier.node_group

            # Look for object input nodes in the node group
            for node in node_group.nodes:
                if node.bl_idname == 'GeometryNodeInputObject':
                    # Try to find the corresponding modifier input
                    for input_name in geo_modifier.keys():
                        try:
                            geo_modifier[input_name] = route_obj
                            print(f"[BLOSM] Set CAR_TRAIL GeoNodes input '{input_name}' to route curve: {route_obj.name}")
                            configured = True
                            break
                        except Exception:
                            pass
                    if configured:
                        break

    if not configured:
        print("[BLOSM] Warning: Could not configure CAR_TRAIL GeoNodes object input")
        print("[BLOSM] Available modifier inputs:")
        for key in geo_modifier.keys():
            print(f"   - {key}: {type(geo_modifier[key])}")
    else:
        print(f"[BLOSM] CAR_TRAIL GeoNodes configured successfully with route curve reference")


def import_assets(context: bpy.types.Context) -> Dict[str, Optional[str]]:
    summary: Dict[str, Optional[str]] = {key: None for key in _LAST_SUMMARY}
    scene = getattr(context, 'scene', None)

    route_mat_candidates = route_resolve.list_blend_datablocks(ROUTE_BLEND_PATH, 'materials')
    route_ng_candidates = route_resolve.list_blend_datablocks(ROUTE_BLEND_PATH, 'node_groups')
    build_ng_candidates = route_resolve.list_blend_datablocks(BUILD_BLEND_PATH, 'node_groups')
    build_mat_candidates = route_resolve.list_blend_datablocks(BUILD_BLEND_PATH, 'materials')
    beam_candidates = route_resolve.list_blend_datablocks(BEAM_BLEND_PATH, 'objects')

    # Only append materials and node_groups from ASSET_ROUTE, never route curve objects
    route_resolve.ensure_appended(ROUTE_BLEND_PATH, 'materials', route_mat_candidates)
    route_resolve.ensure_appended(ROUTE_BLEND_PATH, 'node_groups', route_ng_candidates)
    route_resolve.ensure_appended(BUILD_BLEND_PATH, 'node_groups', build_ng_candidates)
    route_resolve.ensure_appended(BUILD_BLEND_PATH, 'materials', build_mat_candidates)
    route_resolve.ensure_appended(BEAM_BLEND_PATH, 'objects', beam_candidates)

    route_mat = _prefer_name(route_mat_candidates, contains='route')
    route_ng = _prefer_name(route_ng_candidates, contains='route')
    build_ng = _prefer_name(build_ng_candidates, contains='build')
    build_mat = _prefer_name(build_mat_candidates, contains='build')

    # Import ASSET_CAR as collection using legacy object import
    car_collection = None

    print("[BLOSM] Fallback to legacy car object import")
    car_candidates = route_resolve.list_blend_datablocks(CAR_BLEND_PATH, 'objects')
    car_name = _prefer_name(car_candidates, contains='car')
    car_obj = route_resolve.resolve_object((car_name,) if car_name else None, context=context)
    if car_obj:
        # Create a collection for the legacy imported car object
        car_collection = bpy.data.collections.new("ASSET_CAR")
        if car_obj.name not in car_collection.objects.keys():
            car_collection.objects.link(car_obj)
        bpy.context.scene.collection.children.link(car_collection)

        # Ensure taxi sign object (if present in the asset) is also imported and parented
        # to the car so it appears on the roof.
        sign_candidates = [
            name for name in car_candidates
            if name and "taxi" in name.casefold()
        ]
        sign_name = _prefer_name(sign_candidates) if sign_candidates else None
        if sign_name:
            # Append the taxi sign object explicitly from ASSET_CAR.blend
            route_resolve.ensure_appended(CAR_BLEND_PATH, "objects", [sign_name])
            sign_obj = bpy.data.objects.get(sign_name)
            if sign_obj:
                # Link sign into ASSET_CAR collection if not already there
                if sign_obj.name not in car_collection.objects.keys():
                    try:
                        car_collection.objects.link(sign_obj)
                    except RuntimeError:
                        pass
                # Parent sign to the main car object while preserving world transform
                try:
                    sign_obj.parent = car_obj
                    sign_obj.matrix_parent_inverse = car_obj.matrix_world.inverted()
                except Exception:
                    pass

    if not car_collection:
        raise RouteAssetError('Car asset not available')

    # Ensure ASSET_CAR collection is linked at the top level of the scene
    if scene and car_collection.name not in scene.collection.children.keys():
        try:
            scene.collection.children.link(car_collection)
        except RuntimeError:
            pass

    # Process ASSET_BEAM if available
    beam_obj = None

    # Prefer registry-based beam import when available


    # Fallback to legacy object import if registry-based import fails
    if beam_obj is None:
        beam_name = _prefer_name(beam_candidates, contains='beam')
        beam_obj = route_resolve.resolve_object((beam_name,) if beam_name else None, context=context)

    if beam_obj:
        print(f"[BLOSM] Found ASSET_BEAM object: {beam_obj.name}")

        # Position beam at route start (same as car positioning logic)
        try:
            from mathutils import Matrix
            beam_obj.parent = None
            beam_obj.matrix_parent_inverse = Matrix.Identity(4)
        except Exception:
            pass

        start_empty = bpy.data.objects.get('Start')
        if start_empty:
            beam_obj.location = start_empty.location
            print(f"[BLOSM] ASSET_BEAM positioned at Start location: {start_empty.location}")
        else:
            # Position at origin if no Start object
            beam_obj.location = (0.0, 0.0, 1598.6958)  # Use beam's original Z-height
            beam_obj.rotation_euler = (0.0, 0.0, 0.0)
            print("[BLOSM] No Start object found, ASSET_BEAM positioned at origin")

        beam_obj.rotation_mode = 'XYZ'
        beam_obj.hide_viewport = False
        beam_obj.hide_render = False

        # Ensure beam lives in its own ASSET_BEAM collection
        beam_collection = bpy.data.collections.get("ASSET_BEAM")
        if beam_collection is None:
            beam_collection = bpy.data.collections.new("ASSET_BEAM")
            if scene and beam_collection.name not in scene.collection.children.keys():
                try:
                    scene.collection.children.link(beam_collection)
                except RuntimeError:
                    pass

        if beam_obj.name not in beam_collection.objects.keys():
            try:
                beam_collection.objects.link(beam_obj)
            except RuntimeError:
                pass

        try:
            beam_obj.hide_set(False)
        except AttributeError:
            pass
    else:
        print("[BLOSM] ASSET_BEAM not found or available")

    # Process ASSET_MARKERS if available
    markers_candidates = route_resolve.list_blend_datablocks(MARKERS_BLEND_PATH, 'collections')
    route_resolve.ensure_appended(MARKERS_BLEND_PATH, 'collections', markers_candidates)

    markers_name = _prefer_name(markers_candidates, contains='marker')
    markers_coll = None

    if markers_name:
        markers_coll = bpy.data.collections.get(markers_name)
        if markers_coll:
            print(f"[BLOSM] Found ASSET_MARKERS collection: {markers_name}")

            # Link collection to scene
            scene = getattr(context, 'scene', None)
            if scene and markers_coll.name not in scene.collection.children.keys():
                try:
                    scene.collection.children.link(markers_coll)
                    print(f"[BLOSM] ASSET_MARKERS collection linked to scene")
                except RuntimeError:
                    pass

            # Position MARKER_START at route start
            marker_start_obj = bpy.data.objects.get('MARKER_START')
            if marker_start_obj:
                try:
                    from mathutils import Matrix
                    marker_start_obj.parent = None
                    marker_start_obj.matrix_parent_inverse = Matrix.Identity(4)
                except Exception:
                    pass

                start_empty = bpy.data.objects.get('Start')
                if start_empty:
                    marker_start_obj.location = start_empty.location
                    print(f"[BLOSM] MARKER_START positioned at Start location: {start_empty.location}")
                else:
                    # Position at origin if no Start object
                    marker_start_obj.location = (0.0, 0.0, 0.0)
                    print("[BLOSM] No Start object found, MARKER_START positioned at origin")

                marker_start_obj.rotation_mode = 'XYZ'
                marker_start_obj.hide_viewport = False
                marker_start_obj.hide_render = False
            else:
                print("[BLOSM] MARKER_START not found in ASSET_MARKERS collection")

            # Position MARKER_END at route end
            marker_end_obj = bpy.data.objects.get('MARKER_END')
            if marker_end_obj:
                try:
                    from mathutils import Matrix
                    marker_end_obj.parent = None
                    marker_end_obj.matrix_parent_inverse = Matrix.Identity(4)
                except Exception:
                    pass

                end_empty = bpy.data.objects.get('End')
                if end_empty:
                    marker_end_obj.location = end_empty.location
                    print(f"[BLOSM] MARKER_END positioned at End location: {end_empty.location}")
                else:
                    # Position at origin if no End object
                    marker_end_obj.location = (0.0, 0.0, 0.0)
                    print("[BLOSM] No End object found, MARKER_END positioned at origin")

                marker_end_obj.rotation_mode = 'XYZ'
                marker_end_obj.hide_viewport = False
                marker_end_obj.hide_render = False
            else:
                print("[BLOSM] MARKER_END not found in ASSET_MARKERS collection")
        else:
            print(f"[BLOSM] ASSET_MARKERS collection '{markers_name}' not found after import")
    else:
        print("[BLOSM] ASSET_MARKERS collection not found or available")

    summary.update({
        'route_mat': route_mat,
        'route_ng': route_ng,
        'car_obj': car_obj.name if car_obj else None,
        'car_collection': car_collection.name,
        'bld_ng': build_ng,
        'bld_mat': build_mat,
        'beam_obj': beam_obj.name if beam_obj else None,
        'markers_coll': markers_coll.name if markers_coll else None,
    })

    _LAST_SUMMARY.update(summary)

    print(
        "[BLOSM] import_assets summary: "
        f"route_ng='{summary['route_ng']}', route_mat='{summary['route_mat']}', "
        f"car='{summary['car_obj']}', bld_ng='{summary['bld_ng']}', bld_mat='{summary['bld_mat']}', "
        f"beam='{summary['beam_obj']}', markers='{summary['markers_coll']}'"
    )
    return summary


def get_last_summary() -> Dict[str, Optional[str]]:
    return dict(_LAST_SUMMARY)


class BLOSM_OT_import_assets(Operator):
    bl_idname = "blosm.import_assets"
    bl_label = "Import Assets"
    bl_description = "Append BLOSM route assets into the current file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            import_assets(context)
        except RouteAssetError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        except Exception as exc:
            self.report({'ERROR'}, f"Asset import failed: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, "Assets ready")
        return {'FINISHED'}


class BLOSM_OT_assets_selfcheck(Operator):
    bl_idname = "blosm.assets_selfcheck"
    bl_label = "Assets Self-Check"
    bl_description = "Report presence and visibility of BLOSM route assets"
    bl_options = {'REGISTER'}

    def execute(self, context):
        summary = get_last_summary()
        route_ng = summary.get('route_ng')
        route_mat = summary.get('route_mat')
        build_ng = summary.get('bld_ng')
        build_mat = summary.get('bld_mat')
        car_name = summary.get('car_obj')
        beam_name = summary.get('beam_obj')
        markers_name = summary.get('markers_coll')

        route_ng_present = bool(route_ng and bpy.data.node_groups.get(route_ng))
        route_mat_present = bool(route_mat and bpy.data.materials.get(route_mat))
        build_ng_present = bool(build_ng and bpy.data.node_groups.get(build_ng))
        build_mat_present = bool(build_mat and bpy.data.materials.get(build_mat))
        car_obj = bpy.data.objects.get(car_name) if car_name else None
        car_present = car_obj is not None
        beam_obj = bpy.data.objects.get(beam_name) if beam_name else None
        beam_present = beam_obj is not None
        markers_coll = bpy.data.collections.get(markers_name) if markers_name else None
        markers_present = markers_coll is not None

        # Check for marker objects
        marker_start_obj = bpy.data.objects.get('MARKER_START')
        marker_end_obj = bpy.data.objects.get('MARKER_END')
        marker_start_present = marker_start_obj is not None
        marker_end_present = marker_end_obj is not None

        # Car should live in ASSET_CAR collection
        car_collection = bpy.data.collections.get('ASSET_CAR')
        car_in_collection = bool(car_collection and car_obj and car_obj in car_collection.objects)

        # Beam should live in ASSET_BEAM collection
        beam_collection = bpy.data.collections.get('ASSET_BEAM')
        beam_in_collection = bool(beam_collection and beam_obj and beam_obj in beam_collection.objects)

        car_visible = bool(car_obj and (not car_obj.hide_viewport) and (not car_obj.hide_render))
        beam_visible = bool(beam_obj and (not beam_obj.hide_viewport) and (not beam_obj.hide_render))
        marker_start_visible = bool(marker_start_obj and (not marker_start_obj.hide_viewport) and (not marker_start_obj.hide_render))
        marker_end_visible = bool(marker_end_obj and (not marker_end_obj.hide_viewport) and (not marker_end_obj.hide_render))

        print(
            f"[BLOSM] assets_selfcheck: route_ng='{route_ng}':{route_ng_present}, "
            f"route_mat='{route_mat}':{route_mat_present}, "
            f"bld_ng='{build_ng}':{build_ng_present}, "
            f"bld_mat='{build_mat}':{build_mat_present}, car='{car_name}':{car_present}, "
            f"beam='{beam_name}':{beam_present}, markers='{markers_name}':{markers_present}, "
            f"marker_start={marker_start_present}, marker_end={marker_end_present}, "
            f"car_in_collection={car_in_collection}, beam_in_collection={beam_in_collection}, "
            f"car_visible={car_visible}, beam_visible={beam_visible}, "
            f"marker_start_visible={marker_start_visible}, marker_end_visible={marker_end_visible}"
        )
        return {'FINISHED'}


_CLASSES = (
    BLOSM_OT_import_assets,
    BLOSM_OT_assets_selfcheck,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    # Defensive unregister: some classes may already have been removed by
    # Blender when disabling or reloading addons.
    for cls in reversed(_CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            # Class not registered or already unregistered
            continue
        except Exception:
            # Do not propagate shutdown errors
            continue
