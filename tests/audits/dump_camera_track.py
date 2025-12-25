from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def _camera_keyframes(cam: bpy.types.Object) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {"object": [], "data": []}

    def collect(ad, bucket: str) -> None:
        if not ad or not getattr(ad, "action", None):
            return
        frames: set[int] = set()
        for fc in getattr(ad.action, "fcurves", []) or []:
            dp = str(getattr(fc, "data_path", "") or "")
            if dp not in ("location", "rotation_euler", "rotation_quaternion") and not dp.endswith(
                "ortho_scale"
            ):
                continue
            for kp in getattr(fc, "keyframe_points", []) or []:
                try:
                    frames.add(int(round(float(kp.co.x))))
                except Exception:
                    pass
        out[bucket] = sorted(frames)

    collect(getattr(cam, "animation_data", None), "object")
    cam_data = getattr(cam, "data", None)
    collect(getattr(cam_data, "animation_data", None) if cam_data else None, "data")
    return out


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    argv = sys.argv
    args = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--camera", default="ROUTERIG_CAMERA")
    parser.add_argument("--frame-step", type=int, default=1)
    parser.add_argument("--frame-start", type=int, default=-1)
    parser.add_argument("--frame-end", type=int, default=-1)
    ns = parser.parse_args(args)

    scene = bpy.context.scene
    cam = bpy.data.objects.get(ns.camera) or scene.camera
    if cam is None:
        raise RuntimeError(f"Camera not found: {ns.camera} (and scene.camera is None)")

    f0 = int(ns.frame_start) if int(ns.frame_start) > 0 else int(scene.frame_start)
    f1 = int(ns.frame_end) if int(ns.frame_end) > 0 else int(scene.frame_end)
    step = max(1, int(ns.frame_step))

    samples = []
    for f in range(f0, f1 + 1, step):
        scene.frame_set(f)
        mw = cam.matrix_world
        loc = mw.translation
        q = mw.to_quaternion()
        ortho = None
        try:
            ortho = float(getattr(cam.data, "ortho_scale", 0.0))
        except Exception:
            ortho = None
        samples.append(
            {
                "frame": int(f),
                "loc": [float(loc.x), float(loc.y), float(loc.z)],
                "quat": [float(q.w), float(q.x), float(q.y), float(q.z)],
                "ortho_scale": ortho,
            }
        )

    payload = {
        "blend": str(Path(bpy.data.filepath) if bpy.data.filepath else ""),
        "scene": scene.name,
        "frame_start": int(f0),
        "frame_end": int(f1),
        "camera_name": cam.name,
        "camera_type": str(getattr(getattr(cam, "data", None), "type", "")),
        "rotation_mode": str(getattr(cam, "rotation_mode", "")),
        "keyframes": _camera_keyframes(cam),
        "samples": samples,
    }

    out_path = Path(ns.out).resolve()
    _ensure_parent_dir(out_path)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[DumpCameraTrack] Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

