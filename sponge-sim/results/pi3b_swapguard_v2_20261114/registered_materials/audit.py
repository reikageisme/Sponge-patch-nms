"""Structural validation independent of the inferential calculations; no model imports.

Uses the frozen arm/seed design from studies/pi3b_600mhz/run.py:37-48,308-354
(SHA256 9cc349be2c265fb4615d0016e9dae4a5aef53961df0d603abcb42d7a9fdbec8a).
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import random
import re
from pathlib import Path

from guard import violations

ARMS = ['clean_total_A', 'clean_total_B', 'adv_total', 'advcap_total', 'clean_forward', 'adv_forward']
STAGES = ['nms_clean', 'nms_adv', 'mask_clean', 'mask_adv', 'nms_adv_B', 'mask_adv_B']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_session(directory, lock, lock_sha):
    directory = Path(directory)
    errors, condition_errors = [], []
    try:
        m = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        rows = [json.loads(line) for line in (directory / 'raw.jsonl').read_text(encoding='utf-8').splitlines()]
        terminal = json.loads((directory / 'terminal.json').read_text(encoding='utf-8'))
        registration = json.loads((directory.parent / 'registration.json').read_text(encoding='utf-8'))
        cfg = lock['smoke' if m['smoke'] else 'full']
        names = [Path(p).name.split('_')[0] for p in lock['inputs'][:cfg['n_images']]]
        cpus = lock['profiles'][m['profile']]['cpus']
        expected_source = next(f['sha256'] for f in lock['files'] if f['name'] == 'run.py')
        if m['lock_sha256'] != lock_sha or m['runner_sha256'] != expected_source or m['versions'] != lock['versions']:
            errors.append('manifest_source_or_runtime')
        if m['tag'] != lock['registration_tag'] or not re.fullmatch('[a-f0-9]{40}',m['prereg_commit']):
            errors.append('registration')
        if (registration['tag']!=m['tag'] or registration['commit']!=m['prereg_commit']
                or registration['lock_sha256']!=lock_sha
                or registration['mode']!=('smoke' if m['smoke'] else 'full')):
            errors.append('campaign_registration')
        if m['config'] != cfg or m['cpu_set'] != cpus or m['torch_threads'] != len(cpus) or m['interop_threads'] != 1:
            errors.append('manifest_configuration')
        if m['weights_sha256'] != next(f['sha256'] for f in lock['files'] if f['name'] == lock['weights']):
            errors.append('weights')
        if m['guard_policy'] != lock['guard_policy']:
            errors.append('guard_policy')
        if terminal['status'] != 'COMPLETED' or not rows or rows[0]['kind'] != 'pin_start' or rows[-1]['kind'] != 'done':
            errors.append('terminal_or_boundaries')
        if sum(r['kind'] == 'done' for r in rows) != 1 or any(r['kind'] in ('aborted', 'preparation_failed') for r in rows):
            errors.append('completion')
        allowed = {'pin_start','pin_end','reference','environment','condition','counts','timing','memory','guard','done'}
        if any(r['kind'] not in allowed for r in rows):
            errors.append('unknown_row_kind')
        for kind in ('pin_start', 'pin_end'):
            pins = [r for r in rows if r['kind'] == kind]
            if len(pins) != 1 or pins[0]['passed'] is not True or pins[0]['affinity'] != cpus:
                errors.append(kind)
            elif len(pins[0]['busy']) != 4 or any(not math.isfinite(v) or not 0<=v<=1 for v in pins[0]['busy']):
                errors.append(kind+'_busy')
            else:
                pin=pins[0]
                inside=sum(pin['busy'][c] for c in cpus)
                outside=sum(v for c,v in enumerate(pin['busy']) if c not in cpus)
                need=.5 if len(cpus)==1 else .7*len(cpus)
                if (not math.isclose(pin['inside'],inside,abs_tol=1e-12)
                        or not math.isclose(pin['outside'],outside,abs_tol=1e-12)
                        or pin['need']!=need or inside<need or (len(cpus)!=4 and outside>=.5)):
                    errors.append(kind+'_calculation')
        refs = [r for r in rows if r['kind'] == 'reference']
        if [r['block'] for r in refs] != ['start', *range(len(names)), 'end']:
            errors.append('reference_schedule')
        else:
            from statistics import median
            initial = median(refs[0]['samples_ns'])
            for ref in refs:
                values = ref['samples_ns']
                ratio = median(values) / initial
                if (len(values) != cfg['reference_samples'] or any(not positive(v) for v in values)
                        or not math.isclose(ref['ratio'], ratio, rel_tol=1e-12)
                        or ref['flagged'] != (abs(ratio - 1) > lock['gates']['reference_drift'])):
                    errors.append('reference_values')
        envs = [r for r in rows if r['kind'] == 'environment']
        conditions = [r for r in rows if r['kind'] == 'condition']
        blocks = [*range(len(names)), 'end']
        if [r['block'] for r in envs] != blocks or [r['block'] for r in conditions] != blocks:
            errors.append('environment_schedule')
        cr = [r for r in rows if r['kind'] == 'counts']
        if [r['image'] for r in cr] != names or [r['block'] for r in cr] != list(range(len(names))):
            errors.append('count_identities')
        count_by = {r['image']: r['counts'] for r in cr}
        for c in count_by.values():
            for arm in ('clean','adv','advcap'):
                if any(type(c[arm][k]) is not int or c[arm][k] < 0 for k in ('n_tau','kernel_n','k')):
                    errors.append('count_type')
                if c[arm]['k'] > min(c[arm]['kernel_n'], 300):
                    errors.append('count_boundary')
            if c['advcap']['kernel_n'] != min(c['adv']['n_tau'], lock['defense']['max_nms']):
                errors.append('cap_boundary')
            if c['advcap']['n_tau']!=c['adv']['n_tau'] or c['advcap']['options']!=lock['defense']:
                errors.append('cap_configuration')
            for arm in ('clean','adv'):
                if c[arm]['kernel_n']!=min(c[arm]['n_tau'],30000) or not re.fullmatch('[0-9a-f]{64}',c[arm]['prediction_sha256']):
                    errors.append('kernel_count_or_prediction_identity')
        expected = []
        for ix, image in enumerate(names):
            arms = list(ARMS if m['mode'] == 'pipeline' else STAGES)
            if m['mode'] == 'stages' and ix < cfg['dose_images']:
                arms += [f'maskdose_{k}' for k in lock['dose_levels'] if k <= count_by[image]['adv']['k']]
            for rep in range(cfg['repeats'][m['mode'] + '_' + m['profile']]):
                order = list(range(len(arms)))
                random.Random(lock['seed'] + 1000 * ix + rep).shuffle(order)
                expected += [(image, ix, arms[j], rep, pos) for pos, j in enumerate(order)]
        timing = [r for r in rows if r['kind'] == 'timing']
        actual = [(r['image'],r['block'],r['arm'],r['rep'],r['position']) for r in timing]
        if actual != expected:
            errors.append('timing_schedule')
        if [r['image'] for r in rows if r['kind'] == 'memory'] != names:
            errors.append('memory_schedule')
        guards = [r for r in rows if r['kind'] == 'guard']
        n_calls = len(expected) + len(refs) * cfg['reference_samples']
        if [(r['guard_id'],r['phase']) for r in guards] != [(i,p) for i in range(1,n_calls+1) for p in ('pre','post')]:
            errors.append('guard_schedule')
        post = {r['guard_id']: r for r in guards if r['phase'] == 'post'}
        if len({r['guard_id'] for r in timing}) != len(timing):
            errors.append('reused_guard')
        last_end = -1
        for gid in sorted(post):
            r = post[gid]
            if not positive(r['ns']) or not positive(r['t_start_ns']) or r['t_start_ns'] < last_end or r['process_cpu_ns'] < 0:
                errors.append('duration_or_clock')
            last_end = r['t_start_ns'] + r['ns']
        for r in timing:
            if any(r[k] != post[r['guard_id']][k] for k in ('ns','t_start_ns','process_cpu_ns')):
                errors.append('timing_guard_link')
        remaining = Counter(r['ns'] for r in post.values()) - Counter(r['ns'] for r in timing)
        if remaining != Counter(v for r in refs for v in r['samples_ns']):
            errors.append('reference_guard_link')
        baseline = m['initial_fast']['vmstat']
        fast_rows = [m['initial_fast']] + [r['fast'] for r in guards + conditions]
        for fast in fast_rows:
            condition_errors += violations(fast, lock, cpus, baseline)
        if any(r['violations'] for r in guards + conditions):
            condition_errors.append('logged_guard_violation')
        return dict(structure_ok=not errors, errors=sorted(set(errors)),
                    conditions_ok=not condition_errors, condition_errors=sorted(set(condition_errors)),
                    n_timings=len(timing), n_guards=len(guards), expected_timings=len(expected),
                    raw_sha256=sha(directory / 'raw.jsonl'))
    except (OSError, ValueError, KeyError, TypeError, StopIteration, ZeroDivisionError, IndexError) as e:
        return dict(structure_ok=False, conditions_ok=False, errors=errors + [f'{type(e).__name__}: {e}'],
                    condition_errors=condition_errors)


def positive(value):
    return type(value) is int and value > 0
