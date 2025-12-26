from __future__ import annotations

import bpy
from . import ops, scene_props

def register():
    bpy.utils.register_class(scene_props.ROUTERIG_SceneSettings)
    bpy.types.Scene.routerig = bpy.props.PointerProperty(type=scene_props.ROUTERIG_SceneSettings)
    
    bpy.utils.register_class(ops.ROUTERIG_OT_validate_scene)
    bpy.utils.register_class(ops.ROUTERIG_OT_export_scene_summary)
    bpy.utils.register_class(ops.ROUTERIG_OT_spawn_test_camera)
    bpy.utils.register_class(ops.ROUTERIG_OT_generate_camera_animation)
    bpy.utils.register_class(ops.ROUTERIG_OT_spawn_new_camera)
    bpy.utils.register_class(ops.ROUTERIG_OT_spawn_variant_cameras)

def unregister():
    bpy.utils.unregister_class(ops.ROUTERIG_OT_spawn_variant_cameras)
    bpy.utils.unregister_class(ops.ROUTERIG_OT_spawn_new_camera)
    bpy.utils.unregister_class(ops.ROUTERIG_OT_generate_camera_animation)
    bpy.utils.unregister_class(ops.ROUTERIG_OT_spawn_test_camera)
    bpy.utils.unregister_class(ops.ROUTERIG_OT_export_scene_summary)
    bpy.utils.unregister_class(ops.ROUTERIG_OT_validate_scene)
    
    del bpy.types.Scene.routerig
    bpy.utils.unregister_class(scene_props.ROUTERIG_SceneSettings)
