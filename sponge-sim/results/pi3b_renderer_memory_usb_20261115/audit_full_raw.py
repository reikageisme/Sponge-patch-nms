"""Postterminal independent replay; no frozen analyzer/stats imports or device load.

Scheduling, medians, unit conversions and guards are rebuilt from raw; NumPy
provides only RNG/quantiles and bounded vector enumeration of all sign patterns.
Original files are read-only. The exclusive audit output is derived evidence.
"""
from pathlib import Path
from statistics import mean, median, stdev
import csv
import hashlib
import json
import math
import random
import subprocess

import numpy as np

B = Path(__file__).resolve().parent
ROOT = B.parents[2]
S = ROOT/'sponge-sim/studies/pi3b_renderer_memory_usb_20261115'
P = B/'runs/memory_full_01'
R = P/'original'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-14), (a, b)


def stats(values, seed):
    x = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), (20000, len(x)))].mean(axis=1)
    ci = np.exp(np.quantile(means, [.025, .975])).tolist()
    # Enumerate independently of the frozen itertools implementation.
    hits = 0
    for start in range(0, 2**len(x), 8192):
        patterns = np.arange(start, min(start+8192, 2**len(x)), dtype=np.uint32)
        signs = 2*((patterns[:, None] >> np.arange(len(x), dtype=np.uint32)) & 1).astype(float)-1
        hits += int((np.abs((signs*x).mean(axis=1)) >= abs(mean(values))-1e-12).sum())
    return dict(mean_log=mean(values), sd_log=stdev(values), geomean_ratio=math.exp(mean(values)),
                ratio_ci95=ci, p_sign_flip=hits/2**len(x), dz=mean(values)/stdev(values),
                exact_sign_patterns=2**len(x), exact_extreme_patterns=hits, bootstrap_seed=seed)


def main():
    reg = load(S/'memory_registration.json')
    summary = load(P/'summary.json')
    assert summary['quality_pass'] and summary['session_gate_pass'] and summary['restore_ok']
    assert load(R/'campaign_terminal.json') == dict(status='COMPLETED', gate_returncode=0)
    restore = load(R/'restore.json')
    assert restore['status'] == 'RESTORED' and restore['errors'] == []
    tag = reg['tag']
    commit = subprocess.check_output(['git', 'rev-list', '-n', '1', tag], cwd=ROOT, text=True).strip()
    for filename, digest in reg['source_sha256'].items():
        assert sha(S/filename) == digest
        blob = subprocess.check_output(['git', 'show', f'{tag}:sponge-sim/studies/pi3b_renderer_memory_usb_20261115/{filename}'], cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest() == digest
    transfer = load(B/'full_transfer_verification.json')
    files = {p.relative_to(R).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size) for p in R.rglob('*') if p.is_file()}
    assert files == transfer['files'] and len(files) == 1814 and transfer['restore_readback_verified']
    cache = load(S/'cache_manifest.json')
    cases = {(x['image'], x['condition']): x for x in cache['cases']}
    cache_dir = ROOT/'sponge-sim/results/pi3b_renderer_functional_cache_20261114/caches/cache_01'
    assert sha(cache_dir/'manifest.json') == reg['cache_manifest_sha256']
    assert all(sha(cache_dir/x['filename']) == x['sha256'] for x in cache['cases'])
    rows = [json.loads(x) for x in (R/'memory/raw.jsonl').read_text().splitlines()]
    expected = []
    for ix, image in enumerate(reg['image_ids']):
        for rep in range(3):
            block = [(c, a) for c in ('clean', 'adv') for a in reg['arms']]
            random.Random(reg['seed']+1000*ix+rep).shuffle(block)
            for condition, arm in block:
                expected.append(dict(index=len(expected), image=image, condition=condition, arm=arm, rep=rep))
    assert len(rows) == 360 and [x['job'] for x in rows] == expected
    usb = load(R/'usb_preflight.json')
    assert usb['commit'] == commit and usb['lock_sha256'] == sha(S/'memory_registration.json')
    parent = [json.loads(x) for x in (R/'memory/guards.jsonl').read_text().splitlines()]
    fasts = [x['fast'] for x in parent if 'fast' in x]
    parent_count = len(fasts)
    clocks = [x['actual_arm_hz'] for x in parent if 'actual_arm_hz' in x]
    assert len(clocks) == 720 and set(clocks) == {600000000}
    assert all(not x.get('violations') for x in parent)
    for row in rows:
        j, x = row['job'], row['result']
        jobdir = R/'memory/jobs'/f"{j['index']:04d}"
        assert x == load(jobdir/'memory.json')
        done = load(jobdir/'terminal.json')
        assert done['returncode'] == 0 and done['failure'] is None and done['direct_child_reaped']
        assert not done['termination_sent'] and done['status'] == 'COMPLETED'
        assert x['pid'] == done['owned_pid'] == load(jobdir/'started.json')['pid']
        assert x['commit'] == commit and x['tag'] == tag and x['phase'] == 'full'
        assert x['registration_sha256'] == sha(S/'memory_registration.json')
        assert x['usb_preflight_sha256'] == sha(R/'usb_preflight.json')
        case = cases[(j['image'], j['condition'])]
        assert x['cache_sha256'] == case['sha256'] and x['mask_sha256'] == case['mask_sha256']
        assert x['ru_maxrss_bytes'] == 1024*x['ru_maxrss_kib'] > 0
        assert x['includes_import_validation_warmup_hash'] and not x['incremental_renderer_peak']
        assert not x['latency_endpoint_recorded'] and x['sample_point'] == 'after_render_and_output_digest'
        assert set(x['guards']) == {'start', 'ready', 'end'}
        fasts.extend(x['guards'].values())
    baseline_vm = fasts[0]['vmstat']
    for fast in fasts:
        assert fast['usb_state'] == usb['snapshot']
        assert fast['vmstat'] == baseline_vm and fast['swaps'] == []
        assert fast['mem_kb']['SwapTotal'] == 0 and fast['mem_kb']['MemAvailable'] >= 40000
        assert fast['governor'] == 'powersave' and fast['affinity'] == [0, 1, 2, 3]
        assert fast['temp_c'] < 75 and all(fast['masks'].values())
    table = []
    aa = dict(clean=[], adv=[])
    logs = dict(clean=[], adv=[])
    for image in reg['image_ids']:
        for condition in ('clean', 'adv'):
            groups = {a: [] for a in reg['arms']}
            lines = {a: [] for a in reg['arms']}
            for line, row in enumerate(rows, 1):
                j = row['job']
                if (j['image'], j['condition']) == (image, condition):
                    groups[j['arm']].append(row['result']['ru_maxrss_bytes'])
                    lines[j['arm']].append(line)
            assert all(len(v) == 3 for v in groups.values())
            med = {a: median(v) for a, v in groups.items()}
            med['pooled_baseline'] = median(groups['baseline_A']+groups['baseline_B'])
            assert med == summary['per_image_median_bytes'][image][condition]
            ratio = med['candidate16M']/med['pooled_baseline']
            logs[condition].append(math.log(ratio))
            aa[condition].append(math.log(med['baseline_A']/med['baseline_B']))
            table.append(dict(image=image, condition=condition, k=cases[(image, condition)]['k'],
                pooled_baseline_bytes=med['pooled_baseline'], candidate_bytes=med['candidate16M'],
                pooled_baseline_kib=med['pooled_baseline']/1024, candidate_kib=med['candidate16M']/1024,
                candidate_over_baseline=ratio, raw_lines=lines))
    independent = {}
    for label, values, seed, ref in (
        ('primary_adv', logs['adv'], 2026111401, summary['primary_adv_candidate_over_baseline']),
        ('secondary_clean', logs['clean'], 2026111402, summary['secondary_clean_candidate_over_baseline']),
        ('aa_clean', aa['clean'], 2026111403, summary['aa_intervals']['clean']),
        ('aa_adv', aa['adv'], 2026111404, summary['aa_intervals']['adv'])):
        result = stats(values, seed)
        for key in ('mean_log', 'sd_log', 'geomean_ratio', 'p_sign_flip', 'dz'):
            close(result[key], ref[key])
        for a, b in zip(result['ratio_ci95'], ref['ratio_ci95']): close(a, b)
        independent[label] = result
    for c, values in aa.items():
        mde = reg['mde_t_critical_sums']['20']*stdev(values)/math.sqrt(20)
        close(mde, summary['aa_controls'][c]['mde_log_80pct'])
        assert abs(mean(values)) <= .02 and mde <= .05
    out = dict(status='INDEPENDENT_FULL_RAW_REPLAY_PASS', tag=tag, commit=commit,
        unit='image', n_images=20, n_jobs=360, original_files=len(files),
        raw_sha256=sha(R/'memory/raw.jsonl'), usb_preflight_sha256=sha(R/'usb_preflight.json'),
        parent_guard_frames=parent_count, child_guard_frames=len(fasts)-parent_count,
        clock_samples=len(clocks), clock_hz=sorted(set(clocks)),
        sampled_min_mem_available_kib=min(x['mem_kb']['MemAvailable'] for x in fasts),
        sampled_max_temperature_c=max(x['temp_c'] for x in fasts),
        guard_memory_is_not_rss=True, whole_process_high_water_not_renderer_only=True,
        all_output_digests_match=True, identical_usb_snapshot_all_frames=True,
        independent_statistics=independent, table=table)
    with (B/'independent_full_audit.json').open('x', encoding='utf-8') as f:
        json.dump(out, f, indent=2, allow_nan=False)
    with (B/'full_per_image.csv').open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0])); writer.writeheader(); writer.writerows(table)
    print(json.dumps({k: v for k, v in out.items() if k not in ('table', 'independent_statistics')}))


if __name__ == '__main__': main()
