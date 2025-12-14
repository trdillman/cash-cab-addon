import os
import zipfile
import re
from pathlib import Path

# Define the files and directories to include in the addon zip
addon_files = [
    "__init__.py",
    "defs.py",
    "app/",
    "asset_manager/",
    "assets/",
    "building/",
    "config/",
    "context_portal/",
    "gui/",
    "manager/",
    "material/",
    "osm/",
    "parse/",
    "renderer/",
    "road/",
    "route/",
    "routecam/",
    "setup/",
    "terrain/",
    "util/",
    "tests/"
]

def get_version():
    """Reads the version number from the .version file."""
    try:
        with open(".version", "r") as f:
            first_line = f.readline()
            match = re.search(r"v(\d+\.\d+\.\d+)", first_line)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    return "0.0.0"

def create_zip(version):
    """Creates a zip file for the addon."""
    addon_name = "cash_cab_addon"
    # IMPORTANT: Blender's legacy addon installer may derive the module name from the
    # zip filename. Keep this filename import-safe (no hyphens).
    zip_filename = f"{addon_name}-v{version}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Create the root folder inside the zip
        root_folder = Path(addon_name)
        
        for path_str in addon_files:
            path = Path(path_str)
            if path.is_dir():
                for root, dirs, files in os.walk(path):
                    # Exclude __pycache__ directories
                    if "__pycache__" in root:
                        continue
                    
                    for file in files:
                        file_path = Path(root) / file
                        archive_path = root_folder / file_path
                        zf.write(file_path, archive_path)
            elif path.is_file():
                archive_path = root_folder / path
                zf.write(path, archive_path)

    print(f"Successfully created addon zip: {zip_filename}")

if __name__ == "__main__":
    version = get_version()
    create_zip(version)
