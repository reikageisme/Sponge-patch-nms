# A0D fixed hardware/command fingerprint metadata — no load

User now requests A36 Snapdragon6Gen3/8GB as an ARM development surrogate for
the eventual embedded-board pipeline, and explicitly keeps sshd open until
ALL phone ARM tests/measurements are done. User reports overnight charging;
SOC/thermal/idle/network conditions for load remain unverified. Read-only
connectivity has succeeded after A0C shutdown; do NOT shut sshd down again.

Known A0C: main environment googleplay.2026.10.09, CLI0.59.1/tools3.0.9;
24percent/UNPLUGGED/DISCHARGING/temperature35.7, raw preserved. API can now
return battery data. Current Google Play source has built-in BatteryStatus,
but installed binary/dispatch/companion identity is not yet fingerprinted.
No new battery query is part of A0D, and no repeated sysfs reads are attempted.

## Fixed scope, once

One native-Termux invocation of arm_hardware_metadata.sh, source SHA locked
in hardware_a0d_lock.json and tag prereg-arm-hardware-a0d-20261107 before copy.
New source studies/arm_hardware_a0d_20261107_01, NEW result directory
results/phone_a36/hardware_a0d_20261107_01, both under ~/sponge-sim.

Read uname, LONG_BIT/PAGESIZE, bounded first16385 bytes of /proc/meminfo and
first65537 bytes of /proc/cpuinfo, and exactly seven public properties:
ro.product.model/device, ro.soc.manufacturer/model, ro.product.cpu.abilist,
ro.build.version.release/sdk. Capture two CLI package versions; hashes of
$PREFIX/bin/termux-battery-status and $PREFIX/libexec/termux-api; bounded
first16385 bytes of the battery script. Query pm path for com.termux and
com.termux.api once each. These are READ-ONLY public hardware/own-app command
metadata exceptions necessary to the user-authorized ARM investigation; no
writes outside workspace, private app/user data, other package queries, root,
permission bypass, package install or Android/system-setting changes.

Each command has timeout5s+KILL1s. Preserve exact stdout/stderr/exit and errors;
no retry or alternative privilege/source on denial. A buffer at its cap is
incomplete evidence, never silently accepted as a complete file. One outer
metadata deadline150s+KILL5s, no scientific timing endpoint. Transfer and
match every remote/local byte hash after authoritative completion. An
observation timeout must not restart the invocation; inspect THIS run's state.

## Interpretation

MemTotal is kernel-visible usable RAM (kB as reported), not nominal marketed
capacity or a process limit. Keep original units and distinguish MiB/GiB in
derived values. Do not call A36 a Pi4/Pi5 or convert its timings into Pi data.
CPU model/features/properties and memory are descriptive, not an inference
throughput or CPU-affinity qualification. pm path may be denied/empty under
Android; retain that outcome, no dumpsys/root workaround in this scope.
CLI binary hashes do not identify the Android APK implementation by themselves.

No proot/Torch import, pin, matrix/model/segmentation work, camera, native sensor
stress, benchmark or battery status request. Registry thermal units/sentinels,
live guards, actual runtime binding and Android/proot cleanup/reaction QA
remain open before load. Preserve all prior results, keep sshd RUNNING.
