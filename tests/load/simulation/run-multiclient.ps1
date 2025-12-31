<#
.SYNOPSIS
    SAHOOL IDP - Multi-Client Simulation Runner (PowerShell)

.DESCRIPTION
    Runs multi-client load testing with realistic traffic distribution:
    - 60% Mobile (iOS + Android)
    - 30% Web Dashboard
    - 10% API Integration

.PARAMETER Command
    Command to execute: start, mobile, web, multiclient, production, status, stop, clean

.PARAMETER VUs
    Number of virtual users (default: 20)

.PARAMETER Duration
    Test duration (default: 5m)

.EXAMPLE
    .\run-multiclient.ps1 -Command start
    .\run-multiclient.ps1 -Command multiclient -VUs 30
    .\run-multiclient.ps1 -Command production -VUs 50 -Duration 10m
    .\run-multiclient.ps1 -Command stop

.NOTES
    Author: SAHOOL IDP Team
    Version: 2.0.0
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "mobile", "web", "multiclient", "production", "status", "logs", "stop", "clean")]
    [string]$Command,

    [int]$VUs = 20,

    [string]$Duration = "5m"
)

# =============================================================================
# CONFIGURATION
# =============================================================================

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile = Join-Path $ScriptDir "docker-compose-advanced.yml"

# Colors for output
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Banner {
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host "  SAHOOL IDP - Multi-Client Simulation Runner" -ForegroundColor Cyan
    Write-Host "  Multi-Client Load Testing with Realistic Distribution" -ForegroundColor Cyan
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Traffic Distribution:" -ForegroundColor White
    Write-Host "    - Mobile (iOS + Android): 60%" -ForegroundColor Green
    Write-Host "    - Web Dashboard: 30%" -ForegroundColor Blue
    Write-Host "    - API Integration: 10%" -ForegroundColor Yellow
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "-------------------------------------------------------------------------------" -ForegroundColor Blue
    Write-Host "  $Title" -ForegroundColor Blue
    Write-Host "-------------------------------------------------------------------------------" -ForegroundColor Blue
}

# =============================================================================
# DOCKER FUNCTIONS
# =============================================================================

function Test-DockerRunning {
    try {
        $result = docker info 2>&1
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Start-Infrastructure {
    Write-Section "Starting Infrastructure (5 app instances)"

    if (-not (Test-DockerRunning)) {
        Write-ColorOutput "ERROR: Docker is not running. Please start Docker first." "Red"
        return $false
    }

    Write-ColorOutput "Starting database, cache, and monitoring services..." "White"

    # Start core services
    docker compose -f $ComposeFile up -d `
        sahool-db `
        sahool-pgbouncer `
        sahool-redis `
        sahool-prometheus `
        sahool-alertmanager `
        sahool-influxdb `
        sahool-grafana

    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Failed to start core services" "Red"
        return $false
    }

    Write-ColorOutput "Waiting for database to be ready..." "Yellow"
    Start-Sleep -Seconds 10

    # Start app instances and nginx
    Write-ColorOutput "Starting 5 application instances and load balancer..." "White"
    docker compose -f $ComposeFile up -d `
        sahool-app-1 `
        sahool-app-2 `
        sahool-app-3 `
        sahool-app-4 `
        sahool-app-5 `
        sahool-nginx

    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Failed to start application instances" "Red"
        return $false
    }

    Write-ColorOutput "Waiting for applications to initialize..." "Yellow"
    Start-Sleep -Seconds 15

    Write-ColorOutput "[OK] Infrastructure started successfully!" "Green"
    Write-Host ""
    Write-ColorOutput "Access Points:" "Cyan"
    Write-ColorOutput "  - App (Load Balancer): http://localhost:8081" "White"
    Write-ColorOutput "  - Grafana: http://localhost:3032 (admin/admin)" "White"
    Write-ColorOutput "  - Prometheus: http://localhost:9091" "White"
    Write-ColorOutput "  - Alertmanager: http://localhost:9094" "White"

    return $true
}

function Run-MobileTest {
    param([int]$AgentCount, [string]$TestDuration)

    Write-Section "Running Mobile App Simulation"
    Write-ColorOutput "  Agents: $AgentCount (45% iOS, 55% Android)" "White"
    Write-ColorOutput "  Duration: $TestDuration" "White"

    $env:MOBILE_VUS = $AgentCount
    $env:TEST_DURATION = $TestDuration

    docker compose -f $ComposeFile --profile mobile-test run --rm sahool-k6-mobile

    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] Mobile simulation completed!" "Green"
    } else {
        Write-ColorOutput "[FAIL] Mobile simulation failed" "Red"
    }
}

function Run-WebTest {
    param([int]$AgentCount, [string]$TestDuration)

    Write-Section "Running Web Dashboard Simulation"
    Write-ColorOutput "  Agents: $AgentCount (50% Manager, 30% Admin, 20% Analyst)" "White"
    Write-ColorOutput "  Duration: $TestDuration" "White"

    $env:WEB_VUS = $AgentCount
    $env:TEST_DURATION = $TestDuration

    docker compose -f $ComposeFile --profile web-test run --rm sahool-k6-web

    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] Web simulation completed!" "Green"
    } else {
        Write-ColorOutput "[FAIL] Web simulation failed" "Red"
    }
}

function Run-MultiClientTest {
    param([int]$AgentCount, [string]$TestDuration)

    Write-Section "Running Multi-Client Realistic Simulation"
    Write-ColorOutput "  Total Agents: $AgentCount" "White"
    Write-ColorOutput "  Distribution:" "White"

    $mobileVUs = [math]::Ceiling($AgentCount * 0.60)
    $webVUs = [math]::Ceiling($AgentCount * 0.30)
    $apiVUs = [math]::Ceiling($AgentCount * 0.10)

    Write-ColorOutput "    - Mobile: $mobileVUs VUs (60%)" "Green"
    Write-ColorOutput "    - Web: $webVUs VUs (30%)" "Blue"
    Write-ColorOutput "    - API: $apiVUs VUs (10%)" "Yellow"
    Write-ColorOutput "  Duration: $TestDuration" "White"
    Write-ColorOutput "  Success Target: >90%" "Cyan"

    $env:TOTAL_VUS = $AgentCount
    $env:TEST_DURATION = $TestDuration

    docker compose -f $ComposeFile --profile multiclient-test run --rm sahool-k6-multiclient

    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] Multi-client simulation completed!" "Green"
    } else {
        Write-ColorOutput "[FAIL] Multi-client simulation failed" "Red"
    }
}

function Run-ProductionTest {
    param([int]$AgentCount, [string]$TestDuration)

    Write-Section "Running Full Production Simulation"
    Write-ColorOutput "  Total Agents: $AgentCount" "White"
    Write-ColorOutput "  Duration: $TestDuration" "White"
    Write-ColorOutput "  Mode: Production-like stress test" "Magenta"

    $env:TOTAL_VUS = $AgentCount
    $env:TEST_DURATION = $TestDuration

    docker compose -f $ComposeFile --profile production-test run --rm sahool-k6-production

    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] Production simulation completed!" "Green"
    } else {
        Write-ColorOutput "[FAIL] Production simulation failed" "Red"
    }
}

function Show-Status {
    Write-Section "Service Status"
    docker compose -f $ComposeFile ps
}

function Show-Logs {
    param([string]$Service = "")

    if ($Service) {
        docker compose -f $ComposeFile logs -f $Service
    } else {
        docker compose -f $ComposeFile logs -f --tail=100
    }
}

function Stop-Services {
    Write-Section "Stopping All Services"
    docker compose -f $ComposeFile down
    Write-ColorOutput "[OK] All services stopped" "Green"
}

function Clean-Environment {
    Write-Section "Cleaning Environment"

    Write-ColorOutput "Stopping services..." "Yellow"
    docker compose -f $ComposeFile down -v --remove-orphans

    Write-ColorOutput "Removing volumes..." "Yellow"
    docker volume rm $(docker volume ls -q -f name=simulation) 2>$null

    Write-ColorOutput "Cleaning results..." "Yellow"
    $resultsDir = Join-Path $ScriptDir "results"
    if (Test-Path $resultsDir) {
        Remove-Item -Path "$resultsDir\*" -Force -Recurse 2>$null
    }

    Write-ColorOutput "[OK] Environment cleaned" "Green"
}

# =============================================================================
# MAIN
# =============================================================================

Write-Banner

switch ($Command) {
    "start" {
        Start-Infrastructure
    }
    "mobile" {
        Run-MobileTest -AgentCount $VUs -TestDuration $Duration
    }
    "web" {
        Run-WebTest -AgentCount $VUs -TestDuration $Duration
    }
    "multiclient" {
        Run-MultiClientTest -AgentCount $VUs -TestDuration $Duration
    }
    "production" {
        Run-ProductionTest -AgentCount $VUs -TestDuration $Duration
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    "stop" {
        Stop-Services
    }
    "clean" {
        Clean-Environment
    }
}

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  Command completed: $Command" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
