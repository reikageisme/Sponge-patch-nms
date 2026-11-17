#!/bin/bash
# PI3B-600MHZ campaign. Runs ON THE PI. One timing worker at a time, nothing else.
# usage: campaign.sh smoke|full TAG COMMIT RUNNAME
set -u
MODE=$1; TAG=$2; COMMIT=$3; NAME=$4
B="$HOME/sponge-sim/pi3b_600mhz"
PY="$HOME/sponge-venv/bin/python"
POL=/sys/devices/system/cpu/cpufreq/policy0
OUT="$B/runs/$NAME"
mkdir "$OUT" || { echo "run dir exists: $OUT"; exit 2; }
ORIG=$(cat $POL/scaling_governor)
restore() {
  echo "$ORIG" | sudo tee $POL/scaling_governor >/dev/null
  sudo swapon /dev/zram0 2>/dev/null
  echo "restored governor=$(cat $POL/scaling_governor) swap_total_kb=$(awk '/SwapTotal/{print $2}' /proc/meminfo)" >> "$OUT/campaign.log"
}
trap restore EXIT
echo powersave | sudo tee $POL/scaling_governor >/dev/null
sudo swapoff -a
if [ "$MODE" = smoke ]; then SETTLE=10; BETWEEN=10; FLAG=--smoke; else SETTLE=60; BETWEEN=60; FLAG=; fi
{
  echo "start_utc=$(date -u +%FT%TZ) mode=$MODE tag=$TAG commit=$COMMIT orig_governor=$ORIG"
  echo "governor=$(cat $POL/scaling_governor) swap_total_kb=$(awk '/SwapTotal/{print $2}' /proc/meminfo)"
  echo "throttled=$(vcgencmd get_throttled) clock=$(vcgencmd measure_clock arm) temp=$(vcgencmd measure_temp)"
} >> "$OUT/campaign.log"
sleep $SETTLE
run() {
  local profile=$1 mode=$2
  timeout 14400 "$PY" "$B/run.py" --lock "$B/lock.json" --base "$B" --run-dir "$OUT/${mode}_${profile}" \
    --tag "$TAG" --commit "$COMMIT" --profile "$profile" --mode "$mode" $FLAG > "$OUT/${mode}_${profile}.log" 2>&1
  echo "${mode}_${profile} returncode=$? end_utc=$(date -u +%FT%TZ)" >> "$OUT/status.txt"
  sleep $BETWEEN
}
# Fixed order. A failed session is retained; the next session is not a retry.
run PI4 pipeline
run PI1 pipeline
run PI4 stages
echo "end_utc=$(date -u +%FT%TZ)" >> "$OUT/campaign.log"
echo CAMPAIGN_FINISHED
