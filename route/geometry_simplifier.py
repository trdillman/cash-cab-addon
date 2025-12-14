"""
Route geometry helpers.

This module is intentionally pure math/geometry (no bpy dependency) so it can be
unit-tested in Blender headless runs.
"""

from __future__ import annotations

from math import acos, degrees
from typing import List, Optional, Sequence, Tuple

try:
    from mathutils import Vector
except Exception:  # pragma: no cover
    Vector = None  # type: ignore


def _clamp(x: float, lo: float, hi: float) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def _as_vectors(points: Sequence["Vector"]) -> List["Vector"]:
    if Vector is None:  # pragma: no cover
        raise RuntimeError("mathutils.Vector is not available; this function must run inside Blender.")
    return [p if isinstance(p, Vector) else Vector(p) for p in points]


def _arc_lengths(points: Sequence["Vector"]) -> Tuple[List[float], float]:
    if len(points) < 2:
        return [0.0] * len(points), 0.0
    s = [0.0]
    total = 0.0
    for i in range(1, len(points)):
        seg = (points[i] - points[i - 1]).length
        total += float(seg)
        s.append(total)
    return s, total


def _turn_angles(points: Sequence["Vector"]) -> List[float]:
    n = len(points)
    angles = [0.0] * n
    if n < 3:
        return angles

    for i in range(1, n - 1):
        a = points[i] - points[i - 1]
        b = points[i + 1] - points[i]
        if a.length < 1e-8 or b.length < 1e-8:
            angles[i] = 0.0
            continue
        v_prev = a.normalized()
        v_next = b.normalized()
        dot_v = _clamp(float(v_prev.dot(v_next)), -1.0, 1.0)
        angles[i] = degrees(acos(dot_v))
    return angles


def _window_end_index(s: Sequence[float], max_s: float) -> int:
    # Largest index with s[i] <= max_s
    idx = 0
    for i, val in enumerate(s):
        if val <= max_s:
            idx = i
        else:
            break
    return idx


def _window_start_index(s: Sequence[float], min_s: float) -> int:
    # Smallest index with s[i] >= min_s
    for i, val in enumerate(s):
        if val >= min_s:
            return i
    return max(0, len(s) - 1)


def _direction(points: Sequence["Vector"], a: int, b: int) -> Optional["Vector"]:
    if a < 0 or b < 0 or a >= len(points) or b >= len(points) or a == b:
        return None
    v = points[b] - points[a]
    if v.length < 1e-8:
        return None
    return v.normalized()


def trim_end_uturns(
    points: List["Vector"],
    *,
    window_fraction: float = 0.10,
    corner_angle_min: float = 70.0,
    direction_reverse_deg: float = 150.0,
    max_uturn_fraction: float = 0.10,
) -> List["Vector"]:
    """Detect and trim U-turn-like loops at the start/end of a route.

    - window_fraction: fraction of total length to analyze at each end (e.g. 0.1 = 10%).
    - corner_angle_min: minimum angle (in degrees) to treat as a candidate right-angle corner.
    - direction_reverse_deg: minimum angle between net start and end directions to treat as a U-turn.
    - max_uturn_fraction: max fraction of total length allowed for the U-turn region; prevents trimming mid-route hairpins.

    Returns a new list of points; if no U-turn detected, returns the original points unchanged.
    """

    pts = _as_vectors(points)
    n = len(pts)
    if n < 4:
        return points

    s, total_len = _arc_lengths(pts)
    if total_len < 1e-6:
        return points

    min_remaining_fraction = 0.20
    min_remaining_length = 50.0

    def safe_enough_after_cut(cut_idx: int) -> bool:
        remaining = total_len - s[cut_idx]
        return remaining >= min(min_remaining_length, total_len * min_remaining_fraction)

    def safe_enough_before_cut(cut_idx: int) -> bool:
        kept = s[cut_idx]
        return kept >= min(min_remaining_length, total_len * min_remaining_fraction)

    angles = _turn_angles(pts)
    window_len = max(0.0, float(window_fraction)) * total_len

    # ---- Start trimming: cut AFTER the detected U-turn cluster ----
    start_max_idx = _window_end_index(s, window_len)
    start_cut: Optional[int] = None
    if start_max_idx >= 3:
        corner_idxs = [i for i in range(1, start_max_idx) if angles[i] >= corner_angle_min]
        if len(corner_idxs) >= 2:
            for i, j in zip(corner_idxs, corner_idxs[1:]):
                j1 = min(j + 1, n - 1)
                i0 = max(i - 1, 0)
                uturn_len = s[j1] - s[i0]
                if uturn_len > max_uturn_fraction * total_len:
                    continue
                dir_before = _direction(pts, i - 1, i)
                dir_after = _direction(pts, j, j1)
                if dir_before is None or dir_after is None:
                    continue
                dot_ba = _clamp(float(dir_before.dot(dir_after)), -1.0, 1.0)
                angle_ba = degrees(acos(dot_ba))
                if angle_ba < direction_reverse_deg:
                    continue
                # Start U-turn found: skip everything up through j+1
                if j1 < n - 1 and safe_enough_after_cut(j1):
                    start_cut = j1
                break

    if start_cut is not None and start_cut > 0:
        pts = pts[start_cut:]
        n = len(pts)
        if n < 4:
            return pts
        s, total_len = _arc_lengths(pts)
        angles = _turn_angles(pts)
        if total_len < 1e-6:
            return pts
        window_len = max(0.0, float(window_fraction)) * total_len

    # ---- End trimming: cut BEFORE the detected U-turn cluster ----
    end_min_idx = _window_start_index(s, max(0.0, total_len - window_len))
    end_cut: Optional[int] = None
    if end_min_idx <= n - 4:
        corner_idxs = [i for i in range(end_min_idx, n - 1) if angles[i] >= corner_angle_min]
        if len(corner_idxs) >= 2:
            for i, j in zip(corner_idxs, corner_idxs[1:]):
                i0 = max(i - 1, 0)
                j1 = min(j + 1, n - 1)
                uturn_len = s[j1] - s[i0]
                if uturn_len > max_uturn_fraction * total_len:
                    continue
                dir_before = _direction(pts, i - 1, i)
                dir_after = _direction(pts, j, j1)
                if dir_before is None or dir_after is None:
                    continue
                dot_ba = _clamp(float(dir_before.dot(dir_after)), -1.0, 1.0)
                angle_ba = degrees(acos(dot_ba))
                if angle_ba < direction_reverse_deg:
                    continue
                # End U-turn found: keep up through the first corner point (i)
                if i < n - 1 and safe_enough_before_cut(i):
                    end_cut = i
                break

    if end_cut is not None and end_cut < n - 1:
        return pts[: end_cut + 1]

    return points

