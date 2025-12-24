from __future__ import annotations

import bpy


class BulkRouteItem(bpy.types.PropertyGroup):
    selected: bpy.props.BoolProperty(name="Selected", default=False)
    shot_code: bpy.props.StringProperty(name="Shot Code", default="")
    start_address: bpy.props.StringProperty(name="Start Address", default="")
    end_address: bpy.props.StringProperty(name="End Address", default="")
    start_coords: bpy.props.StringProperty(name="Start Coords", default="")
    end_coords: bpy.props.StringProperty(name="End Coords", default="")
    due_date: bpy.props.StringProperty(name="Due Date", default="")
    sheet_status: bpy.props.StringProperty(name="Sheet Status", default="")
    run_state: bpy.props.EnumProperty(
        name="Run State",
        items=(
            ("IDLE", "Idle", "Idle"),
            ("RUNNING", "Running", "Running"),
            ("DONE", "Done", "Done"),
            ("ERROR", "Error", "Error"),
        ),
        default="IDLE",
    )
    log_message: bpy.props.StringProperty(name="Log Message", default="")


class BulkSettings(bpy.types.PropertyGroup):
    manifest_source: bpy.props.EnumProperty(
        name="Source",
        items=(
            ("GOOGLE_SHEET", "Google Sheet", "Google Sheet URL (CSV export)"),
            ("LOCAL_FILE", "Local CSV", "Local CSV file"),
        ),
        default="GOOGLE_SHEET",
    )
    google_sheet_url: bpy.props.StringProperty(
        name="Google Sheet URL",
        default="https://docs.google.com/spreadsheets/d/1pAwg48JmUM88VjrBulA8L6Qe8AqkIFD0RzaSGjoyg-U/edit?gid=967871266#gid=967871266",
    )
    local_file_path: bpy.props.StringProperty(
        name="Local CSV",
        subtype="FILE_PATH",
        default="",
    )
    output_dir: bpy.props.StringProperty(
        name="Output Directory",
        subtype="DIR_PATH",
        default="",
    )
    version_label: bpy.props.StringProperty(
        name="Version Label",
        default="V01",
    )
    auto_snap_addresses: bpy.props.BoolProperty(
        name="Auto Snap",
        description="Use CashCab auto-snap settings when importing routes",
        default=True,
    )
    group_by: bpy.props.EnumProperty(
        name="Group By",
        items=(
            ("NONE", "None", "No grouping"),
            ("DATE", "Due Date", "Group by due date"),
            ("STATUS", "Sheet Status", "Group by sheet status"),
        ),
        default="NONE",
    )
    group_reverse: bpy.props.BoolProperty(
        name="Reverse Order",
        description="Reverse group order",
        default=False,
    )
    expanded_groups: bpy.props.StringProperty(
        name="Expanded Groups",
        description="Comma-separated list of expanded group keys",
        default="",
    )

    routes: bpy.props.CollectionProperty(type=BulkRouteItem)
    active_route_index: bpy.props.IntProperty(default=0)

    is_running: bpy.props.BoolProperty(name="Running", default=False)
    progress_total: bpy.props.IntProperty(name="Total", default=0)
    progress_done: bpy.props.IntProperty(name="Done", default=0)
    current_shot: bpy.props.StringProperty(name="Current Shot", default="")
    log_root: bpy.props.StringProperty(name="Log Root", default="")
