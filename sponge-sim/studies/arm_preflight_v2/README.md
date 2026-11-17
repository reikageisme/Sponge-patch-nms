# Offline audit and draft ARM checks

These files do not replace `e5_phone/run.py`. Separate metadata-only A0/A0B/A0C
phone readouts are documented below; no v2 phone Torch workload, affinity QA
or research timing measurement has been performed.
Local Ubuntu/WSL engineering checks use own-process metadata, sensor fixtures
and a sleeping child; their success does not qualify Android/proot.

- `audit_saved.py` reads existing M6 raw and historical A36 pin summary. It
  recomputes flags, completeness and MDE using the original read-only analyzer,
  asserts agreement with the saved summary and writes a NEW exclusive-create
  JSON. Per-reference raw line numbers and source SHA256 are included.
- `checks.py` contains a proc-stat parser, snapshot comparison, a pure safety
  state machine and an injected own-child supervision contract. Synthetic
  tests cover idle-thread artifacts, bad masks, thread churn/TID reuse,
  thresholds, hysteresis, consecutive interruptions, stale/missing data,
  battery/charging gates, timeout and kill escalation.
  After the user's08/11 explicit100percent instruction, a SEPARATE optional
  `full_100_external` policy is implemented; default legacy30..80+charging is
  unchanged. The new mode requires exactly100, known external source/status,
  keeps FULL/NOT_CHARGING as charging=False, and preserves thermal thresholds.
  Session-start events now include the selected policy. This has host tests
  only, no live collector/profile clearance. See
  `prereg/DRAFT_ARM_EXTERNAL_FULL100_20261108.md`.
- `linux_observe.py` collects raw stat/status and scheduler masks for this
  process's TIDs, checks identity/churn, makes one finite own-TID pin attempt,
  and maps explicitly declared sensor types/units and battery status. It never
  declares a CPU-load/residency PASS from mask readback. Direct reads are
  synchronous; use a bounded adapter rather than calling them in a supervisor.
- `posix_runtime.py` supplies candidate bounded sensor/event helpers and a new
  owned-session process-group adapter. Its Linux bootstrap now arms/verifies
  SIGKILL on creator-thread death BEFORE exec, with parent identity checks on
  both sides. All helpers/workers use it and startup cost counts in deadlines.
  Unsupported/raced setup never executes the payload. Forked descendants do
  not inherit this signal; arbitrary tree cleanup is still open.
  Helper errors/timeouts clean up that
  helper before propagation. Events use exclusive files, fsync and hash ACK;
  an exited worker leader with live group members raises instead of returning
  success. These adapters have local/mock validation only, not phone clearance.
- `session.py` adds a fixed burst ledger, observed stable charging window,
  per-sensor baseline BEFORE load, ordinary 60..180s rest and safety cooldown.
  Interrupted/not-started bursts remain in the ledger and are never retried;
  successful control flow never promotes a scientific quality result.
- `pin_analysis.py` is a candidate analyzer for NEW snapshots: exact all-TID
  masks, stable identities, >=20 active observations, >=99% active last-CPU
  share, original CPU-time/wall bounds, and process/TID accounting. Tick and
  endpoint-read uncertainty is explicit; the maximum accounting slack fraction
  is mandatory and must be fixed before device QA. Incomplete coverage is not
  silently accepted. This cannot re-score the old phone's four FAIL records.
- `pin_worker.py` implements the fresh-process Torch mechanism worker with
  matched process/perf clocks, snapshots + raw flush inside the QA window,
  version/init SHA checks and four pin/pool orderings. It has fake-runtime
  tests only; WSL has no Torch. Two intra-op threads on one CPU intentionally
  test inheritance; every result has profile_qualified=False. `execute_child`
  maps failed preparation/malformed results to exit65, while a COMPLETE
  diagnostic FAIL remains exit0 data. Nonfinite checksums are preserved as
  JSON null with output_finite=False and a diagnostic FAIL. No load CLI.
- `qa_session.py` joins the four fixed cells to the guard/rest coordinator.
  CellSpawner binds source/config bytes, prepares NEW workspace-only files,
  launches fresh owned groups and propagates execute_child's exit code.
  Partial/not-started cells are retained without retry. A separate post-cleanup
  terminal ACK is required; an earlier coordinator ACK does not replace it.
  The extra parent-PID startup check is separate from OwnGroup's direct-child
  death signal; neither establishes Android/proot tree cleanup. This is a callable
  control core, not a registered/qualified phone entry point or load permission.
- `metadata_only.py` and `battery_paths_only.py` are registered read-only A0
  tools, not load launchers. Phone readouts are documented in
  `docs/reports/A36_TAILSCALE_A0_20261107.md`. Sensor/battery gates remain closed.
- `termux_power_metadata.sh` performed one separately tagged A0C native-Termux
  read after the user installed the CLI and invited SSH. All 14 captured files
  match remote byte hashes; `power_a0c_20261107_01/capture/battery.raw.json`
  reports 24%, DISCHARGING/UNPLUGGED and temperature35.7. This is saved metadata,
  not live supervisor telemetry. The main app reports googleplay.2026.10.09;
  CLI0.59.1 is not the companion APK version. Current Google Play source handles
  BatteryStatus inside the main app, so API success does not establish that
  the newly installed companion was necessary or used. No migration is needed.
- `termux_power.py` parses raw bytes without creating a timestamp. The draft
  pure joiner requires explicit same-clock query/thermal acquisition intervals,
  exact registered zone IDs and freshness of BOTH sources. Numeric Celsius is
  never divided again; plugged alone/FULL/NOT_CHARGING is not charging. Missing,
  duplicate, contradictory, nonfinite and malformed input rejects. GOOD health
  is a NEW prospective adapter eligibility condition, not a historical gate.
  This is not yet wired into a device collector or included in old bundles.
  See `docs/reports/A36_TERMUX_POWER_A0C_20261107.md` for raw/source limitations.
- `arm_hardware_metadata.sh` is a separately tagged A0D fixed read-only capture:
  SM-A366B/a36xq, QTI/SM6475, arm64-v8a, Android16/SDK36 and MemTotal7529500kB.
  Native CLI bytes/hashes are preserved; pm path failures remain failures.
  See `A36_HARDWARE_A0D_20261107.md`. SSH is kept open under the new user rule;
  no battery repeat, Torch import or load occurred in this scope.
- `build_draft_bundle.py` exports source hashes and four unresolved templates
  to a NEW directory. `artifacts/arm_preflight_draft_20261107/bundle_01` is
  DRAFT/UNRUN and refuses load validation. Do not overwrite it or equate DIST
  metadata with an imported Torch runtime-version lock.
- `local_linux_check.py` is an engineering-only Linux integration check. Its
  saved receipt is `results/arm_observer_local_20261107/native_01/receipt.json`.
  It checks no model, load benchmark, CPU-time gate or phone sensor. It rejects
  an existing output directory; preserve the fixtures and receipt.
  `native_02` adds all-frame capture and one coordinator session with a real
  60-second rest. Its `executed_source` files match receipt SHA exactly. The
  subsequent fresh-guard reuse check and pin analyzer have host tests only;
  do not attribute those changes to this older native checkpoint.
- `qa_local_check.py` is a separate Linux engineering check for the new
  composition/exit-status contract. It uses local sensor fixtures and a stub
  worker with the two actual exit functions, no Torch, affinity or matrix work.
  Its source snapshot/receipt must remain distinct from old native checks and
  from any future Android/proot qualification.
  Its first run is saved at
  `results/arm_qa_session_local_20261107/native_01/receipt.json`: six control
  checks passed with four fixture frames and no Torch/affinity/model work.
  See `docs/reports/ARM_QA_SESSION_LOCAL_20261107.md` for scope and source SHA.
- `parent_death_local_check.py` adds a NEW local Linux check with sleeping
  children only. Parent hard exit and parent SIGKILL both kill the direct
  worker after exec; its original guard is read back inside that worker.
  A subreaper setting in the check process alone permits reaping its own
  orphans and is restored. The new check and the QA composition under this
  bootstrap are saved separately; see `ARM_PARENT_DEATH_LOCAL_20261107.md`.
  A separately tagged ONE A0E run has now also passed ON A36/Ubuntu-proot:
  direct sleeping-child parent exit/SIGKILL and normal TERM/KILL cleanup only.
  See `A36_GUARD_A0E_20261107.md`; source/raw/proot warning are preserved.
  This does not qualify arbitrary descendants, sensor reaction or Torch load.

Tests, without device/load:

```powershell
python -m pytest sponge-sim/tests/test_arm_preflight_v2.py sponge-sim/tests/test_arm_linux_observe.py sponge-sim/tests/test_arm_posix_runtime.py sponge-sim/tests/test_arm_session.py sponge-sim/tests/test_arm_pin_analysis.py sponge-sim/tests/test_arm_pin_worker.py sponge-sim/tests/test_arm_qa_session.py sponge-sim/tests/test_arm_metadata_only.py sponge-sim/tests/test_arm_draft_bundle.py -q -p no:cacheprovider
python -m pytest sponge-sim/tests/test_arm_termux_power.py -q -p no:cacheprovider
```

Audit, using an output path that does not exist:

```powershell
python sponge-sim/studies/arm_preflight_v2/audit_saved.py --output <new-output.json>
```

## Deliberate limits

No device-qualified segmentation/QA worker or phone runner ships here. Before phone use
it must verify actual sensor IDs/units/permissions, measure reader/logger cost
and composed detection/termination delays, preserve EVERY sensor frame/partial
burst, and validate its owned process group INCLUDING descendants on Android.
The bounded reader now saves every COMPLETED valid/invalid frame before ACK,
with sequence and config SHA. Timeout can leave a gap/partial file; it is kept,
the reader is poisoned, and the session must end without retry. Native checks
cover direct sleeping children, including direct-child parent death locally,
not Android/proot descendant/parent-death qualification. Missing telemetry/log
ACK must invalidate the session and stop load; no existing raw may be replaced.
No command here is offered for starting a phone experiment.

The 6-second freshness allowance and 180-second safety/worker deadlines in
`Policy` are **draft test defaults**, not previously registered values or
measured feasibility estimates. A cooldown observation does not restart an
aborted burst. The session coordinator and analysis must preserve partial
blocks and their reasons; successful completion alone resets the consecutive
thermal-stop counter. Ordinary 60-second rest and per-sensor baseline+1C/180s
rest logic is now implemented in the control coordinator. It also compares
battery temperature with its own baseline+1C. The stable-power window needs at
least two valid charging observations spanning its explicit duration; gaps
beyond freshness reject the session. This is observed stability, not proof
that charging never changed between samples. An already-used guard cannot be
reused to create another session. Cadence plus helper deadlines
and helper/worker TERM/KILL waits must be budgeted together BEFORE any device
registration. Configured timeouts are not proof of actual hardware reaction
bounds or safety under a stalled parent/OS scheduler.

`thread_interval` deliberately produces diagnostics rather than an automatic
profile PASS. Active last-CPU share is not continuous CPU residency. A profile
also needs fresh-process pinning, exact masks for all TIDs, sufficient active
observations, original CPU-time/wall bounds, finite outputs, stable thread
coverage and the new preregistered acceptance rules. Missing TIDs never silently
become good samples. No new result changes the historical four FAILs.
The matched-clock worker and callable session/spawn core are implemented but
not run under real Torch or on A36. A registered device entry and physical guard QA remain
missing; fixture PASS is not a profile PASS. A/A/MDE/reference gates still
belong to the later model study. A0/A0B found no verified live SOC/charging
source. A0C now captures a working API battery response but supplies no monotonic
live join or device-qualified collector. Earlier thermal raw scales remain
unreviewed; earlier CPU raw exceeded the conservative 70C interpretation.
Do not run load or silently discard a hot/ambiguous node.
