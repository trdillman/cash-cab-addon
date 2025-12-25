#!/usr/bin/env python3
"""
Code cleanup analyzer for CashCab addon
Detects unused imports, dead code, and cleanup opportunities
"""

import os
import re
import ast
import json
from collections import defaultdict

def analyze_file(file_path):
    """Analyze a single Python file for cleanup opportunities"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        tree = ast.parse(content)
        issues = {}

        # 1. Check for commented code blocks
        commented_lines = []
        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            if stripped.startswith('#') and len(stripped) > 1:
                # Check if it's not just a comment but looks like code
                if any(c in line for c in ['=', 'def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'return ', 'print(']):
                    commented_lines.append(i)

        if commented_lines:
            issues['commented_code'] = commented_lines

        # 2. Check for unused imports (basic heuristic)
        imports = []
        used_names = set()

        class ImportVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    imports.append(('import', alias.name, node.lineno))

            def visit_ImportFrom(self, node):
                module = node.module or ''
                for alias in node.names:
                    imports.append(('from', f'{module}.{alias.name}', node.lineno))

            def visit_Name(self, node):
                if hasattr(node, 'id'):
                    used_names.add(node.id)

            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        try:
            visitor = ImportVisitor()
            visitor.visit(tree)

            unused_imports = []
            for imp_type, imp_name, line in imports:
                base_name = imp_name.split('.')[0]
                if base_name not in used_names and not base_name.startswith('_'):
                    unused_imports.append((imp_type, imp_name, line))

            if unused_imports:
                issues['unused_imports'] = unused_imports
        except:
            pass

        # 3. Check for TODO/FIXME comments
        todo_comments = []
        for i, line in enumerate(content.split('\n'), 1):
            if re.search(r'#\s*(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
                todo_comments.append(i)

        if todo_comments:
            issues['todo_comments'] = todo_comments

        # 4. Check for empty functions/classes
        empty_functions = []
        empty_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    empty_functions.append((node.name, node.lineno))
            elif isinstance(node, ast.ClassDef):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    empty_classes.append((node.name, node.lineno))

        if empty_functions:
            issues['empty_functions'] = empty_functions
        if empty_classes:
            issues['empty_classes'] = empty_classes

        return issues

    except Exception as e:
        return {'error': str(e)}

def main():
    print("=== CashCab Addon Code Cleanup Analysis ===\n")

    # Scan all Python files
    all_issues = {}
    total_files = 0
    files_with_issues = 0

    for root, dirs, files in os.walk('.'):
        # Skip __pycache__ and .git directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                total_files += 1
                file_path = os.path.join(root, file)

                issues = analyze_file(file_path)
                if issues:
                    files_with_issues += 1
                    all_issues[file_path] = issues

    # Report summary
    print(f"Files analyzed: {total_files}")
    print(f"Files with issues: {files_with_issues}\n")

    # Detailed reporting
    issue_types = defaultdict(list)

    for file_path, issues in all_issues.items():
        print(f"[FILE] {file_path}")

        for issue_type, data in issues.items():
            if issue_type == 'commented_code':
                print(f"  [WARN] Commented code (lines {data})")
                issue_types['commented_code'].append((file_path, data))

            elif issue_type == 'unused_imports':
                for imp_type, imp_name, line in data:
                    print(f"  [UNUSED] {imp_type}: {imp_name} (line {line})")
                    issue_types['unused_imports'].append((file_path, (imp_type, imp_name, line)))

            elif issue_type == 'todo_comments':
                print(f"  [TODO] TODO/FIXME comments (lines {data})")
                issue_types['todo_comments'].append((file_path, data))

            elif issue_type == 'empty_functions':
                for func_name, line in data:
                    print(f"  [EMPTY] Function: {func_name} (line {line})")
                    issue_types['empty_functions'].append((file_path, (func_name, line)))

            elif issue_type == 'empty_classes':
                for class_name, line in data:
                    print(f"  [EMPTY] Class: {class_name} (line {line})")
                    issue_types['empty_classes'].append((file_path, (class_name, line)))

            elif issue_type == 'error':
                print(f"  [ERROR] Error analyzing: {data}")

        print()

    # Summary by issue type
    print("=== SUMMARY BY ISSUE TYPE ===")
    for issue_type, items in issue_types.items():
        print(f"{issue_type.replace('_', ' ').title()}: {len(items)} items")

    # Specific directories to check
    print("\n=== SPECIAL DIRECTORIES ANALYSIS ===")

    # Check refactor directory
    refactor_dir = "refactor"
    if os.path.exists(refactor_dir):
        print(f"\n[DIR] {refactor_dir}/ directory:")
        for item in os.listdir(refactor_dir):
            print(f"  - {item}")

        # Check for deleted files mentioned in git status
        print(f"\n  Note: Git status shows these files were deleted from refactor/:")
        print(f"    - REFAC_SPECIFICATION.md")
        print(f"    - prompts/002_xml_parsing_agent.md")
        print(f"    - prompts/003_asset_loading_agent.md")
        print(f"    - prompts/004_memory_management_agent.md")
        print(f"    - prompts/005_coordinate_caching_agent.md")
        print(f"    - prompts/007_type_hints_agent.md")
        print(f"    - prompts/010_security_tests_agent.md")
        print(f"    - prompts/011_route_services_tests_agent.md")
        print(f"    - prompts/012_documentation_agent.md")
        print(f"    - prompts/_templates/checkpoint_schema.md")
        print(f"    - prompts/_templates/testing_procedure.md")

    # Check tests directory
    tests_dir = "tests"
    if os.path.exists(tests_dir):
        test_files = [f for f in os.listdir(tests_dir) if f.endswith('.py')]
        print(f"\n[DIR] {tests_dir}/ directory: {len(test_files)} test files")

        # Check for test files that might be duplicates
        print("  Test files:")
        for test_file in sorted(test_files):
            print(f"    - {test_file}")

    # Check asset references
    print("\n=== ASSET ANALYSIS ===")
    asset_manager_dir = "asset_manager"
    if os.path.exists(asset_manager_dir):
        asset_files = []
        for root, dirs, files in os.walk(asset_manager_dir):
            for file in files:
                if file.endswith(('.blend', '.json', '.xml')):
                    asset_files.append(os.path.join(root, file))

        print(f"Asset files found: {len(asset_files)}")
        if asset_files:
            print("  Asset files:")
            for asset in sorted(asset_files)[:10]:  # Show first 10
                print(f"    - {asset}")
            if len(asset_files) > 10:
                print(f"    ... and {len(asset_files) - 10} more")

if __name__ == "__main__":
    main()