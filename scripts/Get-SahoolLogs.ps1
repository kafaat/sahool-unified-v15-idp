<#
.SYNOPSIS
    SAHOOL Platform - Log Collection and Analysis Script
    سكريبت جمع وتحليل سجلات منصة سهول

.DESCRIPTION
    Collects, analyzes, and exports logs from all SAHOOL services.
    Detects errors, warnings, and common issues automatically.

.PARAMETER Service
    Specific service to collect logs from (optional)

.PARAMETER Lines
    Number of lines to collect per service (default: 500)

.PARAMETER AnalyzeErrors
    Analyze logs for common errors

.PARAMETER ExportPath
    Directory to export logs

.PARAMETER Follow
    Follow logs in real-time (like tail -f)

.EXAMPLE
    .\Get-SahoolLogs.ps1
    .\Get-SahoolLogs.ps1 -Service yield-prediction-service -Lines 1000
    .\Get-SahoolLogs.ps1 -AnalyzeErrors -ExportPath ".\logs-export"

.NOTES
    Version: 1.0.0
    Author: SAHOOL DevOps Team
#>

[CmdletBinding()]
param(
    [string]$Service,
    [int]$Lines = 500,
    [switch]$AnalyzeErrors,
    [string]$ExportPath,
    [switch]$Follow,
    [switch]$ErrorsOnly
)

$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Common error patterns to detect
$script:ErrorPatterns = @(
    @{ Pattern = "Cannot find module"; Category = "MISSING_DEPENDENCY"; Severity = "Critical"; Solution = "Run npm install or check package.json" }
    @{ Pattern = "reflect-metadata"; Category = "NESTJS_BOOTSTRAP"; Severity = "Critical"; Solution = "Add reflect-metadata to dependencies and import it first in main.ts" }
    @{ Pattern = "ECONNREFUSED"; Category = "CONNECTION_ERROR"; Severity = "High"; Solution = "Check if the target service is running" }
    @{ Pattern = "ENOTFOUND"; Category = "DNS_ERROR"; Severity = "High"; Solution = "Check network configuration and DNS" }
    @{ Pattern = "ETIMEDOUT"; Category = "TIMEOUT_ERROR"; Severity = "Medium"; Solution = "Increase timeout or check network" }
    @{ Pattern = "Error: connect"; Category = "CONNECTION_ERROR"; Severity = "High"; Solution = "Check database/service connectivity" }
    @{ Pattern = "UnauthorizedError"; Category = "AUTH_ERROR"; Severity = "Medium"; Solution = "Check JWT configuration" }
    @{ Pattern = "FATAL"; Category = "FATAL_ERROR"; Severity = "Critical"; Solution = "Check error details" }
    @{ Pattern = "OOMKilled"; Category = "MEMORY_ERROR"; Severity = "Critical"; Solution = "Increase container memory limit" }
    @{ Pattern = "permission denied"; Category = "PERMISSION_ERROR"; Severity = "High"; Solution = "Check file/directory permissions" }
    @{ Pattern = "ENOENT"; Category = "FILE_NOT_FOUND"; Severity = "Medium"; Solution = "Check file paths" }
    @{ Pattern = "SyntaxError"; Category = "CODE_ERROR"; Severity = "Critical"; Solution = "Fix JavaScript/TypeScript syntax" }
    @{ Pattern = "TypeError"; Category = "CODE_ERROR"; Severity = "High"; Solution = "Fix type-related code issues" }
    @{ Pattern = "ReferenceError"; Category = "CODE_ERROR"; Severity = "High"; Solution = "Fix undefined variable references" }
    @{ Pattern = "prisma"; Category = "DATABASE_ERROR"; Severity = "High"; Solution = "Check Prisma schema and migrations" }
    @{ Pattern = "duplicate key"; Category = "DATABASE_ERROR"; Severity = "Medium"; Solution = "Handle unique constraint violations" }
    @{ Pattern = "relation .* does not exist"; Category = "DATABASE_ERROR"; Severity = "Critical"; Solution = "Run database migrations" }
)

# ═══════════════════════════════════════════════════════════════════════════════
# Functions
# ═══════════════════════════════════════════════════════════════════════════════

function Get-AllContainers {
    $containers = docker ps -a --format "{{.Names}}" 2>&1 | Where-Object { $_ -match "sahool" }
    return $containers
}

function Get-ContainerLogs {
    param(
        [string]$ContainerName,
        [int]$TailLines = 500
    )

    Write-Host "📋 Collecting logs from $ContainerName..." -ForegroundColor Cyan

    $logs = docker logs --tail $TailLines --timestamps $ContainerName 2>&1

    return [PSCustomObject]@{
        Container = $ContainerName
        Logs      = $logs
        Timestamp = Get-Date
    }
}

function Find-ErrorsInLogs {
    param([string[]]$LogLines, [string]$ContainerName)

    $errors = @()

    foreach ($line in $LogLines) {
        foreach ($pattern in $ErrorPatterns) {
            if ($line -match $pattern.Pattern) {
                $errors += [PSCustomObject]@{
                    Container = $ContainerName
                    Category  = $pattern.Category
                    Severity  = $pattern.Severity
                    Solution  = $pattern.Solution
                    Line      = $line.Trim()
                    Pattern   = $pattern.Pattern
                }
                break  # Only match first pattern per line
            }
        }

        # Generic error detection
        if ($line -match "\[ERROR\]|ERROR:|error:|Exception:|EXCEPTION:") {
            if (-not ($errors | Where-Object { $_.Line -eq $line.Trim() })) {
                $errors += [PSCustomObject]@{
                    Container = $ContainerName
                    Category  = "GENERIC_ERROR"
                    Severity  = "Medium"
                    Solution  = "Review error message"
                    Line      = $line.Trim()
                    Pattern   = "Generic Error"
                }
            }
        }
    }

    return $errors
}

function Show-ErrorAnalysis {
    param($Errors)

    if ($Errors.Count -eq 0) {
        Write-Host "`n✅ No critical errors detected!" -ForegroundColor Green
        return
    }

    Write-Host "`n═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "   ⚠️  Error Analysis Report - تقرير تحليل الأخطاء" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Red

    # Group by severity
    $critical = $Errors | Where-Object { $_.Severity -eq "Critical" }
    $high = $Errors | Where-Object { $_.Severity -eq "High" }
    $medium = $Errors | Where-Object { $_.Severity -eq "Medium" }

    Write-Host "`n📊 Summary:" -ForegroundColor Yellow
    Write-Host "  🔴 Critical: $($critical.Count)" -ForegroundColor Red
    Write-Host "  🟠 High: $($high.Count)" -ForegroundColor DarkYellow
    Write-Host "  🟡 Medium: $($medium.Count)" -ForegroundColor Yellow

    # Group by category
    $byCategory = $Errors | Group-Object -Property Category

    Write-Host "`n📁 Errors by Category:" -ForegroundColor Yellow
    foreach ($cat in $byCategory | Sort-Object Count -Descending) {
        Write-Host "  $($cat.Name): $($cat.Count)" -ForegroundColor White
    }

    # Show critical errors in detail
    if ($critical.Count -gt 0) {
        Write-Host "`n🔴 Critical Errors (Require Immediate Action):" -ForegroundColor Red
        Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

        $criticalUnique = $critical | Select-Object Container, Category, Solution -Unique

        foreach ($error in $criticalUnique) {
            Write-Host "`n  Container: $($error.Container)" -ForegroundColor White
            Write-Host "  Category:  $($error.Category)" -ForegroundColor Red
            Write-Host "  Solution:  $($error.Solution)" -ForegroundColor Green
        }
    }

    # Show high errors
    if ($high.Count -gt 0) {
        Write-Host "`n🟠 High Priority Errors:" -ForegroundColor DarkYellow
        Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray

        $highUnique = $high | Select-Object Container, Category, Solution -Unique | Select-Object -First 5

        foreach ($error in $highUnique) {
            Write-Host "  [$($error.Container)] $($error.Category): $($error.Solution)" -ForegroundColor DarkYellow
        }
    }

    Write-Host "`n═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Red
}

function Export-Logs {
    param($AllLogs, $AllErrors, [string]$Path)

    $exportDir = if ($Path) { $Path } else { Join-Path $ProjectRoot "logs\export_$Timestamp" }

    if (-not (Test-Path $exportDir)) {
        New-Item -ItemType Directory -Path $exportDir -Force | Out-Null
    }

    Write-Host "`n📁 Exporting logs to: $exportDir" -ForegroundColor Cyan

    # Export individual container logs
    foreach ($log in $AllLogs) {
        $logFile = Join-Path $exportDir "$($log.Container).log"
        $log.Logs | Out-File -FilePath $logFile -Encoding UTF8
        Write-Host "  ✅ $($log.Container).log" -ForegroundColor Green
    }

    # Export error analysis
    if ($AllErrors.Count -gt 0) {
        $errorFile = Join-Path $exportDir "error_analysis.json"
        $AllErrors | ConvertTo-Json -Depth 5 | Out-File -FilePath $errorFile -Encoding UTF8
        Write-Host "  ✅ error_analysis.json" -ForegroundColor Green

        # Create error summary
        $summaryFile = Join-Path $exportDir "error_summary.txt"
        $summary = @"
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Error Summary - ملخص أخطاء سهول
Generated: $(Get-Date)
═══════════════════════════════════════════════════════════════════════════════

Total Errors: $($AllErrors.Count)
Critical: $(($AllErrors | Where-Object { $_.Severity -eq "Critical" }).Count)
High: $(($AllErrors | Where-Object { $_.Severity -eq "High" }).Count)
Medium: $(($AllErrors | Where-Object { $_.Severity -eq "Medium" }).Count)

By Container:
─────────────────────────────────────────────────────────────────
$($AllErrors | Group-Object Container | ForEach-Object { "  $($_.Name): $($_.Count) errors" } | Out-String)

By Category:
─────────────────────────────────────────────────────────────────
$($AllErrors | Group-Object Category | Sort-Object Count -Descending | ForEach-Object { "  $($_.Name): $($_.Count)" } | Out-String)

═══════════════════════════════════════════════════════════════════════════════
"@
        $summary | Out-File -FilePath $summaryFile -Encoding UTF8
        Write-Host "  ✅ error_summary.txt" -ForegroundColor Green
    }

    Write-Host "`n✅ Export completed: $exportDir" -ForegroundColor Green
}

function Watch-Logs {
    param([string]$ContainerName)

    Write-Host "👀 Following logs for $ContainerName (Press Ctrl+C to stop)..." -ForegroundColor Cyan

    if ($ErrorsOnly) {
        docker logs -f --tail 50 $ContainerName 2>&1 | ForEach-Object {
            if ($_ -match "error|Error|ERROR|Exception|FATAL|fail|Fail|FAIL") {
                Write-Host $_ -ForegroundColor Red
            }
        }
    } else {
        docker logs -f --tail 50 $ContainerName 2>&1 | ForEach-Object {
            if ($_ -match "error|Error|ERROR|Exception|FATAL") {
                Write-Host $_ -ForegroundColor Red
            }
            elseif ($_ -match "warn|Warn|WARN") {
                Write-Host $_ -ForegroundColor Yellow
            }
            else {
                Write-Host $_
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

Set-Location $ProjectRoot

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   SAHOOL Platform Log Collector - جامع سجلات منصة سهول" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Follow mode
if ($Follow) {
    if ($Service) {
        Watch-Logs -ContainerName "sahool-$Service"
    } else {
        Write-Host "❌ Please specify a service with -Service parameter for follow mode" -ForegroundColor Red
        exit 1
    }
    exit 0
}

# Get containers
$containers = if ($Service) {
    @("sahool-$Service")
} else {
    Get-AllContainers
}

if ($containers.Count -eq 0) {
    Write-Host "❌ No SAHOOL containers found running" -ForegroundColor Red
    exit 1
}

Write-Host "`n📦 Found $($containers.Count) SAHOOL containers" -ForegroundColor Green

# Collect logs
$allLogs = @()
$allErrors = @()

foreach ($container in $containers) {
    $logData = Get-ContainerLogs -ContainerName $container -TailLines $Lines
    $allLogs += $logData

    if ($AnalyzeErrors -or $ErrorsOnly) {
        $logLines = $logData.Logs -split "`n"
        $errors = Find-ErrorsInLogs -LogLines $logLines -ContainerName $container
        $allErrors += $errors
    }
}

# Show error analysis
if ($AnalyzeErrors -or $ErrorsOnly) {
    Show-ErrorAnalysis -Errors $allErrors
}

# Export if requested
if ($ExportPath -or $AnalyzeErrors) {
    Export-Logs -AllLogs $allLogs -AllErrors $allErrors -Path $ExportPath
}

Write-Host "`n✅ Log collection completed!" -ForegroundColor Green
