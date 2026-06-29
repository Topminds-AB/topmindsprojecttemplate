#Requires -Version 5.1
[CmdletBinding()]
param(
    [int]$TailLines = 500
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'template_runtime.ps1')

$repoRoot = Get-TemplateRepoRoot -StartPath (Split-Path -Parent $MyInvocation.MyCommand.Path)
$envFile = Get-PreferredEnvFile -RepoRoot $repoRoot -ScriptRoot $PSScriptRoot -ExplicitEnvFile $null
$envValues = Read-KeyValueFile -Path $envFile
$identity = Get-ProjectIdentity -RepoRoot $repoRoot -EnvValues $envValues
$composeFiles = Get-ComposeFiles -RepoRoot $repoRoot
$dockerLogsDir = Join-Path $repoRoot '.dockerlogs'
New-Item -ItemType Directory -Path $dockerLogsDir -Force | Out-Null

if (($composeFiles | Measure-Object).Count -eq 0) {
    $readme = Join-Path $dockerLogsDir 'README.txt'
    Set-Content -LiteralPath $readme -Encoding UTF8 -Value 'No compose files found. Docker log collection skipped.'
    Write-Host 'No compose files found. Docker log collection skipped.'
    exit 0
}

$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$zipPath = Join-Path $dockerLogsDir ("{0}_docker_logs_{1}.zip" -f $identity.RepoSlug, $timestamp)
$workingDir = Join-Path $env:TEMP ("dockerlogs_{0}_{1}" -f $identity.RepoSlug, ([Guid]::NewGuid().ToString('N').Substring(0, 8)))
New-Item -ItemType Directory -Path $workingDir -Force | Out-Null

try {
    $composeFile = $composeFiles | Select-Object -First 1
    $services = Get-ComposeServiceHints -ComposeFile $composeFile.FullName

    $psResult = Invoke-HiddenProcess -FileName 'docker' -Arguments @('compose', '-f', $composeFile.FullName, 'ps') -WorkingDirectory $repoRoot
    [System.IO.File]::WriteAllText((Join-Path $workingDir 'docker_compose_ps.txt'), $psResult.StdOut + $psResult.StdErr)

    $infoResult = Invoke-HiddenProcess -FileName 'docker' -Arguments @('version', '--format', '{{.Server.Version}}') -WorkingDirectory $repoRoot
    [System.IO.File]::WriteAllText((Join-Path $workingDir '_docker_info.txt'), $infoResult.StdOut.Trim())

    foreach ($service in $services) {
        $fileName = Join-Path $workingDir ("{0}.log" -f $service.Name)
        $result = Invoke-HiddenProcess -FileName 'docker' -Arguments @('compose', '-f', $composeFile.FullName, 'logs', '--no-color', "--tail=$TailLines", $service.Name) -WorkingDirectory $repoRoot
        [System.IO.File]::WriteAllText($fileName, $result.StdOut + $result.StdErr)
    }

    Compress-Archive -Path (Join-Path $workingDir '*') -DestinationPath $zipPath -CompressionLevel Optimal -Force
    Write-Host "Docker logs created: $zipPath"
} finally {
    Remove-Item -LiteralPath $workingDir -Recurse -Force -ErrorAction SilentlyContinue
}
