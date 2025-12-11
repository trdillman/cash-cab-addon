@echo off
echo Running Blender Test Suite...
blender -b --python ../tests/test_runner.py
echo Test run complete.
pause
