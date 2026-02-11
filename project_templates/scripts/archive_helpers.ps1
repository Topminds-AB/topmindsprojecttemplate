<#
.SYNOPSIS
    Helper functions for codebase archive creation.

.DESCRIPTION
    Contains utility functions used by create_codebase.ps1:
    - Read-EnvFile: Reads .env files
    - Get-Timestamp: Returns formatted timestamps
    - Should-ExcludeItem: Determines exclusion rules
    - Copy-FilteredContent: Copies with exclusions
    - Generate-FileInventory: Creates file inventory
#>

# =============================================================
# SECTION: EXCLUSION PATTERNS
# =============================================================

$EXCLUDE_DIRS = @(
    '.git',
    '.codebasebackup',
    '.dbbackup',
    '.dockerlogs',
    'dbbackup',
    'dockerlogs',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
    '.pytest_cache',
    '.mypy_cache',
    '.next',
    '.cache',
    'tmp',
    'temp',
    'dist',
    'build',
    'out',
    '.idea',
    '.vscode'
)

$EXCLUDE_FILE_PATTERNS = @(
    '.env',
    '.env.local',
    '.env.*.local',
    '*.pyc',
    '*.pyo',
    '*.pem',
    'id_rsa',
    'id_rsa.pub',
    'id_ed25519',
    '*.key',
    'credentials.json',
    'service-account*.json',
    '*.kubeconfig',
    'Thumbs.db',
    'Desktop.ini',
    '.DS_Store'
)

$EXCLUDE_FILES_EXACT = @(
    '.env'
)

# =============================================================
# SECTION: HELPER FUNCTIONS
# =============================================================

function Read-EnvFile {
    <#
    .SYNOPSIS
        Reads a .env file and returns a hashtable of key-value pairs.
    #>
    param([string]$Path)

    $envVars = @{}

    if (-not (Test-Path $Path)) {
        Write-Warning "Environment file not found: $Path"
        return $envVars
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#')) {
            $parts = $line -split '=', 2
            if ($parts.Count -eq 2) {
                $key = $parts[0].Trim()
                $value = $parts[1].Trim()
                $value = $value -replace '^["'']|["'']$', ''
                $envVars[$key] = $value
            }
        }
    }

    return $envVars
}

function Get-ArchiveTimestamp {
    <#
    .SYNOPSIS
        Returns current timestamp for ZIP filename.
        Format: YYYY-MM-DD_HH-mm
    #>
    return Get-Date -Format "yyyy-MM-dd_HH-mm"
}

function Get-FolderTimestamp {
    <#
    .SYNOPSIS
        Returns current timestamp for manifest archive folder.
        Format: YYYY-MM-DD_HH-mm (minutes, not months)
    #>
    return Get-Date -Format "yyyy-MM-dd_HH-mm"
}

function Should-ExcludeItem {
    <#
    .SYNOPSIS
        Determines if an item should be excluded based on exclusion rules.
    #>
    param(
        [System.IO.FileSystemInfo]$Item,
        [string]$RelativePath
    )

    $name = $Item.Name

    if ($Item.PSIsContainer) {
        if ($EXCLUDE_DIRS -contains $name) {
            return $true
        }
    }

    if ($EXCLUDE_FILES_EXACT -contains $name) {
        return $true
    }

    foreach ($pattern in $EXCLUDE_FILE_PATTERNS) {
        if ($name -like $pattern) {
            return $true
        }
    }

    if ($RelativePath -like "test-results/*" -and $name -like "*.zip") {
        return $true
    }

    return $false
}

function Copy-FilteredContent {
    <#
    .SYNOPSIS
        Recursively copies content with exclusion filtering.
    #>
    param(
        [string]$Source,
        [string]$Destination,
        [string]$BasePath
    )

    if (-not (Test-Path $Destination)) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }

    Get-ChildItem -Path $Source -Force | ForEach-Object {
        $item = $_
        $relativePath = $item.FullName.Substring($BasePath.Length).TrimStart('\', '/') -replace '\\', '/'

        if (-not (Should-ExcludeItem -Item $item -RelativePath $relativePath)) {
            $destPath = Join-Path $Destination $item.Name

            if ($item.PSIsContainer) {
                Copy-FilteredContent -Source $item.FullName -Destination $destPath -BasePath $BasePath
            } else {
                Copy-Item -Path $item.FullName -Destination $destPath -Force
            }
        }
    }
}

function Generate-FileInventory {
    <#
    .SYNOPSIS
        Generates file_inventory.txt with all ZIP members and sizes.
    #>
    param(
        [string]$StagingRoot,
        [string]$OutputPath
    )

    $inventory = @()

    Get-ChildItem -Path $StagingRoot -Recurse -File -Force | ForEach-Object {
        $relativePath = $_.FullName.Substring($StagingRoot.Length).TrimStart('\', '/') -replace '\\', '/'
        $size = $_.Length
        $inventory += "$size`t$relativePath"
    }

    $inventory | Sort-Object | Set-Content -Path $OutputPath -Encoding UTF8
}
