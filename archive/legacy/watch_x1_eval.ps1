while($true){
  try { Clear-Host } catch {}
  Write-Output "=== WATCH X1-EVALUATION (Ctrl+C de thoat) ==="
  Get-Date
  $dir = "outputs\x1_500img_20261018\evaluation"
  # Slot records are identified by the JSON payload: a slot record stores `case`
  # as an OBJECT, an independent-EOT record stores `case` as a STRING. Counting by
  # file name is wrong: the six EOT-ablation specs are themselves named `eot_*`,
  # so `*.json` minus `eot_*.json` under-reports by exactly those 60 slots.
  $slots = @()
  Get-ChildItem $dir -Filter '*.json' -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.Name -in @('manifest.json','complete.json','completion_audit.json')) { return }
    try { $j = Get-Content $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } catch { return }
    if ($null -ne $j.case -and $j.case -isnot [string]) { $slots += $_ }
  }
  $n = $slots.Count
  $total = 250
  $pct = [math]::Round(100.0 * $n / $total, 1)
  Write-Output "Tien do: $n/$total slots ($pct pct)"
  $bar = [int](20 * $n / $total)
  Write-Output ("[" + ("#" * $bar) + ("." * (20 - $bar)) + "] $pct pct")
  Write-Output ""
  Write-Output "5 slot moi nhat:"
  $slots | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object { "  " + $_.LastWriteTime.ToString("HH:mm:ss") + "  " + $_.BaseName }
  $py = @(Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CPU -gt 30 })
  Write-Output ""
  if ($py.Count -gt 0) { Write-Output (">>> Python CHAY (CPU " + [math]::Round($py[0].CPU,0) + " giay).") } else { Write-Output ">>> CANH BAO: khong thay python dang lam viec!" }
  if ($n -ge $total) {
    Write-Output ""
    Write-Output ">>> EVALUATION XONG TOAN BO (250/250). Bao Cline chay buoc phan tich."
    break
  }
  Start-Sleep -Seconds 60
}
Read-Host "Nhan Enter de dong"
