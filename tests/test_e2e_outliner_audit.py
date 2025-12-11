#!/usr/bin/env python3
"""
Combined E2E Test + Outliner Visibility Audit for CashCab Addon

This script runs a complete E2E "Fetch Route & Map" workflow and then immediately
executes the outliner visibility audit in the same Blender session to verify
the visibility states of all imported objects and collections.

Usage:
    blender -b --python test_e2e_with_outliner_audit.py
"""

import importlib.util
import os
import sys
import traceback
from pathlib import Path

import bpy

# Import the E2E test functions
sys.path.insert(0, str(Path(__file__).parent))
from test_e2e_then_strict_toronto import (
    _load_addon_module, _ensure_scene_defaults, _run_fetch, 
    _run_strict_audit, _save_blend, ADDRESS_PAIRS
)

# Import the outliner audit functions
from test_outliner_visibility_audit import (
    _get_high_signal_objects, _get_high_signal_collections,
    _audit_object_visibility, _audit_collection_visibility,
    _check_visibility_expectations, _evaluate_visibility_compliance
)

def _log(msg: str) -> None:
    print(f"[COMBINED_E2E_AUDIT] {msg}")

def _get_view_layer_excluded(obj):
    """Check if object is excluded from current view layer"""
    try:
        view_layer = bpy.context.view_layer
        if view_layer and hasattr(view_layer, 'objects'):
            return obj.name not in view_layer.objects
    except:
        pass
    return False

def main():
    _log("Starting Combined E2E Test + Outliner Visibility Audit")
    
    # Step 1: Run E2E test workflow
    try:
        _log("Phase 1: Running E2E route import workflow...")
        
        # Load addon and setup scene
        _load_addon_module()
        _ensure_scene_defaults(bpy.context.scene)
        
        # Run fetch with first Toronto address pair
        start, end = ADDRESS_PAIRS[0]
        result = _run_fetch(start, end)
        
        if result != {"FINISHED"}:
            _log(f"E2E fetch failed with result: {result}")
            return 1
            
        # Run strict audit
        audit_ok = _run_strict_audit()
        if not audit_ok:
            _log("Strict audit failed")
            return 1
            
        _save_blend(1, "combined_e2e_audit")
        _log("E2E workflow completed successfully")
        
    except Exception as exc:
        _log(f"E2E workflow failed: {exc}")
        traceback.print_exc()
        return 1
    
    # Step 2: Run Outliner Visibility Audit on the imported scene
    try:
        _log("Phase 2: Running Outliner Visibility Audit...")
        
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
            expectations = _check_visibility_expectations(obj_audit, collection_results)
            compliance = _evaluate_visibility_compliance(obj_audit, expectations)
            
            obj_audit['expectations'] = expectations
            obj_audit['compliance'] = compliance
            object_results.append(obj_audit)
        
        # Generate comprehensive report
        print("\n" + "=" * 120)
        print("CASH CAB ADDON E2E + OUTLINER VISIBILITY AUDIT REPORT")
        print("=" * 120)
        
        print(f"\nScene Summary:")
        print(f"- Total Objects: {len(all_objects)}")
        print(f"- Total Collections: {len(all_collections)}")
        print(f"- High-Signal Objects Audited: {len(high_signal_objects)}")
        print(f"- High-Signal Collections Audited: {len(high_signal_collections)}")
        print(f"- E2E Test Address Pair: {start} -> {end}")
        
        print(f"\nCollection Inventory & Visibility:")
        print("Collection | Viewport Hidden | Objects Count | Status")
        print("-----------|-----------------|---------------|--------")
        for coll in collection_results:
            status = "HIDDEN" if coll['hide_viewport'] else "VISIBLE"
            print(f"{coll['name']:<11} | {status:<15} | {coll['objects_count']:<13} | Asset collection")
        
        print(f"\nObject Inventory & Visibility:")
        print("Name | Type | Viewport | Render | ViewLayer | Role | Compliance | Issues")
        print("-----|------|----------|--------|-----------|------|------------|-------")
        
        overall_pass = True
        critical_issues = []
        object_categories = {
            'Route': [],
            'Car/Lead': [],
            'CarTrail': [],
            'Roads': [],
            'Buildings': [],
            'Environment': [],
            'Markers': [],
            'Helpers': []
        }
        
        for obj in object_results:
            viewport_status = "HIDDEN" if obj['hide_viewport'] else "VISIBLE"
            render_status = "HIDDEN" if obj['hide_render'] else "VISIBLE"
            viewlayer_status = "EXCLUDED" if obj['view_layer_excluded'] else "INCLUDED"
            
            compliance_icon = "✅" if obj['compliance']['compliant'] else "❌"
            issues_str = "; ".join(obj['compliance']['issues']) if obj['compliance']['issues'] else "OK"
            
            print(f"{obj['name']:<15} | {obj['type']:<6} | {viewport_status:<8} | {render_status:<6} | {viewlayer_status:<9} | {obj['role']:<6} | {compliance_icon:<10} | {issues_str}")
            
            # Categorize objects
            name = obj['name']
            if name in ['ROUTE']:
                object_categories['Route'].append(obj)
            elif name in ['CAR_TRAIL']:
                object_categories['CarTrail'].append(obj)
            elif name in ['ASSET_CAR', 'CAR_LEAD', 'RouteLead', 'RoutePreview']:
                object_categories['Car/Lead'].append(obj)
            elif name in ['ASSET_ROADS']:
                object_categories['Roads'].append(obj)
            elif name in ['ASSET_BUILDINGS']:
                object_categories['Buildings'].append(obj)
            elif name in ['Ground_Plane_Result', 'Water_Plane_Result', 'Islands_Mesh', 'Lake_Mesh_Cutter']:
                object_categories['Environment'].append(obj)
            elif name in ['ASSET_MARKERS']:
                object_categories['Markers'].append(obj)
            elif name.startswith('profile_'):
                object_categories['Helpers'].append(obj)
            
            if not obj['compliance']['compliant']:
                overall_pass = False
                if obj['compliance']['severity'] == 'Blocker':
                    critical_issues.extend(obj['compliance']['issues'])
        
        # Category-based PASS/FAIL assessment
        print(f"\nCategory-Based Assessment:")
        print("Category | Count | Status | Notes")
        print("---------|-------|--------|-------")
        
        category_pass_fail = {}
        for category, objects in object_categories.items():
            if not objects:
                category_pass_fail[category] = "N/A (no objects)"
                status = "N/A"
                notes = "No objects in this category"
            else:
                compliant_count = sum(1 for obj in objects if obj['compliance']['compliant'])
                total_count = len(objects)
                
                if compliant_count == total_count:
                    category_pass_fail[category] = "PASS"
                    status = "PASS"
                    notes = f"All {total_count} objects compliant"
                else:
                    category_pass_fail[category] = "FAIL"
                    status = "FAIL"
                    notes = f"{compliant_count}/{total_count} objects compliant"
            
            print(f"{category:<9} | {len(objects):<5} | {status:<6} | {notes}")
        
        # Final verdict
        print(f"\n" + "=" * 120)
        verdict = "PASS" if overall_pass else "FAIL"
        print(f"FINAL VERDICT: {verdict}")
        
        if not overall_pass:
            print(f"\nCritical Issues Found:")
            for issue in critical_issues:
                print(f"- {issue}")
        
        print(f"\nTest Method:")
        print(f"- Combined E2E workflow + outliner audit in single Blender session")
        print(f"- Address pair: {start} -> {end}")
        print(f"- E2E strict audit: {'PASSED' if audit_ok else 'FAILED'}")
        print(f"- Audited {len(high_signal_objects)} high-signal objects and {len(high_signal_collections)} collections")
        print(f"- Applied CashCab visibility conventions and expectations")
        print(f"- Scene saved to: Desktop/CashCab_QA/RUN1_combined_e2e_audit.blend")
        
        return 0 if overall_pass else 1
        
    except Exception as exc:
        _log(f"Outliner audit failed: {exc}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())