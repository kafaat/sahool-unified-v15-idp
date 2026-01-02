<#
═══════════════════════════════════════════════════════════════════════════════
SAHOOL Platform - Image Optimization Script
سكريبت تحسين الصور وتحويلها إلى WebP

Usage:
    .\scripts\optimize-images.ps1
    .\scripts\optimize-images.ps1 -InputPath "apps/mobile/assets/images"
    .\scripts\optimize-images.ps1 -Quality 90 -KeepOriginals

Requirements:
    - ImageMagick (https://imagemagick.org/script/download.php)
    - Or: choco install imagemagick

═══════════════════════════════════════════════════════════════════════════════
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$InputPath = "assets/images",

    [Parameter(Mandatory=$false)]
    [ValidateRange(1, 100)]
    [int]$Quality = 85,

    [Parameter(Mandatory=$false)]
    [switch]$KeepOriginals = $false,

    [Parameter(Mandatory=$false)]
    [switch]$Recursive = $true,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false,

    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ""
)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$InputFullPath = Join-Path $ProjectRoot $InputPath

# Statistics
$script:TotalFiles = 0
$script:ConvertedFiles = 0
$script:SkippedFiles = 0
$script:TotalSavedBytes = 0
$script:Errors = @()

# Supported image formats
$SupportedFormats = @(".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif")

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────
function Write-Banner {
    Write-Host @"

═══════════════════════════════════════════════════════════════════════════════
    _____ ___    _   _  ___   ___  _
   / ___// _ \  | | | |/ _ \ / _ \| |
   \___ \ /_\ \ | |_| | | | | | | | |
    ___) / ___ \|  _  | |_| | |_| | |___
   |____/_/   \_\_| |_|\___/ \___/|_____|

   IMAGE OPTIMIZER - تحسين الصور
   Converting to WebP with $Quality% quality
═══════════════════════════════════════════════════════════════════════════════

"@ -ForegroundColor Cyan
}

function Test-ImageMagick {
    try {
        $null = magick -version 2>&1
        return $true
    } catch {
        try {
            $null = convert -version 2>&1
            return $true
        } catch {
            return $false
        }
    }
}

function Get-ImageMagickCommand {
    try {
        $null = magick -version 2>&1
        return "magick"
    } catch {
        return "convert"
    }
}

function Format-FileSize {
    param([long]$Bytes)

    if ($Bytes -ge 1MB) {
        return "{0:N2} MB" -f ($Bytes / 1MB)
    } elseif ($Bytes -ge 1KB) {
        return "{0:N2} KB" -f ($Bytes / 1KB)
    } else {
        return "$Bytes bytes"
    }
}

function Convert-ToWebP {
    param(
        [string]$SourceFile,
        [string]$DestFile,
        [int]$Quality
    )

    $cmd = Get-ImageMagickCommand
    $sourceSize = (Get-Item $SourceFile).Length

    try {
        if ($DryRun) {
            Write-Host "  [DRY-RUN] Would convert: $SourceFile" -ForegroundColor Yellow
            return @{ Success = $true; SourceSize = $sourceSize; DestSize = [int]($sourceSize * 0.7) }
        }

        # Create output directory if needed
        $destDir = Split-Path $DestFile -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        # Convert to WebP
        $arguments = @(
            "`"$SourceFile`"",
            "-quality", "$Quality",
            "-define", "webp:lossless=false",
            "-define", "webp:method=6",
            "-define", "webp:alpha-quality=$Quality",
            "`"$DestFile`""
        )

        $process = Start-Process -FilePath $cmd -ArgumentList $arguments -Wait -NoNewWindow -PassThru

        if ($process.ExitCode -eq 0 -and (Test-Path $DestFile)) {
            $destSize = (Get-Item $DestFile).Length
            return @{ Success = $true; SourceSize = $sourceSize; DestSize = $destSize }
        } else {
            throw "Conversion failed with exit code: $($process.ExitCode)"
        }

    } catch {
        $script:Errors += "Failed to convert $SourceFile : $_"
        return @{ Success = $false; SourceSize = $sourceSize; DestSize = 0 }
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Processing
# ─────────────────────────────────────────────────────────────────────────────
function Start-ImageOptimization {
    Write-Banner

    # Check prerequisites
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

    if (-not (Test-ImageMagick)) {
        Write-Host "❌ ImageMagick not found!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install ImageMagick:" -ForegroundColor Yellow
        Write-Host "  Windows: choco install imagemagick" -ForegroundColor Cyan
        Write-Host "  macOS:   brew install imagemagick" -ForegroundColor Cyan
        Write-Host "  Linux:   apt-get install imagemagick" -ForegroundColor Cyan
        Write-Host ""
        exit 1
    }
    Write-Host "  ✅ ImageMagick found" -ForegroundColor Green

    # Check input path
    if (-not (Test-Path $InputFullPath)) {
        Write-Host "❌ Input path not found: $InputFullPath" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✅ Input path: $InputFullPath" -ForegroundColor Green

    # Find images
    Write-Host ""
    Write-Host "📷 Scanning for images..." -ForegroundColor Yellow

    $searchOption = if ($Recursive) { "AllDirectories" } else { "TopDirectoryOnly" }
    $images = Get-ChildItem -Path $InputFullPath -File -Recurse:$Recursive |
              Where-Object { $SupportedFormats -contains $_.Extension.ToLower() }

    if ($images.Count -eq 0) {
        Write-Host "⚠️ No images found in: $InputFullPath" -ForegroundColor Yellow
        exit 0
    }

    Write-Host "  Found $($images.Count) images to process" -ForegroundColor Cyan
    Write-Host ""

    # Process images
    $progressParams = @{
        Activity = "Converting Images to WebP"
        Status = "Processing..."
        PercentComplete = 0
    }

    foreach ($image in $images) {
        $script:TotalFiles++

        # Calculate output path
        $relativePath = $image.FullName.Substring($InputFullPath.Length).TrimStart('\', '/')
        $webpFileName = [System.IO.Path]::ChangeExtension($relativePath, ".webp")

        if ($OutputPath) {
            $destFile = Join-Path (Join-Path $ProjectRoot $OutputPath) $webpFileName
        } else {
            $destFile = Join-Path $InputFullPath $webpFileName
        }

        # Skip if already WebP
        if ($image.Extension.ToLower() -eq ".webp") {
            $script:SkippedFiles++
            continue
        }

        # Skip if WebP already exists and is newer
        if ((Test-Path $destFile) -and -not $DryRun) {
            $destItem = Get-Item $destFile
            if ($destItem.LastWriteTime -ge $image.LastWriteTime) {
                Write-Host "  ⏭️ Skipping (up to date): $($image.Name)" -ForegroundColor DarkGray
                $script:SkippedFiles++
                continue
            }
        }

        # Update progress
        $percent = [int](($script:TotalFiles / $images.Count) * 100)
        Write-Progress @progressParams -PercentComplete $percent -CurrentOperation $image.Name

        # Convert
        $result = Convert-ToWebP -SourceFile $image.FullName -DestFile $destFile -Quality $Quality

        if ($result.Success) {
            $script:ConvertedFiles++
            $saved = $result.SourceSize - $result.DestSize
            $script:TotalSavedBytes += $saved
            $savingsPercent = if ($result.SourceSize -gt 0) {
                [int](($saved / $result.SourceSize) * 100)
            } else { 0 }

            $status = if ($saved -gt 0) { "✅" } else { "⚠️" }
            Write-Host "  $status $($image.Name) -> $(Format-FileSize $result.SourceSize) -> $(Format-FileSize $result.DestSize) ($savingsPercent% saved)" -ForegroundColor $(if ($saved -gt 0) { "Green" } else { "Yellow" })

            # Remove original if requested
            if (-not $KeepOriginals -and -not $DryRun -and $saved -gt 0) {
                Remove-Item $image.FullName -Force
            }
        } else {
            Write-Host "  ❌ Failed: $($image.Name)" -ForegroundColor Red
        }
    }

    Write-Progress @progressParams -Completed

    # Summary
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "                        SUMMARY                                 " -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  📊 Total files scanned:  $($script:TotalFiles)" -ForegroundColor White
    Write-Host "  ✅ Files converted:      $($script:ConvertedFiles)" -ForegroundColor Green
    Write-Host "  ⏭️ Files skipped:        $($script:SkippedFiles)" -ForegroundColor Yellow
    Write-Host "  💾 Total space saved:    $(Format-FileSize $script:TotalSavedBytes)" -ForegroundColor Cyan
    Write-Host ""

    if ($script:Errors.Count -gt 0) {
        Write-Host "  ⚠️ Errors: $($script:Errors.Count)" -ForegroundColor Red
        foreach ($err in $script:Errors) {
            Write-Host "     - $err" -ForegroundColor Red
        }
    }

    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

    if ($DryRun) {
        Write-Host ""
        Write-Host "  ℹ️ This was a DRY RUN. No files were actually modified." -ForegroundColor Yellow
        Write-Host "     Remove -DryRun flag to perform actual conversion." -ForegroundColor Yellow
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────
Start-ImageOptimization
