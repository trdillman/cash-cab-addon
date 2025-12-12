"""
CashCab Route Import - Blender Addon
Import routes and OpenStreetMap data for animation.
"""

bl_info = {
    "name": "CashCab Route Import",
  "version": (2, 2, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > CashCab",
    "description": "Fetch routes and import OpenStreetMap data with Toronto Islands mesh import for CashCab animation",
    "category": "Import",
    "support": "COMMUNITY"
}

try:
    import bpy  # type: ignore
    # Verify Blender runtime by requiring a known API symbol
    try:
        from bpy.app.handlers import persistent  # type: ignore
        _IN_BLENDER = True
    except Exception:
        bpy = None  # type: ignore
        _IN_BLENDER = False
except Exception:
    bpy = None  # type: ignore
    _IN_BLENDER = False
# Defer Blender-dependent imports to Blender runtimes only


_classes = tuple()

routecam_unified = None

if _IN_BLENDER:
    from . import gui
    from .route.fetch_operator import BLOSM_OT_FetchRouteMap, BLOSM_OT_ExtendCityArea
    from .osm.import_operator import BLOSM_OT_ImportData
    from .app import blender as blenderApp
    from .setup import render_settings # Import render settings module

    # RouteCam Integration (Unified Package)
    try:
        from . import routecam
    except Exception as _rc_exc:
        routecam = None
        print(f"[CashCab] RouteCam package not available: {_rc_exc}")

    # Register route operators from route module
    from .route import assets as route_assets
    from .route import nodes as route_nodes
    # Main operator classes
    _classes = (
        BLOSM_OT_ImportData,
        BLOSM_OT_FetchRouteMap,
        BLOSM_OT_ExtendCityArea,
        render_settings.BLOSM_OT_ApplyRenderSettings, # Register Apply Render Settings operator
    )

def _update_animation_properties(self, context):
    """Update keyframes when animation frame properties change"""
    try:
        # Import here to avoid circular imports
        from .route.anim import force_follow_keyframes
        force_follow_keyframes(context.scene)
    except Exception as e:
        print(f"[CashCab] Warning: Could not update animation keyframes: {e}")

def register():
    """Register addon components when running inside Blender.

    Outside Blender this is a no-op to allow importing pure-Python modules
    (e.g., during unit tests).
    """
    print(f"[DEBUG] addon.register called. _IN_BLENDER={_IN_BLENDER}")
    if not _IN_BLENDER:
        # Allow tests and tooling to import package safely
        return

    # Register main route operator
    for cls in _classes:
        bpy.utils.register_class(cls)

    # Register route asset operators
    route_assets.register()
    route_nodes.register()

    # Register RouteCam (Unified Package)
    if routecam is not None:
        try:
            routecam.register()
            print("[CashCab] RouteCam registered")
        except Exception as rc_exc:
            print(f"[CashCab] RouteCam registration failed: {rc_exc}")



    # Register GUI (panels, properties, operators)
    gui.register()

    # Register animation properties for route drivers
    # Car animation (FOLLOW_PATH constraint)
    bpy.types.Scene.blosm_anim_start = bpy.props.IntProperty(
        name="Car Start Frame",
        description="First frame of car animation",
        default=15,
        min=1,
        update=_update_animation_properties
    )

    bpy.types.Scene.blosm_anim_end = bpy.props.IntProperty(
        name="Car End Frame",
        description="Last frame of car animation",
        default=150,
        min=1,
        update=_update_animation_properties
    )

    bpy.types.Scene.blosm_lead_frames = bpy.props.IntProperty(
        name="Lead Frames",
        description="Number of frames the lead object stays ahead of the car",
        default=2,
        min=0,
        update=_update_animation_properties
    )

    # Route trace animation (Geometry Nodes driver)
    bpy.types.Scene.blosm_route_start = bpy.props.IntProperty(
        name="Route Trace Start Frame",
        description="First frame of route trace animation (geometry nodes)",
        default=15,
        min=1,
        update=_update_animation_properties
    )

    bpy.types.Scene.blosm_car_trail_start_adjust = bpy.props.FloatProperty(
        name="CAR_TRAIL Start Adjust",
        description="Driver trim: maps -1..1 to approx -0.01..0.01 for bevel_factor_start",
        default=0.0,
        min=-100.0,
        max=100.0,
        soft_min=-10.0,
        soft_max=10.0,
    )

    bpy.types.Scene.blosm_car_trail_end_adjust = bpy.props.FloatProperty(
        name="CAR_TRAIL End Adjust",
        description="Driver trim: maps -1..1 to approx -0.01..0.01 for bevel_factor_end",
        default=0.0,
        min=-100.0,
        max=100.0,
        soft_min=-10.0,
        soft_max=10.0,
    )

    bpy.types.Scene.blosm_car_trail_tail_shift = bpy.props.FloatProperty(
        name="CAR_TRAIL Tail Shift",
        description="Shared driver shift applied to both bevel_factor_start and bevel_factor_end",
        default=0.0,
        min=-100.0,
        max=100.0,
        soft_min=-10.0,
        soft_max=10.0,
    )

    bpy.types.Scene.blosm_route_end = bpy.props.IntProperty(
        name="Route Trace End Frame",
        description="Last frame of route trace animation (geometry nodes)",
        default=150,
        min=1,
        update=_update_animation_properties
    )

    bpy.types.Scene.blosm_base_start = bpy.props.FloatProperty(
        name="Base Start",
        description="Driver variable for custom animations (user-definable)",
        default=0.0
    )

    bpy.types.Scene.blosm_base_end = bpy.props.FloatProperty(
        name="Base End",
        description="Driver variable for custom animations (user-definable)",
        default=1.0
    )

    bpy.types.Scene.blosm_route_object_name = bpy.props.StringProperty(
        name="Route Object Name",
        description="Last BLOSM route curve name",
        default=""
    )

    bpy.types.Scene.blosm_car_trail_start_adjust = bpy.props.FloatProperty(
        name="CAR_TRAIL Start Adjust",
        description="Car trail window trim for bevel_factor_start",
        default=0.0,
        min=-100.0,
        max=100.0,
        soft_min=-10.0,
        soft_max=10.0,
    )

    bpy.types.Scene.blosm_car_trail_end_adjust = bpy.props.FloatProperty(
        name="CAR_TRAIL End Adjust",
        description="Car trail window trim for bevel_factor_end",
        default=0.0,
        min=-100.0,
        max=100.0,
        soft_min=-10.0,
        soft_max=10.0,
    )

    bpy.types.Scene.blosm_car_trail_tail_shift = bpy.props.FloatProperty(
        name="CAR_TRAIL Tail Shift",
        description="Shared driver shift applied to both bevel_factor_start and bevel_factor_end",
        default=0.0,
        min=-100.0,
        max=100.0,
        soft_min=-10.0,
        soft_max=10.0,
    )

    print("[CashCab] Route import addon registered")


def unregister():
    """Unregister addon and cleanup (Blender only)."""
    if not _IN_BLENDER:
        return

    # Unregister animation properties first
    for attr in (
        "blosm_anim_start",
        "blosm_anim_end",
        "blosm_lead_frames",
        "blosm_route_start",
        "blosm_route_end",
        "blosm_base_start",
        "blosm_base_end",
        "blosm_car_trail_start_adjust",
        "blosm_car_trail_end_adjust",
        "blosm_car_trail_tail_shift",
    ):
        if hasattr(bpy.types.Scene, attr):
            try:
                delattr(bpy.types.Scene, attr)
            except Exception:
                pass

    if hasattr(bpy.types.Scene, 'blosm_route_object_name'):
        try:
            del bpy.types.Scene.blosm_route_object_name
        except Exception:
            pass

    # Unregister GUI
    try:
        gui.unregister()
    except Exception:
        pass

    # Unregister RouteCam
    if routecam is not None:
        try:
            routecam.unregister()
        except Exception as rc_exc:
            print(f"[CashCab] RouteCam unregister failed: {rc_exc}")



    # Unregister route operators
    try:
        route_nodes.unregister()
    except Exception:
        pass
    try:
        route_assets.unregister()
    except Exception:
        pass

    # Unregister main operators defensively in case they were already removed
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            continue
        except Exception:
            continue

    print("[BLOSM] Route import addon unregistered")


if __name__ == "__main__":
    register()
