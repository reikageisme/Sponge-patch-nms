# Engineering QA — Linux counter API only, no NMS workload

Qualify the existing counter reader on real Linux/aarch64 under engineering
tag `qa-pi3b-nms-counters-20261115`. Source is unchanged from d58118f and has
ten synthetic host tests. ONE invocation in a previously absent workspace
`/home/tanh/sponge-sim/pi3b_nms_trace_20261114`, no retries on failed API.

Take exactly two sequential self-process/thread/cgroup snapshots, no sleep,
model, tensor, NMS, operator clock bracket or ru_maxrss. The recorded CPU
clocks are raw API provenance for the observer, not an operator benchmark.
Check identity/monotonic fields, expected process/thread affinity and explicit
UNAVAILABLE for one absent optional file. Missing real cgroup files retain
UNAVAILABLE; never impute zero. Preserve both raw snapshots and failures.

No lease, swap/governor/affinity/power/package/USB/mount mutation. Read-only
metadata is allowed with the user's SSD attached; it is not the closed RSS
protocol or a relaxation of its guard. Check service idle before invocation
and compare governor/swaps/affinity before and after. Keep SSH open.

Save original remote JSON once; verify source and remote/local/result SHA.
Any failure stops, no model is launched next. Passing only qualifies these
counter APIs and observer semantics: thread-pool worker inventory, sham
instrumentation overhead, matched predecessor schedule and NMS mechanism
still need separate source/protocol/QA before measurements.
