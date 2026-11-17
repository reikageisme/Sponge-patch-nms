#!/bin/bash
# PI3B-PI1-SSD campaign: ONE single-thread pipeline session on the Pi, with the declared
# idle USB SSD attached. Masks the zram swap unit so it cannot re-activate mid-run (the
# full01 failure mode), then swapoff; run.py still gates SwapTotal==0 at every block.
# usage: campaign_pi1.sh smoke|full TAG COMMIT RUNNAME
set -u
MODE=$1; TAG=$2; COMMIT=$3; NAME=$4
B="$HOME/sponge-sim/pi3b_pi1_ssd"
PY="$HOME/sponge-venv/bin/python"
POL=/sys/devices/system/cpu/cpufreq/policy0
OUT="$B/runs/$NAME"
mkdir "$OUT" || { echo "run dir exists: $OUT"; exit 2; }
ORIG=$(cat $POL/scaling_governor)
restore() {
  echo "$ORIG" | sudo tee $POL/scaling_governor >/dev/null
  sudo systemctl unmask dev-zram0.swap 2>/dev/null
  sudo systemctl start dev-zram0.swap 2>/dev/null
  echo "restored governor=$(cat $POL/scaling_governor) swap_total_kb=$(awk '/SwapTotal/{print $2}' /proc/meminfo)" >> "$OUT/campaign.log"
}
trap restore EXIT
echo powersave | sudo tee $POL/scaling_governor >/dev/null
sudo systemctl mask dev-zram0.swap 2>/dev/null
sudo swapoff -a
if [ "$MODE" = smoke ]; then SETTLE=10; FLAG=--smoke; else SETTLE=60; FLAG=; fi
{
  echo "start_utc=$(date -u +%FT%TZ) mode=$MODE tag=$TAG commit=$COMMIT orig_governor=$ORIG"
  echo "governor=$(cat $POL/scaling_governor) swap_total_kb=$(awk '/SwapTotal/{print $2}' /proc/meminfo)"
  echo "throttled=$(vcgencmd get_throttled) clock=$(vcgencmd measure_clock arm) temp=$(vcgencmd measure_temp)"
  echo "usb_block=$(ls /sys/block | grep '^sd' | tr '\n' ' ')"
  echo "mounts_sd=$(grep -c '^/dev/sd' /proc/self/mounts)"
} >> "$OUT/campaign.log"
sleep $SETTLE
timeout 14400 "$PY" "$B/run.py" --lock "$B/lock.json" --base "$B" --run-dir "$OUT/pipeline_PI1" \
  --tag "$TAG" --commit "$COMMIT" --profile PI1 --mode pipeline $FLAG > "$OUT/pipeline_PI1.log" 2>&1
echo "pipeline_PI1 returncode=$? end_utc=$(date -u +%FT%TZ)" >> "$OUT/status.txt"
echo CAMPAIGN_FINISHED
