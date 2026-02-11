@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ==============================================================================
REM dbbackup_full.bat — MySQL full dump (schema + data + routines + triggers + events)
REM ==============================================================================
REM
REM Goal
REM - Produce a deterministic, restorable SQL dump for ONE database.
REM - Work in both modes:
REM     1) PROD  (external / managed database)  -> uses DB_* variables
REM     2) LOCAL (internal / docker compose)    -> uses MYSQL_* variables
REM
REM Output
REM - Writes dump file to TARGET_DIRECTORY (default: .\.dbbackup)
REM - Filename format: <PROJECT>_<DBNAME>_YYYY-MM-DD_HH-mm.sql
REM
REM --------------------------------------------------------------------------
REM HOW TO CONFIGURE (Template)
REM --------------------------------------------------------------------------
REM 1) Create a ".env" file at repo root using ".env.example" as base.
REM 2) Fill in either:
REM     - PROD mode:  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
REM     - LOCAL mode: MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
REM
REM 3) Optional PROD SSL variables (only if your DB requires it):
REM     - DB_SSL_MODE        (e.g. REQUIRED, VERIFY_CA, VERIFY_IDENTITY)
REM     - DB_SSL_CA_PATH     (path to CA file)
REM     - DB_SSL_CERT_PATH   (client cert)
REM     - DB_SSL_KEY_PATH    (client key)
REM
REM --------------------------------------------------------------------------
REM USAGE
REM --------------------------------------------------------------------------
REM 1) Auto mode (recommended): chooses PROD if DB_HOST is set, otherwise LOCAL if MYSQL_HOST is set
REM     dbbackup_full.bat
REM
REM 2) Force mode:
REM     dbbackup_full.bat prod
REM     dbbackup_full.bat local
REM
REM 3) Override env file location (optional):
REM     dbbackup_full.bat prod ".\path\to\.env"
REM
REM Notes
REM - This script intentionally does NOT store secrets. Credentials must come from .env.
REM - Make sure mysqldump is available in PATH (MySQL client tools installed).
REM ==============================================================================

REM ---- Defaults you MAY change -------------------------------------------------
REM Default output folder (can be absolute or relative)
set "TARGET_DIRECTORY=%~dp0.dbbackup"

REM Optional project name override. If empty, APP_NAME from .env will be used.
set "PROJECT_OVERRIDE="
REM ------------------------------------------------------------------------------

REM Parse args
set "MODE=%~1"
set "ENV_FILE=%~2"

if "%ENV_FILE%"=="" set "ENV_FILE=%~dp0.env"

REM Load .env (best effort; ignore missing)
call :LoadEnv "%ENV_FILE%"

REM Resolve project name
if not "%PROJECT_OVERRIDE%"=="" (
  set "PROJECT=%PROJECT_OVERRIDE%"
) else if not "%APP_NAME%"=="" (
  set "PROJECT=%APP_NAME%"
) else (
  set "PROJECT=PROJECT"
)

REM Sanitize project for filenames (spaces -> underscore)
set "PROJECT=%PROJECT: =_%"

REM Determine mode if not forced
if /I "%MODE%"=="prod" goto :MODE_PROD
if /I "%MODE%"=="local" goto :MODE_LOCAL

REM Auto mode
if not "%DB_HOST%"=="" goto :MODE_PROD
if not "%MYSQL_HOST%"=="" goto :MODE_LOCAL

echo.
echo ERROR: Could not determine mode.
echo - To auto-detect: set DB_HOST (PROD) or MYSQL_HOST (LOCAL) in "%ENV_FILE%".
echo - Or force: dbbackup_full.bat prod   ^|   dbbackup_full.bat local
echo.
exit /b 2

:MODE_PROD
set "DBMODE=PROD"
call :ValidateRequired DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD || exit /b 2

set "HOST=%DB_HOST%"
set "PORT=%DB_PORT%"
set "DBNAME=%DB_NAME%"
set "USER=%DB_USER%"
set "PASSWORD=%DB_PASSWORD%"

REM Optional SSL flags (PROD)
set "SSL_FLAGS="
if not "%DB_SSL_MODE%"=="" set "SSL_FLAGS=!SSL_FLAGS! --ssl-mode=%DB_SSL_MODE%"
if not "%DB_SSL_CA_PATH%"=="" set "SSL_FLAGS=!SSL_FLAGS! --ssl-ca=%DB_SSL_CA_PATH%"
if not "%DB_SSL_CERT_PATH%"=="" set "SSL_FLAGS=!SSL_FLAGS! --ssl-cert=%DB_SSL_CERT_PATH%"
if not "%DB_SSL_KEY_PATH%"=="" set "SSL_FLAGS=!SSL_FLAGS! --ssl-key=%DB_SSL_KEY_PATH%"

goto :RUN_DUMP

:MODE_LOCAL
set "DBMODE=LOCAL"
call :ValidateRequired MYSQL_HOST MYSQL_PORT MYSQL_DATABASE MYSQL_USER MYSQL_PASSWORD || exit /b 2

set "HOST=%MYSQL_HOST%"
set "PORT=%MYSQL_PORT%"
set "DBNAME=%MYSQL_DATABASE%"
set "USER=%MYSQL_USER%"
set "PASSWORD=%MYSQL_PASSWORD%"

set "SSL_FLAGS="
goto :RUN_DUMP

:RUN_DUMP
REM Create target directory if it doesn't exist
if not exist "%TARGET_DIRECTORY%" mkdir "%TARGET_DIRECTORY%"

REM Stable, locale-independent timestamp via PowerShell (avoids %DATE%/%TIME% quirks)
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set "TS=%%I"

REM Build safe filename (Windows forbids colon in filenames, so we use HH-mm)
set "FILENAME=%PROJECT%_%DBNAME%_%TS%.sql"
set "OUTFILE=%TARGET_DIRECTORY%\%FILENAME%"

echo.
echo ==============================================================================
echo Database backup
echo - Mode:   %DBMODE%
echo - Env:    %ENV_FILE%
echo - Host:   %HOST%:%PORT%
echo - DB:     %DBNAME%
echo - Target: %OUTFILE%
echo ==============================================================================
echo.

REM IMPORTANT: Use --single-transaction for InnoDB consistency without locking tables
REM            (avoid with MyISAM heavy DBs).
REM NOTE: We pass password with -p... which may be visible in process list on some systems.
REM       On Windows this is typically acceptable for local use, but keep in mind when using PROD.
mysqldump ^
  --host="%HOST%" ^
  --port="%PORT%" ^
  --user="%USER%" ^
  --password="%PASSWORD%" ^
  --databases "%DBNAME%" ^
  --single-transaction ^
  --quick ^
  --routines ^
  --triggers ^
  --events ^
  --hex-blob ^
  --set-gtid-purged=OFF ^
  --default-character-set=utf8mb4 ^
  %SSL_FLAGS% ^
  > "%OUTFILE%"

if errorlevel 1 (
  echo.
  echo ERROR: mysqldump failed. No valid backup produced.
  echo - Check that mysqldump is installed and available in PATH.
  echo - Verify connectivity to %HOST%:%PORT% and credentials for %DBNAME%.
  echo.
  exit /b 1
)

echo.
echo SUCCESS: Backup created:
echo   %OUTFILE%
echo.
exit /b 0


REM ==============================================================================
REM Helpers
REM ==============================================================================

:LoadEnv
REM Loads KEY=VALUE pairs from a .env file into the current process environment.
REM - Lines starting with # are ignored.
REM - Empty lines are ignored.
REM - Values are taken verbatim (no quotes stripping beyond simple wrapping "...")
set "FILE=%~1"
if not exist "%FILE%" (
  REM No .env file is not a hard error; some users will set env vars in their shell/session.
  goto :eof
)

for /f "usebackq tokens=1* delims==" %%A in ("%FILE%") do (
  set "K=%%A"
  set "V=%%B"

  REM Trim leading spaces in key
  for /f "tokens=* delims= " %%K in ("!K!") do set "K=%%K"

  REM Skip comments/empty
  if "!K!"=="" goto :continue_env
  if "!K:~0,1!"=="#" goto :continue_env

  REM Remove optional surrounding quotes for value
  if defined V (
    if "!V:~0,1!"=="^"" (
      if "!V:~-1!"=="^"" set "V=!V:~1,-1!"
    )
  )

  set "!K!=!V!"
  :continue_env
)
goto :eof

:ValidateRequired
REM Validates that each named variable is set and not empty.
REM Usage: call :ValidateRequired VAR1 VAR2 VAR3 ...
set "MISSING="
:validate_loop
if "%~1"=="" goto :validate_done
call set "VAL=%%%~1%%"
if "%VAL%"=="" set "MISSING=%MISSING% %~1"
shift
goto :validate_loop
:validate_done

if not "%MISSING%"=="" (
  echo.
  echo ERROR: Missing required environment variables:%MISSING%
  echo - Edit "%ENV_FILE%" and set the variables above.
  echo - For PROD:  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
  echo - For LOCAL: MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
  echo.
  exit /b 1
)

exit /b 0
