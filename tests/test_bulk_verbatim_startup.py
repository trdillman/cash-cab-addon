import os
import unittest


class TestBulkVerbatimStartup(unittest.TestCase):
    def test_bulk_does_not_open_base_blend_in_worker_cmd(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        ops_path = os.path.join(repo_root, "bulk", "ops.py")
        with open(ops_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Regression guard: bulk workers must start from factory startup so the
        # regular operator can append assets/base.blend without a CashCab scene
        # name collision.
        self.assertNotIn("str(_base_blend_path())", text)

    def test_worker_does_not_open_a_base_blend_file(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        worker_path = os.path.join(repo_root, "bulk", "worker.py")
        with open(worker_path, "r", encoding="utf-8") as f:
            text = f.read()

        self.assertNotIn("def _open_base_blend", text)
        self.assertNotIn("bpy.ops.wm.open_mainfile", text)


if __name__ == "__main__":
    unittest.main()

