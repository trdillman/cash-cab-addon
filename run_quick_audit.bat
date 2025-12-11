@echo off
echo Running Quick Scene Audit...
blender -b --python tests/audits/scene_auditor.py -- --level quick --report-path ./quick_audit_report.xml
echo Quick audit complete. Report generated at quick_audit_report.xml
pause
