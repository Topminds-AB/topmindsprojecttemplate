# create_codebase.md - Configuration & Usage Guide version 1.0.

## Quick Start

1. Double-click `create_codebase.bat`
2. Wait for it to finish
3. Find your ZIP in `.codebasebackup/`

## What It Does

Creates a structured ZIP archive for AO (Agent Orchestrator) review:

```
/code/           Source code (secrets redacted, junk excluded)
/dbbackup/       Database dump (from .env credentials)
/dockerlogs/     Docker container logs
/logs/           Git evidence + application logs
/manifest/       manifest.md, file_inventory.txt, change_summary.md,
                 agent_final_message.md, questions_for_po.md
```

**ZIP naming**: `<PREFIX>_codebase_YYYY-MM-DD_HH-MM.zip`
**Saved to**: `/.codebasebackup/`

## How to Configure for a New Project

Open `create_codebase.ps1` and edit the `$CONFIG` block at the top.

### 1. Project Identity

```powershell
ProjectPrefix = "MYPROJ"           # Used in ZIP filename
ProjectName   = "My Project Name"  # Shown in manifest
```

### 2. Database Configuration

**No database** (default):
```powershell
Database = $null
```

**MySQL via Docker** (container runs mysqldump internally):
```powershell
Database = @{
    Type          = "mysql-docker"
    ContainerName = "myproject-mysql-1"     # docker ps to find name
    EnvDbName     = "MYSQL_DATABASE"        # .env variable names
    EnvDbUser     = "MYSQL_USER"
    EnvDbPass     = "MYSQL_PASSWORD"
    DumpOptions   = "--single-transaction --routines --triggers --default-character-set=utf8mb4"
}
```

**External MySQL** (e.g. Loopia, remote server):
```powershell
Database = @{
    Type          = "mysql-local"
    EnvDbHost     = "DB_HOST"              # .env variable for hostname
    EnvDbPort     = "DB_PORT"              # .env variable for port
    EnvDbName     = "DB_NAME"
    EnvDbUser     = "DB_USER"
    EnvDbPass     = "DB_PASSWORD"
    DumpOptions   = "--single-transaction --routines --triggers --default-character-set=utf8mb4"
}
```

Then in your `.env` file:
```
DB_HOST=mysql123.loopia.se
DB_PORT=3306
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=supersecret
```

**IMPORTANT**: The script reads ALL credentials from `.env`. Never write
passwords in the .ps1 file!

### 3. Docker

```powershell
HasDocker = $true    # Set to $true if project uses docker-compose
HasDocker = $false   # Set to $false if no Docker
```

### 4. Exclusions

Add/remove directories and file patterns:
```powershell
ExcludeDirs = @(
    "node_modules"
    ".git"
    # Add your project-specific exclusions here
)

ExcludeFiles = @(
    ".env"
    "*.log"
    # Add patterns here
)
```

### 5. Log Collection

Add paths to log files/directories you want included:
```powershell
LogPaths = @(
    "logs/app.log"
    "test-results/summary.md"
    "test-results/unit"
)
```

### 6. Git Clean Worktree

```powershell
RequireCleanWorktree = $true    # Abort if uncommitted changes
RequireCleanWorktree = $false   # Allow dirty worktree
```

## Secrets Scanner

The script automatically scans ALL text files after copying and replaces
sensitive data with `[REDACTED]`. It catches:

- Passwords (`password=xxx`, `DB_PASSWORD=xxx`)
- API keys (`api_key=xxx`, `OPENAI_API_KEY=sk-...`)
- Tokens (`token=xxx`, `auth_token=xxx`)
- Credit card numbers (13-19 digit sequences)
- GitHub tokens (`ghp_...`)
- Slack tokens (`xoxb-...`)
- AWS/Azure secrets

To add custom patterns, edit `SensitivePatterns` in the config.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Git worktree is dirty" | Commit or stash your changes first |
| "mysqldump not found" | Install MySQL client or add to PATH |
| "Container not running" | Run `docker compose up -d` first |
| ZIP is huge | Add large dirs to `ExcludeDirs` |
| Swedish characters broken | Check SWEDISH_ENCODING_RULES.md in docs/ |

## File Overview

| File | Purpose |
|------|---------|
| `create_codebase.bat` | Double-click launcher |
| `create_codebase.ps1` | Main script (all logic here) |
| `create_codebase.md` | This documentation |
| `delete_nul_script.ps1` | Removes cursed NUL files |
