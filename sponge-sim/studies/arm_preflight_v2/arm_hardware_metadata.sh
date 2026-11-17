#!/data/data/com.termux/files/usr/bin/bash
# A0D: fixed public hardware / own-app command metadata, no load or settings.
set -eu
umask 077
workspace="$HOME/sponge-sim"
test -d "$workspace"
target="$workspace/results/phone_a36/hardware_a0d_20261107_01"
mkdir -p "$workspace/results/phone_a36"
mkdir "$target"
exec >"$target/collector.stdout" 2>"$target/collector.stderr"
capture() {
    name="$1"; shift
    if timeout -k 1s 5s "$@" >"$target/$name.raw" 2>"$target/$name.stderr"; then
        printf '0\n' >"$target/$name.exit"
    else
        printf '%s\n' "$?" >"$target/$name.exit"
    fi
}
printf 'TERMUX_VERSION=%s\nTERMUX_APK_RELEASE=%s\n' \
    "${TERMUX_VERSION-}" "${TERMUX_APK_RELEASE-}" >"$target/environment.txt"
capture kernel uname -a
capture meminfo head -c 16385 /proc/meminfo
capture cpuinfo head -c 65537 /proc/cpuinfo
capture word_bits getconf LONG_BIT
capture page_bytes getconf PAGESIZE
for property in ro.product.model ro.product.device ro.soc.manufacturer ro.soc.model \
    ro.product.cpu.abilist ro.build.version.release ro.build.version.sdk; do
    capture "$property" /system/bin/getprop "$property"
done
capture command_versions dpkg-query -W -f='${Package}\t${Version}\n' termux-api termux-tools
capture command_hashes sha256sum "$PREFIX/bin/termux-battery-status" "$PREFIX/libexec/termux-api"
capture battery_script head -c 16385 "$PREFIX/bin/termux-battery-status"
capture main_package_path /system/bin/pm path com.termux
capture companion_package_path /system/bin/pm path com.termux.api
printf 'HARDWARE_METADATA_ONLY_NO_LOAD_SSH_SERVICE_LEFT_RUNNING\n' >"$target/completed.txt"
