[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$failures = New-Object System.Collections.Generic.List[string]

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        $failures.Add($Message)
    }
}

function Get-FileText {
    param([string]$Path)
    return [System.IO.File]::ReadAllText($Path)
}

$createCodebasePs1 = Join-Path $repoRoot 'create_codebase.ps1'
$createCodebaseBat = Join-Path $repoRoot 'create_codebase.bat'
$dockerlogsBat = Join-Path $repoRoot 'dockerlogs.bat'
$dbbackupBat = Join-Path $repoRoot 'scripts\dbbackup_full.bat'
$dbbackupPs1 = Join-Path $repoRoot 'scripts\dbbackup_full.ps1'
$runtimeHelper = Join-Path $repoRoot 'scripts\template_runtime.ps1'

Assert-True (Test-Path $runtimeHelper) 'Missing shared runtime helper scripts\template_runtime.ps1.'
Assert-True (Test-Path $dbbackupPs1) 'Missing PowerShell db backup engine scripts\dbbackup_full.ps1.'

$createCodebasePs1Text = Get-FileText $createCodebasePs1
$createCodebaseBatText = Get-FileText $createCodebaseBat
$createCodebaseBatLines = Get-Content $createCodebaseBat
$dockerlogsBatText = Get-FileText $dockerlogsBat
$dbbackupBatText = Get-FileText $dbbackupBat

Assert-True (-not ($createCodebasePs1Text -match 'ProjectPrefix\s*=\s*"DPDR"')) 'create_codebase.ps1 still contains hardcoded DPDR project prefix.'
Assert-True (-not ($createCodebasePs1Text -match 'ProjectName\s*=\s*"DocPilot Desktop Recorder"')) 'create_codebase.ps1 still contains hardcoded DocPilot project name.'
Assert-True (((Get-Content $createCodebasePs1).Count) -lt 600) 'create_codebase.ps1 still exceeds the soft file-size limit of 600 lines.'
Assert-True (-not ($createCodebaseBatLines | Where-Object { $_.Trim().ToLowerInvariant() -eq 'pause' })) 'create_codebase.bat still has unconditional pause behavior.'
Assert-True (-not ($dockerlogsBatText -match 'collect_docker_logs\.py')) 'dockerlogs.bat still depends on the Python collector as the primary path.'
Assert-True ($dbbackupBatText -match 'dbbackup_full\.ps1') 'dbbackup_full.bat is not a thin launcher to dbbackup_full.ps1.'
Assert-True (-not ($dbbackupBatText -match '%~dp0\.dbbackup')) 'dbbackup_full.bat still targets scripts\.dbbackup instead of repo-root .dbbackup.'

$dbbackupPs1Text = if (Test-Path $dbbackupPs1) { Get-FileText $dbbackupPs1 } else { '' }
Assert-True ($dbbackupPs1Text -match 'mysql') 'dbbackup_full.ps1 does not mention mysql support.'
Assert-True ($dbbackupPs1Text -match 'mariadb') 'dbbackup_full.ps1 does not mention mariadb support.'
Assert-True ($dbbackupPs1Text -match 'postgres') 'dbbackup_full.ps1 does not mention postgres support.'
Assert-True ($dbbackupPs1Text -match 'sqlite') 'dbbackup_full.ps1 does not mention sqlite support.'
Assert-True ($dbbackupPs1Text -match '\.meta\.json') 'dbbackup_full.ps1 does not produce metadata artifacts.'
Assert-True (($dbbackupPs1Text -match '\.sha256') -or ($dbbackupPs1Text -match 'Write-Sha256File')) 'dbbackup_full.ps1 does not produce sha256 artifacts.'

if ($failures.Count -gt 0) {
    Write-Host 'Template backup standardization smoke test FAILED:' -ForegroundColor Red
    foreach ($failure in $failures) {
        Write-Host " - $failure" -ForegroundColor Red
    }
    exit 1
}

Write-Host 'Template backup standardization smoke test passed.' -ForegroundColor Green
