"""
Diagnostic script for Fetch Route operator.

Run from the dev folder (one level above the addon):
    blender --background --python test_operator_invoke.py
"""

import importlib.util
import os
import sys
import traceback

import bpy


DEV_ROOT = os.path.dirname(__file__)
ADDON_DIR = os.path.join(DEV_ROOT, "cash-cab-addon")
MODULE_NAME = "cash_cab_addon"


def _load_addon_module():
    """Load the addon package directly from the dev folder and register it."""
    if MODULE_NAME in sys.modules:
        module = sys.modules[MODULE_NAME]
    else:
        init_path = os.path.join(ADDON_DIR, "__init__.py")
        spec = importlib.util.spec_from_file_location(
            MODULE_NAME,
            init_path,
            submodule_search_locations=[ADDON_DIR],
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[MODULE_NAME] = module
        spec.loader.exec_module(module)

    register = getattr(module, "register", None)
    if callable(register):
        try:
            register()
        except ValueError as exc:
            print(f"[TEST] register() reported ValueError (likely already registered): {exc}")
        except Exception as exc:
            print(f"[TEST] register() failed: {exc}")
            traceback.print_exc()
            raise
    return module


def _ensure_test_addresses(addon_props):
    if not getattr(addon_props, "route_start_address", "").strip():
        addon_props.route_start_address = "1 Dundas St. E, Toronto"
    if not getattr(addon_props, "route_end_address", "").strip():
        addon_props.route_end_address = "500 Yonge St, Toronto"


def test_operator_invoke():
    print("\n" + "=" * 80)
    print("FETCH ROUTE OPERATOR DIAGNOSTIC")
    print("=" * 80)

    module = _load_addon_module()

    print("\n1) Checking operator registration...")
    if not hasattr(bpy.ops.blosm, "fetch_route_map"):
        print("   ERROR: bpy.ops.blosm.fetch_route_map not registered")
        return False
    print("   OK: operator is registered")

    print("\n2) Importing operator class...")
    try:
        from cash_cab_addon.route.fetch_operator import BLOSM_OT_FetchRouteMap
        print(f"   OK: class imported ({BLOSM_OT_FetchRouteMap.bl_idname})")
    except Exception as exc:
        print(f"   ERROR: could not import operator class: {exc}")
        traceback.print_exc()
        return False

    if not hasattr(BLOSM_OT_FetchRouteMap, "invoke"):
        print("   ERROR: invoke() not found on operator")
        return False
    print("   OK: invoke() exists")

    print("\n3) Ensuring scene properties...")
    scene = bpy.context.scene
    addon_props = getattr(scene, "blosm", None)
    if addon_props is None:
        print("   ERROR: scene.blosm property group missing")
        return False
    _ensure_test_addresses(addon_props)
    print(f"   Start: '{addon_props.route_start_address}'")
    print(f"   End:   '{addon_props.route_end_address}'")
    anim_start = getattr(scene, "blosm_anim_start", None)
    anim_end = getattr(scene, "blosm_anim_end", None)
    lead_frames = getattr(scene, "blosm_lead_frames", None)
    print(f"   Anim defaults: car {anim_start}-{anim_end}, lead_frames={lead_frames}")
    if anim_start != 15 or anim_end != 150 or lead_frames != 2:
        print("   ERROR: Animation defaults mismatch (expected car 15-150, lead_frames=2)")
        return False

    print("\n4) Invoking operator via bpy.ops...")
    try:
        result = bpy.ops.blosm.fetch_route_map("INVOKE_DEFAULT")
        print(f"   bpy.ops result: {result}")
        if result == {"CANCELLED"}:
            print("   ERROR: operator returned CANCELLED")
            return False
    except Exception as exc:
        print(f"   ERROR during bpy.ops invoke: {exc}")
        traceback.print_exc()
        return False

    print("\n5) Verifying CAR_TRAIL setup...")
    route_obj = None
    car_trail = None
    car_obj = None
    for obj in bpy.data.objects:
        role = obj.get("blosm_role")
        if role == "route_curve_osm":
            route_obj = obj
        elif role == "car_trail":
            car_trail = obj
        elif role == "asset_car":
            car_obj = obj
    print(f"   route_curve_osm: {route_obj.name if route_obj else 'MISSING'}")
    print(f"   car_trail:       {car_trail.name if car_trail else 'MISSING'}")
    print(f"   asset_car:       {car_obj.name if car_obj else 'MISSING'}")

    ok = True
    if car_trail is None or route_obj is None:
        print("   ERROR: CAR_TRAIL or route_curve_osm not found")
        ok = False
    else:
        gn_mods = [m for m in car_trail.modifiers if m.type == 'NODES']
        print(f"   CAR_TRAIL GN modifiers: {len(gn_mods)}")
        if not gn_mods:
            print("   ERROR: CAR_TRAIL has no Geometry Nodes modifier")
            ok = False

        anim = getattr(car_trail.data, "animation_data", None)
        drivers = list(getattr(anim, "drivers", []) or [])
        print(f"   CAR_TRAIL driver count: {len(drivers)}")
        if not drivers:
            print("   ERROR: CAR_TRAIL has no drivers on curve data")
            ok = False

    print("\n6) Route naming/collection + Smooth audit (Batch C0/D1)...")
    try:
        from cash_cab_addon.route import pipeline_finalizer as route_pipeline_finalizer
        route_obj = route_pipeline_finalizer._find_route_curve(scene)
    except Exception as exc:
        print(f"   ERROR: C0 audit could not resolve route via _find_route_curve: {exc}")
        traceback.print_exc()
        return False

    if route_obj is None:
        print("   ERROR: C0/D1 audit: route object not resolved")
        ok = False
    else:
        coll_names = [c.name for c in getattr(route_obj, "users_collection", []) or []]
        print(f"   route name: {route_obj.name}")
        print(f"   route collections: {coll_names}")
        if route_obj.name != "ROUTE":
            print("   ERROR: C0 audit: route.name is not 'ROUTE'")
            ok = False
        if "ASSET_ROUTE" not in coll_names:
            print("   ERROR: C0 audit: route not linked to 'ASSET_ROUTE'")
            ok = False
        smooth_mods = [m for m in getattr(route_obj, "modifiers", []) or [] if getattr(m, "type", None) == 'SMOOTH']
        print(f"   route Smooth modifiers: {[(m.name, getattr(m, 'factor', None), getattr(m, 'iterations', None)) for m in smooth_mods]}")
        if not smooth_mods:
            print("   ERROR: D1 audit: route has no Smooth modifier")
            ok = False
        else:
            sm = smooth_mods[0]
            factor = getattr(sm, "factor", None)
            iterations = getattr(sm, "iterations", None)
            if factor is None or abs(float(factor) - 2.0) > 1e-4 or iterations != 7:
                print("   ERROR: D1 audit: Smooth modifier settings incorrect (expected factor=2.0, iterations=7)")
                ok = False

    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80 + "\n")
    return ok


if __name__ == "__main__":
    success = test_operator_invoke()
    if not success:
        sys.exit(1)
