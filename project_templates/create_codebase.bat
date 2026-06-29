@echo off
setlocal EnableExtensions
REM ============================================================================
REM create_codebase.bat - reusable codebase archive launcher
REM ============================================================================
REM Use --interactive if you want the window to stay open after completion.
REM ============================================================================

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PAUSE_ON_EXIT="

if /I "%~1"=="--interactive" (
    set "PAUSE_ON_EXIT=1"
    shift
)

echo.
echo ============================================================================
echo  CREATE CODEBASE ARCHIVE
echo ============================================================================
echo.

REM Check that PS1 exists
if not exist "%SCRIPT_DIR%\create_codebase.ps1" (
    echo ERROR: create_codebase.ps1 not found in %SCRIPT_DIR%
    echo.
    if defined PAUSE_ON_EXIT pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%\create_codebase.ps1" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Archive creation failed! Exit code: %ERRORLEVEL%
    echo.
    if defined PAUSE_ON_EXIT pause
    exit /b %ERRORLEVEL%
)

echo.
if defined PAUSE_ON_EXIT pause
