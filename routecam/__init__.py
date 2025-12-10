"""
RouteCam Combo (Unified)
========================
"""
bl_info = {
    "name": "RouteCam Ultimate",
    "author": "RouteCam System",
    "version": (3, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > RouteCam",
    "description": "Unified Route Camera System (Robust + Viz Modes)",
    "category": "Camera",
}

import bpy
from . import blender_ops

def register():
    blender_ops.register()

def unregister():
    blender_ops.unregister()
