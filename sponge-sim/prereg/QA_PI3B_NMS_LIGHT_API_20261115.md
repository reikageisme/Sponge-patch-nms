# Engineering qualification: lightweight Linux process/thread resource sampler

This new helper implements the next part of the NMS tracer. The older heavy
inventory and native QA remain immutable. No observer overhead/performance
result, NMS/model, mask or RSS endpoint is enabled here. Do not use this
engineering tag as a scientific registration or retry closed NMS protocols.

## Fixed implementation/host qualification

`bracket.py` adapts the qualified output lifetime/GC discipline with explicit
file/range/sourceSHA provenance. A future call holds output until both wall
endpoints and both counter snapshots finish. GC is disabled during the call
and restored to its prior state on every exit. Exceptions propagate; no failed
call becomes a successful or zero-valued sample.

The future instrumented mode reads `getrusage(RUSAGE_SELF)` and
`getrusage(RUSAGE_THREAD)`, selected integer minor/major faults and voluntary/
involuntary context switches, process_cpu_ns/calling_thread_cpu_ns and
PID/callingTID. No procfs/cgroup/full-inventory/library read, Torch, logging,
subprocess or filesystem operation occurs in the helper. Counter snapshots
are outside the perf interval; deltas include observer work and sequential
clock intervals differ. Do not clamp process-vs-thread differences or interpret
context switches/CPU gaps as exact wait duration or a unique cause.

Uninstrumented mode uses the same wall interval/output/GC discipline with no
resource/CPU samples: all such fields are null with NOT_RECORDED, not0.
Instrumented and uninstrumented wall clocks/sham need a future registered
calibration, including observer-induced cache/scheduling effects. The word
light describes fewer operations, not a measured negligible overhead.

Host25tests use fake clocks/counters only, covering exact sample-call ordering,
GC states/exceptions, output lifetime, no sampling in control mode, identity/
schema/type/monotonicity failures, unsupported platform and synthetic Linux
resource API routing. No host operator/performance benchmark was performed.

## ONE native invocation, before timing

- Freeze `qa-pi3b-nms-light-api-20261115`, sources/config/thisplan/test/driver
  hashes before access. Exclusive workspace
  `/home/tanh/sponge-sim/pi3b_nms_light_20261115`, result01/manifest and service
  `sponge-pi3b-nms-light-api-qa-20261115.service`. No overwrite/retry/QA02.
- Existing Python3.13.5/Linux/aarch64, User=tanh, CPUs0–3, cap180s,
  TimeoutStopSec10, KillMode=control-group. Require sampled temp<75C and
  MemAvailable>=400000KiB. No package/network data, model/Torch/NumPy import,
  governor/swap/storage/controller/boot/SSH mutation or lease.
- Record initial governor/swaps/affinity/GC state. Invoke `sample()` exactly
  twice consecutively and `increments()` once. Require same actualPID/TID,
  exact schema/nonnegative integer counters/clocks and nondecreasing deltas.
  `measure()` is NOT invoked; no real perf_counter wall interval or operator
  is recorded. These are API metadata, not overhead or throughput observations.
- Unknown/missing/thread API/type/error closes FAIL with all partial data.
  Counter failure is never0. Do not enable memory cgroup/PSI or alter settings;
  optional unavailable hierarchy metadata is outside this native API test.
- Wait exclusively on the owned service to authoritative terminal; transport
  failure means wait same identity, not relaunch. Fetch original result and
  manifest only after terminal, once, SHAremote-before/local/remote-after.
  Recheck source/config==tag, no owned worker and original context unchanged.
  SSH remains open. Preserve any FAIL/partial without retry.

PASS_LIGHT_RESOURCE_API_ONLY qualifies the native sampler/field/arithmetic
availability. It does not qualify integrated real-clock overhead, full-pool
utilization or NMS causality. Next work is matched-predecessor/observer-sham
runner and prospective scientific PREREG/tag before ANY real call timing.
