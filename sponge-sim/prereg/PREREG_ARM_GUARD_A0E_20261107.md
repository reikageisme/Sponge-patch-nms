# A0E sleeping own-child cleanup controls on A36 — no load benchmark

## Before execution

User authorizes ongoing phone ARM code/tests with SSH left open. A0D confirms
SM-A366B/a36xq,QTI/SM6475,Android16,arm64-v8a,MemTotal7529500kB. Battery API
worked in A0C at24percent/DISCHARGING; that is historical, not current power.
Load gates remain closed. Old four pin-profile FAILs and all raw remain.

Linux/WSL checkpointa939028 direct-child controls passed under parent hard
exit/SIGKILL, plus a normal TERM/KILL cleanup. This does not establish Android
behavior. A0E runs precisely that sleep-only mechanism on the actual device,
before any Torch load, matrix/model/pin/sampler/performance QA. No reaction
latency or throughput endpoint is measured. User-idle/mobile-off/SOC gates
for future scientific timing are not inferred from this engineering check.

## Fixed finite design

ONE invocation of parent_death_local_check.py, four exact files bound in
guard_a0e_lock.json and tag prereg-arm-guard-a0e-20261107 BEFORE source copy:
checks.py,linux_observe.py,posix_runtime.py,parent_death_local_check.py.
Existing Ubuntu/proot venv, workspace bind ~/sponge-sim:/root/sponge-sim.
NEW source studies/arm_guard_a0e_20261107_01; NEW result directory
results/phone_a36/guard_a0e_20261107_01, with capture child directory created
exclusively by the script. Retain all copied source/raw/stdout/stderr/exits.

The check creates only its OWN short-lived children. Two predetermined cases:
creator os._exit23 and creator SIGKILL, each with a sleeping direct child after
ordinary exec. Read back child death signal/PID/PPID/PGID. Require signal9,
correct parent/group, direct child SIGKILL and reap. A third own sleeper ignores
TERM and must be KILLed/reaped by stop_group. Deadline controls are the unchanged
script's5/10s waits and .2s TERM grace, not measured reaction bounds. Sleeper
self-exits after60s even if faulty. Outer invocation bound120s+kill5s.

Only the test Python process toggles/restores its own child-subreaper flag;
no Android/system setting, privilege change, named-process kill, attachment
to a pre-existing process or service shutdown. Kernel syscall denial or proot
semantics failure is a preserved result: no bypass, source edit, alternative
runtime or retry in A0E. On observation timeout inspect this SAME invocation
and recorded owned PIDs; do not start another. Final owned-process state must
be reviewed before claiming the check ended cleanly.

## Gates and interpretation

Five local control checks plus subreaper restoration must all pass for this
finite mechanism check; any error/missing receipt is FAIL/incomplete. This
never sets profile_qualified or study-quality PASS. No Torch import/warmup,
matrix/inference, affinity mutation, CPU stress, sysfs/battery reread, camera,
package installation, permission change or power/network setting changes.
All files stay within workspace; byte hashes remote/local must match.

Even PASS covers direct sleep-only children, not arbitrary descendants,
stalled-parent recovery, actual sensor/reaction/observer overhead, live thermal
registry, model import or a segmentation pin profile. Those need separate
prospective controls and load protocol. Preserve old results and leave sshd
RUNNING throughout this continuing ARM campaign, including on test failure.
