"""Route animation driver helpers."""


from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import bpy
from mathutils import Matrix, Vector

from . import assets as route_assets
from . import nodes as route_nodes
from . import resolve as route_resolve
from .config import DEFAULT_CONFIG

# Constants from configuration
ROUTE_MODIFIER_NAME = route_nodes.ROUTE_MODIFIER_NAME
LEAD_OBJECT_NAME = DEFAULT_CONFIG.objects.lead_object_name
CAR_CONSTRAINT_NAME = DEFAULT_CONFIG.objects.car_constraint_name
LEAD_CONSTRAINT_NAME = DEFAULT_CONFIG.objects.lead_constraint_name
DAMPED_TRACK_NAME = DEFAULT_CONFIG.objects.damped_track_name
_DEFAULT_FLOAT_NAME = DEFAULT_CONFIG.animation.gn_offset_factor_socket
_START_OBJECT_NAME = DEFAULT_CONFIG.objects.start_marker_name

def _smoothstep(value: float) -> float:
    """Smoothstep function for keyframe interpolation."""
    value = float(value)
    if value < 0.0:
        value = 0.0
    elif value > 1.0:
        value = 1.0
    return value * value * (3.0 - 2.0 * value)


def _remove_existing_keyframes(id_data: Optional[bpy.types.ID], data_path: str) -> None:
    """Remove all existing keyframes for a given data path."""
    if not id_data:
        return
    animation_data = getattr(id_data, 'animation_data', None)
    if not animation_data:
        return
    action = animation_data.action
    if not action:
        return

    # Normalize data path for comparison (handle quote variations)
    # This ensures constraints["Name"] matches constraints['Name']
    norm_path = data_path.replace("'", '"')

    # Find and remove all fcurves for this data path
    for fcurve in list(action.fcurves):
        # Check both exact match and normalized match
        fc_path = fcurve.data_path.replace("'", '"')
        if fcurve.data_path == data_path or fc_path == norm_path:
            action.fcurves.remove(fcurve)


def _create_animation_keyframes(
    id_data: Optional[bpy.types.ID],
    data_path: str,
    start_frame: int,
    end_frame: int,
    lead_frames: int = 0,
    *,
    use_lead: bool = False,
) -> bool:
    """Create keyframes for animation using Blender's bezier interpolation.

    Args:
        id_data: Object to animate
        data_path: Property path to animate
        start_frame: Start frame for animation
        end_frame: End frame for animation
        lead_frames: Lead frames offset for CAR_LEAD
        use_lead: Whether to apply lead frames offset (for CAR_LEAD only)

    Returns:
        True if keyframes were created successfully
    """
    if not id_data or end_frame <= start_frame:
        return False

    try:
        # Ensure animation data exists
        id_data.animation_data_create()
    except Exception:
        return False

    # Remove existing keyframes
    _remove_existing_keyframes(id_data, data_path)

    # Create action if needed
    if not id_data.animation_data.action:
        id_data.animation_data.action = bpy.data.actions.new(f"{id_data.name}_action")

    # Calculate actual start with lead frames (for CAR_LEAD only)
    actual_start = start_frame - (lead_frames if use_lead else 0)
    
    print(f"[BLOSM] Animate {id_data.name}: path={data_path} start={start_frame}(adj={actual_start}) end={end_frame}")

    # Set start/end values using robust constraint access
    start_val = 0.01 if use_lead else 0.0
    end_val = 1.01 if use_lead else 1.0
    try:
        # Robust constraint data path parsing and property access
        success = False
        
        # Handle constraint properties with enhanced parsing
        if data_path.startswith('constraints[') and '.offset_factor' in data_path:
            # Simplified robust constraint parsing
            constraint_name = None
            if 'constraints["' in data_path:
                constraint_name = data_path.split('constraints["')[1].split('"]')[0]
            elif "constraints['" in data_path:
                constraint_name = data_path.split("constraints['")[1].split("']")[0]
            
            if constraint_name:
                target_constraint = id_data.constraints.get(constraint_name)
                property_name = 'offset_factor'
                
                if target_constraint and hasattr(target_constraint, property_name):
                    # Set start value
                    setattr(target_constraint, property_name, start_val)
                    id_data.keyframe_insert(data_path=data_path, frame=actual_start)

                    # Set end value
                    setattr(target_constraint, property_name, end_val)
                    id_data.keyframe_insert(data_path=data_path, frame=end_frame)
                    success = True
                    print(f"[BLOSM] Created keyframes for constraint '{target_constraint.name}.{property_name}'")
                else:
                    print(f"[BLOSM] Constraint '{constraint_name}' not found or invalid property")
            else:
                # Fallback to existing logic if simple parsing fails
                print(f"[BLOSM] Complex path, falling back to path_resolve: {data_path}")
                # ... existing logic ...
        
        if not success:
            # Handle non-constraint properties or fallback
            try:
                # Set start value
                id_data.path_resolve(data_path).set(start_val)
                id_data.keyframe_insert(data_path=data_path, frame=actual_start)

                # Set end value
                id_data.path_resolve(data_path).set(end_val)
                id_data.keyframe_insert(data_path=data_path, frame=end_frame)
                success = True
            except Exception as prop_error:
                print(f"[BLOSM] Error setting property values: {prop_error}")
        
        if not success:
            return False
            
    except Exception as e:
        print(f"[BLOSM] Error setting keyframe values: {e}")
        return False

    # Get the created fcurve and set interpolation to bezier
    animation_data = getattr(id_data, 'animation_data', None)
    if animation_data and animation_data.action:
        for fcurve in animation_data.action.fcurves:
            if fcurve.data_path == data_path and fcurve.array_index == 0:
                # Set interpolation to bezier for smooth curves
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'BEZIER'
                break

    return True



@dataclass(frozen=True)
class DriverSetupResult:
    route: Optional[bpy.types.Object]
    lead_driver: bool
    car_driver: bool
    gn_driver: bool
    lead_constraint: Optional[bpy.types.Constraint]
    car_constraint: Optional[bpy.types.Constraint]
    gn_socket_name: Optional[str]
    lead_follow_ok: bool
    car_follow_ok: bool
    car_damped_ok: bool


def _is_float_socket(socket_type: Optional[str]) -> bool:
    if not socket_type:
        return False
    lowered = socket_type.casefold()
    return "float" in lowered or lowered == "value"


def _matches_socket(socket_type: Optional[str], expected: Optional[str]) -> bool:
    if expected is None:
        return True
    if expected == "FLOAT":
        return _is_float_socket(socket_type)
    if not socket_type:
        return False
    return socket_type.casefold() == expected.casefold()


def _find_gn_input_index(
    node_group: Optional[bpy.types.NodeTree],
    name_or_type: str = "FLOAT",
    prefer_name: str = _DEFAULT_FLOAT_NAME,
) -> Optional[int]:
    if not node_group:
        return None
    fallback_by_name = None
    fallback_by_type = None
    prefer_norm = "".join(ch for ch in (prefer_name or "") if ch.isalnum()).casefold()
    for idx, socket_type, socket_name in route_nodes._iter_group_inputs(node_group):
        name_norm = "".join(ch for ch in (socket_name or "") if ch.isalnum()).casefold()
        if prefer_norm and name_norm == prefer_norm:
            if _matches_socket(socket_type, name_or_type):
                return idx
            if fallback_by_name is None:
                fallback_by_name = idx
        if fallback_by_type is None and _matches_socket(socket_type, name_or_type):
            fallback_by_type = idx
    if fallback_by_type is not None:
        return fallback_by_type
    if fallback_by_name is not None:
        return fallback_by_name
    return None


def _resolve_gn_input_property(
    modifier: Optional[bpy.types.Modifier],
    index: Optional[int],
) -> Optional[str]:
    if modifier is None or index is None:
        return None
    node_group = getattr(modifier, 'node_group', None)
    if not node_group:
        return None
    interface = getattr(node_group, 'interface', None)
    if interface is not None:
        items_tree = getattr(interface, 'items_tree', None)
        if items_tree is not None:
            count = 0
            for item in items_tree:
                if getattr(item, 'item_type', None) == 'SOCKET' and getattr(item, 'in_out', None) == 'INPUT':
                    if count == index:
                        identifier = getattr(item, 'identifier', None)
                        if identifier and identifier in modifier.keys():
                            return identifier
                        break
                    count += 1
    inputs = getattr(node_group, 'inputs', None)
    if inputs and 0 <= index < len(inputs):
        socket = inputs[index]
        identifier = getattr(socket, 'identifier', None)
        if identifier and identifier in modifier.keys():
            return identifier
    candidate = f'Input_{index}'
    if candidate in modifier.keys():
        return candidate
    return None


def _ensure_follow_constraint(obj: Optional[bpy.types.Object], name: str) -> Optional[bpy.types.Constraint]:
    if obj is None:
        return None
    for constraint in obj.constraints:
        if constraint.type == 'FOLLOW_PATH' and constraint.name == name:
            return constraint
    try:
        constraint = obj.constraints.new('FOLLOW_PATH')
    except Exception:
        return None
    constraint.name = name
    return constraint


def _configure_follow_path(constraint: Optional[bpy.types.Constraint], target: Optional[bpy.types.Object]) -> None:
    if constraint is None:
        return
    constraint.target = target
    
    # Configure Curve Follow
    if hasattr(constraint, 'use_curve_follow'):
        constraint.use_curve_follow = True
        
    # Configure Fixed Position (Crucial for offset_factor animation)
    # We attempt to set both legacy and new attributes to ensure compatibility
    fixed_set = False
    
    # Try use_fixed_location (Newer Blender)
    if hasattr(constraint, 'use_fixed_location'):
        constraint.use_fixed_location = True
        fixed_set = True
        
    # Try use_fixed_position (Older Blender)
    if hasattr(constraint, 'use_fixed_position'):
        constraint.use_fixed_position = True
        fixed_set = True
        
    if not fixed_set:
        print(f"[BLOSM] WARNING: Could not set Fixed Position on {constraint.name} (properties not found)")

    # Configure Axes
    if hasattr(constraint, 'forward_axis'):
        constraint.forward_axis = 'FORWARD_X'
    if hasattr(constraint, 'up_axis'):
        constraint.up_axis = 'UP_Z'
        
    print(f"[BLOSM] Configured Follow Path '{constraint.name}': Target={target.name if target else 'None'}, FixedPos={fixed_set}")

def _remove_drivers_and_keyframes(id_data: Optional[bpy.types.ID], data_path: Optional[str]) -> None:
    """Remove both drivers and keyframes for a given data path."""
    if not id_data:
        return
    animation_data = getattr(id_data, 'animation_data', None)
    if not animation_data:
        return

    # Remove drivers
    if data_path:
        for fcurve in list(animation_data.drivers):
            if fcurve.data_path == data_path and fcurve.array_index == 0:
                try:
                    animation_data.drivers.remove(fcurve)
                except Exception:
                    pass

        # Remove keyframes
        _remove_existing_keyframes(id_data, data_path)
    else:
        # Remove all drivers and keyframes if no specific path
        while animation_data.drivers:
            try:
                animation_data.drivers.remove(animation_data.drivers[0])
            except Exception:
                pass

        if animation_data.action:
            while animation_data.action.fcurves:
                try:
                    animation_data.action.fcurves.remove(animation_data.action.fcurves[0])
                except Exception:
                    pass


def _assign_scene_driver_var(
    driver: bpy.types.Driver,
    name: str,
    scene: bpy.types.Scene,
    data_path: str,
) -> None:
    var = driver.variables.new()
    var.name = name
    var.type = 'SINGLE_PROP'
    target = var.targets[0]
    target.id_type = 'SCENE'
    target.id = scene
    target.data_path = data_path


def _resolve_route_object(scene: Optional[bpy.types.Scene]) -> Optional[bpy.types.Object]:
    candidates: list[bpy.types.Object] = []
    if scene is not None:
        try:
            candidates.extend(scene.objects)
        except Exception:
            pass
    for obj in bpy.data.objects:
        if obj not in candidates:
            candidates.append(obj)
    for obj in candidates:
        if not obj or getattr(obj, 'type', None) != 'CURVE':
            continue
        modifier = obj.modifiers.get(route_nodes.ROUTE_MODIFIER_NAME)
        if modifier and modifier.type == 'NODES':
            return obj
    return None


def _ensure_route_trace_keyframes(scene: Optional[bpy.types.Scene]) -> bool:
    """Ensure RouteTrace GN offset factor is static (no animation).

    Older versions created keyframes on the GeoNodes input to animate the route
    drawing on. For the rollback branch we now require this value to stay at
    1.0 with no drivers or keyframes so that behaviour is fully deterministic.
    """
    scene = scene or getattr(bpy.context, 'scene', None)
    if scene is None:
        return False

    route_obj = _resolve_route_object(scene)
    if route_obj is None:
        return False

    modifier = route_obj.modifiers.get(route_nodes.ROUTE_MODIFIER_NAME)
    if modifier is None or modifier.type != 'NODES':
        return False

    node_group = getattr(modifier, 'node_group', None)
    if node_group is None:
        return False

    # We no longer animate this value; just resolve the GN input once and
    # force it to 1.0 with no animation data attached.
    prop_name = None

    # Method 1: Try the existing resolution function
    index = _find_gn_input_index(node_group, 'FLOAT', _DEFAULT_FLOAT_NAME)
    if index is not None:
        prop_name = _resolve_gn_input_property(modifier, index)

    # Method 2: If not found, try Socket_10 directly (common fallback)
    if not prop_name and 'Socket_10' in modifier.keys():
        prop_name = 'Socket_10'

    if not prop_name:
        print("[BLOSM] Warning: Could not resolve RouteTrace GN offset property")
        return False

    # Remove any existing drivers/keyframes and force a constant value of 1.0
    data_path = f'modifiers["{modifier.name}"]["{prop_name}"]'
    _remove_drivers_and_keyframes(route_obj, data_path)
    try:
        modifier[prop_name] = 1.0
        print(f"[BLOSM] RouteTrace offset factor set to static 1.0 on '{prop_name}' (no animation)")
        return True
    except Exception as e:
        print(f"[BLOSM] Error setting static RouteTrace property: {e}")
        return False


def _ensure_follow_keyframes(
    constraint: Optional[bpy.types.Constraint],
    scene: Optional[bpy.types.Scene],
    *,
    use_lead: bool = False,
    force: bool = False,
) -> bool:
    """Create keyframes for Follow Path constraint animation."""
    if constraint is None or scene is None:
        return False
    id_data = constraint.id_data
    if id_data is None:
        return False

    # Check if this constraint type supports offset_factor
    if not hasattr(constraint, 'offset_factor'):
        print(f"[BLOSM] Constraint {constraint.name} of type {constraint.type} doesn't support offset_factor, skipping keyframes")
        return False

    data_path = f'constraints["{constraint.name}"].offset_factor'

    # Check if KEYFRAMES already exist for this property
    # We want to preserve manual edits, so if fcurves exist, we assume they are correct.
    # UNLESS force is True (e.g. from UI update)
    if not force:
        animation_data = getattr(id_data, 'animation_data', None)
        if animation_data and animation_data.action:
            for fcurve in animation_data.action.fcurves:
                if fcurve.data_path == data_path:
                    print(f"[BLOSM] Keyframes already exist for {constraint.name}, preserving manual edits")
                    return True

    # Note: We do NOT preserve drivers. If a driver exists, we want to replace it 
    # with keyframes to allow manual editing (as requested).
    # _remove_drivers_and_keyframes will handle the cleanup.

    # Get animation parameters from scene properties
    start_frame = getattr(scene, 'blosm_anim_start', 1)
    end_frame = getattr(scene, 'blosm_anim_end', 250)
    lead_frames = getattr(scene, 'blosm_lead_frames', 30)

    # Remove existing drivers and keyframes
    _remove_drivers_and_keyframes(id_data, data_path)

    # Create keyframes - CAR_LEAD gets lead frames offset, ASSET_CAR doesn't
    return _create_animation_keyframes(
        id_data, data_path,
        start_frame=start_frame,
        end_frame=end_frame,
        lead_frames=lead_frames,
        use_lead=use_lead  # Only True for CAR_LEAD
    )




def ensure_follow_keyframes(
    scene: Optional[bpy.types.Scene] = None,
    *,
    car_constraint: Optional[bpy.types.Constraint] = None,
    lead_constraint: Optional[bpy.types.Constraint] = None,
) -> dict[str, bool]:
    """Create keyframes for Follow Path constraints."""
    scene = scene or getattr(bpy.context, "scene", None)
    results = {"car": False, "lead": False}
    if scene is None:
        return results
    if lead_constraint is None:
        # Check for both RouteLead (creation name) and CAR_LEAD (final name)
        lead_obj = bpy.data.objects.get(LEAD_OBJECT_NAME) or bpy.data.objects.get('CAR_LEAD')
        if lead_obj:
            for constraint in lead_obj.constraints:
                if constraint.type == 'FOLLOW_PATH' and constraint.name == LEAD_CONSTRAINT_NAME:
                    lead_constraint = constraint
                    break
    if car_constraint is None:
        car_obj = _resolve_car_object(context=scene)
        if car_obj:
            for constraint in car_obj.constraints:
                if constraint.type == 'FOLLOW_PATH' and constraint.name == CAR_CONSTRAINT_NAME:
                    car_constraint = constraint
                    break
    results["lead"] = _ensure_follow_keyframes(lead_constraint, scene, use_lead=True)
    results["car"] = _ensure_follow_keyframes(car_constraint, scene, use_lead=False)
    return results



def force_follow_keyframes(
    scene: Optional[bpy.types.Scene] = None,
    *,
    car_constraint: Optional[bpy.types.Constraint] = None,
    lead_constraint: Optional[bpy.types.Constraint] = None,
) -> dict[str, bool]:
    """Force creation of all animation keyframes."""
    scene = scene or getattr(bpy.context, 'scene', None)
    results = {'car': False, 'lead': False, 'route': False}
    if scene is None:
        return results

    # MARKER_END Scale Animation (148-156)
    marker_end_name = DEFAULT_CONFIG.objects.end_marker_name or 'MARKER_END'
    marker_end = bpy.data.objects.get(marker_end_name)
    if marker_end:
        try:
            if not marker_end.animation_data:
                marker_end.animation_data_create()
            
            # Remove existing scale keyframes
            if marker_end.animation_data.action:
                for fc in list(marker_end.animation_data.action.fcurves):
                    if fc.data_path == "scale":
                        marker_end.animation_data.action.fcurves.remove(fc)

            # Keyframe 1: Frame 148, Scale (20, 20, 20)
            marker_end.scale = (20.0, 20.0, 20.0)
            marker_end.keyframe_insert(data_path="scale", frame=148)

            # Keyframe 2: Frame 156, Scale (0, 0, 0)
            marker_end.scale = (0.0, 0.0, 0.0)
            marker_end.keyframe_insert(data_path="scale", frame=156)
            
            print(f"[BLOSM] Created scale animation for {marker_end_name} (148-156)")
        except Exception as e:
            print(f"[BLOSM] Failed to animate {marker_end_name}: {e}")

    if lead_constraint is None:
        # Check for both RouteLead (creation name) and CAR_LEAD (final name)
        lead_obj = bpy.data.objects.get(LEAD_OBJECT_NAME) or bpy.data.objects.get('CAR_LEAD')
        if lead_obj:
            for constraint in lead_obj.constraints:
                if constraint.type == 'FOLLOW_PATH' and constraint.name == LEAD_CONSTRAINT_NAME:
                    lead_constraint = constraint
                    break

    if car_constraint is None:
        car_obj = _resolve_car_object(context=scene)
        if car_obj:
            print(f"[BLOSM] Resolved car object: {car_obj.name}")
            for constraint in car_obj.constraints:
                print(f"[BLOSM] Checking constraint: {constraint.name} ({constraint.type}) vs {CAR_CONSTRAINT_NAME}")
                if constraint.type == 'FOLLOW_PATH' and constraint.name == CAR_CONSTRAINT_NAME:
                    car_constraint = constraint
                    print(f"[BLOSM] Found car constraint: {constraint.name}")
                    break
        else:
            print("[BLOSM] Failed to resolve car object")

    results['lead'] = _ensure_follow_keyframes(lead_constraint, scene, use_lead=True, force=True)
    results['car'] = _ensure_follow_keyframes(car_constraint, scene, use_lead=False, force=True)
    results['route'] = _ensure_route_trace_keyframes(scene)

    # Ensure Damped Track constraint exists on ASSET_CAR pointing to CAR_LEAD
    lead_obj = bpy.data.objects.get(LEAD_OBJECT_NAME) or bpy.data.objects.get('CAR_LEAD')
    car_obj = _resolve_car_object(context=scene)
    if lead_obj and car_obj:
        damped_track = _ensure_damped_track(car_obj, lead_obj)
        if damped_track:
            print(f"[BLOSM] Damped Track constraint ensured on ASSET_CAR -> CAR_LEAD")
        else:
            print(f"[BLOSM] WARNING Failed to create Damped Track constraint")

    return results

def _ensure_damped_track(car_obj: Optional[bpy.types.Object], lead_obj: Optional[bpy.types.Object]) -> Optional[bpy.types.Constraint]:
    if car_obj is None or lead_obj is None:
        return None
    for constraint in car_obj.constraints:
        if constraint.type == 'DAMPED_TRACK' and constraint.name == DAMPED_TRACK_NAME:
            damped = constraint
            break
    else:
        try:
            damped = car_obj.constraints.new('DAMPED_TRACK')
        except Exception:
            return None
        damped.name = DAMPED_TRACK_NAME
    damped.target = lead_obj
    try:
        damped.track_axis = 'TRACK_X'
    except Exception:
        pass
    try:
        damped.up_axis = 'UP_Z'
    except Exception:
        pass
    return damped


def _ensure_or_create_lead(
    context: bpy.types.Context,
    start_obj: Optional[bpy.types.Object],
    car_obj: Optional[bpy.types.Object],
) -> Optional[bpy.types.Object]:
    # Check for both RouteLead (creation name) and CAR_LEAD (final name)
    lead = bpy.data.objects.get(LEAD_OBJECT_NAME) or bpy.data.objects.get('CAR_LEAD')
    if lead is None:
        lead = bpy.data.objects.new(LEAD_OBJECT_NAME, None)
        lead.empty_display_type = 'PLAIN_AXES'
        lead.empty_display_size = 2.0
        context.scene.collection.objects.link(lead)
    if start_obj:
        try:
            lead.matrix_world = start_obj.matrix_world.copy()
        except Exception:
            lead.rotation_euler = getattr(start_obj, 'rotation_euler', lead.rotation_euler)
    elif car_obj:
        lead.rotation_euler = getattr(car_obj, 'rotation_euler', lead.rotation_euler)
    # Keep lead at the start position; only enforce rotation mode/selection here.
    lead.rotation_mode = 'XYZ'
    lead.select_set(False)
    return lead


def _resolve_car_object(
    provided: Optional[bpy.types.Object] = None,
    *,
    context: Optional[bpy.types.Context] = None,
) -> Optional[bpy.types.Object]:
    if provided:
        return provided
        
    # Priority 1: Check for the configured car object name in the scene
    # This respects the current scene state (and any manual renames/creations)
    default_name = DEFAULT_CONFIG.objects.car_object_name
    existing_obj = bpy.data.objects.get(default_name)
    if existing_obj:
        return existing_obj

    # Priority 2: Use asset resolution logic (which might load from library)
    summary = route_assets.get_last_summary()
    preferred = summary.get('car_obj') if summary else None
    
    resolved = route_resolve.resolve_object((preferred,) if preferred else None, context=context)
    if resolved:
        return resolved
        
    return None


def _setup_route_animation_drivers(
    context: bpy.types.Context,
    *,
    route_obj: Optional[bpy.types.Object] = None,
    lead_obj: Optional[bpy.types.Object] = None,
    car_obj: Optional[bpy.types.Object] = None,
) -> DriverSetupResult:
    scene = getattr(context, 'scene', None)
    if not scene:
        return DriverSetupResult(route=None, lead_driver=False, car_driver=False, gn_driver=False, lead_constraint=None, car_constraint=None, gn_socket_name=None, lead_follow_ok=False, car_follow_ok=False, car_damped_ok=False)

    route_obj = route_obj or route_resolve.resolve_route_obj(context)
    if route_obj is None:
        return DriverSetupResult(route=None, lead_driver=False, car_driver=False, gn_driver=False, lead_constraint=None, car_constraint=None, gn_socket_name=None, lead_follow_ok=False, car_follow_ok=False, car_damped_ok=False)
    if hasattr(route_obj.data, 'use_path') and getattr(route_obj.data, 'use_path', True) is not True:
        route_obj.data.use_path = True

    try:
        ensure_summary = route_nodes.ensure_route_nodes(context)
        if isinstance(ensure_summary, dict):
            ensured_route = ensure_summary.get('route_obj')
            if isinstance(ensured_route, bpy.types.Object):
                route_obj = ensured_route
    except Exception as exc:
        print(f"[BLOSM] WARN route_nodes_ensure: {exc}")

    start_obj = bpy.data.objects.get(_START_OBJECT_NAME)
    car_obj = _resolve_car_object(car_obj, context=context)
    if start_obj and car_obj:
        try:
            car_obj.parent = None
            car_obj.matrix_parent_inverse = Matrix.Identity(4)
        except Exception:
            pass
        try:
            car_obj.matrix_world = start_obj.matrix_world.copy()
        except Exception:
            car_obj.location = start_obj.location
            try:
                car_obj.rotation_euler = start_obj.rotation_euler
            except Exception:
                pass
    lead_obj = _ensure_or_create_lead(context, start_obj, car_obj if car_obj else None)

    if car_obj:
        car_obj.rotation_mode = 'XYZ'
        car_obj.hide_viewport = False
        car_obj.hide_render = False
        try:
            car_obj.hide_set(False)
        except AttributeError:
            pass
        # Preserve XY placement (from Start empty); only normalize height if possible.
        try:
            loc = list(car_obj.location)
            loc[2] = 1.5
            car_obj.location = tuple(loc)
        except Exception:
            pass
    damped_track = _ensure_damped_track(car_obj, lead_obj)

    lead_constraint = _ensure_follow_constraint(lead_obj, LEAD_CONSTRAINT_NAME)
    car_constraint = _ensure_follow_constraint(car_obj, CAR_CONSTRAINT_NAME)
    _configure_follow_path(lead_constraint, route_obj)
    _configure_follow_path(car_constraint, route_obj)

    if lead_constraint:
        lead_constraint.offset_factor = 0.0
    if car_constraint:
        car_constraint.offset_factor = 0.0

    lead_driver = _ensure_follow_keyframes(lead_constraint, scene, use_lead=True)
    car_driver = _ensure_follow_keyframes(car_constraint, scene, use_lead=False)

    modifier = route_obj.modifiers.get(route_nodes.ROUTE_MODIFIER_NAME) if route_obj else None
    gn_socket_name = None
    if modifier and modifier.type == 'NODES' and modifier.node_group:
        gn_index = _find_gn_input_index(modifier.node_group, 'FLOAT', _DEFAULT_FLOAT_NAME)
        gn_socket_name = _resolve_gn_input_property(modifier, gn_index)
    gn_driver = bool(modifier and modifier.type == 'NODES' and modifier.node_group)

    lead_follow_ok = bool(
        lead_constraint
        and lead_constraint.target is route_obj
        and getattr(lead_constraint, 'use_fixed_position', True)
    )
    car_follow_ok = bool(
        car_constraint
        and car_constraint.target is route_obj
        and getattr(car_constraint, 'use_fixed_position', True)
    )

    # ASSET_CAR should have Damped Track constraint to CAR_LEAD
    track_ok = bool(
        damped_track
        and getattr(damped_track, 'target', None) is lead_obj
        and getattr(damped_track, 'track_axis', 'TRACK_X') == 'TRACK_X'
    )
    up_axis_ok = True
    if damped_track and hasattr(damped_track, 'up_axis'):
        up_axis_ok = getattr(damped_track, 'up_axis', 'UP_Z') == 'UP_Z'
    car_damped_ok = track_ok and up_axis_ok

    lead_target = (0.0, 0.0, 1.5)
    lead_at_target = False
    if lead_obj:
        try:
            lead_at_target = all(abs(float(coord) - target) <= 1e-4 for coord, target in zip(lead_obj.location, lead_target))
        except Exception:
            lead_at_target = False
    if start_obj and lead_obj and not lead_at_target:
        try:
            lead_pos = Vector(lead_obj.matrix_world.translation)
            start_pos = Vector(start_obj.matrix_world.translation)
            if (lead_pos - start_pos).length > 0.05:
                print('[BLOSM] WARN route_lead_start_offset')
        except Exception:
            pass

    print(
        f"[BLOSM] route_anim_setup: lead_fp={lead_follow_ok}, car_fp={car_follow_ok}, car_dt={car_damped_ok}, lead_drv={lead_driver}, car_drv={car_driver}"
    )
    print(f"[BLOSM] route_anim_setup: CAR_LEAD FollowPath={lead_follow_ok}, ASSET_CAR DampedTrack={car_damped_ok}")

    return DriverSetupResult(
        route=route_obj,
        lead_driver=lead_driver,
        car_driver=car_driver,
        gn_driver=gn_driver,
        lead_constraint=lead_constraint,
        car_constraint=car_constraint,
        gn_socket_name=gn_socket_name,
        lead_follow_ok=lead_follow_ok,
        car_follow_ok=car_follow_ok,
        car_damped_ok=car_damped_ok,
    )


__all__ = (
    'DriverSetupResult',
    '_find_gn_input_index',
    '_resolve_gn_input_property',
    '_setup_route_animation_drivers',
    'LEAD_OBJECT_NAME',
    'LEAD_CONSTRAINT_NAME',
    'CAR_CONSTRAINT_NAME',
    'DAMPED_TRACK_NAME',
)

