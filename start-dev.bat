@echo off
rem ==============================================================================
rem CLINOVA AI - Developer Interactive Launcher (Windows)
rem Starts PostgreSQL/SQLite, Redis, FastAPI Backend, and Next.js Frontend,
rem opens the Clinical Workstation in your default browser, and keeps the
rem console window open with a live interactive control dashboard.
rem ==============================================================================

title Clinova AI - Local Clinical Workstation
color 0B
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ====================================================================
echo   CLINOVA AI - LOCAL WINDOWS CLINICAL WORKSTATION
echo ====================================================================
echo.
echo Starting Clinova AI services natively on Windows...
echo (FastAPI Backend, Next.js Frontend, SQLite/PostgreSQL, Redis fallback)
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" start -Open %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ====================================================================
    echo [ERROR] Clinova startup encountered an issue.
    echo ====================================================================
    echo.
    echo Running system diagnostics to diagnose the issue...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" doctor
    echo.
    echo Press any key to close this window.
    pause >nul
    exit /b %ERRORLEVEL%
)

:MENU
echo.
echo ====================================================================
echo   CLINOVA AI IS ACTIVE AND READY
echo ====================================================================
echo   Clinical Workstation:  http://localhost:3000
echo   FastAPI Backend API:   http://localhost:8000
echo   Swagger OpenAPI Docs:  http://localhost:8000/docs
echo   Database:              SQLite (clinova-demo.db zero-install)
echo ====================================================================
echo.
echo Select an option:
echo   [1] Open Clinical Workstation in Browser (http://localhost:3000)
echo   [2] Open API Documentation (Swagger /docs)
echo   [3] Inspect Live Service Health and Status
echo   [4] View Backend Server Logs
echo   [5] View Frontend Server Logs
echo   [6] Restart All Services
echo   [7] Stop All Services and Exit
echo.
set /p "USER_CHOICE=Enter option [1-7] or 'Q' to quit: "

if "%USER_CHOICE%"=="1" (
    start http://localhost:3000
    goto MENU
)
if "%USER_CHOICE%"=="2" (
    start http://localhost:8000/docs
    goto MENU
)
if "%USER_CHOICE%"=="3" (
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" status
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" health
    goto MENU
)
if "%USER_CHOICE%"=="4" (
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" logs -Service backend -Lines 30
    goto MENU
)
if "%USER_CHOICE%"=="5" (
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" logs -Service frontend -Lines 30
    goto MENU
)
if "%USER_CHOICE%"=="6" (
    echo.
    echo Restarting all Clinova services...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" restart -Open
    goto MENU
)
if /i "%USER_CHOICE%"=="7" goto SHUTDOWN
if /i "%USER_CHOICE%"=="Q" goto SHUTDOWN
if /i "%USER_CHOICE%"=="quit" goto SHUTDOWN
if /i "%USER_CHOICE%"=="exit" goto SHUTDOWN

goto MENU

:SHUTDOWN
echo.
echo Gracefully stopping all Clinova AI services...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\clinova.ps1" stop
echo.
echo All Clinova services have been stopped.
echo Window will close in 3 seconds...
timeout /t 3 >nul
exit /b 0
