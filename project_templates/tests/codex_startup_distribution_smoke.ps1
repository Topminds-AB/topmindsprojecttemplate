[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Assert-SkillBundle {
    param(
        [string]$Root,
        [string]$Name,
        [string[]]$RequiredFiles
    )

    $skillRoot = Join-Path $Root $Name
    $entrypoint = Join-Path $skillRoot "SKILL.md"
    Assert-True (Test-Path -LiteralPath $entrypoint) "Missing skill entrypoint: $entrypoint"

    $content = Get-Content -LiteralPath $entrypoint -Raw
    Assert-True $content.StartsWith("---") "$entrypoint is missing YAML frontmatter."
    Assert-True ($content -match "(?m)^name:\s*$([regex]::Escape($Name))\s*$") "$entrypoint has an invalid name."
    Assert-True ($content -match "(?m)^description:\s*(?:\S|[>|])") "$entrypoint is missing a description."

    foreach ($relativePath in $RequiredFiles) {
        $path = Join-Path $skillRoot $relativePath
        Assert-True (Test-Path -LiteralPath $path) "Incomplete $Name bundle; missing $path"
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$config = Get-Content -LiteralPath (Join-Path $repoRoot ".codex\config.toml") -Raw
Assert-True ($config -notmatch "(?m)^\s*codex_hooks\s*=") "Deprecated features.codex_hooks remains in the template."
Assert-True ($config -match "(?m)^\s*hooks\s*=\s*false\s*$") "Template must preserve disabled hooks with features.hooks = false."

$repoDocsFiles = @(
    "scripts\config_check.py",
    "scripts\scan_repo.py",
    "scripts\capture.py",
    "references\discovery.md",
    "references\capture-playwright.md",
    "templates\feature.md"
)
$domainFiles = @(
    "scripts\configure_domain.py",
    "scripts\verify_domain.py",
    "scripts\cloudflare_api.py",
    "references\architecture.md",
    "references\verification.md",
    "templates\traefik-router.yml.j2"
)

$agentsRoot = Join-Path $repoRoot ".agents\skills"
$claudeRoot = Join-Path $repoRoot ".claude\skills"
Assert-SkillBundle -Root $agentsRoot -Name "repo-user-documentation" -RequiredFiles $repoDocsFiles
Assert-SkillBundle -Root $agentsRoot -Name "system-docs-domain" -RequiredFiles $domainFiles
Assert-SkillBundle -Root $claudeRoot -Name "repo-user-documentation" -RequiredFiles $repoDocsFiles
Assert-SkillBundle -Root $claudeRoot -Name "system-docs-domain" -RequiredFiles $domainFiles

$agentFiles = Get-ChildItem -LiteralPath $agentsRoot -Recurse -File |
    Where-Object { $_.FullName -match "[\\/](repo-user-documentation|system-docs-domain)[\\/]" }
foreach ($file in $agentFiles) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    Assert-True ($content -notmatch "(?i)\.claude[/\\]skills[/\\](repo-user-documentation|system-docs-domain)") "Codex bundle contains a Claude-only path: $($file.FullName)"
}

Write-Host "Codex startup distribution smoke test passed."
