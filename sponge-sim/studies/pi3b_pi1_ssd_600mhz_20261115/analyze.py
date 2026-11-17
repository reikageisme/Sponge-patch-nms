"""Analysis for PI3B-600MHZ (runs on the laptop from fetched raw). Registered in PREREG_PI3B_600MHZ_20261114.md.

Unit of inference: image (n = number of frozen pairs). One board, one model, one attack set.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))
from sponge_sim import stats  # noqa: E402

SEED = 20261114


def load(run_dir):
    rows = [json.loads(line) for line in (Path(run_dir) / 'raw.jsonl').read_text(encoding='utf-8').splitlines() if line]
    manifest = json.loads((Path(run_dir) / 'manifest.json').read_text(encoding='utf-8'))
    return manifest, rows


def medians(rows):
    """{image: {arm: median ns}} from timing rows; also returns sample counts."""
    acc = {}
    for r in rows:
        if r['kind'] == 'timing':
            acc.setdefault(r['image'], {}).setdefault(r['arm'], []).append(r['ns'])
    return ({im: {a: float(np.median(v)) for a, v in arms.items()} for im, arms in acc.items()},
            {im: {a: len(v) for a, v in arms.items()} for im, arms in acc.items()})


def clock_hz(text):
    try:
        return int(text.split('=')[1])
    except Exception:
        return None


def gates(manifest, rows, lock, n_expected):
    g = lock['gates']
    env = [r for r in rows if r['kind'] == 'environment']
    env.append(dict(manifest['environment_start']))
    done = [r for r in rows if r['kind'] == 'done']
    if done:
        env.append(dict(done[0]['environment_end']))
    clocks = [clock_hz(e['arm_clock_hz']) for e in env]
    refs = [r for r in rows if r['kind'] == 'reference']
    temps = [float(''.join(c for c in e['temp'] if c in '0123456789.')) for e in env]
    images = {r['image'] for r in rows if r['kind'] == 'timing'}
    out = dict(
        completed=bool(done) and not any(r['kind'] == 'aborted' for r in rows),
        images_complete=len(images) == n_expected,
        governor_ok=all(e['governor'] == lock['governor'] for e in env),
        clock_ok=all(c is not None and g['clock_hz'][0] <= c <= g['clock_hz'][1] for c in clocks),
        swap_off=all(e['mem_kb']['SwapTotal'] == 0 for e in env),
        reference_flags=sum(bool(r['flagged']) for r in refs),
        pin_ok=all(r['passed'] for r in rows if r['kind'] in ('pin_start', 'pin_end')),
        temp_max_c=max(temps), clock_min_hz=min(c for c in clocks if c is not None),
        clock_max_hz=max(c for c in clocks if c is not None),
        throttled_values=sorted({e['throttled'] for e in env}),
        reference_ratio_range=[min(r['ratio'] for r in refs), max(r['ratio'] for r in refs)],
        n_environment=len(env), n_reference=len(refs))
    out['reference_ok'] = out['reference_flags'] <= g['max_reference_flags']
    if lock.get('allow_usb_storage'):
        disks = [e.get('usb_disk', {}) for e in env]
        names = sorted({n for d in disks for n in (d or {})})
        writes = {n: sorted({d[n]['sectors_written'] for d in disks if isinstance(d.get(n), dict)}) for n in names}
        out['usb_disks'] = names
        out['usb_sectors_written_values'] = writes
        out['ssd_idle'] = bool(names) and all(len(v) == 1 for v in writes.values())
    return out


def ratio_summary(logs, seed):
    s = stats.paired_summary(logs, seed)
    s['geomean_ratio'] = math.exp(s['mean'])
    s['ratio_ci95'] = [math.exp(v) for v in s['ci95']]
    return s


def pipeline(run_dir, lock, reference_counts=None):
    manifest, rows = load(run_dir)
    cfg = lock['smoke' if manifest['smoke'] else 'full']
    med, counts_n = medians(rows)
    images = sorted(med)
    need = ['clean_total_A', 'clean_total_B', 'adv_total', 'advcap_total', 'clean_forward', 'adv_forward']
    images = [im for im in images if all(a in med[im] for a in need)]
    pooled = {}
    for r in rows:
        if r['kind'] == 'timing' and r['arm'] in ('clean_total_A', 'clean_total_B'):
            pooled.setdefault(r['image'], []).append(r['ns'])
    clean = {im: float(np.median(pooled[im])) for im in images}
    log = lambda a, b: [math.log(a[im] / b[im]) for im in images]
    col = lambda arm: {im: med[im][arm] for im in images}
    out = dict(run_dir=str(run_dir), profile=manifest['profile'], smoke=manifest['smoke'], n_images=len(images),
               unit='image', tag=manifest['tag'], lock_sha256=manifest['lock_sha256'])
    out['gates'] = gates(manifest, rows, lock, cfg['n_images'])
    if len(images) >= 2:
        out['h1_adv_over_clean'] = ratio_summary(log(col('adv_total'), clean), SEED + 1)
        out['h2_advcap_over_adv'] = ratio_summary(log(col('advcap_total'), col('adv_total')), SEED + 2)
        out['aa_cleanA_over_cleanB'] = ratio_summary(log(col('clean_total_A'), col('clean_total_B')), SEED + 3)
        out['advcap_over_clean'] = ratio_summary(log(col('advcap_total'), clean), SEED + 4)
        out['forward_adv_over_clean'] = ratio_summary(log(col('adv_forward'), col('clean_forward')), SEED + 5)
        p = [out['h1_adv_over_clean']['p_sign_flip'], out['h2_advcap_over_adv']['p_sign_flip']]
        out['holm_h1_h2'] = stats.holm(p)
        aa = out['aa_cleanA_over_cleanB']
        out['mde_log_80pct'] = stats.mde_paired(aa['sd'], aa['n'])
        out['mde_ratio_80pct'] = math.exp(out['mde_log_80pct'])
        out['gates']['aa_ok'] = abs(aa['mean']) <= lock['gates']['aa_abs_log']
        out['gates']['mde_ok'] = out['mde_log_80pct'] <= lock['gates']['mde_log']
    ms = lambda d: float(np.median([d[im] for im in images])) / 1e6
    out['median_ms_across_images'] = dict(clean_total=ms(clean), adv_total=ms(col('adv_total')),
                                          advcap_total=ms(col('advcap_total')), clean_forward=ms(col('clean_forward')),
                                          adv_forward=ms(col('adv_forward')))
    out['forward_share'] = dict(clean=float(np.median([med[im]['clean_forward'] / clean[im] for im in images])),
                                adv=float(np.median([med[im]['adv_forward'] / med[im]['adv_total'] for im in images])))
    cr = {r['image']: r['counts'] for r in rows if r['kind'] == 'counts'}
    out['counts'] = {im: {a: {k: cr[im][a][k] for k in ('n_tau', 'k')} for a in ('clean', 'adv', 'advcap')} for im in images}
    out['count_medians'] = {a: dict(n_tau=float(np.median([cr[im][a]['n_tau'] for im in images])),
                                    k=float(np.median([cr[im][a]['k'] for im in images]))) for a in ('clean', 'adv', 'advcap')}
    if reference_counts:
        ref = reference_counts['counts']
        same = lambda a, k: sum(cr[im][a][k] == ref[im][a][k] for im in images)
        out['parity_vs_laptop'] = dict(
            laptop_versions=reference_counts['versions'], n=len(images),
            k_clean_equal=same('clean', 'k'), k_adv_equal=same('adv', 'k'), k_advcap_equal=same('advcap', 'k'),
            n_tau_clean_equal=same('clean', 'n_tau'), n_tau_adv_equal=same('adv', 'n_tau'),
            prediction_bytes_equal=sum(cr[im][a]['prediction_sha256'] == ref[im][a]['prediction_sha256']
                                       for im in images for a in ('clean', 'adv')),
            max_abs_k_diff=max(abs(cr[im][a]['k'] - ref[im][a]['k']) for im in images for a in ('clean', 'adv', 'advcap')))
    gate_keys = ['completed', 'images_complete', 'governor_ok', 'clock_ok', 'swap_off', 'reference_ok', 'pin_ok', 'aa_ok', 'mde_ok']
    if lock.get('allow_usb_storage'):
        gate_keys.append('ssd_idle')
    out['quality_pass'] = all(out['gates'].get(k, False) for k in gate_keys)
    out['sample_counts'] = counts_n
    return out


def stages(run_dir, lock):
    manifest, rows = load(run_dir)
    cfg = lock['smoke' if manifest['smoke'] else 'full']
    med, _ = medians(rows)
    images = sorted(im for im in med if all(a in med[im] for a in ('nms_clean', 'nms_adv', 'mask_clean', 'mask_adv')))
    out = dict(run_dir=str(run_dir), profile=manifest['profile'], smoke=manifest['smoke'], n_images=len(images),
               unit='image', tag=manifest['tag'], label='secondary/descriptive')
    out['gates'] = gates(manifest, rows, lock, cfg['n_images'])
    if len(images) >= 2:
        out['mask_adv_over_clean'] = ratio_summary([math.log(med[im]['mask_adv'] / med[im]['mask_clean']) for im in images], SEED + 6)
        out['nms_adv_over_clean'] = ratio_summary([math.log(med[im]['nms_adv'] / med[im]['nms_clean']) for im in images], SEED + 7)
    out['median_ms_across_images'] = {a: float(np.median([med[im][a] for im in images])) / 1e6
                                      for a in ('nms_clean', 'nms_adv', 'mask_clean', 'mask_adv')}
    dose = {}
    for im in images:
        for arm, v in med[im].items():
            if arm.startswith('maskdose_'):
                dose.setdefault(im, {})[int(arm.split('_')[1])] = v / 1e6
    out['mask_dose_ms'] = dose
    fits = {}
    for im, d in dose.items():
        if len(d) >= 3:
            k = np.array(sorted(d), float)
            y = np.array([d[int(x)] for x in k])
            slope, intercept = np.polyfit(k, y, 1)
            ss = float(((y - (slope * k + intercept)) ** 2).sum())
            fits[im] = dict(slope_ms_per_mask=float(slope), intercept_ms=float(intercept),
                            r2=1 - ss / float(((y - y.mean()) ** 2).sum()), spearman=stats.spearman(k, y))
    out['mask_dose_linear_fit_descriptive'] = fits
    out['quality_pass'] = all(out['gates'].get(k, False) for k in
                              ('completed', 'images_complete', 'governor_ok', 'clock_ok', 'swap_off', 'reference_ok', 'pin_ok'))
    return out


if __name__ == '__main__':
    campaign = Path(sys.argv[1])
    lock = json.loads((Path(__file__).resolve().parent / 'lock.json').read_text())
    ref_path = campaign.parent / 'laptop_reference_counts.json'
    ref = json.loads(ref_path.read_text()) if ref_path.exists() else None
    summary = {}
    for name in ('pipeline_PI4', 'pipeline_PI1', 'stages_PI4'):
        d = campaign / name
        if not (d / 'raw.jsonl').exists():
            summary[name] = dict(missing=True)
            continue
        summary[name] = stages(d, lock) if name.startswith('stages') else pipeline(d, lock, ref)
    (campaign / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    for name, s in summary.items():
        print(name, 'quality_pass' in s and s['quality_pass'], json.dumps(s.get('gates', s))[:400])
