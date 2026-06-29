#Requires -Version 5.1

Set-StrictMode -Version Latest

$script:TemplateDbAliasMap = @{
    Engine   = @('DB_ENGINE', 'DB_CONNECTION')
    Url      = @('DB_URL', 'DATABASE_URL', 'DATABASE_URL_SYNC')
    Host     = @('DB_HOST', 'POSTGRES_HOST', 'MYSQL_HOST', 'DBHOST', 'MARIADBHOST', 'PROD_DB_HOST', 'MOBILE_DB_HOST', 'DOCPILOT_DB_HOST')
    Port     = @('DB_PORT', 'POSTGRES_PORT', 'MYSQL_PORT', 'POSTGRES_HOST_PORT', 'MYSQL_HOST_PORT')
    Name     = @('DB_NAME', 'DB_DATABASE', 'POSTGRES_DB', 'MYSQL_DATABASE', 'MYSQL_DB', 'MARIADBDB')
    User     = @('DB_USER', 'DB_USERNAME', 'POSTGRES_USER', 'MYSQL_USER', 'DBUSER', 'MARIADBUSER', 'DB_APP_USER')
    Password = @('DB_PASSWORD', 'DB_PASS', 'POSTGRES_PASSWORD', 'MYSQL_PASSWORD', 'DB_ROOT_PASSWORD', 'DB_ROOT_PASS', 'MARIADBPASSWORD', 'DB_APP_PASSWORD')
    Path     = @('DB_PATH', 'SQLITE_PATH', 'SQLITE_FILE', 'DATABASE_FILE')
}

function Get-TemplateRepoRoot {
    param([string]$StartPath)

    $resolved = (Resolve-Path -LiteralPath $StartPath).Path
    if ((Split-Path -Leaf $resolved) -ieq 'scripts') {
        return (Split-Path -Parent $resolved)
    }

    return $resolved
}

function Get-PreferredEnvFile {
    param(
        [string]$RepoRoot,
        [string]$ScriptRoot,
        [string]$ExplicitEnvFile
    )

    $candidates = @()
    if ($ExplicitEnvFile) {
        if ([System.IO.Path]::IsPathRooted($ExplicitEnvFile)) {
            $candidates += $ExplicitEnvFile
        } else {
            $candidates += (Join-Path $RepoRoot $ExplicitEnvFile)
        }
    }

    $candidates += (Join-Path $RepoRoot '.env')
    $candidates += (Join-Path $RepoRoot 'infra\.env')
    $candidates += (Join-Path $ScriptRoot '.env')

    return $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
}

function Resolve-InterpolatedValue {
    param(
        [string]$Value,
        [hashtable]$Values,
        [System.Collections.Generic.HashSet[string]]$Visited
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $Value
    }

    $resolved = $Value
    $resolved = [regex]::Replace($resolved, '\$\{([A-Za-z_][A-Za-z0-9_]*)\}', {
        param($match)
        $name = $match.Groups[1].Value
        if ($Values.ContainsKey($name)) { return [string]$Values[$name] }
        return $match.Value
    })
    $resolved = [regex]::Replace($resolved, '%([A-Za-z_][A-Za-z0-9_]*)%', {
        param($match)
        $name = $match.Groups[1].Value
        if ($Values.ContainsKey($name)) { return [string]$Values[$name] }
        return $match.Value
    })

    if ($Values.ContainsKey($resolved) -and -not $Visited.Contains($resolved)) {
        $Visited.Add($resolved) | Out-Null
        return Resolve-InterpolatedValue -Value ([string]$Values[$resolved]) -Values $Values -Visited $Visited
    }

    return $resolved
}

function Read-KeyValueFile {
    param([string]$Path)

    $values = @{}
    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) {
        return $values
    }

    foreach ($rawLine in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $line = $rawLine.Trim()
        if (-not $line -or $line.StartsWith('#')) {
            continue
        }

        if ($line.StartsWith('export ')) {
            $line = $line.Substring(7).Trim()
        }

        $index = $line.IndexOf('=')
        if ($index -lt 1) {
            continue
        }

        $key = $line.Substring(0, $index).Trim()
        $value = $line.Substring($index + 1).Trim()
        if ($value.Length -ge 2 -and (
            ($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))
        )) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        $values[$key] = $value
    }

    foreach ($name in @($values.Keys)) {
        $visited = New-Object 'System.Collections.Generic.HashSet[string]'
        $visited.Add($name) | Out-Null
        $values[$name] = Resolve-InterpolatedValue -Value ([string]$values[$name]) -Values $values -Visited $visited
    }

    return $values
}

function Get-ConfigValue {
    param(
        [hashtable]$FileValues,
        [string[]]$Names,
        [string]$ExplicitValue
    )

    if ($ExplicitValue) {
        return $ExplicitValue
    }

    foreach ($name in $Names) {
        if ($FileValues.ContainsKey($name) -and -not [string]::IsNullOrWhiteSpace($FileValues[$name])) {
            return ([string]$FileValues[$name]).Trim()
        }
    }

    foreach ($name in $Names) {
        $value = [Environment]::GetEnvironmentVariable($name, 'Process')
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return $value.Trim()
        }
    }

    return $null
}

function ConvertTo-RepoSlug {
    param(
        [string]$Value,
        [switch]$Uppercase
    )

    $slug = ($Value -replace '[^A-Za-z0-9]+', '_').Trim('_')
    if (-not $slug) {
        $slug = 'project'
    }

    if ($Uppercase) {
        return $slug.ToUpperInvariant()
    }

    return $slug.ToLowerInvariant()
}

function Get-ProjectIdentity {
    param(
        [string]$RepoRoot,
        [hashtable]$EnvValues
    )

    $repoName = Split-Path -Leaf $RepoRoot
    $displayName = Get-ConfigValue -FileValues $EnvValues -Names @('APP_NAME') -ExplicitValue $null
    if (-not $displayName) {
        $displayName = $repoName
    }

    $prefixSource = if ($repoName) { $repoName } else { $displayName }
    $prefix = ConvertTo-RepoSlug -Value $prefixSource -Uppercase
    if ($prefix.Length -gt 24) {
        $prefix = $prefix.Substring(0, 24)
    }

    [pscustomobject]@{
        RepoName    = $repoName
        DisplayName = $displayName
        RepoSlug    = ConvertTo-RepoSlug -Value $displayName
        Prefix      = $prefix
    }
}

function Get-ComposeFiles {
    param([string]$RepoRoot)

    $patterns = @('docker-compose*.yml', 'docker-compose*.yaml', 'compose*.yml', 'compose*.yaml')
    $files = foreach ($pattern in $patterns) {
        Get-ChildItem -LiteralPath $RepoRoot -Filter $pattern -File -ErrorAction SilentlyContinue
    }

    return $files | Sort-Object FullName -Unique
}

function Get-ComposeServiceHints {
    param([string]$ComposeFile)

    $lines = Get-Content -LiteralPath $ComposeFile -Encoding UTF8
    $services = New-Object System.Collections.Generic.List[object]
    $insideServices = $false
    $current = $null

    foreach ($line in $lines) {
        if (-not $insideServices) {
            if ($line -match '^\s*services\s*:\s*$') {
                $insideServices = $true
            }
            continue
        }

        if ($line -match '^\S') {
            break
        }

        if ($line -match '^\s{2}([A-Za-z0-9._-]+)\s*:\s*$') {
            if ($null -ne $current) {
                $services.Add([pscustomobject]$current)
            }
            $current = @{
                Name         = $Matches[1]
                Image        = $null
                Container    = $null
                EngineHint   = $null
                ComposeFile  = $ComposeFile
            }
            continue
        }

        if ($null -eq $current) {
            continue
        }

        if ($line -match '^\s{4}image\s*:\s*(.+?)\s*$') {
            $current.Image = $Matches[1].Trim().Trim('"').Trim("'")
            if ($current.Image -match 'postgres') { $current.EngineHint = 'postgres' }
            elseif ($current.Image -match 'mariadb') { $current.EngineHint = 'mariadb' }
            elseif ($current.Image -match 'mysql') { $current.EngineHint = 'mysql' }
            continue
        }

        if ($line -match '^\s{4}container_name\s*:\s*(.+?)\s*$') {
            $current.Container = $Matches[1].Trim().Trim('"').Trim("'")
        }
    }

    if ($null -ne $current) {
        $services.Add([pscustomobject]$current)
    }

    return $services
}

function Get-ComposeServiceForEngine {
    param(
        [string]$RepoRoot,
        [string]$Engine,
        [string]$PreferredService
    )

    $serviceHints = foreach ($composeFile in Get-ComposeFiles -RepoRoot $RepoRoot) {
        Get-ComposeServiceHints -ComposeFile $composeFile.FullName
    }

    if ($PreferredService) {
        $explicit = $serviceHints | Where-Object { $_.Name -ieq $PreferredService }
        if ($explicit) {
            return $explicit | Select-Object -First 1
        }
    }

    $normalizedEngine = $Engine.ToLowerInvariant()
    $matching = $serviceHints | Where-Object {
        $_.EngineHint -eq $normalizedEngine -or
        ($normalizedEngine -eq 'mariadb' -and $_.EngineHint -eq 'mysql') -or
        ($normalizedEngine -eq 'mysql' -and $_.EngineHint -eq 'mariadb')
    }

    if (($matching | Measure-Object).Count -eq 1) {
        return $matching | Select-Object -First 1
    }

    return $null
}

function Convert-CommandArgument {
    param([string]$Value)

    if ($null -eq $Value) {
        return '""'
    }

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    return '"' + ($Value -replace '"', '\"') + '"'
}

function Join-CommandArguments {
    param([string[]]$Arguments)

    return (($Arguments | ForEach-Object { Convert-CommandArgument -Value $_ }) -join ' ')
}

function Invoke-HiddenProcess {
    param(
        [string]$FileName,
        [string[]]$Arguments = @(),
        [string]$WorkingDirectory,
        [hashtable]$Environment = @{},
        [string]$StdOutPath
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FileName
    $psi.Arguments = Join-CommandArguments -Arguments $Arguments
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    foreach ($entry in $Environment.GetEnumerator()) {
        $psi.EnvironmentVariables[$entry.Key] = [string]$entry.Value
    }

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()

    $stdout = ''
    if ($StdOutPath) {
        $outStream = [System.IO.File]::Open($StdOutPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try {
            $process.StandardOutput.BaseStream.CopyTo($outStream)
        } finally {
            $outStream.Dispose()
        }
    } else {
        $stdout = $process.StandardOutput.ReadToEnd()
    }

    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    [pscustomobject]@{
        ExitCode = $process.ExitCode
        StdOut   = $stdout
        StdErr   = $stderr
        Command  = "$FileName $($psi.Arguments)"
    }
}

function Get-NativeCommandPath {
    param(
        [string[]]$Names,
        [string[]]$CommonPaths = @()
    )

    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    foreach ($path in $CommonPaths) {
        if (Test-Path -LiteralPath $path) {
            return $path
        }
    }

    return $null
}

function Write-JsonUtf8 {
    param(
        [string]$Path,
        [object]$Value
    )

    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 8), $utf8)
}

function Get-Sha256Hex {
    param([string]$Path)

    $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $Path
    return $hash.Hash.ToLowerInvariant()
}

function Write-Sha256File {
    param([string]$Path)

    $hash = Get-Sha256Hex -Path $Path
    $shaPath = "$Path.sha256"
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($shaPath, $hash, $utf8)
    return $shaPath
}

function Remove-ExpiredBackupArtifacts {
    param(
        [string]$Directory,
        [int]$RetentionDays
    )

    if (-not (Test-Path -LiteralPath $Directory)) {
        return @()
    }

    $cutoff = (Get-Date).Date.AddDays(-1 * $RetentionDays)
    $removed = New-Object System.Collections.Generic.List[string]

    foreach ($file in Get-ChildItem -LiteralPath $Directory -File -ErrorAction SilentlyContinue) {
        if ($file.LastWriteTime -lt $cutoff) {
            Remove-Item -LiteralPath $file.FullName -Force -ErrorAction SilentlyContinue
            $removed.Add($file.FullName)
        }
    }

    return $removed
}
