#!/usr/bin/env python3
"""
Outliner Visibility Audit Script for CashCab Addon E2E QA

This script audits the visibility states of all objects and collections after a successful
"Fetch Route & Map" workflow. It generates a PASS/FAIL report based on CashCab conventions.

Run this script in the SAME Blender session after a successful E2E import.

Expected high-level visibility rules:
- ROUTE and CAR_TRAIL should be visible in viewport and render
- ASSET_CAR and CAR_LEAD visible in viewport and render  
- Environment results (ground/water/islands/shoreline) visible
- Helper/profile curves should be hidden/excluded from active view layer
- No critical collection should be accidentally excluded from ViewLayer
"""

import bpy
import sys
from pathlib import Path


def _log(msg: str) -> None:
    print(f"[OUTLINER_AUDIT] {msg}")


def _get_view_layer_excluded(obj):
    """Check if object is excluded from current view layer"""
    try:
        view_layer = bpy.context.view_layer
        if view_layer and hasattr(view_layer, 'objects'):
            return obj.name not in view_layer.objects
    except:
        pass
    return False


def _any_collection_viewport_visible(obj) -> bool:
    try:
        collections = list(getattr(obj, "users_collection", []) or [])
        if not collections:
            return True
        return any(getattr(c, "hide_viewport", False) is False for c in collections)
    except Exception:
        return True


def _audit_object_visibility(obj):
    """Audit visibility properties of a single object"""
    hide_viewport = getattr(obj, "hide_viewport", False)
    hide_render = getattr(obj, "hide_render", False)
    hide_get = getattr(obj, "hide_get", lambda: False)()
    view_layer_excluded = _get_view_layer_excluded(obj)

    viewport_visible = (not hide_viewport) and (not hide_get) and _any_collection_viewport_visible(obj) and (not view_layer_excluded)
    render_visible = not hide_render

    result = {
        'name': obj.name,
        'type': obj.type,
        'hide_viewport': hide_viewport,
        'hide_render': hide_render,
        'hide_get': hide_get,
        'view_layer_excluded': view_layer_excluded,
        'viewport_visible': viewport_visible,
        'render_visible': render_visible,
        'users_collection': [c.name for c in getattr(obj, 'users_collection', []) or []],
        'role': obj.get('blosm_role', ''),
        'origin': obj.get('blosm_origin', '')
    }
    return result


def _audit_collection_visibility(collection):
    """Audit visibility properties of a single collection"""
    result = {
        'name': collection.name,
        'hide_viewport': getattr(collection, 'hide_viewport', False),
        'objects_count': len(collection.objects) if hasattr(collection, 'objects') else 0
    }
    return result


def _get_high_signal_objects():
    """Get high-signal objects for detailed auditing"""
    high_signal_names = [
        'ROUTE', 'CAR_TRAIL', 'CAR_LEAD', 'ASSET_CAR',
        'ASSET_ROUTE', 'ASSET_ROADS', 'ASSET_BUILDINGS', 'ASSET_WATER_RESULT',
        'ASSET_MARKERS', 'ASSET_WORLD', 'ASSET_CNTower',
        'Ground_Plane_Result', 'Water_Plane_Result', 'Islands_Mesh', 'Lake_Mesh_Cutter',
        'RouteLead', 'RoutePreview'
    ]
    
    # Also include profile curves (should typically be hidden)
    high_signal_objects = []
    for obj in bpy.data.objects:
        if obj.name in high_signal_names or obj.name.startswith('profile_'):
            high_signal_objects.append(obj)
    
    return high_signal_objects


def _get_high_signal_collections():
    """Get high-signal collections for detailed auditing"""
    high_signal_names = [
        'ASSET_ROUTE', 'ASSET_ROADS', 'ASSET_BUILDINGS', 'ASSET_WATER_RESULT',
        'ASSET_MARKERS', 'ASSET_WORLD', 'ASSET_CNTower', 'LIGHTING'
    ]
    
    high_signal_collections = []
    for coll in bpy.data.collections:
        if coll.name in high_signal_names:
            high_signal_collections.append(coll)
    
    return high_signal_collections


def _check_visibility_expectations(obj_audit, collections):
    """Check if object meets CashCab visibility expectations"""
    name = obj_audit['name']
    role = obj_audit['role']
    
    # Helper/profile curves should be hidden
    if name.startswith('profile_') or 'profile' in name.lower():
        return {
            'expected_viewport_visible': False,
            'expected_render_visible': False,
            'expected_view_layer_excluded': True,
            'notes': 'Profile curve - should be hidden/internal'
        }
    
    # Route and CAR_TRAIL should be visible
    if name in ['ROUTE', 'CAR_TRAIL']:
        return {
            'expected_viewport_visible': True,
            'expected_render_visible': True,
            'expected_view_layer_excluded': False,
            'notes': 'Route/CAR_TRAIL - should be visible'
        }
    
    # Car objects should be visible
    if name in ['ASSET_CAR', 'CAR_LEAD', 'RouteLead', 'RoutePreview']:
        return {
            'expected_viewport_visible': True,
            'expected_render_visible': True,
            'expected_view_layer_excluded': False,
            'notes': 'Car object - should be visible'
        }
    
    # Environment objects should be visible
    if name == 'Lake_Mesh_Cutter':
        return {
            'expected_viewport_visible': False,
            'expected_render_visible': False,
            'expected_view_layer_excluded': False,
            'notes': 'Boolean/utility cutter - should not be visible'
        }

    env_names = ['Ground_Plane_Result', 'Water_Plane_Result', 'Islands_Mesh']
    if name in env_names:
        return {
            'expected_viewport_visible': True,
            'expected_render_visible': True,
            'expected_view_layer_excluded': False,
            'notes': 'Environment object - should be visible'
        }
    
    # Collection-specific checks
    for coll in collections or []:
        try:
            if name in [o.name for o in coll.objects]:
                if 'ASSET_' in coll.name or coll.name in ['LIGHTING']:
                    return {
                        'expected_viewport_visible': True,
                        'expected_render_visible': True,
                        'expected_view_layer_excluded': False,
                        'notes': f'Asset collection object ({coll.name}) - should be visible'
                    }
        except Exception:
            continue
    
    return {
        'expected_viewport_visible': True,  # Default expectation
        'expected_render_visible': True,
        'expected_view_layer_excluded': False,
        'notes': 'Default expectation - should be visible'
    }

def _evaluate_visibility_compliance(obj_audit, expectations):
    """Evaluate if object meets visibility expectations"""
    name = obj_audit['name']
    issues = []
    
    # Check viewport visibility
    if obj_audit.get('viewport_visible') != expectations['expected_viewport_visible']:
        issues.append(
            f"Viewport visibility mismatch: expected {expectations['expected_viewport_visible']}, got {obj_audit.get('viewport_visible')}"
        )
    
    # Check render visibility  
    if obj_audit.get('render_visible') != expectations['expected_render_visible']:
        issues.append(
            f"Render visibility mismatch: expected {expectations['expected_render_visible']}, got {obj_audit.get('render_visible')}"
        )
    
    # Check view layer exclusion
    if obj_audit['view_layer_excluded'] != expectations['expected_view_layer_excluded']:
        issues.append(f"View layer exclusion mismatch: expected {expectations['expected_view_layer_excluded']}, got {obj_audit['view_layer_excluded']}")
    
    severity = 'Blocker' if any('Route' in name or 'CAR_TRAIL' in name or 'ASSET_CAR' in name for name in [name]) else 'Major'
    
    return {
        'compliant': len(issues) == 0,
        'issues': issues,
        'severity': severity if issues else 'OK'
    }

def main():
    _log("Starting Outliner Visibility Audit")
    
    # Get current scene and view layer
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer
    
    # Collect all objects and collections
    all_objects = list(bpy.data.objects)
    all_collections = list(bpy.data.collections)
    
    _log(f"Scene audit: {len(all_objects)} objects, {len(all_collections)} collections")
    
    # Focus on high-signal objects and collections
    high_signal_objects = _get_high_signal_objects()
    high_signal_collections = _get_high_signal_collections()
    
    _log(f"High-signal audit: {len(high_signal_objects)} objects, {len(high_signal_collections)} collections")
    
    # Audit collections first
    collection_results = []
    for coll in high_signal_collections:
        coll_audit = _audit_collection_visibility(coll)
        collection_results.append(coll_audit)
    
    # Audit objects
    object_results = []
    for obj in high_signal_objects:
        obj_audit = _audit_object_visibility(obj)
        expectations = _check_visibility_expectations(obj_audit, high_signal_collections)
        compliance = _evaluate_visibility_compliance(obj_audit, expectations)
        
        obj_audit['expectations'] = expectations
        obj_audit['compliance'] = compliance
        object_results.append(obj_audit)
    
    # Generate report
    print("\n" + "=" * 120)
    print("OUTLINER VISIBILITY AUDIT REPORT")
    print("=" * 120)
    
    print(f"\nScene Summary:")
    print(f"- Total Objects: {len(all_objects)}")
    print(f"- Total Collections: {len(all_collections)}")
    print(f"- High-Signal Objects Audited: {len(high_signal_objects)}")
    print(f"- High-Signal Collections Audited: {len(high_signal_collections)}")
    
    print(f"\nCollection Visibility Status:")
    print("Collection | Viewport Hidden | Objects Count | Notes")
    print("-----------|-----------------|---------------|-------")
    for coll in collection_results:
        status = "HIDDEN" if coll['hide_viewport'] else "VISIBLE"
        print(f"{coll['name']:<11} | {status:<15} | {coll['objects_count']:<13} | Asset collection")
    
    print(f"\nObject Visibility Status:")
    print("Name | Type | Viewport | Render | ViewLayer | Role | Compliance | Issues")
    print("-----|------|----------|--------|-----------|------|------------|-------")
    
    overall_pass = True
    critical_issues = []
    
    for obj in object_results:
        viewport_status = "HIDDEN" if obj['hide_viewport'] else "VISIBLE"
        render_status = "HIDDEN" if obj['hide_render'] else "VISIBLE"
        viewlayer_status = "EXCLUDED" if obj['view_layer_excluded'] else "INCLUDED"
        
        compliance_icon = "✅" if obj['compliance']['compliant'] else "❌"
        issues_str = "; ".join(obj['compliance']['issues']) if obj['compliance']['issues'] else "OK"
        
        print(f"{obj['name']:<15} | {obj['type']:<6} | {viewport_status:<8} | {render_status:<6} | {viewlayer_status:<9} | {obj['role']:<6} | {compliance_icon:<10} | {issues_str}")
        
        if not obj['compliance']['compliant']:
            overall_pass = False
            if obj['compliance']['severity'] == 'Blocker':
                critical_issues.extend(obj['compliance']['issues'])
    
    # Final verdict
    print(f"\n" + "=" * 120)
    verdict = "PASS" if overall_pass else "FAIL"
    print(f"FINAL VERDICT: {verdict}")
    
    if not overall_pass:
        print(f"\nCritical Issues Found:")
        for issue in critical_issues:
            print(f"- {issue}")
    
    print(f"\nTest Method:")
    print(f"- Executed in Blender session after successful E2E route import")
    print(f"- Address pair: 100 Queen St W, Toronto, ON, Canada -> 200 University Ave, Toronto, ON, Canada")
    print(f"- Audited {len(high_signal_objects)} high-signal objects and {len(high_signal_collections)} collections")
    print(f"- Applied CashCab visibility conventions and expectations")
    
    return 0 if overall_pass else 1

if __name__ == "__main__":
    sys.exit(main())
