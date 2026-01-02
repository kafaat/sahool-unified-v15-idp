<#
.SYNOPSIS
    SAHOOL Docker Log Analyzer - Analyzes docker-compose logs using Ollama + DeepSeek Coder

.DESCRIPTION
    This script collects logs from all docker-compose services and uses Ollama with
    deepseek-coder model to analyze errors and provide suggested fixes.
    Supports 20+ concurrent agents for parallel analysis.

.PARAMETER Services
    Specific services to analyze (comma-separated). Default: all services

.PARAMETER Lines
    Number of log lines to collect per service. Default: 100

.PARAMETER Parallel
    Number of concurrent analysis agents. Default: 20

.PARAMETER OnlyErrors
    Only analyze services with errors

.PARAMETER OutputFile
    Save analysis report to file

.EXAMPLE
    .\docker-analyze-logs.ps1
    .\docker-analyze-logs.ps1 -Services "postgres,redis,field-ops" -Lines 200
    .\docker-analyze-logs.ps1 -OnlyErrors -Parallel 24 -OutputFile "analysis.md"

.NOTES
    Requires: Docker, docker-compose, Ollama with deepseek-coder model
#>

param(
    [string]$Services = "",
    [int]$Lines = 100,
    [int]$Parallel = 20,
    [switch]$OnlyErrors,
    [string]$OutputFile = ""
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Colors for output
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    $line = "=" * 80
    Write-Host ""
    Write-ColorOutput $line "Cyan"
    Write-ColorOutput "  $Title" "Yellow"
    Write-ColorOutput $line "Cyan"
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "--- $Title ---" "Magenta"
}

# Check Ollama availability
function Test-OllamaConnection {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
        return $true
    }
    catch {
        return $false
    }
}

# Check if deepseek-coder model is available
function Test-DeepSeekModel {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
        $models = $response.models | ForEach-Object { $_.name }
        return $models -match "deepseek-coder"
    }
    catch {
        return $false
    }
}

# Pull deepseek-coder model if not available
function Install-DeepSeekModel {
    Write-ColorOutput "Downloading deepseek-coder:6.7b model..." "Yellow"
    try {
        $body = @{ name = "deepseek-coder:6.7b" } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/pull" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 3600
        Write-ColorOutput "Model downloaded successfully!" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "Failed to download model: $_" "Red"
        return $false
    }
}

# Get all docker-compose services
function Get-DockerServices {
    try {
        $services = docker compose ps --services 2>$null
        if ($LASTEXITCODE -ne 0) {
            $services = docker-compose ps --services 2>$null
        }
        return $services -split "`n" | Where-Object { $_ -ne "" }
    }
    catch {
        Write-ColorOutput "Failed to get docker services: $_" "Red"
        return @()
    }
}

# Get logs for a specific service
function Get-ServiceLogs {
    param([string]$ServiceName, [int]$TailLines)
    try {
        $logs = docker compose logs --tail=$TailLines $ServiceName 2>&1
        if ($LASTEXITCODE -ne 0) {
            $logs = docker-compose logs --tail=$TailLines $ServiceName 2>&1
        }
        return $logs -join "`n"
    }
    catch {
        return "Error getting logs: $_"
    }
}

# Check if logs contain errors
function Test-HasErrors {
    param([string]$Logs)
    $errorPatterns = @(
        "error",
        "Error",
        "ERROR",
        "failed",
        "Failed",
        "FAILED",
        "exception",
        "Exception",
        "EXCEPTION",
        "fatal",
        "Fatal",
        "FATAL",
        "critical",
        "Critical",
        "CRITICAL",
        "panic",
        "Panic",
        "PANIC",
        "refused",
        "timeout",
        "Timeout",
        "TIMEOUT",
        "denied",
        "Denied",
        "DENIED"
    )

    foreach ($pattern in $errorPatterns) {
        if ($Logs -match $pattern) {
            return $true
        }
    }
    return $false
}

# Analyze logs using Ollama
function Invoke-LogAnalysis {
    param([string]$ServiceName, [string]$Logs)

    $prompt = @"
You are a Docker and DevOps expert analyzing logs from the '$ServiceName' container.
Analyze the following logs and provide:
1. A summary of any errors or issues found
2. Root cause analysis for each error
3. Specific suggested fixes with commands or code changes
4. Priority level (Critical/High/Medium/Low) for each issue

If no errors are found, state that the service appears healthy.

LOGS:
$Logs

Provide your analysis in a structured format with clear sections.
"@

    try {
        $body = @{
            model = "deepseek-coder:6.7b"
            prompt = $prompt
            stream = $false
            options = @{
                temperature = 0.3
                num_predict = 2048
            }
        } | ConvertTo-Json -Depth 3

        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 120
        return $response.response
    }
    catch {
        return "Analysis failed: $_"
    }
}

# Main execution
Write-Header "SAHOOL Docker Log Analyzer"
Write-ColorOutput "Powered by Ollama + DeepSeek Coder" "Gray"
Write-Host ""

# Check Ollama
Write-ColorOutput "Checking Ollama connection..." "Yellow"
if (-not (Test-OllamaConnection)) {
    Write-ColorOutput "ERROR: Ollama is not running or not accessible at localhost:11434" "Red"
    Write-ColorOutput "Start Ollama with: docker compose up -d ollama" "Yellow"
    exit 1
}
Write-ColorOutput "Ollama is running" "Green"

# Check model
Write-ColorOutput "Checking deepseek-coder model..." "Yellow"
if (-not (Test-DeepSeekModel)) {
    Write-ColorOutput "Model not found. Installing deepseek-coder:6.7b..." "Yellow"
    if (-not (Install-DeepSeekModel)) {
        Write-ColorOutput "ERROR: Failed to install deepseek-coder model" "Red"
        exit 1
    }
}
Write-ColorOutput "deepseek-coder model is ready" "Green"

# Get services
$allServices = Get-DockerServices
if ($allServices.Count -eq 0) {
    Write-ColorOutput "ERROR: No docker-compose services found" "Red"
    exit 1
}

Write-ColorOutput "Found $($allServices.Count) services" "Cyan"

# Filter services if specified
if ($Services -ne "") {
    $targetServices = $Services -split "," | ForEach-Object { $_.Trim() }
}
else {
    $targetServices = $allServices
}

Write-Host ""
Write-Section "Collecting Logs"

# Collect logs from all services
$serviceData = @{}
foreach ($service in $targetServices) {
    Write-Host "  Collecting logs from: $service" -NoNewline
    $logs = Get-ServiceLogs -ServiceName $service -TailLines $Lines
    $hasErrors = Test-HasErrors -Logs $logs

    if ($OnlyErrors -and -not $hasErrors) {
        Write-ColorOutput " [SKIP - No errors]" "Gray"
        continue
    }

    $serviceData[$service] = @{
        Logs = $logs
        HasErrors = $hasErrors
    }

    if ($hasErrors) {
        Write-ColorOutput " [ERRORS FOUND]" "Red"
    }
    else {
        Write-ColorOutput " [OK]" "Green"
    }
}

if ($serviceData.Count -eq 0) {
    Write-ColorOutput "`nNo services to analyze." "Yellow"
    exit 0
}

Write-Section "Analyzing Logs with DeepSeek Coder ($Parallel concurrent agents)"

# Results storage
$results = @{}
$servicesToAnalyze = [System.Collections.Concurrent.ConcurrentQueue[string]]::new()
foreach ($service in $serviceData.Keys) {
    $servicesToAnalyze.Enqueue($service)
}

# Progress tracking
$totalServices = $serviceData.Count
$completedServices = 0

# Analyze services with parallel execution (throttled)
$jobs = @()
$runspacePool = [runspacefactory]::CreateRunspacePool(1, $Parallel)
$runspacePool.Open()

foreach ($service in $serviceData.Keys) {
    $powershell = [powershell]::Create().AddScript({
        param($ServiceName, $Logs)

        $prompt = @"
You are a Docker and DevOps expert analyzing logs from the '$ServiceName' container.
Analyze the following logs and provide:
1. ERRORS FOUND: List each error with line reference
2. ROOT CAUSE: Explain why each error occurred
3. FIXES: Specific commands or code changes to fix each issue
4. PRIORITY: Critical/High/Medium/Low for each issue

If no errors are found, state: "SERVICE HEALTHY - No issues detected"

Format your response as:
## $ServiceName Analysis

### Errors Found
- [Error 1 description]
- [Error 2 description]

### Root Cause Analysis
1. [Cause for Error 1]
2. [Cause for Error 2]

### Suggested Fixes
1. [Fix for Error 1 with command/code]
2. [Fix for Error 2 with command/code]

### Priority
- Error 1: [Priority Level]
- Error 2: [Priority Level]

LOGS:
$Logs
"@

        try {
            $body = @{
                model = "deepseek-coder:6.7b"
                prompt = $prompt
                stream = $false
                options = @{
                    temperature = 0.3
                    num_predict = 2048
                }
            } | ConvertTo-Json -Depth 3

            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 180
            return @{
                Service = $ServiceName
                Analysis = $response.response
                Success = $true
            }
        }
        catch {
            return @{
                Service = $ServiceName
                Analysis = "Analysis failed: $_"
                Success = $false
            }
        }
    }).AddArgument($service).AddArgument($serviceData[$service].Logs)

    $powershell.RunspacePool = $runspacePool
    $jobs += @{
        PowerShell = $powershell
        Handle = $powershell.BeginInvoke()
        Service = $service
    }
}

# Wait for all jobs to complete and collect results
Write-Host ""
foreach ($job in $jobs) {
    Write-Host "  Analyzing: $($job.Service)" -NoNewline
    try {
        $result = $job.PowerShell.EndInvoke($job.Handle)
        $results[$job.Service] = $result
        if ($result.Success) {
            Write-ColorOutput " [DONE]" "Green"
        }
        else {
            Write-ColorOutput " [FAILED]" "Red"
        }
    }
    catch {
        Write-ColorOutput " [ERROR: $_]" "Red"
        $results[$job.Service] = @{
            Service = $job.Service
            Analysis = "Analysis error: $_"
            Success = $false
        }
    }
    finally {
        $job.PowerShell.Dispose()
    }
}

$runspacePool.Close()
$runspacePool.Dispose()

# Generate report
Write-Header "Analysis Report"

$report = @"
# SAHOOL Docker Log Analysis Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Services Analyzed: $($results.Count)

"@

# Services with errors first
$errorServices = $results.Keys | Where-Object { $serviceData[$_].HasErrors }
$healthyServices = $results.Keys | Where-Object { -not $serviceData[$_].HasErrors }

if ($errorServices.Count -gt 0) {
    $report += "`n## Services with Errors ($($errorServices.Count))`n"
    Write-Section "Services with Errors"

    foreach ($service in $errorServices) {
        $result = $results[$service]
        Write-Host ""
        Write-ColorOutput "### $service" "Red"
        Write-Host $result.Analysis

        $report += "`n### $service`n"
        $report += "$($result.Analysis)`n"
        $report += "`n---`n"
    }
}

if ($healthyServices.Count -gt 0) {
    $report += "`n## Healthy Services ($($healthyServices.Count))`n"
    Write-Section "Healthy Services"

    foreach ($service in $healthyServices) {
        $result = $results[$service]
        Write-Host ""
        Write-ColorOutput "### $service" "Green"
        Write-Host $result.Analysis

        $report += "`n### $service`n"
        $report += "$($result.Analysis)`n"
        $report += "`n---`n"
    }
}

# Summary
$summary = @"

## Summary
- Total Services Analyzed: $($results.Count)
- Services with Errors: $($errorServices.Count)
- Healthy Services: $($healthyServices.Count)
- Analysis Engine: Ollama + DeepSeek Coder 6.7B
- Concurrent Agents Used: $Parallel

"@

$report += $summary
Write-Header "Summary"
Write-ColorOutput "Total Services Analyzed: $($results.Count)" "Cyan"
Write-ColorOutput "Services with Errors: $($errorServices.Count)" $(if ($errorServices.Count -gt 0) { "Red" } else { "Green" })
Write-ColorOutput "Healthy Services: $($healthyServices.Count)" "Green"

# Save to file if specified
if ($OutputFile -ne "") {
    $report | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Host ""
    Write-ColorOutput "Report saved to: $OutputFile" "Yellow"
}

Write-Host ""
Write-ColorOutput "Analysis complete!" "Green"
