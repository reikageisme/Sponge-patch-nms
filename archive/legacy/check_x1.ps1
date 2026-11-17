# -*- CHAY BANG POWERSHELL: chuot phai -> Run with PowerShell hoac double-click -*-
# Kiem tra tien trinh X1: outputs/x1_500img_20261018
$root = "d:\Physical-Visual-DoS-EdgeAI-main"
$out  = Join-Path $root "outputs\x1_500img_20261018"
$log  = Join-Path $root "outputs\env_verify\x1_optim.log"

Write-Host "=== TRANG THAI X1 ===" -ForegroundColor Cyan

$optimDirs = Join-Path $out "optimization"
if (Test-Path $optimDirs) {
    $all   = Get-ChildItem $optimDirs -Directory
    $done  = @($all | Where-Object { Test-Path (Join-Path $_.FullName "complete.json") }).Count
    $total = 160   # 16 specs x 10 seeds
    Write-Host ("Hoan tat toi uu hoa: {0}/{1} luot ({2:N0}%)" -f $done, $total, (100*$done/$total))
    $manifest = Join-Path $out "manifest.json"
    if ((Test-Path $manifest) -and (Select-String -Path $manifest -Pattern "optimization_finished_utc" -Quiet)) {
        Write-Host ">>> TOI UU HOA XONG TOAN BO. Buoc tiep: python experiments/extended_evaluation.py --run-dir outputs/x1_500img_20261018" -ForegroundColor Green
    } else {
        Write-Host ">>> CHUA xong - van dang chay hoac da dung giua (co checkpoint, chay lai lenh cu de resume)."
    }
} else {
    Write-Host "Chua thay folder outputs/x1_500img_20261018 - X1 chua phat."
    Write-Host "Chay lenh: python experiments/extended_validation.py --seeds 10 --out-dir outputs/x1_500img_20261018"
}

if (Test-Path $log) {
    Write-Host "`n=== 6 DONG CUOI CUA LOG ===" -ForegroundColor Cyan
    Get-Content $log -Tail 6
    $proc = Get-Process python -ErrorAction SilentlyContinue
    $busy = @($proc | Where-Object { $_.CPU -gt 60 })
    if ($busy.Count -gt 0) { Write-Host "`n>>> Python dang CHAY (CPU dang lam viec)." -ForegroundColor Green }
    elseif ($proc) { Write-Host "`n>>> Python dang mo nhung CPU thap - co the da xong hoac dang nghi." -ForegroundColor Yellow }
    else { Write-Host "`n>>> Khong con process python nao dang chay." -ForegroundColor Yellow }
}

Write-Host "`n(Cua so nay tu dong dong sau 30 giay)"
Start-Sleep -Seconds 30

