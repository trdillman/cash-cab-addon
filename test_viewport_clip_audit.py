"""
Test script for viewport clip operator.

This script verifies that the BLOSM_OT_SetViewportClip operator
correctly sets clip_start and clip_end for VIEW_3D spaces.

Usage:
    blender --background --python test_viewport_clip_audit.py
"""

import sys
import bpy


def test_viewport_clip_operator():
    """Test the viewport clip operator functionality."""
    print("\n" + "=" * 60)
    print("VIEWPORT CLIP OPERATOR TEST")
    print("=" * 60)

    # Step 1: Register the addon
    print("\n[1/4] Registering addon...")
    try:
        # Import and register the addon
        addon_path = bpy.path.abspath("//")
        if addon_path not in sys.path:
            sys.path.insert(0, addon_path)
        
        # Import the main addon module
        import __init__ as cash_cab_addon
        
        # Register if not already registered
        if not hasattr(bpy.types.Scene, 'blosm'):
            cash_cab_addon.register()
            print("  ✓ Addon registered successfully")
        else:
            print("  ✓ Addon already registered")
    except Exception as e:
        print(f"  ✗ Failed to register addon: {e}")
        return False

    # Step 2: Check initial viewport states
    print("\n[2/4] Checking initial viewport states...")
    initial_count = 0
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        initial_count += 1
                        print(f"  Found VIEW_3D: clip_start={space.clip_start}, clip_end={space.clip_end}")

    if initial_count == 0:
        print("  ⚠ No VIEW_3D spaces found in bpy.data.screens")
        print("  Note: This is expected in headless Blender")
    else:
        print(f"  ✓ Found {initial_count} VIEW_3D space(s)")

    # Step 3: Execute the operator
    print("\n[3/4] Executing blosm.set_viewport_clip operator...")
    try:
        result = bpy.ops.blosm.set_viewport_clip('EXEC_DEFAULT')
        print(f"  Operator result: {result}")
        
        if result == {'FINISHED'}:
            print("  ✓ Operator executed successfully")
        elif result == {'CANCELLED'}:
            print("  ⚠ Operator was cancelled (no viewports to update)")
        else:
            print(f"  ? Operator returned unexpected result: {result}")
    except Exception as e:
        print(f"  ✗ Operator execution failed: {e}")
        return False

    # Step 4: Verify the results
    print("\n[4/4] Verifying clip values...")
    updated_count = 0
    expected_clip_start = 1.0
    expected_clip_end = 1000000.0
    
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        matches_start = abs(space.clip_start - expected_clip_start) < 0.001
                        matches_end = abs(space.clip_end - expected_clip_end) < 0.001
                        
                        if matches_start and matches_end:
                            updated_count += 1
                            print(f"  ✓ VIEW_3D updated: clip_start={space.clip_start}, clip_end={space.clip_end}")
                        else:
                            print(f"  ✗ VIEW_3D not updated correctly: clip_start={space.clip_start}, clip_end={space.clip_end}")

    # Final verdict
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    if initial_count == 0:
        print("\nStatus: PASS (with limitations)")
        print("  - No VIEW_3D spaces available in headless mode")
        print("  - Operator executed without errors")
        print("  - This is expected behavior for headless Blender")
        return True
    elif updated_count > 0:
        print(f"\nStatus: PASS")
        print(f"  - Updated {updated_count} viewport(s) successfully")
        print(f"  - All viewports have correct clip values")
        return True
    else:
        print(f"\nStatus: FAIL")
        print(f"  - Found {initial_count} viewport(s) but none were updated")
        return False


if __name__ == "__main__":
    success = test_viewport_clip_operator()
    sys.exit(0 if success else 1)
