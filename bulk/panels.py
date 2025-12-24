from __future__ import annotations

import datetime
import re

import bpy

from .properties import BulkSettings


def _shorten(text: str, max_len: int) -> str:
    clean = (text or "").strip()
    if len(clean) <= max_len:
        return clean
    return clean[: max(0, max_len - 3)].rstrip() + "..."


def _run_state_icon(run_state: str) -> str:
    if run_state == "DONE":
        return "CHECKMARK"
    if run_state == "ERROR":
        return "ERROR"
    if run_state == "RUNNING":
        return "TIME"
    return "NONE"


def _group_key(settings: BulkSettings, route) -> str:
    if settings.group_by == "DATE":
        return (route.due_date or "").strip() or "(no date)"
    if settings.group_by == "STATUS":
        return (route.sheet_status or "").strip() or "(no status)"
    return ""


_DATE_FORMATS = (
    "%B %d, %Y",
    "%b %d, %Y",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%Y",
)

_DATE_CLEAN_RE = re.compile(r"[^\w\s,/-]")


def _date_sort_key(date_str: str) -> tuple:
    if not date_str:
        return (9999, 12, 31, "")
    cleaned = _DATE_CLEAN_RE.sub("", date_str.strip())
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.datetime.strptime(cleaned, fmt).date()
            return (parsed.year, parsed.month, parsed.day, cleaned)
        except ValueError:
            continue
    match = re.search(r"\b(20\d{2})\b", cleaned)
    if match:
        year = int(match.group(1))
        return (year, 12, 31, cleaned)
    return (9999, 12, 31, cleaned)


def _expanded_keys(settings: BulkSettings) -> set:
    return {k for k in (settings.expanded_groups or "").split(",") if k}


def _group_token(key: str) -> str:
    return (key or "").replace(",", "%2C")


def _draw_route_row(layout, route, settings: BulkSettings):
    row = layout.row(align=True)
    row.prop(route, "selected", text="")
    row.label(text=route.shot_code or "(no code)")
    row.label(text=_shorten(route.start_address, 22))
    row.label(text=_shorten(route.end_address, 22))
    if settings.auto_snap_addresses:
        row.label(text=_shorten(route.start_coords, 14))
        row.label(text=_shorten(route.end_coords, 14))
    status_text = (route.sheet_status or "").strip() or "-"
    icon = _run_state_icon(route.run_state)
    if icon == "NONE":
        row.label(text=status_text)
    else:
        if route.run_state == "ERROR" and (route.log_message or "").strip():
            row.label(text=f"{status_text} | {_shorten(route.log_message, 26)}", icon=icon)
        else:
            row.label(text=status_text, icon=icon)


class BLOSM_UL_BulkRoutes(bpy.types.UIList):
    bl_idname = "BLOSM_UL_BulkRoutes"

    def draw_item(self, context, layout, data, item, icon, active_data, active_prop):
        settings: BulkSettings = getattr(context.scene, "cashcab_bulk", None)
        if settings is None:
            return
        _draw_route_row(layout, item, settings)


class BLOSM_PT_BulkImport(bpy.types.Panel):
    bl_idname = "BLOSM_PT_BulkImport"
    bl_label = "Bulk Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CashCab"
    bl_parent_id = "BLOSM_PT_RouteImport"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings: BulkSettings = getattr(scene, "cashcab_bulk", None)
        if settings is None:
            layout.label(text="Bulk settings missing", icon="ERROR")
            return

        # Summary box at top
        summary_box = layout.box()
        summary_header = summary_box.row(align=True)
        summary_header.label(text="Bulk Import Summary", icon="SEQUENCE")

        total = len(settings.routes)
        selected = sum(1 for item in settings.routes if item.selected)
        done = sum(1 for item in settings.routes if item.run_state == "DONE")
        errors = sum(1 for item in settings.routes if item.run_state == "ERROR")

        summary_row = summary_box.row(align=True)
        summary_row.label(text=f"Routes: {total} | Selected: {selected} | Done: {done} | Errors: {errors}", icon="INFO")

        if settings.is_running:
            summary_box.label(text=f"Running: {settings.current_shot} ({settings.progress_done}/{settings.progress_total})", icon="TIME")
        elif settings.output_dir:
            summary_box.label(text=f"Output: {settings.version_label} → {_shorten(settings.output_dir, 30)}", icon="FILE_FOLDER")

        if settings.manifest_source == "GOOGLE_SHEET" and settings.google_sheet_url:
            sheet_id = settings.google_sheet_url.split("/d/")[-1].split("/")[0][:12]
            summary_box.label(text=f"Sheet: {sheet_id}...", icon="URL")

        layout.separator()

        source_box = layout.box()
        source_box.label(text="Manifest Source", icon="FILE")
        source_box.prop(settings, "manifest_source", text="")
        if settings.manifest_source == "GOOGLE_SHEET":
            source_box.prop(settings, "google_sheet_url", text="URL")
        else:
            source_box.prop(settings, "local_file_path", text="CSV")
        source_box.operator("blosm.bulk_fetch_manifest", text="Fetch Manifest", icon="FILE_REFRESH")

        batch_box = layout.box()
        batch_box.label(text="Batch Settings", icon="SEQUENCE")
        batch_box.prop(settings, "output_dir")
        batch_box.prop(settings, "version_label")
        batch_box.prop(settings, "auto_snap_addresses", text="Auto Snap")

        options_box = layout.box()
        options_box.label(text="Grouping", icon="SORTALPHA")
        options_box.prop(settings, "group_by", text="Group By")
        options_box.prop(settings, "group_reverse", text="Reverse")

        defaults_box = layout.box()
        defaults_box.label(text="Default CashCab Settings", icon="PREFERENCES")
        addon = getattr(scene, "blosm", None)
        if addon is None:
            defaults_box.label(text="CashCab settings unavailable", icon="ERROR")
        else:
            defaults_box.prop(addon, "route_padding_m")
            defaults_box.prop(addon, "route_create_preview_animation")
            defaults_box.prop(addon, "route_generate_camera")

        layout.separator()

        if settings.group_by == "NONE":
            layout.template_list(
                "BLOSM_UL_BulkRoutes",
                "",
                settings,
                "routes",
                settings,
                "active_route_index",
                rows=6,
            )
        else:
            grouped = {}
            for route in settings.routes:
                key = _group_key(settings, route)
                grouped.setdefault(key, []).append(route)

            expanded = _expanded_keys(settings)
            if settings.group_by == "DATE":
                keys = sorted(grouped.keys(), key=_date_sort_key)
            else:
                keys = sorted(grouped.keys())
            if settings.group_reverse:
                keys = list(reversed(keys))

            for key in keys:
                header = layout.row(align=True)
                token = _group_token(key)
                is_open = token in expanded
                icon = "TRIA_DOWN" if is_open else "TRIA_RIGHT"
                op = header.operator("blosm.bulk_toggle_group", text="", icon=icon)
                op.group_key = token
                header.label(text=f"{key} ({len(grouped[key])})")

                if is_open:
                    box = layout.box()
                    for route in grouped[key]:
                        _draw_route_row(box, route, settings)

        row = layout.row(align=True)
        row.operator("blosm.bulk_select_all", text="Select All", icon="CHECKMARK")
        row.operator("blosm.bulk_deselect_all", text="Deselect All", icon="X")

        row = layout.row(align=True)
        row.enabled = not settings.is_running
        row.operator("blosm.bulk_run_selected", text="Run Selected", icon="PLAY")

        if settings.is_running:
            progress = layout.box()
            progress.label(
                text=f"Running: {settings.current_shot} ({settings.progress_done}/{settings.progress_total})",
                icon="TIME",
            )
            if settings.log_root:
                progress.label(text=f"Logs: {settings.log_root}", icon="TEXT")
