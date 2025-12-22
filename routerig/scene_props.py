from __future__ import annotations

import bpy


class ROUTERIG_SceneSettings(bpy.types.PropertyGroup):
    frame_active_end: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Active End Frame",
        default=160,
        min=1,
    )
    frame_total: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Total Frames",
        default=160,
        min=1,
    )
    sample_step: bpy.props.IntProperty(  # type: ignore[valid-type]
        name="Sample Step",
        default=5,
        min=1,
        description="Frame step for analysis sampling (lower is slower but more detailed)",
    )

    report_dir: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="Report Folder",
        default="//routerig_reports",
        subtype="DIR_PATH",
        description="Relative paths are resolved from the .blend file location",
    )

