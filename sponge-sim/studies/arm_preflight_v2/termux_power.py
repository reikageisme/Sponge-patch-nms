"""Pure draft battery adapter. No commands, collection, deployment or load.

Schema reference: termux/termux-api v0.53.0 BatteryStatusAPI.java; numeric
temperature is already Celsius. This reference does NOT fingerprint A36's
Google Play implementation or companion APK. Its actual route must be bound
before live use. Parsing saved bytes never produces a fresh Reading.
"""
from dataclasses import dataclass
import hashlib
import json
import math

from checks import Reading, PLUGGED_SOURCES

SOURCE_CONTRACT = ('https://github.com/termux/termux-api/blob/v0.53.0/'
                   'app/src/main/java/com/termux/api/apis/BatteryStatusAPI.java')
PLUGGED = PLUGGED_SOURCES
STATUSES = frozenset({'CHARGING', 'DISCHARGING', 'FULL', 'NOT_CHARGING'})


@dataclass(frozen=True)
class PowerPayload:
    raw_sha256: str
    battery_c: float
    battery_pct: float
    status: str
    plugged: str
    health: str

    @property
    def charging(self):
        return self.status == 'CHARGING' and self.plugged in PLUGGED


def _number(value):
    if type(value) not in (int, float):
        raise ValueError('finite JSON number required, no strings/booleans')
    try:
        if math.isfinite(value):
            return value
    except OverflowError:
        pass
    raise ValueError('nonfinite or unrepresentable number')


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field: ' + key)
        result[key] = value
    return result


def _constant(value):
    raise ValueError('nonstandard JSON number: ' + value)


def parse_power(raw):
    """Parse exact stdout BYTES; retain raw separately even on rejection.

    GOOD health is a NEW prospective adapter eligibility condition. Unknown
    states reject; FULL/NOT_CHARGING remain known noncharging observations.
    No fallback to level/scale, current sign, plugged alone or guessed units.
    """
    if not isinstance(raw, bytes) or not 0 < len(raw) <= 65536:
        raise ValueError('nonempty stdout bytes, at most 64KiB, required')
    try:
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=_object,
                          parse_constant=_constant,
                          parse_float=lambda value: _number(float(value)),
                          parse_int=lambda value: _number(int(value)))
    except (UnicodeError, RecursionError) as e:
        raise ValueError('invalid UTF-8 or excessive JSON nesting') from e
    required = {'present', 'health', 'plugged', 'status', 'temperature', 'percentage'}
    if not isinstance(data, dict) or not required <= data.keys():
        raise ValueError('missing battery fields or non-object response')
    if data['present'] is not True or data['health'] != 'GOOD':
        raise ValueError('present battery and GOOD health required')
    status, plugged = data['status'], data['plugged']
    if (not isinstance(status, str) or status not in STATUSES
            or not isinstance(plugged, str) or plugged not in PLUGGED | {'UNPLUGGED'}):
        raise ValueError('unknown charging status or power source')
    if status == 'CHARGING' and plugged == 'UNPLUGGED':
        raise ValueError('contradictory charging/unplugged response')
    temperature, percentage = _number(data['temperature']), _number(data['percentage'])
    if temperature < -273.15 or not 0 <= percentage <= 100:
        raise ValueError('physically invalid temperature or battery percentage')
    return PowerPayload(hashlib.sha256(raw).hexdigest(), temperature, percentage,
                        status, plugged, data['health'])


def combine_live(power, *, power_started_s, power_finished_s, zones_c,
                 zones_started_s, zones_finished_s, policy, now_s):
    """Join ONE bounded live query and a separately verified thermal registry.

    Caller must use the SAME monotonic clock and timestamps captured BEFORE
    and AFTER each acquisition, with every raw frame durably saved before ACK.
    Do not call with restamped historical JSON or incomplete thermal reads.
    The oldest acquisition start governs freshness; slow or future reads fail.
    This pure joiner cannot establish registry units/permissions, enforce IO
    deadlines, or qualify Android/proot reaction/cleanup by itself.
    """
    if not isinstance(power, PowerPayload) or not isinstance(zones_c, dict):
        raise ValueError('parsed power and complete Celsius zone dictionary required')
    if (set(zones_c) != set(policy.expected_zones) or not zones_c
            or any(not isinstance(key, str) or not key for key in zones_c)):
        raise ValueError('exact nonempty registered zone IDs required')
    for value in zones_c.values():
        if _number(value) < -273.15:
            raise ValueError('physically invalid zone temperature')
    for start, finish in ((power_started_s, power_finished_s),
                          (zones_started_s, zones_finished_s)):
        if not 0 <= _number(start) <= _number(finish) <= _number(now_s):
            raise ValueError('nonnegative ordered acquisition times required')
        if now_s-start > policy.max_age_s:
            raise ValueError('stale acquisition; never restamp at consumption')
    return Reading(min(power_started_s, zones_started_s), dict(zones_c),
                   power.battery_c, power.battery_pct, power.charging,
                   power_source=power.plugged, power_status=power.status)
