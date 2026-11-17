"""Loaded-library and visible kernel/controller metadata, no configuration writes.

Stage co-occurrence is temporal evidence, not library ownership of a TID.
Optional kernel configuration files remain unavailable when not exposed.
"""
from pathlib import Path
import gzip
import hashlib
import platform

from counters import birth, optional
import inventory


def proc_cgroups(text):
    rows = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith('#'): continue
        name, hierarchy, count, enabled = line.split()
        values = [int(hierarchy), int(count), int(enabled)]
        if name in rows or min(values) < 0 or values[-1] not in (0, 1):
            raise ValueError('invalid/duplicate proc cgroup controller')
        rows[name] = dict(hierarchy=values[0], num_cgroups=values[1], enabled=values[2])
    if not rows: raise ValueError('empty proc cgroups')
    return rows


def library_paths(text):
    paths = set()
    for line in text.splitlines():
        fields = line.split(None, 5)
        if len(fields) == 6 and fields[5].startswith('/') and '.so' in fields[5]:
            paths.add(fields[5])
    return sorted(paths)


def kernel_metadata(proc_root=Path('/proc'), cgroup_root=Path('/sys/fs/cgroup'), boot_root=Path('/boot')):
    proc_root, cgroup_root, boot_root = map(Path, (proc_root, cgroup_root, boot_root))
    raw = {n: optional(proc_root/n) for n in ('cmdline', 'cgroups', 'self/mountinfo')}
    if raw['cgroups']['status'] == 'OK': raw['cgroups']['rows'] = proc_cgroups(raw['cgroups']['text'])
    raw['root.controllers'] = optional(cgroup_root/'cgroup.controllers')
    flags = {}
    for p in (proc_root/'config.gz', boot_root/('config-'+platform.release())):
        try:
            data = p.read_bytes()
            text = (gzip.decompress(data) if p.name == 'config.gz' else data).decode('utf-8')
            selected = [dict(line=k, text=x) for k, x in enumerate(text.splitlines(), 1)
                        if any(token in x for token in ('CONFIG_CGROUP', 'CONFIG_MEMCG', 'CONFIG_PSI', 'CONFIG_FAIR_GROUP_SCHED', 'CONFIG_CFS_BANDWIDTH'))]
            flags[str(p)] = dict(status='OK', sha256=hashlib.sha256(data).hexdigest(), selected_lines=selected)
        except (OSError, UnicodeError, EOFError) as exc:
            flags[str(p)] = dict(status='UNAVAILABLE', error=type(exc).__name__)
    return dict(proc=raw, kernel_config=flags, kernel_release=platform.release(),
                visible_hierarchy_only=True, configuration_changed=False)


def stage(label, proc_root=Path('/proc'), cgroup_root=Path('/sys/fs/cgroup')):
    snap = inventory.snapshot(proc_root, cgroup_root)
    names = {}
    for tid in snap['tids_before']:
        task = Path(proc_root)/'self/task'/str(tid)
        try:
            before = birth((task/'stat').read_text(), tid)
            name = (task/'comm').read_text().rstrip('\n')
            after = birth((task/'stat').read_text(), tid)
            if before != after or before != snap['threads'][str(tid)]['stat']['start_ticks']:
                raise ValueError('TID reused while reading name')
            names[str(tid)] = dict(status='OK', comm=name, start_ticks=after)
        except (OSError, ValueError, KeyError) as exc:
            names[str(tid)] = dict(status='UNAVAILABLE', error=type(exc).__name__)
    maps = (Path(proc_root)/'self/maps').read_text()
    controls = {g['path']:optional(p/'cgroup.subtree_control') for (g, (_, p)) in
                zip(snap['cgroup_ancestors'], inventory.ancestors(snap['cgroup_path'], cgroup_root))}
    return dict(label=label, inventory=snap, thread_names=names, loaded_libraries=library_paths(maps),
        subtree_controls=controls, complete=snap['complete_stable_set'] and all(x['status'] == 'OK' for x in names.values()),
        sequential_not_atomic=True, library_ownership_identified=False)


def transitions(stages):
    rows = []
    for old, new in zip(stages, stages[1:]):
        if not old['complete'] or not new['complete']: raise ValueError('incomplete stage, no filtered transition')
        a, b = old['inventory'], new['inventory']
        if (a['pid'], a['start_ticks'], a['cgroup_path']) != (b['pid'], b['start_ticks'], b['cgroup_path']):
            raise ValueError('different process/group')
        ids = lambda s:{(int(tid), x['stat']['start_ticks']) for tid,x in s['threads'].items()}
        born, gone = ids(b)-ids(a), ids(a)-ids(b)
        rows.append(dict(before=old['label'], after=new['label'],
            born_identities=[dict(tid=t, start_ticks=k) for t,k in sorted(born)],
            gone_identities=[dict(tid=t, start_ticks=k) for t,k in sorted(gone)],
            newly_mapped_libraries=sorted(set(new['loaded_libraries'])-set(old['loaded_libraries'])),
            temporal_cooccurrence_only=True, library_ownership_identified=False))
    return rows
