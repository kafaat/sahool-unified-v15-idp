# ================================================================================
# Docker Compose Build and Up - One by One
# Builds and starts Docker containers sequentially to avoid resource conflicts
# ================================================================================

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error-Custom { Write-Host $args -ForegroundColor Red }

Write-Info "================================================================================"
Write-Info "           Docker Compose - Build and Up (One by One)                        "
Write-Info "================================================================================"
Write-Host ""

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Error-Custom "ERROR: docker-compose.yml not found in current directory"
    exit 1
}

# Check if docker compose is available
try {
    $null = docker compose version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose not found"
    }
} catch {
    Write-Error-Custom "ERROR: docker compose command not available"
    Write-Error-Custom "Please ensure Docker Desktop is installed and running"
    exit 1
}

# Get list of services from docker-compose.yml
Write-Info "Getting list of services from docker-compose.yml..."
try {
    $serviceOutput = docker compose config --services 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to parse docker-compose.yml: $serviceOutput"
    }
    
    $services = @($serviceOutput | Where-Object { $_ -and $_.Trim() -ne "" -and $_ -notmatch "WARN" })
    
    if ($services.Count -eq 0) {
        Write-Error-Custom "ERROR: No services found in docker-compose.yml"
        exit 1
    }
    
    Write-Success "Found $($services.Count) service(s)"
    Write-Host ""
} catch {
    Write-Error-Custom "ERROR: Failed to get services from docker-compose.yml"
    Write-Error-Custom $_.Exception.Message
    exit 1
}

# ================================================================================
# Phase 1: Build containers (one by one)
# ================================================================================

Write-Info "================================================================================"
Write-Info "PHASE 1: Building containers (--no-cache)"
Write-Info "================================================================================"
Write-Host ""

$buildFailures = @()
$buildCount = 0

foreach ($service in $services) {
    $buildCount++
    Write-Info "[$buildCount/$($services.Count)] Building: $service"
    Write-Host "--------------------------------------------------------------------------------"
    
    try {
        $buildOutput = docker compose build --no-cache $service 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Build failed with exit code $LASTEXITCODE"
        }
        Write-Success "[OK] Successfully built: $service"
    } catch {
        Write-Error-Custom "[FAIL] Failed to build: $service"
        $buildFailures += $service
    }
    
    Write-Host ""
}

# Summary of build phase
Write-Info "================================================================================"
Write-Info "Build Phase Summary"
Write-Info "================================================================================"
Write-Success "Successfully built: $($services.Count - $buildFailures.Count)/$($services.Count)"

if ($buildFailures.Count -gt 0) {
    Write-Warning "Failed builds: $($buildFailures.Count)"
    foreach ($failed in $buildFailures) {
        Write-Warning "  - $failed"
    }
    Write-Host ""
    $continue = Read-Host "Some builds failed. Continue with 'up' phase anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Info "Exiting..."
        exit 1
    }
}
Write-Host ""

# ================================================================================
# Phase 2: Start containers (one by one)
# ================================================================================

Write-Info "================================================================================"
Write-Info "PHASE 2: Starting containers (up -d)"
Write-Info "================================================================================"
Write-Host ""

$upFailures = @()
$upCount = 0

foreach ($service in $services) {
    $upCount++
    Write-Info "[$upCount/$($services.Count)] Starting: $service"
    Write-Host "--------------------------------------------------------------------------------"
    
    try {
        $upOutput = docker compose up -d $service 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Up failed with exit code $LASTEXITCODE"
        }
        Write-Success "[OK] Successfully started: $service"
    } catch {
        Write-Error-Custom "[FAIL] Failed to start: $service"
        $upFailures += $service
    }
    
    Write-Host ""
}

# Final Summary
Write-Info "================================================================================"
Write-Info "Final Summary"
Write-Info "================================================================================"
Write-Success "Builds completed: $($services.Count - $buildFailures.Count)/$($services.Count)"
Write-Success "Containers started: $($services.Count - $upFailures.Count)/$($services.Count)"

if ($buildFailures.Count -gt 0) {
    Write-Warning "Build failures:"
    foreach ($failed in $buildFailures) {
        Write-Warning "  - $failed"
    }
}

if ($upFailures.Count -gt 0) {
    Write-Warning "Start failures:"
    foreach ($failed in $upFailures) {
        Write-Warning "  - $failed"
    }
}

Write-Host ""
Write-Info "Check container status with: docker compose ps"
Write-Info "View logs with: docker compose logs [service-name]"
Write-Host ""

if ($buildFailures.Count -eq 0 -and $upFailures.Count -eq 0) {
    Write-Success "All operations completed successfully!"
    exit 0
} else {
    Write-Warning "Some operations had failures. Review the output above."
    exit 1
}
