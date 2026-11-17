# A0C native Termux power metadata — prospective, no load

## Context already observed

User installed the Termux:API companion and ran the CLI manually. User-pasted
output reports CLI termux-api 0.59.1, GOOD/UNPLUGGED/DISCHARGING, 25 percent,
36.1 Celsius. The echo of TERMUX_APK_RELEASE was empty. This is operator-provided
text, not remotely captured raw; CLI version is NOT companion APK version or
proof of signing source. User explicitly enabled Tailscale/sshd and invited
remote access. This is a NEW working API route after A0/A0B failed fixed sysfs
reads. Do not repeat those failed paths or infer readiness from the new route.

## Fixed read-only scope

One invocation of termux_power_metadata.sh in NATIVE Termux, not Ubuntu/proot.
Read only command location, TERMUX_VERSION/TERMUX_APK_RELEASE environment,
dpkg metadata of termux-api/termux-tools, UTC wall timestamps, and exactly ONE
termux-battery-status request. The query is bounded by timeout 10s, KILL after
2s. Save stdout bytes, stderr, exit status and partial/error output without
retry. No performance timing/statistical endpoint, Torch import, affinity,
matrix/model work, sysfs discovery, package installation, permission changes,
system-setting changes or attempts to access another device.

All source/results writes remain under ~/sponge-sim. Remote source directory
studies/arm_power_a0c_20261107_01 must be NEW. Result directory
results/phone_a36/power_a0c_20261107_01 must be NEW. Existing paths refuse the
run; never overwrite or select a replacement attempt to improve observed SOC.
Copy the source only after prereg-arm-power-a0c-20261107 tag exists; verify
remote source SHA against termux_power_a0c_lock.json before invocation. Fetch
all result files after the process finishes, match remote/local byte hashes,
and retain SSH/transport status. End this phone stage by closing sshd as in
CLAUDE.md. A transport observation timeout is not permission to rerun: first
check authoritative process/result state of this SAME invocation.

## Interpretation and gates

This read may establish a working live battery route, not an accepted sensor
registry, signing compatibility audit, freshness/reaction guarantee or phone
profile. Wall timestamps bracket collection but cannot supply a monotonic
supervisor Reading; do not attach new monotonic timestamps during offline
analysis to make the saved output appear fresh. Celsius is the prospective
v0.53 source contract, not proof of the actual APK version. Preserve the
numeric response, never infer units by magnitude or divide temperature again.

SOC outside30..80, status other than CHARGING, unknown/contradictory state,
invalid/missing data all keep the load gate CLOSED. CPU thermal type/unit and
sentinel registry, actual runtime binding, Android/proot cleanup/parent-death,
observation cost/reaction QA, current idle/network/charging state and separate
registered load protocol remain required. No A0C outcome starts a workload.
