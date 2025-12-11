@echo off
echo Running Quick Scene Audit...
blender -b --python ../tests/audits/scene_auditor.py -- --level quick --report-path ../reports/quick_audit_report.xml
echo Quick audit complete. Report generated at reports/quick_audit_report.xml
pause
