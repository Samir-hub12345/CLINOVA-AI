@echo off
rem Clinova AI CLI shortcut
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" %*
exit /b %ERRORLEVEL%
