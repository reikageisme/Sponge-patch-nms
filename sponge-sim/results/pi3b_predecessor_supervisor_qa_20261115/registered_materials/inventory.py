# Copied unchanged from sponge-sim/studies/pi3b_nms_observer_20261115/inventory.py:1-141
# SHA256 0eb533ad54b69c33508ab429d590405c4eaf1b0476e0c3dde211aa4a5e56d6b7; prior QA sources/data preserved.
"""Sequential self-TID/cgroup-ancestor inventory, not an NMS performance test.

Churn, reused identities and missing counters stay explicit. Neither a count
of threads nor configured Torch threads establishes simultaneous execution.
All read brackets include observer work and are not atomic process snapshots.
"""
from pathlib import Path
import os
import platform

from counters import birth, integer_rows, optional, thread_status, unified_group

CGROUP_FILES = ('cgroup.type', 'cgroup.controllers', 'cpu.max', 'cpu.stat',
                'cpu.weight', 'memory.max', 'memory.high', 'memory.current',
                'memory.events', 'memory.events.local', 'memory.pressure')


def cpu_list(text):
    cpus = []
    for part in text.strip().split(','):
        bits = part.split('-')
        if len(bits) not in (1, 2) or any(not x.isdecimal() for x in bits):
            raise ValueError('invalid CPU list')
        first, last = int(bits[0]), int(bits[-1])
        if last < first or last > 1048575: raise ValueError('invalid CPU range')
        cpus.extend(range(first, last+1))
    if not cpus or cpus != sorted(set(cpus)): raise ValueError('unordered/overlapping CPU list')
    return cpus


def task_stat(text, tid):
    start = birth(text, tid)
    fields = text.rsplit(')', 1)[1].split()
    if len(fields) < 37: raise ValueError('task stat lacks processor field')
    result = dict(start_ticks=start, state=fields[0], minflt=int(fields[7]),
                  majflt=int(fields[9]), utime_ticks=int(fields[11]),
                  stime_ticks=int(fields[12]), processor_at_sample=int(fields[36]))
    if any(result[k] < 0 for k in result if k not in ('state',)):
        raise ValueError('negative task counter/identity')
    return result


def ancestors(group, root):
    _, target = unified_group('0::'+group, root)
    root = Path(root).resolve()
    paths = []
    while True:
        paths.append(target)
        if target == root: break
        target = target.parent
    return [('/' if p == root else '/'+p.relative_to(root).as_posix(), p) for p in paths]


def quota(raw):
    parts = raw.split()
    if len(parts) != 2 or not parts[1].isdecimal() or int(parts[1]) <= 0:
        raise ValueError('invalid cpu.max period')
    if parts[0] == 'max': return dict(quota_us=None, period_us=int(parts[1]))
    if not parts[0].isdecimal() or int(parts[0]) <= 0: raise ValueError('invalid cpu.max quota')
    return dict(quota_us=int(parts[0]), period_us=int(parts[1]))


def cgroup_inventory(group, root):
    rows = []
    for name, path in ancestors(group, root):
        files = {n: optional(path/n) for n in CGROUP_FILES}
        for n in ('cpu.stat', 'memory.events', 'memory.events.local'):
            if files[n]['status'] == 'OK': files[n]['values'] = integer_rows(files[n]['text'])
        if files['cpu.max']['status'] == 'OK': files['cpu.max']['parsed'] = quota(files['cpu.max']['text'])
        rows.append(dict(path=name, files=files))
    return rows


def snapshot(proc_root=Path('/proc'), cgroup_root=Path('/sys/fs/cgroup')):
    if platform.system() != 'Linux': raise RuntimeError('Linux inventory required')
    pid = os.getpid()
    base = Path(proc_root)/'self'
    start = birth((base/'stat').read_text(), pid)
    group, _ = unified_group((base/'cgroup').read_text(), cgroup_root)
    task = base/'task'
    before = sorted(int(p.name) for p in task.iterdir() if p.name.isdecimal())
    if not before or len(before) > 128: raise ValueError('empty or excessive self-thread inventory')
    threads = {}
    for tid in before:
        path = task/str(tid)
        try:
            stat = task_stat((path/'stat').read_text(), tid)
            status = thread_status((path/'status').read_text())
            allowed = cpu_list(status['Cpus_allowed_list'])
            live_affinity = sorted(os.sched_getaffinity(tid))
            end = task_stat((path/'stat').read_text(), tid)
            if stat['start_ticks'] != end['start_ticks']: raise ValueError('TID reused while sampling')
            if allowed != live_affinity: raise ValueError('affinity changed during sampling')
            threads[str(tid)] = dict(status='OK', stat=stat, thread_status=status, affinity=allowed)
        except (OSError, ValueError) as exc:
            threads[str(tid)] = dict(status='UNAVAILABLE', error=type(exc).__name__, message=str(exc))
    cgroups = cgroup_inventory(group, cgroup_root)
    after = sorted(int(p.name) for p in task.iterdir() if p.name.isdecimal())
    end_births = {}
    for tid in after:
        try: end_births[str(tid)] = dict(status='OK', start_ticks=birth((task/str(tid)/'stat').read_text(), tid))
        except (OSError, ValueError) as exc: end_births[str(tid)] = dict(status='UNAVAILABLE', error=type(exc).__name__)
    if birth((base/'stat').read_text(), pid) != start: raise ValueError('process identity changed')
    if unified_group((base/'cgroup').read_text(), cgroup_root)[0] != group: raise ValueError('cgroup changed while sampling')
    stable = before == after and all(x['status'] == 'OK' for x in threads.values())
    stable = stable and all(end_births[str(t)]['status'] == 'OK' and
        end_births[str(t)]['start_ticks'] == threads[str(t)]['stat']['start_ticks'] for t in before)
    return dict(pid=pid, start_ticks=start, cgroup_path=group, threads=threads, end_start_ticks=end_births,
        tids_before=before, tids_after=after, cgroup_ancestors=cgroups,
        complete_stable_set=stable,
        sequential_not_atomic=True, configured_threads_do_not_prove_parallel_execution=True,
        observer_work_included=True, nms_endpoint_recorded=False)


def increments(before, after):
    """Refuse whole-pool deltas on churn; never silently keep only common TIDs."""
    if not before['complete_stable_set'] or not after['complete_stable_set']:
        raise ValueError('incomplete inventory; no filtered delta')
    for key in ('pid', 'start_ticks', 'cgroup_path', 'tids_before', 'tids_after'):
        if before[key] != after[key]: raise ValueError('process/group/thread set changed')
    for snap in (before, after):
        if set(snap['threads']) != {str(t) for t in snap['tids_before']}:
            raise ValueError('filtered thread mapping')
    deltas = {}
    for tid, a in before['threads'].items():
        b = after['threads'][tid]
        if a['stat']['start_ticks'] != b['stat']['start_ticks'] or a['affinity'] != b['affinity']:
            raise ValueError('TID identity or affinity changed')
        keys = ('minflt', 'majflt', 'utime_ticks', 'stime_ticks')
        values = {k: b['stat'][k]-a['stat'][k] for k in keys}
        for k in ('voluntary_ctxt_switches', 'nonvoluntary_ctxt_switches'):
            values[k] = b['thread_status'][k]-a['thread_status'][k]
        if any(v < 0 for v in values.values()): raise ValueError('task counter decreased')
        deltas[tid] = values
    a_groups, b_groups = before['cgroup_ancestors'], after['cgroup_ancestors']
    if [x['path'] for x in a_groups] != [x['path'] for x in b_groups]: raise ValueError('ancestor chain changed')
    for a, b in zip(a_groups, b_groups):
        for key in ('cpu.max', 'cpu.weight', 'memory.max', 'memory.high'):
            if a['files'][key] != b['files'][key]: raise ValueError('ancestor resource configuration changed')
    return dict(threads=deltas, observer_work_included=True, unique_wait_cause_identified=False,
                cgroup_counters_are_shared_not_thread_attribution=True)
