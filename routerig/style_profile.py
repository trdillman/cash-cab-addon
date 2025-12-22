from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Keyframe1D:
    frame: int
    value: float


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def eval_keys(keys: list[Keyframe1D], frame: int) -> float:
    if not keys:
        raise ValueError("No keys")
    if frame <= keys[0].frame:
        return keys[0].value
    if frame >= keys[-1].frame:
        return keys[-1].value
    for a, b in zip(keys, keys[1:]):
        if a.frame <= frame <= b.frame:
            t = (frame - a.frame) / float(b.frame - a.frame)
            return _lerp(a.value, b.value, t)
    return keys[-1].value


def load_default_profile() -> dict:
    here = Path(__file__).resolve().parent
    learned = here / "style_profile_learned.json"
    if learned.exists():
        return json.loads(learned.read_text(encoding="utf-8"))

    path = here / "style_profile_default.json"
    return json.loads(path.read_text(encoding="utf-8"))
