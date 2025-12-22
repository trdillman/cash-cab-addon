from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


def _deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def _find_collection(name: str):
    return bpy.data.collections.get(name)


def _camera_axes_world(cam_obj: bpy.types.Object) -> tuple[Vector, Vector, Vector]:
    mw: Matrix = cam_obj.matrix_world.to_3x3()
    right = (mw @ Vector((1, 0, 0))).normalized()
    up = (mw @ Vector((0, 1, 0))).normalized()
    forward = (mw @ Vector((0, 0, -1))).normalized()
    return right, up, forward


def _camera_yaw_pitch_roll(cam_obj: bpy.types.Object) -> dict:
    world_up = Vector((0, 0, 1))
    _, up, forward = _camera_axes_world(cam_obj)

    f_xy = Vector((forward.x, forward.y, 0.0))
    yaw = _deg(math.atan2(f_xy.y, f_xy.x)) if f_xy.length > 1e-9 else 0.0
    pitch = _deg(math.asin(max(-1.0, min(1.0, forward.z))))

    proj_world_up = (world_up - world_up.dot(forward) * forward)
    if proj_world_up.length < 1e-9:
        roll = 0.0
    else:
        proj_world_up.normalize()
        dot_u = max(-1.0, min(1.0, proj_world_up.dot(up)))
        angle = math.acos(dot_u)
        sign = 1.0 if forward.dot(proj_world_up.cross(up)) >= 0 else -1.0
        roll = _deg(angle * sign)

    return {"yaw_deg": yaw, "pitch_deg": pitch, "roll_deg": roll}


def _fcurve_summary(id_data) -> dict:
    ad = getattr(id_data, "animation_data", None)
    if not ad or not ad.action:
        return {"has_action": False, "action": None, "fcurves": []}

    fcurves = []
    for fc in ad.action.fcurves:
        kps = getattr(fc, "keyframe_points", None)
        fcurves.append(
            {
                "data_path": fc.data_path,
                "array_index": int(fc.array_index),
                "keyframes": int(len(kps)) if kps else 0,
            }
        )
    return {"has_action": True, "action": ad.action.name, "fcurves": fcurves}


def _choose_primary_camera(scene: bpy.types.Scene) -> bpy.types.Object | None:
    if scene.camera and scene.camera.type == "CAMERA":
        return scene.camera

    cameras = [o for o in scene.objects if o.type == "CAMERA"]
    if not cameras:
        return None

    def score(cam: bpy.types.Object) -> int:
        s = 0
        obj_anim = _fcurve_summary(cam)
        data_anim = _fcurve_summary(cam.data)
        s += sum(fc["keyframes"] for fc in obj_anim["fcurves"])
        s += sum(fc["keyframes"] for fc in data_anim["fcurves"])
        return s

    cameras.sort(key=score, reverse=True)
    return cameras[0]


def build_scene_summary(
    *,
    scene: bpy.types.Scene,
    camera_name: str = "",
    frames: tuple[int, int] = (1, 180),
    step: int = 5,
    start_marker_name: str = "MARKER_START",
    end_marker_name: str = "MARKER_END",
    route_object_name: str = "ROUTE",
    car_lead_name: str = "CAR_LEAD",
    buildings_collection_name: str = "ASSET_BUILDINGS",
) -> dict:
    frame_start, frame_end = frames

    required_objects = [
        start_marker_name,
        end_marker_name,
        route_object_name,
        car_lead_name,
    ]
    obj_presence = {name: (bpy.data.objects.get(name) is not None) for name in required_objects}

    buildings_col = _find_collection(buildings_collection_name)
    buildings_mesh_count = 0
    if buildings_col:
        buildings_mesh_count = sum(1 for o in buildings_col.all_objects if o.type == "MESH")

    cameras = [o for o in scene.objects if o.type == "CAMERA"]
    active_camera = scene.camera if scene.camera and scene.camera.type == "CAMERA" else None
    primary_camera = bpy.data.objects.get(camera_name) if camera_name else _choose_primary_camera(scene)

    payload: dict = {
        "file": str(Path(bpy.data.filepath).resolve()) if bpy.data.filepath else "",
        "scene": {
            "name": scene.name,
            "frame_start": int(scene.frame_start),
            "frame_end": int(scene.frame_end),
            "fps": float(scene.render.fps / scene.render.fps_base),
            "resolution": [int(scene.render.resolution_x), int(scene.render.resolution_y)],
        },
        "conventions": {
            "objects_present": obj_presence,
            "buildings_collection_name": buildings_collection_name,
            "buildings_collection_present": buildings_col is not None,
            "buildings_mesh_count": buildings_mesh_count,
        },
        "cameras": {
            "active": active_camera.name if active_camera else None,
            "primary": primary_camera.name if primary_camera else None,
            "all": [c.name for c in cameras],
        },
        "animation": {
            "primary_camera_object": _fcurve_summary(primary_camera) if primary_camera else {"has_action": False},
            "primary_camera_data": _fcurve_summary(primary_camera.data)
            if primary_camera and primary_camera.type == "CAMERA"
            else {"has_action": False},
        },
        "camera_motion_samples": {},
    }

    if primary_camera and primary_camera.type == "CAMERA":
        samples = []
        depsgraph = bpy.context.evaluated_depsgraph_get()
        step = max(1, int(step))
        for f in range(frame_start, frame_end + 1, step):
            scene.frame_set(f)
            depsgraph.update()
            cam_eval = primary_camera.evaluated_get(depsgraph)
            loc = cam_eval.matrix_world.to_translation()
            ypr = _camera_yaw_pitch_roll(cam_eval)
            samples.append(
                {
                    "frame": f,
                    "loc": [float(loc.x), float(loc.y), float(loc.z)],
                    "ortho_scale": float(getattr(cam_eval.data, "ortho_scale", 0.0)),
                    **ypr,
                }
            )
        payload["camera_motion_samples"][primary_camera.name] = samples

    return payload


def write_scene_summary(payload: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

