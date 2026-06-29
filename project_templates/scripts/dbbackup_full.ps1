#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$EnvFile,
    [string]$Profile,
    [string]$OutputDirectory,
    [int]$RetentionDays = 10,
    [switch]$SkipIfUnconfigured,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'template_runtime.ps1')

function Write-Info {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message
    }
}

function Parse-DbUrl {
    param([string]$Url)

    if (-not $Url) {
        return $null
    }

    try {
        $uri = [Uri]$Url
    } catch {
        return $null
    }

    $engine = $uri.Scheme.ToLowerInvariant()
    if ($engine -eq 'pgsql') {
        $engine = 'postgres'
    }

    $dbName = $uri.AbsolutePath.Trim('/')
    $userInfo = $uri.UserInfo
    $user = $null
    $password = $null
    if ($userInfo) {
        $parts = $userInfo.Split(':', 2)
        $user = [Uri]::UnescapeDataString($parts[0])
        if ($parts.Count -gt 1) {
            $password = [Uri]::UnescapeDataString($parts[1])
        }
    }

    [pscustomobject]@{
        Engine   = $engine
        Host     = $uri.Host
        Port     = if ($uri.IsDefaultPort) { $null } else { $uri.Port.ToString() }
        Name     = [Uri]::UnescapeDataString($dbName)
        User     = $user
        Password = $password
        Url      = $Url
    }
}

function New-DbCandidate {
    param(
        [string]$Engine,
        [string]$Name,
        [string]$HostName,
        [string]$Port,
        [string]$User,
        [string]$Password,
        [string]$Url,
        [string]$Path,
        [string]$Source,
        [string]$ProfileName
    )

    if ($Engine -eq 'pgsql') {
        $Engine = 'postgres'
    }

    [pscustomobject]@{
        Engine      = if ($Engine) { $Engine.ToLowerInvariant() } else { $null }
        Name        = $Name
        Host        = $HostName
        Port        = $Port
        User        = $User
        Password    = $Password
        Url         = $Url
        Path        = $Path
        Source      = $Source
        ProfileName = $ProfileName
    }
}

function Test-ViableCandidate {
    param([object]$Candidate)

    if ($null -eq $Candidate) {
        return $false
    }

    switch ($Candidate.Engine) {
        'mysql' { return ($Candidate.Url -or ($Candidate.Name -and ($Candidate.Host -or $Candidate.Path) -and $Candidate.User)) }
        'mariadb' { return ($Candidate.Url -or ($Candidate.Name -and ($Candidate.Host -or $Candidate.Path) -and $Candidate.User)) }
        'postgres' { return ($Candidate.Url -or ($Candidate.Name -and ($Candidate.Host -or $Candidate.Path) -and $Candidate.User)) }
        'sqlite' { return -not [string]::IsNullOrWhiteSpace($Candidate.Path) }
        default { return $false }
    }
}

function Get-PrimaryCandidate {
    param([hashtable]$EnvValues)

    $url = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.Url -ExplicitValue $null
    $engine = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.Engine -ExplicitValue $null
    $dbHost = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.Host -ExplicitValue $null
    $port = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.Port -ExplicitValue $null
    $name = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.Name -ExplicitValue $null
    $user = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.User -ExplicitValue $null
    $password = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.Password -ExplicitValue $null
    $path = Get-ConfigValue -FileValues $EnvValues -Names $script:TemplateDbAliasMap.Path -ExplicitValue $null

    if ($url) {
        $parsed = Parse-DbUrl -Url $url
        if ($parsed) {
            if (-not $engine) { $engine = $parsed.Engine }
            if (-not $dbHost) { $dbHost = $parsed.Host }
            if (-not $port) { $port = $parsed.Port }
            if (-not $name) { $name = $parsed.Name }
            if (-not $user) { $user = $parsed.User }
            if (-not $password) { $password = $parsed.Password }
        }
    }

    return New-DbCandidate -Engine $engine -Name $name -HostName $dbHost -Port $port -User $user -Password $password -Url $url -Path $path -Source 'primary' -ProfileName $null
}

function Get-ProfileCandidate {
    param(
        [hashtable]$EnvValues,
        [string]$ProfileName
    )

    if (-not $ProfileName) {
        return $null
    }

    $normalized = ($ProfileName -replace '[^A-Za-z0-9]+', '_').ToUpperInvariant()
    $prefix = "DB_BACKUP_${normalized}_"
    $url = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}URL") -ExplicitValue $null
    $engine = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}ENGINE") -ExplicitValue $null
    $dbHost = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}HOST") -ExplicitValue $null
    $port = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}PORT") -ExplicitValue $null
    $name = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}NAME", "${prefix}DATABASE") -ExplicitValue $null
    $user = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}USER", "${prefix}USERNAME") -ExplicitValue $null
    $password = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}PASSWORD", "${prefix}PASS") -ExplicitValue $null
    $path = Get-ConfigValue -FileValues $EnvValues -Names @("${prefix}PATH") -ExplicitValue $null

    if ($url) {
        $parsed = Parse-DbUrl -Url $url
        if ($parsed) {
            if (-not $engine) { $engine = $parsed.Engine }
            if (-not $dbHost) { $dbHost = $parsed.Host }
            if (-not $port) { $port = $parsed.Port }
            if (-not $name) { $name = $parsed.Name }
            if (-not $user) { $user = $parsed.User }
            if (-not $password) { $password = $parsed.Password }
        }
    }

    return New-DbCandidate -Engine $engine -Name $name -HostName $dbHost -Port $port -User $user -Password $password -Url $url -Path $path -Source 'profile' -ProfileName $ProfileName
}

function Get-LocalCandidates {
    param([hashtable]$EnvValues)

    $candidates = New-Object System.Collections.Generic.List[object]

    $mysqlUrl = Get-ConfigValue -FileValues $EnvValues -Names @('MYSQL_URL') -ExplicitValue $null
    $mysql = New-DbCandidate `
        -Engine 'mysql' `
        -Name (Get-ConfigValue -FileValues $EnvValues -Names @('MYSQL_DATABASE', 'MYSQL_DB') -ExplicitValue $null) `
        -HostName (Get-ConfigValue -FileValues $EnvValues -Names @('MYSQL_HOST') -ExplicitValue $null) `
        -Port (Get-ConfigValue -FileValues $EnvValues -Names @('MYSQL_PORT', 'MYSQL_HOST_PORT') -ExplicitValue $null) `
        -User (Get-ConfigValue -FileValues $EnvValues -Names @('MYSQL_USER') -ExplicitValue $null) `
        -Password (Get-ConfigValue -FileValues $EnvValues -Names @('MYSQL_PASSWORD', 'MYSQL_ROOT_PASSWORD') -ExplicitValue $null) `
        -Url $mysqlUrl `
        -Path $null `
        -Source 'mysql-local' `
        -ProfileName $null
    if ($mysqlUrl) {
        $parsed = Parse-DbUrl -Url $mysqlUrl
        if ($parsed) {
            $mysql.Host = if ($mysql.Host) { $mysql.Host } else { $parsed.Host }
            $mysql.Port = if ($mysql.Port) { $mysql.Port } else { $parsed.Port }
            $mysql.Name = if ($mysql.Name) { $mysql.Name } else { $parsed.Name }
            $mysql.User = if ($mysql.User) { $mysql.User } else { $parsed.User }
            $mysql.Password = if ($mysql.Password) { $mysql.Password } else { $parsed.Password }
        }
    }
    if (Test-ViableCandidate -Candidate $mysql) { $candidates.Add($mysql) }

    $pgUrl = Get-ConfigValue -FileValues $EnvValues -Names @('POSTGRES_URL') -ExplicitValue $null
    $postgres = New-DbCandidate `
        -Engine 'postgres' `
        -Name (Get-ConfigValue -FileValues $EnvValues -Names @('POSTGRES_DB') -ExplicitValue $null) `
        -HostName (Get-ConfigValue -FileValues $EnvValues -Names @('POSTGRES_HOST') -ExplicitValue $null) `
        -Port (Get-ConfigValue -FileValues $EnvValues -Names @('POSTGRES_PORT', 'POSTGRES_HOST_PORT') -ExplicitValue $null) `
        -User (Get-ConfigValue -FileValues $EnvValues -Names @('POSTGRES_USER') -ExplicitValue $null) `
        -Password (Get-ConfigValue -FileValues $EnvValues -Names @('POSTGRES_PASSWORD') -ExplicitValue $null) `
        -Url $pgUrl `
        -Path $null `
        -Source 'postgres-local' `
        -ProfileName $null
    if ($pgUrl) {
        $parsed = Parse-DbUrl -Url $pgUrl
        if ($parsed) {
            $postgres.Host = if ($postgres.Host) { $postgres.Host } else { $parsed.Host }
            $postgres.Port = if ($postgres.Port) { $postgres.Port } else { $parsed.Port }
            $postgres.Name = if ($postgres.Name) { $postgres.Name } else { $parsed.Name }
            $postgres.User = if ($postgres.User) { $postgres.User } else { $parsed.User }
            $postgres.Password = if ($postgres.Password) { $postgres.Password } else { $parsed.Password }
        }
    }
    if (Test-ViableCandidate -Candidate $postgres) { $candidates.Add($postgres) }

    return $candidates
}

function Resolve-DbCandidate {
    param(
        [hashtable]$EnvValues,
        [string]$RepoRoot,
        [string]$ExplicitProfile
    )

    $candidates = New-Object System.Collections.Generic.List[object]

    $envProfile = Get-ConfigValue -FileValues $EnvValues -Names @('DB_BACKUP_PROFILE') -ExplicitValue $null
    $profileToUse = if ($ExplicitProfile) { $ExplicitProfile } else { $envProfile }
    if ($profileToUse) {
        $profileCandidate = Get-ProfileCandidate -EnvValues $EnvValues -ProfileName $profileToUse
        if (Test-ViableCandidate -Candidate $profileCandidate) {
            return $profileCandidate
        }
        throw "DB backup profile '$profileToUse' is set but incomplete. Define DB_BACKUP_${($profileToUse -replace '[^A-Za-z0-9]+', '_').ToUpperInvariant()}_* keys."
    }

    $primary = Get-PrimaryCandidate -EnvValues $EnvValues
    if (Test-ViableCandidate -Candidate $primary) {
        $candidates.Add($primary)
    }

    foreach ($candidate in Get-LocalCandidates -EnvValues $EnvValues) {
        $duplicate = $candidates | Where-Object {
            $_.Engine -eq $candidate.Engine -and $_.Name -eq $candidate.Name -and $_.Host -eq $candidate.Host -and $_.Port -eq $candidate.Port
        }
        if (-not $duplicate) {
            $candidates.Add($candidate)
        }
    }

    if ($primary.Engine -eq 'sqlite' -and -not [string]::IsNullOrWhiteSpace($primary.Path)) {
        return $primary
    }

    if ($candidates.Count -eq 1) {
        return $candidates[0]
    }

    if ($candidates.Count -gt 1 -and (Test-ViableCandidate -Candidate $primary) -and -not [string]::IsNullOrWhiteSpace($primary.Engine)) {
        return $primary
    }

    if ($candidates.Count -gt 1) {
        $summary = $candidates | ForEach-Object {
            "{0}:{1}@{2}:{3} ({4})" -f $_.Engine, $_.Name, $_.Host, $_.Port, $_.Source
        }
        throw "Multiple viable database targets were found: $($summary -join ', '). Set DB_BACKUP_PROFILE explicitly instead of letting the script guess."
    }

    return $null
}

function Get-BackupOutputBaseName {
    param(
        [object]$Identity,
        [object]$Candidate
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
    $dbName = if ($Candidate.Engine -eq 'sqlite') {
        if ($Candidate.Name) { $Candidate.Name } else { [System.IO.Path]::GetFileNameWithoutExtension($Candidate.Path) }
    } else {
        $Candidate.Name
    }

    return '{0}_{1}_{2}_{3}' -f $Identity.RepoSlug, $Candidate.Engine, (ConvertTo-RepoSlug -Value $dbName), $timestamp
}

function Invoke-MySqlDump {
    param(
        [object]$Candidate,
        [string]$RepoRoot,
        [string]$DumpPath
    )

    $commonPaths = @(
        'C:\xampp\mysql\bin\mysqldump.exe',
        'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe',
        'C:\Program Files\MariaDB 10.6\bin\mysqldump.exe',
        'C:\Program Files\MariaDB 11.4\bin\mariadb-dump.exe'
    )
    $dumpExe = Get-NativeCommandPath -Names @('mysqldump', 'mariadb-dump') -CommonPaths $commonPaths
    $composeHint = Get-ComposeServiceForEngine -RepoRoot $RepoRoot -Engine $Candidate.Engine -PreferredService $Candidate.Host
    $preferCompose = ($composeHint -and ($Candidate.Host -eq $composeHint.Name -or $Candidate.Source -like '*local'))

    $attemptedDirect = $false
    if ($dumpExe -and -not $preferCompose) {
        $attemptedDirect = $true
        $args = @(
            "--host=$($Candidate.Host)",
            "--port=$($Candidate.Port)",
            "--user=$($Candidate.User)",
            "--password=$($Candidate.Password)",
            '--databases', $Candidate.Name,
            '--single-transaction',
            '--quick',
            '--routines',
            '--triggers',
            '--events',
            '--hex-blob',
            '--set-gtid-purged=OFF',
            '--default-character-set=utf8mb4',
            '--skip-comments'
        )
        $result = Invoke-HiddenProcess -FileName $dumpExe -Arguments $args -WorkingDirectory $RepoRoot -StdOutPath $DumpPath
        if ($result.ExitCode -eq 0 -and (Test-Path -LiteralPath $DumpPath) -and (Get-Item $DumpPath).Length -gt 0) {
            return [pscustomobject]@{ UsedCompose = $false; Command = $result.Command }
        }
    }

    if ($composeHint) {
        $dockerResult = Invoke-HiddenProcess -FileName 'docker' -Arguments @(
            'compose',
            '-f', $composeHint.ComposeFile,
            'exec', '-T',
            '-e', "MYSQL_PWD=$($Candidate.Password)",
            $composeHint.Name,
            'mysqldump',
            '--user', $Candidate.User,
            '--databases', $Candidate.Name,
            '--single-transaction',
            '--quick',
            '--routines',
            '--triggers',
            '--events',
            '--hex-blob',
            '--set-gtid-purged=OFF',
            '--default-character-set=utf8mb4',
            '--skip-comments'
        ) -WorkingDirectory $RepoRoot -StdOutPath $DumpPath
        if ($dockerResult.ExitCode -eq 0 -and (Test-Path -LiteralPath $DumpPath) -and (Get-Item $DumpPath).Length -gt 0) {
            return [pscustomobject]@{ UsedCompose = $true; Command = $dockerResult.Command }
        }
        throw "MySQL dump failed. Direct client attempted=$attemptedDirect. Docker stderr: $($dockerResult.StdErr.Trim())"
    }

    throw "MySQL dump failed. No working direct client/compose fallback was available."
}

function Invoke-PostgresDump {
    param(
        [object]$Candidate,
        [string]$RepoRoot,
        [string]$DumpPath
    )

    $commonPaths = @(
        'C:\Program Files\PostgreSQL\17\bin\pg_dump.exe',
        'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe',
        'C:\Program Files\PostgreSQL\15\bin\pg_dump.exe'
    )
    $dumpExe = Get-NativeCommandPath -Names @('pg_dump') -CommonPaths $commonPaths
    $composeHint = Get-ComposeServiceForEngine -RepoRoot $RepoRoot -Engine 'postgres' -PreferredService $Candidate.Host
    $preferCompose = ($composeHint -and ($Candidate.Host -eq $composeHint.Name -or $Candidate.Source -like '*local'))

    $attemptedDirect = $false
    if ($dumpExe -and -not $preferCompose) {
        $attemptedDirect = $true
        $args = @(
            '--host', $Candidate.Host,
            '--port', $Candidate.Port,
            '--username', $Candidate.User,
            '--dbname', $Candidate.Name,
            '--format=plain',
            '--encoding=UTF8',
            '--no-owner',
            '--no-privileges',
            '--clean',
            '--if-exists'
        )
        $result = Invoke-HiddenProcess -FileName $dumpExe -Arguments $args -WorkingDirectory $RepoRoot -Environment @{ PGPASSWORD = $Candidate.Password } -StdOutPath $DumpPath
        if ($result.ExitCode -eq 0 -and (Test-Path -LiteralPath $DumpPath) -and (Get-Item $DumpPath).Length -gt 0) {
            return [pscustomobject]@{ UsedCompose = $false; Command = $result.Command }
        }
    }

    if ($composeHint) {
        $dockerResult = Invoke-HiddenProcess -FileName 'docker' -Arguments @(
            'compose',
            '-f', $composeHint.ComposeFile,
            'exec', '-T',
            '-e', "PGPASSWORD=$($Candidate.Password)",
            $composeHint.Name,
            'pg_dump',
            '-U', $Candidate.User,
            '-d', $Candidate.Name,
            '--format=plain',
            '--encoding=UTF8',
            '--no-owner',
            '--no-privileges',
            '--clean',
            '--if-exists'
        ) -WorkingDirectory $RepoRoot -StdOutPath $DumpPath
        if ($dockerResult.ExitCode -eq 0 -and (Test-Path -LiteralPath $DumpPath) -and (Get-Item $DumpPath).Length -gt 0) {
            return [pscustomobject]@{ UsedCompose = $true; Command = $dockerResult.Command }
        }
        throw "Postgres dump failed. Direct client attempted=$attemptedDirect. Docker stderr: $($dockerResult.StdErr.Trim())"
    }

    throw "Postgres dump failed. No working direct client/compose fallback was available."
}

$repoRoot = Get-TemplateRepoRoot -StartPath (Split-Path -Parent $MyInvocation.MyCommand.Path)
$envFilePath = Get-PreferredEnvFile -RepoRoot $repoRoot -ScriptRoot $PSScriptRoot -ExplicitEnvFile $EnvFile
$envValues = Read-KeyValueFile -Path $envFilePath
$identity = Get-ProjectIdentity -RepoRoot $repoRoot -EnvValues $envValues
$outputRoot = if ($OutputDirectory) { $OutputDirectory } else { (Join-Path $repoRoot '.dbbackup') }
if (-not [System.IO.Path]::IsPathRooted($outputRoot)) {
    $outputRoot = Join-Path $repoRoot $outputRoot
}
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null

$candidate = Resolve-DbCandidate -EnvValues $envValues -RepoRoot $repoRoot -ExplicitProfile $Profile
if ($null -eq $candidate) {
    if ($SkipIfUnconfigured) {
        Write-Info 'No database configuration found. Skipping db backup.'
        [pscustomobject]@{
            Status  = 'skipped'
            Reason  = 'not-configured'
            Repo    = $identity.RepoName
            EnvFile = $envFilePath
        }
        exit 0
    }

    throw 'No viable database configuration was found. Set DB_ENGINE plus DB_URL or DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD, or define DB_BACKUP_PROFILE.'
}

if ($candidate.Engine -eq 'sqlite') {
    $path = $candidate.Path
    if (-not [System.IO.Path]::IsPathRooted($path)) {
        $path = Join-Path $repoRoot $path
    }
    if (-not (Test-Path -LiteralPath $path)) {
        throw "SQLite database file not found: $path"
    }

    $baseName = Get-BackupOutputBaseName -Identity $identity -Candidate $candidate
    $targetPath = Join-Path $outputRoot ($baseName + '.sqlite')
    Copy-Item -LiteralPath $path -Destination $targetPath -Force
    foreach ($suffix in @('-wal', '-shm')) {
        $sidecar = $path + $suffix
        if (Test-Path -LiteralPath $sidecar) {
            Copy-Item -LiteralPath $sidecar -Destination ($targetPath + $suffix) -Force
        }
    }

    $shaPath = Write-Sha256File -Path $targetPath
    $metaPath = $targetPath + '.meta.json'
    $logPath = $targetPath + '.log'
    $meta = [pscustomobject]@{
        created_at = (Get-Date).ToString('o')
        repo = $identity.RepoName
        engine = 'sqlite'
        source = $candidate.Source
        profile = $candidate.ProfileName
        output_file = $targetPath
        sha256_file = $shaPath
        env_file = $envFilePath
        retention_days = $RetentionDays
    }
    Write-JsonUtf8 -Path $metaPath -Value $meta
    Set-Content -LiteralPath $logPath -Encoding UTF8 -Value @(
        "status=success",
        "engine=sqlite",
        "repo=$($identity.RepoName)",
        "output=$targetPath",
        "env_file=$envFilePath"
    )

    $removed = Remove-ExpiredBackupArtifacts -Directory $outputRoot -RetentionDays $RetentionDays
    Write-Info "SQLite backup created: $targetPath"
    [pscustomobject]@{
        Status = 'success'
        Engine = 'sqlite'
        Output = $targetPath
        Removed = $removed
    }
    exit 0
}

if (-not $candidate.Port) {
    $candidate.Port = if ($candidate.Engine -eq 'postgres') { '5432' } else { '3306' }
}

$baseName = Get-BackupOutputBaseName -Identity $identity -Candidate $candidate
$targetDump = Join-Path $outputRoot ($baseName + '.sql')
$commandResult = switch ($candidate.Engine) {
    'mysql' { Invoke-MySqlDump -Candidate $candidate -RepoRoot $repoRoot -DumpPath $targetDump }
    'mariadb' { Invoke-MySqlDump -Candidate $candidate -RepoRoot $repoRoot -DumpPath $targetDump }
    'postgres' { Invoke-PostgresDump -Candidate $candidate -RepoRoot $repoRoot -DumpPath $targetDump }
    default { throw "Unsupported DB engine: $($candidate.Engine)" }
}

if (-not (Test-Path -LiteralPath $targetDump)) {
    throw "Database dump was not created: $targetDump"
}

$shaPath = Write-Sha256File -Path $targetDump
$metaPath = $targetDump + '.meta.json'
$logPath = $targetDump + '.log'
$meta = [pscustomobject]@{
    created_at = (Get-Date).ToString('o')
    repo = $identity.RepoName
    engine = $candidate.Engine
    db_name = $candidate.Name
    host = $candidate.Host
    port = $candidate.Port
    source = $candidate.Source
    profile = $candidate.ProfileName
    output_file = $targetDump
    sha256_file = $shaPath
    env_file = $envFilePath
    used_compose_fallback = $commandResult.UsedCompose
    command = $commandResult.Command
    retention_days = $RetentionDays
}
Write-JsonUtf8 -Path $metaPath -Value $meta
Set-Content -LiteralPath $logPath -Encoding UTF8 -Value @(
    "status=success",
    "engine=$($candidate.Engine)",
    "repo=$($identity.RepoName)",
    "db_name=$($candidate.Name)",
    "output=$targetDump",
    "env_file=$envFilePath",
    "used_compose_fallback=$($commandResult.UsedCompose)"
)

$removed = Remove-ExpiredBackupArtifacts -Directory $outputRoot -RetentionDays $RetentionDays
Write-Info "Database backup created: $targetDump"
[pscustomobject]@{
    Status = 'success'
    Engine = $candidate.Engine
    Output = $targetDump
    UsedComposeFallback = $commandResult.UsedCompose
    Removed = $removed
}
