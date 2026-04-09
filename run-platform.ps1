#Requires -Version 5.1
<#
.SYNOPSIS
    SAHOOL Platform Launcher - starts backend services

.PARAMETER InfraOnly
    Start only infrastructure (postgres, redis, nats, kong) without app services

.PARAMETER Down
    Stop all running platform services

.PARAMETER Logs
    Follow logs for core services after startup

.EXAMPLE
    .\run-platform.ps1
    .\run-platform.ps1 -InfraOnly
    .\run-platform.ps1 -Down
    .\run-platform.ps1 -Logs
#>

param(
    [switch]$InfraOnly,
    [switch]$Down,
    [switch]$Logs
)

$ErrorActionPreference = 'Stop'

function Write-Header { param($m) Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Step   { param($m) Write-Host "  > $m" -ForegroundColor White }
function Write-Ok     { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn   { param($m) Write-Host "  [WARN] $m" -ForegroundColor Yellow }
function Write-Err    { param($m) Write-Host "  [ERR] $m" -ForegroundColor Red }

$Root    = $PSScriptRoot
$EnvFile = Join-Path $Root ".env"

Set-Location $Root

# ---- Tear-down ---------------------------------------------------------------
if ($Down) {
    Write-Header "Stopping SAHOOL Platform"
    Write-Step "Stopping Docker services..."
    docker compose down
    Write-Ok "Platform stopped."
    exit 0
}

# ---- Prerequisites -----------------------------------------------------------
Write-Header "SAHOOL Platform v16.0.0"
Write-Step "Checking prerequisites..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Err "Docker is not installed or not in PATH"
    exit 1
}

docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Err "Docker Desktop is not running. Please start it first."
    exit 1
}
Write-Ok "Docker is running"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Err "Node.js is not installed or not in PATH"
    exit 1
}
Write-Ok "Node.js $(node --version)"

if (-not (Test-Path $EnvFile)) {
    Write-Err ".env file not found at $EnvFile -- create it before running the platform."
    exit 1
}
Write-Ok ".env found"

# ---- Infrastructure Services -------------------------------------------------
Write-Header "Starting Infrastructure Services"

$infraServices = @("postgres", "pgbouncer", "redis", "nats", "kong")
Write-Step "Starting: $($infraServices -join ', ')"

docker compose up -d @infraServices
if ($LASTEXITCODE -ne 0) {
    Write-Err "Failed to start infrastructure services."
    exit 1
}
Write-Ok "Infrastructure services started"

# Wait for PostgreSQL
Write-Step "Waiting for PostgreSQL..."
$pgUser = (Get-Content $EnvFile | Where-Object { $_ -match '^POSTGRES_USER=' } | Select-Object -First 1) -replace '^POSTGRES_USER=', ''
if (-not $pgUser) { $pgUser = 'sahool' }
$maxWait = 60
$waited  = 0
$pgReady = ""
do {
    Start-Sleep -Seconds 3
    $waited += 3
    $pgReady = docker exec sahool-postgres pg_isready -U $pgUser 2>&1
    if ($pgReady -match "accepting connections") { break }
    Write-Host "    ... waiting (${waited}s)" -ForegroundColor DarkGray
} while ($waited -lt $maxWait)

if ($pgReady -match "accepting connections") {
    Write-Ok "PostgreSQL is ready"
} else {
    Write-Warn "PostgreSQL not ready after ${maxWait}s -- services may fail to migrate"
}

# Wait for Kong — TCP check on port 8000 (HTTP would throw on 404, Admin is loopback-only)
Write-Step "Waiting for Kong gateway..."
$kongWait = 0
$kongReady = $false
do {
    Start-Sleep -Seconds 2
    $kongWait += 2
    $tcp = Test-NetConnection -ComputerName localhost -Port 8000 -WarningAction SilentlyContinue
    if ($tcp.TcpTestSucceeded) { $kongReady = $true; break }
    Write-Host "    ... waiting (${kongWait}s)" -ForegroundColor DarkGray
} while ($kongWait -lt 30)

if ($kongReady) {
    Write-Ok "Kong proxy is up (http://localhost:8000)"
} else {
    Write-Warn "Kong not responding yet -- continuing anyway"
}

# Load declarative config (KONG_DECLARATIVE_CONFIG_DIR does not auto-load on Kong 3.9 startup)
# The Lua script lives in infrastructure/gateway/kong/reload-config.lua
Write-Step "Loading Kong declarative config from kong.yml..."
$luaFile = Join-Path $Root "infrastructure\gateway\kong\reload-config.lua"
docker cp $luaFile sahool-kong:/tmp/reload-config.lua | Out-Null
$kongLoadResult = docker exec sahool-kong resty /tmp/reload-config.lua 2>&1
if ($kongLoadResult -match "^201") {
    Write-Ok "Kong config loaded (routes active)"
} elseif ($kongLoadResult -match "^200") {
    Write-Ok "Kong config reloaded (routes active)"
} else {
    Write-Warn "Kong config reload returned: $kongLoadResult"
}

if ($InfraOnly) {
    Write-Header "Infrastructure Ready"
    Write-Ok "Kong API Gateway : http://localhost:8000 (routes loaded)"
    Write-Ok "PostgreSQL       : localhost:5432"
    Write-Ok "Redis            : localhost:6379"
    Write-Ok "NATS             : localhost:4222"
    exit 0
}

# ---- Core App Services -------------------------------------------------------
Write-Header "Starting Core Application Services"

$appServices = @(
    "user-service"
    "field-management-service"
    "weather-service"
    "vegetation-analysis-service"
    "notification-service"
    "ws-gateway"
)
Write-Step "Starting: $($appServices -join ', ')"

docker compose up -d @appServices
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Some app services failed to start (they may already be running)."
} else {
    Write-Ok "Core app services started"
}

# Wait for user-service
Write-Step "Waiting for user-service (port 3025)..."
$svcWait  = 0
$svcReady = $false
do {
    Start-Sleep -Seconds 3
    $svcWait += 3
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:3025/healthz" -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $svcReady = $true; break }
    } catch { }
    Write-Host "    ... waiting (${svcWait}s)" -ForegroundColor DarkGray
} while ($svcWait -lt 60)

if ($svcReady) {
    Write-Ok "user-service is healthy"
} else {
    Write-Warn "user-service not responding yet -- web app may show auth errors initially"
}

# ---- Summary -----------------------------------------------------------------
Write-Header "SAHOOL Platform is Running"
Write-Host ""
Write-Host "  Kong API Gateway  : " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Kong Admin        : " -NoNewline; Write-Host "http://localhost:8001" -ForegroundColor Cyan
Write-Host "  WebSocket Gateway : " -NoNewline; Write-Host "ws://localhost:8081"   -ForegroundColor Cyan
Write-Host "  PostgreSQL        : " -NoNewline; Write-Host "localhost:5432"        -ForegroundColor Cyan
Write-Host "  Redis             : " -NoNewline; Write-Host "localhost:6379"        -ForegroundColor Cyan
Write-Host ""
Write-Host "  To stop : .\run-platform.ps1 -Down" -ForegroundColor DarkGray
Write-Host "  Logs    : docker compose logs -f user-service field-management-service" -ForegroundColor DarkGray
Write-Host ""

if ($Logs) {
    Write-Step "Following service logs (Ctrl+C to exit)..."
    docker compose logs -f user-service field-management-service kong
}
