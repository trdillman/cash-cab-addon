@echo off
echo Running Strict Scene Audit...
blender -b --python ../tests/audits/scene_auditor.py -- --level strict --report-path ../reports/strict_audit_report.xml
echo Strict audit complete. Report generated at reports/strict_audit_report.xml
pause
