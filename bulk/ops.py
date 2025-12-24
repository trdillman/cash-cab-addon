from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List

import bpy

from . import google_sheet, parser
from .filename_utils import address_only
from .properties import BulkSettings

_APPEND_SAFE_RE = re.compile(r"[^A-Za-z0-9_\-]+")

_NON_ROUTE_KEYS = [
    "buildings",
    "water",
    "forests",
    "vegetation",
    "highways",
    "railways",
    "coordinatesAsFilter",
]


def _is_jsonable_primitive(value) -> bool:
    return value is None or isinstance(value, (bool, int, float, str))


def _snapshot_regular_import_settings(context) -> dict:
    """Capture regular-import settings for a bulk worker run.

    Bulk is intended to run the regular import workflow verbatim; the per-row
    manifest fields (addresses/coords) act as overrides.
    """
    scene = getattr(context, "scene", None)
    addon = getattr(scene, "blosm", None) if scene else None

    addon_settings: dict[str, object] = {}
    if addon is not None:
        for attr in dir(addon):
            if not (attr.startswith("route_") or attr in _NON_ROUTE_KEYS):
                continue
            try:
                value = getattr(addon, attr)
            except Exception:
                continue
            if _is_jsonable_primitive(value):
                addon_settings[attr] = value

    scene_settings: dict[str, object] = {}
    if scene is not None:
        for key in [
            "blosm_anim_start",
            "blosm_anim_end",
            "blosm_lead_frames",
            "blosm_route_start",
            "blosm_route_end",
        ]:
            if hasattr(scene, key):
                try:
                    value = getattr(scene, key)
                except Exception:
                    continue
                if _is_jsonable_primitive(value):
                    scene_settings[key] = value

        # FPS affects playback timing (seconds) even if keyframes match.
        try:
            scene_settings["render_fps"] = int(getattr(scene.render, "fps", 24))
            scene_settings["render_fps_base"] = float(
                getattr(scene.render, "fps_base", 1.0)
            )
        except Exception:
            pass

        try:
            scene_settings["frame_start"] = int(getattr(scene, "frame_start", 1))
            scene_settings["frame_end"] = int(getattr(scene, "frame_end", 250))
        except Exception:
            pass

    return {"addon": addon_settings, "scene": scene_settings}


def _build_worker_cmd(*, blender_bin: str, worker_script: Path, job: dict) -> list[str]:
    # Important: do NOT open assets/base.blend here. The regular operator
    # appends the base scene itself; opening base.blend causes a CashCab scene
    # name collision that can change animation defaults/timing.
    return [
        blender_bin,
        "--factory-startup",
        "-b",
        "--python",
        str(worker_script),
        "--",
        "--job_json",
        json.dumps(job),
    ]


def _slugify(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    raw = raw.replace(" ", "_")
    return _APPEND_SAFE_RE.sub("", raw)


def _address_slug(text: str) -> str:
    return _slugify(address_only(text))


def _addon_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _base_blend_path() -> Path:
    return _addon_root() / "assets" / "base.blend"


def _worker_script_path() -> Path:
    return Path(__file__).resolve().parent / "worker.py"


def _resolve_google_api_key(context) -> str:
    # Prefer scanning preferences (matches route.utils.resolve_google_api_key behavior)
    try:
        addons = getattr(getattr(context, "preferences", None), "addons", None)
        if addons:
            for addon in addons.values():
                prefs = getattr(addon, "preferences", None)
                if prefs and hasattr(prefs, "google_api_key"):
                    val = getattr(prefs, "google_api_key", "") or ""
                    if str(val).strip():
                        return str(val).strip()
    except Exception:
        pass

    # Fall back to environment variable
    try:
        import os
        val = os.environ.get("CASHCAB_GOOGLE_API_KEY", "") or ""
        if val.strip():
            return val.strip()
    except Exception:
        pass

    return ""


class BLOSM_OT_BulkFetchManifest(bpy.types.Operator):
    bl_idname = "blosm.bulk_fetch_manifest"
    bl_label = "Fetch Bulk Manifest"

    def execute(self, context):
        scene = context.scene
        settings: BulkSettings = getattr(scene, "cashcab_bulk", None)
        if settings is None:
            self.report({"ERROR"}, "Bulk settings missing")
            return {"CANCELLED"}

        try:
            if settings.manifest_source == "GOOGLE_SHEET":
                csv_text = google_sheet.fetch_csv(settings.google_sheet_url)
            else:
                raw_path = (settings.local_file_path or "").strip()
                if not raw_path:
                    raise ValueError("Local CSV path is empty")
                csv_path = Path(bpy.path.abspath(raw_path)).resolve()
                if not csv_path.exists():
                    raise FileNotFoundError(f"CSV not found: {csv_path}")
                csv_text = csv_path.read_text(encoding="utf-8-sig")
        except Exception as exc:
            self.report({"ERROR"}, f"Failed to load manifest: {exc}")
            return {"CANCELLED"}

        try:
            routes = parser.parse_manifest_text(csv_text)
        except Exception as exc:
            self.report({"ERROR"}, f"Manifest parse failed: {exc}")
            return {"CANCELLED"}

        settings.routes.clear()
        count = 0
        for route in routes:
            item = settings.routes.add()
            item.selected = False
            item.shot_code = route.shot_code
            item.start_address = route.start_address
            item.end_address = route.end_address
            item.start_coords = route.start_coords
            item.end_coords = route.end_coords
            item.due_date = route.due_date
            item.sheet_status = route.sheet_status
            item.run_state = "IDLE"
            item.log_message = ""
            count += 1

        settings.active_route_index = 0
        if count == 0:
            self.report({"ERROR"}, "No routes parsed from manifest")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Loaded {count} routes")
        return {"FINISHED"}


class BLOSM_OT_BulkSelectAll(bpy.types.Operator):
    bl_idname = "blosm.bulk_select_all"
    bl_label = "Select All Bulk Routes"

    def execute(self, context):
        settings: BulkSettings = getattr(context.scene, "cashcab_bulk", None)
        if settings is None:
            return {"CANCELLED"}
        for route in settings.routes:
            route.selected = True
        return {"FINISHED"}


class BLOSM_OT_BulkDeselectAll(bpy.types.Operator):
    bl_idname = "blosm.bulk_deselect_all"
    bl_label = "Deselect All Bulk Routes"

    def execute(self, context):
        settings: BulkSettings = getattr(context.scene, "cashcab_bulk", None)
        if settings is None:
            return {"CANCELLED"}
        for route in settings.routes:
            route.selected = False
        return {"FINISHED"}


class BLOSM_OT_BulkToggleGroup(bpy.types.Operator):
    bl_idname = "blosm.bulk_toggle_group"
    bl_label = "Toggle Bulk Group"

    group_key: bpy.props.StringProperty(name="Group Key", default="")

    def execute(self, context):
        settings: BulkSettings = getattr(context.scene, "cashcab_bulk", None)
        if settings is None:
            return {"CANCELLED"}

        key = (self.group_key or "").strip()
        if not key:
            return {"CANCELLED"}

        current = [k for k in (settings.expanded_groups or "").split(",") if k]
        if key in current:
            current = [k for k in current if k != key]
        else:
            current.append(key)
        settings.expanded_groups = ",".join(current)
        return {"FINISHED"}


class BLOSM_OT_BulkRunSelected(bpy.types.Operator):
    bl_idname = "blosm.bulk_run_selected"
    bl_label = "Run Selected Bulk Routes"

    _timer = None
    _queue: List[int] = []
    _process = None
    _log_handle = None

    def execute(self, context):
        scene = context.scene
        settings: BulkSettings = getattr(scene, "cashcab_bulk", None)
        if settings is None:
            self.report({"ERROR"}, "Bulk settings missing")
            return {"CANCELLED"}

        if settings.is_running:
            self.report({"WARNING"}, "Bulk run already active")
            return {"CANCELLED"}

        selected_indices = [idx for idx, item in enumerate(settings.routes) if item.selected]
        if not selected_indices:
            self.report({"ERROR"}, "No routes selected")
            return {"CANCELLED"}

        output_raw = (settings.output_dir or "").strip()
        if not output_raw:
            self.report({"ERROR"}, "Output directory is empty")
            return {"CANCELLED"}

        output_dir = Path(bpy.path.abspath(output_raw)).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        if not _base_blend_path().exists():
            self.report({"ERROR"}, f"Base blend missing: {_base_blend_path()}")
            return {"CANCELLED"}

        log_root = Path(tempfile.gettempdir()) / "cashcab_bulk_native" / time.strftime("%Y%m%d_%H%M%S")
        log_root.mkdir(parents=True, exist_ok=True)

        settings.is_running = True
        settings.progress_total = len(selected_indices)
        settings.progress_done = 0
        settings.current_shot = ""
        settings.log_root = str(log_root)

        for route in settings.routes:
            if route.selected:
                route.run_state = "IDLE"
                route.log_message = ""

        self._queue = selected_indices
        self._process = None
        self._log_handle = None

        if bpy.app.background or getattr(context, "window", None) is None:
            return self._run_headless(context)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        self.report({"INFO"}, f"Starting bulk run with {len(selected_indices)} routes")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        settings: BulkSettings = getattr(context.scene, "cashcab_bulk", None)
        if settings is None:
            self._cleanup_timer(context)
            return {"CANCELLED"}

        if not settings.is_running:
            self._cleanup_timer(context)
            return {"CANCELLED"}

        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        if self._process is None:
            return self._start_next(context)

        if self._process.poll() is None:
            return {"RUNNING_MODAL"}

        exit_code = int(self._process.poll() or 0)
        self._finalize_current(settings, exit_code)
        return self._start_next(context)

    def _start_next(self, context):
        settings: BulkSettings = getattr(context.scene, "cashcab_bulk", None)
        if settings is None:
            return {"CANCELLED"}

        if not self._queue:
            settings.is_running = False
            settings.current_shot = ""
            self._cleanup_timer(context)
            self.report({"INFO"}, "Bulk run completed")
            return {"FINISHED"}

        index = self._queue.pop(0)
        if index < 0 or index >= len(settings.routes):
            return {"RUNNING_MODAL"}

        route = settings.routes[index]
        route.run_state = "RUNNING"
        settings.current_shot = route.shot_code

        log_root = Path(settings.log_root or tempfile.gettempdir())
        log_root.mkdir(parents=True, exist_ok=True)
        log_path = log_root / f"{route.shot_code}_{_address_slug(route.start_address)}_to_{_address_slug(route.end_address)}.log"

        try:
            output_dir = Path(bpy.path.abspath(settings.output_dir)).resolve()
            shot_dir = output_dir / (route.shot_code or "UNKNOWN")
            shot_dir.mkdir(parents=True, exist_ok=True)

            version = (settings.version_label or "V01").strip() or "V01"
            filename = (
                f"{route.shot_code}_"
                f"{_address_slug(route.start_address)}_to_{_address_slug(route.end_address)}_"
                f"{version}.blend"
            )
            output_path = shot_dir / filename

            job = {
                "shot_code": route.shot_code,
                "start_address": route.start_address,
                "end_address": route.end_address,
                "start_coords": route.start_coords,
                "end_coords": route.end_coords,
                "output_path": str(output_path),
                "auto_snap": bool(settings.auto_snap_addresses),
                "google_api_key": _resolve_google_api_key(context),
                "transfer": _snapshot_regular_import_settings(context),
            }

            blender_bin = bpy.app.binary_path
            worker_script = _worker_script_path()
            cmd = _build_worker_cmd(
                blender_bin=blender_bin,
                worker_script=worker_script,
                job=job,
            )

            self._log_handle = open(log_path, "w", encoding="utf-8")
            self._process = subprocess.Popen(cmd, stdout=self._log_handle, stderr=subprocess.STDOUT)
        except Exception as exc:
            route.run_state = "ERROR"
            route.log_message = str(exc)
            try:
                log_path.write_text(f"[BulkRunner] ERROR: {exc}\n", encoding="utf-8")
            except Exception:
                pass
            try:
                if self._log_handle is not None:
                    self._log_handle.close()
            except Exception:
                pass
            self._log_handle = None
            self._process = None
            settings.progress_done = min(settings.progress_total, settings.progress_done + 1)
            settings.current_shot = ""
            return {"RUNNING_MODAL"}

        return {"RUNNING_MODAL"}

    def _finalize_current(self, settings: BulkSettings, exit_code: int) -> None:
        current = settings.current_shot
        for route in settings.routes:
            if route.shot_code != current:
                continue
            if exit_code == 0:
                # Validate output exists (guard against "empty folders, no errors")
                try:
                    output_dir = Path(bpy.path.abspath(settings.output_dir)).resolve()
                    shot_dir = output_dir / (route.shot_code or "UNKNOWN")
                    version = (settings.version_label or "V01").strip() or "V01"
                    filename = (
                        f"{route.shot_code}_"
                        f"{_address_slug(route.start_address)}_to_{_address_slug(route.end_address)}_"
                        f"{version}.blend"
                    )
                    output_path = shot_dir / filename
                    if not output_path.exists():
                        route.run_state = "ERROR"
                        route.log_message = "Worker exited 0 but output .blend missing"
                    else:
                        route.run_state = "DONE"
                        route.log_message = ""
                except Exception as exc:
                    route.run_state = "ERROR"
                    route.log_message = f"Post-run validation failed: {exc}"
            else:
                route.run_state = "ERROR"
                route.log_message = f"Exit code {exit_code}"
            break

        settings.progress_done = min(settings.progress_total, settings.progress_done + 1)
        settings.current_shot = ""

        try:
            if self._log_handle is not None:
                self._log_handle.close()
        except Exception:
            pass

        self._log_handle = None
        self._process = None

    def _cleanup_timer(self, context):
        wm = context.window_manager
        if self._timer is not None:
            try:
                wm.event_timer_remove(self._timer)
            except Exception:
                pass
            self._timer = None

    def _run_headless(self, context):
        settings: BulkSettings = getattr(context.scene, "cashcab_bulk", None)
        if settings is None:
            return {"CANCELLED"}
        self.report({"INFO"}, f"Starting headless bulk run with {settings.progress_total} routes")
        while settings.is_running:
            if self._process is None:
                self._start_next(context)
            else:
                if self._process.poll() is None:
                    time.sleep(0.5)
                    continue
                exit_code = int(self._process.poll() or 0)
                self._finalize_current(settings, exit_code)
            if not self._queue and self._process is None:
                settings.is_running = False
                settings.current_shot = ""
        return {"FINISHED"}
