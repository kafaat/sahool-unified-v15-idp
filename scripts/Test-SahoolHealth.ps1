<#
.SYNOPSIS
    SAHOOL Platform - Health Check Script
    سكريبت فحص صحة منصة سهول

.DESCRIPTION
    Checks the health status of all SAHOOL services and generates a report.

.PARAMETER OutputFormat
    Output format: Console, JSON, HTML

.PARAMETER ExportPath
    Path to export the health report

.EXAMPLE
    .\Test-SahoolHealth.ps1
    .\Test-SahoolHealth.ps1 -OutputFormat JSON -ExportPath ".\health-report.json"

.NOTES
    Version: 1.0.0
    Author: SAHOOL DevOps Team
#>

[CmdletBinding()]
param(
    [ValidateSet("Console", "JSON", "HTML")]
    [string]$OutputFormat = "Console",

    [string]$ExportPath
)

$script:ProjectRoot = Split-Path -Parent $PSScriptRoot

# ═══════════════════════════════════════════════════════════════════════════════
# Health Check Functions
# ═══════════════════════════════════════════════════════════════════════════════

function Get-ContainerHealth {
    $containers = @()

    $rawContainers = docker ps -a --format "{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}" 2>&1 |
        Where-Object { $_ -match "sahool" }

    foreach ($line in $rawContainers) {
        if ($line -match "^([^|]+)\|([^|]+)\|([^|]+)\|(.*)$") {
            $id = $Matches[1]
            $name = $Matches[2]
            $status = $Matches[3]
            $ports = $Matches[4]

            # Determine health status
            $healthStatus = "unknown"
            if ($status -match "healthy") { $healthStatus = "healthy" }
            elseif ($status -match "unhealthy") { $healthStatus = "unhealthy" }
            elseif ($status -match "starting") { $healthStatus = "starting" }
            elseif ($status -match "Up") { $healthStatus = "running" }
            elseif ($status -match "Exited") { $healthStatus = "stopped" }

            $containers += [PSCustomObject]@{
                ID          = $id
                Name        = $name
                Status      = $status
                Health      = $healthStatus
                Ports       = $ports
                LastChecked = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
    }

    return $containers
}

function Get-ServiceEndpointHealth {
    param([string]$ServiceName, [int]$Port, [string]$HealthPath = "/health")

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port$HealthPath" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        return [PSCustomObject]@{
            Service    = $ServiceName
            Port       = $Port
            StatusCode = $response.StatusCode
            Status     = "Healthy"
            Message    = "Endpoint responding"
        }
    }
    catch {
        return [PSCustomObject]@{
            Service    = $ServiceName
            Port       = $Port
            StatusCode = 0
            Status     = "Unhealthy"
            Message    = $_.Exception.Message
        }
    }
}

function Get-ResourceUsage {
    $stats = docker stats --no-stream --format "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}" 2>&1 |
        Where-Object { $_ -match "sahool" }

    $resources = @()

    foreach ($line in $stats) {
        if ($line -match "^([^|]+)\|([^|]+)\|([^|]+)\|(.*)$") {
            $resources += [PSCustomObject]@{
                Container = $Matches[1]
                CPU       = $Matches[2]
                Memory    = $Matches[3]
                Network   = $Matches[4]
            }
        }
    }

    return $resources
}

function Get-DatabaseHealth {
    Write-Host "`n🗄️  Database Health Check" -ForegroundColor Yellow

    # PostgreSQL
    $pgHealth = docker exec sahool-postgres pg_isready -U sahool 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ PostgreSQL: Ready" -ForegroundColor Green
    } else {
        Write-Host "  ❌ PostgreSQL: Not Ready" -ForegroundColor Red
    }

    # Redis
    $redisHealth = docker exec sahool-redis redis-cli ping 2>&1
    if ($redisHealth -match "PONG") {
        Write-Host "  ✅ Redis: Ready" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Redis: Not Ready" -ForegroundColor Red
    }

    # NATS
    $natsHealth = docker exec sahool-nats nats-server --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ NATS: Running" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  NATS: Status Unknown" -ForegroundColor Yellow
    }
}

function Show-HealthReport {
    param($Containers, $Resources)

    Write-Host "`n═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "   SAHOOL Platform Health Report - تقرير صحة منصة سهول" -ForegroundColor Cyan
    Write-Host "   Generated: $(Get-Date)" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

    # Summary
    $healthy = ($Containers | Where-Object { $_.Health -eq "healthy" }).Count
    $unhealthy = ($Containers | Where-Object { $_.Health -eq "unhealthy" }).Count
    $running = ($Containers | Where-Object { $_.Health -eq "running" }).Count
    $stopped = ($Containers | Where-Object { $_.Health -eq "stopped" }).Count
    $total = $Containers.Count

    Write-Host "`n📊 Summary / الملخص" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "  Total Containers: $total"
    Write-Host "  ✅ Healthy: $healthy" -ForegroundColor Green
    Write-Host "  🔄 Running: $running" -ForegroundColor Blue
    Write-Host "  ❌ Unhealthy: $unhealthy" -ForegroundColor Red
    Write-Host "  ⏹️  Stopped: $stopped" -ForegroundColor Gray

    # Container Details
    Write-Host "`n📦 Container Status / حالة الحاويات" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

    foreach ($container in $Containers | Sort-Object Name) {
        $icon = switch ($container.Health) {
            "healthy"   { "✅" }
            "running"   { "🔄" }
            "unhealthy" { "❌" }
            "starting"  { "⏳" }
            "stopped"   { "⏹️" }
            default     { "❓" }
        }

        $color = switch ($container.Health) {
            "healthy"   { "Green" }
            "running"   { "Blue" }
            "unhealthy" { "Red" }
            "starting"  { "Yellow" }
            "stopped"   { "Gray" }
            default     { "White" }
        }

        Write-Host "  $icon $($container.Name): $($container.Health)" -ForegroundColor $color
    }

    # Resource Usage
    if ($Resources) {
        Write-Host "`n💻 Resource Usage / استخدام الموارد" -ForegroundColor Yellow
        Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
        Write-Host "  Container                          CPU        Memory" -ForegroundColor Gray

        foreach ($resource in $Resources | Sort-Object Container) {
            $name = $resource.Container.PadRight(35)
            Write-Host "  $name $($resource.CPU.PadRight(10)) $($resource.Memory)"
        }
    }

    # Database Health
    Get-DatabaseHealth

    Write-Host "`n═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Export-HealthReportJSON {
    param($Containers, $Resources, $Path)

    $report = @{
        GeneratedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Summary     = @{
            Total     = $Containers.Count
            Healthy   = ($Containers | Where-Object { $_.Health -eq "healthy" }).Count
            Unhealthy = ($Containers | Where-Object { $_.Health -eq "unhealthy" }).Count
            Running   = ($Containers | Where-Object { $_.Health -eq "running" }).Count
            Stopped   = ($Containers | Where-Object { $_.Health -eq "stopped" }).Count
        }
        Containers  = $Containers
        Resources   = $Resources
    }

    $report | ConvertTo-Json -Depth 5 | Out-File -FilePath $Path -Encoding UTF8
    Write-Host "Report exported to: $Path" -ForegroundColor Green
}

function Export-HealthReportHTML {
    param($Containers, $Resources, $Path)

    $html = @"
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>SAHOOL Health Report - تقرير صحة سهول</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        h1 { color: #00d9ff; text-align: center; }
        .summary { display: flex; justify-content: center; gap: 20px; margin: 20px 0; }
        .stat { background: #16213e; padding: 20px; border-radius: 10px; text-align: center; min-width: 100px; }
        .stat.healthy { border-left: 4px solid #00ff88; }
        .stat.unhealthy { border-left: 4px solid #ff4757; }
        .stat.running { border-left: 4px solid #3498db; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #333; }
        th { background: #16213e; color: #00d9ff; }
        tr:hover { background: #16213e; }
        .healthy { color: #00ff88; }
        .unhealthy { color: #ff4757; }
        .running { color: #3498db; }
        .stopped { color: #666; }
    </style>
</head>
<body>
    <h1>🌾 SAHOOL Platform Health Report</h1>
    <h2 style="text-align: center; color: #888;">تقرير صحة منصة سهول</h2>
    <p style="text-align: center;">Generated: $(Get-Date)</p>

    <div class="summary">
        <div class="stat healthy">
            <h3>$(($Containers | Where-Object { $_.Health -eq "healthy" }).Count)</h3>
            <p>Healthy</p>
        </div>
        <div class="stat running">
            <h3>$(($Containers | Where-Object { $_.Health -eq "running" }).Count)</h3>
            <p>Running</p>
        </div>
        <div class="stat unhealthy">
            <h3>$(($Containers | Where-Object { $_.Health -eq "unhealthy" }).Count)</h3>
            <p>Unhealthy</p>
        </div>
    </div>

    <h2>📦 Container Status</h2>
    <table>
        <tr><th>Container</th><th>Status</th><th>Health</th><th>Ports</th></tr>
"@

    foreach ($container in $Containers | Sort-Object Name) {
        $healthClass = $container.Health.ToLower()
        $html += "        <tr><td>$($container.Name)</td><td>$($container.Status)</td><td class='$healthClass'>$($container.Health)</td><td>$($container.Ports)</td></tr>`n"
    }

    $html += @"
    </table>

    <h2>💻 Resource Usage</h2>
    <table>
        <tr><th>Container</th><th>CPU</th><th>Memory</th><th>Network I/O</th></tr>
"@

    foreach ($resource in $Resources | Sort-Object Container) {
        $html += "        <tr><td>$($resource.Container)</td><td>$($resource.CPU)</td><td>$($resource.Memory)</td><td>$($resource.Network)</td></tr>`n"
    }

    $html += @"
    </table>
</body>
</html>
"@

    $html | Out-File -FilePath $Path -Encoding UTF8
    Write-Host "HTML Report exported to: $Path" -ForegroundColor Green
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

Set-Location $ProjectRoot

Write-Host "🔍 Checking SAHOOL services health..." -ForegroundColor Cyan

$containers = Get-ContainerHealth
$resources = Get-ResourceUsage

switch ($OutputFormat) {
    "Console" {
        Show-HealthReport -Containers $containers -Resources $resources
    }
    "JSON" {
        $path = if ($ExportPath) { $ExportPath } else { ".\health-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json" }
        Export-HealthReportJSON -Containers $containers -Resources $resources -Path $path
    }
    "HTML" {
        $path = if ($ExportPath) { $ExportPath } else { ".\health-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').html" }
        Export-HealthReportHTML -Containers $containers -Resources $resources -Path $path
    }
}
