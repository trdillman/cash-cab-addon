# Diff Log - 2025-12-10 add import camera safe areas

## Scope
- Ensure a dedicated CAMERAS collection, CASHCAB_CAMERA object, and safe-area presets during the Fetch Route & Map finalizer.
- Expand the strict scene audit to guard the new camera collection and safe-area invariants.

## Summary
- Introduced constants for the camera collection/camera name and safe-area target, implemented a helper that creates/links the camera, and invoked it near the end of `route.pipeline_finalizer.run`.
- Added safe-area helpers and new audit checks for the CAMERAS collection plus title/action safe-area floats (per the 0.95 requirement), marking them as hard failures.
- Adjusted the E2E loader so it treats the repo root as the addon package and can import `cash_cab_addon` before running the Fetch Route pipeline and strict audit.

## Unified Diff
```
diff --git a/route/pipeline_finalizer.py b/route/pipeline_finalizer.py
@@
  CAR_TRAIL_RESAMPLE_SPACING = 10.0  # Project spec: CAR_TRAIL resample spacing (world units)
  CAR_TRAIL_SAMPLES_PER_SEGMENT = 16  # Project spec: CAR_TRAIL resample samples per segment
+CAMERAS_COLLECTION_NAME = "CAMERAS"
+CASHCAB_CAMERA_NAME = "CASHCAB_CAMERA"
+SAFE_AREA_TARGET_VALUE = 0.95
@@
  def _ensure_cn_tower_marker(scene: Optional[bpy.types.Scene]) -> None:
  @@
      print(f"[BLOSM] CN Tower marker placed at ({marker.location.x:.3f}, {marker.location.y:.3f})")
  
  
+def _set_safe_area_vector(vec: object) -> bool:
+    if vec is None:
+        return False
+    updated = False
+    for axis in ("x", "y"):
+        if hasattr(vec, axis):
+            try:
+                setattr(vec, axis, SAFE_AREA_TARGET_VALUE)
+                updated = True
+            except Exception:
+                pass
+    try:
+        vec[0] = SAFE_AREA_TARGET_VALUE
+        vec[1] = SAFE_AREA_TARGET_VALUE
+        updated = True
+    except Exception:
+        pass
+    return updated
+
+
+def _apply_safe_areas_to_target(target: object) -> bool:
+    safe_areas = getattr(target, "safe_areas", None)
+    if safe_areas is None:
+        return False
+    updated = False
+    for attr in ("title", "action"):
+        if _set_safe_area_vector(getattr(safe_areas, attr, None)):
+            updated = True
+    return updated
+
+
+def _ensure_cashcab_camera_and_safe_areas(scene: Optional[bpy.types.Scene]) -> dict[str, object]:
+    result = {
+        "collection": None,
+        "camera": None,
+        "collection_created": False,
+        "camera_created": False,
+        "camera_linked": False,
+        "safe_area_set": False,
+    }
+
+    if scene is None:
+        return result
+
+    camera_collection = bpy.data.collections.get(CAMERAS_COLLECTION_NAME)
+    if camera_collection is None:
+        camera_collection = bpy.data.collections.new(CAMERAS_COLLECTION_NAME)
+        result["collection_created"] = True
+
+    result["collection"] = getattr(camera_collection, "name", None)
+
+    scene_root = getattr(scene, "collection", None)
+    if camera_collection and scene_root:
+        child_names = {child.name for child in scene_root.children}
+        if camera_collection.name not in child_names:
+            try:
+                scene_root.children.link(camera_collection)
+            except RuntimeError:
+                pass
+
+    camera_obj = bpy.data.objects.get(CASHCAB_CAMERA_NAME)
+    if camera_obj is None:
+        cam_data = bpy.data.cameras.new(CASHCAB_CAMERA_NAME)
+        camera_obj = bpy.data.objects.new(CASHCAB_CAMERA_NAME, cam_data)
+        result["camera_created"] = True
+
+    if camera_collection and camera_obj is not None:
+        existing_names = {obj.name for obj in camera_collection.objects}
+        if camera_obj.name not in existing_names:
+            try:
+                camera_collection.objects.link(camera_obj)
+            except RuntimeError:
+                pass
+        result["camera_linked"] = camera_obj.name in {obj.name for obj in camera_collection.objects}
+        for coll in list(getattr(camera_obj, "users_collection", []) or []):
+            if coll is camera_collection:
+                continue
+            try:
+                coll.objects.unlink(camera_obj)
+            except Exception:
+                pass
+
+    result["camera"] = getattr(camera_obj, "name", None)
+
+    scene_safe = _apply_safe_areas_to_target(scene)
+    cam_safe = _apply_safe_areas_to_target(getattr(camera_obj, "data", None)) if camera_obj else False
+    result["safe_area_set"] = scene_safe or cam_safe
+
+    return result
+
+
 def _ensure_car_trail_node_group() -> bpy.types.NodeTree | None:
 @@
      if _ensure_car_trail_material(scene):
          result["car_trail_material"] = "CAR_TRAIL_SHADER"
  except Exception as exc:
      print(f"[BLOSM] WARN CAR_TRAIL material assignment failed: {exc}")
  
+    try:
+        camera_info = _ensure_cashcab_camera_and_safe_areas(scene)
+        if camera_info and camera_info.get("camera"):
+            result["cashcab_camera"] = camera_info
+    except Exception as exc:
+        print(f"[BLOSM] WARN cashcab camera ensure failed: {exc}")
+
  try:
      result["orphan_data_purged"] = _purge_orphaned_data()
  except Exception as exc:
      print(f"[FP][PURGE] WARN orphan purge wrapper failed: {exc}")
@@
diff --git a/test_scene_audit_strict.py b/test_scene_audit_strict.py
@@
 CAR_TRAIL_SAMPLES = getattr(route_pf, "CAR_TRAIL_SAMPLES_PER_SEGMENT", 16)
 TEMPLATE_BLEND = route_pf.CAR_TRAIL_TEMPLATE_BLEND
 CAR_TRAIL_MATERIAL_NAME = "CAR_TRAIL_SHADER"
+CAMERAS_COLLECTION_NAME = getattr(route_pf, "CAMERAS_COLLECTION_NAME", "CAMERAS")
+CASHCAB_CAMERA_NAME = getattr(route_pf, "CASHCAB_CAMERA_NAME", "CASHCAB_CAMERA")
+SAFE_AREA_TARGET = getattr(route_pf, "SAFE_AREA_TARGET_VALUE", 0.95)
+SAFE_AREA_TOLERANCE = 1e-6
@@
 def _environment_status():
 @@
     }
 
 
+def _vector_xy(vec):
+    if vec is None:
+        return None
+    x = getattr(vec, "x", None)
+    y = getattr(vec, "y", None)
+    if x is None or y is None:
+        try:
+            x = float(vec[0])
+            y = float(vec[1])
+        except Exception:
+            return None
+    try:
+        return (float(x), float(y))
+    except Exception:
+        return None
+
+
+def _scene_safe_area_values(scene):
+    safe_areas = getattr(scene, "safe_areas", None)
+    if safe_areas is None:
+        return {}
+    values = {}
+    for attr_name in ("title", "action"):
+        vector = _vector_xy(getattr(safe_areas, attr_name, None))
+        if vector is not None:
+            values[attr_name] = vector
+    return values
+

 def _car_trail_config_ok(car_trail, route_obj):
  @@
      checks.append(("Environment ground present", env["ground"], ""))
      checks.append(("Environment water present", env["water"], ""))
      checks.append(("Environment islands present", env["islands"], ""))
      checks.append(("Environment shoreline present", env["shoreline"], ""))
  
+    cam_collection = bpy.data.collections.get(CAMERAS_COLLECTION_NAME)
+    camera_names = [getattr(obj, "name", None) for obj in (cam_collection.objects if cam_collection else [])]
+    camera_found = cam_collection is not None and CASHCAB_CAMERA_NAME in camera_names
+    camera_note = (
+        f"collection={'present' if cam_collection else 'missing'}, members={camera_names}"
+        if camera_names
+        else f"collection={'present' if cam_collection else 'missing'}"
+    )
+    checks.append(
+        (
+            "CASHCAB_CAMERA exists in CAMERAS collection",
+            camera_found,
+            camera_note,
+        )
+    )
+
+    safe_values = _scene_safe_area_values(scene)
+    def _safe_value_ok(vals):
+        if vals is None:
+            return False
+        return all(abs(v - SAFE_AREA_TARGET) <= SAFE_AREA_TOLERANCE for v in vals)
+
+    title_vals = safe_values.get("title")
+    action_vals = safe_values.get("action")
+    safe_ok = _safe_value_ok(title_vals) and _safe_value_ok(action_vals)
+    safe_note = f"title={title_vals}, action={action_vals}"
+    if not safe_values:
+        safe_note = "safe_areas missing"
+    checks.append(("Safe areas title/action set to 0.95", safe_ok, safe_note))

     # RouteTrace offset value/static checks (no drivers/keys, value == 1.0)
@@
     hard_checks = {
  @@
         "Taxi sign attached to car F3",
+        "CASHCAB_CAMERA exists in CAMERAS collection",
+        "Safe areas title/action set to 0.95",
     }
 ```diff

## Acceptance Checklist
- PASS: After the fetch/import, the `CAMERAS` collection exists and includes a `CASHCAB_CAMERA`.
- PASS: The scene and camera safe-area-presets for title/action settled at `0.95`.
- FAIL: The strict audit still reports `CAR_TRAIL bevel_object set` as `bevel=None`.
- FAIL: Overall strict verdict is still `FAIL` (due to the above bevel check), so end-to-end exit code is non-zero.

## Commands Run
- `blender -b --python test_e2e_then_strict_toronto.py` *(runs to fetch/map and strict audit; the camera/safe-area invariants PASS but the strict audit overall still FAILs because `CAR_TRAIL bevel_object set` reports `bevel=None`, so the process exits 1.)*

### Recent strict audit excerpt
```
[STRICT_AUDIT] Starting STRICT CashCab scene audit

[STRICT_AUDIT] Invariant Results:
Check | Result | Notes
------|--------|------
CAR_TRAIL driver targets safe E | PASS | bad_targets=[]
CAR_TRAIL bevel_object set | FAIL | bevel=None
CAR_TRAIL material is CAR_TRAIL_SHADER | PASS | material=CAR_TRAIL_SHADER
...
CASHCAB_CAMERA exists in CAMERAS collection | PASS | collection=present, members=['CASHCAB_CAMERA']
Safe areas title/action set to 0.95 | PASS | title=(0.949999988079071, 0.949999988079071), action=(0.949999988079071, 0.949999988079071)
[STRICT_AUDIT] Overall strict verdict: FAIL
```
