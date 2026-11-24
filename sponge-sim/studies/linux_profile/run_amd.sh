#!/usr/bin/env bash
# Chạy đợt đo lại theo PREREG_AMD_REPLICATION_20261124.md. Dùng: run_amd.sh smoke|full [thí nghiệm ...]
# Thí nghiệm: e1 e1nc1l e9 e10 e12 (mặc định: tất cả, đúng thứ tự PREREG).
set -euo pipefail
mode="${1:?smoke|full}"; shift
case "$mode" in smoke) extra=(--smoke) ;; full) extra=() ;; *) echo "smoke|full" >&2; exit 2 ;; esac
exps=("$@"); [ ${#exps[@]} -eq 0 ] && exps=(e1 e1nc1l e9 e10 e12)
repo="$(cd -- "$(dirname -- "$0")/../../.." && pwd)"; cd "$repo"
tag=prereg-amd-replication-20261124
test "$(git rev-parse HEAD)" = "$(git rev-parse "$tag^{commit}")"
git diff --quiet HEAD -- sponge-sim
root="$repo/runs/amd-20261124/$mode"; mkdir -p "$root"
py="$repo/.venv/bin/python"; lock=sponge-sim/studies/linux_profile/lock_env.sh
export SPONGE_PROFILES='{"P1_cpu2":[2]}' YOLO_CONFIG_DIR="$repo/.ultralytics"
gate() {
  test "$(cat /sys/devices/system/cpu/cpu8/online)" = 0
  test "$(cat /sys/devices/system/cpu/cpufreq/boost)" = 0
  sudo -n bash "$lock" verify 2 --seconds 10 > "$1"
}
cd sponge-sim
for e in "${exps[@]}"; do
  out="$root/$e"; test ! -e "$out"; mkdir "$out"
  "$py" -m pip freeze > "$out/environment.txt"; git rev-parse HEAD > "$out/prereg_commit.txt"
  gate "$out/xung_truoc.log"
  date -u +"[%FT%TZ] start $e $mode" | tee -a "$root/supervisor.log"
  case "$e" in
    e1)     "$py" -X utf8 studies/e1_dose/run.py --profiles P1_cpu2 --run-dir "$out/run" "${extra[@]}" ;;
    e1nc1l) "$py" -X utf8 studies/e1_dose/run.py --profiles P1_cpu2 --nc1-large --run-dir "$out/run" "${extra[@]}" ;;
    e9)     "$py" -X utf8 studies/e9_pipeline/run.py --run-dir "$out/run" "${extra[@]}" ;;
    e10)    "$py" -X utf8 studies/e10_reference/run.py --run-dir "$out/run" "${extra[@]}" ;;
    e12)    "$py" -X utf8 studies/e12_patch_remeasure_gated/run.py --profile P1_cpu2 --e7-dir results/e7_gpu/final/runs/e7 --run-dir "$out/run" "${extra[@]}" ;;
    *) echo "unknown $e" >&2; exit 2 ;;
  esac > "$out/run.log" 2>&1
  gate "$out/xung_sau.log"
  date -u +"[%FT%TZ] done $e $mode" | tee -a "$root/supervisor.log"
  touch "$out/DONE"
done
touch "$root/ALL_DONE"
