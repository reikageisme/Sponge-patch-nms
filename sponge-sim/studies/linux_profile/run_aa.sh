#!/usr/bin/env bash
# Run the Ryzen clean-image calibration defined by PREREG_AA_LINUX_20261124.md.
set -euo pipefail
case "${1:-}" in
  smoke) extra=(--smoke) ;;
  full) extra=() ;;
  *) printf 'Usage: %s smoke|full RUN_DIRECTORY\n' "$0" >&2; exit 2 ;;
esac
run_root="${2:?provide a new run directory}"
repo="$(cd -- "$(dirname -- "$0")/../../.." && pwd)"
cd "$repo"
tag=prereg-aa-linux-20261124
test "$(git rev-parse HEAD)" = "$(git rev-parse "$tag^{commit}")"
git diff --quiet HEAD -- sponge-sim
mkdir "$run_root"

python="$repo/.venv/bin/python"
study=sponge-sim/studies/e5_protocol
lock=sponge-sim/studies/linux_profile/lock_env.sh
export SPONGE_PROFILES='{"P1_cpu2":[2]}'
export YOLO_CONFIG_DIR="$repo/.ultralytics"
"$python" -m pip freeze > "$run_root/environment.txt"
git rev-parse HEAD > "$run_root/prereg_commit.txt"
cp outputs/datasets/coco_val2017_extended/instances_subset.json "$run_root/image_manifest.json"
"$python" - <<'PY'
from hashlib import sha256
import json
from pathlib import Path

root = Path('outputs/datasets/coco_val2017_extended')
images = json.loads((root / 'instances_subset.json').read_text())['images']
expected_weights = 'f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36'
if sha256(Path('yolov8n.pt').read_bytes()).hexdigest() != expected_weights:
    raise SystemExit('YOLOv8n weights differ from E5')
for image in images:
    path = root / 'images' / image['file_name']
    if sha256(path.read_bytes()).hexdigest() != image['sha256']:
        raise SystemExit(f'COCO image hash mismatch: {path}')
print(f'Input SHA-256 verified for weights and {len(images)} COCO images')
PY
for canvas in 320 640; do
  test "$(cat /sys/devices/system/cpu/cpu8/online)" = 0
  test "$(cat /sys/devices/system/cpu/cpufreq/boost)" = 0
  sudo -n bash "$lock" verify 2 --seconds 10 | tee "$run_root/xung_${canvas}_truoc.log"
  date -u +'[%FT%TZ] Bắt đầu A/A'
  "$python" -X utf8 "$study/run.py" --require-lock --profiles P1_cpu2 \
    --canvas "$canvas" --run-dir "$run_root/aa_$canvas" "${extra[@]}" | tee "$run_root/aa_$canvas.log"
  sudo -n bash "$lock" verify 2 --seconds 10 | tee "$run_root/xung_${canvas}_sau.log"
  "$python" -X utf8 "$study/analyze.py" "$run_root/aa_$canvas" | tee -a "$run_root/aa_$canvas.log"
done
touch "$run_root/DONE"
