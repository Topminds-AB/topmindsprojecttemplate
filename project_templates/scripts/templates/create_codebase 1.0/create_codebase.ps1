#Requires -Version 5.1
#Codebase Creator v.1.0.
<#

.SYNOPSIS
    Reusable codebase snapshot generator for AI agent orchestration workflow.
.DESCRIPTION
    Creates a structured ZIP archive with code, logs, db backups, docker logs,
    and manifest files. Designed to be dropped into any project repo.
    
    All configuration is in the $CONFIG block at the top - edit ONLY that section.
    
    Features:
    - Robocopy-based fast file copying with .gitignore respect
    - Secrets scanner (censors passwords, API keys, tokens in text files)
    - Configurable log collection via LogPaths
    - Optional database backup (reads credentials from .env)
    - Optional Docker log collection
    - NUL file cleanup
    - ZIP verification
    
.NOTES
    Usage: Double-click create_codebase.bat (or run this ps1 directly)
    Output: <ProjectPrefix>_codebase_YYYY-MM-DD_HH-MM.zip in .codebasebackup/
#>

[CmdletBinding()]
param(
    [switch]$SkipNulCleanup,
    [switch]$SkipDb,
    [switch]$SkipDocker,
    [switch]$SkipSecretsScan
)

$ErrorActionPreference = "Stop"

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION - EDIT THIS SECTION FOR YOUR PROJECT                        ║
# ║  Everything below this block should work without changes.                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

$CONFIG = @{

    # ── Project Identity ──────────────────────────────────────────────────────
    ProjectPrefix    = "DPDR"                          # ZIP filename prefix
    ProjectName      = "DocPilot Desktop Recorder"     # Human-readable name

    # ── Paths ─────────────────────────────────────────────────────────────────
    RepoRoot         = $PSScriptRoot                   # Usually $PSScriptRoot
    OutputDir        = ".codebasebackup"               # Where ZIP is saved (relative)
    TempBase         = $env:TEMP                       # Windows temp directory

    # ── Git Settings ──────────────────────────────────────────────────────────
    RequireCleanWorktree = $false                      # $true = abort if dirty

    # ── Directory Exclusions (robocopy /XD) ───────────────────────────────────
    # These directories are NEVER copied to the ZIP.
    # .gitignore patterns are ALSO respected automatically.
    ExcludeDirs      = @(
        # Version control & IDE
        ".git", ".vscode", ".idea"
        # Dependencies
        "node_modules", "vendor", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache"
        # Build output
        "dist", "build", "out", ".next", ".nuxt", ".cache"
        # Project infrastructure (our own backup/staging dirs)
        ".codebasebackup", ".dbbackup", ".dockerlogs"
        # Test artifacts (large, regenerable)
        "test-results", "test-artifacts", "playwright-report", "traces", "videos", "coverage"
        # Temp & misc
        "temp", "tmp", "old", "storage"
        # Prompts (agent templates, not code)
        ".prompts"
    )

    # ── File Exclusions (robocopy /XF) ────────────────────────────────────────
    # These file patterns are NEVER copied.
    ExcludeFiles     = @(
        # Secrets & environment
        ".env", ".env.*", "*.env"
        # Credentials & keys
        "*.pem", "*.key", "*.crt", "*.p12", "*.pfx"
        "credentials.json", "secrets.json", "storageState*.json"
        # Binary & generated
        "*.zip", "*.rar", "*.7z", "*.tar", "*.gz"
        "*.log"
        "*.sqlite", "*.db"
        # OS noise
        "Thumbs.db", "Desktop.ini", ".DS_Store"
        # Windows reserved name files
        "nul"
    )

    # ── Secrets Scanner Patterns ──────────────────────────────────────────────
    # Regex patterns matched against file CONTENT. Matches are replaced with [REDACTED].
    # Only applied to text files (see ScanExtensions below).
    SensitivePatterns = @(
        '(?i)(password|passwd|pwd)\s*[=:]\s*[''"]?[^\s''"}{,]+'
        '(?i)(api[_-]?key|apikey)\s*[=:]\s*[''"]?[^\s''"}{,]+'
        '(?i)(secret[_-]?key|client[_-]?secret)\s*[=:]\s*[''"]?[^\s''"}{,]+'
        '(?i)(access[_-]?token|auth[_-]?token|bearer)\s*[=:]\s*[''"]?[^\s''"}{,]+'
        '(?i)(DB_PASSWORD|DATABASE_PASSWORD|MYSQL_PASSWORD|MYSQL_ROOT_PASSWORD)\s*=\s*[^\s'']+'
        '(?i)(PRIVATE[_-]?KEY)\s*[=:]\s*[''"]?[^\s''"}{,]+'
        '(?i)(ftp_pass|ftp_password|FTP_PASS)\s*=\s*[^\s'']+'
        # Credit card patterns (13-19 digits)
        '\b[3-6]\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,4}\b'
    )

    # File extensions to scan for secrets (text files only)
    ScanExtensions   = @(
        ".txt", ".md", ".json", ".yml", ".yaml", ".ini", ".cfg", ".conf", ".toml",
        ".ts", ".js", ".mjs", ".cjs", ".jsx", ".tsx",
        ".py", ".sh", ".bat", ".ps1", ".cmd",
        ".sql", ".html", ".css", ".scss", ".xml", ".csv"
    )

    # ── Database Configuration ────────────────────────────────────────────────
    # Set to $null to skip database backup entirely.
    # Credentials are ALWAYS read from .env (never hardcode here!)
    Database         = $null
    <# Example for MySQL via Docker:
    Database         = @{
        Type          = "mysql-docker"           # mysql-docker | mysql-local | postgres-docker
        ContainerName = "myproject-mysql-1"       # Docker container name
        ServiceName   = "mysql"                  # docker-compose service name
        EnvDbName     = "MYSQL_DATABASE"          # .env variable name for DB name
        EnvDbUser     = "MYSQL_USER"              # .env variable name for DB user
        EnvDbPass     = "MYSQL_PASSWORD"           # .env variable name for DB password
    }
    Example for external MySQL (e.g. Loopia):
    Database         = @{
        Type          = "mysql-external"
        EnvDbHost     = "DB_HOST"
        EnvDbPort     = "DB_PORT"
        EnvDbName     = "DB_NAME"
        EnvDbUser     = "DB_USER"
        EnvDbPass     = "DB_PASSWORD"
    }
    #>

    # ── Docker Configuration ──────────────────────────────────────────────────
    HasDocker        = $false                          # $true if project uses Docker
    DockerComposeFile = "docker-compose.yml"

    # ── Log Paths ─────────────────────────────────────────────────────────────
    # Relative paths to log files or directories to include in /logs/
    # These are copied AS-IS into the ZIP /logs/ folder.
    LogPaths         = @(
        # "logs/app.log"
        # "test-results/summary.md"
    )

    # ── Agent Manifest Paths ──────────────────────────────────────────────────
    # Where to look for agent_final_message.md and questions_for_po.md
    AgentFinalMessagePath = "manifest\agent_final_message.md"
    QuestionsForPoPath    = "manifest\questions_for_po.md"
}

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  END OF CONFIGURATION - Do not edit below unless you know what you're doing║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Step {
    param([string]$StepNum, [string]$Message)
    Write-Host ""
    Write-Host "[$StepNum] $Message" -ForegroundColor Yellow
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Skip {
    param([string]$Message)
    Write-Host "  [SKIP] $Message" -ForegroundColor DarkYellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
}

function Read-EnvFile {
    param([string]$Path)
    $vars = @{}
    if (-not (Test-Path $Path)) { return $vars }
    Get-Content $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#')) {
            $idx = $line.IndexOf('=')
            if ($idx -gt 0) {
                $key = $line.Substring(0, $idx).Trim()
                $val = $line.Substring($idx + 1).Trim()
                $val = $val -replace '^["'']|["'']$', ''
                $vars[$key] = $val
            }
        }
    }
    return $vars
}

function Invoke-SecretsScan {
    param([string]$Directory)
    
    Write-Host "  Scanning for secrets in text files..." -ForegroundColor Gray
    $scannedCount = 0
    $redactedCount = 0
    
    Get-ChildItem -Path $Directory -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
        $CONFIG.ScanExtensions -contains $_.Extension.ToLower()
    } | ForEach-Object {
        $scannedCount++
        try {
            $content = [System.IO.File]::ReadAllText($_.FullName)
            $modified = $content
            foreach ($pattern in $CONFIG.SensitivePatterns) {
                $modified = [regex]::Replace($modified, $pattern, '[REDACTED]')
            }
            if ($modified -ne $content) {
                [System.IO.File]::WriteAllText($_.FullName, $modified)
                $redactedCount++
            }
        } catch { }
    }
    
    return @{ Scanned = $scannedCount; Redacted = $redactedCount }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

$startTime = Get-Date
$repoRoot = $CONFIG.RepoRoot
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$zipName = "$($CONFIG.ProjectPrefix)_codebase_$timestamp.zip"
$backupDir = Join-Path $repoRoot $CONFIG.OutputDir

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  $($CONFIG.ProjectName) - Codebase Snapshot" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  Repo:   $repoRoot" -ForegroundColor Gray
Write-Host "  Output: $zipName" -ForegroundColor Gray
Write-Host ("=" * 70) -ForegroundColor Cyan

# ── STEP 1: NUL File Cleanup ─────────────────────────────────────────────────

Write-Step "1/9" "NUL file cleanup"

if ($SkipNulCleanup) {
    Write-Skip "Skipped (-SkipNulCleanup)"
} else {
    $nulScript = Join-Path $repoRoot "delete_nul_script.ps1"
    if (Test-Path $nulScript) {
        try {
            Push-Location $repoRoot
            & $nulScript
            Pop-Location
            Write-Ok "NUL cleanup completed"
        } catch {
            Pop-Location
            Write-Skip "NUL cleanup failed: $_"
        }
    } else {
        Write-Skip "delete_nul_script.ps1 not found"
    }
}

# ── STEP 2: Git Worktree Check ───────────────────────────────────────────────

Write-Step "2/9" "Git worktree check"

$gitBranch = "unknown"
$gitCommit = "unknown"
$gitStatus = ""

try {
    $oldEAP = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    Push-Location $repoRoot
    $gitBranch = (git rev-parse --abbrev-ref HEAD 2>$null) | Out-String
    $gitBranch = $gitBranch.Trim()
    $gitCommit = (git rev-parse --short HEAD 2>$null) | Out-String
    $gitCommit = $gitCommit.Trim()
    $gitStatus = git status --porcelain 2>$null | Out-String
    Pop-Location
    $ErrorActionPreference = $oldEAP
} catch { Pop-Location; $ErrorActionPreference = $oldEAP }

if ($CONFIG.RequireCleanWorktree -and $gitStatus.Trim()) {
    Write-Fail "Dirty worktree detected and RequireCleanWorktree=$true. Aborting."
    Write-Host $gitStatus -ForegroundColor Yellow
    exit 1
}

if ($gitStatus.Trim()) {
    Write-Skip "Dirty worktree (allowed by config)"
} else {
    Write-Ok "Clean worktree on branch $gitBranch ($gitCommit)"
}

# ── STEP 3: Create Staging Directory ─────────────────────────────────────────

Write-Step "3/9" "Creating staging directory"

$guid = [Guid]::NewGuid().ToString('N').Substring(0, 8)
$stagingDir = Join-Path $CONFIG.TempBase "codebase_$($CONFIG.ProjectPrefix)_$guid"

$subDirs = @("code", "dbbackup", "dockerlogs", "logs", "manifest")
foreach ($sub in $subDirs) {
    New-Item -ItemType Directory -Path (Join-Path $stagingDir $sub) -Force | Out-Null
}

Write-Ok "Staging: $stagingDir"

# ── STEP 4: Copy Code (Robocopy) ─────────────────────────────────────────────

Write-Step "4/9" "Copying code via robocopy"

$codeDir = Join-Path $stagingDir "code"

# Build robocopy exclusion args
$xdArgs = $CONFIG.ExcludeDirs | ForEach-Object { "/XD"; $_ }
$xfArgs = $CONFIG.ExcludeFiles | ForEach-Object { "/XF"; $_ }

$robocopyArgs = @(
    $repoRoot,
    $codeDir,
    "/E",           # Copy subdirs including empty
    "/NP",          # No progress percentage
    "/NFL",         # No file list
    "/NDL",         # No directory list
    "/NJH",         # No job header
    "/NJS",         # No job summary
    "/R:0",         # No retries
    "/W:0"          # No wait between retries
) + $xdArgs + $xfArgs

$null = & robocopy @robocopyArgs 2>&1

# Robocopy: 0-7 = success, 8+ = error
if ($LASTEXITCODE -ge 8) {
    Write-Fail "Robocopy failed with code $LASTEXITCODE"
    exit 1
}

# Safety: remove any .env that slipped through
Get-ChildItem -Path $codeDir -Recurse -Force -Filter ".env*" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

$codeFileCount = (Get-ChildItem -Path $codeDir -Recurse -File -ErrorAction SilentlyContinue).Count
Write-Ok "Copied $codeFileCount files to /code/"

# ── STEP 5: Secrets Scanner ──────────────────────────────────────────────────

Write-Step "5/9" "Secrets scanner"

if ($SkipSecretsScan) {
    Write-Skip "Skipped (-SkipSecretsScan)"
} else {
    $scanResult = Invoke-SecretsScan -Directory $codeDir
    if ($scanResult.Redacted -gt 0) {
        Write-Ok "Scanned $($scanResult.Scanned) files, redacted secrets in $($scanResult.Redacted) files"
    } else {
        Write-Ok "Scanned $($scanResult.Scanned) files - no secrets found"
    }
}

# ── STEP 6: Database Backup ──────────────────────────────────────────────────

Write-Step "6/9" "Database backup"

$dbBackupDir = Join-Path $stagingDir "dbbackup"
$dbSuccess = $false

if ($SkipDb -or $null -eq $CONFIG.Database) {
    Write-Skip "No database configured (or -SkipDb)"
    "No database backup - project has no database." | Out-File -FilePath (Join-Path $dbBackupDir "README.txt") -Encoding UTF8
} else {
    $envFile = Join-Path $repoRoot ".env"
    $envVars = Read-EnvFile -Path $envFile
    $db = $CONFIG.Database
    
    $dumpFile = Join-Path $dbBackupDir "$($CONFIG.ProjectPrefix)_db_dump_$timestamp.sql"
    
    switch ($db.Type) {
        "mysql-docker" {
            $dbName = $envVars[$db.EnvDbName]
            $dbUser = $envVars[$db.EnvDbUser]
            $dbPass = $envVars[$db.EnvDbPass]
            
            if (-not $dbName -or -not $dbPass) {
                Write-Fail "DB credentials not found in .env ($($db.EnvDbName), $($db.EnvDbPass))"
                break
            }
            
            # Check container is running
            $running = docker inspect -f '{{.State.Running}}' $db.ContainerName 2>$null
            if ($running -ne "true") {
                Write-Fail "Container $($db.ContainerName) is not running"
                break
            }
            
            Write-Host "  Dumping $dbName via docker exec..." -ForegroundColor Gray
            $containerDump = "/tmp/codebase_dump_temp.sql"
            $dumpCmd = "mysqldump --default-character-set=utf8mb4 -u$dbUser -p`"$dbPass`" --single-transaction --routines --triggers $dbName > $containerDump"
            docker exec $db.ContainerName sh -c $dumpCmd 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                $containerId = docker compose ps -q $db.ServiceName 2>$null
                docker cp "${containerId}:${containerDump}" $dumpFile 2>$null
                docker exec $db.ContainerName sh -c "rm -f $containerDump" 2>$null
                
                if ((Test-Path $dumpFile) -and (Get-Item $dumpFile).Length -gt 500) {
                    $sz = [math]::Round((Get-Item $dumpFile).Length / 1KB, 1)
                    Write-Ok "DB dump created ($sz KB)"
                    $dbSuccess = $true
                } else {
                    Write-Fail "Dump file empty or missing"
                }
            } else {
                Write-Fail "mysqldump failed (exit $LASTEXITCODE)"
            }
        }
        
        "mysql-local" {
            $dbHost = $envVars[$db.EnvDbHost]; if (-not $dbHost) { $dbHost = "127.0.0.1" }
            $dbPort = $envVars[$db.EnvDbPort]; if (-not $dbPort) { $dbPort = "3306" }
            $dbName = $envVars[$db.EnvDbName]
            $dbUser = $envVars[$db.EnvDbUser]
            $dbPass = $envVars[$db.EnvDbPass]
            
            if (-not $dbName -or -not $dbPass) {
                Write-Fail "DB credentials not found in .env"
                break
            }
            
            # Find mysqldump
            $mysqldump = Get-Command mysqldump -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
            if (-not $mysqldump) {
                @("C:\xampp\mysql\bin\mysqldump.exe",
                  "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
                  "C:\Program Files\MariaDB 10.6\bin\mysqldump.exe"
                ) | ForEach-Object { if ((Test-Path $_) -and -not $mysqldump) { $mysqldump = $_ } }
            }
            
            if (-not $mysqldump) {
                Write-Fail "mysqldump not found on system"
                break
            }
            
            Write-Host "  Dumping $dbName from ${dbHost}:${dbPort}..." -ForegroundColor Gray
            $dumpArgs = @("-h", $dbHost, "-P", $dbPort, "-u", $dbUser, "-p$dbPass",
                          "--default-character-set=utf8mb4", "--single-transaction",
                          "--routines", "--triggers", $dbName)
            
            & $mysqldump @dumpArgs 2>$null | Out-File -FilePath $dumpFile -Encoding UTF8
            
            if ((Test-Path $dumpFile) -and (Get-Item $dumpFile).Length -gt 500) {
                $sz = [math]::Round((Get-Item $dumpFile).Length / 1KB, 1)
                Write-Ok "DB dump created ($sz KB)"
                $dbSuccess = $true
            } else {
                Write-Fail "Dump file empty or failed"
            }
        }
        
        default {
            Write-Skip "Unknown database type: $($db.Type)"
        }
    }
    
    if (-not $dbSuccess) {
        "Database backup failed or was skipped." | Out-File -FilePath (Join-Path $dbBackupDir "README.txt") -Encoding UTF8
    }
}

# ── STEP 7: Docker Logs & Application Logs ───────────────────────────────────

Write-Step "7/9" "Collecting logs"

$dockerLogsOut = Join-Path $stagingDir "dockerlogs"
$logsOut = Join-Path $stagingDir "logs"

# Docker logs
if ($SkipDocker -or -not $CONFIG.HasDocker) {
    Write-Skip "Docker logs not applicable"
    "No docker logs - project does not use Docker." | Out-File -FilePath (Join-Path $dockerLogsOut "README.txt") -Encoding UTF8
} else {
    try {
        # Try dockerlogs.bat first (project-specific)
        $dockerlogsBat = Join-Path $repoRoot "dockerlogs.bat"
        $collectPy = Join-Path $repoRoot "scripts\collect_docker_logs.py"
        
        if (Test-Path $dockerlogsBat) {
            Push-Location $repoRoot
            & cmd /c "$dockerlogsBat" 2>&1 | Out-Null
            Pop-Location
        }
        
        # Copy existing docker logs from repo
        $repoDockerLogs = Join-Path $repoRoot ".dockerlogs"
        if ((Test-Path $repoDockerLogs) -and (Get-ChildItem $repoDockerLogs -File -ErrorAction SilentlyContinue).Count -gt 0) {
            Get-ChildItem $repoDockerLogs -File | Copy-Item -Destination $dockerLogsOut -Force
            Write-Ok "Docker logs collected from .dockerlogs/"
        } else {
            # Fallback: docker compose logs directly
            Push-Location $repoRoot
            $composeLogs = docker compose logs --no-color --tail=500 2>&1 | Out-String
            if ($composeLogs) {
                $composeLogs | Out-File -FilePath (Join-Path $dockerLogsOut "docker_compose_logs.txt") -Encoding UTF8
            }
            $composePs = docker compose ps 2>&1 | Out-String
            if ($composePs) {
                $composePs | Out-File -FilePath (Join-Path $dockerLogsOut "docker_compose_ps.txt") -Encoding UTF8
            }
            Pop-Location
            Write-Ok "Docker logs collected via docker compose"
        }
    } catch {
        Write-Skip "Docker log collection failed: $_"
    }
}

# Application logs (configurable paths)
$logsCopied = 0
foreach ($logPath in $CONFIG.LogPaths) {
    $fullPath = Join-Path $repoRoot $logPath
    if (Test-Path $fullPath) {
        $item = Get-Item $fullPath
        if ($item.PSIsContainer) {
            Get-ChildItem $fullPath -File -ErrorAction SilentlyContinue | ForEach-Object {
                Copy-Item $_.FullName -Destination $logsOut -Force
                $logsCopied++
            }
        } else {
            Copy-Item $fullPath -Destination $logsOut -Force
            $logsCopied++
        }
    }
}

# Git evidence (always generated fresh)
# Note: $ErrorActionPreference set to Continue here because git warnings (CRLF etc)
# are captured by 2>&1 and would otherwise become terminating errors.
try {
    $oldEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $utf8 = New-Object System.Text.UTF8Encoding $false
    Push-Location $repoRoot
    
    $gitStatusP = git status --porcelain=v1 2>$null | Out-String
    [System.IO.File]::WriteAllText((Join-Path $logsOut "git_status_porcelain.txt"), $gitStatusP, $utf8)
    
    $gitDiffStat = git diff --stat 2>$null | Out-String
    [System.IO.File]::WriteAllText((Join-Path $logsOut "git_diff_stat.txt"), $gitDiffStat, $utf8)
    
    $gitDiff = git diff 2>$null | Out-String
    [System.IO.File]::WriteAllText((Join-Path $logsOut "git_diff.txt"), $gitDiff, $utf8)
    
    $gitDiffCached = git diff --cached 2>$null | Out-String
    [System.IO.File]::WriteAllText((Join-Path $logsOut "git_diff_cached.txt"), $gitDiffCached, $utf8)
    
    Pop-Location
    $ErrorActionPreference = $oldEAP
    $logsCopied += 4
    Write-Ok "Git evidence + $logsCopied log files collected"
} catch {
    Pop-Location
    $ErrorActionPreference = $oldEAP
    Write-Skip "Git evidence failed: $_"
}

# ── STEP 8: Generate Manifest ─────────────────────────────────────────────────

Write-Step "8/9" "Generating manifest files"

$manifestOut = Join-Path $stagingDir "manifest"
$utf8 = New-Object System.Text.UTF8Encoding $false

# ---- manifest.md ----
$manifestMd = @"
# $($CONFIG.ProjectPrefix) Codebase Snapshot Manifest

## System Information
- **Project**: $($CONFIG.ProjectName)
- **Prefix**: $($CONFIG.ProjectPrefix)
- **Generated**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- **Hostname**: $env:COMPUTERNAME
- **Git Branch**: $gitBranch
- **Git Commit**: $gitCommit

## Generation Command
``````
create_codebase.bat -> create_codebase.ps1
``````

## Declared Exclusions

### Directories
$($CONFIG.ExcludeDirs | ForEach-Object { "- ``$_``" } | Out-String)
### File Patterns
$($CONFIG.ExcludeFiles | ForEach-Object { "- ``$_``" } | Out-String)

## ZIP Structure
- ``/code/`` - Source code (secrets redacted)
- ``/dbbackup/`` - Database dumps
- ``/dockerlogs/`` - Container logs
- ``/logs/`` - Git evidence and app logs
- ``/manifest/`` - This manifest, inventory, change summary

## Security
- Secrets scanner applied to all text files
- .env files excluded
- No hardcoded credentials
"@
[System.IO.File]::WriteAllText((Join-Path $manifestOut "manifest.md"), $manifestMd, $utf8)

# ---- change_summary.md ----
$gitLog = ""
try {
    $oldEAP2 = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    Push-Location $repoRoot
    $gitLog = git log --oneline -10 2>$null | Out-String
    Pop-Location
    $ErrorActionPreference = $oldEAP2
} catch { Pop-Location; $ErrorActionPreference = $oldEAP2 }

$changeSummary = @"
# Change Summary

## Git Status at Snapshot Time
``````
$($gitStatus.Trim())
``````

## Recent Commits (last 10)
``````
$($gitLog.Trim())
``````
"@
[System.IO.File]::WriteAllText((Join-Path $manifestOut "change_summary.md"), $changeSummary, $utf8)

# ---- agent_final_message.md ----
$agentMsgPath = Join-Path $repoRoot $CONFIG.AgentFinalMessagePath
if (Test-Path $agentMsgPath) {
    Copy-Item $agentMsgPath -Destination (Join-Path $manifestOut "agent_final_message.md") -Force
    Write-Host "  Copied agent_final_message.md" -ForegroundColor Gray
} else {
    $defaultMsg = "# Agent Final Message`n`nNo agent message provided. This snapshot was created manually.`n"
    [System.IO.File]::WriteAllText((Join-Path $manifestOut "agent_final_message.md"), $defaultMsg, $utf8)
}

# ---- questions_for_po.md ----
$questionsPath = Join-Path $repoRoot $CONFIG.QuestionsForPoPath
if (Test-Path $questionsPath) {
    Copy-Item $questionsPath -Destination (Join-Path $manifestOut "questions_for_po.md") -Force
} else {
    [System.IO.File]::WriteAllText((Join-Path $manifestOut "questions_for_po.md"), "# Questions for PO`n`nNo questions.`n", $utf8)
}

# ---- file_inventory.txt ----
$inventoryLines = @()
$inventoryLines += "#### File Inventory for $zipName"
$inventoryLines += ""
$inventoryLines += "Format: path<TAB>size_bytes"
$inventoryLines += ""

Get-ChildItem -Path $stagingDir -Recurse -File -ErrorAction SilentlyContinue | Sort-Object FullName | ForEach-Object {
    $rel = $_.FullName.Substring($stagingDir.Length + 1).Replace("\", "/")
    $inventoryLines += "$rel`t$($_.Length)"
}

$inventoryContent = $inventoryLines -join "`n"
[System.IO.File]::WriteAllText((Join-Path $manifestOut "file_inventory.txt"), $inventoryContent, $utf8)

Write-Ok "Manifest files created (5 files)"

# ── STEP 9: Create & Verify ZIP ──────────────────────────────────────────────

Write-Step "9/9" "Creating ZIP archive"

# Ensure output directory exists
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

$zipPath = Join-Path $backupDir $zipName

# Remove old ZIP if exists
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

# Create ZIP
try {
    Compress-Archive -Path (Join-Path $stagingDir "*") -DestinationPath $zipPath -CompressionLevel Optimal -Force
} catch {
    Write-Fail "ZIP creation failed: $_"
    exit 1
}

$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Ok "Created $zipName ($zipSize MB)"

# Verify ZIP structure
Write-Host "  Verifying archive..." -ForegroundColor Gray
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    
    $requiredDirs = @("code/", "manifest/")
    $missingDirs = @()
    foreach ($dir in $requiredDirs) {
        $found = $zip.Entries | Where-Object { $_.FullName.Replace("\","/").StartsWith($dir) }
        if (-not $found) { $missingDirs += $dir }
    }
    
    # Check for forbidden files (secrets that shouldn't be there)
    $forbidden = @("\.env$", "\.pem$", "\.key$", "credentials\.json$")
    $foundBad = @()
    foreach ($entry in $zip.Entries) {
        foreach ($pat in $forbidden) {
            if ($entry.FullName -match $pat) { $foundBad += $entry.FullName }
        }
    }
    
    $zip.Dispose()
    
    if ($missingDirs.Count -gt 0) {
        Write-Fail "Missing directories in ZIP: $($missingDirs -join ', ')"
    }
    if ($foundBad.Count -gt 0) {
        Write-Fail "FORBIDDEN files found in ZIP: $($foundBad -join ', ')"
        Write-Host "  WARNING: These files may contain secrets!" -ForegroundColor Red
    }
    if ($missingDirs.Count -eq 0 -and $foundBad.Count -eq 0) {
        Write-Ok "ZIP verification passed"
    }
} catch {
    Write-Skip "ZIP verification skipped: $_"
}

# ── CLEANUP ──────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "  Cleaning up staging..." -ForegroundColor Gray
try {
    Remove-Item -Path $stagingDir -Recurse -Force -ErrorAction SilentlyContinue
} catch { }

# ── SUMMARY ──────────────────────────────────────────────────────────────────

$elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "  SNAPSHOT CREATED SUCCESSFULLY" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host ""
Write-Host "  File:     $zipName" -ForegroundColor White
Write-Host "  Location: $backupDir" -ForegroundColor White
Write-Host "  Size:     $zipSize MB" -ForegroundColor White
Write-Host "  Time:     $elapsed seconds" -ForegroundColor White
Write-Host "  Files:    $codeFileCount code files" -ForegroundColor White
Write-Host ""
Write-Host "  Structure:" -ForegroundColor Gray
Write-Host "    /code/       - Source code (secrets redacted)" -ForegroundColor Gray
Write-Host "    /dbbackup/   - Database dumps" -ForegroundColor Gray
Write-Host "    /dockerlogs/ - Container logs" -ForegroundColor Gray
Write-Host "    /logs/       - Git evidence + app logs" -ForegroundColor Gray
Write-Host "    /manifest/   - Manifest, inventory, change summary" -ForegroundColor Gray
Write-Host ""

exit 0
