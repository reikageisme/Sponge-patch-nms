#!/usr/bin/env bash
# Đợt đo lại theo góp ý 27/11/2026 (PREREG_AMD_REVISION_20261128.md, tag prereg-amd-revision-20261128).
# Dựa trên run_amd.sh (cùng cổng kiểm xung). Dùng: run_revision.sh smoke|full [thí nghiệm ...]
# Thí nghiệm: e9r e10r e10rm (mặc định cả ba, đúng thứ tự PREREG). e10rm = phiên thăm dò 10 ảnh với --malloc-fixed.
set -euo pipefail
mode="${1:?smoke|full}"; shift
case "$mode" in smoke) extra=(--smoke) ;; full) extra=() ;; *) echo "smoke|full" >&2; exit 2 ;; esac
exps=("$@"); [ ${#exps[@]} -eq 0 ] && exps=(e9r e10r e10rm)
repo="$(cd -- "$(dirname -- "$0")/../../.." && pwd)"; cd "$repo"
tag="${PREREG_TAG:?đặt PREREG_TAG=<tag PREREG đã tạo>}"
test "$(git rev-parse HEAD)" = "$(git rev-parse "$tag^{commit}")"
git diff --quiet HEAD -- sponge-sim
root="$repo/runs/amd-revision/${RUN_ID:-$mode}"; mkdir -p "$root"
py="$repo/.venv/bin/python"; lock="$repo/sponge-sim/studies/linux_profile/lock_env.sh"
export SPONGE_PROFILES='{"P1_cpu2":[2]}' YOLO_CONFIG_DIR="$repo/.ultralytics"
gate() {
  test "$(cat /sys/devices/system/cpu/cpu8/online)" = 0
  test "$(cat /sys/devices/system/cpu/cpufreq/boost)" = 0
  test "$(swapon --noheadings | wc -l)" = 0
  sudo -n bash "$lock" verify 2 --seconds 10 > "$1"
}
cd sponge-sim
for e in "${exps[@]}"; do
  out="$root/$e"; test ! -e "$out"; mkdir "$out"
  "$py" -m pip freeze > "$out/environment.txt"; git rev-parse HEAD > "$out/prereg_commit.txt"
  gate "$out/xung_truoc.log"
  date -u +"[%FT%TZ] start $e $mode" | tee -a "$root/supervisor.log"
  case "$e" in
    e9r)   "$py" -X utf8 studies/e9r_pipeline_finegrid/run.py --run-dir "$out/run" "${extra[@]}" ;;
    e10r)  "$py" -X utf8 studies/e10r_reference_rerun/run.py --run-dir "$out/run" "${extra[@]}" ;;
    e10rm) "$py" -X utf8 studies/e10r_reference_rerun/run.py --run-dir "$out/run" --malloc-fixed --n-images 10 "${extra[@]}" ;;
    *) echo "unknown $e" >&2; exit 2 ;;
  esac > "$out/run.log" 2>&1
  gate "$out/xung_sau.log"
  date -u +"[%FT%TZ] done $e $mode" | tee -a "$root/supervisor.log"
  touch "$out/DONE"
done
touch "$root/ALL_DONE"
