<#
.SYNOPSIS
    SAHOOL IDP - Simulation Environment Verification Script (PowerShell)
    سكريبت التحقق من بيئة المحاكاة لمنصة سهول

.DESCRIPTION
    This script verifies that all simulation files are present and valid,
    then attempts to build and run the simulation environment.

.PARAMETER Mode
    Verification mode: Full, Check, or Build
    - Full: Complete verification and build test (default)
    - Check: Only check files (no build)
    - Build: Skip checks, just validate docker-compose

.EXAMPLE
    .\verify-simulation.ps1
    .\verify-simulation.ps1 -Mode Check
    .\verify-simulation.ps1 -Mode Build

.NOTES
    Author: SAHOOL IDP Team
    Version: 1.0.0
#>

param(
    [ValidateSet("Full", "Check", "Build")]
    [string]$Mode = "Full"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item "$ScriptDir\..\..\..").FullName

# Counters
$Script:ChecksPassed = 0
$Script:ChecksFailed = 0
$Script:Warnings = 0

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Write-Banner {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  SAHOOL IDP - Simulation Verification Script (PowerShell)" -ForegroundColor Cyan
    Write-Host "  سكريبت التحقق من بيئة المحاكاة" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Project Root: $ProjectRoot"
    Write-Host "  Script Dir: $ScriptDir"
    Write-Host ""
}

function Write-SectionHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host "───────────────────────────────────────────────────────────────────────────────" -ForegroundColor Blue
    Write-Host "  $Title" -ForegroundColor Blue
    Write-Host "───────────────────────────────────────────────────────────────────────────────" -ForegroundColor Blue
}

function Write-CheckPass {
    param([string]$Message)
    Write-Host "  [✓ PASS] $Message" -ForegroundColor Green
    $Script:ChecksPassed++
}

function Write-CheckFail {
    param([string]$Message)
    Write-Host "  [✗ FAIL] $Message" -ForegroundColor Red
    $Script:ChecksFailed++
}

function Write-CheckWarn {
    param([string]$Message)
    Write-Host "  [⚠ WARN] $Message" -ForegroundColor Yellow
    $Script:Warnings++
}

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

function Test-CoreFiles {
    Write-SectionHeader "1. Core Simulation Files - الملفات الأساسية"

    # docker-compose-sim.yml
    $composeFile = Join-Path $ScriptDir "docker-compose-sim.yml"
    if (Test-Path $composeFile) {
        Write-CheckPass "docker-compose-sim.yml exists"

        $content = Get-Content $composeFile -Raw

        if ($content -match "sahool-db:") {
            Write-CheckPass "docker-compose-sim.yml contains sahool-db service"
        } else {
            Write-CheckFail "docker-compose-sim.yml missing sahool-db service"
        }

        if ($content -match "sahool-app-1:") {
            Write-CheckPass "docker-compose-sim.yml contains app instances"
        } else {
            Write-CheckFail "docker-compose-sim.yml missing app instances"
        }

        if ($content -match "sahool-nginx:") {
            Write-CheckPass "docker-compose-sim.yml contains nginx load balancer"
        } else {
            Write-CheckFail "docker-compose-sim.yml missing nginx load balancer"
        }

        if ($content -match "sahool-k6:") {
            Write-CheckPass "docker-compose-sim.yml contains k6 testing service"
        } else {
            Write-CheckFail "docker-compose-sim.yml missing k6 testing service"
        }
    } else {
        Write-CheckFail "docker-compose-sim.yml NOT FOUND"
    }

    # README.md
    if (Test-Path (Join-Path $ScriptDir "README.md")) {
        Write-CheckPass "README.md documentation exists"
    } else {
        Write-CheckWarn "README.md documentation missing"
    }

    # run-simulation.sh
    if (Test-Path (Join-Path $ScriptDir "run-simulation.sh")) {
        Write-CheckPass "run-simulation.sh runner script exists"
    } else {
        Write-CheckFail "run-simulation.sh NOT FOUND"
    }

    # run-simulation.ps1
    if (Test-Path (Join-Path $ScriptDir "run-simulation.ps1")) {
        Write-CheckPass "run-simulation.ps1 PowerShell script exists"
    } else {
        Write-CheckWarn "run-simulation.ps1 PowerShell script missing"
    }

    # .env.example
    if (Test-Path (Join-Path $ScriptDir ".env.example")) {
        Write-CheckPass ".env.example environment template exists"
    } else {
        Write-CheckWarn ".env.example template missing"
    }
}

function Test-NginxConfig {
    Write-SectionHeader "2. Nginx Configuration - إعدادات موازن الحمل"

    $nginxConf = Join-Path $ScriptDir "config\nginx.conf"
    if (Test-Path $nginxConf) {
        Write-CheckPass "config/nginx.conf exists"

        $content = Get-Content $nginxConf -Raw

        if ($content -match "upstream sahool_backend") {
            Write-CheckPass "nginx.conf contains upstream backend definition"
        } else {
            Write-CheckFail "nginx.conf missing upstream backend definition"
        }

        if ($content -match "least_conn") {
            Write-CheckPass "nginx.conf uses least_conn load balancing"
        } else {
            Write-CheckWarn "nginx.conf may not have optimal load balancing"
        }

        if ($content -match "sahool-app-1:8080") {
            Write-CheckPass "nginx.conf references app instances correctly"
        } else {
            Write-CheckFail "nginx.conf missing app instance references"
        }
    } else {
        Write-CheckFail "config/nginx.conf NOT FOUND"
    }

    # nginx-upstream.conf
    if (Test-Path (Join-Path $ScriptDir "config\nginx-upstream.conf")) {
        Write-CheckPass "config/nginx-upstream.conf exists"
    } else {
        Write-CheckWarn "config/nginx-upstream.conf missing (optional)"
    }

    # proxy-params.conf
    if (Test-Path (Join-Path $ScriptDir "config\proxy-params.conf")) {
        Write-CheckPass "config/proxy-params.conf exists"
    } else {
        Write-CheckWarn "config/proxy-params.conf missing (optional)"
    }
}

function Test-K6Scripts {
    Write-SectionHeader "3. K6 Load Testing Scripts - سكريبتات اختبار الحمل"

    $k6Script = Join-Path $ScriptDir "scripts\agent-simulation.js"
    if (Test-Path $k6Script) {
        Write-CheckPass "scripts/agent-simulation.js exists"

        $content = Get-Content $k6Script -Raw

        if ($content -match "export default function") {
            Write-CheckPass "agent-simulation.js has main test function"
        } else {
            Write-CheckFail "agent-simulation.js missing main test function"
        }

        if ($content -match "loginSuccessRate") {
            Write-CheckPass "agent-simulation.js has custom metrics"
        } else {
            Write-CheckWarn "agent-simulation.js missing custom metrics"
        }

        if ($content -match "connection_pool_errors") {
            Write-CheckPass "agent-simulation.js tracks connection pool errors"
        } else {
            Write-CheckWarn "agent-simulation.js may not track connection pool errors"
        }

        if ($content -match "session_loss_errors") {
            Write-CheckPass "agent-simulation.js tracks session loss errors"
        } else {
            Write-CheckWarn "agent-simulation.js may not track session loss errors"
        }
    } else {
        Write-CheckFail "scripts/agent-simulation.js NOT FOUND"
    }
}

function Test-GrafanaConfig {
    Write-SectionHeader "4. Grafana Dashboards - لوحات المراقبة"

    if (Test-Path (Join-Path $ScriptDir "grafana\dashboards\k6-dashboard.json")) {
        Write-CheckPass "grafana/dashboards/k6-dashboard.json exists"
    } else {
        Write-CheckWarn "grafana/dashboards/k6-dashboard.json missing"
    }

    if (Test-Path (Join-Path $ScriptDir "grafana\dashboards\dashboards.yml")) {
        Write-CheckPass "grafana/dashboards/dashboards.yml exists"
    } else {
        Write-CheckWarn "grafana/dashboards/dashboards.yml missing"
    }

    if (Test-Path (Join-Path $ScriptDir "grafana\datasources\influxdb.yml")) {
        Write-CheckPass "grafana/datasources/influxdb.yml exists"
    } else {
        Write-CheckWarn "grafana/datasources/influxdb.yml missing"
    }
}

function Test-Dockerfile {
    Write-SectionHeader "5. Application Dockerfile - ملف بناء التطبيق"

    $dockerfile = Join-Path $ProjectRoot "apps\services\field-ops\Dockerfile"
    if (Test-Path $dockerfile) {
        Write-CheckPass "apps/services/field-ops/Dockerfile exists"

        $content = Get-Content $dockerfile -Raw

        if ($content -match "FROM python") {
            Write-CheckPass "Dockerfile uses Python base image"
        } elseif ($content -match "FROM node") {
            Write-CheckPass "Dockerfile uses Node.js base image"
        } else {
            Write-CheckWarn "Dockerfile base image unclear"
        }

        if ($content -match "HEALTHCHECK") {
            Write-CheckPass "Dockerfile includes HEALTHCHECK"
        } else {
            Write-CheckWarn "Dockerfile missing HEALTHCHECK instruction"
        }

        if ($content -match "8080") {
            Write-CheckPass "Dockerfile exposes port 8080"
        } else {
            Write-CheckWarn "Dockerfile may not expose correct port"
        }
    } else {
        Write-CheckFail "apps/services/field-ops/Dockerfile NOT FOUND"
        Write-Host "    → The docker-compose-sim.yml references this Dockerfile" -ForegroundColor Yellow
    }
}

function Test-Directories {
    Write-SectionHeader "6. Required Directories - المجلدات المطلوبة"

    # Results directory
    $resultsDir = Join-Path $ScriptDir "results"
    if (Test-Path $resultsDir) {
        Write-CheckPass "results/ directory exists"
    } else {
        Write-CheckWarn "results/ directory missing (creating...)"
        New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null
        Write-CheckPass "results/ directory created"
    }

    # Init scripts directory
    $initScriptsDir = Join-Path $ScriptDir "init-scripts"
    if (Test-Path $initScriptsDir) {
        Write-CheckPass "init-scripts/ directory exists"
    } else {
        Write-CheckWarn "init-scripts/ directory missing (creating...)"
        New-Item -ItemType Directory -Path $initScriptsDir -Force | Out-Null
        Write-CheckPass "init-scripts/ directory created"
    }

    # Config directory
    if (Test-Path (Join-Path $ScriptDir "config")) {
        Write-CheckPass "config/ directory exists"
    } else {
        Write-CheckFail "config/ directory NOT FOUND"
    }

    # Scripts directory
    if (Test-Path (Join-Path $ScriptDir "scripts")) {
        Write-CheckPass "scripts/ directory exists"
    } else {
        Write-CheckFail "scripts/ directory NOT FOUND"
    }
}

function Test-DockerEnvironment {
    Write-SectionHeader "7. Docker Environment - بيئة Docker"

    # Check if Docker is installed
    try {
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckPass "Docker is installed"
            Write-Host "    Version: $dockerVersion" -ForegroundColor Cyan
        } else {
            Write-CheckFail "Docker is NOT installed"
        }
    } catch {
        Write-CheckFail "Docker is NOT installed or not in PATH"
    }

    # Check if Docker Compose is available
    try {
        $composeVersion = docker-compose --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckPass "Docker Compose is installed (standalone)"
            Write-Host "    Version: $composeVersion" -ForegroundColor Cyan
        } else {
            # Try docker compose (plugin)
            $composeVersion = docker compose version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-CheckPass "Docker Compose is installed (plugin)"
                Write-Host "    Version: $composeVersion" -ForegroundColor Cyan
            } else {
                Write-CheckFail "Docker Compose is NOT installed"
            }
        }
    } catch {
        Write-CheckFail "Docker Compose is NOT installed or not in PATH"
    }

    # Check if Docker daemon is running
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckPass "Docker daemon is running"
        } else {
            Write-CheckWarn "Docker daemon is not running (start Docker Desktop to build)"
        }
    } catch {
        Write-CheckWarn "Could not check Docker daemon status"
    }
}

function Test-DockerCompose {
    Write-SectionHeader "8. Build Test - اختبار البناء"

    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-CheckWarn "Skipping build test - Docker daemon not running"
            return
        }
    } catch {
        Write-CheckWarn "Skipping build test - Docker not available"
        return
    }

    Write-Host "  Attempting to validate docker-compose configuration..." -ForegroundColor White

    Push-Location $ScriptDir
    try {
        $result = docker-compose -f docker-compose-sim.yml config 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckPass "docker-compose-sim.yml is valid YAML"
        } else {
            Write-CheckFail "docker-compose-sim.yml has syntax errors"
            Write-Host "    Run: docker-compose -f docker-compose-sim.yml config" -ForegroundColor Yellow
        }
    } catch {
        Write-CheckFail "Could not validate docker-compose configuration"
    }
    Pop-Location

    Write-Host ""
    Write-Host "  To build and run the simulation:" -ForegroundColor White
    Write-Host "    cd $ScriptDir" -ForegroundColor Cyan
    Write-Host "    .\run-simulation.ps1 -Command Start" -ForegroundColor Cyan
    Write-Host "    .\run-simulation.ps1 -Command Test" -ForegroundColor Cyan
}

function Write-Summary {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  VERIFICATION SUMMARY - ملخص التحقق" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Passed:   $Script:ChecksPassed checks" -ForegroundColor Green
    Write-Host "  Failed:   $Script:ChecksFailed checks" -ForegroundColor Red
    Write-Host "  Warnings: $Script:Warnings checks" -ForegroundColor Yellow
    Write-Host ""

    if ($Script:ChecksFailed -eq 0) {
        Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host "  ✓ ALL CRITICAL CHECKS PASSED - SIMULATION READY" -ForegroundColor Green
        Write-Host "  ✓ جميع الفحوصات الحرجة نجحت - المحاكاة جاهزة" -ForegroundColor Green
        Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Next steps:" -ForegroundColor White
        Write-Host "    1. cd tests\load\simulation"
        Write-Host "    2. .\run-simulation.ps1 -Command Start"
        Write-Host "    3. .\run-simulation.ps1 -Command Test"
        Write-Host ""
        return $true
    } else {
        Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Red
        Write-Host "  ✗ SOME CHECKS FAILED - REVIEW REQUIRED" -ForegroundColor Red
        Write-Host "  ✗ بعض الفحوصات فشلت - مراجعة مطلوبة" -ForegroundColor Red
        Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

Write-Banner

switch ($Mode) {
    "Check" {
        Write-Host "Running file checks only..." -ForegroundColor White
        Test-CoreFiles
        Test-NginxConfig
        Test-K6Scripts
        Test-GrafanaConfig
        Test-Dockerfile
        Test-Directories
    }
    "Build" {
        Write-Host "Running build test only..." -ForegroundColor White
        Test-DockerEnvironment
        Test-DockerCompose
    }
    default {
        Test-CoreFiles
        Test-NginxConfig
        Test-K6Scripts
        Test-GrafanaConfig
        Test-Dockerfile
        Test-Directories
        Test-DockerEnvironment
        Test-DockerCompose
    }
}

$success = Write-Summary

if (-not $success) {
    exit 1
}
