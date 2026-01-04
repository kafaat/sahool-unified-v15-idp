# ═══════════════════════════════════════════════════════════════════════════
# SAHOOL Mobile App - Code Generation Script (Windows)
# سكريبت توليد الكود لتطبيق سهول الموبايل
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        SAHOOL Mobile App - Code Generation                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Check if Flutter is installed
$flutterPath = Get-Command flutter -ErrorAction SilentlyContinue
if (-not $flutterPath) {
    Write-Host "❌ Flutter is not installed" -ForegroundColor Red
    Write-Host "Please install Flutter from https://flutter.dev"
    exit 1
}

# Navigate to mobile app directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\.."

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
flutter pub get

Write-Host ""
Write-Host "🔧 Generating code with build_runner..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..."

# Run build_runner
flutter pub run build_runner build --delete-conflicting-outputs

Write-Host ""
Write-Host "🌐 Generating localization files..." -ForegroundColor Yellow
flutter gen-l10n

Write-Host ""
Write-Host "✅ Code generation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Generated files:"
Write-Host "  - *.freezed.dart (Freezed models)"
Write-Host "  - *.g.dart (JSON serialization)"
Write-Host "  - lib/generated/l10n/ (Localization)"
Write-Host ""
Write-Host "You can now run the app with:"
Write-Host "  flutter run"
