"""Nhóm B của kế hoạch sửa bài 27/11/2026 — phân tích POST HOC, chỉ đọc bản ghi thô đã lưu, KHÔNG đo mới.

    python -X utf8 sponge-sim/studies/review_20261127/diag_posthoc.py   (chạy từ gốc repo)
    -> sponge-sim/results/review_20261127/diag_posthoc.json

B1  Thời gian end-to-end của nhánh sạch có hai mức tách bạch không (mọi phiên AMD + A/A Linux)?
    Với E10: trạng thái nhanh/chậm của từng đơn vị có phụ thuộc đơn vị chạy ngay trước không?
B2  Phần dư âm của Bảng 10 (E10: dTotal - dNMS) còn không khi chỉ giữ các cặp cùng trạng thái?
B3  Ngưỡng "gây hại" tạm đề xuất: thêm >= 5% (và 10%) của khung 33,33 ms ở 30 FPS vào t_total
    (1,667 ms và 3,333 ms). Ngưỡng do người viết kế hoạch đề xuất 27/11, CHƯA được tác giả chốt;
    áp lên dữ liệu đã thấy nên là post hoc.

Chỉ dùng thư viện chuẩn Python (máy soạn bài không có numpy; không cài gói theo quy tắc cứng 7).
Bootstrap percentile 20 000 lần, seed cố định; trung vị theo lần lặp như các script gốc.
"""
from __future__ import annotations

import gzip
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]
RES = SIM / 'results'
OUT = RES / 'review_20261127'
SEED = 20261127
N_BOOT = 20000
FRAME_MS = 1000 / 30
HARM = {'5pct_frame30': 0.05 * FRAME_MS, '10pct_frame30': 0.10 * FRAME_MS}
SRC = dict(
    e9='amd_20261124/full-01/e9/run/raw_P1_cpu2.jsonl',
    e10='amd_20261124/full-01/e10/run/raw_P1_cpu2.jsonl',
    e12='amd_20261124/full-01/e12/run/raw_P1_cpu2.jsonl.gz',
    aa320='aa_linux_20261124/x/sponge-aa-20261124/full-01/aa_320/raw_P1_cpu2.jsonl',
    aa640='aa_linux_20261124/x/sponge-aa-20261124/full-01/aa_640/raw_P1_cpu2.jsonl',
)


def rows(key):
    path = RES / SRC[key]
    op = gzip.open if path.suffix == '.gz' else open
    with op(path, 'rt', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line)


def quant(sorted_vals, q):
    i = (len(sorted_vals) - 1) * q
    lo, hi = math.floor(i), math.ceil(i)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (i - lo)


def pct_ci(samples):
    s = sorted(samples)
    return [quant(s, .025), quant(s, .975)]


def boot_mean(values, seed=SEED):
    """Bootstrap percentile của trung bình (đơn vị độc lập = phần tử, ví dụ ảnh)."""
    rng = random.Random(seed)
    n = len(values)
    return pct_ci([sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(N_BOOT)])


def boot_two_level(matrix, seed=SEED):
    """matrix[ảnh][seed]: rút lại ảnh rồi rút lại seed (cột), như stats.two_level_bootstrap (bản không numpy)."""
    rng = random.Random(seed)
    ni, ns = len(matrix), len(matrix[0])
    out = []
    for _ in range(N_BOOT):
        cols = [rng.randrange(ns) for _ in range(ns)]
        tot = 0.0
        for _ in range(ni):
            r = matrix[rng.randrange(ni)]
            tot += sum(r[c] for c in cols) / ns
        out.append(tot / ni)
    return pct_ci(out)


def two_means(values):
    """Chia 1 chiều thành hai cụm, tối thiểu tổng bình phương (duyệt mọi điểm cắt trên mảng đã sắp)."""
    v = sorted(values)
    n = len(v)
    pre = [0.0]
    pre2 = [0.0]
    for x in v:
        pre.append(pre[-1] + x)
        pre2.append(pre2[-1] + x * x)
    best = None
    for k in range(1, n):
        s1, s2 = pre[k], pre[n] - pre[k]
        q1, q2 = pre2[k], pre2[n] - pre2[k]
        sse = (q1 - s1 * s1 / k) + (q2 - s2 * s2 / (n - k))
        if best is None or sse < best[0]:
            best = (sse, k)
    sse, k = best
    lo, hi = v[:k], v[k:]
    pooled = math.sqrt(sse / max(n - 2, 1))
    return dict(n=n, median_ms=st.median(v), low_mean_ms=st.mean(lo), high_mean_ms=st.mean(hi),
                gap_pct=100 * (st.mean(hi) / st.mean(lo) - 1), share_high=len(hi) / n,
                separation_sd=(st.mean(hi) - st.mean(lo)) / pooled if pooled > 0 else float('inf'),
                cut_ms=(v[k - 1] + v[k]) / 2)


def bimodal(d):
    return d['gap_pct'] > 3 and d['separation_sd'] > 5 and min(d['share_high'], 1 - d['share_high']) >= .05


# ------------------------------------------------------------------ B1: các luồng thời gian sạch
def b1_streams():
    streams = defaultdict(list)
    for r in rows('e10'):
        if r['kind'] == 'pipeline' and r['arm'] in ('clean_a', 'clean_b'):
            streams[f'E10|YOLOv5s640|clean|{r["backend"]}'].append(r['total_ns'] / 1e6)
    for r in rows('e9'):
        if r['kind'] == 'cell' and r['n'] == 0 and r['cap'] is None:
            streams[f'E9|YOLOv8n{r["canvas"]}|N0|{r["backend"]}'].append(r['total_ns'] / 1e6)
    for r in rows('e12'):
        if r['kind'] == 'pipeline' and r['arm'] in ('clean_a', 'clean_b'):
            streams[f'E12|YOLOv8n{r["canvas"]}|clean|{r["backend"]}'].append(r['total_ns'] / 1e6)
    for cv in (320, 640):
        for r in rows(f'aa{cv}'):
            if r['kind'] == 'measure':
                streams[f'AA|YOLOv8n{cv}|total'].append(r['stages_ns']['total'] / 1e6)
                streams[f'AA|YOLOv8n{cv}|forward'].append(r['stages_ns']['forward'] / 1e6)
    out = {}
    for k, v in sorted(streams.items()):
        d = two_means(v)
        d['bimodal_flag'] = bimodal(d)
        out[k] = d
    return out


# ------------------------------------------------------------------ E10: đơn vị, trạng thái, phân rã
def e10_units():
    """Đơn vị = (ảnh, nhánh, seed). Trả: thứ tự đơn vị, trung vị pipeline/micro theo backend, N tại tau 0,25."""
    order, pipe, micro, ntau = [], defaultdict(list), defaultdict(list), {}
    for r in rows('e10'):
        if r['kind'] not in ('pipeline', 'micro'):
            continue
        u = (r['image_id'], r['arm'], r['seed'])
        if u not in ntau:
            order.append(u)
            ntau[u] = r['n_by_tau']['0.25']
        if r['kind'] == 'pipeline':
            pipe[u + (r['backend'],)].append(r['total_ns'] / 1e6)
        else:
            micro[u + (r['backend'],)].append(r['nms_ns'] / 1e6)
    pm = {k: st.median(v) for k, v in pipe.items()}
    mm = {k: st.median(v) for k, v in micro.items()}
    backends = sorted({k[3] for k in pm})
    # "nền" của đơn vị = toàn trình - NMS vi mô cùng backend, trung bình 3 backend: xấp xỉ forward + decode + lọc
    base = {u: st.mean(pm[u + (b,)] - mm[u + (b,)] for b in backends) for u in order}
    return order, pm, mm, ntau, base, backends


def b1_e10_mechanism(order, ntau, base):
    split = two_means(list(base.values()))
    state = {u: ('slow' if base[u] > split['cut_ms'] else 'fast') for u in order}
    tab = defaultdict(lambda: defaultdict(int))
    for prev, cur in zip(order, order[1:]):
        kind = 'clean' if prev[1].startswith('clean') else 'perturbed'
        tab[f'prev_{kind}'][state[cur]] += 1
        # cùng ảnh hay sang ảnh mới (mỗi ảnh tải lại tensor sạch)
        tab['prev_same_image' if prev[0] == cur[0] else 'prev_new_image'][state[cur]] += 1
    # trạng thái có giữ nguyên từ đơn vị trước không
    same = sum(state[a] == state[b] for a, b in zip(order, order[1:]))
    # tương quan hạng giữa N(tau 0,25) của đơn vị trước và "nền" của đơn vị sau
    prev_n = [ntau[a] for a in order[:-1]]
    cur_b = [base[b] for b in order[1:]]
    rho = spearman(prev_n, cur_b)
    p_slow = {k: v['slow'] / (v['slow'] + v['fast']) for k, v in tab.items()}
    return dict(split_of_unit_base=split, transitions={k: dict(v) for k, v in tab.items()}, p_slow_given=p_slow,
                state_persists_share=same / (len(order) - 1), spearman_prevN_vs_base=rho,
                n_units=len(order), share_slow=sum(s == 'slow' for s in state.values()) / len(order)), state


def ranks(x):
    idx = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and x[idx[j + 1]] == x[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return num / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))


def b2_decomp(order, pm, mm, state, backends):
    """Như studies/e10_reference/stage_decomp.py, rồi tách theo trạng thái nhánh tấn công so với hai nhánh sạch."""
    ids = sorted({u[0] for u in order})
    methods = sorted({u[1] for u in order if not u[1].startswith('clean')})
    out = {}
    for m in methods:
        seeds = sorted({u[2] for u in order if u[1] == m})
        for be in backends:
            all_rest, matched, by_case = [], defaultdict(list), defaultdict(list)
            mat = []
            for i in ids:
                ca, cb = (i, 'clean_a', None), (i, 'clean_b', None)
                cl_t = (pm[ca + (be,)] + pm[cb + (be,)]) / 2
                cl_n = (mm[ca + (be,)] + mm[cb + (be,)]) / 2
                row = []
                for s in seeds:
                    u = (i, m, s)
                    rest = (pm[u + (be,)] - cl_t) - (mm[u + (be,)] - cl_n)
                    row.append(rest)
                    case = f'attack_{state[u]}|clean_{state[ca]}+{state[cb]}'
                    by_case[case].append(rest)
                    if state[u] == state[ca] == state[cb]:
                        matched[i].append(rest)
                mat.append(row)
                all_rest.extend(row)
            # cặp cùng trạng thái: bootstrap cụm theo ảnh (mỗi ảnh = trung bình các seed khớp)
            per_img = [st.mean(v) for v in matched.values()]
            out[f'{m}|{be}'] = dict(
                rest_all_mean_ms=st.mean(all_rest), rest_all_ci95=boot_two_level(mat),
                rest_state_matched_mean_ms=st.mean(per_img) if per_img else None,
                rest_state_matched_ci95=boot_mean(per_img) if len(per_img) > 1 else None,
                n_images_with_matched_pairs=len(per_img), n_matched_pairs=sum(len(v) for v in matched.values()),
                rest_mean_by_state_case_ms={k: dict(mean=st.mean(v), n=len(v)) for k, v in sorted(by_case.items())})
    return out


# ------------------------------------------------------------------ B3: ngưỡng gây hại
def b3_e9():
    med = defaultdict(list)
    for r in rows('e9'):
        if r['kind'] == 'cell':
            med[(r['canvas'], r['image_id'], r['n'], r['geometry'], r['cap'], r['backend'])].append(r['total_ns'] / 1e6)
    med = {k: st.median(v) for k, v in med.items()}
    out = {}
    for cv in sorted({k[0] for k in med}):
        ids = sorted({k[1] for k in med if k[0] == cv})
        ns = sorted({k[2] for k in med if k[0] == cv and k[2] > 0})
        for be in sorted({k[5] for k in med}):
            for g in ('disjoint', 'mixed', 'dense_cluster'):
                for cap in (None, 300):
                    series = {}
                    for n in ns:
                        if cap is not None and n <= cap:
                            continue
                        d = [med[(cv, i, n, g, cap, be)] - med[(cv, i, 0, 'disjoint', None, be)] for i in ids
                             if (cv, i, n, g, cap, be) in med and (cv, i, 0, 'disjoint', None, be) in med]
                        if d:
                            series[n] = dict(delta_total_ms=st.mean(d), ci95=boot_mean(d), n_images=len(d))
                    if not series:
                        continue
                    nh = {}
                    for hk, thr in HARM.items():
                        hit = [n for n, v in series.items() if v['ci95'][0] > thr]
                        nh[hk] = min(hit) if hit else f'>{max(series)}'
                    out[f'{cv}|{be}|{g}|cap{cap}'] = dict(series={str(k): v for k, v in series.items()}, n_harm=nh)
    return out


def b3_paired(key, arm_ok):
    """E10 / E12: dTotal theo (ảnh, seed) so với trung bình hai nhánh sạch; bootstrap hai tầng."""
    pipe = defaultdict(list)
    for r in rows(key):
        if r['kind'] == 'pipeline':
            pipe[(r.get('canvas', 640), r['image_id'], r['arm'], r['seed'], r['backend'])].append(r['total_ns'] / 1e6)
    pm = {k: st.median(v) for k, v in pipe.items()}
    out = {}
    for cv in sorted({k[0] for k in pm}):
        ids = sorted({k[1] for k in pm if k[0] == cv})
        arms = sorted({k[2] for k in pm if k[0] == cv and arm_ok(k[2])})
        for arm in arms:
            seeds = sorted({k[3] for k in pm if k[0] == cv and k[2] == arm}, key=str)
            for be in sorted({k[4] for k in pm if k[0] == cv}):
                mat = []
                for i in ids:
                    cl = [pm[k] for k in ((cv, i, 'clean_a', None, be), (cv, i, 'clean_b', None, be)) if k in pm]
                    if not cl:
                        cl = [v for k, v in pm.items() if k[0] == cv and k[1] == i and k[2] in ('clean_a', 'clean_b') and k[4] == be]
                    if not cl or any((cv, i, arm, s, be) not in pm for s in seeds):
                        continue
                    c = st.mean(cl)
                    mat.append([pm[(cv, i, arm, s, be)] - c for s in seeds])
                if not mat:
                    continue
                mean = st.mean(x for r in mat for x in r)
                ci = boot_two_level(mat)
                out[f'{cv}|{arm}|{be}'] = dict(delta_total_ms=mean, ci95=ci, n_images=len(mat), n_seeds=len(seeds),
                                               above_harm={hk: ci[0] > thr for hk, thr in HARM.items()},
                                               share_of_frame30_pct=100 * mean / FRAME_MS)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = dict(analysis='Review 27/11 group B, post hoc, saved records only', sources=SRC, bootstrap_seed=SEED, n_boot=N_BOOT,
               harm_thresholds_ms=HARM, harm_threshold_status='proposed 27/11 by the plan, not yet confirmed by the authors')
    res['B1_streams'] = b1_streams()
    order, pm, mm, ntau, base, backends = e10_units()
    res['B1_e10_mechanism'], state = b1_e10_mechanism(order, ntau, base)
    res['B2_e10_decomp_by_state'] = b2_decomp(order, pm, mm, state, backends)
    res['B3_e9_n_harm'] = b3_e9()
    res['B3_e10_delta_total'] = b3_paired('e10', lambda a: not a.startswith('clean'))
    res['B3_e12_delta_total'] = b3_paired('e12', lambda a: not a.startswith('clean'))
    (OUT / 'diag_posthoc.json').write_text(json.dumps(res, indent=1, default=str), encoding='utf-8', newline='\n')
    print('B1 streams:')
    for k, v in res['B1_streams'].items():
        print(f"  {k:34s} n={v['n']:5d} lo={v['low_mean_ms']:.2f} hi={v['high_mean_ms']:.2f} gap={v['gap_pct']:.2f}% "
              f"sep={v['separation_sd']:.1f} shareHi={v['share_high']:.2f} bimodal={v['bimodal_flag']}")
    mech = res['B1_e10_mechanism']
    print('E10 mechanism: p_slow_given', {k: round(v, 3) for k, v in mech['p_slow_given'].items()},
          'persist', round(mech['state_persists_share'], 3), 'rho(prevN, base)', round(mech['spearman_prevN_vs_base'], 3),
          'share_slow', round(mech['share_slow'], 3))
    print('B2:')
    for k, v in res['B2_e10_decomp_by_state'].items():
        print(f"  {k:28s} rest_all={v['rest_all_mean_ms']:.2f} {[round(x, 2) for x in v['rest_all_ci95']]} "
              f"matched={v['rest_state_matched_mean_ms']} {v['rest_state_matched_ci95']} imgs={v['n_images_with_matched_pairs']}")
    print('B3 E9 n_harm (cap None):')
    for k, v in res['B3_e9_n_harm'].items():
        if k.endswith('capNone'):
            print('  ', k, v['n_harm'])
    for key in ('B3_e10_delta_total', 'B3_e12_delta_total'):
        print(key)
        for k, v in res[key].items():
            print(f"   {k:30s} dT={v['delta_total_ms']:.3f} {[round(x, 3) for x in v['ci95']]} frame%={v['share_of_frame30_pct']:.2f} harm={v['above_harm']}")


if __name__ == '__main__':
    main()
