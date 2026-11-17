# DRAFT — renderer memory comparison after the closed Pi full20

Not a scientific registration or permission to start another campaign. No
variant has been measured. Full20 primary passed; its component session failed
NMS precision and PI1 was cancelled. Those decisions remain unchanged.

## Question and design decision already made before variant observations

Can a renderer with preallocated uint8 output, direct float-to-output copy and
a 16,000,000-pixel float-chunk budget reduce process peak RSS while preserving
exact masks, relative to the frozen baseline with list+cat/32,000,000 pixels?
This is a new renderer condition, not a retry of NMS or PI1. The 16M choice is
motivated by an explicit static storage model, not latency/RSS tuning.

Source: `studies/pi3b_renderer_prealloc_20261114/`. Helpers/baseline copied with
file/line/SHA provenance from locked ops SHA828de5d2…; installed packages and
all old study sources are unchanged. Functional laptop QA12tests passes with
finite synthetic FP32 inputs, including zero masks/zero logits/empty and
off-image boxes/noncontiguous coefficients/multiple chunk boundaries/K300 at
640². No real-image/device parity, empirical memory or speed qualification yet.

Keep the 32M-preallocated variant only as a functional/static diagnostic,
NOT another timing condition selected after comparison. Its modeled maximum
can exceed baseline. No unregistered chunk-size/performance search.

## Proposed fixed endpoints and material preparation

- Use the same20 input pairs, weights, FP32/640/batch1 and declared Pi3B600MHz
  condition; do not relabel as heldout or an independent replication. Produce
  one immutable CPU prototype/coefficient/box cache per image before timed
  execution. Bind caches, original inputs, package source and weight SHAs in
  a new lock. Record count parity and exact candidate/baseline mask hashes.
- Require actual-device finite output parity on all20 clean AND attacked cases
  before any latency experiment; failures stop, with raw outputs retained.
  Functional QA uses no clocked endpoint; it is not a performance PASS.
- Memory endpoint: whole-process Linux `ru_maxrss` in fresh child processes
  which load only a single frozen renderer cache, import the same runtime and
  execute one locked renderer condition. No model loaded in that child. Read
  high-water RSS after rendering and the zero-copy output digest, including
  imports, cache load/validation, same-renderer K1 warm-up if available,
  input/output/allocator/workspaces;
  do NOT subtract startup RSS and label the difference renderer peak memory.
  A dominating startup high-water mark can hide differences and is a possible
  negative result. Exact masks must hash identically in every child.
- Compare baselineA/baselineB/candidate16M in fresh processes on BOTH clean and
  attacked cases, three repetitions, 20images (360 children maximum). Shuffle
  the six arm/condition combinations with seed20261114+1000*image_index+rep.
  Use perimage medians; pool the six baselineA+B samples for each denominator,
  never divide across-image medians. Attacked candidate/baseline is primary;
  clean is secondary to expose any regression. Both clean and attacked
  baselineA/B controls must satisfy absmeanlog≤.02 and MDElog≤.05 on20images;
  retain negative/partial results, never drop individual cases to pass.
  Primary bootstrap20000 images, exact signflip2^20; analysis RNGs still to be
  fixed before a scientific tag. Each child capped180s, campaign21600s. Timing
  and memory campaigns remain separate so sampling/profiling cannot distort
  a claimed latency endpoint. Static byte models are not empirical RSS.
- Optional matched latency endpoint must be decided BEFORE registration:
  baselineA/baselineB/candidate16M,5reps each,20images, fixed shuffle. Same guard,
  clock/pin/reference/restore and AA absmeanlog≤.02/MDElog≤.05 gates as the
  accepted pipeline protocol, but only renderer calls are timed. No NMS stage
  claim or component-gate rescue. One independent latency session, no retry.
  Do not compare its absolute values causally against earlier full20 sessions.

## Required implementation before a scientific tag

1. Cache-builder and strict material manifests; verify cache keys/dimensions/
   finite values/device parities; source-copy regression against baseline.
2. Bounded fresh-process memory collector with exact child identity/reaping,
   timeout/exception/low-memory/thermal/swap/restore controls and no orphan
   outputs. Reuse supervisor only with provenance and host/device sleeping-QA.
3. Lock inference unit, RNGs, method, latency inclusion, finite repetition/time
   caps, preconditions and stopping rule. Register protocol+git tag BEFORE
   any empirical memory or latency endpoint. No silent generation of a new
   campaign after a gate failure; retain all outcomes and ask about any changed
   design rather than perform serial attempts until PASS.

Current state: offline code now includes cache.py/build_cache.py (functional
material preparation only), memory_worker.py and memory_campaign.py. The
collector remains torch-free; child processes alone load the runtime. Host
tests cover source/registration binding, cache corruption/identity/schema,
single-output parity lifetime and direct-child stop/reaping, including a
journal error immediately after spawn. This is NOT actual Pi cgroup,
SIGKILL-parent, restore or empirical RSS qualification. The new supervisor,
full analyzer, cache/device QA and scientific registration still need work.
No deployment,
device load, new runtime masks/governor change or empirical endpoint recorded.
No speed, measured RSS savings, accuracy equivalence or Q1 guarantee claimed.
