param(
    [switch]$DiagnoseOnly,
    [switch]$ApplyFix,
    [switch]$FullReset
)

$ErrorActionPreference = "Stop"

$repoRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$composeFile = Join-Path $repoRoot "docker-compose-core.yml"
$natsConf = Join-Path $repoRoot "config/nats/nats.conf"

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Cyan
}

function Get-EnvValue {
    param([string]$Name)
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        $envPath = Join-Path $repoRoot ".env"
        if (Test-Path $envPath) {
            $line = Get-Content -Path $envPath | Where-Object { $_ -match "^\s*$Name\s*=" } | Select-Object -First 1
            if ($line) {
                return ($line -split "=", 2)[1].Trim()
            }
        }
        return $null
    }
    return $value
}

function Invoke-Diagnose {
    Write-Section "NATS auth diagnosis"
    if (!(Test-Path $natsConf)) {
        throw "NATS config not found: $natsConf"
    }
    if (!(Test-Path $composeFile)) {
        throw "Compose file not found: $composeFile"
    }

    $conf = Get-Content -Path $natsConf -Raw
    $compose = Get-Content -Path $composeFile -Raw
    $natsPassword = Get-EnvValue "NATS_PASSWORD"

    $checks = @(
        @{ Name = "nats.conf uses password placeholder \${NATS_PASSWORD}"; Pass = $conf -match 'password:\s*\$\{NATS_PASSWORD\}' },
        @{ Name = "nats.conf app user is sahool_app"; Pass = $conf -match 'user:\s*sahool_app' },
        @{ Name = "docker-compose mounts config/nats/nats.conf"; Pass = $compose -match '\./config/nats/nats\.conf:/etc/nats/nats\.conf:ro' },
        @{ Name = "docker-compose exposes NATS_PASSWORD env var"; Pass = $compose -match 'NATS_PASSWORD:\s*\$\{NATS_PASSWORD' },
        @{ Name = ".env has NATS_PASSWORD value"; Pass = -not [string]::IsNullOrWhiteSpace($natsPassword) }
    )

    foreach ($check in $checks) {
        if ($check.Pass) {
            Write-Host "[PASS] $($check.Name)" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] $($check.Name)" -ForegroundColor Red
        }
    }
}

function Invoke-ApplyFix {
    Write-Section "Applying NATS auth hotfix"
    if (!(Test-Path $natsConf)) {
        throw "NATS config not found: $natsConf"
    }

    $conf = Get-Content -Path $natsConf -Raw
    $updated = $conf

    $updated = [regex]::Replace($updated, 'user:\s*\$NATS_USER', 'user: sahool_app')
    $updated = [regex]::Replace($updated, 'password:\s*"\$2b\$11\$yahIlu7zoJPFyaasYqf2BuNmgpSDe237NJ7KJ7joubDOlfF2\.ajwu"', 'password: ${NATS_PASSWORD}')

    if ($updated -ne $conf) {
        Set-Content -Path $natsConf -Value $updated -NoNewline -Encoding UTF8
        Write-Host "Updated: $natsConf" -ForegroundColor Green
    } else {
        Write-Host "No content changes required in $natsConf" -ForegroundColor Yellow
    }
}

function Invoke-FullReset {
    Write-Section "Full reset (NATS + dependent service)"
    Push-Location $repoRoot
    try {
        docker compose -f $composeFile down
        docker volume rm sahool_nats_data 2>$null | Out-Null
        docker volume rm sahool_nats-data 2>$null | Out-Null
        docker compose -f $composeFile up -d nats
        docker compose -f $composeFile up -d notification-service
        docker compose -f $composeFile logs --tail=200 notification-service | Select-String -Pattern "nats|NATS|auth|Authorization"
    }
    finally {
        Pop-Location
    }
}

if (-not ($DiagnoseOnly -or $ApplyFix -or $FullReset)) {
    Write-Host "Usage:"
    Write-Host "  .\fix-nats-auth-v16.ps1 -DiagnoseOnly"
    Write-Host "  .\fix-nats-auth-v16.ps1 -ApplyFix"
    Write-Host "  .\fix-nats-auth-v16.ps1 -FullReset"
    exit 0
}

if ($ApplyFix) {
    Invoke-ApplyFix
}

if ($DiagnoseOnly -or $ApplyFix) {
    Invoke-Diagnose
}

if ($FullReset) {
    Invoke-FullReset
}
