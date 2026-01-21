<#
.SYNOPSIS
    SAHOOL Platform - Frontend & Mobile Diagnostic Tool
    أداة تشخيص الواجهات والتطبيق المحمول لمنصة سهول

.DESCRIPTION
    Comprehensive diagnostics for:
    - Web Dashboard (Next.js/React)
    - Admin Portal (React)
    - Shared Packages (TypeScript)
    - Mobile App (Flutter/Dart)

.PARAMETER Fix
    Apply automatic fixes where possible

.PARAMETER Web
    Run web frontend diagnostics only

.PARAMETER Mobile
    Run mobile app diagnostics only

.EXAMPLE
    .\scripts\diagnose-frontend.ps1
    .\scripts\diagnose-frontend.ps1 -Fix
    .\scripts\diagnose-frontend.ps1 -Mobile -Fix

.NOTES
    Author: SAHOOL Platform Team
    Version: 1.0.0
#>

param(
    [switch]$Fix,
    [switch]$Web,
    [switch]$Mobile,
    [switch]$All
)

# If no specific flag, run all
if (-not $Web -and -not $Mobile) {
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

function Test-Directory($path) {
    return Test-Path $path -PathType Container
}

function Test-Command($cmd) {
    return $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

# Start
$startTime = Get-Date

Write-Host @"

═══════════════════════════════════════════════════════════════════════════════
   🔍 SAHOOL Frontend & Mobile Diagnostic Suite
   أداة تشخيص الواجهات والتطبيق المحمول
═══════════════════════════════════════════════════════════════════════════════

"@ -ForegroundColor Cyan

# ═══════════════════════════════════════════════════════════════════════════════
# Web Frontend Diagnostics
# ═══════════════════════════════════════════════════════════════════════════════
if ($All -or $Web) {

    # Web Dashboard
    if (Test-Directory "apps/web") {
        Write-Header "🌐 Web Dashboard | لوحة القيادة"

        Push-Location "apps/web"

        Write-SubHeader "ESLint - فحص الكود"
        if ($Fix) {
            npm run lint -- --fix 2>$null
        } else {
            npm run lint 2>$null
        }

        Write-SubHeader "TypeScript - فحص الأنواع"
        npx tsc --noEmit 2>$null

        Pop-Location
    } else {
        Write-Warning "apps/web غير موجود"
    }

    # Admin Portal
    if (Test-Directory "apps/admin") {
        Write-Header "👤 Admin Portal | بوابة الإدارة"

        Push-Location "apps/admin"

        Write-SubHeader "ESLint - فحص الكود"
        if ($Fix) {
            npm run lint -- --fix 2>$null
        } else {
            npm run lint 2>$null
        }

        Write-SubHeader "TypeScript - فحص الأنواع"
        npx tsc --noEmit 2>$null

        Pop-Location
    } else {
        Write-Warning "apps/admin غير موجود"
    }

    # Shared Packages
    Write-Header "📦 Shared Packages | الحزم المشتركة"

    $packages = @(
        "packages/shared-ui",
        "packages/shared-utils",
        "packages/shared-types",
        "packages/shared-hooks",
        "packages/api-client",
        "packages/design-system"
    )

    foreach ($pkg in $packages) {
        if (Test-Directory $pkg) {
            Write-SubHeader "$pkg - فحص"
            Push-Location $pkg
            npm run lint --if-present 2>$null
            Pop-Location
        }
    }

    # Frontend Tests
    Write-Header "🧪 Frontend Tests | اختبارات الواجهات"
    Write-SubHeader "Vitest - الاختبارات"
    npm run test --workspaces --if-present 2>$null
}

# ═══════════════════════════════════════════════════════════════════════════════
# Mobile App Diagnostics (Flutter)
# ═══════════════════════════════════════════════════════════════════════════════
if ($All -or $Mobile) {

    if (Test-Directory "apps/mobile") {

        # Check Flutter is installed
        if (-not (Test-Command "flutter")) {
            Write-Error "Flutter غير مثبت - يرجى تثبيت Flutter SDK"
            Write-Host "https://docs.flutter.dev/get-started/install" -ForegroundColor Yellow
        } else {

            Push-Location "apps/mobile"

            # Flutter Analyze
            Write-Header "📱 Mobile App Analysis | تحليل التطبيق المحمول"
            Write-SubHeader "Dart Analyzer - تحليل الكود"
            flutter analyze

            # Flutter Format
            Write-Header "🎨 Mobile Code Formatting | تنسيق الكود"
            if ($Fix) {
                Write-SubHeader "Dart Format - تنسيق"
                dart format .
            } else {
                Write-SubHeader "Dart Format - فحص التنسيق"
                dart format --set-exit-if-changed . 2>$null
            }

            # Flutter Fix (only if -Fix flag)
            if ($Fix) {
                Write-Header "🔧 Mobile Auto-Fix | الإصلاح التلقائي"
                Write-SubHeader "Dart Fix - إصلاح تلقائي"
                dart fix --apply
            }

            # Flutter Tests
            Write-Header "🧪 Mobile Tests | اختبارات التطبيق"
            Write-SubHeader "Flutter Test - الاختبارات"
            flutter test

            # Dependency Check
            Write-Header "📋 Mobile Dependencies | التبعيات"
            Write-SubHeader "Outdated Packages - الحزم القديمة"
            flutter pub outdated

            Pop-Location
        }
    } else {
        Write-Warning "apps/mobile غير موجود"
    }

    # Check for sahool_field_app
    if (Test-Directory "apps/mobile/sahool_field_app") {
        Write-Header "📱 SAHOOL Field App | تطبيق سهول الميداني"

        Push-Location "apps/mobile/sahool_field_app"

        if (Test-Command "flutter") {
            Write-SubHeader "Flutter Analyze"
            flutter analyze

            if ($Fix) {
                Write-SubHeader "Dart Fix"
                dart fix --apply
            }
        }

        Pop-Location
    }
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

# Quick Commands Summary
Write-Host @"
═══════════════════════════════════════════════════════════════════════════════
   📋 Quick Commands | أوامر سريعة
═══════════════════════════════════════════════════════════════════════════════

   Web Frontend:
   ─────────────
   cd apps/web && npm run lint --fix     # إصلاح ESLint
   cd apps/web && npx tsc --noEmit       # فحص TypeScript
   npm run test --workspace=apps/web     # تشغيل الاختبارات

   Mobile App:
   ───────────
   cd apps/mobile && flutter analyze     # تحليل الكود
   cd apps/mobile && dart fix --apply    # إصلاح تلقائي
   cd apps/mobile && flutter test        # تشغيل الاختبارات
   cd apps/mobile && flutter pub upgrade # تحديث التبعيات

"@ -ForegroundColor Cyan
