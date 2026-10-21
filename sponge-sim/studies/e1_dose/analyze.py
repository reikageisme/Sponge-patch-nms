"""Phân tích E1 theo PREREG_E1.md. Đọc raw_*.jsonl, ghi summary.json.

CI: bootstrap percentile rút lại LẦN LẶP trong từng ô (20.000, seed 20261021). Lần lặp trong một ô không độc lập
hoàn toàn (cùng phiên, xen kẽ backend) -> CI mô tả độ ổn định của trung vị, không phải độ bất định giữa máy/phiên.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))
from sponge_sim import stats  # noqa: E402

SEED = 20261021
MDE_P1_NMS_TORCH_PURE = 0.0107  # results/e5/20261021T151412/summary.json:profiles.P1.stages.nms_torch_pure.mde_ratio_pct
ULTRA_TIME_LIMIT_NS = 2.05e9


def boot_medians(x, rng, n=stats.N_BOOT):
    x = np.asarray(x, float)
    return np.median(x[rng.integers(0, len(x), (n, len(x)))], axis=1)


def ratio_ci(a, b, seed=SEED):
    rng = np.random.default_rng(seed)
    r = boot_medians(a, rng) / boot_medians(b, rng)
    return float(np.median(a) / np.median(b)), np.quantile(r, [.025, .975]).tolist()


def wilson(k, n, z=1.96):
    if n == 0:
        return [math.nan, math.nan]
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [c - h, c + h]


def main():
    run_dir = Path(sys.argv[1])
    micro, pipe, pins, refs = defaultdict(list), defaultdict(list), {}, defaultdict(list)
    for f in sorted(run_dir.glob('raw_*.jsonl')):
        for line in f.read_text(encoding='utf-8').splitlines():
            r = json.loads(line)
            if r['kind'] == 'pin':
                pins[r['profile']] = dict(readback=r['readback'], **{k: r['verify'][k] for k in
                                          ('effective_cores', 'upper_ok', 'lower_ok', 'passed')})
            elif r['kind'] == 'micro':
                key = (r['profile'], r['anchors'], r['backend'], r['geometry'], r['nc'], r['cap'], r['n'])
                micro[key].append((r['nms_ns'], r['tau_ns']))
            elif r['kind'] == 'pipeline':
                pipe[(r['profile'], r['backend'], r['n'])].append(r['total_ns'])
            elif r['kind'] == 'reference':
                refs[f.stem].append(dict(block=r['block'], rel=r['rel_change'], flagged=r['flagged']))
    nms = {k: np.array([v[0] for v in vs], float) / 1e6 for k, vs in micro.items()}
    tau = {k: np.array([v[1] for v in vs], float) / 1e6 for k, vs in micro.items()}
    out = dict(experiment='E1', run_dir=str(run_dir), bootstrap_seed=SEED, n_boot=stats.N_BOOT, pins=pins,
               reference_drift={k: dict(n=len(v), flagged=sum(x['flagged'] for x in v),
                                        max_abs=max(abs(x['rel']) for x in v)) for k, v in refs.items()})

    # Chính 1
    a = nms.get(('P1', 2100, 'torch_pure', 'disjoint', 80, None, 2100))
    b = nms.get(('P1', 2100, 'torch_pure', 'disjoint', 80, None, 10))
    if a is not None and b is not None:
        R, ci = ratio_ci(a, b)
        out['primary_1'] = dict(R=R, ci95=ci, threshold=1 + MDE_P1_NMS_TORCH_PURE, met=ci[0] > 1 + MDE_P1_NMS_TORCH_PURE,
                                median_ms_N2100=float(np.median(a)), median_ms_N10=float(np.median(b)))
    # Chính 2
    t = pipe.get(('P1', 'torch_pure', 2100))
    if t is not None:
        miss = int((np.asarray(t) / 1e6 > 100.0).sum())
        out['primary_2'] = dict(n=len(t), misses=miss, frac=miss / len(t), wilson95=wilson(miss, len(t)),
                                met=miss / len(t) >= .5, median_total_ms=float(np.median(t) / 1e6))

    # Phụ (a) đường cong + (h) time limit
    curves = {}
    for k, x in sorted(nms.items(), key=lambda kv: tuple(str(v) for v in kv[0])):
        lo, hi = np.quantile(boot_medians(x, np.random.default_rng(SEED)), [.025, .975])
        curves['|'.join(map(str, k))] = dict(median_ms=float(np.median(x)), ci95=[float(lo), float(hi)],
                                             tau_median_ms=float(np.median(tau[k])), n=len(x),
                                             over_ultra_time_limit=int((x * 1e6 > ULTRA_TIME_LIMIT_NS).sum()))
    out['curves'] = curves
    # (b) độ dốc log-log, N >= 100
    slopes = {}
    series = defaultdict(dict)
    for (prof, A, be, geom, nc, cap, n), x in nms.items():
        if n >= 100:
            series[(prof, A, be, geom, nc, cap)][n] = x
    for key, d in series.items():
        ns = sorted(d)
        if len(ns) < 3:
            continue
        lx = np.log(ns)
        rng = np.random.default_rng(SEED)
        meds = np.stack([boot_medians(d[n], rng, 2000) for n in ns], 1)  # 2.000 cho chi phí
        bs = np.polyfit(lx, np.log(meds.T), 1)[0]
        slope = float(np.polyfit(lx, np.log([np.median(d[n]) for n in ns]), 1)[0])
        slopes['|'.join(map(str, key))] = dict(slope=slope, ci95=np.quantile(bs, [.025, .975]).tolist(), n_levels=len(ns),
                                               note='mô tả; không suy bậc phức tạp', n_boot=2000)
    out['loglog_slopes'] = slopes
    # (c) backend / tv_nms, (d) disjoint / dense, (e) cap300 / capNone, (f) nc80 / nc1
    contrasts = defaultdict(dict)
    for (prof, A, be, geom, nc, cap, n), x in nms.items():
        ref = nms.get((prof, A, 'tv_nms', geom, nc, cap, n))
        if be != 'tv_nms' and ref is not None:
            contrasts['backend_over_tv_nms'][f'{prof}|{A}|{be}|{geom}|{nc}|{cap}|{n}'] = ratio_ci(x, ref)
        dense = nms.get((prof, A, be, 'dense_cluster', nc, cap, n))
        if geom == 'disjoint' and dense is not None:
            contrasts['disjoint_over_dense'][f'{prof}|{A}|{be}|{nc}|{cap}|{n}'] = ratio_ci(x, dense)
        nocap = nms.get((prof, A, be, geom, nc, None, n))
        if cap == 300 and n >= 600 and nocap is not None:
            contrasts['cap300_over_capNone'][f'{prof}|{A}|{be}|{geom}|{nc}|{n}'] = ratio_ci(x, nocap)
        nc1 = nms.get((prof, A, be, geom, 1, cap, n))
        if nc == 80 and nc1 is not None and be in ('tv_batched', 'ultra_native'):
            contrasts['nc80_over_nc1'][f'{prof}|{A}|{be}|{geom}|{cap}|{n}'] = ratio_ci(x, nc1)
    out['contrasts'] = {k: {kk: dict(ratio=vv[0], ci95=vv[1]) for kk, vv in v.items()} for k, v in contrasts.items()}
    # (g) phần B
    out['pipeline'] = {f'{p}|{be}|{n}': dict(median_total_ms=float(np.median(t) / 1e6), n=len(t),
                                             misses_100ms=int((np.asarray(t) / 1e6 > 100).sum()),
                                             wilson95=wilson(int((np.asarray(t) / 1e6 > 100).sum()), len(t)))
                       for (p, be, n), t in pipe.items()}
    (run_dir / 'summary.json').write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: out.get(k) for k in ('pins', 'primary_1', 'primary_2')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
