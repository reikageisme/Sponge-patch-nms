# Read-only A36 metadata A0 — 07/11/2026, before device readout

Purpose: identify current runtime/source, own-process CPU namespace and raw
sensor-node accessibility to prepare a later load protocol. NO Torch import,
model/matrix workload, affinity mutation, warmup, benchmark or profile PASS.
All historical phone FAILs and newer laptop results are already known.
Tailscale inventory and SSH handshake were observed before this document;
current runtime hashes/sensor readout have not yet been collected.

User explicitly requested SSH via Tailscale and enabled Termux sshd. Target
Anh's A36,100.85.153.4,useru0_a445,port8022. StrictSSHhostkey was successfully
matched to the previously stored phone key via alias[192.168.1.139]:8022;
do not accept changed/new keys or connect the deleted rentedWindowshost.
Current idle/charging/SOC/mobile-data-off state is NOT asserted by that reply.
This A0 grants no permission to infer those states or start load.

One invocation of metadata_only.py in the EXISTING Ubuntu/proot runtime using
venv/bin/python and existing ~/sponge-sim -> /root/sponge-sim bind. New source
directory studies/arm_metadata_a0_20261107_01; output
results/phone_a36/metadata_a0_20261107_01/metadata.json,exclusive-create.
No package install/upgrade, power/thermal/Android changes or writes outside
the approved sponge-sim workspace. Source consists only of metadata_only.py,
linux_observe.py and checks.py; SHA binds exactbytes in metadata_a0_lock.json.
Tag prereg-arm-metadata-a0-20261107 BEFORE new device readout/transfer.

Record Python/platform/architecture, inherited CPUmask, SC_CLK_TCK, ownTID
stat/status/masks and package DIST metadata/init-sourceSHA WITHOUT importing
Torch/torchvision/Ultralytics. Under the previously approved A0 sysfs scope,
explicit --allow-sysfs records only thermal-zone type/temp and power-supply
type/temp/capacity/status/online RAWstrings plus paths/errors. No conversion,
sensor selection from temperature, missing=zero, charging inference or runtime
GPU capability inference from version suffix. Candidate units/registry need
separate explicit review; unreadable sensors remain unreadable evidence.

This is current metadata, not scientific latency/count/thermal-response data.
No statistical endpoint/CI/MDE or load-safety qualification. No retesting four
historical profiles. Retain raw/errors and command outcome even if incomplete;
never repair an old raw file. If infra failure occurs BEFORE script/readout,
record it and repair only that infrastructure before an identical invocation.
If sensor/readout fails, preserve error; no runtime fallback/install or
privilege bypass. Termux command timeout bounds the metadata subprocess;
it is not a measured device reaction-time guarantee.

Verify source SHA on device before invocation, fetch byte-identical result,
record remote+local SHA, tagcommit/lock and declarations. Further reads/load
require their own scope/protocol; this is one readout. End phone stage by
closing sshd perCLAUDE unless continuing the authorized phone workflow.
