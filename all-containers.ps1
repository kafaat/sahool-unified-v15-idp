# all-containers.ps1
# Saves logs for every running container to .\logs\<timestamp>\<name>.log
# Processes containers in parallel batches of 5.

param(
    [int]    $BatchSize = 5,
    [int]    $TailLines = 500,
    [string] $LogDir    = (Join-Path $PSScriptRoot "logs")
)

# Setup
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$runDir    = Join-Path $LogDir $timestamp
New-Item -ItemType Directory -Path $runDir | Out-Null

Write-Host "=== Sahool Container Log Collector ===" -ForegroundColor Cyan
Write-Host "Output : $runDir"
Write-Host "Tail   : $TailLines lines per container"
Write-Host "Batch  : $BatchSize containers in parallel"
Write-Host ""

# Discover containers
$containers = @(docker ps --format "{{.Names}}" 2>&1 | Where-Object { $_ -match '\S' })

if ($containers.Count -eq 0) {
    Write-Host "ERROR: No running containers found." -ForegroundColor Red
    exit 1
}

$total = $containers.Count
Write-Host "Found $total running container(s)." -ForegroundColor Green
Write-Host ""

# Batch loop
$successList = [System.Collections.Generic.List[string]]::new()
$failedList  = [System.Collections.Generic.List[string]]::new()

for ($i = 0; $i -lt $total; $i += $BatchSize) {

    $end        = [Math]::Min($i + $BatchSize - 1, $total - 1)
    $batch      = $containers[$i..$end]
    $batchNum   = [Math]::Floor($i / $BatchSize) + 1
    $totalBatch = [Math]::Ceiling($total / $BatchSize)

    Write-Host ("Batch {0}/{1}  [{2}]" -f $batchNum, $totalBatch, ($batch -join ", ")) -ForegroundColor Yellow

    # Start a job for each container in this batch
    $jobs = foreach ($name in $batch) {
        $outFile = Join-Path $runDir ($name + ".log")
        Start-Job -ScriptBlock {
            param($n, $f, $t)
            $sep    = "-" * 72
            $header = "# Container : $n`r`n# Generated : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`r`n# Tail      : $t lines`r`n# $sep`r`n"
            [System.IO.File]::WriteAllText($f, $header, [System.Text.Encoding]::UTF8)
            docker logs $n --tail $t 2>&1 | Out-File -FilePath $f -Encoding UTF8 -Append
            return $LASTEXITCODE
        } -ArgumentList $name, $outFile, $TailLines
    }

    # Wait for batch and collect results
    $results = $jobs | Wait-Job | Receive-Job
    $jobs | Remove-Job -Force

    for ($j = 0; $j -lt $batch.Count; $j++) {
        $name = $batch[$j]
        $code = if ($results -is [array]) { $results[$j] } else { $results }
        if ($code -eq 0) {
            $successList.Add($name)
            Write-Host ("  OK   {0}" -f $name) -ForegroundColor Green
        } else {
            $failedList.Add($name)
            Write-Host ("  FAIL {0}" -f $name) -ForegroundColor Red
        }
    }
    Write-Host ""
}

# Summary
Write-Host ("Done. {0} succeeded, {1} failed" -f $successList.Count, $failedList.Count)
Write-Host ("Logs saved to: {0}" -f $runDir)

if ($failedList.Count -gt 0) {
    Write-Host ("Failed: {0}" -f ($failedList -join ", ")) -ForegroundColor Red
}

# Manifest
$manifestPath = Join-Path $runDir "_manifest.txt"
$nl = [System.Environment]::NewLine
$content  = "Sahool Container Log Dump" + $nl
$content += "Generated  : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" + $nl
$content += "Total      : $total" + $nl
$content += "Succeeded  : $($successList.Count)" + $nl
$content += "Failed     : $($failedList.Count)" + $nl
$content += $nl + "=== Containers ===" + $nl
$content += ($containers -join $nl)
[System.IO.File]::WriteAllText($manifestPath, $content, [System.Text.Encoding]::UTF8)
