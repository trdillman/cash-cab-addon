import unittest

from mathutils import Vector

from cash_cab_addon.route.geometry_simplifier import trim_end_uturns


class TestRouteUTurnTrim(unittest.TestCase):
    def test_trim_start_uturn(self):
        # U-turn cluster near the start, then a long straight run.
        pts = [
            Vector((0.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((10.0, 10.0, 0.0)),
            Vector((0.0, 10.0, 0.0)),     # after the two 90° corners, heading back
            Vector((-340.0, 10.0, 0.0)),  # long run to ensure the u-turn is within the first 10%
        ]

        out = trim_end_uturns(pts)
        self.assertLess(len(out), len(pts))
        self.assertEqual(tuple(out[0]), tuple(pts[3]))
        self.assertEqual(tuple(out[-1]), tuple(pts[-1]))

    def test_trim_end_uturn(self):
        # Long straight run, then a tight u-turn cluster near the end.
        pts = [
            Vector((0.0, 0.0, 0.0)),
            Vector((300.0, 0.0, 0.0)),
            Vector((600.0, 0.0, 0.0)),
            Vector((880.0, 0.0, 0.0)),
            Vector((900.0, 0.0, 0.0)),
            Vector((900.0, 10.0, 0.0)),
            Vector((850.0, 10.0, 0.0)),
        ]

        out = trim_end_uturns(pts)
        self.assertLess(len(out), len(pts))
        # End should be cut before the u-turn loop begins (keep the first-corner point).
        self.assertEqual(tuple(out[-1]), tuple(pts[4]))

    def test_mid_route_uturn_not_trimmed(self):
        pts = [
            Vector((0.0, 0.0, 0.0)),
            Vector((200.0, 0.0, 0.0)),
            Vector((200.0, 10.0, 0.0)),
            Vector((150.0, 10.0, 0.0)),
            Vector((150.0, 0.0, 0.0)),
            Vector((700.0, 0.0, 0.0)),
        ]

        out = trim_end_uturns(pts)
        self.assertEqual(len(out), len(pts))
        self.assertEqual(tuple(out[0]), tuple(pts[0]))
        self.assertEqual(tuple(out[-1]), tuple(pts[-1]))

    def test_short_routes_unchanged(self):
        pts = [Vector((0.0, 0.0, 0.0)), Vector((1.0, 0.0, 0.0)), Vector((2.0, 0.0, 0.0))]
        out = trim_end_uturns(pts)
        self.assertIs(out, pts)

    def test_window_fraction_can_disable_detection(self):
        # With a tiny window, the corner cluster isn't inside the analysis region.
        pts = [
            Vector((0.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((10.0, 10.0, 0.0)),
            Vector((0.0, 10.0, 0.0)),
            Vector((-340.0, 10.0, 0.0)),
        ]
        out = trim_end_uturns(pts, window_fraction=0.001)
        self.assertEqual(len(out), len(pts))

    def test_corner_angle_threshold_can_disable_detection(self):
        pts = [
            Vector((0.0, 0.0, 0.0)),
            Vector((10.0, 0.0, 0.0)),
            Vector((10.0, 10.0, 0.0)),
            Vector((0.0, 10.0, 0.0)),
            Vector((-340.0, 10.0, 0.0)),
        ]
        out = trim_end_uturns(pts, corner_angle_min=179.0)
        self.assertEqual(len(out), len(pts))
