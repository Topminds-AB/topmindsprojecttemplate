@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ==============================================================================
REM deploy_loopia.bat — Deployment helper (template)
REM ==============================================================================
REM
REM Purpose
REM - Optional helper to deploy a project to a Loopia-hosted environment.
REM - Keep it simple and explicit: edit ONLY the EDIT HERE section.
REM
REM When to run
REM - After each completed phase (only if this repo uses Loopia deployment):
REM     1) create_codebase.bat
REM     2) deploy_loopia.bat
REM
REM Requirements
REM - Windows + an installed SFTP/FTP tool in PATH, or configure one below.
REM - This template uses WinSCP if available (recommended), but you may swap it.
REM
REM ==============================================================================
REM EDIT HERE
REM ==============================================================================
set "DEPLOY_ENABLED=false"

REM Choose one: sftp | ftp
set "DEPLOY_PROTOCOL=sftp"

REM Remote host and credentials (do not commit real secrets; use .env where possible)
set "DEPLOY_HOST="
set "DEPLOY_PORT="
set "DEPLOY_USER="
set "DEPLOY_PASSWORD="

REM Remote target directory
set "DEPLOY_REMOTE_PATH="

REM Local path to deploy (examples: .\services\app\public  or  .\dist)
set "DEPLOY_LOCAL_PATH="

REM Optional exclude patterns (space-separated)
set "DEPLOY_EXCLUDES=node_modules .git .env .env.* .codebasebackup .dbdump .dbbackup"

REM ==============================================================================
REM END EDIT HERE
REM ==============================================================================

if /I "%DEPLOY_ENABLED%" NEQ "true" (
  echo.
  echo deploy_loopia.bat is disabled (DEPLOY_ENABLED=false).
  echo - Enable it by setting DEPLOY_ENABLED=true in the EDIT HERE section.
  echo.
  exit /b 0
)

if "%DEPLOY_HOST%"=="" goto :MISSING
if "%DEPLOY_USER%"=="" goto :MISSING
if "%DEPLOY_REMOTE_PATH%"=="" goto :MISSING
if "%DEPLOY_LOCAL_PATH%"=="" goto :MISSING

REM Prefer WinSCP if installed
where winscp.com >nul 2>nul
if errorlevel 1 (
  echo.
  echo ERROR: WinSCP not found in PATH.
  echo - Install WinSCP and ensure winscp.com is available in PATH
  echo - Or replace this script with your preferred deployment tool.
  echo.
  exit /b 1
)

REM Build WinSCP script
set "WINSCP_SCRIPT=%TEMP%\winscp_deploy_%RANDOM%.txt"

(
  echo option batch abort
  echo option confirm off
  echo open %DEPLOY_PROTOCOL%://%DEPLOY_USER%:%DEPLOY_PASSWORD%@%DEPLOY_HOST%:%DEPLOY_PORT%
  echo lcd "%DEPLOY_LOCAL_PATH%"
  echo cd "%DEPLOY_REMOTE_PATH%"
  echo synchronize remote -delete -criteria=time -transfer=binary -filemask="|*/%DEPLOY_EXCLUDES%"
  echo exit
) > "%WINSCP_SCRIPT%"

echo.
echo ==============================================================================
echo Loopia deploy
echo - Local:  %DEPLOY_LOCAL_PATH%
echo - Remote: %DEPLOY_PROTOCOL%://%DEPLOY_HOST%:%DEPLOY_PORT%%DEPLOY_REMOTE_PATH%
echo ==============================================================================
echo.

winscp.com /script="%WINSCP_SCRIPT%"
set "RC=%ERRORLEVEL%"
del "%WINSCP_SCRIPT%" >nul 2>nul

if not "%RC%"=="0" (
  echo.
  echo ERROR: Deployment failed (exit code %RC%).
  exit /b %RC%
)

echo.
echo SUCCESS: Deployment completed.
exit /b 0

:MISSING
echo.
echo ERROR: Missing required deployment settings in EDIT HERE section.
echo - DEPLOY_HOST, DEPLOY_USER, DEPLOY_REMOTE_PATH, DEPLOY_LOCAL_PATH
echo.
exit /b 2
