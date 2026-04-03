#!/usr/bin/env pwsh
# SAHOOL Health Check - All Services
$services = @(
    @{Name="nats"; Url="http://localhost:8222/healthz"},
    @{Name="user-service"; Url="http://localhost:3025/healthz"},
    @{Name="field-service"; Url="http://localhost:3000/healthz"},
    @{Name="ai-advisor"; Url="http://localhost:8112/healthz"},
    @{Name="notification"; Url="http://localhost:8110/healthz"}
)

Write-Host "SAHOOL Health Check" -ForegroundColor Cyan
foreach ($svc in $services) {
    $status = "DOWN"
    $color = "Red"
    try {
        $null = Invoke-RestMethod -Uri $svc.Url -TimeoutSec 5 -ErrorAction Stop
        $status = "UP"; $color = "Green"
    } catch {
        # Log the failure reason at verbose level for troubleshooting
        Write-Verbose "Health check failed for $($svc.Name) ($($svc.Url)): $($_.Exception.Message)"
    }
    Write-Host "$($svc.Name): $status" -ForegroundColor $color
}
