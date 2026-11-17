# DRAFT — downstream NMS after output-equivalent mask renderer interventions

NOT PREREGISTERED / NOT RUNNABLE. No timing registration/tag exists for this
proposal. This is a concrete next design after old NMS controls failed, the
separate memory intervention passed and observer APIs were qualified. It
does not retroactively preregister or retry any earlier session. No new NMS
or overhead timing data has been collected to choose these settings.

## Question and fixed material

Primary question: does replacing the native32M mask predecessor with the
preallocated/direct-copy16M predecessor change the latency of the NEXT fixed
NMS wrapper call on the same attacked predictions? This is a combined-renderer
intervention, not isolation of memory size, allocator or scheduling. Secondary
kernel-call/counter/sham data characterize possible carryover, never establish
a unique paging/threadpool cause or DoS on their own.

Use all20 previously observed frozen pairs, IDs9,25,30,34,36,42,49,61,64,71,
72,73,74,77,78,81,86,89,92,94 (12-digit zero padding), same one attack init,
weights/model/source/inputs bound by original SHA manifests. Fixed FP32 CPU,
640², confidence.25/IoU.45/nc80/max_det300/max_nms30000/class-aware and locked
torchvision backend; no count/image/seed/thread/cap/backend search.
This is a reused finite cohort, not an independent replication/new seeds.

Read existing frozen mask caches/manifest61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165.
Model remains resident in one worker across images as in the earlier mixed
workload. Prepare each image's predictions/prototypes once, retain required
inputs, audit counts/mask hashes against frozen material and extract exact
kernel-call boxes/scores through ONE outside-clock wrapper interception.
Remove interception before timing; require one expected backend invocation
and selected-index/detection parity. No hand-built boxes replace true input.
New functional material/runner QA must establish this before timing.

## Proposed fixed factorial schedule

- Predecessor: native32M mask, candidate16M mask, NMS-reference on the same
  prediction. First two have finite exact mask parity; NMS-reference is a
  contextual control, not equal work/memory. No predecessor timing endpoint.
- Target: complete Ultralytics wrapper, torchvision NMS call on its exact
  prepared boxes/scores, empty callable sham. Kernel-call boundary retains
  Python/library dispatch overhead, not bare C++ instruction time.
- Observer: instrumented lightweight process/current-thread resource snapshots
  versus uninstrumented (null counters, same wall bracket/lifetime/GC).
- Two identical copies A/B of every cell; five repeats. Shuffle36cells within
  image/repetition with seed20261115+1000*master_image_index+rep, never
  renumber a subset. Full20=3600target trials; technical smokeIDs9+30=360.
  No replacement image/repeat, serialsmoke02/full02 or post-outcome grid.

Prepare target clones/arguments BEFORE predecessor; guard/intent outside the
whole pair. Disable GC across predecessor+target. Execute predecessor, release
its output BEFORE target, then immediately call the fixed target/bracket.
No hash/procfs/cgroup/guard/log/subprocess/gc.collect between predecessor and
target; only the declared lightweight sampler in instrumented mode. Retain
target output through endpoints, then release before post-guard. Do not
subtract separate medians to reconstruct a pipeline. Output digests/parity
are outside timing in functional qualification, not extra intervening work.
Do not subtract sham time from NMS values. Input setup/counter observer work
outside clock can still alter state; this is why calibration/sham are required.
Bind/import resource and all sampler dependencies during setup BEFORE any
predecessor/trial, not lazily inside the per-call sampler. The qualified API
prototype f725 still has lazy import and is immutable; its final runtime copy
needs an explicit initialization/call-path regression and integration QA.
No explicit file API does not guarantee absence of demand-paging I/O.

Full TID/birth/all-affinity inventory and cgroup ancestor readback at block
boundaries, not each call. Preserve all born/gone identities; unexpected
configuration/drift/missing required state stops without filtered TID/image
intersection. Optional memory cgroup counters remain unavailable/null with
reason; never enable controllers or interpret missing as0. Keep clock/counter
raw, including process CPU/wall ratios>1 or sequential interval differences.

## Proposed gates and analysis (before future first timing)

New isolated supervised source/workspace, reversible qualified swap/governor
lease/independent cleanup, idle SSD topology/I/O contract and per-phase baseline
as in the accepted USB condition. Pi3B undervoltage/600MHz declared, affinity
0–3/intraop4/interop1/env4. Same sampled thermal<75C, MemAvailable>=40000KiB,
swapOFF/pswp/oom/governor/mask/USB gates and actualclock594..606MHz. No source/
power/firmware/package change to rescue a run. Supervisor cap smoke3600s,
full21600s; model/operator/whole-campaign cleanup and fault-injection QA needed.

Before final registration specify and implement fixed warmups and forward
reference cadence/flag gates, actual-load process parallelism sentry and
exact counter-read/serialization placement. These parts are NOT implemented
or finalized by this draft; they cannot be invented after observations.
Keep all critical source/model/material/observer/contract/QA hashes in lock
and prelaunch manifests. API-only QA does not qualify integrated runner.

ONE technical smoke then SHA/structure/physical/restore/source audit and
budget; smoke AA/MDE diagnostic only, no efficacy, fixed prospectively before
first timing of THIS distinct question. Earlier pilot FAIL stays closed.
STOP for concrete review before one full. Full requires all scheduled data,
source/parity/physical/restore and the following full20 controls, unchanged:
- A/A for each nonsham target×predecessor×observer (12contexts): per-image
  log(medianA5/medianB5), absmean<=.02 AND MDElog80%<=.05 in EVERY context.
- Instrumentation calibration for each nonsham target×predecessor (6contexts):
  per-image log(pooled instrumented median10 / pooled uninstrumented median10),
  absmean<=.02 AND MDElog80%<=.05 in EVERY context. Acceptance gates are not
  formal equivalence claims. Any failure leaves campaign diagnostic/closed;
  no dropping images, borrowing another control, primary-only rescue or retry.
- All nonsham target times strictly positive; unknown/errors never0. Sham
  zero from clock resolution may be retained; no unstable sham ratio gate.

Primary: uninstrumented wrapper, median10(A+B) after candidate / median10(A+B)
after native, ratio within each image then log. Geometric mean, image-bootstrap
percentile20000/RNG2026111501, exact two-sided sign-flip2^20, d_z=mean/SDddof1,
primary MDE80% plus all AA/calibration MDEs (central-t formula). One confirmatory
endpoint, no additional confirmatory family. ZeroSD gives dznull, not
equivalence. No inference across attack seeds/devices.
Kernel-call, NMS-reference, instrumented values and process/thread fault/
context/CPU/sham summaries are descriptive with every raw-line mapping; do not
treat3600trials as independent image units. Counter deltas include observer
work, use corresponding sham context; do not label any event exact NMS-only.
Complete quality-failed data may have diagnostic summaries; partial/corrupt
cohorts get audit/raw only, no image-filtered efficacy interval.

The primary effect could be absent or controls could fail. Keep all outcomes;
no serial protocol search for PASS, clock/device conversion or DoS claim.
Final PREREG requires the outstanding runner/material/sentry/reference/QA
details and source/test hashes before scientific tag or timing. This draft
neither launches a smoke nor waives any old gate.

## Implementation checkpoint15November, not qualification of the full runner

Core helpers now exist in studies/pi3b_nms_predecessor_20261115 with51host
functional/fake-clock tests; source package is PREPARED_CORE_NOT_RUNNABLE,
scientific/function-device flagsFalse in engineering_lock_v2.json. Explicit
resource setup, immediate pair/lifetime, factorial schedule, true kernel input
capture with stride/offset and cache-content/count parity are implemented.
Host functional source matches installed Pi nms.py but Torch/torchvision
compiled versions differ. No native40-case or real timing evidence yet.

Fresh model prototype/coefficients/boxes may replace the loaded cache tensor
objects ONLY after exact value parity; preserve original cache files. Finalize
the resident clean+adv buffer contract and release the validation duplicate
before trials, rather than silently changing model-memory context after
observations. Warmup/reference/sentry/model worker/guard/supervisor/restore,
material export/auditor and full analyzer remain prerequisites, not optional
work to omit because core unit tests pass. Initial distribution-metadata lock
and two host-test failures remain archived; module versions bind future runtime.
