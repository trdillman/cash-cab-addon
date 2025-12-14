import unittest

import bpy


class TestStreetLabels(unittest.TestCase):
    def test_ensure_collection_hidden(self):
        from cash_cab_addon.road import street_labels

        scene = bpy.context.scene
        coll = street_labels.ensure_street_labels_collection(scene)
        self.assertEqual(coll.name, "STREET_LABELS")
        self.assertTrue(coll.hide_render)
        self.assertTrue(coll.hide_viewport)

    def test_toggle_visibility(self):
        from cash_cab_addon.road import street_labels

        scene = bpy.context.scene
        street_labels.set_street_labels_visible(scene, True)
        coll = bpy.data.collections.get("STREET_LABELS")
        self.assertIsNotNone(coll)
        self.assertFalse(coll.hide_viewport)
        self.assertTrue(coll.hide_render)

        street_labels.set_street_labels_visible(scene, False)
        self.assertTrue(coll.hide_viewport)
        self.assertTrue(coll.hide_render)
