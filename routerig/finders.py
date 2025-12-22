from __future__ import annotations

import bpy


def _name_matches(canonical: str, actual: str) -> bool:
    if actual == canonical:
        return True
    if actual.startswith(canonical + ".") or actual.startswith(canonical + "_"):
        return True
    c = canonical.casefold()
    a = actual.casefold()
    if a == c:
        return True
    if a.startswith(c + ".") or a.startswith(c + "_"):
        return True
    return False


def find_object(canonical_name: str) -> bpy.types.Object | None:
    # Fast path exact hit
    obj = bpy.data.objects.get(canonical_name)
    if obj is not None:
        return obj
    for o in bpy.data.objects:
        if _name_matches(canonical_name, o.name):
            return o
    return None


def find_object_any(candidates: list[str]) -> bpy.types.Object | None:
    for name in candidates:
        obj = find_object(name)
        if obj is not None:
            return obj
    return None


def find_collection(canonical_name: str) -> bpy.types.Collection | None:
    col = bpy.data.collections.get(canonical_name)
    if col is not None:
        return col
    for c in bpy.data.collections:
        if _name_matches(canonical_name, c.name):
            return c
    return None
