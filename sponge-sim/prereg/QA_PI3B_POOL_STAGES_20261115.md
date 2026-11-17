# Engineering stage/pool and kernel/controller metadata, one invocation

The earlier service QA remains closed PASS under03999b2 with ten observed
TIDs despite configured intraop4. This new finite diagnostic fixes stages
before observing their data. It neither reruns NMS nor estimates performance,
latency/RSS, simultaneous utilization, observer overhead or a causal effect.
Native TID creation between stages is temporal association, not ownership.

Freeze engineering tag `qa-pi3b-pool-stages-20261115`, sources/config and plan
before access. New workspace `/home/tanh/sponge-sim/pi3b_pool_stages_20261115`,
new service `sponge-pi3b-pool-stages-qa-20261115.service`, exclusive manifest
and result01. No retry/QA02 or old-file overwrite. Preserve FAIL/partial.

## Fixed sequence

- Existing User=tanh/python3.13.5/torch2.15.0+cpu/numpy2.5.4, CPUs0–3,
  OMP/MKL/OpenBLAS4, intraop4/interop1. No independent thread-setting search.
  Runtime cap180s, stop cap10s, KillMode=control-group, Type=exec.
- Readonly governor/swaps/affinity before; require Linux/aarch64, free
  MemAvailable>=400000KiB, sampled temperature<75C. No lease, governor/
  swap/controller/firmware/storage/power/SSH change or package download.
- Before library imports save raw cmdline, proc/cgroups and mountinfo,
  root controllers and optional kernel config flags/line numbers+fileSHA
  from /proc/config.gz and /boot/config-<kernelrelease>. Missing/unreadable
  files stay UNAVAILABLE/error, not0 or inferred kernel settings.
- Capture the following exact11 snapshots, no sampling-rate search:
  1. baseline, before NumPy/Torch import;
  2. numpy_import;
  3. numpy_mm_and_diagnostics: one CPUFP32 mm(ones512²,ones512²), exact512
     output check, delete arrays, then np.show_config;
  4. torch_import;
  5. torch_set_intraop (set4);
  6. torch_set_interop (set1);
  7. torch_ones (one512²FP32 CPU tensor);
  8. torch_mm (one512² mm of that tensor with itself);
  9. torch_validation_and_gc (all entries512/deviceCPU, delete tensors/gc);
  10. torch_diagnostics (record getthreads/getinterop/parallel_info/env);
  11. final_adjacent, no workload between10–11.
- Every snapshot reuses qualified all-TID inventory with original parser/
  source provenance, stable process/TID/birth/affinity and ancestor chain.
  Add per-TID comm after checking birth and mapped shared-library paths.
  Save cgroup.subtree_control at leaf/ancestors. Sequential observations
  are not atomic and miss TIDs created/destroyed between snapshots.
- Require all11 stages complete, same process/group, all TID affinities0–3,
  exact functional values/versions and >=4 TIDs at final snapshot. The final
  pair must have identical TIDs/births/config and nondecreasing counters.
  Between earlier stages retain all born/gone/reused identities, no filtering.
- Ancestor optional memory/cpu APIs may be unavailable. Do not treat this as
  missing events=0, automatically enable controllers, change boot flags or
  use leaf unlimited/missing as proof about every ancestor or scheduling cause.
- Save transitions as lists of born/gone(tid,start_ticks) and newly mapped
  libraries with temporal_only=True/library_ownership_identified=False.
  A block that combines mm/check/config does not distinguish those substeps.
- No model/cache/mask/NMS, perf_counter_ns brackets or ru_maxrss endpoint.
  Runtime/CPU counters in unit/proc metadata do not become operator timings.
- Wait only for the same owned service until terminal; transport failure is
  not terminal or permission to restart. Then collect exactly once, hash
  remote-before/local/remote-after, verify source/config==tag, no owned worker
  and original governor/swaps/affinity unchanged. Keep SSH open.

PASS_STAGED_POOL_METADATA_ONLY qualifies the reader/functional stage capture.
It does not solve NMS instability or attribute TIDs to libraries. Scientific
sham overhead/matched-predecessor/wrapper-versus-bare-kernel measurement still
requires a separately qualified runner and prospective PREREG/tag/smoke review.
All earlier NMS/timing/memory failures and accepted results remain unchanged.
