# WATCH X1 - chay lien tuc, tu refresh moi 60 giay. Ctrl+C de thoat.
# Mo terminal trong VS Code (Ctrl+~), chay:
#   powershell -ExecutionPolicy Bypass -File watch_x1.ps1
$root = "d:\Physical-Visual-DoS-EdgeAI-main"
$out  = Join-Path $root "outputs\x1_500img_20261018"
$log  = Join-Path $root "outputs\env_verify\x1_optim.log"
$optimDirs = Join-Path $out "optimization"

while ($true) {
    Clear-Host
    Write-Host "=== WATCH X1 (Ctrl+C de thoat) ===" -ForegroundColor Cyan
    Write-Host (Get-Date -Format "HH:mm:ss")
    Write-Host ""
    if (Test-Path $optimDirs) {
        $all   = Get-ChildItem $optimDirs -Directory
        $done  = @($all | Where-Object { Test-Path (Join-Path $_.FullName "complete.json") }).Count
        $total = 160
        $pct   = [math]::Round(100 * $done / $total, 1)
        $pctText = "$pct pct"
        Write-Host "Tien do toi uu hoa: $done/$total luot ($pctText)" -ForegroundColor White
        $barLen = [int]($done / 4)
        $bar = "#" * $barLen
        $bar = $bar.PadRight(40, ".")
        Write-Host "[$bar] $pctText"
        Write-Host ""
        Write-Host "3 luot xong gan nhat:" -ForegroundColor Cyan
        $recent = Get-ChildItem $optimDirs -Directory |
            Where-Object { Test-Path (Join-Path $_.FullName "complete.json") } |
            Sort-Object { (Get-Item (Join-Path $_.FullName "complete.json")).LastWriteTime } -Descending |
            Select-Object -First 3
        foreach ($r in $recent) { Write-Host ("  [x] " + $r.Name) }
        Write-Host ""
        Write-Host "Log moi nhat:" -ForegroundColor Cyan
        Get-Content $log -Tail 3
        $manifest = Join-Path $out "manifest.json"
        if ((Test-Path $manifest) -and (Select-String -Path $manifest -Pattern "optimization_finished_utc" -Quiet)) {
            Write-Host ""
            Write-Host ">>> OPTIMIZATION XONG TOAN BO! Buoc ke: python experiments/extended_evaluation.py --run-dir outputs/x1_500img_20261018" -ForegroundColor Green
        }
        $busy = @((Get-Process python -ErrorAction SilentlyContinue) | Where-Object { $_.CPU -gt 60 })
        if ($busy.Count -eq 0) {
            Write-Host ""
            Write-Host ">>> CANH BAO: khong thay python dang chay - process co the da dung (checkpoint van an toan)." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Chua thay out-dir. X1 chua phat." -ForegroundColor Yellow
    }
    Start-Sleep -Seconds 60
}
