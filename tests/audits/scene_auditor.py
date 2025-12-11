import os
import sys
from pathlib import Path
import argparse
import bpy
import time
import socket
from mathutils import Vector

def _generate_junit_xml_report(test_suite_name, test_cases):
    """
    Generates a JUnit-XML report string from a list of TestCase-like objects
    without any external dependencies.
    """
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')
    hostname = socket.gethostname()
    
    total_tests = len(test_cases)
    total_failures = sum(1 for tc in test_cases if tc.is_failure())
    
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<testsuite name="{test_suite_name}" tests="{total_tests}" failures="{total_failures}" errors="0" skipped="0" timestamp="{timestamp}" hostname="{hostname}">'
    ]
    
    for tc in test_cases:
        xml.append(f'  <testcase classname="{tc.classname}" name="{tc.name}" time="{tc.elapsed_sec:.4f}">')
        if tc.is_failure():
            xml.append(f'    <failure message="{tc.failure_message}">')
            xml.append(f'      <![CDATA[{tc.stdout}]]>')
            xml.append('    </failure>')
        xml.append('  </testcase>')
        
    xml.append('</testsuite>')
    return '\n'.join(xml)

class TestCase:
    """A simple, dependency-free container for test case results."""
    def __init__(self, name, classname, elapsed_sec=0, stdout="", stderr=""):
        self.name = name
        self.classname = classname
        self.elapsed_sec = elapsed_sec
        self.stdout = stdout
        self.stderr = stderr
        self._is_failure = False
        self.failure_message = ""

    def add_failure_info(self, message="", output="", failure_type=""):
        self._is_failure = True
        self.failure_message = message
        if output:
            self.stdout = output

    def is_failure(self):
        return self._is_failure

def _load_pipeline_finalizer():
    try:
        from cash_cab_addon.route import pipeline_finalizer as pf
        return pf
    except ImportError:
        addon_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if addon_root not in sys.path:
            sys.path.append(addon_root)
        try:
            import cash_cab_addon
            from cash_cab_addon.route import pipeline_finalizer as pf
            return pf
        except Exception as e:
            print(f"Failed to import addon for audit: {e}")
            return None

route_pf = _load_pipeline_finalizer()
if not route_pf:
    print("CRITICAL: Could not load pipeline_finalizer. Audit checks will fail.")

CAMERAS_COLLECTION_NAME = getattr(route_pf, "CAMERAS_COLLECTION_NAME", "CAMERAS")
ASSET_CAMERA_NAME = getattr(route_pf, "ASSET_CAMERA_NAME", "ASSET_CAMERA")

def _log(msg: str):
    print(f"[SCENE_AUDITOR] {msg}")

class SceneAuditor:
    def __init__(self):
        self.scene = bpy.context.scene
        self.test_cases = []

    def run_check(self, name, check_function, *args, **kwargs):
        start_time = time.time()
        is_success, notes = check_function(*args, **kwargs)
        elapsed_sec = time.time() - start_time
        
        test_case = TestCase(name, 'SceneAudit', elapsed_sec=elapsed_sec)
        if not is_success:
            test_case.add_failure_info(f"Check failed: {name}", notes)
        
        self.test_cases.append(test_case)
        status = "PASS" if is_success else "FAIL"
        _log(f"{name} | {status} | {notes}")
        return is_success

    def get_route_object(self):
        route_obj = self.scene.objects.get("ROUTE")
        if route_obj and route_obj.type == 'CURVE':
            return route_obj
        for obj in self.scene.objects:
            if obj.type == 'CURVE' and obj.get("blosm_role") == "route_curve_osm":
                return obj
        return None

    def check_route_and_car_presence(self):
        route_obj = self.get_route_object()
        car_obj = self.scene.objects.get("ASSET_CAR")
        if not route_obj:
            return False, "ROUTE object not found"
        if not car_obj:
            return False, "ASSET_CAR object not found"
        return True, f"ROUTE: {route_obj.name}, CAR: {car_obj.name}"

    def check_camera_presence(self):
        camera_obj = self.scene.objects.get(ASSET_CAMERA_NAME)
        cameras_coll = bpy.data.collections.get(CAMERAS_COLLECTION_NAME)
        if not camera_obj:
            return False, f"{ASSET_CAMERA_NAME} not found"
        if not cameras_coll:
            return False, f"'{CAMERAS_COLLECTION_NAME}' collection not found"
        if camera_obj.name not in cameras_coll.objects:
            return False, f"{ASSET_CAMERA_NAME} not in '{CAMERAS_COLLECTION_NAME}' collection"
        return True, f"{ASSET_CAMERA_NAME} found in {CAMERAS_COLLECTION_NAME}"

    def check_animation_range(self):
        start = self.scene.frame_start
        end = self.scene.frame_end
        if end <= start:
            return False, f"Frame range is invalid or not set (start: {start}, end: {end})"
        return True, f"Frame range: {start}-{end}"

    def check_render_engine(self):
        engine = self.scene.render.engine
        if engine != 'CYCLES':
            return False, f"Render engine is '{engine}', expected 'CYCLES'"
        return True, "Render engine is CYCLES"

    def check_for_duplicate_objects(self):
        duplicates = [obj.name for obj in self.scene.objects if ".00" in obj.name]
        if duplicates:
            return False, f"Found {len(duplicates)} objects with .00x suffixes: {duplicates[:5]}"
        return True, "No duplicate objects found"

    def check_driver_validity(self):
        invalid_drivers = []
        for obj in bpy.data.objects:
            if obj.animation_data and obj.animation_data.drivers:
                for d in obj.animation_data.drivers:
                    if not d.is_valid:
                        invalid_drivers.append(f"{obj.name}:{d.data_path}")
        # Also check scene level drivers
        if self.scene.animation_data and self.scene.animation_data.drivers:
            for d in self.scene.animation_data.drivers:
                if not d.is_valid:
                    invalid_drivers.append(f"Scene:{d.data_path}")
        
        if invalid_drivers:
            return False, f"Found {len(invalid_drivers)} invalid drivers: {invalid_drivers[:5]}"
        return True, "All drivers are valid"

    def check_compositor_setup(self):
        if not self.scene.use_nodes:
            return False, "Scene does not use compositor nodes"
        if not self.scene.node_tree:
            return False, "Scene has no compositor node tree"
        return True, "Compositor is enabled"

    def run_quick_audit(self):
        _log("--- Running Quick Audit ---")
        self.run_check("Route and Car Presence", self.check_route_and_car_presence)
        self.run_check("Camera Presence", self.check_camera_presence)
        self.run_check("Animation Range Set", self.check_animation_range)
        return self.test_cases

    def run_strict_audit(self):
        _log("--- Running Strict Audit ---")
        self.run_quick_audit()
        self.run_check("Render Engine is CYCLES", self.check_render_engine)
        self.run_check("No Duplicate Objects", self.check_for_duplicate_objects)
        self.run_check("All Drivers are Valid", self.check_driver_validity)
        self.run_check("Compositor is Enabled", self.check_compositor_setup)
        return self.test_cases

def main():
    parser = argparse.ArgumentParser(description="Run scene audits for CashCab.")
    parser.add_argument(
        '--level', type=str, choices=['quick', 'strict'], default='strict',
        help="The level of audit to run."
    )
    parser.add_argument(
                '--report-path',
                type=str,
                default="reports/audit_report.xml",
                help="Path to save the JUnit-XML report."
    )
    
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    args = parser.parse_args(argv)
    auditor = SceneAuditor()
    
    if args.level == 'quick':
        test_cases = auditor.run_quick_audit()
    else:
        test_cases = auditor.run_strict_audit()

    suite_name = f"CashCab Scene Audit - {args.level.capitalize()}"
    report_path = os.path.abspath(args.report_path)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        xml_string = _generate_junit_xml_report(suite_name, test_cases)
        f.write(xml_string)
    _log(f"Audit report saved to {report_path}")

    if any(case.is_failure() for case in test_cases):
        _log("Audit finished with failures.")
        sys.exit(1)
    else:
        _log("Audit finished successfully.")

if __name__ == "__main__":
    main()
