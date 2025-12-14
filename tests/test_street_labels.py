import unittest

import bpy


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


class TestStreetLabels(unittest.TestCase):
    def test_ensure_collection_hidden(self):
        _load_local_addon()
        import cash_cab_addon.road.street_labels as street_labels

        scene = bpy.context.scene
        coll = street_labels.ensure_street_labels_collection(scene)
        self.assertEqual(coll.name, "STREET_LABELS")
        self.assertTrue(coll.hide_render)
        self.assertTrue(coll.hide_viewport)

    def test_toggle_visibility(self):
        _load_local_addon()
        import cash_cab_addon.road.street_labels as street_labels

        scene = bpy.context.scene
        street_labels.set_street_labels_visible(scene, True)
        coll = bpy.data.collections.get("STREET_LABELS")
        self.assertIsNotNone(coll)
        self.assertFalse(coll.hide_viewport)
        self.assertTrue(coll.hide_render)

        street_labels.set_street_labels_visible(scene, False)
        self.assertTrue(coll.hide_viewport)
        self.assertTrue(coll.hide_render)
