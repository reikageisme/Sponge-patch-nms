"""Unrun-on-device v2 building blocks; no torch, proc/sysfs reads or deployment.

Thresholds 70/40 -> <55/<38 and SOC30..80 come from PREREG_E5_phone B.
Freshness and cooldown deadlines are NEW draft choices, not retroactive rules.
"""
from dataclasses import dataclass
import math

PLUGGED_SOURCES = frozenset({'PLUGGED_AC','PLUGGED_USB','PLUGGED_WIRELESS','PLUGGED_DOCK'})


def parse_stat(text):
    """Linux proc stat: comm may contain spaces and closing parentheses."""
    fields = text[text.rindex(')')+1:].split()  # index0 = kernel field3
    return dict(state=fields[0], ticks=int(fields[11])+int(fields[12]),
                starttime=int(fields[19]), last_cpu=int(fields[36]))


def thread_interval(before, after, allowed):
    """Snapshot dicts: TID -> {ticks,starttime,last_cpu,mask,state}.

    Last-CPU samples from active TIDs are diagnostics, not proof of continuous
    residency. Mask equality is checked for EVERY TID, including idle ones.
    A changing thread set is inconclusive and must not silently become PASS.
    """
    allowed = set(allowed)
    stable = before.keys() == after.keys() and bool(after) and bool(allowed)
    masks_ok = all(set(r['mask']) == allowed for r in [*before.values(), *after.values()])
    active, inside, ticks = 0, 0, 0
    for tid in before.keys() & after.keys():
        a, b = before[tid], after[tid]
        delta = b['ticks']-a['ticks']
        if b['starttime'] != a['starttime'] or delta < 0:
            stable = False
            continue
        if delta > 0:
            active += 1
            inside += b['last_cpu'] in allowed
            ticks += delta
    return dict(complete=stable, masks_ok=masks_ok, active_samples=active,
                active_inside=inside, active_ticks=ticks,
                active_share=None if not active else inside/active,
                new_tids=sorted(after.keys()-before.keys()),
                missing_tids=sorted(before.keys()-after.keys()))


@dataclass(frozen=True)
class Reading:
    sampled_s: float                  # same monotonic clock as supervisor
    zones_c: dict                     # explicit registered ID -> Celsius
    battery_c: float                  # REQUIRED separately identified sensor
    battery_pct: float
    charging: bool                    # adapter must resolve status explicitly
    power_source: str | None = None    # actual raw API source; never inferred
    power_status: str | None = None    # FULL remains FULL, not charging=True


@dataclass(frozen=True)
class Policy:
    expected_zones: frozenset         # locked in preflight, never learned hot
    max_age_s: float = 6.0            # DRAFT; 5s cadence + 1s allowance
    max_cooldown_s: float = 180.0     # DRAFT safety deadline, not old rule
    worker_timeout_s: float = 180.0   # DRAFT per-burst feasibility deadline
    power_profile: str = 'legacy_30_80_charging'

    def __post_init__(self):
        if not self.expected_zones or any(not math.isfinite(v) or v <= 0 for v in (
                self.max_age_s, self.max_cooldown_s, self.worker_timeout_s)):
            raise ValueError('nonempty sensor set and positive finite deadlines required')
        if self.power_profile not in ('legacy_30_80_charging','full_100_external'):
            raise ValueError('explicit known power profile required')

    def classify(self, r, now):
        if not isinstance(r, Reading):
            return 'invalid_telemetry'
        values = [r.sampled_s, r.battery_c, r.battery_pct, *r.zones_c.values()]
        if (set(r.zones_c) != set(self.expected_zones)
                or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values)
                or not 0 <= now-r.sampled_s <= self.max_age_s):
            return 'invalid_telemetry'
        if self.power_profile == 'legacy_30_80_charging':
            if not 30 <= r.battery_pct <= 80 or r.charging is not True:
                return 'power_gate'
        else:
            if (not isinstance(r.power_source,str) or not isinstance(r.power_status,str)
                    or r.power_source not in PLUGGED_SOURCES | {'UNPLUGGED'}
                    or r.power_status not in ('CHARGING','FULL','NOT_CHARGING','DISCHARGING')
                    or type(r.charging) is not bool
                    or r.charging != (r.power_status == 'CHARGING')):
                return 'invalid_telemetry'
            if (r.battery_pct != 100 or r.power_source not in PLUGGED_SOURCES
                    or r.power_status == 'DISCHARGING'):
                return 'power_gate'
        if r.battery_c >= 40 or any(t >= 70 for t in r.zones_c.values()):
            return 'hot'
        return 'ok'

    def cooled(self, r, now):
        return (self.classify(r, now) == 'ok' and r.battery_c < 38
                and all(t < 55 for t in r.zones_c.values()))


class Guard:
    """Parent-side decisions. Never restarts an interrupted measurement.

    Three consecutive thermal interruptions end session; only a COMPLETED
    safe burst resets count. Cooling alone never resets it. A policy rejection
    before spawn launches nothing. Persist EVERY event, including partial runs.
    """
    def __init__(self, policy):
        self.policy = policy
        self.state = 'READY'
        self.stops = 0
        self.cooling_since = None
        self.session_started = False

    def observe(self, reading, now):
        if self.state == 'END':
            return 'end'
        reason = self.policy.classify(reading, now)
        if reason not in ('ok', 'hot'):
            self.state = 'END'
            return reason
        if self.state == 'COOLING':
            if now-self.cooling_since >= self.policy.max_cooldown_s:
                self.state = 'END'
                return 'cooldown_timeout'
            if self.policy.cooled(reading, now):
                self.state = 'READY'
                return 'cooled'
            return 'cooling'
        if reason == 'hot':
            self.stops += 1
            self.cooling_since = now
            self.state = 'END' if self.stops >= 3 else 'COOLING'
            return 'third_thermal_stop' if self.state == 'END' else 'thermal_stop'
        return 'ok'

    def completed(self):
        if self.state != 'READY':
            raise RuntimeError('cannot complete an unsafe burst')
        self.stops = 0


def supervise_once(guard, spawn, read, emit, clock, wait, *, poll_s=1):
    """One own-child burst; adapters MUST bound read/emit latency.

    Candidate OS adapters are separate, NOT a device-qualified phone runner.
    Child adapter must own
    its process group and expose poll/terminate/wait/kill. Never target by name.
    """
    if isinstance(poll_s,bool) or not math.isfinite(poll_s) or poll_s<=0:
        raise ValueError('positive finite polling cadence required')
    def stop(child):
        child.terminate()
        try:
            child.wait(timeout=2)
        except TimeoutError:
            child.kill()
            child.wait(timeout=2)

    child = None
    try:
        reason = guard.observe(read(), clock())
        emit(dict(kind='gate', reason=reason, state=guard.state, stops=guard.stops))
        if reason != 'ok':
            return reason
        child = spawn()
        start = clock()
        emit(dict(kind='worker_started', pgid=getattr(child,'pgid',None), started_s=start))
        while True:
            reason = guard.observe(read(), clock())
            if reason != 'ok':
                stop(child)
                emit(dict(kind='aborted', reason=reason, state=guard.state, stops=guard.stops))
                return reason
            if clock()-start >= guard.policy.worker_timeout_s:
                guard.state = 'END'
                stop(child)
                emit(dict(kind='aborted', reason='worker_timeout'))
                return 'worker_timeout'
            code = child.poll()
            if code is not None:
                if code == 0:
                    guard.completed()
                    emit(dict(kind='completed', code=code))
                    return 'completed'
                guard.state = 'END'
                stop(child)
                emit(dict(kind='aborted', reason='worker_error', code=code))
                return 'worker_error'
            wait(poll_s)  # cadence must be prospectively locked and device-validated
    except BaseException:
        guard.state = 'END'
        if child is not None:
            # A failed poll/logger must not prevent cleanup. The owned-child
            # adapter makes stopping an already-finished group idempotent.
            stop(child)
        raise
