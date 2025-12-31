<#
.SYNOPSIS
    SAHOOL IDP - Advanced Load Testing Runner (PowerShell)
    سكريبت اختبار الحمل المتقدم لمنصة سهول

.DESCRIPTION
    Runs advanced load tests with multiple scenarios including:
    - Standard testing (20 agents)
    - Stress testing (50+ agents)
    - Spike testing (sudden load)
    - Chaos engineering testing

.PARAMETER Command
    start       - Start advanced infrastructure (5 instances)
    standard    - Run standard test (20 agents)
    stress      - Run stress test (50+ agents)
    spike       - Run spike test (sudden load)
    chaos       - Run chaos engineering test
    all         - Run all tests sequentially
    status      - Check status
    stop        - Stop all services
    clean       - Clean up everything

.PARAMETER AgentCount
    Number of base agents (default: 20)

.PARAMETER ChaosLevel
    Chaos level: low, medium, high, extreme (default: medium)

.EXAMPLE
    .\run-advanced.ps1 -Command start
    .\run-advanced.ps1 -Command stress -AgentCount 50
    .\run-advanced.ps1 -Command chaos -ChaosLevel high
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "standard", "stress", "spike", "chaos", "all", "status", "stop", "clean", "help")]
    [string]$Command = "help",

    [int]$AgentCount = 20,

    [ValidateSet("low", "medium", "high", "extreme")]
    [string]$ChaosLevel = "medium"
)

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile = Join-Path $ScriptDir "docker-compose-advanced.yml"

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Write-Banner {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  SAHOOL IDP - Advanced Load Testing" -ForegroundColor Cyan
    Write-Host "  اختبار الحمل المتقدم لمنصة سهول" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Info { param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param([string]$Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warn { param([string]$Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Err { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Test-Docker {
    try {
        $null = docker info 2>&1
        if ($LASTEXITCODE -ne 0) { Write-Err "Docker is not running"; exit 1 }
    } catch { Write-Err "Docker not installed"; exit 1 }
}

# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

function Start-AdvancedInfrastructure {
    Write-Banner
    Write-Info "Starting advanced infrastructure (5 app instances)..."
    Test-Docker

    Push-Location $ScriptDir
    try {
        # Start infrastructure
        docker-compose -f $ComposeFile up -d `
            sahool-db sahool-pgbouncer sahool-redis `
            sahool-prometheus sahool-alertmanager `
            sahool-influxdb sahool-grafana

        Write-Info "Waiting for databases (30s)..."
        Start-Sleep -Seconds 30

        # Start app instances
        docker-compose -f $ComposeFile up -d `
            sahool-app-1 sahool-app-2 sahool-app-3 sahool-app-4 sahool-app-5 sahool-nginx

        Write-Info "Waiting for apps (30s)..."
        Start-Sleep -Seconds 30

        Write-Success "Advanced infrastructure started!"
        Write-Host ""
        Write-Host "Access Points:" -ForegroundColor Yellow
        Write-Host "  Grafana:      http://localhost:3032"
        Write-Host "  Prometheus:   http://localhost:9091"
        Write-Host "  Alertmanager: http://localhost:9094"
        Write-Host "  App LB:       http://localhost:8081"
        Write-Host ""
    } finally { Pop-Location }
}

function Start-StandardTest {
    Write-Banner
    Write-Info "Running STANDARD test ($AgentCount agents)..."

    Push-Location $ScriptDir
    docker-compose -f $ComposeFile --profile standard-test run --rm `
        -e AGENT_COUNT=$AgentCount `
        sahool-k6-standard
    Pop-Location

    Write-Success "Standard test completed!"
}

function Start-StressTest {
    Write-Banner
    Write-Info "Running STRESS test ($AgentCount base agents, scaling to $($AgentCount * 5))..."

    Push-Location $ScriptDir
    docker-compose -f $ComposeFile --profile stress-test run --rm `
        -e AGENT_COUNT=$AgentCount `
        sahool-k6-stress
    Pop-Location

    Write-Success "Stress test completed!"
}

function Start-SpikeTest {
    Write-Banner
    Write-Info "Running SPIKE test (sudden load to $($AgentCount * 10) agents)..."

    Push-Location $ScriptDir
    docker-compose -f $ComposeFile --profile spike-test run --rm `
        -e AGENT_COUNT=$AgentCount `
        sahool-k6-spike
    Pop-Location

    Write-Success "Spike test completed!"
}

function Start-ChaosTest {
    Write-Banner
    Write-Info "Running CHAOS test (level: $ChaosLevel)..."

    Push-Location $ScriptDir
    docker-compose -f $ComposeFile --profile chaos-test run --rm `
        -e AGENT_COUNT=$AgentCount `
        -e CHAOS_LEVEL=$ChaosLevel `
        sahool-k6-chaos
    Pop-Location

    Write-Success "Chaos test completed!"
}

function Start-AllTests {
    Write-Banner
    Write-Info "Running ALL tests sequentially..."

    Start-StandardTest
    Start-Sleep -Seconds 30

    Start-StressTest
    Start-Sleep -Seconds 30

    Start-SpikeTest
    Start-Sleep -Seconds 30

    Start-ChaosTest

    Write-Success "All tests completed! Check Grafana for results."
}

function Get-Status {
    Write-Banner
    Push-Location $ScriptDir
    docker-compose -f $ComposeFile ps
    Pop-Location
}

function Stop-Services {
    Write-Banner
    Write-Info "Stopping all services..."
    Push-Location $ScriptDir
    docker-compose -f $ComposeFile down
    Pop-Location
    Write-Success "Services stopped."
}

function Clear-All {
    Write-Banner
    Write-Warn "This will remove ALL data!"
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -match "^[Yy]$") {
        Push-Location $ScriptDir
        docker-compose -f $ComposeFile down -v --remove-orphans
        Pop-Location
        Write-Success "Cleanup complete."
    }
}

function Show-Help {
    Write-Banner
    Write-Host "Usage: .\run-advanced.ps1 -Command <command> [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  start     Start advanced infrastructure (5 instances)"
    Write-Host "  standard  Run standard test (20 agents)"
    Write-Host "  stress    Run stress test (50+ agents)"
    Write-Host "  spike     Run spike test (sudden load)"
    Write-Host "  chaos     Run chaos engineering test"
    Write-Host "  all       Run all tests sequentially"
    Write-Host "  status    Check service status"
    Write-Host "  stop      Stop all services"
    Write-Host "  clean     Remove everything"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -AgentCount   Base agent count (default: 20)"
    Write-Host "  -ChaosLevel   low, medium, high, extreme (default: medium)"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run-advanced.ps1 -Command start"
    Write-Host "  .\run-advanced.ps1 -Command stress -AgentCount 50"
    Write-Host "  .\run-advanced.ps1 -Command chaos -ChaosLevel high"
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

switch ($Command) {
    "start"    { Start-AdvancedInfrastructure }
    "standard" { Start-StandardTest }
    "stress"   { Start-StressTest }
    "spike"    { Start-SpikeTest }
    "chaos"    { Start-ChaosTest }
    "all"      { Start-AllTests }
    "status"   { Get-Status }
    "stop"     { Stop-Services }
    "clean"    { Clear-All }
    default    { Show-Help }
}
