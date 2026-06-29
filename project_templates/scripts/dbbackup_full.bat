@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
set "PS1=%SCRIPT_DIR%dbbackup_full.ps1"

if not exist "%PS1%" (
  echo ERROR: dbbackup_full.ps1 not found next to %~nx0
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
exit /b %ERRORLEVEL%
