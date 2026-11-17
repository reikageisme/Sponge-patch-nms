# Engineering supervisor QA for the integrated NMS material worker

No scientific timing/model run is authorized by this tag. Freeze
`qa-pi3b-nms-predecessor-supervisor-20261115` before device access; new isolated
workspace `/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115`. Preserve all
earlier negative/positive protocols and original files. Exactly one set of
five sleeping cases; stop at first unexpected failure, no retry/QA02.

## Fixed engineering changes

- Copy record/System/validate_snapshot/Lease from qualified USB controller,
  unchanged AST, with file/range/SHA. Copy USB guard/physical guard and
  all-thread inventory unchanged AST. New entrypoints accept only qa and
  functional; no timing or scientific-registration branch exists.
- Same runtime governor/swap mask lease and independent ExecStopPost restore,
  KillMode=control-group, User=current authorized SSH user, TimeoutStopSec120.
  Add unit CPUAffinity0–3 and process-local OMP/MKL/OpenBLAS4, YOLO_OFFLINE=true,
  YOLO_AUTOINSTALL=false/config path owned by new workspace. No global power,
  firmware, package, SSH, USB mount/eject/format or controller changes.
- Same static idle SSD topology/SD dev179:2, only workspace path changes to
  this new namespace. Readonly frontend storage+original-state validation
  before run allocation/lease; saved phase frame rechecked before mutation,
  never refreshed after I/O. All phase counters/generation/path/mount rules
  from prior USB guard remain, root/cache identity/source hashes bound.
- Initial controller_lock functional/scientific/empirical flagsFalse. A
  separate future functional activation must bind actual passed five-case
  receipt, exact controller source/config and prospective material plan/tag.
  Missing/malformed/unqualified activation refuses BEFORE lease/model/run.
  Functional source exists for host checks but is not executed in this QA.

## Five cases, exactly once

Use shared unit `sponge-pi3b-swapguard-v2.service` to prevent overlapping
resource leases, unique run names qa_normal_01, qa_mainkill_01,
qa_childkill_01, qa_timeout_01, qa_disconnect_01. Before every launch require
same unit inactive/MainPID0 and consistent original snapshot. No resumption
or reuse of prior run directories.

- normal: sleeping readiness15s, supervisor cap90s, require normal completion;
- mainkill: sleeping60s/cap120s, readiness then SIGKILL ONLY verified service MainPID;
- childkill: sleeping60s/cap120s, readiness then SIGKILL ONLY verified childPID/startticks/cgroup;
- timeout: sleeping90s, supervisor cap45s, require runtime termination;
- disconnect: readiness15s/cap90s; terminate ONLY owned local SSH frontend,
  verify same invocation continues and completes, no relaunch.

READY requires no Torch/scipy in payload, same MainPID/InvocationID as the
record, live owned child birth and cgroup, governorpowersave/swapOFF/runtime
masks and saved USB binding match. Every case including timeout requires READY
under the unchanged qualified-driver assessment; an earlier timeout is FAIL,
not a waiver. Do not invent missing files or relabel a failed observation PASS.

After authoritative terminal of each case require original governor, swap
topology/priority, timer/helper/setup states and no masks restored; original
child no longer exists with same birth. Preserve original launch/stdout/
fault/restore/journal warnings. Transient frontend failure is not job terminal:
inspect only same owned service/state, never restart or fetch a live run.
While QA is live, assistant waits only for its owned driver; no git/files/
analysis/tests/browser work concurrently. Keep SSH/sshd open throughout.

Only after all five terminal collect originals once, SHAremote-before/local/
remote-after, compare current sources/config/references to tag/archive and
independent restore/readback. Report every partial/failure/warning under four
CLAUDE sections. Native material/source version/parity40cases and actual
timing/sentry/warmup/reference/analyzer remain separate gates. Sleeping tests
do not prove power-loss/kernel-stall recovery or arbitrary-model behavior.
