#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$SkipNulCleanup,
    [switch]$SkipDb,
    [switch]$SkipDocker,
    [switch]$SkipSecretsScan
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'scripts\create_codebase_lib.ps1')

Invoke-CreateCodebase `
    -RepoRoot $PSScriptRoot `
    -ScriptRoot (Join-Path $PSScriptRoot 'scripts') `
    -SkipNulCleanup:$SkipNulCleanup `
    -SkipDb:$SkipDb `
    -SkipDocker:$SkipDocker `
    -SkipSecretsScan:$SkipSecretsScan | Out-Null
