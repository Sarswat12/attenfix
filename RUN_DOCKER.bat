@echo off
REM RUN_DOCKER.bat - simple wrapper to run Docker Compose
cd /d %~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File start_docker.ps1
pause
