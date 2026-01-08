<#
.SYNOPSIS
    SAHOOL Platform - Internal Environment Build Script
    سكريبت بناء منصة سهول للبيئة الداخلية

.DESCRIPTION
    Comprehensive build script with logging system for building SAHOOL platform
    in Windows environment using Docker Compose.

.PARAMETER Mode
    Build mode: all, infra, core, ai, integration, health, logs, clean

.PARAMETER Verbose
    Enable verbose output

.EXAMPLE
    .\Build-SahoolInternal.ps1 -Mode all
    .\Build-SahoolInternal.ps1 -Mode infra
    .\Build-SahoolInternal.ps1 -Mode health

.NOTES
    Version: 1.0.0
    Author: SAHOOL DevOps Team
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("all", "infra", "core", "ai", "integration", "health", "logs", "clean")]
    [string]$Mode = "all",

    [switch]$NoCache,
    [switch]$Parallel
)

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration / التكوين
# ═══════════════════════════════════════════════════════════════════════════════
$ErrorActionPreference = "Continue"
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:LogsDir = Join-Path $ProjectRoot "logs"
$script:Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Log files
$script:BuildLog = Join-Path $LogsDir "build_$Timestamp.log"
$script:ErrorLog = Join-Path $LogsDir "errors_$Timestamp.log"
$script:SummaryLog = Join-Path $LogsDir "summary_$Timestamp.log"
$script:CombinedLog = Join-Path $LogsDir "sahool_build_$Timestamp.log"

# Build counters
$script:BuildSuccess = 0
$script:BuildFailed = 0
$script:BuildWarnings = 0
$script:FailedServices = @()
$script:BuildStartTime = Get-Date

# ═══════════════════════════════════════════════════════════════════════════════
# Logging Functions / دوال التسجيل
# ═══════════════════════════════════════════════════════════════════════════════
function Initialize-Logging {
    if (-not (Test-Path $LogsDir)) {
        New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    }

    $header = @"
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Build Log - سجل بناء منصة سهول
Build Started: $(Get-Date)
Environment: Internal / البيئة الداخلية
PowerShell Version: $($PSVersionTable.PSVersion)
═══════════════════════════════════════════════════════════════════════════════

"@
    $header | Out-File -FilePath $BuildLog -Encoding UTF8

    $errorHeader = @"
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Error Log - سجل أخطاء منصة سهول
Build Started: $(Get-Date)
═══════════════════════════════════════════════════════════════════════════════

"@
    $errorHeader | Out-File -FilePath $ErrorLog -Encoding UTF8

    $combinedHeader = @"
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Combined Build Log
منصة سهول - سجل البناء الموحد
═══════════════════════════════════════════════════════════════════════════════
Build ID: $Timestamp
Started: $(Get-Date)
Project Root: $ProjectRoot
Mode: $Mode
═══════════════════════════════════════════════════════════════════════════════

"@
    $combinedHeader | Out-File -FilePath $CombinedLog -Encoding UTF8
}

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARNING", "ERROR", "STEP")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$Level] [$timestamp] $Message"

    # Console output with colors
    switch ($Level) {
        "INFO"    { Write-Host $logMessage -ForegroundColor Cyan }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        "WARNING" {
            Write-Host $logMessage -ForegroundColor Yellow
            $script:BuildWarnings++
        }
        "ERROR"   {
            Write-Host $logMessage -ForegroundColor Red
            $logMessage | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
        }
        "STEP"    {
            Write-Host ""
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
            Write-Host "[$Level] $Message" -ForegroundColor Magenta
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
        }
    }

    # File output
    $logMessage | Out-File -FilePath $BuildLog -Append -Encoding UTF8
    $logMessage | Out-File -FilePath $CombinedLog -Append -Encoding UTF8
}

# ═══════════════════════════════════════════════════════════════════════════════
# Prerequisites Check / فحص المتطلبات
# ═══════════════════════════════════════════════════════════════════════════════
function Test-Prerequisites {
    Write-Log "Checking Prerequisites / فحص المتطلبات الأساسية" -Level STEP

    $hasErrors = $false

    # Check Docker
    try {
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Docker installed: $dockerVersion" -Level SUCCESS
        } else {
            throw "Docker not found"
        }
    }
    catch {
        Write-Log "Docker is not installed or not in PATH" -Level ERROR
        Write-Log "Docker غير مثبت أو غير موجود في PATH" -Level ERROR
        $hasErrors = $true
    }

    # Check Docker Compose
    try {
        $composeVersion = docker compose version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Docker Compose installed: $composeVersion" -Level SUCCESS
        } else {
            # Try legacy docker-compose
            $composeVersion = docker-compose --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Docker Compose (legacy) installed: $composeVersion" -Level SUCCESS
            } else {
                throw "Docker Compose not found"
            }
        }
    }
    catch {
        Write-Log "Docker Compose is not installed" -Level ERROR
        Write-Log "Docker Compose غير مثبت" -Level ERROR
        $hasErrors = $true
    }

    # Check Docker daemon
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Docker daemon is running" -Level SUCCESS
        } else {
            throw "Docker daemon not running"
        }
    }
    catch {
        Write-Log "Docker daemon is not running" -Level ERROR
        Write-Log "خدمة Docker غير تعمل" -Level ERROR
        $hasErrors = $true
    }

    # Check .env file
    $envFile = Join-Path $ProjectRoot ".env"
    if (Test-Path $envFile) {
        Write-Log ".env file exists" -Level SUCCESS
    } else {
        Write-Log ".env file not found. Creating from .env.example..." -Level WARNING
        $envExample = Join-Path $ProjectRoot ".env.example"
        if (Test-Path $envExample) {
            Copy-Item $envExample $envFile
            Write-Log "Created .env from .env.example" -Level SUCCESS
            Write-Log "Please update .env with your actual values" -Level WARNING
        } else {
            Write-Log ".env.example not found" -Level ERROR
            $hasErrors = $true
        }
    }

    # Check docker-compose.yml
    $composeFile = Join-Path $ProjectRoot "docker-compose.yml"
    if (Test-Path $composeFile) {
        Write-Log "docker-compose.yml exists" -Level SUCCESS
    } else {
        Write-Log "docker-compose.yml not found" -Level ERROR
        $hasErrors = $true
    }

    return -not $hasErrors
}

# ═══════════════════════════════════════════════════════════════════════════════
# Build Functions / دوال البناء
# ═══════════════════════════════════════════════════════════════════════════════
function Build-Service {
    param(
        [string]$ServiceName
    )

    $startTime = Get-Date
    Write-Log "Building $ServiceName..." -Level INFO

    $buildArgs = @("compose", "build")
    if ($NoCache) { $buildArgs += "--no-cache" }
    $buildArgs += $ServiceName

    try {
        $output = & docker @buildArgs 2>&1
        $output | Out-File -FilePath $BuildLog -Append -Encoding UTF8

        if ($LASTEXITCODE -eq 0) {
            $duration = ((Get-Date) - $startTime).TotalSeconds
            Write-Log "$ServiceName built successfully (${duration}s)" -Level SUCCESS
            $script:BuildSuccess++

            # Start the service
            Write-Log "Starting $ServiceName..." -Level INFO
            $startOutput = & docker compose up -d $ServiceName 2>&1
            $startOutput | Out-File -FilePath $BuildLog -Append -Encoding UTF8

            if ($LASTEXITCODE -eq 0) {
                Write-Log "$ServiceName started successfully" -Level SUCCESS
            } else {
                Write-Log "$ServiceName built but failed to start" -Level WARNING
                $script:FailedServices += "${ServiceName}:start"
            }
        } else {
            throw "Build failed"
        }
    }
    catch {
        $duration = ((Get-Date) - $startTime).TotalSeconds
        Write-Log "$ServiceName build FAILED after ${duration}s" -Level ERROR
        $script:FailedServices += $ServiceName
        $script:BuildFailed++

        # Capture error details
        "─────────────────────────────────────────────────────────" | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
        "Service: $ServiceName" | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
        "Time: $(Get-Date)" | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
        $output | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
        "─────────────────────────────────────────────────────────" | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
    }
}

function Build-Infrastructure {
    Write-Log "Building Infrastructure Services / بناء خدمات البنية التحتية" -Level STEP

    $infraServices = @("postgres", "pgbouncer", "redis", "nats")

    foreach ($service in $infraServices) {
        Write-Log "Starting $service..." -Level INFO
        try {
            $output = & docker compose up -d $service 2>&1
            $output | Out-File -FilePath $BuildLog -Append -Encoding UTF8

            if ($LASTEXITCODE -eq 0) {
                Write-Log "$service started successfully" -Level SUCCESS
                $script:BuildSuccess++
            } else {
                throw "Failed to start"
            }
        }
        catch {
            Write-Log "Failed to start $service" -Level ERROR
            $script:FailedServices += $service
            $script:BuildFailed++
        }
    }

    Write-Log "Waiting for infrastructure services to be healthy..." -Level INFO
    Start-Sleep -Seconds 10
}

function Build-CoreServices {
    Write-Log "Building Core Application Services / بناء الخدمات الأساسية" -Level STEP

    $coreServices = @(
        "user-service",
        "field-service",
        "weather-service",
        "field-core",
        "field-ops"
    )

    foreach ($service in $coreServices) {
        Build-Service -ServiceName $service
    }
}

function Build-AIServices {
    Write-Log "Building AI & Analytics Services / بناء خدمات الذكاء الاصطناعي" -Level STEP

    $aiServices = @(
        "ai-advisor",
        "crop-health-ai",
        "agro-advisor",
        "yield-prediction",
        "ndvi-engine"
    )

    foreach ($service in $aiServices) {
        Build-Service -ServiceName $service
    }
}

function Build-IntegrationServices {
    Write-Log "Building Integration Services / بناء خدمات التكامل" -Level STEP

    $integrationServices = @(
        "iot-service",
        "notification-service",
        "chat-service",
        "ws-gateway"
    )

    foreach ($service in $integrationServices) {
        Build-Service -ServiceName $service
    }
}

function Build-AllServices {
    Write-Log "Building All Services / بناء جميع الخدمات" -Level STEP

    Write-Log "Running docker compose build..." -Level INFO

    $buildArgs = @("compose", "build")
    if ($NoCache) { $buildArgs += "--no-cache" }
    if ($Parallel) { $buildArgs += "--parallel" }

    $output = & docker @buildArgs 2>&1
    $output | Out-File -FilePath $BuildLog -Append -Encoding UTF8

    if ($LASTEXITCODE -eq 0) {
        Write-Log "All services built successfully" -Level SUCCESS
    } else {
        Write-Log "Some services may have failed to build. Check error log." -Level WARNING
    }

    Write-Log "Starting all services..." -Level INFO
    $output = & docker compose up -d 2>&1
    $output | Out-File -FilePath $BuildLog -Append -Encoding UTF8

    if ($LASTEXITCODE -eq 0) {
        Write-Log "All services started" -Level SUCCESS
    } else {
        Write-Log "Some services may have failed to start. Check error log." -Level WARNING
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# Health Check / فحص الصحة
# ═══════════════════════════════════════════════════════════════════════════════
function Test-ServicesHealth {
    Write-Log "Checking Services Health / فحص صحة الخدمات" -Level STEP

    $healthy = 0
    $unhealthy = 0
    $starting = 0

    $containers = docker ps --format "{{.Names}},{{.Status}}" 2>&1 | Where-Object { $_ -match "sahool" }

    foreach ($container in $containers) {
        if ($container -match "^([^,]+),(.+)$") {
            $name = $Matches[1]
            $status = $Matches[2]

            if ($status -match "healthy") {
                Write-Log "${name}: healthy" -Level SUCCESS
                $healthy++
            }
            elseif ($status -match "unhealthy") {
                Write-Log "${name}: unhealthy" -Level ERROR
                $unhealthy++
                # Get logs for unhealthy container
                docker logs --tail 50 $name 2>&1 | Out-File -FilePath $ErrorLog -Append -Encoding UTF8
            }
            elseif ($status -match "starting") {
                Write-Log "${name}: still starting..." -Level WARNING
                $starting++
            }
            else {
                Write-Log "${name}: $status" -Level INFO
            }
        }
    }

    Write-Log "Health Summary: $healthy healthy, $unhealthy unhealthy, $starting starting" -Level INFO
}

function Get-AllContainerLogs {
    Write-Log "Collecting Container Logs / جمع سجلات الحاويات" -Level STEP

    $containerLogsDir = Join-Path $LogsDir "containers_$Timestamp"
    New-Item -ItemType Directory -Path $containerLogsDir -Force | Out-Null

    $containers = docker compose ps -q 2>&1

    foreach ($containerId in $containers) {
        if ($containerId) {
            $containerName = docker inspect --format '{{.Name}}' $containerId 2>&1
            $containerName = $containerName -replace '^/', ''

            if ($containerName) {
                Write-Log "Collecting logs for $containerName..." -Level INFO
                docker logs $containerId 2>&1 | Out-File -FilePath (Join-Path $containerLogsDir "$containerName.log") -Encoding UTF8
            }
        }
    }

    Write-Log "Container logs saved to: $containerLogsDir" -Level SUCCESS
}

# ═══════════════════════════════════════════════════════════════════════════════
# Clean Function / دالة التنظيف
# ═══════════════════════════════════════════════════════════════════════════════
function Clear-DockerResources {
    Write-Log "Cleaning Docker Resources / تنظيف موارد Docker" -Level STEP

    Write-Log "Stopping all containers..." -Level INFO
    docker compose down 2>&1 | Out-File -FilePath $BuildLog -Append -Encoding UTF8

    Write-Log "Removing unused images..." -Level INFO
    docker image prune -f 2>&1 | Out-File -FilePath $BuildLog -Append -Encoding UTF8

    Write-Log "Removing unused volumes..." -Level INFO
    docker volume prune -f 2>&1 | Out-File -FilePath $BuildLog -Append -Encoding UTF8

    Write-Log "Cleanup completed" -Level SUCCESS
}

# ═══════════════════════════════════════════════════════════════════════════════
# Summary Generation / إنشاء الملخص
# ═══════════════════════════════════════════════════════════════════════════════
function New-BuildSummary {
    Write-Log "Generating Build Summary / إنشاء ملخص البناء" -Level STEP

    $endTime = Get-Date
    $duration = $endTime - $BuildStartTime

    $summary = @"
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform Build Summary - ملخص بناء منصة سهول
═══════════════════════════════════════════════════════════════════════════════

Build Information:
─────────────────────────────────────────────────────────────────────────────
Build ID:        $Timestamp
Start Time:      $BuildStartTime
End Time:        $endTime
Duration:        $($duration.ToString("hh\:mm\:ss"))
Project Root:    $ProjectRoot
Build Mode:      $Mode

Build Results:
─────────────────────────────────────────────────────────────────────────────
Successful:      $BuildSuccess
Failed:          $BuildFailed
Warnings:        $BuildWarnings

"@

    if ($FailedServices.Count -gt 0) {
        $summary += @"
Failed Services:
─────────────────────────────────────────────────────────────────────────────
"@
        foreach ($service in $FailedServices) {
            $summary += "  - $service`n"
        }
        $summary += "`n"
    }

    $summary += @"
Log Files:
─────────────────────────────────────────────────────────────────────────────
Build Log:       $BuildLog
Error Log:       $ErrorLog
Combined Log:    $CombinedLog
Summary:         $SummaryLog

Running Containers:
─────────────────────────────────────────────────────────────────────────────
"@

    $containers = docker compose ps 2>&1
    $summary += $containers -join "`n"

    $summary += @"

═══════════════════════════════════════════════════════════════════════════════
End of Build Summary
═══════════════════════════════════════════════════════════════════════════════
"@

    # Save summary
    $summary | Out-File -FilePath $SummaryLog -Encoding UTF8
    $summary | Out-File -FilePath $CombinedLog -Append -Encoding UTF8

    # Display summary
    Write-Host ""
    Write-Host $summary
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Function / الدالة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════════
function Main {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "   SAHOOL Platform - Internal Environment Build (PowerShell)" -ForegroundColor Cyan
    Write-Host "   منصة سهول - بناء البيئة الداخلية" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""

    Set-Location $ProjectRoot

    # Initialize logging
    Initialize-Logging
    Write-Log "Build started at $BuildStartTime" -Level INFO
    Write-Log "Project root: $ProjectRoot" -Level INFO
    Write-Log "Logs directory: $LogsDir" -Level INFO
    Write-Log "Build mode: $Mode" -Level INFO

    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Log "Prerequisites check failed. Please fix the issues above and try again." -Level ERROR
        Write-Log "فشل فحص المتطلبات. يرجى إصلاح المشاكل أعلاه والمحاولة مرة أخرى." -Level ERROR
        New-BuildSummary
        exit 1
    }

    # Execute based on mode
    switch ($Mode) {
        "infra" {
            Build-Infrastructure
        }
        "core" {
            Build-Infrastructure
            Build-CoreServices
        }
        "ai" {
            Build-AIServices
        }
        "integration" {
            Build-IntegrationServices
        }
        "all" {
            Build-AllServices
        }
        "health" {
            Test-ServicesHealth
        }
        "logs" {
            Get-AllContainerLogs
        }
        "clean" {
            Clear-DockerResources
        }
    }

    # Post-build tasks
    if ($Mode -notin @("health", "logs", "clean")) {
        Write-Log "Waiting for services to initialize..." -Level INFO
        Start-Sleep -Seconds 15
        Test-ServicesHealth
        Get-AllContainerLogs
    }

    # Generate summary
    New-BuildSummary

    # Final status
    if ($BuildFailed -eq 0) {
        Write-Log "Build completed successfully!" -Level SUCCESS
        Write-Log "اكتمل البناء بنجاح!" -Level SUCCESS
        exit 0
    } else {
        Write-Log "Build completed with $BuildFailed failures" -Level ERROR
        Write-Log "اكتمل البناء مع $BuildFailed فشل" -Level ERROR
        exit 1
    }
}

# Run main function
Main
