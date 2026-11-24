"""Phân tích E5 theo PREREG_E5.md. Đọc raw_*.jsonl trong run dir, ghi summary.json.

Đơn vị suy luận: ẢNH (100). Mỗi ảnh: median 10 lần nhãn A, median 10 lần nhãn B (A/A, cùng điều kiện).
d_i = ln(median_A / median_B). Báo mean d, CI bootstrap percentile theo ảnh (20.000, seed 20261021),
MDE (xấp xỉ t, 80% công suất, alpha .05) theo log -> đổi ra %.
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))
from sponge_sim import stats  # noqa: E402
from run import IMAGE_IDS

BOOT_SEED = 20261021
PRIMARY_STAGES = ['forward', 'total']


def load(run_dir: Path):
    out = {}
    for f in sorted(run_dir.glob('raw_*.jsonl')):
        rows = [json.loads(line) for line in f.read_text(encoding='utf-8').splitlines()]
        out[rows[0]['profile']] = rows
    return out


def audit_locked_profile(rows, config):
    start, end = rows[0], rows[-1]
    if start['kind'] != 'pin' or end['kind'] != 'pin_end':
        raise ValueError('locked A/A evidence does not include both pin checks')
    if len(start['allowed']) != 1 or start['readback'] != start['allowed']:
        raise ValueError('initial affinity is not exactly one CPU')
    cpu = start['allowed'][0]
    for row in (start, end):
        if not row['verify']['passed'] or not row['lock_status']['ready'] or row['lock_status']['cpu'] != cpu:
            raise ValueError('pin or lock check failed')
    if start['torch_threads'] != 1 or start['interop'] != 1:
        raise ValueError('unexpected Torch thread configuration')

    ids = IMAGE_IDS[:config['n_images']]
    block_size = config['block_size']
    refs = [r['block'] for r in rows if r['kind'] == 'reference']
    if refs != [*range((len(ids) + block_size - 1) // block_size), 'end']:
        raise ValueError('missing or unordered reference rows')

    by_image = defaultdict(list)
    for row in rows:
        if row['kind'] == 'measure':
            by_image[row['image_id']].append(row)
    if list(by_image) != ids:
        raise ValueError('measured cohort differs from the preregistered image sequence')
    rng = random.Random(config['label_order_seed'] + cpu)
    for pos, image_id in enumerate(ids):
        measurements = by_image[image_id]
        order = 'ABBA' if rng.random() < .5 else 'BAAB'
        expected = [order[i % 4] for i in range(2 * config['repeats'])]
        if [row['label'] for row in measurements] != expected:
            raise ValueError(f'image {image_id}: missing or out-of-order A/B repetitions')
        for idx, row in enumerate(measurements):
            if row['seq_index'] != idx or row['block'] != pos // block_size:
                raise ValueError(f'image {image_id}: wrong block or repetition index')
            stages = row['stages_ns']
            if set(stages) != set(config['stages']) or any(t <= 0 for t in stages.values()):
                raise ValueError(f'image {image_id}: invalid stage timings')
        if len({row['n_tau'] for row in measurements}) != 1:
            raise ValueError(f'image {image_id}: inconsistent candidate count on identical input')
    return dict(status='PASS', pin_start=start['verify'], pin_end=end['verify'],
                lock_start=start['lock_status'], lock_end=end['lock_status'])


def analyze_profile(rows):
    pin = rows[0]
    meas = [r for r in rows if r['kind'] == 'measure']
    refs = [r for r in rows if r['kind'] == 'reference']
    flagged_blocks = sorted({r['block'] for r in refs if r['flagged']}, key=str)
    stages = list(meas[0]['stages_ns'])
    ids = sorted({r['image_id'] for r in meas})
    res = dict(pin=dict(allowed=pin['allowed'], readback=pin['readback'], passed=pin['verify']['passed'],
                        effective_cores=pin['verify']['effective_cores'], torch_threads=pin['torch_threads']),
               n_images=len(ids), n_measure_rows=len(meas),
               drift=dict(reference_points=len(refs), flagged=[r['block'] for r in refs if r['flagged']],
                          max_abs_rel_change=max(abs(r['rel_change']) for r in refs)),
               stages={})
    for s in stages:
        d, cv, med = [], [], []
        for i in ids:
            a = np.array([r['stages_ns'][s] for r in meas if r['image_id'] == i and r['label'] == 'A'], float)
            b = np.array([r['stages_ns'][s] for r in meas if r['image_id'] == i and r['label'] == 'B'], float)
            both = np.concatenate([a, b])
            d.append(np.log(np.median(a) / np.median(b)))
            cv.append(both.std(ddof=1) / both.mean())
            med.append(np.median(both) / 1e6)
        d = np.array(d)
        lo, hi = stats.bootstrap_ci(d, BOOT_SEED)
        mde_log = stats.mde_paired(d.std(ddof=1), len(d))
        res['stages'][s] = dict(
            aa_mean_log_ratio=float(d.mean()), aa_ci95_log=[float(lo), float(hi)],
            aa_ratio=float(np.exp(d.mean())), aa_ci95_ratio=[float(np.exp(lo)), float(np.exp(hi))],
            aa_ci_contains_1=bool(lo <= 0 <= hi), sd_log=float(d.std(ddof=1)),
            mde_ratio_pct=float((np.exp(mde_log) - 1) * 100),
            median_within_image_cv=float(np.median(cv)), median_of_image_medians_ms=float(np.median(med)),
        )
    # Headroom mô tả: NMS torch_pure / total theo ảnh (trung vị mỗi ảnh), không cộng trung vị
    share = []
    for i in ids:
        rr = [r for r in meas if r['image_id'] == i]
        share.append(np.median([r['stages_ns']['nms_torch_pure'] / r['stages_ns']['total'] for r in rr]))
    res['nms_torch_pure_share_of_total'] = dict(median=float(np.median(share)), max=float(np.max(share)),
                                                note='mô tả; tỷ số theo lần đo rồi trung vị theo ảnh')
    # Sensitivity: bỏ khối có cờ trôi
    res['sensitivity_excluding_flagged_blocks'] = None
    if flagged_blocks and any(b != 'end' for b in flagged_blocks):
        keep = [r for r in meas if r['block'] not in flagged_blocks]
        kept_ids = sorted({r['image_id'] for r in keep})
        sens = {}
        for s in PRIMARY_STAGES:
            d = []
            for i in kept_ids:
                a = [r['stages_ns'][s] for r in keep if r['image_id'] == i and r['label'] == 'A']
                b = [r['stages_ns'][s] for r in keep if r['image_id'] == i and r['label'] == 'B']
                d.append(np.log(np.median(a) / np.median(b)))
            ci = [float(x) for x in stats.bootstrap_ci(d, BOOT_SEED)] if len(d) >= 2 else None
            sens[s] = dict(n_images=len(d), aa_mean_log_ratio=float(np.mean(d)) if len(d) else None,
                           aa_ci95_log=ci)
        res['sensitivity_excluding_flagged_blocks'] = sens
    return res


def main():
    run_dir = Path(sys.argv[1])
    data = load(run_dir)
    manifest = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    config = manifest['config']
    audits = {}
    if config.get('require_lock'):
        if set(data) != set(config['profiles']):
            raise ValueError('raw files do not match the configured profiles')
        audits = {p: audit_locked_profile(rows, config) for p, rows in data.items()}
    summary = dict(experiment='E5', run_dir=str(run_dir), manifest_config_sha256=manifest['config_sha256'],
                   git_head=manifest['git']['head'], tags_at_head=manifest['git']['tags_at_head'],
                   bootstrap_seed=BOOT_SEED, n_boot=stats.N_BOOT, unit='image',
                   profiles={p: analyze_profile(rows) for p, rows in data.items()})
    if audits:
        summary.update(canvas=config['canvas'], smoke=config['smoke'], audit=audits)
    summary['primary'] = {p: {s: dict(ci_contains_1=v['stages'][s]['aa_ci_contains_1'],
                                      ratio=v['stages'][s]['aa_ratio'], ci95=v['stages'][s]['aa_ci95_ratio'],
                                      mde_pct=v['stages'][s]['mde_ratio_pct'])
                              for s in PRIMARY_STAGES} for p, v in summary['profiles'].items()}
    (run_dir / 'summary.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding='utf-8')
    for p, v in summary['primary'].items():
        print(p, {s: (round(x['ratio'], 4), [round(c, 4) for c in x['ci95']], round(x['mde_pct'], 2)) for s, x in v.items()})


if __name__ == '__main__':
    main()
