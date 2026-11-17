# Copied unchanged from sponge-sim/studies/pi3b_renderer_memory_usb_20261115/guard.py:1-101
# SHA256 9b38481bc70e563732be47bc7cc0eef646d32fd19739918313eadce3cd4f7ebe; old qualified source/data immutable.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_memory_v1_20261114/guard.py:1-91
# SHA256 f669bc058b42869b7b2b40743c2cd2b6492d29ef3f86258d875ce68ca0cf3525; closed USB-absent V1 source/runs remain immutable.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_prealloc_20261114/guard.py:1-89
# SHA256 ee9add3a7ca142a6ab38c32d5c9f94183a066a284bc4467a89d3b3bf5a98bebd; earlier QA/cache source and runs remain immutable.
# Copied from sponge-sim/studies/pi3b_full20_20261114/guard.py:1-87
# SHA256 0922c853451a9943a843cfc1c9d60f73e85f5941f66a3b4624900c8ae348d48c; closed full20 source remains immutable.
# Copied from sponge-sim/studies/pi3b_600mhz_swapguard_v2/guard.py:1-85
# SHA256 d803ff62aa7b1f8e6999aa3443f28f1936373b90d2bebf7eefa3c20988edc3ab; parent protocol remains CLOSED and immutable.
"""Pi swapguard v2: cheap, fail-closed readbacks outside every clock region.

Derived checks: studies/pi3b_600mhz/run.py:51-85,267-276,
SHA256 9cc349be2c265fb4615d0016e9dae4a5aef53961df0d603abcb42d7a9fdbec8a.
No Torch import, configuration mutation, or benchmark in this module.
"""
from __future__ import annotations

import math
import os
import re
from pathlib import Path
import usb_guard

UNITS = ('dev-zram0.swap', 'rpi-zram-writeback.service', 'rpi-zram-writeback.timer')
POLICY = Path('/sys/devices/system/cpu/cpufreq/policy0')
STORAGE_PATHS=dict(workspace=Path(__file__).resolve().parent,
    cache=Path('/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/caches/cache_01'))


def read_storage():return usb_guard.read_snapshot(STORAGE_PATHS)


def parse_swaps(text):
    lines = text.splitlines()
    if not lines or lines[0].split() != ['Filename', 'Type', 'Size', 'Used', 'Priority']:
        raise ValueError('unexpected /proc/swaps header')
    rows = []
    for line in lines[1:]:
        fields = line.split()
        if len(fields) != 5:
            raise ValueError('unexpected swap row')
        name, kind, size, used, priority = fields
        rows.append(dict(name=name, kind=kind, size_kb=int(size), used_kb=int(used), priority=int(priority)))
    return rows


def read_fast():
    mem = dict((line.split(':', 1)[0], int(line.split(':', 1)[1].split()[0]))
               for line in Path('/proc/meminfo').read_text().splitlines()
               if line.split(':', 1)[0] in ('MemAvailable', 'SwapTotal'))
    vm = dict((k, int(v)) for k, v in (line.split() for line in Path('/proc/vmstat').read_text().splitlines())
              if k in ('pswpin', 'pswpout', 'oom_kill'))
    return dict(governor=(POLICY / 'scaling_governor').read_text().strip(),
                scaling_cur_khz=int((POLICY / 'scaling_cur_freq').read_text()),
                temp_c=int(Path('/sys/class/thermal/thermal_zone0/temp').read_text()) / 1000,
                affinity=sorted(os.sched_getaffinity(0)), mem_kb=mem, vmstat=vm,
                swaps=parse_swaps(Path('/proc/swaps').read_text()),
                usb=sorted(p.name for p in Path('/sys/block').iterdir() if p.name.startswith('sd')),
                usb_state=read_storage(),
                masks={u: (Path('/run/systemd/system') / u).is_symlink()
                       and os.readlink(Path('/run/systemd/system') / u) == '/dev/null' for u in UNITS})


def violations(env, lock, cpus, baseline_vmstat=None, usb_baseline=None):
    """Missing/malformed fields are failures, never an implicit pass."""
    errors = []
    try:
        if any(type(env['vmstat'][k]) is not int or env['vmstat'][k] < 0 for k in ('pswpin','pswpout','oom_kill')):
            errors.append('invalid_vmstat')
        if any(type(env['mem_kb'][k]) is not int or env['mem_kb'][k] < 0 for k in ('SwapTotal','MemAvailable')):
            errors.append('invalid_meminfo')
        if env['governor'] != lock['governor']:
            errors.append('governor')
        if env['affinity'] != cpus:
            errors.append('affinity')
        if env['mem_kb']['SwapTotal'] != 0 or env['swaps']:
            errors.append('swap')
        if env['mem_kb']['MemAvailable'] < lock['gates']['abort_mem_available_kb']:
            errors.append('memory')
        temp = env['temp_c']
        if not isinstance(temp, (int, float)) or not math.isfinite(temp) or not 0 <= temp < lock['gates']['abort_temp_c']:
            errors.append('temperature')
        if not lock['gates']['clock_hz'][0] <= env['scaling_cur_khz'] * 1000 <= lock['gates']['clock_hz'][1]:
            errors.append('requested_clock')
        if usb_baseline is None:errors.append('usb_baseline_missing')
        errors.extend(usb_guard.validate(env['usb_state'],lock['usb_contract'],usb_baseline))
        if env['usb']!=sorted(env['usb_state']['disks']):errors.append('usb_inventory_disagrees')
        if any(env['masks'][u] is not True for u in UNITS):
            errors.append('runtime_mask')
        if baseline_vmstat is not None and any(env['vmstat'][k] != baseline_vmstat[k]
                                               for k in ('pswpin', 'pswpout', 'oom_kill')):
            errors.append('vmstat_change')
    except (KeyError, TypeError, ValueError, OverflowError):
        errors.append('invalid_readback')
    return errors


def strict_temp(text):
    match = re.fullmatch(r"temp=([0-9]+(?:\.[0-9]+)?)'C", text)
    if not match:
        raise ValueError('invalid vcgencmd temperature')
    return float(match.group(1))
