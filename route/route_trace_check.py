"""RouteTrace setup inspection script (non-destructive).

How to use (in Blender UI):
- Open this file in the Text Editor (route/route_trace_check.py) and Run Script, or
- In the Python Console: import blosm.route.route_trace_check as rtc; rtc.run()

It prints:
- Route object name resolved
- Presence of the RouteTrace modifier and its node group
- The driven GN input property (if detected)
- Whether the driver is present and its expression
- Scene variables used by the driver (blosm_anim_start/end/lead)
"""

from __future__ import annotations

import bpy


def _find_route_curve() -> bpy.types.Object | None:
    """Best-effort route curve resolution without creating anything."""
    # Try addon resolver first
    try:
        import blosm.route.resolve as resolve
        obj = resolve.resolve_route_obj(bpy.context)
        if obj is not None:
            return obj
    except Exception:
        pass

    # Heuristic: curve with RouteTrace GN modifier
    for obj in bpy.data.objects:
        if getattr(obj, 'type', None) != 'CURVE':
            continue
        for m in getattr(obj, 'modifiers', []) or []:
            if getattr(m, 'type', None) == 'NODES' and getattr(m, 'name', '') == 'RouteTrace':
                return obj

    # Fallback by name
    for obj in bpy.data.objects:
        if getattr(obj, 'type', None) == 'CURVE' and 'route' in (obj.name or '').casefold():
            return obj
    return None


def run() -> dict[str, object]:
    sc = bpy.context.scene
    route = _find_route_curve()
    print(f"[CHECK][RouteTrace] route object: {getattr(route, 'name', None)}")

    # Find the modifier and node group
    modifier = None
    if route is not None:
        modifier = route.modifiers.get('RouteTrace')
        if not (modifier and getattr(modifier, 'type', None) == 'NODES'):
            for m in getattr(route, 'modifiers', []) or []:
                if getattr(m, 'type', None) != 'NODES':
                    continue
                ng = getattr(m, 'node_group', None)
                if ng and getattr(ng, 'name', '') == 'ASSET_RouteTrace':
                    modifier = m
                    break
    ng = getattr(modifier, 'node_group', None)
    print(f"[CHECK][RouteTrace] modifier exists: {bool(modifier and getattr(modifier,'type',None)=='NODES')} name: {getattr(modifier, 'name', None)}")
    print(f"[CHECK][RouteTrace] node_group: {getattr(ng, 'name', None)}")

    # Determine float input property used for driver
    prop_name = None
    if modifier and ng:
        try:
            import blosm.route.anim as anim
            idx = anim._find_gn_input_index(ng, 'FLOAT', 'OffsetFactor')
            prop_name = anim._resolve_gn_input_property(modifier, idx) if idx is not None else None
        except Exception as exc:
            print(f"[CHECK][RouteTrace] WARN anim helpers unavailable: {exc}")
    print(f"[CHECK][RouteTrace] float input property: {prop_name}")

    # Check if a driver is present on that property
    has_driver = False
    expr = None
    data_path = None
    if route and modifier and prop_name:
        data_path = f'modifiers["{modifier.name}"]["{prop_name}"]'
        ad = getattr(route, 'animation_data', None)
        if ad:
            for fc in getattr(ad, 'drivers', []) or []:
                if fc.data_path == data_path:
                    has_driver = True
                    expr = getattr(fc.driver, 'expression', None)
                    break
    print(f"[CHECK][RouteTrace] driver present: {has_driver} data_path: {data_path} expr: {expr}")

    # Scene variables used by the driver
    for key in ('blosm_anim_start', 'blosm_anim_end', 'blosm_lead_frames'):
        print(f"[CHECK][RouteTrace] scene var {key}: {key in sc} value: {sc.get(key)}")

    return {
        'route': getattr(route, 'name', None),
        'modifier': getattr(modifier, 'name', None),
        'node_group': getattr(ng, 'name', None),
        'prop': prop_name,
        'driver': has_driver,
        'data_path': data_path,
        'driver_expr': expr,
    }


if __name__ == '__main__':
    run()

