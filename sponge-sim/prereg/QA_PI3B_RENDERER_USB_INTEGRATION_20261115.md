# Engineering QA — USB-present runner/supervisor, no resource endpoint

New source/workspace `pi3b_renderer_memory_usb_20261115` keeps the qualified
USB helper byte-identical to metadata tag465f6e5. Renderer, cache, statistics,
System/Lease/record/validate_snapshot bodies are unchanged from qualified V1.
Only namespace, USB contract/baseline plumbing, preflight and audit differ.
The closed USB-absent V1 smoke remains0RSS/FAIL/full cancelled, no retry.

Before a new scientific registration, host tests must verify: USB refusal
before run-directory allocation; payload recheck before Lease.apply; exact
tag/commit/phase/config/contract binding; sampler baseline and hash propagation
through every child/parent row; independent recomputation by auditor; rejection
of missing/changed baselines; full eligibility binds the smoke USB hash. The
non-USB guard AST and unchanged algorithm/statistics AST are compared to the
qualified sources. No host synthetic result becomes an empirical RSS result.

Engineering tag `qa-pi3b-renderer-memory-usb-20261115` freezes eleven Python
files plus cache/functional-audit/USB-contract references. Scientific file is
absent and empirical_endpoints_enabled=False. The existing metadata-only Pi
workspace has exactly usb_guard.py and its original qa_metadata_01.json;
preserve both bytes, deploy only absent new files, no overwrite or cache copy.
Read-only preflight requires shared service inactive/MainPID0, original stable
lease configuration, known qualified source and idle matching USB/SD paths.

Five sleeping-only cases, one each in the new workspace:

|Case|Sleep/RuntimeMax seconds|Fault|
|---|---|---|
|qa_normal_01|15/90|none|
|qa_mainkill_01|60/120|verified owned main PID/invocation SIGKILL|
|qa_childkill_01|60/120|verified child PID/startticks/cgroup SIGKILL|
|qa_timeout_01|90/45|manager timeout after READY|
|qa_disconnect_01|15/90|terminate owned local SSH client only|

READY verifies no Torch/scipy, powersave/no swap/expected masks and the saved
USB baseline still matches. Fault cases require the expected failure, original
child identity gone and independent ExecStopPost restoration/readback matching
original governor/swap/helper/timer/masks. Normal/disconnect must end normally.
No model/tensor/render/ru_maxrss/operator latency, no disk I/O benchmark,
mount/eject, package or supply changes. Keep sshd open.
Normal sleep is15s rather than the prior5s, chosen before this QA to leave
room for the added independent USB readiness checks over SSH; it is not a
measured renderer interval or a change made after a case failure.

One failed assertion stops all remaining cases, no retry. Capture all intent,
actions, logs, warning journals and assessments. After service terminal fetch
originals once into fresh destinations; compare remote/local/remote hashes,
all deployed source/reference hashes and old metadata JSON unchanged. Retain
warnings and failures. Sleeping-child QA is not power-loss/arbitrary-descendant
or real-renderer peak-RSS qualification. PREREG/tag and one technical smoke
still precede any resource endpoint; no automatic full from engineering QA.
