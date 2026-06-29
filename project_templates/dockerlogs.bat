@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
set "PS1=%SCRIPT_DIR%scripts\collect_docker_logs.ps1"

if not exist "%PS1%" (
  echo ERROR: collect_docker_logs.ps1 not found in scripts\
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
exit /b %ERRORLEVEL%
