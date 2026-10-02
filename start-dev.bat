@echo off
rem ==============================================================================
rem CLINOVA AI - Developer Quick Launch (Windows Batch)
rem Delegates directly to the Native Windows PowerShell orchestrator.
rem ==============================================================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" start %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Clinova startup encountered an error.
    pause
    exit /b %ERRORLEVEL%
)
