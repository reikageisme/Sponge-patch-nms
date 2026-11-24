"""Phân tích POST HOC trên phiên AMD full-01 (PREREG_AMD_REPLICATION_20261124), chỉ đọc raw đã đo, không đo mới.
    python posthoc_amd.py E1_SUMMARY E12_RUN E10_RUN OUT_JSON

Thay cho các số laptop vẫn dùng trong bài mà không có runner riêng:
  n_only    dự đoán t_NMS chỉ từ N (đường cong E1 AMD, head 2100 anchor, 80 lớp, không cap; nội suy log-log như
            studies/e6_remeasure/analyze.py: curve/predict, gọi lại nguyên hàm) cho mọi đơn vị micro tau 0,01 của các nhánh
            320 px của E12 (clean_a, clean_b, C1, C3, B1-B4); thêm tỷ lệ điểm nằm giữa đường rời nhau và cụm dày.
  rho       Spearman giữa N và t_NMS trên ảnh sạch (clean_a) và giữa dN và dt do patch (nhánh 320 px), như E6.
  struct    E10: mô hình chỉ-NMS với thời gian NMS đo của chính tập ứng viên, R_struct = 1 + dNMS/T_clean, so với R đo;
            và tỷ phần NMS trong toàn trình sau tấn công (giống structural_check_posthoc.json của laptop).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))
from sponge_sim import stats  # noqa: E402

spec = importlib.util.spec_from_file_location('e6a', SIM / 'studies' / 'e6_remeasure' / 'analyze.py')
e6a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e6a)
BE = ['torch_pure', 'tv_nms', 'tv_batched', 'ultra_native']
A320 = ['clean_a', 'clean_b', 'C1', 'C3', 'B1', 'B2', 'B3', 'B4']
PATCH320 = ['C1', 'C3', 'B1', 'B2', 'B3', 'B4']


def rows(run_dir):
    for line in open(next(Path(run_dir).glob('raw_*.jsonl')), encoding='utf-8'):
        yield json.loads(line)


def n_only(curves, e12):
    med, nmap = defaultdict(list), {}
    for r in rows(e12):
        if r['kind'] == 'micro' and r['tau'] == 0.01 and r['arm'] in A320:
            k = (r['image_id'], r['arm'], r['seed'], r['backend'])
            med[k].append(r['nms_ns'] / 1e6)
            nmap[k[:3]] = r['nms_input']
    med = {k: float(np.median(v)) for k, v in med.items()}
    pred = {}
    for be in BE:
        errs, inside = [], 0
        for (i, arm, s, b), t in med.items():
            n = nmap[(i, arm, s)]
            if b != be or n <= 0:
                continue
            ps = {g: e6a.predict(*e6a.curve(curves, 'P1_cpu2', 2100, be, g), n) for g in e6a.GEOMS}
            errs.append(abs(np.log(t / ps['mixed'])))
            inside += int(min(ps.values()) <= t <= max(ps.values()))
        pred[be] = dict(n_points=len(errs), median_abs_log_error_vs_mixed=float(np.median(errs)),
                        p90_abs_log_error=float(np.quantile(errs, .9)), fraction_inside_envelope=inside / len(errs))
    rho = {}
    ids = sorted({k[0] for k in med})
    for be in BE:
        nc = np.array([nmap[(i, 'clean_a', None)] for i in ids], float)
        tc = np.array([med[(i, 'clean_a', None, be)] for i in ids])
        rho[f'between_clean|{be}'] = stats.spearman(nc, tc)
        for arm in PATCH320:
            seeds = sorted({k[2] for k in nmap if k[1] == arm})
            dN = np.array([[nmap[(i, arm, s)] - nmap[(i, 'clean_a', None)] for s in seeds] for i in ids], float)
            dt = np.array([[med[(i, arm, s, be)] - np.mean([med[(i, 'clean_a', None, be)], med[(i, 'clean_b', None, be)]]) for s in seeds] for i in ids])
            rho[f'dN_dt|{arm}|{be}'] = stats.spearman(dN.ravel(), dt.ravel())
    return pred, rho


def struct(e10):
    cell = {'micro': defaultdict(list), 'pipeline': defaultdict(list)}
    for r in rows(e10):
        if r['kind'] in cell:
            cell[r['kind']][(r['image_id'], r['arm'], r['seed'], r['backend'])].append((r['nms_ns'] if r['kind'] == 'micro' else r['total_ns']) / 1e6)
    med = {k: {kk: float(np.median(v)) for kk, v in d.items()} for k, d in cell.items()}
    ids = sorted({k[0] for k in med['pipeline']})
    out = {}
    for m in ('overload', 'phantom_sponges'):
        seeds = sorted({k[2] for k in med['pipeline'] if k[1] == m})
        for be in sorted({k[3] for k in med['pipeline']}):
            cl = lambda kind, i: np.mean([med[kind][(i, 'clean_a', None, be)], med[kind][(i, 'clean_b', None, be)]])  # noqa: E731
            err, share = [], []
            for i in ids:
                for s in seeds:
                    tp, np_ = med['pipeline'][(i, m, s, be)], med['micro'][(i, m, s, be)]
                    r_meas = tp / cl('pipeline', i)
                    r_struct = 1 + (np_ - cl('micro', i)) / cl('pipeline', i)
                    err.append(abs(np.log(r_meas / r_struct)))
                    share.append(np_ / tp)
            out[f'{m}|{be}'] = dict(median_abs_log_err_struct=float(np.median(err)), nms_share_patched=float(np.median(share)))
    return out


def main():
    e1, e12, e10, out = sys.argv[1:5]
    curves = json.loads(Path(e1).read_text(encoding='utf-8'))['curves']
    pred, rho = n_only(curves, e12)
    res = dict(analysis='AMD post hoc (no new measurement)', e1=e1, e12=e12, e10=e10,
               n_only_prediction_from_e1=pred, rho=rho, structural_check=struct(e10))
    Path(out).write_text(json.dumps(res, indent=1), encoding='utf-8')
    print(json.dumps({k: res[k] for k in ('n_only_prediction_from_e1', 'structural_check')}, indent=0)[:3000])


if __name__ == '__main__':
    main()
