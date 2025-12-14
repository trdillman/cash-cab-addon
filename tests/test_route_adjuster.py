import unittest

import bpy
from mathutils import Vector


def _load_local_addon() -> None:
    # Force-load addon package from this worktree, not from any installed addon path.
    import importlib.util
    import sys
    from pathlib import Path

    addon_dir = Path(__file__).resolve().parent.parent
    init_path = addon_dir / "__init__.py"

    spec = importlib.util.spec_from_file_location(
        "cash_cab_addon",
        init_path,
        submodule_search_locations=[str(addon_dir)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["cash_cab_addon"] = module
    spec.loader.exec_module(module)


class TestRouteAdjuster(unittest.TestCase):
    def test_ensure_controls_creates_empties(self):
        _load_local_addon()
        import cash_cab_addon.route.route_adjuster as route_adjuster

        scene = bpy.context.scene

        curve = bpy.data.curves.new("ROUTE_DATA", type="CURVE")
        curve.dimensions = "3D"
        spline = curve.splines.new("POLY")
        spline.points.add(1)
        spline.points[0].co = (0.0, 0.0, 0.0, 1.0)
        spline.points[1].co = (100.0, 0.0, 0.0, 1.0)

        route_obj = bpy.data.objects.new("ROUTE", curve)
        scene.collection.objects.link(route_obj)

        ok = route_adjuster.ensure_route_control_empties(scene)
        self.assertTrue(ok)

        start = bpy.data.objects.get(route_adjuster.CTRL_START_NAME)
        end = bpy.data.objects.get(route_adjuster.CTRL_END_NAME)
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)

        coll = bpy.data.collections.get(route_adjuster.CONTROL_COLLECTION_NAME)
        self.assertIsNotNone(coll)
        self.assertIn(start.name, coll.objects)
        self.assertIn(end.name, coll.objects)

        bpy.data.objects.remove(start, do_unlink=True)
        bpy.data.objects.remove(end, do_unlink=True)
        bpy.data.objects.remove(route_obj, do_unlink=True)
        bpy.data.curves.remove(curve, do_unlink=True)
        try:
            bpy.data.collections.remove(coll)
        except Exception:
            pass

    def test_recompute_updates_endpoints_and_markers(self):
        _load_local_addon()
        import cash_cab_addon.route.route_adjuster as route_adjuster

        scene = bpy.context.scene

        curve = bpy.data.curves.new("ROUTE_DATA_RECOMP", type="CURVE")
        curve.dimensions = "3D"
        spline = curve.splines.new("POLY")
        spline.points.add(1)
        spline.points[0].co = (0.0, 0.0, 0.0, 1.0)
        spline.points[1].co = (100.0, 0.0, 0.0, 1.0)

        route_obj = bpy.data.objects.new("ROUTE", curve)
        scene.collection.objects.link(route_obj)

        start_empty = bpy.data.objects.new("Start", None)
        start_empty.location = (0.0, 0.0, 0.0)
        end_empty = bpy.data.objects.new("End", None)
        end_empty.location = (100.0, 0.0, 0.0)
        scene.collection.objects.link(start_empty)
        scene.collection.objects.link(end_empty)

        marker_start = bpy.data.objects.new("MARKER_START", None)
        marker_end = bpy.data.objects.new("MARKER_END", None)
        scene.collection.objects.link(marker_start)
        scene.collection.objects.link(marker_end)

        ok = route_adjuster.ensure_route_control_empties(scene)
        self.assertTrue(ok)

        end_ctrl = bpy.data.objects.get(route_adjuster.CTRL_END_NAME)
        self.assertIsNotNone(end_ctrl)
        end_ctrl.location = (200.0, 50.0, 0.0)

        orig_world_to_geo = route_adjuster._world_to_geographic
        orig_geo_to_world = route_adjuster._geographic_to_world
        orig_fetch = route_adjuster.fetch_route

        def fake_world_to_geo(_scene, world_xyz: Vector):
            return float(world_xyz.x), float(world_xyz.y)

        def fake_geo_to_world(_scene, lat: float, lon: float, z: float):
            return Vector((float(lat), float(lon), float(z)))

        class FakeRoute:
            def __init__(self, points):
                self.points = points

        def fake_fetch_route(start, end, user_agent, waypoints=None):
            _ = (user_agent, waypoints)
            return FakeRoute(points=[(start.lat, start.lon), (end.lat, end.lon)])

        try:
            route_adjuster._world_to_geographic = fake_world_to_geo
            route_adjuster._geographic_to_world = fake_geo_to_world
            route_adjuster.fetch_route = fake_fetch_route

            ok = route_adjuster.recompute_route_from_controls(bpy.context)
            self.assertTrue(ok)

            pts = list(curve.splines[0].points)
            last = pts[-1].co
            self.assertAlmostEqual(float(last[0]), 200.0, places=4)
            self.assertAlmostEqual(float(last[1]), 50.0, places=4)

            self.assertAlmostEqual(end_empty.location.x, 200.0, places=4)
            self.assertAlmostEqual(end_empty.location.y, 50.0, places=4)
            self.assertAlmostEqual(marker_start.location.x, start_empty.location.x, places=4)
            self.assertAlmostEqual(marker_start.location.y, start_empty.location.y, places=4)
            self.assertAlmostEqual(marker_end.location.x, end_empty.location.x, places=4)
            self.assertAlmostEqual(marker_end.location.y, end_empty.location.y, places=4)
            self.assertAlmostEqual(marker_end.location.z, route_adjuster.MARKER_END_Z, places=4)
        finally:
            route_adjuster._world_to_geographic = orig_world_to_geo
            route_adjuster._geographic_to_world = orig_geo_to_world
            route_adjuster.fetch_route = orig_fetch

            start_ctrl = bpy.data.objects.get(route_adjuster.CTRL_START_NAME)
            end_ctrl2 = bpy.data.objects.get(route_adjuster.CTRL_END_NAME)
            coll = bpy.data.collections.get(route_adjuster.CONTROL_COLLECTION_NAME)
            if start_ctrl is not None:
                bpy.data.objects.remove(start_ctrl, do_unlink=True)
            if end_ctrl2 is not None:
                bpy.data.objects.remove(end_ctrl2, do_unlink=True)
            bpy.data.objects.remove(marker_start, do_unlink=True)
            bpy.data.objects.remove(marker_end, do_unlink=True)
            bpy.data.objects.remove(start_empty, do_unlink=True)
            bpy.data.objects.remove(end_empty, do_unlink=True)
            bpy.data.objects.remove(route_obj, do_unlink=True)
            bpy.data.curves.remove(curve, do_unlink=True)
            try:
                if coll is not None:
                    bpy.data.collections.remove(coll)
            except Exception:
                pass

