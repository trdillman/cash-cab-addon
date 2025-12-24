RouteRig Timeline Auto-Adapt (Notes)

Goal
- RouteRig camera should preserve the same “relative timing” of its style beats (anchors/weights/pitch/ortho behavior) even if the scene’s animation window changes.

Interpretation (what “auto-adapt” means)
- Treat the style profile’s timeline (keyframes, active_end, total) as a normalized schedule.
- Map that schedule onto the shot’s actual animation window (e.g. scene.blosm_anim_start/end or scene.frame_start/end).
- Preserve relative pacing between anchors (MARKER_START/MARKER_END), route window, and CAR_LEAD framing.
- Ensure the camera does not “hold” while the car is still moving (if car/route ends later than profile frame_active_end, extend active_end or add a terminal key).

Constraints / Expectations
- Default behavior should match current style profile output when the shot uses the standard timing.
- When timing differs (e.g. 15–150 vs longer), camera keys should be re-timed (stretched/compressed), not re-authored.

