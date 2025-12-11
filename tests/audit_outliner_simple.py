#!/usr/bin/env python3
"""
Simple Outliner Visibility Audit for CashCab Addon

This script loads the saved .blend file and performs a basic visibility audit
of all objects and collections to verify CashCab outliner states.
"""

import bpy
import sys
from pathlib import Path

def _log(msg: str) -> None:
    print(f"[SIMPLE_AUDIT] {msg}")

def main():
    _log("Starting Simple Outliner Visibility Audit")
    
    # Try to find and load the saved .blend file
    desktop_path = Path.home() / "Desktop" / "CashCab_QA"
    blend_files = list(desktop_path.glob("*.blend"))
    
    if not blend_files:
        _log("No saved .blend files found in Desktop/CashCab_QA/")
        print("ERROR: No saved .blend files found. Please run E2E test first.")
        return 1
    
    # Load the most recent .blend file
    latest_blend = max(blend_files, key=lambda f: f.stat().st_mtime)
    _log(f"Loading .blend file: {latest_blend}")
    
    try:
        bpy.ops.wm.open_mainfile(filepath=str(latest_blend))
        _log("Successfully loaded .blend file")
    except Exception as exc:
        _log(f"Failed to load .blend file: {exc}")
        return 1
    
    # Get current scene and view layer
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer
    
    # Collect all objects and collections
    all_objects = list(bpy.data.objects)
    all_collections = list(bpy.data.collections)
    
    _log(f"Scene audit: {len(all_objects)} objects, {len(all_collections)} collections")
    
    # Focus on high-signal objects
    high_signal_names = [
        'ROUTE', 'CAR_TRAIL', 'CAR_LEAD', 'ASSET_CAR',
        'ASSET_ROUTE', 'ASSET_ROADS', 'ASSET_BUILDINGS', 'ASSET_WATER_RESULT',
        'ASSET_MARKERS', 'ASSET_WORLD', 'ASSET_CNTower',
        'Ground_Plane_Result', 'Water_Plane_Result', 'Islands_Mesh', 'Lake_Mesh_Cutter',
        'RouteLead', 'RoutePreview'
    ]
    
    high_signal_objects = []
    for obj in all_objects:
        if obj.name in high_signal_names or obj.name.startswith('profile_'):
            high_signal_objects.append(obj)
    
    # High-signal collections
    high_signal_collection_names = [
        'ASSET_ROUTE', 'ASSET_ROADS', 'ASSET_BUILDINGS', 'ASSET_WATER_RESULT',
        'ASSET_MARKERS', 'ASSET_WORLD', 'ASSET_CNTower', 'LIGHTING'
    ]
    
    high_signal_collections = []
    for coll in all_collections:
        if coll.name in high_signal_collection_names:
            high_signal_collections.append(coll)
    
    _log(f"High-signal audit: {len(high_signal_objects)} objects, {len(high_signal_collections)} collections")
    
    # Generate comprehensive report
    print("\n" + "=" * 120)
    print("CASH CAB ADDON E2E OUTLINER VISIBILITY AUDIT REPORT")
    print("=" * 120)
    
    print(f"\nScene Summary:")
    print(f"- Loaded from: {latest_blend.name}")
    print(f"- Total Objects: {len(all_objects)}")
    print(f"- Total Collections: {len(all_collections)}")
    print(f"- High-Signal Objects: {len(high_signal_objects)}")
    print(f"- High-Signal Collections: {len(high_signal_collections)}")
    
    print(f"\nCollection Visibility Status:")
    print("Collection | Viewport Hidden | Objects Count | Notes")
    print("-----------|-----------------|---------------|-------")
    for coll in high_signal_collections:
        status = "HIDDEN" if coll.hide_viewport else "VISIBLE"
        print(f"{coll.name:<11} | {status:<15} | {len(coll.objects):<13} | Asset collection")
    
    print(f"\nObject Visibility Status:")
    print("Name | Type | Viewport | Render | Collections | Role | Notes")
    print("-----|------|----------|--------|-------------|------|-------")
    
    # Categorize and assess objects
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
    
    for obj in high_signal_objects:
        viewport_status = "HIDDEN" if obj.hide_viewport else "VISIBLE"
        render_status = "HIDDEN" if obj.hide_render else "VISIBLE"
        collections = ", ".join([c.name for c in obj.users_collection])
        role = obj.get('blosm_role', 'none')
        
        # Categorize objects
        name = obj.name
        category = "Other"
        notes = "General object"
        
        if name in ['ROUTE']:
            object_categories['Route'].append(obj)
            category = "Route"
            notes = "Route curve - should be visible"
        elif name in ['CAR_TRAIL']:
            object_categories['CarTrail'].append(obj)
            category = "CarTrail"
            notes = "Car trail - should be visible"
        elif name in ['ASSET_CAR', 'CAR_LEAD', 'RouteLead', 'RoutePreview']:
            object_categories['Car/Lead'].append(obj)
            category = "Car/Lead"
            notes = "Car object - should be visible"
        elif name in ['ASSET_ROADS']:
            object_categories['Roads'].append(obj)
            category = "Roads"
            notes = "Roads mesh - should be visible"
        elif name in ['ASSET_BUILDINGS']:
            object_categories['Buildings'].append(obj)
            category = "Buildings"
            notes = "Buildings mesh - should be visible"
        elif name in ['Ground_Plane_Result', 'Water_Plane_Result', 'Islands_Mesh', 'Lake_Mesh_Cutter']:
            object_categories['Environment'].append(obj)
            category = "Environment"
            notes = "Environment result - should be visible"
        elif name in ['ASSET_MARKERS']:
            object_categories['Markers'].append(obj)
            category = "Markers"
            notes = "Route markers - should be visible"
        elif name.startswith('profile_'):
            object_categories['Helpers'].append(obj)
            category = "Helpers"
            notes = "Profile curve - should be hidden"
        
        print(f"{name:<15} | {obj.type:<6} | {viewport_status:<8} | {render_status:<6} | {collections:<11} | {role:<6} | {notes}")
    
    # Category-based assessment
    print(f"\nCategory-Based Assessment:")
    print("Category | Count | Expected | Actual Status")
    print("---------|-------|----------|-------------")
    
    category_assessment = {}
    for category, objects in object_categories.items():
        if not objects:
            category_assessment[category] = "N/A"
            status = "N/A"
            print(f"{category:<9} | {len(objects):<5} | N/A | No objects")
        else:
            visible_count = sum(1 for obj in objects if not obj.hide_viewport)
            total_count = len(objects)
            
            # Determine expected behavior
            if category == 'Helpers':
                expected = "Hidden"
                actual = "Hidden" if visible_count == 0 else f"{visible_count}/{total_count} visible"
                assessment = "PASS" if visible_count == 0 else "FAIL"
            else:
                expected = "Visible"
                actual = f"{visible_count}/{total_count} visible"
                assessment = "PASS" if visible_count == total_count else "FAIL"
            
            category_assessment[category] = assessment
            print(f"{category:<9} | {total_count:<5} | {expected:<8} | {actual}")
    
    # Final verdict
    print(f"\n" + "=" * 120)
    
    # Calculate overall pass/fail
    fail_categories = [cat for cat, assessment in category_assessment.items() if assessment == "FAIL"]
    overall_pass = len(fail_categories) == 0
    
    verdict = "PASS" if overall_pass else "FAIL"
    print(f"FINAL VERDICT: {verdict}")
    
    if not overall_pass:
        print(f"\nFailed Categories:")
        for cat in fail_categories:
            print(f"- {cat}")
    
    print(f"\nTest Method:")
    print(f"- Loaded saved .blend file from E2E test: {latest_blend.name}")
    print(f"- Audited {len(high_signal_objects)} high-signal objects and {len(high_signal_collections)} collections")
    print(f"- Applied CashCab visibility conventions:")
    print(f"  - Route/CAR_TRAIL/Car objects should be visible in viewport and render")
    print(f"  - Environment objects (ground/water/islands) should be visible")
    print(f"  - Helper/profile curves should be hidden")
    print(f"  - Collections should generally be visible unless specifically hidden")
    
    return 0 if overall_pass else 1

if __name__ == "__main__":
    sys.exit(main())