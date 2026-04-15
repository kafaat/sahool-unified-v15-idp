powershell_script = '''# fix-1.ps1
# إصلاح تعارضات Git merge في ملفات package.json

param(
    [string]$ServicesPath = ".\\services",
    [switch]$KeepHead = $true,
    [switch]$KeepTheirs = $false,
    [switch]$WhatIf = $false
)

Write-Host "🔧 SAHOOL Package.json Conflict Fixer" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# إحصائيات
$stats = @{
    Total = 0
    Fixed = 0
    Failed = 0
    Skipped = 0
}

# البحث عن ملفات package.json
$packageFiles = Get-ChildItem -Path $ServicesPath -Recurse -Filter "package.json" -File

Write-Host "🔍 Searching for package.json files in: $ServicesPath" -ForegroundColor Yellow
Write-Host "Found: $($packageFiles.Count) files" -ForegroundColor Gray
Write-Host ""

foreach ($file in $packageFiles) {
    $stats.Total++
    $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
    
    # التحقق من وجود تعارض
    if ($content -match "<<<<<<< HEAD") {
        Write-Host "❌ Conflict found: $($file.FullName)" -ForegroundColor Red
        
        if ($WhatIf) {
            Write-Host "   [WhatIf] Would fix this file" -ForegroundColor Magenta
            $stats.Skipped++
            continue
        }
        
        try {
            # إنشاء نسخة احتياطية
            $backupPath = "$($file.FullName).backup"
            Copy-Item -Path $file.FullName -Destination $backupPath -Force
            
            $fixedContent = $content
            
            if ($KeepHead) {
                # الاحتفاظ بـ HEAD (النسخة الحالية)
                $fixedContent = [regex]::Replace($fixedContent, 
                    '<<<<<<< HEAD[\\s\\S]*?=======', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
                $fixedContent = [regex]::Replace($fixedContent, 
                    '>>>>>>> [\\w\\-\\/\\.]+', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
                    
                Write-Host "   → Kept HEAD version" -ForegroundColor Green
            }
            elseif ($KeepTheirs) {
                # الاحتفاظ بالـ incoming (الفرع المدمج)
                $fixedContent = [regex]::Replace($fixedContent, 
                    '<<<<<<< HEAD[\\s\\S]*?=======[\\r\\n]*', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
                $fixedContent = [regex]::Replace($fixedContent, 
                    '[\\r\\n]*>>>>>>> [\\w\\-\\/\\.]+', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
                    
                Write-Host "   → Kept incoming version" -ForegroundColor Green
            }
            
            # تنظيف المسافات الفارغة الزائدة
            $fixedContent = $fixedContent -replace "\\n\\n\\n+", "\\n\\n"
            
            # حفظ الملف
            Set-Content -Path $file.FullName -Value $fixedContent -NoNewline -Encoding UTF8
            
            # التحقق من صحة JSON
            try {
                $null = $fixedContent | ConvertFrom-Json -ErrorAction Stop
                Write-Host "   ✅ Valid JSON" -ForegroundColor Green
                $stats.Fixed++
                
                # حذف النسخة الاحتياطية
                Remove-Item -Path $backupPath -Force
            }
            catch {
                Write-Host "   ❌ Invalid JSON after fix! Restoring backup..." -ForegroundColor Red
                Copy-Item -Path $backupPath -Destination $file.FullName -Force
                $stats.Failed++
            }
        }
        catch {
            Write-Host "   ❌ Error: $_" -ForegroundColor Red
            $stats.Failed++
        }
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   Total files scanned: $($stats.Total)" -ForegroundColor White
Write-Host "   Fixed: $($stats.Fixed)" -ForegroundColor Green
Write-Host "   Failed: $($stats.Failed)" -ForegroundColor Red
Write-Host "   Skipped (WhatIf): $($stats.Skipped)" -ForegroundColor Magenta
Write-Host ""

if ($stats.Failed -gt 0) {
    Write-Host "⚠️  Some files failed. Check .backup files for manual recovery." -ForegroundColor Yellow
    exit 1
}
elseif ($stats.Fixed -gt 0) {
    Write-Host "✅ All conflicts resolved successfully!" -ForegroundColor Green
    Write-Host "   Run: git add . && git commit -m 'fix: resolve package.json merge conflicts'" -ForegroundColor Gray
    exit 0
}
else {
    Write-Host "✅ No conflicts found!" -ForegroundColor Green
    exit 0
}
'''

# Save to file
with open('/mnt/kimi/output/fix-1.ps1', 'w', encoding='utf-8') as f:
    f.write(powershell_script)

print("✅ Saved: fix-1.ps1")
print(f"📁 Location: /mnt/kimi/output/fix-1.ps1")
print(f"📊 Size: {len(powershell_script)} characters")
Now

