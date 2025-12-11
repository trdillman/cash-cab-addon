@echo off
echo Running Strict Scene Audit...
blender -b --python tests/audits/scene_auditor.py -- --level strict --report-path ./strict_audit_report.xml
echo Strict audit complete. Report generated at strict_audit_report.xml
pause
