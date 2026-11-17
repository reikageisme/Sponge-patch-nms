# DRAFT: A36 full100 with external power — new condition, not E5 replication

User on08/11 reports100percent, enabled SSH and explicitly says to run. They
want the Snapdragon6Gen3/nominal8GB phone used as an ARM development surrogate
while considering a physical Pi4 2GB. This is prospective authorization of a
different power condition. Preserve the old E5 30..80+charging protocol/raw;
do not relax its gates or re-score its four historical pin FAILs. All old GPU,
laptop and A36 results have already been observed; no v2 model timing exists.

## Proposed fixed power condition

An explicit policy name `full_100_external`, never auto-selected from results.
Require battery percentage EXACTLY100 for every preflight/load/rest sample,
known plugged source AC/USB/WIRELESS/DOCK and known status CHARGING/FULL/
NOT_CHARGING. DISCHARGING, unplugged, missing/unknown fields or percentage99
end the session without retry. GOOD battery health remains required by the
API parser. Retain original status/source in every frame; FULL remains
charging=False. Do not infer supply from current sign or call FULL charging.

Reason: this is an externally powered ARM development surrogate at the state
the operator actually authorizes. It is not the original actively charging
30..80percent condition and not evidence of a Pi power/thermal envelope.
Observed valid samples over the prospectively fixed stable-power window do
not prove voltage/current was constant between samples. A reading consistent
with external power is not a measurement of board/input power draw.

Legacy policy remains the DEFAULT and still rejects100. New profile requires
explicit API source/status; old sysfs-only or synthetic assumed-charging
readings cannot silently enter it. Session-start journal records the full
policy, including selected power profile, before any child is created.

## Thermal and other gates remain

Any VALID registered temperature>=70C or battery>=40C interrupts the worker.
Resume eligibility requires ALL zones<55C and battery<38C; no interrupted burst
is retried. Three consecutive interruptions end session; completed safe burst
alone resets the counter. Freshness, all-frame durable logging/ACK, deadlines,
ordinary rest/preload per-sensor baseline, source/runtime/input locks and
pin/A/A/reference/MDE gates remain. Missing/unresolved sensors do not become0.

Kernel thermal sysfs ABI specifies milli-Celsius for temp. A0 contains two
vendor nodes sys-therm-1/2 with raw481271/662478 and remote/sentinel-like nodes.
The generic ABI alone does not resolve those vendor exceptions. Do not scale
them by a guessed factor, discard by magnitude or call them cooled. Resolve
sensor semantics/validity from primary driver/metadata evidence BEFORE a
registered live registry; keep all raw and exclusion reasons. Current loading
remains closed while that registry and collector are incomplete.

## Before any load or timing

Implement and host-test the explicit policy without modifying accepted/rejected
old runs. Read live source/status and thermal metadata under its own NEW tag,
using the fixed native CLI fingerprints from A0D. Validate bounded native/proot
transport and shared monotonic acquisition timestamps, then sensor/logger
failure/termination/reaction QA on A36. A0E direct sleep-only parent-death PASS
does not establish these remaining properties or a whole descendant tree.

Resolve/register exact sample cadence/deadlines/stability duration, registry,
state, runtime/CPU/source and fixed workload BEFORE model import/warmup/load.
Use the already proposed finite four-cell mechanism plan, no fastest-core
selection/retries until PASS. Later segmentation requires independent profile
qualification and model A/A/MDE/reference gates. No standalone load command
is authorized merely by this DRAFT; no device launch occurs in host tests.

Keep SSH open through the whole ARM campaign as the user instructed. Confirm
current idle/mobile-off/minimal-WiFi state at the actual scientific timing
step. User's100percent report is not sensor data or proof of current temperature.
