<#
.SYNOPSIS
    SAHOOL All Docker Compose Fix - Analyzes and fixes all docker-compose files using Ollama + qwen3-coder:30b

.DESCRIPTION
    Discovers every docker-compose.yml / docker-compose.yaml file across the entire
    repository, sends each one to the qwen3-coder:30b model running in Ollama, and
    writes back the corrected file.  The original is preserved as <file>.bak before
    any changes are applied.

    Common issues the model is instructed to fix:
      - Invalid / unsupported YAML syntax
      - Obsolete top-level "version:" key (Compose Spec no longer requires it)
      - Missing or wrong "networks:", "volumes:" declarations
      - Incorrect image tags or service configuration
      - Missing health-checks, restart policies, or resource limits
      - Wrong indentation or duplicate keys
      - Deprecated options (links, extends file, etc.)
      - Mismatched port bindings or protocol specifications
      - Environment-variable syntax errors

.PARAMETER RootPath
    Root directory to scan for docker-compose files.
    Default: directory containing this script.

.PARAMETER OllamaUrl
    Base URL of the Ollama API.
    Default: http://localhost:11434

.PARAMETER Model
    Ollama model to use for analysis.
    Default: qwen3-coder:30b

.PARAMETER DryRun
    Show what would be fixed without writing any changes.

.PARAMETER SkipBackup
    Do not create .bak backup files before overwriting.

.PARAMETER MaxRetries
    Number of API call retries per file on transient error.
    Default: 3

.PARAMETER TimeoutSec
    Seconds to wait for each Ollama generation call.
    Default: 600

.PARAMETER Exclude
    Comma-separated list of path fragments to exclude
    (e.g. "archive,legacy").  Default: "archive,legacy"

.PARAMETER OutputReport
    If provided, save a Markdown report to this path.

.EXAMPLE
    .\all-docker-compose-fix.ps1
    .\all-docker-compose-fix.ps1 -DryRun
    .\all-docker-compose-fix.ps1 -RootPath "C:\projects\sahool" -OutputReport "fix-report.md"
    .\all-docker-compose-fix.ps1 -Exclude "archive" -SkipBackup

.NOTES
    Requires: Docker, Ollama (http://localhost:11434), qwen3-coder:30b model
    Ollama docs: https://github.com/ollama/ollama
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [string]  $RootPath     = $PSScriptRoot,
    [string]  $OllamaUrl    = "http://localhost:11434",
    [string]  $Model        = "qwen3-coder:30b",
    [switch]  $DryRun,
    [switch]  $SkipBackup,
    [int]     $MaxRetries   = 3,
    [int]     $TimeoutSec   = 600,
    [string]  $Exclude      = "archive,legacy",
    [string]  $OutputReport = ""
)

$ErrorActionPreference = "Continue"
$ProgressPreference    = "SilentlyContinue"

# ─────────────────────────────────────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────────────────────────────────────
function Write-Header {
    param([string]$Title)
    $line = "=" * 80
    Write-Host ""
    Write-Host $line                     -ForegroundColor Cyan
    Write-Host "  $Title"               -ForegroundColor Yellow
    Write-Host $line                     -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host ("─" * 80) -ForegroundColor DarkCyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("─" * 80) -ForegroundColor DarkCyan
}

function Write-Success { param([string]$Msg) Write-Host "  ✅ $Msg" -ForegroundColor Green  }
function Write-Info    { param([string]$Msg) Write-Host "  ℹ  $Msg" -ForegroundColor Cyan   }
function Write-Warn    { param([string]$Msg) Write-Host "  ⚠  $Msg" -ForegroundColor Yellow }
function Write-Fail    { param([string]$Msg) Write-Host "  ❌ $Msg" -ForegroundColor Red    }
function Write-Change  { param([string]$Msg) Write-Host "  📝 $Msg" -ForegroundColor Magenta}

# ─────────────────────────────────────────────────────────────────────────────
# Ollama helpers
# ─────────────────────────────────────────────────────────────────────────────
function Test-OllamaAvailable {
    try {
        $null = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 8
        return $true
    }
    catch { return $false }
}

function Get-OllamaModels {
    try {
        $response = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 10
        return $response.models | ForEach-Object { $_.name }
    }
    catch { return @() }
}

function Install-OllamaModel {
    param([string]$ModelName)
    Write-Info "Pulling model '$ModelName' from Ollama registry (this may take several minutes)..."
    try {
        $body = @{ name = $ModelName; stream = $false } | ConvertTo-Json
        Invoke-RestMethod -Uri "$OllamaUrl/api/pull" -Method Post `
            -Body $body -ContentType "application/json" -TimeoutSec 7200 | Out-Null
        Write-Success "Model '$ModelName' downloaded successfully."
        return $true
    }
    catch {
        Write-Fail "Failed to pull model '$ModelName': $_"
        return $false
    }
}

function Invoke-OllamaFix {
    <#
    .SYNOPSIS Sends a docker-compose file to Ollama and returns the fixed YAML text.
    #>
    param(
        [string]$FilePath,
        [string]$FileContent
    )

    $relPath = $FilePath.Replace($RootPath, "").TrimStart("/\")

    $systemPrompt = @"
You are an expert Docker Compose engineer. Your task is to analyze a docker-compose
YAML file and return a corrected version with ALL bugs and errors fixed.

Rules:
1. Return ONLY the corrected YAML — no markdown fences, no explanations, no extra text.
2. Preserve the original intent and service definitions; only fix what is broken.
3. Fix every one of the following classes of problem if present:
   - Invalid YAML syntax (bad indentation, tabs instead of spaces, duplicate keys)
   - Top-level "version:" field: if invalid (e.g. a non-string value or misplaced), fix
     the syntax; if it is valid but unnecessary, add a comment "# version field is
     optional in Compose Spec" but do NOT remove it (many environments still need it)
   - Deprecated "links:" or incorrect "extends: file:" usage
   - Missing or mis-declared top-level "networks:" or "volumes:" sections
   - Image tags that use "latest" where a pinned version would be safer (add a comment
     like "# TODO: pin to a specific version" but keep latest if that was the intent)
   - Broken environment variable syntax (e.g. bare VAR without quotes when value contains
     special characters)
   - Port-binding entries that are missing the protocol or have wrong format
   - Missing "restart:" policies where the service is clearly long-running
   - Healthcheck "test" arrays that mix CMD / CMD-SHELL incorrectly
   - Resource limit sections that use the wrong Compose v3 syntax
   - Any other YAML or Compose-specific error
4. If the file is already correct, return it unchanged.
"@

    $userPrompt = @"
File: $relPath

--- BEGIN DOCKER-COMPOSE CONTENT ---
$FileContent
--- END DOCKER-COMPOSE CONTENT ---

Return only the corrected YAML.
"@

    $body = @{
        model  = $Model
        prompt = $userPrompt
        system = $systemPrompt
        stream = $false
        options = @{
            temperature    = 0.2
            num_predict    = 8192
            num_ctx        = 32768
        }
    } | ConvertTo-Json -Depth 5

    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        $attempt++
        try {
            $response = Invoke-RestMethod -Uri "$OllamaUrl/api/generate" `
                -Method Post -Body $body -ContentType "application/json" `
                -TimeoutSec $TimeoutSec
            return $response.response
        }
        catch {
            if ($attempt -ge $MaxRetries) { throw }
            Write-Warn "API call failed (attempt $attempt/$MaxRetries): $_  — retrying in $($attempt * 5)s..."
            Start-Sleep -Seconds ($attempt * 5)
        }
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# YAML cleanup: strip stray markdown fences the model might emit
# ─────────────────────────────────────────────────────────────────────────────
function Clean-ModelOutput {
    param([string]$Raw)
    # Remove leading ```yaml or ``` fence
    $cleaned = $Raw -replace '(?s)^```(?:yaml)?\s*', ''
    # Remove trailing ``` fence
    $cleaned = $cleaned -replace '(?s)\s*```\s*$', ''
    return $cleaned.Trim()
}

# ─────────────────────────────────────────────────────────────────────────────
# Detect whether two YAML strings differ meaningfully.
# Normalises CRLF to LF and trims only trailing blank lines at the end of the
# document so that a single trailing newline difference does not count as a
# change, while real content differences are always detected.
# ─────────────────────────────────────────────────────────────────────────────
function Compare-YamlContent {
    param([string]$Original, [string]$Fixed)
    # Normalise line endings
    $origNorm  = $Original -replace '\r\n', "`n"
    $fixedNorm = $Fixed    -replace '\r\n', "`n"
    # Trim only trailing whitespace/newlines (not leading, to preserve YAML indentation)
    $origNorm  = $origNorm.TrimEnd()
    $fixedNorm = $fixedNorm.TrimEnd()
    return $origNorm -ne $fixedNorm
}

# ─────────────────────────────────────────────────────────────────────────────
# Collect paths to exclude
# ─────────────────────────────────────────────────────────────────────────────
$excludeFragments = @($Exclude -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })

function Should-Exclude {
    param([string]$Path)
    foreach ($frag in $excludeFragments) {
        if ($Path -match [regex]::Escape($frag)) { return $true }
    }
    return $false
}

# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────
Write-Header "SAHOOL — All Docker Compose Fix  (qwen3-coder:30b)"
Write-Info "Root path : $RootPath"
Write-Info "Ollama URL: $OllamaUrl"
Write-Info "Model     : $Model"
Write-Info "Dry run   : $DryRun"
Write-Info "Skip backup: $SkipBackup"
Write-Info "Excludes  : $Exclude"

# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Verify Ollama is running
# ─────────────────────────────────────────────────────────────────────────────
Write-Section "Step 1 — Verifying Ollama availability"

if (-not (Test-OllamaAvailable)) {
    Write-Fail "Ollama is not reachable at $OllamaUrl"
    Write-Fail "Please start Ollama before running this script."
    Write-Fail "  Windows / macOS : https://ollama.com/download"
    Write-Fail "  Docker          : docker run -d -p 11434:11434 ollama/ollama"
    exit 1
}
Write-Success "Ollama is running at $OllamaUrl"

# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Ensure the model is present
# ─────────────────────────────────────────────────────────────────────────────
Write-Section "Step 2 — Checking for model '$Model'"

$availableModels = Get-OllamaModels
$modelPresent    = $availableModels | Where-Object { $_ -like "$Model*" }

if (-not $modelPresent) {
    Write-Warn "Model '$Model' is not present locally."
    if (-not $DryRun) {
        $ok = Install-OllamaModel -ModelName $Model
        if (-not $ok) {
            Write-Fail "Cannot proceed without the model. Exiting."
            exit 1
        }
    }
    else {
        Write-Info "[DryRun] Would pull model '$Model' — skipping."
    }
}
else {
    Write-Success "Model '$Model' is available."
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Discover all docker-compose files
# ─────────────────────────────────────────────────────────────────────────────
Write-Section "Step 3 — Discovering docker-compose files"

$allFiles = Get-ChildItem -Path $RootPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match '^docker-compose(\.[\w\-]+)?\.(yml|yaml)$' -and
        -not (Should-Exclude $_.FullName)
    } |
    Sort-Object FullName

Write-Info "Found $($allFiles.Count) docker-compose file(s) (after exclusions)."
$allFiles | ForEach-Object {
    Write-Host "    $($_.FullName.Replace($RootPath,'').TrimStart('/\'))" -ForegroundColor DarkGray
}

if ($allFiles.Count -eq 0) {
    Write-Warn "No docker-compose files found. Exiting."
    exit 0
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Analyze and fix each file
# ─────────────────────────────────────────────────────────────────────────────
Write-Section "Step 4 — Analyzing and fixing files"

$results = [System.Collections.Generic.List[PSCustomObject]]::new()
$idx     = 0

foreach ($file in $allFiles) {
    $idx++
    $relPath = $file.FullName.Replace($RootPath, "").TrimStart("/\")
    Write-Host ""
    Write-Host "  [$idx/$($allFiles.Count)] $relPath" -ForegroundColor White
    Write-Host ("  " + ("─" * 76)) -ForegroundColor DarkGray

    $result = [PSCustomObject]@{
        File    = $relPath
        Status  = "unchanged"
        Backup  = ""
        Error   = ""
        Changes = ""
    }

    # Read original content
    try {
        $original = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    }
    catch {
        Write-Fail "Cannot read file: $_"
        $result.Status = "error"
        $result.Error  = "Read error: $_"
        $results.Add($result)
        continue
    }

    if ([string]::IsNullOrWhiteSpace($original)) {
        Write-Warn "File is empty — skipping."
        $result.Status = "skipped"
        $results.Add($result)
        continue
    }

    # Send to Ollama
    if ($DryRun) {
        Write-Info "[DryRun] Would send $($original.Length) chars to $Model."
        $result.Status = "dry-run"
        $results.Add($result)
        continue
    }

    Write-Info "Sending to $Model for analysis..."
    try {
        $rawFixed = Invoke-OllamaFix -FilePath $file.FullName -FileContent $original
        $fixedContent = Clean-ModelOutput -Raw $rawFixed
    }
    catch {
        Write-Fail "Ollama call failed: $_"
        $result.Status = "error"
        $result.Error  = "Ollama error: $_"
        $results.Add($result)
        continue
    }

    if ([string]::IsNullOrWhiteSpace($fixedContent)) {
        Write-Warn "Model returned empty output — skipping file."
        $result.Status = "skipped"
        $results.Add($result)
        continue
    }

    # Detect changes
    $hasChanges = Compare-YamlContent -Original $original -Fixed $fixedContent

    if (-not $hasChanges) {
        Write-Success "No changes needed."
        $result.Status = "unchanged"
        $results.Add($result)
        continue
    }

    # Show diff summary (line count delta)
    $origLines  = ($original    -split "`n").Count
    $fixedLines = ($fixedContent -split "`n").Count
    $delta      = $fixedLines - $origLines
    $deltaStr   = if ($delta -ge 0) { "+$delta" } else { "$delta" }
    Write-Change "Changes detected  (original: $origLines lines → fixed: $fixedLines lines, Δ$deltaStr)"

    # Backup original
    if (-not $SkipBackup) {
        $backupPath = "$($file.FullName).bak"
        try {
            Copy-Item -Path $file.FullName -Destination $backupPath -Force
            Write-Info "Backup saved: $(Split-Path $backupPath -Leaf)"
            $result.Backup = $backupPath
        }
        catch {
            Write-Warn "Could not create backup ($backupPath): $_"
        }
    }

    # Write fixed content — always append a single trailing newline (POSIX convention)
    if (-not $fixedContent.EndsWith("`n")) {
        $fixedContent += "`n"
    }
    try {
        Set-Content -Path $file.FullName -Value $fixedContent -Encoding UTF8 -NoNewline
        Write-Success "File updated successfully."
        $result.Status  = "fixed"
        $result.Changes = "Lines: $origLines → $fixedLines (Δ$deltaStr)"
    }
    catch {
        Write-Fail "Could not write fixed content: $_"
        $result.Status = "error"
        $result.Error  = "Write error: $_"
        # Attempt to restore backup
        if ($result.Backup -and (Test-Path $result.Backup)) {
            Copy-Item -Path $result.Backup -Destination $file.FullName -Force
            Write-Warn "Original restored from backup."
        }
    }

    $results.Add($result)
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Summary
# ─────────────────────────────────────────────────────────────────────────────
Write-Section "Step 5 — Summary"

$fixed     = @($results | Where-Object { $_.Status -eq "fixed"     })
$unchanged = @($results | Where-Object { $_.Status -eq "unchanged" })
$skipped   = @($results | Where-Object { $_.Status -eq "skipped"   })
$dryRun    = @($results | Where-Object { $_.Status -eq "dry-run"   })
$errors    = @($results | Where-Object { $_.Status -eq "error"     })

Write-Host ""
Write-Host ("  {0,-16} {1}" -f "Total files:",    $results.Count)      -ForegroundColor White
Write-Host ("  {0,-16} {1}" -f "Fixed:",           $fixed.Count)        -ForegroundColor Green
Write-Host ("  {0,-16} {1}" -f "Unchanged:",       $unchanged.Count)    -ForegroundColor Gray
Write-Host ("  {0,-16} {1}" -f "Skipped:",         $skipped.Count)      -ForegroundColor DarkGray
if ($DryRun) {
    Write-Host ("  {0,-16} {1}" -f "Dry-run:",     $dryRun.Count)       -ForegroundColor Cyan
}
if ($errors.Count -gt 0) {
    Write-Host ("  {0,-16} {1}" -f "Errors:",      $errors.Count)       -ForegroundColor Red
}

if ($fixed.Count -gt 0) {
    Write-Host ""
    Write-Host "  Fixed files:" -ForegroundColor Green
    foreach ($r in $fixed) {
        Write-Host "    ✅ $($r.File)  ($($r.Changes))" -ForegroundColor Green
    }
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "  Errors:" -ForegroundColor Red
    foreach ($r in $errors) {
        Write-Host "    ❌ $($r.File)" -ForegroundColor Red
        Write-Host "       $($r.Error)" -ForegroundColor DarkRed
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Optional: Markdown report
# ─────────────────────────────────────────────────────────────────────────────
if ($OutputReport) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $sb = [System.Text.StringBuilder]::new()

    [void]$sb.AppendLine("# Docker Compose Fix Report")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("| Key | Value |")
    [void]$sb.AppendLine("|-----|-------|")
    [void]$sb.AppendLine("| Date | $timestamp |")
    [void]$sb.AppendLine("| Model | $Model |")
    [void]$sb.AppendLine("| Root | $RootPath |")
    [void]$sb.AppendLine("| Dry run | $DryRun |")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("## Results")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("| File | Status | Changes | Error |")
    [void]$sb.AppendLine("|------|--------|---------|-------|")

    foreach ($r in $results) {
        $statusEmoji = switch ($r.Status) {
            "fixed"     { "✅ fixed"     }
            "unchanged" { "⬜ unchanged" }
            "skipped"   { "⏭ skipped"   }
            "dry-run"   { "🔵 dry-run"   }
            "error"     { "❌ error"     }
            default     { $r.Status      }
        }
        $safeErr = $r.Error -replace '\|', '&#124;'
        [void]$sb.AppendLine("| ``$($r.File)`` | $statusEmoji | $($r.Changes) | $safeErr |")
    }

    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("## Totals")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("| Status | Count |")
    [void]$sb.AppendLine("|--------|-------|")
    [void]$sb.AppendLine("| Fixed | $($fixed.Count) |")
    [void]$sb.AppendLine("| Unchanged | $($unchanged.Count) |")
    [void]$sb.AppendLine("| Skipped | $($skipped.Count) |")
    [void]$sb.AppendLine("| Errors | $($errors.Count) |")

    try {
        Set-Content -Path $OutputReport -Value $sb.ToString() -Encoding UTF8
        Write-Host ""
        Write-Success "Report saved: $OutputReport"
    }
    catch {
        Write-Warn "Could not save report to '$OutputReport': $_"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Exit code
# ─────────────────────────────────────────────────────────────────────────────
Write-Host ""
if ($errors.Count -gt 0) {
    Write-Warn "Completed with $($errors.Count) error(s)."
    exit 1
}
else {
    Write-Success "All done!  $($fixed.Count) file(s) fixed, $($unchanged.Count) already clean."
    exit 0
}
