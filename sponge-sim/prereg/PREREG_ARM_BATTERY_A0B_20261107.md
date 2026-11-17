# Read-only fixed battery paths A0B — after A0 observations, before this read

A0metadata tag143be48 completed once. Current Ubuntu/proot metadata: aarch64,
CPU0..7,SC_CLK_TCK100,TorchDIST2.15.0,58thermal nodes; power_supply listing
denied. CPUrawup to71800,thermalbatteryraw39100, some other nodes have
unverified raw scale/sentinel values. No Torch import/load/pin performed.
Termux termux-battery-status/termux-api commands were checked and are absent.
Idle/charging/mobile-off remain unasserted. Fullload is CLOSED.

Purpose: determine whether ordinary reads of FOUR known battery files are
permitted even when listing their parent is denied. This is metadata-access
diagnosis, not a permission/SELinux bypass, thermal-unit inference or cooldown
retry. No su/chmod/root/APK/package install or system changes. Same authorized
Tailscale SSH target/user/strict previously trusted phone hostkey and existing
Ubuntu/proot venv, approved A0 metadata scope. No other paths are searched.

Exactly one process reads /sys/class/power_supply/battery/{type,capacity,status,temp}
once each using normal file permissions, max4KiB per field. Preserve readable
RAWstrings AND every denial/missing/error, with no conversion/zeroimputation.
Allerror is a valid readout that leaves the load gate closed; no retries or
runtime/source alternatives in this protocol. No statistical endpoint or
scientific performance timing is collected.

Source battery_paths_only.py SHA in battery_a0b_lock.json, new tag
prereg-arm-battery-a0b-20261107 BEFORE sourcecopy/read. New remote source
studies/arm_battery_a0b_20261107_01/battery_paths_only.py; output
results/phone_a36/battery_a0b_20261107_01/metadata.json,exclusive-create.
Verify sourcehash beforeinvoke; timeout60+kill5 metadata process bound, not
hardware reaction proof. Fetch and match remote/local byteSHA. Keep A0 unchanged.
No reading in this protocol qualifies a sensor registry or permits matrix/model
work. Further device load needs real state, typed live sensors, guard QA and
separate prospective registration. Close sshd when phone work finishes.
