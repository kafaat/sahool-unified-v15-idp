<#
.SYNOPSIS
    SAHOOL IDP - Simulation Environment Verification Script (PowerShell)

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

# =============================================================================
# CONFIGURATION
# =============================================================================

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item "$ScriptDir\..\..\..").FullName

# Counters
$Script:ChecksPassed = 0
$Script:ChecksFailed = 0
$Script:Warnings = 0

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

function Write-Banner {
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host "  SAHOOL IDP - Simulation Verification Script (PowerShell)" -ForegroundColor Cyan
    Write-Host "  Simulation Environment Verification" -ForegroundColor Cyan
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Project Root: $ProjectRoot"
    Write-Host "  Script Dir: $ScriptDir"
    Write-Host ""
}

function Write-SectionHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host "-------------------------------------------------------------------------------" -ForegroundColor Blue
    Write-Host "  $Title" -ForegroundColor Blue
    Write-Host "-------------------------------------------------------------------------------" -ForegroundColor Blue
}

function Write-CheckPass {
    param([string]$Message)
    Write-Host "  [PASS] $Message" -ForegroundColor Green
    $Script:ChecksPassed++
}

function Write-CheckFail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor Red
    $Script:ChecksFailed++
}

function Write-CheckWarn {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
    $Script:Warnings++
}

# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

function Test-CoreFiles {
    Write-SectionHeader "1. Core Simulation Files"

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

    # docker-compose-advanced.yml
    $advancedFile = Join-Path $ScriptDir "docker-compose-advanced.yml"
    if (Test-Path $advancedFile) {
        Write-CheckPass "docker-compose-advanced.yml exists"
    } else {
        Write-CheckWarn "docker-compose-advanced.yml missing"
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
}

function Test-NginxConfig {
    Write-SectionHeader "2. Nginx Configuration"

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

    # nginx-advanced.conf
    if (Test-Path (Join-Path $ScriptDir "config\nginx-advanced.conf")) {
        Write-CheckPass "config/nginx-advanced.conf exists"
    } else {
        Write-CheckWarn "config/nginx-advanced.conf missing"
    }

    # proxy-params.conf
    if (Test-Path (Join-Path $ScriptDir "config\proxy-params.conf")) {
        Write-CheckPass "config/proxy-params.conf exists"
    } else {
        Write-CheckWarn "config/proxy-params.conf missing"
    }
}

function Test-K6Scripts {
    Write-SectionHeader "3. K6 Load Testing Scripts"

    $scriptsDir = Join-Path $ScriptDir "scripts"

    $scripts = @(
        "agent-simulation.js",
        "advanced-scenarios.js",
        "chaos-testing.js",
        "mobile-app-simulation.js",
        "web-dashboard-simulation.js",
        "multi-client-simulation.js"
    )

    foreach ($script in $scripts) {
        $scriptPath = Join-Path $scriptsDir $script
        if (Test-Path $scriptPath) {
            Write-CheckPass "$script exists"

            $content = Get-Content $scriptPath -Raw
            if ($content -match "export (default )?function") {
                Write-CheckPass "$script has valid K6 structure"
            } else {
                Write-CheckWarn "$script may have invalid structure"
            }
        } else {
            Write-CheckFail "$script not found"
        }
    }
}

function Test-GrafanaConfig {
    Write-SectionHeader "4. Grafana Dashboards"

    $dashboardsDir = Join-Path $ScriptDir "grafana\dashboards"

    $dashboards = @(
        "k6-dashboard.json",
        "advanced-dashboard.json",
        "multi-client-dashboard.json"
    )

    foreach ($dashboard in $dashboards) {
        $dashPath = Join-Path $dashboardsDir $dashboard
        if (Test-Path $dashPath) {
            Write-CheckPass "$dashboard exists"

            try {
                $null = Get-Content $dashPath -Raw | ConvertFrom-Json
                Write-CheckPass "$dashboard is valid JSON"
            } catch {
                Write-CheckFail "$dashboard is invalid JSON"
            }
        } else {
            Write-CheckWarn "$dashboard not found"
        }
    }

    $datasourcesDir = Join-Path $ScriptDir "grafana\datasources"
    $influxDs = Join-Path $datasourcesDir "influxdb.yml"
    if (Test-Path $influxDs) {
        Write-CheckPass "InfluxDB datasource config exists"
    } else {
        Write-CheckWarn "InfluxDB datasource config not found"
    }
}

function Test-MonitoringConfig {
    Write-SectionHeader "5. Monitoring Configuration"

    $monitoringDir = Join-Path $ScriptDir "monitoring"

    $configs = @(
        "prometheus.yml",
        "alertmanager.yml",
        "alert-rules.yml"
    )

    foreach ($config in $configs) {
        $configPath = Join-Path $monitoringDir $config
        if (Test-Path $configPath) {
            Write-CheckPass "$config exists"
        } else {
            Write-CheckWarn "$config not found"
        }
    }
}

function Test-Dockerfile {
    Write-SectionHeader "6. Application Dockerfile"

    $dockerfile = Join-Path $ProjectRoot "apps\services\field-ops\Dockerfile"
    if (Test-Path $dockerfile) {
        Write-CheckPass "apps/services/field-ops/Dockerfile exists"

        $content = Get-Content $dockerfile -Raw

        if ($content -match "FROM") {
            Write-CheckPass "Dockerfile has FROM instruction"
        } else {
            Write-CheckFail "Dockerfile missing FROM instruction"
        }

        if ($content -match "8080") {
            Write-CheckPass "Dockerfile exposes port 8080"
        } else {
            Write-CheckWarn "Dockerfile may not expose correct port"
        }
    } else {
        Write-CheckFail "apps/services/field-ops/Dockerfile NOT FOUND"
    }
}

function Test-Directories {
    Write-SectionHeader "7. Required Directories"

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

function Test-RunnerScripts {
    Write-SectionHeader "8. Runner Scripts"

    $scripts = @(
        "run-simulation.sh",
        "run-simulation.ps1",
        "run-advanced.sh",
        "run-advanced.ps1",
        "run-multiclient.ps1",
        "verify-simulation.sh"
    )

    foreach ($script in $scripts) {
        $scriptPath = Join-Path $ScriptDir $script
        if (Test-Path $scriptPath) {
            Write-CheckPass "$script exists"
        } else {
            Write-CheckWarn "$script not found"
        }
    }
}

function Test-DockerEnvironment {
    Write-SectionHeader "9. Docker Environment"

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
        $composeVersion = docker compose version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckPass "Docker Compose is installed (plugin)"
            Write-Host "    Version: $composeVersion" -ForegroundColor Cyan
        } else {
            # Try docker-compose (standalone)
            $composeVersion = docker-compose --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-CheckPass "Docker Compose is installed (standalone)"
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
    Write-SectionHeader "10. Docker Compose Validation"

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
        $result = docker compose -f docker-compose-sim.yml config 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckPass "docker-compose-sim.yml is valid"
        } else {
            Write-CheckFail "docker-compose-sim.yml has syntax errors"
        }
    } catch {
        Write-CheckWarn "Could not validate docker-compose-sim.yml"
    }

    try {
        $result = docker compose -f docker-compose-advanced.yml config 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-CheckPass "docker-compose-advanced.yml is valid"
        } else {
            Write-CheckWarn "docker-compose-advanced.yml has issues"
        }
    } catch {
        Write-CheckWarn "Could not validate docker-compose-advanced.yml"
    }
    Pop-Location
}

function Write-Summary {
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host "  VERIFICATION SUMMARY" -ForegroundColor Cyan
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Passed:   $Script:ChecksPassed checks" -ForegroundColor Green
    Write-Host "  Failed:   $Script:ChecksFailed checks" -ForegroundColor Red
    Write-Host "  Warnings: $Script:Warnings checks" -ForegroundColor Yellow
    Write-Host ""

    if ($Script:ChecksFailed -eq 0) {
        Write-Host "===============================================================================" -ForegroundColor Green
        Write-Host "  ALL CRITICAL CHECKS PASSED - SIMULATION READY" -ForegroundColor Green
        Write-Host "===============================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Next steps:" -ForegroundColor White
        Write-Host "    1. .\run-simulation.ps1 -Command Start"
        Write-Host "    2. .\run-simulation.ps1 -Command Test -AgentCount 10"
        Write-Host ""
        Write-Host "  Or for multi-client testing:" -ForegroundColor White
        Write-Host "    1. .\run-multiclient.ps1 -Command start"
        Write-Host "    2. .\run-multiclient.ps1 -Command multiclient -VUs 20"
        Write-Host ""
        return $true
    } else {
        Write-Host "===============================================================================" -ForegroundColor Red
        Write-Host "  SOME CHECKS FAILED - REVIEW REQUIRED" -ForegroundColor Red
        Write-Host "===============================================================================" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# =============================================================================
# MAIN
# =============================================================================

Write-Banner

switch ($Mode) {
    "Check" {
        Write-Host "Running file checks only..." -ForegroundColor White
        Test-CoreFiles
        Test-NginxConfig
        Test-K6Scripts
        Test-GrafanaConfig
        Test-MonitoringConfig
        Test-Dockerfile
        Test-Directories
        Test-RunnerScripts
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
        Test-MonitoringConfig
        Test-Dockerfile
        Test-Directories
        Test-RunnerScripts
        Test-DockerEnvironment
        Test-DockerCompose
    }
}

$success = Write-Summary

if (-not $success) {
    exit 1
}
