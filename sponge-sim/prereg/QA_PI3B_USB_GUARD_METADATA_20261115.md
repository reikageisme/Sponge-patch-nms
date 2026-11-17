# Engineering QA — USB-present metadata guard, no workload

After41synthetic host tests, freeze source+driver under engineering tag
`qa-pi3b-usb-guard-metadata-20261115`. Exactly one real-device invocation,
two adjacent metadata frames, no sleep, model, rendering, ru_maxrss, timing
bracket, disk benchmark or disk contents. No mutation of swap/governor,
affinity, USB, partitions, mounts or data. Keep SSH open.

New workspace `/home/tanh/sponge-sim/pi3b_renderer_memory_usb_20261115` must
be absent before deployment. Deploy only frozen `usb_guard.py`; the existing
cache is read-only. Confirm shared service inactive/MainPID0 before invocation.
Bind workspace/cache paths to SD179:2; expected disks sda/sdb match previous
metadata (ADATA SP900/SupTronicsX89, capacities250069680/0, sda1size250067599).

Preserve complete frames even if validation fails. Validate actual identities,
all USB devices, partition/mount/holder state, generation and I/O baseline
across the two adjacent frames. Fresh contract is a QA candidate only, not
scientific registration. Then exercise wrong-model, I/O-increment and
in-flight branches on copied dictionaries, never actual hardware.

Any missing required API, non-idle frame, unexpected device or failed assertion
ends this one invocation, no retry. Save original JSON once on Pi, fetch and
verify remote/local/remote SHA plus source SHA. Governor/swaptopology/affinity
readback before/after must match. Original raw failures remain preserved.

PASS only qualifies standalone read-only API/schema behavior. It does not
qualify frontend-before-lease ordering, runtime/auditor integration, controller
cleanup, RSS savings, latency or NMS mechanism. These remain later work before
any new scientific PREREG/tag/endpoint. The closed RSS-V1 USB FAIL stays closed.
