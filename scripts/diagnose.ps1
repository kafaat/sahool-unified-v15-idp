<#
.SYNOPSIS
    SAHOOL Platform - Comprehensive Diagnostic Tool
    أداة التشخيص الشاملة لمنصة سهول

.DESCRIPTION
    Runs comprehensive diagnostics on the SAHOOL platform including:
    - Python linting and type checking
    - JavaScript/TypeScript analysis
    - Security scanning
    - Infrastructure validation

.PARAMETER Fix
    Apply automatic fixes where possible

.PARAMETER Python
    Run Python diagnostics only

.PARAMETER JavaScript
    Run JavaScript/TypeScript diagnostics only

.PARAMETER Security
    Run security diagnostics only

.EXAMPLE
    .\scripts\diagnose.ps1
    .\scripts\diagnose.ps1 -Fix
    .\scripts\diagnose.ps1 -Python -Fix

.NOTES
    Author: SAHOOL Platform Team
    Version: 1.0.0
#>

param(
    [switch]$Fix,
    [switch]$Python,
    [switch]$JavaScript,
    [switch]$Security,
    [switch]$All
)

# If no specific flag, run all
if (-not $Python -and -not $JavaScript -and -not $Security) {
    $All = $true
}

$ErrorActionPreference = "Continue"

# Colors
function Write-Header($text) {
    Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "   $text" -ForegroundColor White
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-SubHeader($text) {
    Write-Host "`n▶ $text" -ForegroundColor Magenta
}

function Write-Success($text) {
    Write-Host "✅ $text" -ForegroundColor Green
}

function Write-Warning($text) {
    Write-Host "⚠️ $text" -ForegroundColor Yellow
}

function Write-Error($text) {
    Write-Host "❌ $text" -ForegroundColor Red
}

function Test-Command($cmd) {
    return $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

# Start
$startTime = Get-Date

Write-Host @"

═══════════════════════════════════════════════════════════════════════════════
   🔍 SAHOOL Platform Diagnostic Suite | أداة تشخيص منصة سهول
═══════════════════════════════════════════════════════════════════════════════

"@ -ForegroundColor Cyan

# Python Diagnostics
if ($All -or $Python) {
    Write-Header "🐍 Python Diagnostics | تشخيص Python"

    # Ruff
    Write-SubHeader "Ruff - فحص وتنسيق Python"
    if (Test-Command "ruff") {
        if ($Fix) {
            ruff check --fix --unsafe-fixes apps/ shared/
            ruff format apps/ shared/
        } else {
            ruff check apps/ shared/
        }
    } else {
        Write-Warning "ruff غير مثبت - pip install ruff"
    }

    # Pyright
    Write-SubHeader "Pyright - فحص الأنواع"
    if (Test-Command "pyright") {
        pyright shared/ai/
    } else {
        Write-Warning "pyright غير مثبت - pip install pyright"
    }

    # Bandit
    Write-SubHeader "Bandit - فحص أمني"
    if (Test-Command "bandit") {
        bandit -r shared/ apps/services/ -ll -q
    } else {
        Write-Warning "bandit غير مثبت - pip install bandit"
    }

    # Vulture
    Write-SubHeader "Vulture - كشف الكود الميت"
    if (Test-Command "vulture") {
        vulture shared/ apps/kernel/ --min-confidence 90
    } else {
        Write-Warning "vulture غير مثبت - pip install vulture"
    }
}

# JavaScript/TypeScript Diagnostics
if ($All -or $JavaScript) {
    Write-Header "📦 JavaScript/TypeScript Diagnostics | تشخيص JS/TS"

    # oxlint
    Write-SubHeader "oxlint - فحص سريع"
    npx oxlint .

    # TypeScript
    Write-SubHeader "TypeScript - فحص الأنواع"
    npx tsc --noEmit 2>$null

    # Knip
    Write-SubHeader "Knip - كشف الكود الميت"
    npx knip 2>$null

    # Biome
    if ($Fix) {
        Write-SubHeader "Biome - فحص وإصلاح"
        npx biome check --apply .
    }
}

# Security Diagnostics
if ($All -or $Security) {
    Write-Header "🔐 Security Diagnostics | التشخيص الأمني"

    # npm audit
    Write-SubHeader "npm audit - فحص أمني Node.js"
    npm audit --audit-level=moderate

    # Safety
    Write-SubHeader "Safety - فحص أمني Python"
    if (Test-Command "safety") {
        safety check
    } else {
        Write-Warning "safety غير مثبت - pip install safety"
    }
}

# Infrastructure Diagnostics
if ($All) {
    Write-Header "🐳 Infrastructure Diagnostics | تشخيص البنية التحتية"

    # Docker Compose
    Write-SubHeader "Docker Compose - فحص التكوين"
    docker compose config --quiet
    if ($?) {
        Write-Success "Docker Compose configuration is valid"
    }

    # Container Status
    Write-SubHeader "Container Status - حالة الحاويات"
    docker compose ps
}

# Summary
$duration = ((Get-Date) - $startTime).TotalSeconds

Write-Host @"

═══════════════════════════════════════════════════════════════════════════════
   ✅ Diagnostic Complete | اكتمل التشخيص
   ⏱️  Duration: $([math]::Round($duration, 2))s | المدة: $([math]::Round($duration, 2)) ثانية
═══════════════════════════════════════════════════════════════════════════════

"@ -ForegroundColor Green

if ($Fix) {
    Write-Host "تم تطبيق الإصلاحات التلقائية. راجع التغييرات قبل الـ commit." -ForegroundColor Yellow
}
