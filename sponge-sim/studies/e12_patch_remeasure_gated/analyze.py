"""Phân tích E12 (PREREG_AMD_REPLICATION_20261124 + DRAFT_PREREG_E12).   python analyze.py RUN_DIR OUT_DIR

Viết SAU khi phiên E12 chạy xong (ghi ở DEVIATIONS_AMD_20261124, mục 3): bản nháp PREREG E12 nói dùng
studies/e11_patch_remeasure/analyze.py, nhưng runner E12 ghi điểm tham chiếu dạng kind='block_attempt'
(timing.DriftGate) thay cho kind='reference' của E11, nên analyzer E11 dừng ở max() rỗng.
Ở đây: (1) gọi NGUYÊN logic E11 (không sửa file E11), chỉ đổi bước đọc: mỗi lần thử được NHẬN của một khối thành một điểm
tham chiếu với rel_change = độ lệch lớn nhất (trước/sau so với đầu phiên), flagged = |rel_change| > 3%;
(2) thêm endpoint E12-P4 (TOST 1%, 5% trên tỉ số toàn trình), E12-P5 (ba cách tóm tắt tỉ số N_tau), E12-P6 (đuôi phân phối);
(3) báo cáo cổng trôi (gate_summary) và phân tích độ nhạy ngưỡng 2%.
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

spec = importlib.util.spec_from_file_location('e11a', SIM / 'studies' / 'e11_patch_remeasure' / 'analyze.py')
e11a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e11a)
SEED = e11a.SEED


def gate_rows(run_dir):
    rows = [json.loads(l) for l in next(Path(run_dir).glob('raw_*.jsonl')).read_text(encoding='utf-8').splitlines()]
    att = [r for r in rows if r['kind'] == 'block_attempt']
    summ = [r for r in rows if r['kind'] == 'gate_summary']
    return att, (summ[0] if summ else None)


_orig_load = e11a.load


def load_e12(run_dir):
    micro, pipe, nmap, refs, pin = _orig_load(run_dir)
    att, _ = gate_rows(run_dir)
    for a in att:
        if a['block'] == 'start' or not a['accepted']:
            continue
        d = max((a['rel_before'], a['rel_after']), key=abs)
        refs.append(dict(kind='reference', block=a['block'], rel_change=d, flagged=abs(d) > 0.03, source='block_attempt'))
    return micro, pipe, nmap, refs, pin


def extra(run_dir, out_dir):
    micro, pipe, nmap, refs, pin = _orig_load(run_dir)
    pmed = {k[:4]: float(np.median(v)) for k, v in pipe.items()}
    reps = defaultdict(list)
    for k, v in pipe.items():
        reps[(k[1], k[3])].extend(v)
    att, gsum = gate_rows(run_dir)
    acc = [a for a in att if a['block'] != 'start' and a['accepted']]
    dev = {a['block']: max(abs(a['rel_before']), abs(a['rel_after']), abs(a['rel_within'])) for a in acc}
    out = dict(experiment='E12', run_dir=str(run_dir), bootstrap_seed=SEED, n_boot=stats.N_BOOT,
               gate=dict(summary=gsum, attempts=[a for a in att if a['block'] != 'start'],
                         sensitivity_2pct=dict(blocks_dropped=sorted(b for b, d in dev.items() if d > 0.02),
                                               note='kết quả chính không đổi nếu không khối nào bị bỏ')),
               P4_tost={}, P5_ratio={}, P6_tail={})
    for arm, canvas in e11a.CANVAS.items():
        ca, cb = e11a.CLEAN[canvas]
        ids = sorted({k[0] for k in pmed if k[1] == arm})
        seeds = sorted({k[2] for k in pmed if k[1] == arm})
        if not ids:
            continue
        for be in e11a.PIPE:
            tc = np.array([[np.mean([pmed[(i, ca, None, be)], pmed[(i, cb, None, be)]]) for _ in seeds] for i in ids])
            tp = np.array([[pmed[(i, arm, s, be)] for s in seeds] for i in ids])
            out['P4_tost'][f'{arm}|{be}'] = {f'{m:g}': stats.tost_ratio(tp / tc, m, SEED) for m in (0.01, 0.05)}
        for tau in (0.01, 0.25):
            nc = np.array([nmap[(i, ca, None, tau)] for i in ids], float)
            npat = np.array([[nmap[(i, arm, s, tau)] for s in seeds] for i in ids], float)
            out['P5_ratio'][f'{arm}|tau{tau}'] = stats.ratio_summaries(npat, nc, SEED)
    for (arm, be), v in sorted(reps.items()):
        out['P6_tail'][f'{arm}|{be}'] = stats.tail_summary(v)
    (out_dir / 'e12_extra.json').write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding='utf-8')
    return out


def main():
    run_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    e11a.load = load_e12
    for excl in (False, True):
        sys.argv = ['analyze.py', str(run_dir)] + (['--exclude-flagged'] if excl else [])
        e11a.main()
    ex = extra(run_dir, out_dir)
    print(json.dumps(ex['gate']['summary']), 'sens2%', ex['gate']['sensitivity_2pct']['blocks_dropped'])
    for k, v in ex['P4_tost'].items():
        print('TOST', k, {m: (round(r['mean_ratio'], 4), [round(x, 4) for x in r['ci90_ratio']], r['equivalent']) for m, r in v.items()})


if __name__ == '__main__':
    main()
