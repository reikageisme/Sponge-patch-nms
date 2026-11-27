"""E10-R — các endpoint MỚI của DRAFT_PREREG_AMD_REVISION_20261127 (endpoint chính kiểu E10 vẫn dùng studies/e10_reference/analyze.py,
vì bản ghi E10-R giữ nguyên các khóa của E10 và chỉ thêm trường).

    python -X utf8 analyze_new.py RUN_DIR [--harm-ms 1.667 --harm-ms 3.333]  -> RUN_DIR/e10r_new_endpoints.json

(a) Phân rã theo (ảnh, phương pháp, seed, backend), trung vị theo lần lặp, trừ trung bình hai nhánh sạch cùng ảnh:
    dTotal, dNMS_micro (NMS vi mô), dNMS_in (NMS đo TRONG lần gọi toàn trình: nms_in_ns), dFwd (fwd_ns),
    rest_in = dTotal - dNMS_in, gap = dNMS_micro - dNMS_in. KTC bootstrap hai tầng ảnh × seed.
(b) dTotal so với từng ngưỡng gây hại (cận dưới KTC > ngưỡng).
(c) MDE trong phiên của nhánh sạch (clean_b so với clean_a, log tỷ số theo ảnh) cho từng backend.
(d) Page fault: tương quan hạng giữa minflt và total_ns của nhánh sạch; trung vị minflt theo trạng thái nhanh/chậm (thăm dò).
Chỉ dùng thư viện chuẩn (dùng lại helper của studies/review_20261127/diag_posthoc.py).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location('diag', SIM / 'studies' / 'review_20261127' / 'diag_posthoc.py')
diag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(diag)


def t_quantile(p, df):
    """Phân vị Student t (xấp xỉ Cornish-Fisher, đủ chính xác với df >= 10)."""
    z = st.NormalDist().inv_cdf(p)
    g1 = (z ** 3 + z) / 4
    g2 = (5 * z ** 5 + 16 * z ** 3 + 3 * z) / 96
    g3 = (3 * z ** 7 + 19 * z ** 5 + 17 * z ** 3 - 15 * z) / 384
    return z + g1 / df + g2 / df ** 2 + g3 / df ** 3


def mde_pct(logs, alpha=.05, power=.8):
    n = len(logs)
    sd = st.stdev(logs)
    # cùng định nghĩa với studies/e10_reference/analyze.py: 100 x MDE trên thang log (stats.mde_paired)
    return 100 * (t_quantile(1 - alpha / 2, n - 1) + t_quantile(power, n - 1)) * sd / math.sqrt(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_dir')
    ap.add_argument('--harm-ms', type=float, action='append')
    a = ap.parse_args()
    run_dir = Path(a.run_dir)
    harm = a.harm_ms or [0.05 * 1000 / 30, 0.10 * 1000 / 30]
    pipe, micro = defaultdict(lambda: defaultdict(list)), defaultdict(list)
    raw = next(run_dir.glob('raw_*.jsonl'))
    for line in raw.read_text(encoding='utf-8').splitlines():
        r = json.loads(line)
        if r['kind'] == 'pipeline':
            k = (r['image_id'], r['arm'], r['seed'], r['backend'])
            for f in ('total_ns', 'fwd_ns', 'nms_in_ns', 'minflt'):
                pipe[k][f].append(r[f])
        elif r['kind'] == 'micro':
            micro[(r['image_id'], r['arm'], r['seed'], r['backend'])].append(r['nms_ns'])
    pm = {k: {f: st.median(v) / (1 if f == 'minflt' else 1e6) for f, v in d.items()} for k, d in pipe.items()}
    mm = {k: st.median(v) / 1e6 for k, v in micro.items()}
    ids = sorted({k[0] for k in pm})
    methods = sorted({k[1] for k in pm if not k[1].startswith('clean')})
    backends = sorted({k[3] for k in pm})
    out = dict(analysis='E10-R new endpoints', raw=str(raw), bootstrap_seed=diag.SEED, n_boot=diag.N_BOOT, harm_ms=harm, cells={}, clean={})
    for m in methods:
        seeds = sorted({k[2] for k in pm if k[1] == m})
        for be in backends:
            mats = defaultdict(list)
            for i in ids:
                c = [(i, 'clean_a', None, be), (i, 'clean_b', None, be)]
                cl = {f: st.mean(pm[x][f] for x in c) for f in ('total_ns', 'fwd_ns', 'nms_in_ns')}
                cmic = st.mean(mm[x] for x in c)
                rows = defaultdict(list)
                for s in seeds:
                    u = (i, m, s, be)
                    d_total = pm[u]['total_ns'] - cl['total_ns']
                    d_in = pm[u]['nms_in_ns'] - cl['nms_in_ns']
                    d_mic = mm[u] - cmic
                    rows['d_total_ms'].append(d_total)
                    rows['d_nms_in_ms'].append(d_in)
                    rows['d_nms_micro_ms'].append(d_mic)
                    rows['d_fwd_ms'].append(pm[u]['fwd_ns'] - cl['fwd_ns'])
                    rows['rest_in_ms'].append(d_total - d_in)
                    rows['micro_minus_in_ms'].append(d_mic - d_in)
                for f, v in rows.items():
                    mats[f].append(v)
            cell = {}
            for f, mat in mats.items():
                cell[f] = dict(mean=st.mean(x for r in mat for x in r), ci95=diag.boot_two_level(mat))
            cell['above_harm'] = {str(h): cell['d_total_ms']['ci95'][0] > h for h in harm}
            out['cells'][f'{m}|{be}'] = cell
    for be in backends:
        logs = [math.log(pm[(i, 'clean_b', None, be)]['total_ns'] / pm[(i, 'clean_a', None, be)]['total_ns']) for i in ids]
        tot = [pm[(i, arm, None, be)]['total_ns'] for i in ids for arm in ('clean_a', 'clean_b')]
        flt = [pm[(i, arm, None, be)]['minflt'] for i in ids for arm in ('clean_a', 'clean_b')]
        split = diag.two_means(tot)
        slow = [f for f, t in zip(flt, tot) if t > split['cut_ms']]
        fast = [f for f, t in zip(flt, tot) if t <= split['cut_ms']]
        out['clean'][be] = dict(in_session_mde_pct=mde_pct(logs), mean_log_ratio=st.mean(logs), n_images=len(ids),
                                split=split, bimodal_flag=diag.bimodal(split), spearman_minflt_total=diag.spearman(flt, tot),
                                median_minflt_slow=st.median(slow) if slow else None, median_minflt_fast=st.median(fast) if fast else None)
    (run_dir / 'e10r_new_endpoints.json').write_text(json.dumps(out, indent=1), encoding='utf-8', newline='\n')
    for k, v in out['cells'].items():
        print(k, {f: round(v[f]['mean'], 3) for f in v if f != 'above_harm'}, 'harm', v['above_harm'])
    for k, v in out['clean'].items():
        print('clean', k, 'MDE %.3f%%' % v['in_session_mde_pct'], 'bimodal', v['bimodal_flag'], 'rho(minflt,total) %.2f' % v['spearman_minflt_total'])


if __name__ == '__main__':
    main()
