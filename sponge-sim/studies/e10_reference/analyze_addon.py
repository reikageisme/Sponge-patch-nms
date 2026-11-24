"""Phân tích bổ sung cho E10 sau phản biện 16/11/2026. POST HOC, chỉ dùng raw đã đo; không thay analyze.py.

    python analyze_addon.py RUN_DIR E1_SUMMARY OUT_JSON

Cùng đơn vị (ảnh, phương pháp, seed), cùng mẫu số sạch, cùng nội suy đường cong E1 và cùng seed bootstrap như analyze.py. Thêm:
  model      mô hình ngân sách so với mô hình rỗng R_pred = 1: sai số từng đơn vị, luật pass 0,05 cho cả hai, skill, độ lệch có dấu
  tost       TOST biên 1% và 5% cho tỉ số toàn trình (và cho A/A clean_b / clean_a)
  n_ratio    N_tau: trung bình tỉ số, trung vị tỉ số, tỉ số hai trung vị
  tails      p95, p99, tỉ lệ vượt 33,3 ms và 100 ms trên từng lần lặp
  criterion  tiêu chí viết theo Delta t_total: Delta t_total và Delta t_NMS so với ngưỡng MDE_trong_phiên x t_total_sạch
"""
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))
from sponge_sim import stats  # noqa: E402

SEED = 20261021
spec = importlib.util.spec_from_file_location('e10a', Path(__file__).with_name('analyze.py'))
e10a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e10a)


def load(run):
    micro, pipe, reps, nmap = defaultdict(list), defaultdict(list), defaultdict(list), {}
    for line in open(next(Path(run).glob('raw_*.jsonl')), encoding='utf-8'):
        r = json.loads(line)
        if r['kind'] == 'micro':
            micro[(r['image_id'], r['arm'], r['seed'], r['backend'])].append(r['nms_ns'] / 1e6)
            nmap[(r['image_id'], r['arm'], r['seed'])] = (r['n_by_tau'], r['nms_input'], r['kept'])
        elif r['kind'] == 'pipeline':
            pipe[(r['image_id'], r['arm'], r['seed'], r['backend'])].append(r['total_ns'] / 1e6)
            reps[(r['arm'], r['backend'])].append(r['total_ns'] / 1e6)
    return {k: float(np.median(v)) for k, v in micro.items()}, {k: float(np.median(v)) for k, v in pipe.items()}, reps, nmap


def analyse(run, e1_summary, n_boot=stats.N_BOOT):
    curves = json.loads(Path(e1_summary).read_text(encoding='utf-8'))['curves']
    mm, pm, reps, nmap = load(run)
    ids = sorted({k[0] for k in pm})
    seeds = sorted({k[2] for k in pm if k[2] is not None})
    methods = sorted({k[1] for k in pm if k[1] not in ('clean_a', 'clean_b')})
    pbe = sorted({k[3] for k in pm})
    ci = lambda M, **kw: [float(x) for x in stats.two_level_bootstrap(M, SEED, n_boot=n_boot, **kw)]
    clean_t = {(i, be): float(np.median([pm[(i, 'clean_a', None, be)], pm[(i, 'clean_b', None, be)]])) for i in ids for be in pbe}
    out = dict(analysis='E10 addon (post hoc, review 2026-11-16)', run_dir=str(run), bootstrap_seed=SEED, n_boot=n_boot, n_images=len(ids),
               seeds=seeds, model={}, tost={}, n_ratio={}, tails={}, criterion={})
    for be in pbe:
        aa = np.array([[pm[(i, 'clean_b', None, be)] / pm[(i, 'clean_a', None, be)]] for i in ids])
        d = np.log(aa[:, 0])
        mde = stats.mde_paired(float(np.std(d, ddof=1)), len(d))
        out['tost'][f'A/A|{be}'] = {str(m): stats.tost_ratio(aa, m, SEED, n_boot) for m in (.01, .05)}
        out['tails'][f'clean|{be}'] = stats.tail_summary(reps[('clean_a', be)] + reps[('clean_b', be)])
        ns_c, ms_c = e10a.curve(curves, be, 'mixed')
        for m in methods:
            R = np.array([[pm[(i, m, s, be)] / clean_t[(i, be)] for s in seeds] for i in ids])
            Rp = np.array([[1 + (e10a.f_interp(ns_c, ms_c, nmap[(i, m, s)][1]) - e10a.f_interp(ns_c, ms_c, nmap[(i, 'clean_a', None)][1])) / clean_t[(i, be)]
                            for s in seeds] for i in ids])
            out['model'][f'{m}|{be}'] = stats.skill_vs_null(R, Rp, SEED, n_boot)
            out['tost'][f'{m}|{be}'] = {str(x): stats.tost_ratio(R, x, SEED, n_boot) for x in (.01, .05)}
            out['tails'][f'{m}|{be}'] = stats.tail_summary(reps[(m, be)])
            dT = np.array([[pm[(i, m, s, be)] - clean_t[(i, be)] for s in seeds] for i in ids])
            thr = mde * float(np.median([clean_t[(i, be)] for i in ids]))
            row = dict(in_session_mde_pct=100 * mde, threshold_ms=thr, d_total_ms=float(dT.mean()), d_total_ci95=ci(dT), d_total_above_threshold=bool(ci(dT)[0] > thr))
            if (ids[0], m, seeds[0], be) in mm and (ids[0], 'clean_a', None, be) in mm:
                dN = np.array([[mm[(i, m, s, be)] - mm[(i, 'clean_a', None, be)] for s in seeds] for i in ids])
                row.update(d_nms_ms=float(dN.mean()), d_nms_ci95=ci(dN), d_nms_above_threshold=bool(ci(dN)[0] > thr),
                           share_outside_nms=float(1 - dN.mean() / dT.mean()))
            out['criterion'][f'{m}|{be}'] = row
    for m in methods:
        for tau in ('0.01', '0.25'):
            Na = np.array([[nmap[(i, m, s)][0][tau] for s in seeds] for i in ids], float)
            Nc = np.array([nmap[(i, 'clean_a', None)][0][tau] for i in ids], float)
            out['n_ratio'][f'{m}|tau{tau}'] = stats.ratio_summaries(Na, Nc, SEED, n_boot)
    return out


if __name__ == '__main__':
    res = analyse(sys.argv[1], sys.argv[2])
    Path(sys.argv[3]).write_text(json.dumps(res, indent=1), encoding='utf-8')
    print(json.dumps({k: dict(skill=v['skill'], model_passes=v['model_passes'], null_passes=v['null_passes']) for k, v in res['model'].items()}, indent=1))
