#!/usr/bin/env python3
"""
Safe cleanup script for CashCab addon
Removes unused imports and commented code based on analysis
"""

import os
import re
import ast
from collections import defaultdict

def safe_remove_unused_imports(file_path):
    """Safely remove unused imports from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        # Collect all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(('import', alias.name, node.lineno, node.col_offset))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(('from', f'{module}.{alias.name}', node.lineno, node.col_offset))

        # Collect used names
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                used_names.add(node.value.id)

        # Find unused imports
        unused_imports = []
        for imp_type, imp_name, line, col in imports:
            base_name = imp_name.split('.')[0]
            if base_name not in used_names and not base_name.startswith('_'):
                unused_imports.append((imp_type, imp_name, line, col))

        # Remove unused imports from content
        lines = content.split('\n')
        lines_to_remove = set()

        for imp_type, imp_name, line, col in unused_imports:
            # Mark the import line for removal
            lines_to_remove.add(line - 1)  # Convert to 0-based index

        # Filter out unused import lines
        new_lines = []
        for i, line in enumerate(lines):
            if i not in lines_to_remove:
                new_lines.append(line)

        new_content = '\n'.join(new_lines)

        # Only write if changes were made
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return len(unused_imports)

        return 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def remove_safe_commented_code(file_path):
    """Remove safe commented code blocks"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        new_lines = []
        removed_count = 0

        for line in lines:
            stripped = line.strip()
            # Remove commented code that looks like actual code
            if (stripped.startswith('#') and
                len(stripped) > 1 and
                any(c in line for c in ['=', 'def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'return ', 'print('])):
                removed_count += 1
                continue
            new_lines.append(line)

        new_content = '\n'.join(new_lines)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return removed_count

        return 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def fix_bom_issue(file_path):
    """Fix BOM encoding issues"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # If content starts with BOM, remove it
        if content.startswith('\ufeff'):
            content = content[1:]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error fixing BOM for {file_path}: {e}")
        return False

def main():
    print("=== CashCab Addon Cleanup Script ===\n")

    # Files to process for unused imports
    files_with_unused_imports = [
        'build.py',
        'asset_manager/cli.py',
        'bulk/google_sheet.py',
        'asset_manager/asset_extractor.py',
        'asset_manager/asset_file_manager.py',
        'asset_manager/asset_safety.py',
        'asset_manager/loader.py',
        'asset_manager/registry.py',
        'asset_manager/simple_asset_updater.py',
        'asset_manager/single_file_loader.py',
        'asset_manager/validation.py',
        'building/gn_2d.py',
        'building/layer.py',
        'building/manager.py',
        'building/renderer.py',
        'building/roof/flat.py',
        'building/roof/half_hipped.py',
        'building/roof/hipped.py',
        'building/roof/mansard.py',
        'building/roof/mesh.py',
        'building/roof/profile.py',
        'building/roof/pyramidal.py',
        'building/roof/skillion.py',
        'building/roof/__init__.py',
        'bulk/ops.py',
        'bulk/panels.py',
        'bulk/parser.py',
        'bulk/properties.py',
        'bulk/worker.py',
        'gui/cleanup_operator.py',
        'gui/cleanup_patterns.py',
        'gui/operators.py',
        'gui/panels.py',
        'gui/preferences.py',
        'osm/import_operator.py',
        'parse/osm/__init__.py',
        'parse/osm/relation/building.py',
        'parse/osm/relation/multipolygon.py',
        'renderer/curve_layer.py',
        'renderer/curve_renderer.py',
        'renderer/layer.py',
        'renderer/node_layer.py',
        'renderer/node_renderer.py',
        'renderer/__init__.py',
        'road/config.py',
        'road/curve_converter.py',
        'road/detection.py',
        'road/materials.py',
        'road/processor.py',
        'road/street_labels.py',
        'road/__init__.py',
        'route/anim.py',
        'route/assets.py',
        'route/config.py',
        'route/debug_monitor.py',
        'route/error_recovery.py'
    ]

    # Files with BOM issues
    files_with_bom = [
        '__init__.py',
        'gui/properties.py',
        'route/buildings.py'
    ]

    total_removed = 0

    print("Phase 1: Removing unused imports...")
    for file_name in files_with_unused_imports:
        file_path = os.path.join('.', file_name)
        if os.path.exists(file_path):
            removed = safe_remove_unused_imports(file_path)
            if removed > 0:
                print(f"  {file_name}: removed {removed} unused imports")
                total_removed += removed

    print("\nPhase 2: Removing safe commented code...")
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                removed = remove_safe_commented_code(file_path)
                if removed > 0:
                    print(f"  {os.path.join(root, file_name)}: removed {removed} commented lines")
                    total_removed += removed

    print("\nPhase 3: Fixing BOM issues...")
    for file_name in files_with_bom:
        file_path = os.path.join('.', file_name)
        if os.path.exists(file_path):
            if fix_bom_issue(file_path):
                print(f"  {file_name}: fixed BOM issue")

    print(f"\n=== Summary ===")
    print(f"Total cleanup operations: {total_removed}")
    print("\nNext steps:")
    print("1. Run test suite to verify no functionality was broken")
    print("2. Check for any import errors in Blender")
    print("3. Review remaining commented code for potential removal")
    print("4. Replace print() statements with proper logging")

if __name__ == "__main__":
    main()