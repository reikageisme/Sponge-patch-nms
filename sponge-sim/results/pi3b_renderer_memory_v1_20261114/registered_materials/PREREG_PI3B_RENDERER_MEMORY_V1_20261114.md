# DRAFT â€” fresh-process renderer RSS on the existing Pi cohort

Final prospective protocol, before the FIRST renderer RSS observation.
Scientific tag: prereg-pi3b-renderer-memory-v1-20261114.
No new empirical RSS has been observed at registration.
This prospective memory endpoint follows the renderer proposal made before the
accepted full20 run, the static 16M-pixel design, and functional parity on all
40 frozen Pi caches. It does not repeat/rescore rejected NMS or PI1 sessions.
The earlier two-image swapguard-v2 latency pilot remains FAIL and closed.

## Question, scope and material

Does the fixed preallocated/direct-copy 16M renderer reduce whole-process
Linux high-water RSS versus the frozen native 32M renderer on attacked cases?
Clean cases are secondary, to expose regressions. No latency, model accuracy,
causal NMS mechanism, deadline failure or DoS endpoint is enabled here.

Use the same twenty previously observed PGD input pairs: COCO IDs
9,25,30,34,36,42,49,61,64,71,72,73,74,77,78,81,86,89,92,94, zero-padded to
12 digits. This is a reused finite cohort, one attack initialization per pair;
it is not a held-out replication or additional attack seeds.

Immutable material: `/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/caches/cache_01`.
Manifest SHA256 `61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165`.
All forty tensor SHAs, K/count metadata and expected exact output digests are
bound by that manifest. The functional audit and original cache provenance
retain weights/input/runtime/source identities. Do not regenerate caches.
No mask rendering on the laptop is substituted for device hash verification.

New isolated source/workspace: `studies/pi3b_renderer_memory_v1_20261114/` /
`/home/tanh/sponge-sim/pi3b_renderer_memory_v1_20261114`. Freeze nine runtime
source SHAs, reference SHAs, protocol SHA and scientific tag before smoke.
The engineering lock and its QA tag alone cannot enable a scientific run.

## Endpoint and fixed execution

One fresh process imports torch2.15.0+cpu/numpy2.5.4/Python3.13.5, loads and
validates one CPU FP32 cache, performs same-renderer K1 warmup once if K>0,
renders the full case and computes a zero-copy output digest. Immediately
after the digest, read `resource.getrusage(RUSAGE_SELF).ru_maxrss` on Linux
(KiB), record the exact integer and multiply by1024 for bytes. Require the
expected output digest. No model is loaded in this child. Parent is Torch-free.

This high-water mark includes imports, validation, warmup, allocator/workspaces,
inputs/output and hashing. It is NOT renderer-only or incremental peak memory.
Do not subtract a startup RSS reading. Startup high-water may hide an effect;
counter quantization is1024bytes. Guard MemAvailable is not the RSS endpoint.

Arms are baseline_A, baseline_B (identical native code) and candidate16M.
Both clean/adv conditions, three fresh processes per arm and condition.
Within each image/repetition shuffle six combinations with Python Random
seed `20261114 + 1000*master_image_index + repetition`, master index0..19,
repetition0..2. Smoke uses the same master index, never a renumbered subset.
No chunk-size, thread-count, image or repetition search after observations.

Pin child to logical CPUs0,1,2,3; four Torch/OMP/MKL/OpenBLAS threads, one
interop thread. Pi3B1GB remains in its declared undervoltage-limited600MHz
condition: powersave lease, actual clock594..606MHz before/after every child,
three child guard snapshots and parent watchdog no slower than2seconds.
Abort on temperature>=75C, MemAvailable<40000KiB, any swap topology/activity,
pswpin/pswpout/oom_kill increase, unexpected masks/governor/affinity or errors.
All masks/governor/swap/helper/timer state must restore to original readback.
Do not change supply, firmware, turbo, packages or SSH service.

## Prospective smoke policy and full eligibility

ONE technical smoke `memory_smoke_01`: image9 (representative) and image30
(first K300 attacked cache in the frozen cohort), selected before observing
RSS. Both conditions/three arms/three repeats =36 fresh processes,180seconds
per child and3600seconds campaign limit. Smoke verifies API/units/source,
schedule/completeness, every tensor/output hash, physical guards, child
reaping, controller completion and independent restore/readback. Any failure
stops without retry. Retain every partial output and terminal reason.

Smoke A/A bias/MDE are diagnostic, not an eligibility threshold. This policy
is fixed prospectively before the FIRST memory measurement. A two-image
technical smoke is never an efficacy result and cannot yield quality_pass.
It does not amend the closed latency pilot's different protocol or FAIL.

After terminal, independent artifact/hash audit and a saved `smoke_review.json`
must bind tag/commit/registration, smoke raw, gates and restore SHAs. Review
observed smoke runtime/storage and the fixed full budget before proceeding;
do not silently change the registered sample or thresholds if inconvenient.
The skill's smoke-before-full method review must be resolved before full.

ONE full `memory_full_01`, exactly all20 images =360 fresh processes,180seconds
per child and21600seconds campaign limit. Full requires smoke PASS, normal
controller completion, successful restore and saved independent review. Same
tag/source/registration, exclusive new directory, no full02 or replacements.

Full quality requires ALL360 scheduled jobs, hashes/physical/cleanup gates
and BOTH clean/adv A/A precision gates: abs(mean(log(A/B)))<=.02 and
MDElog<=.05. A failure leaves full diagnostic and closed; never filter images,
choose repetitions or borrow smoke precision to promote it. Changes require
a separate explicit review, not serial attempts to obtain PASS.

## Analysis fixed before observations

For each image/condition, numerator is median of three candidate samples;
denominator is median of all six baseline_A/B samples. Endpoint is their log
ratio. A/A uses log(median of A / median of B). Inferential unit is image.

Primary: attacked geometric mean candidate/baseline with image percentile
bootstrap20000, RNG2026111401; exact two-sided sign-flip over2^20 patterns.
Secondary clean uses RNG2026111402 and is descriptive, outside a confirmatory
family. A/A intervals use2026111403(clean)/2026111404(adv), diagnostic.
There is one confirmatory endpoint; no unregistered extra confirmatory tests.
Report raw p and its resolution2/2^20; no seed-level generalization.

MDElog = (t_(.975,n-1)+t_(.8,n-1))*sample_SD(logAA)/sqrt(n), constants
14.082586656645868 for smoke n2 and2.9539746046772377 for full n20.
Report d_z=mean/SD; if SD0, d_z=null and MDE0 is only observed resolution,
not equivalence. Physical/precision-failed complete data may have explicitly
diagnostic summaries; incomplete/corrupt cohorts have audit only, no filtered CI.
Store per-image medians and exact raw-line/job-index mappings for every number.

## Readiness verified before the scientific tag

Host phase/eligibility tests passed77 cases. Five sleeping-device fault cases
passed under engineering tag d58118f8162398925076c4ac0fe0d1db856694d0, with39
original-file SHAs and14 source/reference SHAs checked; independent restore
and readback passed. The original draft and all earlier raw data remain.
Scientific registration binds these receipts, runtime sources, exact caches,
original model/input hashes and this protocol. No page-cache flush, reboot or
allocator tuning is part of the experiment; reused filesystem caches are an
operating-condition limitation, not a cold-start benchmark. Do not report static byte estimates or functional QA as a
measured RSS benefit. RSS alone does not solve the failed NMS timing gate;
per-process fault/thread/cgroup trace and matched sham controls remain separate.


## Authorization and review boundary

Standing user instructions authorize algorithm optimization, code/QA and finite
experiments on this Pi; this is the renderer memory axis proposed before the
accepted full20 baseline. It is not permission inferred from NMS failure or
automatic goal continuation, and it does not reopen prior failed sessions.
Only one technical smoke is opened first. After its terminal/audit, stop for
review of the concrete smoke results and fixed full20 budget as required by
`.claude/skills/sponge-research/SKILL.md` section1.4; full is not launched
automatically. Preserve any failed/partial smoke and do not retry.

Protocol derived from DRAFT SHA256 12e1ad574ce2cd03b1f13d3132f02b5deaa530d4f67451d447965541518a2417.
