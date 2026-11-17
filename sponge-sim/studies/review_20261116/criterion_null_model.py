"""Kiểm lại tiêu chí "Delta t_NMS > MDE x t_total", luật pass của mô hình ngân sách và cách tóm tắt N_tau.
Chỉ đọc các file summary đã có trong repo (không đo lại, không cần GPU).

    python studies/review_20261116/criterion_null_model.py <gốc repo> sponge-sim/results/review_20261116

Trả lời các điểm phản biện:
  W2  tiêu chí viết theo Delta t_NMS bị Table 8 phản ví dụ -> viết theo Delta t_total thì nhất quán
  W2  luật "cận dưới CI > 1 + MDE" so với ngưỡng hiệu ứng cố định (1%, 5%)
  W3  luật pass |ln(R_meas / R_pred)| < 0.05 không phân biệt được với mô hình rỗng R_pred = 1
  Kiểm số: "340-389 lần" là trung bình tỉ số, không phải tỉ số trung vị; khoảng tin cậy ở bảng patch có chứa 1 hay không
"""
import json
import math
import sys
from pathlib import Path

repo = Path(sys.argv[1])
out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / 'ket_qua'
out_dir.mkdir(parents=True, exist_ok=True)
R = repo / 'sponge-sim' / 'results'
J = lambda p: json.loads((R / p).read_text(encoding='utf-8'))
e10 = J('e10/E10_P1cpu2_20261102/summary.json')
dec = J('e10/E10_P1cpu2_20261102/stage_decomp_posthoc.json')['cells']
med = J('e10/E10_P1cpu2_20261102/stage_medians_posthoc.json')
e11 = J('e11/E11_P1cpu2_20261103/summary.json')
res, md = {}, ['# A1. Tiêu chí, mô hình rỗng và cách tóm tắt N_tau', '', f'Nguồn: `{R}` (E10, E11).', '']

# ---- 1. tiêu chí theo Delta t_NMS so với theo Delta t_total
md += ['## 1. Tiêu chí hiển thị end-to-end (E10: YOLOv5s, 640 px)', '',
       '| Tấn công | NMS | MDE trong phiên | Ngưỡng Δt* (ms) | Δt_NMS (ms) | Δt_total (ms) | Bảng ghi "vượt MDE" | Δt_NMS > Δt* | Δt_total > Δt* |',
       '|---|---|---|---|---|---|---|---|---|']
rows = []
for key, tr in e10['total_ratio'].items():
    m, be = key.split('|')
    mde = e10['in_session_mde_pct'][be] / 100
    t_clean = med['total_ms'][f'clean|{be}']['median']
    thr = mde * t_clean
    d = dec[key]
    row = dict(attack=m, backend=be, mde_pct=100 * mde, threshold_ms=thr, d_nms_ms=d['d_nms_ms'], d_total_ms=d['d_total_ms'],
               table_says_above_mde=tr['exceeds_in_session_mde'], nms_criterion=d['d_nms_ms'] > thr, total_criterion=d['d_total_ms'] > thr,
               ratio=tr['mean'], ci95=tr['ci95'])
    row['counterexample_to_only_if'] = row['table_says_above_mde'] and not row['nms_criterion']
    rows.append(row)
    yn = lambda b: 'có' if b else 'không'
    md.append(f"| {m} | {be} | {100 * mde:.2f}% | {thr:.1f} | {d['d_nms_ms']:.1f} | {d['d_total_ms']:.1f} | {yn(row['table_says_above_mde'])} | {yn(row['nms_criterion'])} | {yn(row['total_criterion'])} |")
n_ce = sum(r['counterexample_to_only_if'] for r in rows)
res['criterion'] = dict(rows=rows, counterexamples_to_only_if=n_ce,
                        delta_total_exceeds_threshold_in=f"{sum(r['total_criterion'] for r in rows)}/{len(rows)}")
md += ['', f'- Số ô phản ví dụ cho câu "chỉ thấy được **khi** Δt_NMS > MDE × t_total": **{n_ce}/{len(rows)}** (bảng ghi vượt MDE trong khi Δt_NMS dưới ngưỡng).',
       f"- Viết theo Δt_total thì điều kiện cần đúng ở {res['criterion']['delta_total_exceeds_threshold_in']} ô: phần tăng ngoài NMS (lọc điểm, forward) cũng góp vào.",
       '- Lưu ý: cột "vượt MDE" của bảng dùng cận dưới khoảng tin cậy của tỉ số, còn hai cột cuối so trung bình với ngưỡng. Hai phép này khác nhau, nên bài phải nói rõ dùng phép nào.', '']

# ---- 2. luật quyết định: 1 + MDE so với ngưỡng cố định
md += ['## 2. Cùng dữ liệu, ba luật quyết định', '',
       '| Tấn công | NMS | Tỉ số (CI 95%) | CI loại 1 | cận dưới > 1 + MDE | cận dưới > 1,01 | cận dưới > 1,05 |', '|---|---|---|---|---|---|---|']
for r in rows:
    lo, hi = r['ci95']
    r['rules'] = dict(ci_excludes_1=lo > 1, above_mde=lo > 1 + r['mde_pct'] / 100, above_1pct=lo > 1.01, above_5pct=lo > 1.05)
    yn = lambda b: 'có' if b else 'không'
    md.append(f"| {r['attack']} | {r['backend']} | {r['ratio']:.3f} ({lo:.3f} đến {hi:.3f}) | {yn(lo > 1)} | {yn(r['rules']['above_mde'])} | {yn(lo > 1.01)} | {yn(lo > 1.05)} |")
md += ['', '- Mọi ô đều có khoảng tin cậy loại 1: hiệu ứng có thật và vào khoảng 3%. Câu đúng là "tăng khoảng 3%, dưới ngưỡng 5%", không phải "không thấy được".',
       '- MDE là đại lượng thiết kế, đổi theo cỡ mẫu và phiên đo; nên báo thêm một ngưỡng hiệu ứng cố định có ý nghĩa vận hành.', '']

# ---- 3. mô hình rỗng
md += ['## 3. Luật pass của mô hình ngân sách so với mô hình rỗng R_pred = 1', '',
       '| Tấn công | NMS | R đo | R dự đoán | sai số mô hình (trung vị, cận trên CI) | pass | sai số mô hình rỗng (xấp xỉ) | mô hình rỗng dưới 0,05 |', '|---|---|---|---|---|---|---|---|']
null_rows = []
for key, a in e10['amdahl'].items():
    m, be = key.split('|')
    null_err = abs(math.log(a['r_meas_mean']))
    null_rows.append(dict(attack=m, backend=be, r_meas=a['r_meas_mean'], r_pred=a['r_pred_mean'], model_err=a['median_abs_log_err'],
                          model_err_ci_hi=a['ci95'][1], passes=a['passes_prereg_rule'], null_err_approx=null_err, null_below_0_05=null_err < 0.05,
                          err_of_means=abs(math.log(a['r_meas_mean'] / a['r_pred_mean']))))
    md.append(f"| {m} | {be} | {a['r_meas_mean']:.3f} | {a['r_pred_mean']:.3f} | {a['median_abs_log_err']:.3f} (≤ {a['ci95'][1]:.3f}) | {'có' if a['passes_prereg_rule'] else 'không'} | {null_err:.3f} | {'có' if null_err < 0.05 else 'không'} |")
res['null_model'] = dict(rows=null_rows, model_passes=sum(r['passes'] for r in null_rows), null_point_below_0_05=sum(r['null_below_0_05'] for r in null_rows),
                         note='sai số mô hình rỗng tính từ trung bình R đo; con số chính xác theo từng đơn vị cần file raw (xem studies/e10_reference/analyze_addon.py)')
md += ['', f"- Mô hình ngân sách pass {res['null_model']['model_passes']}/6 ô. Mô hình rỗng (luôn đoán \"không chậm đi\") có sai số điểm dưới 0,05 ở {res['null_model']['null_point_below_0_05']}/6 ô.",
       '- Vậy luật pass hiện tại không chứng tỏ mô hình có sức dự đoán. Cần báo sai số mô hình rỗng bên cạnh và một skill score, tính trên từng đơn vị (ảnh, seed).',
       '- Sai số theo đơn vị (cột 5) lớn hơn nhiều so với sai số giữa hai trung bình: nhiễu từng đơn vị chi phối, không phải độ lệch của mô hình.', '']

# ---- 4. N_tau: trung bình tỉ số so với tỉ số trung vị
md += ['## 4. "N_tau tăng bao nhiêu lần" phụ thuộc cách tóm tắt', '', '| Tấn công | tau | Trung bình các tỉ số (CI 95%) | Trung vị sạch → bị tấn công | Tỉ số hai trung vị |', '|---|---|---|---|---|']
nt = []
for key, v in e10['n_ratio'].items():
    nm = e10['n_median'][key]
    rm = nm['patched'] / nm['clean']
    nt.append(dict(cell=key, mean_of_ratios=v['mean'], ci95=v['ci95'], median_clean=nm['clean'], median_attacked=nm['patched'], ratio_of_medians=rm))
    m, tau = key.split('|tau')
    md.append(f"| {m} | {tau} | {v['mean']:.0f} ({v['ci95'][0]:.0f} đến {v['ci95'][1]:.0f}) | {nm['clean']:.1f} → {nm['patched']:.1f} | {rm:.0f} |")
res['n_tau'] = nt
md += ['', '- Con số "340 đến 389 lần" trong abstract là trung bình các tỉ số, bị kéo bởi các ảnh có N sạch rất nhỏ. Theo trung vị chỉ khoảng 107 đến 124 lần. Bài phải ghi rõ thống kê nào, tốt nhất báo cả hai.', '']

# ---- 5. bảng patch: khoảng tin cậy của tỉ số N có chứa 1 không
md += ['## 5. Bảng patch (E11): tỉ số N_tau và khoảng tin cậy', '', '| Nhánh | tau | Tỉ số N (CI 95%) | CI chứa 1 | Hướng |', '|---|---|---|---|---|']
pt = []
for arm, a in e11['arms'].items():
    for k, v in a.items():
        if k.startswith('N_tau') and isinstance(v, dict) and 'ratio_ci95' in v:
            lo, hi = v['ratio_ci95']
            d = 'tăng' if lo > 1 else 'giảm' if hi < 1 else 'không rõ'
            pt.append(dict(arm=arm, tau=k[5:], ratio=v['ratio_mean'], ci95=[lo, hi], contains_1=lo <= 1 <= hi, direction=d))
            md.append(f"| {arm} | {k[5:]} | {v['ratio_mean']:.2f} ({lo:.2f} đến {hi:.2f}) | {'có' if lo <= 1 <= hi else 'không'} | {d} |")
res['patch_table'] = pt
up = [p for p in pt if p['direction'] == 'tăng']
down = [p for p in pt if p['direction'] == 'giảm']
md += ['', f'- {len(up)} dòng có khoảng tin cậy nằm trên 1 và {len(down)} dòng nằm dưới 1. Câu "the intervals of the ratio contain 1" không đúng cho mọi dòng; các dòng giảm cũng cần được bàn.', '']

(out_dir / 'a1_criterion_null_model.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
(out_dir / 'a1_criterion_null_model.md').write_text('\n'.join(md), encoding='utf-8')
print('\n'.join(md))
