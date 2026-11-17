# DRAFT — renderer RSS with the user's intentional USB storage attached

Method proposal only. No new scientific registration/tag/workspace or RSS
measurement is authorized by this draft. The user has explained that the SSD
is attached for additional storage; do not request removal or silently mount,
format, eject, relocate data or enable disk swap.

## Why a separate condition is necessary

RSS-V1 tag289c2e3 rejected the initial USB guard before any child/RSS reading;
its one smoke remains FAIL, full cancelled, no retry. Its preflight omitted
the USB check before lease. This proposal responds to physical configuration,
not observed RSS effects: no renderer RSS has yet been obtained. It changes
the declared USB condition prospectively, never the old guard or its verdict.

Current metadata: ADATA SP900 behind SupTronics X89 (USB174c:0829), sda with
250069680sectors and sda1 with250067599; second LUN sdb has0sectors. At query,
neither disk/partition has a mount/holder; workspace device179:2 is the SD
card. Storage capacity is not extra RAM. Continued attachment does not imply
the SSD is already being used for the workspace or swap.

## Concrete USB-present contract to implement and lock before load

- New isolated study/workspace `pi3b_renderer_memory_usb_20261115`, never
  edit/reuse closed V1 run directories. Copy qualified source with original
  file/range/SHA; document every difference and test before a new tag.
- Keep both existing devices attached. Freeze identities/topology, vendor/
  model, capacity, partition layout and mount/holder state at registration.
  Record raw block-I/O counters in metadata but bind a fresh counter/lifetime
  baseline before EACH phase; using the SSD outside a measurement phase is
  not an exclusion. This clarification is before any USB-present RSS data.
  Require the same devices, no additions/removals,
  no media/reset/re-enumeration or unexpected mounted volume/holder.
- Keep caches and measurement logs on their existing SD paths; original
  cache-manifest SHA remains
  `61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165`.
  Validate filesystem/device identity before the lease; do not move files to
  the SSD under this protocol. Using it as the active data disk is a different
  I/O condition and must not be silently substituted.
- Require USB disks idle before the lease. Sample their block counters before
  and after each child and in the parent watchdog; completed read/write/
  sector counters must remain unchanged, in-flight requests zero, identities
  unchanged. Any I/O, hotplug, missing/malformed readback or topology change
  aborts once and preserves all data. Metadata sampling is included in the
  declared child/parent overhead; no claim of exact operator-only cost.
  Compare all available block-stat fields, including discards/flushes when
  present, not just read/write totals. Bind diskseq, USB device addresses and
  mount namespace within each phase to detect reset/re-enumeration. Static
  model/topology identifiers are not a cryptographic proof of physical identity.
- Add read-only USB/topology/I/O/workspace checks BEFORE any swap/governor
  lease or run-directory allocation. This fixes the preflight ordering gap;
  initial mismatches do not start a scientific attempt. Keep runtime checks
  as well. Test idle match, wrong identity, extra/missing device, pending I/O,
  changed counters/reset, mounts/holders and missing readbacks.
- Same temporary lease and independent restore mechanism; no supply/firmware/
  package/affinity changes outside the registered setting. SSD power draw is
  part of this new condition, not declared causal or compensated by changing
  clocks. No USB benchmark, voltage manipulation or swap activation.

## Scientific design retained, not selected for a better outcome

Retain exactly the V1 nine-runtime algorithm bodies except explicit namespace,
USB-readback/preflight/audit changes; baseline32M and candidate16M, no chunk
search. Same40frozen caches/20previously-observed PGD pairs, CPUFP32/640²,
600MHz sampled band594..606MHz, CPUs0..3/four intra-op/one interop, three
fresh processes per condition/arm, same master-index randomization.

One technical smoke images9+30 (K300 included),36children/180s per child/
3600s campaign; structural, physical, parity, API/unit, child cleanup and
independent restoration gates. Smoke A/A/MDE descriptive, no efficacy claim.
One full20/360children/21600s campaign only after successful smoke and method
review. No retries, replacement images, extra seeds or filtered subcohorts.

Retain full A/A bias absmeanlog<=.02 and MDElog<=.05 independently for BOTH
clean/adv; thermal>=75C, MemAvailable<40000KiB, swap/pswpin/pswpout/oom change
still abort. Same whole-process ru_maxrss after digest (not isolated renderer
peak), output SHA parity, medians/pooled-baseline ratios, primaryadv,
descriptiveclean, bootstrap20000/exactsignflip and fixed RNGs/constants as
V1. Preserve startup-floor/quantization/reused-cohort/one-board limitations.

New numbers compare randomized arms WITHIN the USB-present session; never
treat the old USB-absent main latency or V1's zero RSS as a paired baseline.
This does not solve the rejected NMS timing gate or establish DoS.

## Required before a new science tag

Explicit method review of this condition change; implement/copy/source-bind
the exact USB contract, host regressions and real-device read-only USB API
qualification. Independently verify supervisor/restore behavior for the new
namespace before resource endpoints. Freeze protocol/config/source/material
SHAs and one finite schedule before the first RSS. Record user/UTC/local
timestamps and that this was designed after the physical V1 guard failure.

If the user needs a mounted/active SSD during measurements, review that
different condition instead of weakening the idle-USB gate after failure.
No workload has been started from this draft.

Implementation stage1: new standalone `usb_guard.py` and41synthetic host
regressions. Reads disk/partition identities, all USB device descriptors
(including internal hub/Ethernet), holders/mounts, diskseq/stat and SD path
bindings. Missing required metadata fails; optional manufacturer/product
absence is explicitNone. No older guard, renderer or protocol was changed.
Actual-device metadata QA and runner/auditor integration are still required.
Stage1 metadata QA has since passed under465f6e5 (two read-only frames,
source/raw hashes retained). Stage2 now copies qualified runtime with source
provenance: frontend USB/original-state validation before directory allocation,
payload recheck before lease, fixed preflight hash in collector/children and
independent auditor validation. Non-USB guard/algorithm/statistics AST unchanged.
Host regression final130PASS; initial129PASS/one UTF8 test-loader failure kept
and corrected without relaxing assertions. New-namespace sleeping-supervisor
QA remains pending, no new scientific registration or endpoint.
