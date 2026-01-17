# fix_flutter_errors_v2.ps1
# Run from: D:\projects\v64\sahool\apps\mobile

$ErrorActionPreference = "Stop"

function Backup-File($path) {
  if (Test-Path $path) {
    Copy-Item $path "$path.bak" -Force
  }
}

function Read-File($path) {
  return Get-Content $path -Raw -ErrorAction Stop
}

function Write-File($path, $text) {
  Set-Content -Path $path -Value $text -NoNewline -Encoding UTF8
}

function Show-Matches($path, $pattern, $label) {
  if (!(Test-Path $path)) { return }
  $m = Select-String -Path $path -Pattern $pattern -AllMatches -CaseSensitive:$false
  if ($m) {
    Write-Host "`nFOUND [$label] in $path" -ForegroundColor Cyan
    $m | ForEach-Object {
      Write-Host ("  line {0}: {1}" -f $_.LineNumber, $_.Line.Trim()) -ForegroundColor Gray
    }
  } else {
    Write-Host "`nNOT FOUND [$label] in $path" -ForegroundColor DarkGray
  }
}

function Patch-File($path, [scriptblock]$patcher, $label) {
  if (!(Test-Path $path)) {
    Write-Host "SKIP missing: $path" -ForegroundColor Yellow
    return
  }
  Backup-File $path
  $old = Read-File $path
  $new = & $patcher $old
  if ($new -ne $old) {
    Write-Host "UPDATED: $label -> $path" -ForegroundColor Green
    Write-File $path $new
  } else {
    Write-Host "NOCHANGE: $label -> $path" -ForegroundColor DarkGray
  }
}

$mainPath = Join-Path $PWD "lib\main.dart"
$dbPath   = Join-Path $PWD "lib\core\storage\database.dart"
$syncPath = Join-Path $PWD "lib\core\sync\sync_engine.dart"
$retryPath= Join-Path $PWD "lib\core\http\retry_interceptor.dart"
$piiPath  = Join-Path $PWD "lib\core\utils\pii_filter.dart"
$ratePath = Join-Path $PWD "lib\core\http\rate_limiter.dart"

Write-Host "`n=== Scan current issues (what the compiler complained about) ===" -ForegroundColor Magenta

Show-Matches $mainPath  "final\s+crashReporting\s*=\s*CrashReportingService\(\)\s*;" "main.dart local crashReporting"
Show-Matches $dbPath    "AppLogger\.w\([^;]*\berror\s*:" "database.dart AppLogger.w error:"
Show-Matches $syncPath  "_calculateBackoff\s*\(" "sync_engine.dart _calculateBackoff"
Show-Matches $syncPath  "AppLogger\.w\([^;]*\berror\s*:" "sync_engine.dart AppLogger.w error:"
Show-Matches $retryPath "TimeoutException" "retry_interceptor.dart TimeoutException"
Show-Matches $retryPath "import\s+'dart:async';" "retry_interceptor.dart import dart:async"
Show-Matches $piiPath   "replaceAll\([^,]+,\s*\(\s*match\s*\)" "pii_filter.dart replaceAll(function)"
Show-Matches $ratePath  "Dio\(\)\s*\.\.\s*options\s*=\s*newOptions" "rate_limiter.dart Dio()..options=newOptions"

Write-Host "`n=== Applying robust patches ===" -ForegroundColor Magenta

# 1) main.dart: remove any INDENTED 'final crashReporting = CrashReportingService();' (shadowing)
Patch-File $mainPath {
  param($t)
  # remove indented local shadowing (inside blocks)
  $t2 = $t -replace "(?m)^[ \t]+final\s+crashReporting\s*=\s*CrashReportingService\(\)\s*;\s*\r?\n", ""
  return $t2
} "Remove local crashReporting shadowing"

# 2) database.dart: Replace AppLogger.w(..., error: e) => AppLogger.w(..., data: {'error': e.toString()})
Patch-File $dbPath {
  param($t)
  # Replace any AppLogger.w call that contains "error:" named arg (single-line or multi-line)
  # Convert "error: <expr>" into "data: {'error': <expr>.toString()}"
  $t2 = [regex]::Replace(
    $t,
    "AppLogger\.w\((?<inside>[\s\S]*?)\);",
    {
      param($m)
      $inside = $m.Groups["inside"].Value
      if ($inside -notmatch "\berror\s*:") { return $m.Value }

      # Extract the error expression after error:
      $inside2 = [regex]::Replace($inside, "\berror\s*:\s*(?<err>[^,\)\r\n]+)\s*", {
        param($mm)
        $err = $mm.Groups["err"].Value.Trim()
        "data: {'error': $err.toString()} "
      })

      "AppLogger.w($inside2);"
    },
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
  )
  return $t2
} "Fix AppLogger.w(error:) in database.dart"

# 3) sync_engine.dart: same AppLogger.w(error:) fix + add _calculateBackoff if missing
Patch-File $syncPath {
  param($t)
  $t2 = $t

  # Fix AppLogger.w(error:) anywhere in file
  $t2 = [regex]::Replace(
    $t2,
    "AppLogger\.w\((?<inside>[\s\S]*?)\);",
    {
      param($m)
      $inside = $m.Groups["inside"].Value
      if ($inside -notmatch "\berror\s*:") { return $m.Value }

      $inside2 = [regex]::Replace($inside, "\berror\s*:\s*(?<err>[^,\)\r\n]+)\s*", {
        param($mm)
        $err = $mm.Groups["err"].Value.Trim()
        "data: {'error': $err.toString()} "
      })

      "AppLogger.w($inside2);"
    },
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
  )

  # Add _calculateBackoff if missing
  if ($t2 -notmatch "Duration\s+_calculateBackoff\s*\(") {
    $method = @"

  /// Calculate exponential backoff duration after repeated sync failures.
  /// Starts after 3 failures, doubles each time, capped at 5 minutes.
  Duration _calculateBackoff(int failures) {
    final exponent = (failures - 3).clamp(0, 10);
    final seconds = (1 << exponent);
    final capped = seconds.clamp(1, 300);
    return Duration(seconds: capped);
  }

"@

    # Insert before dispose() if exists, else before last '}' of class file
    if ($t2 -match "(?s)\n\s*void\s+dispose\s*\(\)\s*\{") {
      $t2 = [regex]::Replace($t2, "(?s)\n(\s*void\s+dispose\s*\(\)\s*\{)", "$method`n`$1", 1)
    } else {
      # best-effort: insert before final closing brace
      $t2 = [regex]::Replace($t2, "\n\}\s*$", "$method`n}`n", 1)
    }
  }

  return $t2
} "Fix SyncEngine AppLogger.w(error:) + add _calculateBackoff"

# 4) retry_interceptor.dart: add import dart:async if TimeoutException used
Patch-File $retryPath {
  param($t)
  if ($t -match "TimeoutException" -and $t -notmatch "import\s+'dart:async';") {
    if ($t -match "(?m)^(import\s+'.*?';\s*\r?\n)") {
      return $t -replace "(?m)^(import\s+'.*?';\s*\r?\n)", "`$1import 'dart:async';`r`n"
    }
    return "import 'dart:async';`r`n$t"
  }
  return $t
} "Add dart:async import for TimeoutException"

# 5) pii_filter.dart: replaceAll(x, (match)...) -> replaceAllMapped(x, (match)...)
Patch-File $piiPath {
  param($t)
  $t2 = $t
  # only change if second arg is a function (match)
  $t2 = [regex]::Replace(
    $t2,
    "replaceAll\(\s*(?<arg1>[^,]+)\s*,\s*\(\s*match\s*\)\s*\{",
    "replaceAllMapped(${arg1}, (match) {",
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
  )
  return $t2
} "Fix replaceAll(function) -> replaceAllMapped"

# 6) rate_limiter.dart: fix Dio()..options = newOptions (RequestOptions -> BaseOptions)
Patch-File $ratePath {
  param($t)
  $t2 = $t
  $t2 = [regex]::Replace(
    $t2,
    "final\s+dio\s*=\s*Dio\(\)\s*\.\.\s*options\s*=\s*newOptions\s*;",
@"
final dio = Dio(
              BaseOptions(
                baseUrl: newOptions.baseUrl,
                headers: Map<String, dynamic>.from(newOptions.headers ?? const {}),
                connectTimeout: newOptions.connectTimeout,
                receiveTimeout: newOptions.receiveTimeout,
                sendTimeout: newOptions.sendTimeout,
                responseType: newOptions.responseType,
                contentType: newOptions.contentType,
                followRedirects: newOptions.followRedirects,
                receiveDataWhenStatusError: newOptions.receiveDataWhenStatusError,
                validateStatus: newOptions.validateStatus,
              ),
            );
"@,
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
  )
  return $t2
} "Fix Dio options assignment type"

Write-Host "`n=== Re-scan after patch (should be NOT FOUND for bad patterns) ===" -ForegroundColor Magenta
Show-Matches $mainPath  "^[ \t]+final\s+crashReporting\s*=\s*CrashReportingService\(\)\s*;" "main.dart local crashReporting (indented)"
Show-Matches $dbPath    "AppLogger\.w\([^;]*\berror\s*:" "database.dart AppLogger.w error:"
Show-Matches $syncPath  "AppLogger\.w\([^;]*\berror\s*:" "sync_engine.dart AppLogger.w error:"
Show-Matches $syncPath  "Duration\s+_calculateBackoff\s*\(" "sync_engine.dart _calculateBackoff"
Show-Matches $piiPath   "replaceAll\([^,]+,\s*\(\s*match\s*\)" "pii_filter.dart replaceAll(function)"
Show-Matches $ratePath  "Dio\(\)\s*\.\.\s*options\s*=\s*newOptions" "rate_limiter.dart Dio()..options=newOptions"

Write-Host "`n=== Build steps ===" -ForegroundColor Magenta
& flutter clean
& flutter pub get
& dart run build_runner build --delete-conflicting-outputs
Write-Host "`nNow run: flutter run -t lib/main.dart" -ForegroundColor Cyan
