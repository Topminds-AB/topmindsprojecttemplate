#Requires -Version 5.1

Set-StrictMode -Version Latest

$script:SnapshotExcludeDirs = @(
    '.git', '.vscode', '.idea',
    'node_modules', 'vendor', '.venv', 'venv', '__pycache__', '.pytest_cache', '.mypy_cache',
    'dist', 'build', 'out', '.next', '.nuxt', '.cache',
    '.codebasebackup', '.dbbackup', '.dockerlogs',
    'test-results', 'test-artifacts', 'playwright-report', 'traces', 'videos', 'coverage',
    'temp', 'tmp', 'old', 'storage',
    '.prompts'
)

$script:SnapshotExcludeFiles = @(
    '.env', '.env.*', '*.env',
    '*.pem', '*.key', '*.crt', '*.p12', '*.pfx',
    'credentials.json', 'secrets.json', 'storageState*.json',
    '*.zip', '*.rar', '*.7z', '*.tar', '*.gz',
    '*.log',
    'Thumbs.db', 'Desktop.ini', '.DS_Store',
    'nul'
)

$script:SnapshotScanExtensions = @(
    '.txt', '.md', '.json', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.toml',
    '.ts', '.js', '.mjs', '.cjs', '.jsx', '.tsx',
    '.py', '.sh', '.bat', '.ps1', '.cmd',
    '.sql', '.html', '.css', '.scss', '.xml', '.csv'
)

$script:SnapshotSensitivePatterns = @(
    '(?i)(password|passwd|pwd)\s*[=:]\s*[''"]?[^\s''"}{,]+',
    '(?i)(api[_-]?key|apikey)\s*[=:]\s*[''"]?[^\s''"}{,]+',
    '(?i)(secret[_-]?key|client[_-]?secret)\s*[=:]\s*[''"]?[^\s''"}{,]+',
    '(?i)(access[_-]?token|auth[_-]?token|bearer)\s*[=:]\s*[''"]?[^\s''"}{,]+',
    '(?i)(DB_PASSWORD|DATABASE_PASSWORD|MYSQL_PASSWORD|MYSQL_ROOT_PASSWORD|POSTGRES_PASSWORD)\s*=\s*[^\s'']+',
    '(?i)(PRIVATE[_-]?KEY)\s*[=:]\s*[''"]?[^\s''"}{,]+',
    '(?i)(ftp_pass|ftp_password|FTP_PASS)\s*=\s*[^\s'']+'
)

function Write-Step {
    param([string]$StepNum, [string]$Message)
    Write-Host ''
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

function Format-FileSize {
    param([long]$Bytes)

    if ($Bytes -ge 1MB) { return '{0:N1} MB' -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return '{0:N1} KB' -f ($Bytes / 1KB) }
    return "$Bytes B"
}

function Build-RepoTree {
    param(
        [string]$RootPath,
        [string[]]$ExcludeTopDirs
    )

    $output = New-Object System.Collections.Generic.List[string]
    $output.Add((Split-Path $RootPath -Leaf))

    function Recurse {
        param(
            [string]$Directory,
            [string]$Prefix,
            [string[]]$Skip
        )

        $items = @(Get-ChildItem -LiteralPath $Directory -Force -ErrorAction SilentlyContinue |
            Where-Object { -not ($_.PSIsContainer -and $Skip -contains $_.Name) } |
            Sort-Object { -not $_.PSIsContainer }, Name)

        for ($i = 0; $i -lt $items.Count; $i++) {
            $last = ($i -eq ($items.Count - 1))
            $connector = if ($last) { '\---' } else { '+---' }
            $extension = if ($last) { '    ' } else { '|   ' }
            if ($items[$i].PSIsContainer) {
                $output.Add("${Prefix}${connector}$($items[$i].Name)")
                Recurse -Directory $items[$i].FullName -Prefix "${Prefix}${extension}" -Skip @()
            } else {
                $output.Add("${Prefix}${connector}$($items[$i].Name)  ($(Format-FileSize $items[$i].Length))")
            }
        }
    }

    Recurse -Directory $RootPath -Prefix '' -Skip $ExcludeTopDirs
    return ($output.ToArray() -join "`n")
}

function Invoke-SecretsScan {
    param([string]$Directory)

    $scanned = 0
    $redacted = 0

    Get-ChildItem -LiteralPath $Directory -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
        $script:SnapshotScanExtensions -contains $_.Extension.ToLowerInvariant()
    } | ForEach-Object {
        $scanned++
        try {
            $content = [System.IO.File]::ReadAllText($_.FullName)
            $updated = $content
            foreach ($pattern in $script:SnapshotSensitivePatterns) {
                $updated = [regex]::Replace($updated, $pattern, '[REDACTED]')
            }
            if ($updated -ne $content) {
                [System.IO.File]::WriteAllText($_.FullName, $updated)
                $redacted++
            }
        } catch {
        }
    }

    return [pscustomobject]@{
        Scanned = $scanned
        Redacted = $redacted
    }
}

function Get-ExtraLogPaths {
    param([hashtable]$EnvValues)

    $value = Get-ConfigValue -FileValues $EnvValues -Names @('CREATE_CODEBASE_LOG_PATHS') -ExplicitValue $null
    $paths = New-Object System.Collections.Generic.List[string]
    foreach ($default in @('logs', 'storage\logs', 'manifest')) {
        $paths.Add($default)
    }

    if ($value) {
        foreach ($path in ($value -split ',')) {
            $trimmed = $path.Trim()
            if ($trimmed) {
                $paths.Add($trimmed)
            }
        }
    }

    return $paths | Sort-Object -Unique
}

function Invoke-CreateCodebase {
    param(
        [string]$RepoRoot,
        [string]$ScriptRoot,
        [switch]$SkipNulCleanup,
        [switch]$SkipDb,
        [switch]$SkipDocker,
        [switch]$SkipSecretsScan
    )

    . (Join-Path $ScriptRoot 'template_runtime.ps1')

    $envFilePath = Get-PreferredEnvFile -RepoRoot $RepoRoot -ScriptRoot $ScriptRoot -ExplicitEnvFile $null
    $envValues = Read-KeyValueFile -Path $envFilePath
    $identity = Get-ProjectIdentity -RepoRoot $RepoRoot -EnvValues $envValues
    $startTime = Get-Date
    $timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm'
    $zipName = '{0}_codebase_{1}.zip' -f $identity.Prefix, $timestamp
    $backupDir = Join-Path $RepoRoot '.codebasebackup'

    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor Cyan
    Write-Host "  $($identity.DisplayName) - Codebase Snapshot" -ForegroundColor Cyan
    Write-Host ('=' * 70) -ForegroundColor Cyan
    Write-Host "  Repo:   $RepoRoot" -ForegroundColor Gray
    Write-Host "  Output: $zipName" -ForegroundColor Gray
    Write-Host ('=' * 70) -ForegroundColor Cyan

    Write-Step '1/9' 'NUL file cleanup'
    if ($SkipNulCleanup) {
        Write-Skip 'Skipped (-SkipNulCleanup)'
    } else {
        $nulScript = Join-Path $RepoRoot 'delete_nul_script.ps1'
        if (Test-Path -LiteralPath $nulScript) {
            try {
                Push-Location $RepoRoot
                & $nulScript
                Pop-Location
                Write-Ok 'NUL cleanup completed'
            } catch {
                Pop-Location
                Write-Skip "NUL cleanup failed: $_"
            }
        } else {
            Write-Skip 'delete_nul_script.ps1 not found'
        }
    }

    Write-Step '2/9' 'Git worktree check'
    $gitBranch = 'unknown'
    $gitCommit = 'unknown'
    $gitStatus = ''
    try {
        Push-Location $RepoRoot
        $gitBranch = ((git rev-parse --abbrev-ref HEAD 2>$null) | Out-String).Trim()
        $gitCommit = ((git rev-parse --short HEAD 2>$null) | Out-String).Trim()
        $gitStatus = (git status --porcelain 2>$null | Out-String)
        Pop-Location
    } catch {
        Pop-Location
    }
    if ($gitStatus.Trim()) { Write-Skip 'Dirty worktree (allowed by template)' } else { Write-Ok "Clean worktree on branch $gitBranch ($gitCommit)" }

    Write-Step '3/9' 'Creating staging directory'
    $stagingDir = Join-Path $env:TEMP ('codebase_{0}_{1}' -f $identity.RepoSlug, ([Guid]::NewGuid().ToString('N').Substring(0, 8)))
    foreach ($subDir in @('code', 'dbbackup', 'dockerlogs', 'logs', 'manifest')) {
        New-Item -ItemType Directory -Path (Join-Path $stagingDir $subDir) -Force | Out-Null
    }
    Write-Ok "Staging: $stagingDir"

    Write-Step '4/9' 'Copying code via robocopy'
    $codeDir = Join-Path $stagingDir 'code'
    $xdArgs = $script:SnapshotExcludeDirs | ForEach-Object { '/XD'; $_ }
    $xfArgs = $script:SnapshotExcludeFiles | ForEach-Object { '/XF'; $_ }
    $robocopyArgs = @($RepoRoot, $codeDir, '/E', '/NP', '/NFL', '/NDL', '/NJH', '/NJS', '/R:0', '/W:0') + $xdArgs + $xfArgs
    $null = & robocopy @robocopyArgs 2>&1
    if ($LASTEXITCODE -ge 8) {
        throw "Robocopy failed with code $LASTEXITCODE"
    }
    Get-ChildItem -LiteralPath $codeDir -Recurse -Force -Filter '.env*' -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    $codeFileCount = @(Get-ChildItem -LiteralPath $codeDir -Recurse -File -ErrorAction SilentlyContinue).Count
    Write-Ok "Copied $codeFileCount files to /code/"

    Write-Step '5/9' 'Secrets scanner'
    if ($SkipSecretsScan) {
        Write-Skip 'Skipped (-SkipSecretsScan)'
    } else {
        $scanResult = Invoke-SecretsScan -Directory $codeDir
        if ($scanResult.Redacted -gt 0) {
            Write-Ok "Scanned $($scanResult.Scanned) files, redacted secrets in $($scanResult.Redacted) files"
        } else {
            Write-Ok "Scanned $($scanResult.Scanned) files - no secrets found"
        }
    }

    Write-Step '6/9' 'Database backup'
    $stagingDbDir = Join-Path $stagingDir 'dbbackup'
    $repoDbDir = Join-Path $RepoRoot '.dbbackup'
    if ($SkipDb) {
        Write-Skip 'Skipped (-SkipDb)'
        Set-Content -LiteralPath (Join-Path $stagingDbDir 'README.txt') -Encoding UTF8 -Value 'Database backup skipped by request.'
    } else {
        $dbScript = Join-Path $RepoRoot 'scripts\dbbackup_full.ps1'
        if (Test-Path -LiteralPath $dbScript) {
            $dbOutput = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $dbScript -SkipIfUnconfigured
            if ($LASTEXITCODE -ne 0) {
                throw "dbbackup_full.ps1 failed with exit code $LASTEXITCODE"
            }
            if (Test-Path -LiteralPath $repoDbDir) {
                Get-ChildItem -LiteralPath $repoDbDir -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 12 | Copy-Item -Destination $stagingDbDir -Force
                if (@(Get-ChildItem -LiteralPath $stagingDbDir -File -ErrorAction SilentlyContinue).Count -gt 0) {
                    Write-Ok 'Database backup artifacts copied from repo-root .dbbackup'
                } else {
                    Set-Content -LiteralPath (Join-Path $stagingDbDir 'README.txt') -Encoding UTF8 -Value 'No database artifacts were present after backup step.'
                    Write-Skip 'No database backup artifacts were present'
                }
            } else {
                Set-Content -LiteralPath (Join-Path $stagingDbDir 'README.txt') -Encoding UTF8 -Value 'No repo-root .dbbackup directory exists.'
                Write-Skip 'No repo-root .dbbackup directory exists'
            }
            $dbOutput | Out-Null
        } else {
            Set-Content -LiteralPath (Join-Path $stagingDbDir 'README.txt') -Encoding UTF8 -Value 'No dbbackup_full.ps1 script exists.'
            Write-Skip 'No dbbackup_full.ps1 script exists'
        }
    }

    Write-Step '7/9' 'Collecting logs'
    $dockerLogsOut = Join-Path $stagingDir 'dockerlogs'
    $logsOut = Join-Path $stagingDir 'logs'
    $composeFiles = Get-ComposeFiles -RepoRoot $RepoRoot
    if ($SkipDocker -or ($composeFiles | Measure-Object).Count -eq 0) {
        $message = if ($SkipDocker) { 'Docker logs skipped (-SkipDocker)' } else { 'No compose files detected' }
        Write-Skip $message
        Set-Content -LiteralPath (Join-Path $dockerLogsOut 'README.txt') -Encoding UTF8 -Value $message
    } else {
        $dockerlogsBat = Join-Path $RepoRoot 'dockerlogs.bat'
        if (Test-Path -LiteralPath $dockerlogsBat) {
            & cmd /c "$dockerlogsBat" | Out-Null
        }
        $repoDockerLogs = Join-Path $RepoRoot '.dockerlogs'
        if (Test-Path -LiteralPath $repoDockerLogs) {
            Get-ChildItem -LiteralPath $repoDockerLogs -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | Copy-Item -Destination $dockerLogsOut -Force
        }
        if (@(Get-ChildItem -LiteralPath $dockerLogsOut -File -ErrorAction SilentlyContinue).Count -gt 0) {
            Write-Ok 'Docker logs collected'
        } else {
            Set-Content -LiteralPath (Join-Path $dockerLogsOut 'README.txt') -Encoding UTF8 -Value 'Docker log collection produced no files.'
            Write-Skip 'Docker log collection produced no files'
        }
    }

    $logsCopied = 0
    foreach ($logPath in Get-ExtraLogPaths -EnvValues $envValues) {
        $fullPath = Join-Path $RepoRoot $logPath
        if (-not (Test-Path -LiteralPath $fullPath)) {
            continue
        }
        $item = Get-Item -LiteralPath $fullPath
        if ($item.PSIsContainer) {
            Get-ChildItem -LiteralPath $fullPath -File -ErrorAction SilentlyContinue | Select-Object -First 25 | ForEach-Object {
                Copy-Item -LiteralPath $_.FullName -Destination $logsOut -Force
                $logsCopied++
            }
        } else {
            Copy-Item -LiteralPath $fullPath -Destination $logsOut -Force
            $logsCopied++
        }
    }

    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText((Join-Path $logsOut 'git_status_porcelain.txt'), $gitStatus, $utf8)
    $oldEap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    Push-Location $RepoRoot
    [System.IO.File]::WriteAllText((Join-Path $logsOut 'git_diff_stat.txt'), (git diff --stat 2>&1 | Out-String), $utf8)
    [System.IO.File]::WriteAllText((Join-Path $logsOut 'git_diff.txt'), (git diff 2>&1 | Out-String), $utf8)
    [System.IO.File]::WriteAllText((Join-Path $logsOut 'git_diff_cached.txt'), (git diff --cached 2>&1 | Out-String), $utf8)
    Pop-Location
    $ErrorActionPreference = $oldEap
    Write-Ok "Git evidence + $logsCopied log files collected"

    Write-Step '8/9' 'Generating manifest files'
    $manifestOut = Join-Path $stagingDir 'manifest'
    $manifestMd = @"
# $($identity.Prefix) Codebase Snapshot Manifest

## System Information
- **Project**: $($identity.DisplayName)
- **Prefix**: $($identity.Prefix)
- **Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Hostname**: $env:COMPUTERNAME
- **Git Branch**: $gitBranch
- **Git Commit**: $gitCommit
- **Env file**: $(if ($envFilePath) { $envFilePath } else { 'none' })

## Generation Command
``````
create_codebase.bat -> create_codebase.ps1 -> scripts/create_codebase_lib.ps1
``````

## ZIP Structure
- ``/code/`` - Source code (secrets redacted)
- ``/dbbackup/`` - Database dumps and metadata
- ``/dockerlogs/`` - Container logs
- ``/logs/`` - Git evidence and runtime logs
- ``/manifest/`` - Manifest, inventory, change summary
"@
    [System.IO.File]::WriteAllText((Join-Path $manifestOut 'manifest.md'), $manifestMd, $utf8)

    $gitLog = ''
    Push-Location $RepoRoot
    $gitLog = git log --oneline -10 2>$null | Out-String
    Pop-Location
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
    [System.IO.File]::WriteAllText((Join-Path $manifestOut 'change_summary.md'), $changeSummary, $utf8)

    $agentMessagePath = Join-Path $RepoRoot 'manifest\agent_final_message.md'
    if (Test-Path -LiteralPath $agentMessagePath) {
        Copy-Item -LiteralPath $agentMessagePath -Destination (Join-Path $manifestOut 'agent_final_message.md') -Force
    } else {
        [System.IO.File]::WriteAllText((Join-Path $manifestOut 'agent_final_message.md'), "# Agent Final Message`n`nNo agent message provided.`n", $utf8)
    }

    $questionsPath = Join-Path $RepoRoot 'manifest\questions_for_po.md'
    if (Test-Path -LiteralPath $questionsPath) {
        Copy-Item -LiteralPath $questionsPath -Destination (Join-Path $manifestOut 'questions_for_po.md') -Force
    } else {
        [System.IO.File]::WriteAllText((Join-Path $manifestOut 'questions_for_po.md'), "# Questions for PO`n`nNo questions.`n", $utf8)
    }

    $tree = Build-RepoTree -RootPath $RepoRoot -ExcludeTopDirs @('.git', '.codebasebackup')
    [System.IO.File]::WriteAllText((Join-Path $manifestOut 'file_inventory.txt'), $tree, $utf8)
    Write-Ok 'Manifest files created'

    Write-Step '9/9' 'Creating ZIP archive'
    if (-not (Test-Path -LiteralPath $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }
    $zipPath = Join-Path $backupDir $zipName
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    Compress-Archive -Path (Join-Path $stagingDir '*') -DestinationPath $zipPath -CompressionLevel Optimal -Force
    $zipSize = [math]::Round((Get-Item -LiteralPath $zipPath).Length / 1MB, 2)
    Write-Ok "Created $zipName ($zipSize MB)"

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        foreach ($requiredDir in @('code/', 'manifest/')) {
            $found = $zip.Entries | Where-Object { $_.FullName.Replace('\', '/').StartsWith($requiredDir) }
            if (-not $found) {
                throw "Missing directory in ZIP: $requiredDir"
            }
        }
    } finally {
        $zip.Dispose()
    }
    Write-Ok 'ZIP verification passed'

    Remove-Item -LiteralPath $stagingDir -Recurse -Force -ErrorAction SilentlyContinue
    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor Green
    Write-Host '  SNAPSHOT CREATED SUCCESSFULLY' -ForegroundColor Green
    Write-Host ('=' * 70) -ForegroundColor Green
    Write-Host ''
    Write-Host "  File:     $zipName" -ForegroundColor White
    Write-Host "  Location: $backupDir" -ForegroundColor White
    Write-Host "  Size:     $zipSize MB" -ForegroundColor White
    Write-Host "  Time:     $elapsed seconds" -ForegroundColor White
    Write-Host "  Files:    $codeFileCount code files" -ForegroundColor White

    return $zipPath
}
