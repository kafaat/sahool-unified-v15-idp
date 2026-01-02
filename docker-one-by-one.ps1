<#
.SYNOPSIS
    SAHOOL Docker Sequential Build and Start Script

.DESCRIPTION
    This script builds and starts Docker containers one by one sequentially.
    It first builds all services with --no-cache, then starts them with up -d.
    Services are organized by dependency order: infrastructure first, then application services.

.NOTES
    Compatible with Windows 11 PowerShell 5.1+ and PowerShell Core 7+

.EXAMPLE
    .\docker-one-by-one.ps1

.EXAMPLE
    .\docker-one-by-one.ps1 -SkipBuild

.EXAMPLE
    .\docker-one-by-one.ps1 -SkipStart
#>

[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [switch]$SkipStart,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Continue"

# Colors for output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
}

function Write-ServiceStatus {
    param(
        [string]$Service,
        [string]$Status,
        [string]$Color
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor DarkGray
    Write-Host "$Service " -NoNewline -ForegroundColor White
    Write-Host "- $Status" -ForegroundColor $Color
}

# ═══════════════════════════════════════════════════════════════════════════════
# Infrastructure Services (images only - no build needed)
# These are pulled from Docker Hub and don't require building
# ═══════════════════════════════════════════════════════════════════════════════
$infrastructureServices = @(
    "postgres",
    "pgbouncer",
    "redis",
    "nats",
    "mqtt",
    "qdrant",
    "etcd",
    "minio",
    "milvus",
    "kong"
)

# ═══════════════════════════════════════════════════════════════════════════════
# Application Services (require building)
# Ordered by dependencies - services that others depend on come first
# ═══════════════════════════════════════════════════════════════════════════════
$buildableServices = @(
    # Core services (fewer dependencies)
    "field-ops",
    "ws-gateway",
    "billing-core",
    "provider-config",
    "crop-health",

    # Weather and vegetation services
    "weather-service",
    "weather-core",
    "vegetation-analysis-service",
    "indicators-service",

    # Field and management services
    "field-management-service",
    "field-service",
    "field-chat",

    # IoT services
    "iot-gateway",
    "iot-service",

    # Advisory and intelligence services
    "advisory-service",
    "agro-advisor",
    "crop-intelligence-service",

    # Analysis services
    "ndvi-engine",
    "ndvi-processor",
    "virtual-sensors",
    "yield-prediction-service",
    "yield-prediction",
    "lai-estimation",
    "crop-growth-model",

    # Smart services
    "irrigation-smart",

    # Notification and alert services
    "notification-service",
    "alert-service",

    # Business services
    "marketplace-service",
    "research-core",
    "disaster-assessment",
    "inventory-service",
    "equipment-service",
    "task-service",

    # Chat services
    "chat-service",
    "community-chat",

    # Calendar and rules
    "astronomical-calendar",
    "agro-rules",

    # AI services (depend on many others)
    "ai-advisor",

    # MCP Server (depends on Kong and others)
    "mcp-server"
)

# Track statistics
$buildSuccess = 0
$buildFailed = 0
$startSuccess = 0
$startFailed = 0
$failedServices = @()

# ═══════════════════════════════════════════════════════════════════════════════
# Build Phase
# ═══════════════════════════════════════════════════════════════════════════════
if (-not $SkipBuild) {
    Write-Header "PHASE 1: Building Services (--no-cache)"

    $totalBuildable = $buildableServices.Count
    $current = 0

    foreach ($service in $buildableServices) {
        $current++
        Write-Host ""
        Write-Host "[$current/$totalBuildable] " -NoNewline -ForegroundColor Yellow
        Write-Host "Building: " -NoNewline -ForegroundColor White
        Write-Host $service -ForegroundColor Green
        Write-Host ("-" * 50) -ForegroundColor DarkGray

        $startTime = Get-Date

        try {
            $process = Start-Process -FilePath "docker" -ArgumentList "compose", "build", "--no-cache", $service -NoNewWindow -Wait -PassThru

            $duration = (Get-Date) - $startTime
            $durationStr = "{0:mm\:ss}" -f $duration

            if ($process.ExitCode -eq 0) {
                Write-ServiceStatus $service "Build SUCCESS ($durationStr)" "Green"
                $buildSuccess++
            }
            else {
                Write-ServiceStatus $service "Build FAILED (exit code: $($process.ExitCode))" "Red"
                $buildFailed++
                $failedServices += "build:$service"
            }
        }
        catch {
            Write-ServiceStatus $service "Build ERROR: $_" "Red"
            $buildFailed++
            $failedServices += "build:$service"
        }
    }

    Write-Host ""
    Write-Host "Build Phase Complete: " -NoNewline -ForegroundColor Cyan
    Write-Host "$buildSuccess succeeded, " -NoNewline -ForegroundColor Green
    Write-Host "$buildFailed failed" -ForegroundColor $(if ($buildFailed -gt 0) { "Red" } else { "Green" })
}

# ═══════════════════════════════════════════════════════════════════════════════
# Start Phase
# ═══════════════════════════════════════════════════════════════════════════════
if (-not $SkipStart) {
    Write-Header "PHASE 2: Starting Infrastructure Services"

    $totalInfra = $infrastructureServices.Count
    $current = 0

    foreach ($service in $infrastructureServices) {
        $current++
        Write-Host ""
        Write-Host "[$current/$totalInfra] " -NoNewline -ForegroundColor Yellow
        Write-Host "Starting: " -NoNewline -ForegroundColor White
        Write-Host $service -ForegroundColor Magenta

        try {
            $process = Start-Process -FilePath "docker" -ArgumentList "compose", "up", "-d", $service -NoNewWindow -Wait -PassThru

            if ($process.ExitCode -eq 0) {
                Write-ServiceStatus $service "Started SUCCESS" "Green"
                $startSuccess++

                # Wait a bit for infrastructure services to initialize
                if ($service -in @("postgres", "redis", "nats")) {
                    Write-Host "  Waiting 5 seconds for $service to initialize..." -ForegroundColor DarkGray
                    Start-Sleep -Seconds 5
                }
                elseif ($service -in @("milvus", "kong")) {
                    Write-Host "  Waiting 10 seconds for $service to initialize..." -ForegroundColor DarkGray
                    Start-Sleep -Seconds 10
                }
                else {
                    Start-Sleep -Seconds 2
                }
            }
            else {
                Write-ServiceStatus $service "Start FAILED (exit code: $($process.ExitCode))" "Red"
                $startFailed++
                $failedServices += "start:$service"
            }
        }
        catch {
            Write-ServiceStatus $service "Start ERROR: $_" "Red"
            $startFailed++
            $failedServices += "start:$service"
        }
    }

    Write-Header "PHASE 3: Starting Application Services"

    $totalApps = $buildableServices.Count
    $current = 0

    foreach ($service in $buildableServices) {
        $current++
        Write-Host ""
        Write-Host "[$current/$totalApps] " -NoNewline -ForegroundColor Yellow
        Write-Host "Starting: " -NoNewline -ForegroundColor White
        Write-Host $service -ForegroundColor Blue

        try {
            $process = Start-Process -FilePath "docker" -ArgumentList "compose", "up", "-d", $service -NoNewWindow -Wait -PassThru

            if ($process.ExitCode -eq 0) {
                Write-ServiceStatus $service "Started SUCCESS" "Green"
                $startSuccess++

                # Small delay between service starts
                Start-Sleep -Seconds 2
            }
            else {
                Write-ServiceStatus $service "Start FAILED (exit code: $($process.ExitCode))" "Red"
                $startFailed++
                $failedServices += "start:$service"
            }
        }
        catch {
            Write-ServiceStatus $service "Start ERROR: $_" "Red"
            $startFailed++
            $failedServices += "start:$service"
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════
Write-Header "DEPLOYMENT SUMMARY"

if (-not $SkipBuild) {
    Write-Host "Build Results:" -ForegroundColor Cyan
    Write-Host "  Succeeded: $buildSuccess" -ForegroundColor Green
    Write-Host "  Failed:    $buildFailed" -ForegroundColor $(if ($buildFailed -gt 0) { "Red" } else { "Green" })
    Write-Host ""
}

if (-not $SkipStart) {
    Write-Host "Start Results:" -ForegroundColor Cyan
    Write-Host "  Succeeded: $startSuccess" -ForegroundColor Green
    Write-Host "  Failed:    $startFailed" -ForegroundColor $(if ($startFailed -gt 0) { "Red" } else { "Green" })
    Write-Host ""
}

if ($failedServices.Count -gt 0) {
    Write-Host "Failed Services:" -ForegroundColor Red
    foreach ($failed in $failedServices) {
        Write-Host "  - $failed" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "To retry failed services, run:" -ForegroundColor Yellow
    Write-Host "  docker compose build --no-cache <service-name>" -ForegroundColor White
    Write-Host "  docker compose up -d <service-name>" -ForegroundColor White
}
else {
    Write-Host "All services deployed successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "To check status: " -NoNewline -ForegroundColor Cyan
Write-Host "docker compose ps" -ForegroundColor White
Write-Host "To view logs:    " -NoNewline -ForegroundColor Cyan
Write-Host "docker compose logs -f <service-name>" -ForegroundColor White
Write-Host ""
