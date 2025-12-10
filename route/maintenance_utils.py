"""Miscellaneous maintenance helpers for BLOSM."""

from __future__ import annotations

import bpy

from . import anim as route_anim


def refresh_follow_drivers(scene: bpy.types.Scene | None = None) -> dict[str, bool]:
    """Manual entry point to refresh follow-path drivers."""
    return route_anim.force_follow_keyframes(scene)
