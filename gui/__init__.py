"""
CashCab Route Import - GUI Module
Minimal GUI registration for route import functionality.
"""

import bpy
from bpy.app.handlers import persistent

from .properties import BlosmRouteWaypoint, BlosmDefaultLevelsEntry, BlosmProperties
from .panels import (
    BLOSM_UL_DefaultLevels,
    BLOSM_PT_RouteImport,
)
from .operators import (
    BLOSM_OT_AddWaypoint,
    BLOSM_OT_RemoveWaypoint,
    BLOSM_OT_LevelsAdd,
    BLOSM_OT_LevelsDelete,
    BLOSM_OT_SetViewportClip,
    BLOSM_OT_AssetsUpdateNotice,
    BLOSM_OT_ApplyUTurnTrim,
)
from .cleanup_operator import BLOSM_OT_CleanAndClear


# default number of levels and its relative weight
_defaultLevels = (
    (4, 10),
    (5, 40),
    (6, 10)
)


def addDefaultLevels():
    defaultLevels = bpy.context.scene.blosm.defaultLevels
    if not defaultLevels:
        for n, w in _defaultLevels:
            e = defaultLevels.add()
            e.levels = n
            e.weight = w


# This handler is needed to set the defaults for <context.scene.blosm.defaultLevels>
# just after the addon registration
def _onRegister(scene):
    addDefaultLevels()
    # the handler isn't needed anymore, so we remove it
    bpy.app.handlers.scene_update_post.remove(_onRegister)


def _onRegister280():
    addDefaultLevels()
    return


# This handler is needed to set the defaults for <context.scene.blosm.defaultLevels>
# after each start of Blender or reloading the start-up file via Ctrl N or loading any Blender file.
# That's why the persistent decorator is used
@persistent
def _onFileLoaded(scene):
    addDefaultLevels()


# Classes to register
_classes = (
    BlosmRouteWaypoint,
    BlosmDefaultLevelsEntry,
    BLOSM_UL_DefaultLevels,
    BLOSM_OT_AddWaypoint,
    BLOSM_OT_RemoveWaypoint,
    BLOSM_OT_LevelsAdd,
    BLOSM_OT_LevelsDelete,
    BLOSM_OT_SetViewportClip,
    BLOSM_OT_AssetsUpdateNotice,
    BLOSM_OT_ApplyUTurnTrim,
    BLOSM_OT_CleanAndClear,
    BLOSM_PT_RouteImport,
    BlosmProperties
)



def register():
    """Register all GUI classes and initialize properties"""
    print("[DEBUG] gui.register called")
    for cls in _classes:
        bpy.utils.register_class(cls)

    # Create scene property group
    print("[DEBUG] Registering Scene.blosm property")
    bpy.types.Scene.blosm = bpy.props.PointerProperty(type=BlosmProperties)

    # Initialize default levels after a short delay
    bpy.app.timers.register(_onRegister280, first_interval=0.5)


def unregister():
    """Unregister all GUI classes and cleanup"""
    # Remove scene property first if it exists
    if hasattr(bpy.types.Scene, "blosm"):
        try:
            del bpy.types.Scene.blosm
        except Exception:
            # Safe to ignore; indicates it was already removed
            pass

    # Unregister classes defensively; Blender may already have
    # unregistered some classes when reloading or disabling addons.
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            # Class was not registered or was already unregistered
            continue
        except Exception:
            # Avoid hard failures during shutdown/unload
            continue
