#!/data/data/com.termux/files/usr/bin/bash
# A0C: one native-Termux battery read. No proot, sysfs, Torch or load.
# All writes are exclusive/new and confined to the existing workspace.
set -eu
umask 077
workspace="$HOME/sponge-sim"
test -d "$workspace"
target="$workspace/results/phone_a36/power_a0c_20261107_01"
mkdir -p "$workspace/results/phone_a36"
mkdir "$target"
exec >"$target/collector.stdout" 2>"$target/collector.stderr"
printf 'TERMUX_VERSION=%s\nTERMUX_APK_RELEASE=%s\n' \
    "${TERMUX_VERSION-}" "${TERMUX_APK_RELEASE-}" >"$target/environment.txt"
if command -v termux-battery-status >"$target/command.txt"; then
    printf '0\n' >"$target/command.exit"
else
    printf '%s\n' "$?" >"$target/command.exit"
fi
if dpkg-query -W -f='${Package}\t${Version}\n' termux-api termux-tools \
    >"$target/packages.txt" 2>"$target/packages.stderr"; then
    printf '0\n' >"$target/packages.exit"
else
    printf '%s\n' "$?" >"$target/packages.exit"
fi
date -u +%Y-%m-%dT%H:%M:%SZ >"$target/query_started_utc.txt"
if timeout -k 2s 10s termux-battery-status \
    >"$target/battery.raw.json" 2>"$target/battery.stderr"; then
    printf '0\n' >"$target/battery.exit"
else
    printf '%s\n' "$?" >"$target/battery.exit"
fi
date -u +%Y-%m-%dT%H:%M:%SZ >"$target/query_finished_utc.txt"
printf 'METADATA_ONLY_NO_LOAD_NO_SENSOR_QUALIFICATION\n' >"$target/completed.txt"
