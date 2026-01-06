<#
.SYNOPSIS
    SAHOOL IDP - Load Testing Simulation Runner (PowerShell)
    سكريبت تشغيل محاكاة اختبار الحمل لمنصة سهول

.DESCRIPTION
    This script manages the simulation environment for load testing.
    Supports starting infrastructure, running tests, and cleanup.

.PARAMETER Command
    The command to execute:
    - Start: Start simulation infrastructure (DB, Redis, monitoring)
    - StartApps: Start application instances (requires built images)
    - Test: Run k6 agent simulation
    - Quick: Run quick standalone test
    - Status: Check status of all services
    - Health: Check health of services
    - Logs: View logs (use -Service to specify)
    - Stop: Stop all services
    - Clean: Clean up everything including volumes
    - Help: Show help message

.PARAMETER AgentCount
    Number of virtual agents for load testing (default: 10)

.PARAMETER BaseUrl
    Base URL for quick test (default: http://localhost:8080)

.PARAMETER Service
    Service name for logs command

.EXAMPLE
    .\run-simulation.ps1 -Command Start
    .\run-simulation.ps1 -Command Test -AgentCount 20
    .\run-simulation.ps1 -Command Quick -BaseUrl "http://localhost:8080"
    .\run-simulation.ps1 -Command Logs -Service sahool-db

.NOTES
    Author: SAHOOL IDP Team
    Version: 1.0.0
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("Start", "StartApps", "Test", "Quick", "Status", "Health", "Logs", "Stop", "Clean", "Help")]
    [string]$Command = "Help",

    [int]$AgentCount = 10,

    [string]$BaseUrl = "http://localhost:8080",

    [string]$Service = ""
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile = Join-Path $ScriptDir "docker-compose-sim.yml"

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Write-Banner {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "  SAHOOL IDP - Load Testing Simulation" -ForegroundColor Blue
    Write-Host "  محاكاة اختبار الحمل لمنصة سهول" -ForegroundColor Blue
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Docker {
    try {
        $null = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Docker is not running. Please start Docker Desktop first."
            exit 1
        }
    } catch {
        Write-Error "Docker is not installed or not in PATH."
        exit 1
    }
}

function New-ResultsDirectory {
    $resultsDir = Join-Path $ScriptDir "results"
    $initScriptsDir = Join-Path $ScriptDir "init-scripts"

    if (-not (Test-Path $resultsDir)) {
        New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null
    }
    if (-not (Test-Path $initScriptsDir)) {
        New-Item -ItemType Directory -Path $initScriptsDir -Force | Out-Null
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Start-Infrastructure {
    Write-Banner
    Write-Info "Starting simulation infrastructure..."

    Test-Docker
    New-ResultsDirectory

    # Start infrastructure services
    Push-Location $ScriptDir
    try {
        docker-compose -f $ComposeFile up -d `
            sahool-db `
            sahool-pgbouncer `
            sahool-redis `
            sahool-influxdb `
            sahool-grafana

        Write-Info "Waiting for databases to be ready (30 seconds)..."
        Start-Sleep -Seconds 30

        # Check health
        Get-ServiceHealth

        Write-Success "Infrastructure started successfully!"
        Write-Host ""
        Write-Info "Access points:"
        Write-Host "  - Grafana: http://localhost:3031 (admin/admin)"
        Write-Host "  - InfluxDB: http://localhost:8087 (see .env.influxdb.secret for credentials)"
        Write-Host "  - PostgreSQL: localhost:5433"
        Write-Host "  - Redis: localhost:6380"
        Write-Host ""
        Write-Info "To start application instances, run: .\run-simulation.ps1 -Command StartApps"
    } finally {
        Pop-Location
    }
}

function Start-ApplicationInstances {
    Write-Banner
    Write-Info "Starting 3 application instances..."

    Test-Docker

    Write-Warning "Application instances require the actual SAHOOL service images."
    Write-Info "In production, run:"
    Write-Host "  docker-compose -f $ComposeFile up -d sahool-app-1 sahool-app-2 sahool-app-3 sahool-nginx"
}

function Start-LoadTest {
    Write-Banner
    Write-Info "Running k6 agent simulation with $AgentCount virtual agents..."

    Test-Docker
    New-ResultsDirectory

    Write-Info "Agent count: $AgentCount"
    Write-Info "Duration: 3 minutes"
    Write-Host ""

    Push-Location $ScriptDir
    try {
        # Run k6 with simulation script
        docker-compose -f $ComposeFile --profile testing run --rm `
            -e AGENT_COUNT=$AgentCount `
            sahool-k6

        Write-Success "Simulation completed!"
        Write-Info "Check results in: $ScriptDir\results\"
        Write-Info "View Grafana dashboard: http://localhost:3031"
    } finally {
        Pop-Location
    }
}

function Start-QuickTest {
    Write-Banner
    Write-Info "Running quick k6 test (standalone mode)..."

    Test-Docker
    New-ResultsDirectory

    Write-Info "Base URL: $BaseUrl"
    Write-Info "Agent count: $AgentCount"
    Write-Host ""

    docker run --rm `
        --network host `
        -v "${ScriptDir}\scripts:/scripts:ro" `
        -v "${ScriptDir}\results:/results" `
        -e BASE_URL="$BaseUrl" `
        -e AGENT_COUNT=$AgentCount `
        -e ENVIRONMENT="quick-test" `
        grafana/k6:0.48.0 run /scripts/agent-simulation.js

    Write-Success "Quick test completed!"
    Write-Info "Check results in: $ScriptDir\results\"
}

function Get-ServiceHealth {
    Write-Info "Checking service health..."

    # Check PostgreSQL
    try {
        $result = docker exec sahool_db_sim pg_isready -U sahool_admin 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  PostgreSQL: " -NoNewline
            Write-Host "HEALTHY" -ForegroundColor Green
        } else {
            Write-Host "  PostgreSQL: " -NoNewline
            Write-Host "UNHEALTHY" -ForegroundColor Red
        }
    } catch {
        Write-Host "  PostgreSQL: " -NoNewline
        Write-Host "NOT RUNNING" -ForegroundColor Red
    }

    # Check Redis
    try {
        $result = docker exec sahool_redis_sim redis-cli -a sim_redis_pass_123 ping 2>&1
        if ($result -match "PONG") {
            Write-Host "  Redis: " -NoNewline
            Write-Host "HEALTHY" -ForegroundColor Green
        } else {
            Write-Host "  Redis: " -NoNewline
            Write-Host "UNHEALTHY" -ForegroundColor Red
        }
    } catch {
        Write-Host "  Redis: " -NoNewline
        Write-Host "NOT RUNNING" -ForegroundColor Red
    }

    # Check InfluxDB
    try {
        $result = docker exec sahool_influxdb_sim influx ping 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  InfluxDB: " -NoNewline
            Write-Host "HEALTHY" -ForegroundColor Green
        } else {
            Write-Host "  InfluxDB: " -NoNewline
            Write-Host "UNHEALTHY" -ForegroundColor Red
        }
    } catch {
        Write-Host "  InfluxDB: " -NoNewline
        Write-Host "NOT RUNNING" -ForegroundColor Red
    }

    # Check Grafana
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3031/api/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "  Grafana: " -NoNewline
            Write-Host "HEALTHY" -ForegroundColor Green
        } else {
            Write-Host "  Grafana: " -NoNewline
            Write-Host "UNHEALTHY" -ForegroundColor Red
        }
    } catch {
        Write-Host "  Grafana: " -NoNewline
        Write-Host "NOT RUNNING" -ForegroundColor Red
    }
}

function Get-ServiceStatus {
    Write-Banner
    Write-Info "Service status:"

    Push-Location $ScriptDir
    try {
        docker-compose -f $ComposeFile ps
    } finally {
        Pop-Location
    }

    Write-Host ""
    Get-ServiceHealth
}

function Get-ServiceLogs {
    Push-Location $ScriptDir
    try {
        if ([string]::IsNullOrEmpty($Service)) {
            docker-compose -f $ComposeFile logs --tail=100 -f
        } else {
            docker-compose -f $ComposeFile logs --tail=100 -f $Service
        }
    } finally {
        Pop-Location
    }
}

function Stop-Services {
    Write-Banner
    Write-Info "Stopping simulation services..."

    Push-Location $ScriptDir
    try {
        docker-compose -f $ComposeFile down
        Write-Success "All services stopped."
    } finally {
        Pop-Location
    }
}

function Clear-Everything {
    Write-Banner
    Write-Warning "This will remove all containers, volumes, and data!"

    $confirm = Read-Host "Are you sure? (y/N)"
    if ($confirm -match "^[Yy]$") {
        Write-Info "Cleaning up..."

        Push-Location $ScriptDir
        try {
            docker-compose -f $ComposeFile down -v --remove-orphans

            $resultsDir = Join-Path $ScriptDir "results"
            if (Test-Path $resultsDir) {
                Remove-Item -Path "$resultsDir\*" -Recurse -Force -ErrorAction SilentlyContinue
            }

            Write-Success "Cleanup complete."
        } finally {
            Pop-Location
        }
    } else {
        Write-Info "Cleanup cancelled."
    }
}

function Show-Help {
    Write-Banner
    Write-Host "Usage: .\run-simulation.ps1 -Command <command> [options]"
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  Start           Start simulation infrastructure (DB, Redis, monitoring)"
    Write-Host "  StartApps       Start application instances (requires built images)"
    Write-Host "  Test            Run k6 agent simulation"
    Write-Host "  Quick           Run quick standalone test"
    Write-Host "  Status          Check status of all services"
    Write-Host "  Health          Check health of services"
    Write-Host "  Logs            View logs (use -Service for specific service)"
    Write-Host "  Stop            Stop all services"
    Write-Host "  Clean           Clean up everything including volumes"
    Write-Host "  Help            Show this help message"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -AgentCount     Number of virtual agents (default: 10)"
    Write-Host "  -BaseUrl        Base URL for quick test (default: http://localhost:8080)"
    Write-Host "  -Service        Service name for logs command"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run-simulation.ps1 -Command Start"
    Write-Host "  .\run-simulation.ps1 -Command Test -AgentCount 20"
    Write-Host "  .\run-simulation.ps1 -Command Quick -BaseUrl 'http://myserver:8080'"
    Write-Host "  .\run-simulation.ps1 -Command Logs -Service sahool-db"
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

switch ($Command) {
    "Start" { Start-Infrastructure }
    "StartApps" { Start-ApplicationInstances }
    "Test" { Start-LoadTest }
    "Quick" { Start-QuickTest }
    "Status" { Get-ServiceStatus }
    "Health" { Get-ServiceHealth }
    "Logs" { Get-ServiceLogs }
    "Stop" { Stop-Services }
    "Clean" { Clear-Everything }
    "Help" { Show-Help }
    default { Show-Help }
}
