@echo off
setlocal enabledelayedexpansion
REM ============================================================================
REM create_codebase.bat version 1.0. - Reusable Codebase Archive Generator
REM ============================================================================
REM Double-click this file to create a structured ZIP snapshot.
REM All configuration lives in create_codebase.ps1 (top of file).
REM ============================================================================

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo.
echo ============================================================================
echo  CREATE CODEBASE ARCHIVE
echo ============================================================================
echo.

REM Check that PS1 exists
if not exist "%SCRIPT_DIR%\create_codebase.ps1" (
    echo ERROR: create_codebase.ps1 not found in %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

REM Execute PowerShell script with bypass
powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%\create_codebase.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Archive creation failed! Exit code: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
pause
