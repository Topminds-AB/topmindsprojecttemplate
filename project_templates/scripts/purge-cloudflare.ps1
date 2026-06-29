<#
  purge-cloudflare.ps1 - Purge Cloudflare cache for the current repo/site.

  WHY: HTML behind Cloudflare can stay stale after a deploy even when asset URLs
  are cache-busted. Run this when a repo needs a selective or full cache purge.

  USAGE (PowerShell):
    .\scripts\purge-cloudflare.ps1 -Everything
    .\scripts\purge-cloudflare.ps1 -Url 'https://example.com/'
    .\scripts\purge-cloudflare.ps1 -Url 'https://example.com/about/' -Url 'https://example.com/'
    .\scripts\purge-cloudflare.ps1 -Everything -RepoRoot 'E:\projects\some-repo'
    .\scripts\purge-cloudflare.ps1 -Everything -UseReserveToken

  READS (never printed), in order:
    1. Explicit flags such as -ApiToken, -ZoneId, -Domain, -EnvFile
    2. Repo .env (default: <repo>/.env, then <repo>/infra/.env)
    3. Process environment variables
    4. Reserve token file only when -UseReserveToken is passed
#>
[CmdletBinding()]
param(
  [Alias('Urls')]
  [string[]]$Url,
  [string]$EnvFile,
  [string]$RepoRoot,
  [string]$Domain,
  [Alias('Zone')]
  [string]$ZoneId,
  [string]$ApiToken,
  [switch]$Everything,
  [switch]$UseReserveToken,
  [string]$ReserveTokenFile
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

. (Join-Path $PSScriptRoot 'template_runtime.ps1')

if ($Everything -and $Url) {
  throw 'Choose either -Everything or -Url. Do not pass both.'
}

if (-not $Everything -and (-not $Url -or $Url.Count -eq 0)) {
  throw 'Pass -Everything or at least one -Url.'
}

function Get-DomainFromUrlValue {
  param([string]$Value)

  if (-not $Value) {
    return $null
  }

  try {
    return ([Uri]$Value).Host
  } catch {
    return $Value.Trim().Trim('/')
  }
}

function Get-DefaultReserveTokenFile {
  param([hashtable]$FileValues)

  if ($ReserveTokenFile) {
    return $ReserveTokenFile
  }

  $vaultPath = Get-ConfigValue -ExplicitValue $null -FileValues $FileValues -Names @('OBSIDIAN_VAULT_PATH')
  if (-not $vaultPath) {
    return $null
  }

  return Join-Path $vaultPath '_keys\Cloudflare.md'
}

$resolvedRepoRoot = if ($RepoRoot) {
  (Resolve-Path -LiteralPath $RepoRoot).Path
} else {
  Get-TemplateRepoRoot -StartPath (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$resolvedEnvFile = Get-PreferredEnvFile -RepoRoot $resolvedRepoRoot -ScriptRoot $PSScriptRoot -ExplicitEnvFile $EnvFile
$envVars = Read-KeyValueFile -Path $resolvedEnvFile

$token = Get-ConfigValue -ExplicitValue $ApiToken -FileValues $envVars -Names @('CLOUDFLARE_API_TOKEN', 'CF_API_TOKEN', 'CLOUDFLARE_TOKEN')
if (-not $token -and $UseReserveToken) {
  $ReserveTokenFile = Get-DefaultReserveTokenFile -FileValues $envVars
  $reserveVars = Read-KeyValueFile -Path $ReserveTokenFile
  $token = Get-ConfigValue -ExplicitValue $null -FileValues $reserveVars -Names @('CLOUDFLARE_API_TOKEN', 'CF_API_TOKEN', 'CLOUDFLARE_TOKEN')
}

$domain = Get-ConfigValue -ExplicitValue $Domain -FileValues $envVars -Names @('SITE_DOMAIN')
if (-not $domain) {
  foreach ($urlKey in @('SITE_URL', 'BASE_URL', 'PUBLIC_BASE_URL')) {
    $domain = Get-DomainFromUrlValue -Value (Get-ConfigValue -ExplicitValue $null -FileValues $envVars -Names @($urlKey))
    if ($domain) { break }
  }
}
$zone = Get-ConfigValue -ExplicitValue $ZoneId -FileValues $envVars -Names @('CLOUDFLARE_ZONE_ID', 'CF_ZONE_ID', 'ZONE_ID')

if (-not $domain) {
  throw 'No domain found. Set SITE_DOMAIN in .env or pass -Domain.'
}

if (-not $token) {
  throw 'No Cloudflare API token found. Set CLOUDFLARE_API_TOKEN in repo .env, pass -ApiToken, or use -UseReserveToken.'
}

$headers = @{ 'Authorization' = "Bearer $token"; 'Content-Type' = 'application/json' }
$api = 'https://api.cloudflare.com/client/v4'

if (-not $zone) {
  $lookup = Invoke-RestMethod -Method Get -Uri "$api/zones?name=$domain" -Headers $headers
  if (-not $lookup.success -or $lookup.result.Count -lt 1) {
    throw "Could not resolve zone id for domain '$domain'. Set CLOUDFLARE_ZONE_ID explicitly."
  }
  $zone = $lookup.result[0].id
  Write-Host "Resolved zone '$domain' -> $zone"
}

if ($Url -and $Url.Count -gt 0) {
  foreach ($entry in $Url) {
    [void][Uri]$entry
  }
  $body = @{ files = $Url } | ConvertTo-Json -Depth 4
  Write-Host ('Purging {0} URL(s) on zone {1} ({2}) ...' -f $Url.Count, $zone, $domain)
} else {
  $body = '{"purge_everything":true}'
  Write-Host "Purging EVERYTHING on zone $zone ($domain) ..."
}

$response = Invoke-RestMethod -Method Post -Uri "$api/zones/$zone/purge_cache" -Headers $headers -Body $body
if ($response.success) {
  Write-Host 'Cloudflare cache purge OK.' -ForegroundColor Green
} else {
  Write-Host 'Cloudflare cache purge FAILED:' -ForegroundColor Red
  $response.errors | ForEach-Object { Write-Host ('  [{0}] {1}' -f $_.code, $_.message) }
  exit 1
}
