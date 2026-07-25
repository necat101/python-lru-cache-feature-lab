@echo off
setlocal
cd /d "%~dp0"
python run_lab.py
if errorlevel 1 exit /b %errorlevel%
python -m unittest test_lab -v
