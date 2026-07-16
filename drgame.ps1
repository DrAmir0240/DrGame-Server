# ============================================================
# DrGame ERP — Windows PowerShell equivalent of Makefile
# Usage: .\drgame.ps1 <command> [options]
# ============================================================

param(
    [Parameter(Position = 0)]
    [string]$Command = "help",

    [string]$ENV = "dev",
    [string]$app  = "",
    [string]$name = "",
    [string]$f    = ""
)

$ComposeFile = "docker-compose.$ENV.yml"

# ── Colors ────────────────────────────────────────────────────
function Write-Cyan($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Red($msg)  { Write-Host $msg -ForegroundColor Red  }

# ── Help ──────────────────────────────────────────────────────
function Invoke-Help {
    Write-Host ""
    Write-Cyan "DrGame ERP — Available commands"
    Write-Host ""
    Write-Host "  .\drgame.ps1 build                   Build images (ENV=dev|prod)"
    Write-Host "  .\drgame.ps1 build-no-cache           Build images without cache"
    Write-Host "  .\drgame.ps1 up                       Start containers in background"
    Write-Host "  .\drgame.ps1 up-build                 Start containers and rebuild"
    Write-Host "  .\drgame.ps1 down                     Stop and remove containers"
    Write-Host "  .\drgame.ps1 restart                  Restart all containers"
    Write-Host "  .\drgame.ps1 logs                     Follow all logs"
    Write-Host "  .\drgame.ps1 logs-app                 Follow app logs only"
    Write-Host "  .\drgame.ps1 logs-db                  Follow db logs only"
    Write-Host "  .\drgame.ps1 logs-redis               Follow redis logs only"
    Write-Host "  .\drgame.ps1 shell                    Open bash shell in app container"
    Write-Host "  .\drgame.ps1 db-shell                 Open psql in db container"
    Write-Host "  .\drgame.ps1 redis-shell              Open redis-cli in redis container"
    Write-Host "  .\drgame.ps1 migrate                  Run manage.py migrate"
    Write-Host "  .\drgame.ps1 migrate-create -app foo  Run makemigrations for app"
    Write-Host "  .\drgame.ps1 migrate-down -app foo -name 0001  Revert to migration"
    Write-Host "  .\drgame.ps1 migrate-history          Show all migrations"
    Write-Host "  .\drgame.ps1 backup                   Dump database to .\backup\"
    Write-Host "  .\drgame.ps1 restore -f backup\file   Restore DB from file"
    Write-Host "  .\drgame.ps1 ps                       Show running containers"
    Write-Host "  .\drgame.ps1 clean                    Remove stopped containers"
    Write-Host "  .\drgame.ps1 fclean                   Remove containers + volumes (DANGER)"
    Write-Host ""
    Write-Host "  -ENV dev (default) | prod"
    Write-Host ""
}

# ── Build ─────────────────────────────────────────────────────
function Invoke-Build          { docker compose -f $ComposeFile build }
function Invoke-BuildNoCache   { docker compose -f $ComposeFile build --no-cache }

# ── Up / Down / Restart ───────────────────────────────────────
function Invoke-Up             { docker compose -f $ComposeFile up -d }
function Invoke-UpBuild        { docker compose -f $ComposeFile up -d --build }
function Invoke-Down           { docker compose -f $ComposeFile down }
function Invoke-Restart        { docker compose -f $ComposeFile restart }

# ── Logs ──────────────────────────────────────────────────────
function Invoke-Logs           { docker compose -f $ComposeFile logs -f }
function Invoke-LogsApp        { docker compose -f $ComposeFile logs -f app }
function Invoke-LogsDb         { docker compose -f $ComposeFile logs -f db }
function Invoke-LogsRedis      { docker compose -f $ComposeFile logs -f redis }

# ── Shell ─────────────────────────────────────────────────────
function Invoke-Shell          { docker exec -it drgame_app bash }
function Invoke-DbShell {
    $pgUser = $env:POSTGRES_USER
    $pgDb   = $env:POSTGRES_DB
    docker exec -it drgame-db psql -U $pgUser -d $pgDb
}
function Invoke-RedisShell     { docker exec -it drgame-redis redis-cli }

# ── Migrations ────────────────────────────────────────────────
function Invoke-Migrate        { docker exec -it drgame_app python manage.py migrate }

function Invoke-MigrateCreate {
    if (-not $app) {
        Write-Red "Usage: .\drgame.ps1 migrate-create -app <app_name>"
        exit 1
    }
    docker exec -it drgame_app python manage.py makemigrations $app
}

function Invoke-MigrateDown {
    if (-not $app -or -not $name) {
        Write-Red "Usage: .\drgame.ps1 migrate-down -app <app_name> -name <migration_name>"
        exit 1
    }
    docker exec -it drgame_app python manage.py migrate $app $name
}

function Invoke-MigrateHistory { docker exec -it drgame_app python manage.py showmigrations }

# ── Backup / Restore ──────────────────────────────────────────
function Invoke-Backup {
    $pgUser = $env:POSTGRES_USER
    $pgDb   = $env:POSTGRES_DB

    if (-not (Test-Path ".\backup")) { New-Item -ItemType Directory -Path ".\backup" | Out-Null }

    $timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = ".\backup\backup_$timestamp.sql"

    docker exec drgame-db pg_dump -U $pgUser $pgDb | Out-File -FilePath $backupFile -Encoding utf8
    Write-Cyan "Backup saved to $backupFile"
}

function Invoke-Restore {
    if (-not $f) {
        Write-Red "Usage: .\drgame.ps1 restore -f backup\filename.sql"
        exit 1
    }
    $pgUser = $env:POSTGRES_USER
    $pgDb   = $env:POSTGRES_DB

    Get-Content $f | docker exec -i drgame-db psql -U $pgUser -d $pgDb
    Write-Cyan "Restore done from $f"
}

# ── Status ────────────────────────────────────────────────────
function Invoke-Ps    { docker compose -f $ComposeFile ps }

# ── Cleanup ───────────────────────────────────────────────────
function Invoke-Clean {
    docker compose -f $ComposeFile rm -f
}

function Invoke-Fclean {
    Write-Red "WARNING: This will delete all volumes and data!"
    $confirm = Read-Host "Are you sure? [y/N]"
    if ($confirm -ne "y") { Write-Host "Aborted."; exit 0 }
    docker compose -f $ComposeFile down -v
    docker image prune -f
}

# ── Router ────────────────────────────────────────────────────
switch ($Command) {
    "help"             { Invoke-Help }
    "build"            { Invoke-Build }
    "build-no-cache"   { Invoke-BuildNoCache }
    "up"               { Invoke-Up }
    "up-build"         { Invoke-UpBuild }
    "down"             { Invoke-Down }
    "restart"          { Invoke-Restart }
    "logs"             { Invoke-Logs }
    "logs-app"         { Invoke-LogsApp }
    "logs-db"          { Invoke-LogsDb }
    "logs-redis"       { Invoke-LogsRedis }
    "shell"            { Invoke-Shell }
    "db-shell"         { Invoke-DbShell }
    "redis-shell"      { Invoke-RedisShell }
    "migrate"          { Invoke-Migrate }
    "migrate-create"   { Invoke-MigrateCreate }
    "migrate-down"     { Invoke-MigrateDown }
    "migrate-history"  { Invoke-MigrateHistory }
    "backup"           { Invoke-Backup }
    "restore"          { Invoke-Restore }
    "ps"               { Invoke-Ps }
    "clean"            { Invoke-Clean }
    "fclean"           { Invoke-Fclean }
    default {
        Write-Red "Unknown command: $Command"
        Write-Host "Run '.\drgame.ps1 help' for usage."
        exit 1
    }
}