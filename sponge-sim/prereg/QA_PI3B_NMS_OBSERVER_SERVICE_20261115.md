# Engineering qualification: self-TID pool and service cgroup inventory

This is not a scientific NMS/latency/RSS registration. No outcome or effect
estimate will be produced. The earlier NMS AA/MDE failure, cancelled PI1 and
closed RSS protocols are immutable. This qualification addresses gaps in the
older calling-thread/SSH-scope API check, not a retry of its data or of NMS.

Before device access freeze engineering tag
`qa-pi3b-nms-observer-service-20261115`, three Python sources and qa_config.json,
host test receipt and this plan. Use an exclusive new workspace
`/home/tanh/sponge-sim/pi3b_nms_observer_20261115`, one result `qa_result_01.json`
and one service `sponge-pi3b-nms-observer-qa-20261115.service`. Stop on error;
retain original bytes/failed/partial data. No QA02 or automatic relaunch.

## Fixed actions, before any device observation

1. Verify no active old measurement service or same-name QA service. Bind
   source/config/tag/commit in a launch manifest before starting. Strict SSH
   host-key checking, existing key/venv, no download/install or network data.
2. Launch one systemd service with Type=exec, User=tanh, CPUs0–3,
   KillMode=control-group, RuntimeMaxSec=180 and TimeoutStopSec=10. Set
   OMP/MKL/OpenBLAS thread environment to4. This creates an ephemeral service;
   it does not change governor, swap, USB/storage, system power, timer or SSH.
   No configuration lease/ExecStopPost is required because no such state is
   mutated. Record initial governor/swaps/affinity and require final equality.
3. Before importing Torch require Linux/aarch64, self affinity0–3, cgroup-v2
   root controller metadata, MemAvailable>=400000KiB and sampled temperature
   <75C. This is a bounded small functional check, not a stress measurement.
4. Save a pre-import all-self-thread inventory inside the service. Import
   existing torch2.15.0+cpu; set intraop4/interop1 and record parallel_info and
   thread environment. Execute exactly one FP32 CPU `mm(ones512²,ones512²)`;
   require every output element512. Delete tensors and collect Python garbage.
   No model/cache/mask/NMS, per-operator timing or ru_maxrss is read or logged.
5. Save two adjacent post-functional inventories, no extra workload between
   them. Require at least4 observed native TIDs, complete stable identities,
   all affinities0–3, same service cgroup and monotonic per-TID deltas. Do not
   equate observed/configured thread count with active parallel utilization.
6. For every snapshot retain the whole cgroup ancestor chain to root. Read
   cpu.max/stat/weight, memory limits/current/events/pressure and metadata as
   available. Optional failures are UNAVAILABLE with error type, never0.
   Root missing control files need not mean error or an unconstrained hierarchy.
   No quota is changed or inferred from the leaf alone. Shared ancestor
   counters do not attribute events to an operator/thread.
7. Inventory uses sequential procfs reads, not atomic snapshots. Enumerate
   TIDs before/after, check each thread's birth at its read and at snapshot
   end. Missing/reused/churned identities make it incomplete; no intersection
   filtering to rescue a whole-pool delta. Record per-thread CPU ticks,
   faults and context-switch counters and CPU-at-sample only as API metadata.
8. Wait only for this owned invocation until authoritative terminal. An SSH
   failure is not terminal: inspect only same service identity/state and
   continue waiting; never restart. No files/git/tests/analysis while it runs.
9. Only after inactive/MainPID0, collect original result/manifest once into
   an exclusive local original/; compare remote-before/local/remote-after
   SHAs, source hashes and native result/status. Verify no owned worker remains
   and governor/swaps/affinity match. SSH stays open. Keep FAIL/partial as-is.

## Interpretation boundary and next gate

PASS_SERVICE_POOL_INVENTORY_API_ONLY means one finite implementation/API
qualification in a service, with a functionally initialized Torch pool. It
does not establish performance of the future final workload unit, parallel
CPU utilization, stable NMS, low/no observer overhead, model-resident behavior,
or any paging/threadpool cause. memory.events/pressure may still be unavailable.
Future scientific tracing needs sham brackets/overhead and matched predecessor
controls, immutable inputs/backend, physical guards and new PREREG/tag plus
smoke/full review. No scientific load is allowed from this engineering tag.
