# Copied from sponge-sim/studies/pi3b_600mhz_swapguard_v2/analyze.py:1-265
# SHA256 e3e891dae75bf50f7ca10f86c13241bdc65e593746e237c0caa0bd56877e815a; parent protocol remains CLOSED and immutable.
# Copied from sponge-sim/studies/pi3b_600mhz/analyze.py:1-183
# SHA256 8af562c9bca2b3e5c0889e7d11d271e0cd6d70e0c452028e239741ee002aea58; original is immutable.
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
from audit import audit_session, sha  # noqa: E402

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
    return out


def ratio_summary(logs, seed):
    import stats_frozen as stats
    s = stats.paired_summary(logs, seed)
    s['geomean_ratio'] = math.exp(s['mean'])
    s['ratio_ci95'] = [math.exp(v) for v in s['ci95']]
    return s


def pipeline(run_dir, lock, reference_counts=None):
    import stats_frozen as stats
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
    out['quality_pass'] = all(out['gates'].get(k, False) for k in gate_keys)
    out['sample_counts'] = counts_n
    return out


def stages(run_dir, lock):
    import stats_frozen as stats
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


def gate_session(directory, lock_path):
    """Cheap complete-session gate; no bootstrap or sign-flip and no image filtering."""
    lock = json.loads(Path(lock_path).read_text(encoding='utf-8'))
    audit = audit_session(directory, lock, sha(lock_path))
    result = dict(quality_pass=False, audit=audit)
    if not audit['structure_ok']:
        return result
    m, rows = load(directory)
    cfg = lock['smoke' if m['smoke'] else 'full']
    g = gates(m, rows, lock, cfg['n_images'])
    keys = ['completed','images_complete','governor_ok','clock_ok','swap_off','reference_ok','pin_ok']
    if m['mode'] == 'pipeline':
        med, _ = medians(rows)
        logs = [math.log(v['clean_total_A'] / v['clean_total_B']) for v in med.values()]
        g['aa_mean_log'] = float(np.mean(logs))
        # Same operation order as stats_frozen.mde_paired; critical sum locked on laptop.
        critical_sum = lock['mde_t_critical_sums'][str(len(logs))]
        g['mde_log_80pct'] = float(critical_sum * float(np.std(logs, ddof=1)) / np.sqrt(len(logs)))
        g['aa_ok'] = abs(g['aa_mean_log']) <= lock['gates']['aa_abs_log']
        g['mde_ok'] = math.isfinite(g['mde_log_80pct']) and g['mde_log_80pct'] <= lock['gates']['mde_log']
        keys += ['aa_ok','mde_ok']
    else:
        med, _ = medians(rows)
        controls = {}
        for stage in ('nms','mask'):
            logs = [math.log(v[stage+'_adv'] / v[stage+'_adv_B']) for v in med.values()]
            mean = float(np.mean(logs))
            mde = float(lock['mde_t_critical_sums'][str(len(logs))] * float(np.std(logs,ddof=1)) / np.sqrt(len(logs)))
            controls[stage] = dict(mean_log=mean,geomean_ratio=math.exp(mean),mde_log_80pct=mde,
                                   aa_ok=abs(mean)<=lock['gates']['aa_abs_log'],
                                   mde_ok=math.isfinite(mde) and mde<=lock['gates']['mde_log'])
        result['stage_controls'] = controls
        # Two-image smoke checks execution and physical gates. New stage noise gates
        # qualify full-cohort component claims only, prospectively, never retroactively.
        result['stage_aa_enforced'] = not m['smoke']
        if not m['smoke']:
            g['stage_aa_mde_ok'] = all(c['aa_ok'] and c['mde_ok'] for c in controls.values())
            keys += ['stage_aa_mde_ok']
    result['gates'] = g
    result['quality_pass'] = audit['conditions_ok'] and all(g[k] for k in keys)
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('directory', type=Path)
    ap.add_argument('--lock', type=Path, default=Path(__file__).with_name('lock.json'))
    ap.add_argument('--reference', type=Path)
    ap.add_argument('--gate-only', action='store_true')
    args = ap.parse_args()
    if args.gate_only:
        result = gate_session(args.directory, args.lock)
        with (args.directory / 'gates.json').open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result))
        return 0 if result['quality_pass'] else 66
    campaign = args.directory
    lock = json.loads(args.lock.read_text(encoding='utf-8'))
    if not args.reference or sha(args.reference) != lock['reference_counts_sha256']:
        raise ValueError('explicit locked laptop count reference required')
    ref = json.loads(args.reference.read_text(encoding='utf-8'))
    restore_path=campaign/'restore.json'
    restore=json.loads(restore_path.read_text(encoding='utf-8')) if restore_path.exists() else {}
    restored=restore.get('status')=='RESTORED' and restore.get('errors')==[]
    summary = {}
    for name in ('pipeline_PI4', 'pipeline_PI1', 'stages_PI4'):
        d = campaign / name
        if not (d / 'raw.jsonl').exists():
            summary[name] = dict(missing=True, quality_pass=False)
            continue
        gate = gate_session(d, args.lock)
        if not gate['audit']['structure_ok']:
            summary[name] = gate
            continue
        summary[name] = stages(d, lock) if name.startswith('stages') else pipeline(d, lock, ref)
        summary[name]['audit'] = gate['audit']
        summary[name]['gates'].update(gate['gates'])
        summary[name]['campaign_restore_ok'] = restored
        summary[name]['quality_pass'] = gate['quality_pass'] and restored
        if 'stage_controls' in gate:
            summary[name]['stage_controls'] = gate['stage_controls']
            summary[name]['stage_aa_enforced'] = gate['stage_aa_enforced']
    with (campaign / 'summary.json').open('x', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    for name, s in summary.items():
        print(name, 'quality_pass' in s and s['quality_pass'], json.dumps(s.get('gates', s))[:400])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
