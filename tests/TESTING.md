# CashCab Addon Testing & Auditing

This document outlines the testing, auditing, and quality assurance framework for the CashCab Blender addon.

## Directory Structure

All test and audit files are located in the `tests/` directory:

```
tests/
├── audits/
│   └── scene_auditor.py  # Main script for scene audits (quick and strict)
├── test_runner.py        # Discovers and runs all unit/integration tests
├── test_asset_camera.py
├── test_scene_safe_areas.py
└── ... (other test files)
```

## Running Tests and Audits

This project uses a combination of Python's `unittest` framework and custom audit scripts. All tests and audits must be run from within Blender's Python environment to have access to the `bpy` module.

### Using Batch Scripts (Windows)

The easiest way to run the validation suites is by using the provided `.bat` files in the project root. Double-click them to run.

- **`run_tests.bat`**: Executes all unit and integration tests found in the `tests/` directory.
- **`run_quick_audit.bat`**: Runs a fast, high-level check for major scene errors. Generates `quick_audit_report.xml`.
- **`run_strict_audit.bat`**: Runs a comprehensive, deep inspection of the scene. Generates `strict_audit_report.xml`.

### Manual Execution

You can also run the scripts manually from the command line.

**Run all tests:**
```sh
blender -b --python tests/test_runner.py
```

**Run Scene Audits:**
```sh
# Run the quick audit
blender -b --python tests/audits/scene_auditor.py -- --level quick

# Run the strict audit and specify a report path
blender -b --python tests/audits/scene_auditor.py -- --level strict --report-path ./ci/reports/strict_audit.xml
```

## Audit Reports

The audit scripts generate JUnit-XML reports, which are standard for CI/CD systems. These reports are saved to the path specified by the `--report-path` argument (e.g., `strict_audit_report.xml`).

These XML files can be inspected manually or, more commonly, parsed by a CI/CD platform (like GitHub Actions) to provide a clear summary of test results.

## CI/CD Pipeline (GitHub Actions)

The CI/CD pipeline is defined in `.github/workflows/ci.yml`. It automates the quality assurance process on every push or pull request to the `main` branch.

The pipeline consists of the following stages:

1.  **Lint**: The code is checked against the `flake8` linter to enforce a consistent style and catch common errors.
2.  **Build**: The addon is packaged into a distributable `.zip` file, which is archived as a build artifact.
3.  **Test**: The full test suite (unit and integration) is run using the `test_runner.py` script. The scene audits are also run during this stage.
4.  **Deploy**: On a push to the `main` branch, a new GitHub Release is created, and the addon `.zip` from the Build stage is uploaded as a release asset, making it easy to download and install.

This automated process ensures that any code changes are automatically validated, maintaining a high level of quality and stability for the project.
