"""Sinh mọi bảng số của paper_vi/main_vi.tex từ các tệp tóm tắt trong sponge-sim/results (mỗi bảng một tệp .tex được \\input).

    python paper_vi/tables/make_tables.py          # ghi paper_vi/tables/tab_*.tex và numbers.json
    python paper_vi/tables/make_tables.py --check  # chỉ so: báo bảng nào khác bản sinh lại (sửa tay) -> mã thoát 1

Không sửa tay các tệp tab_*.tex. numbers.json ghi từng ô số kèm nguồn (tệp:selector) cho check_numbers.py.
Bảng phụ thuộc E11 (patch, cài đặt, ngưỡng) in \\todo khi chưa có results/e11/E11_*/summary.json.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'sponge-sim' / 'results'
OUT = Path(__file__).resolve().parent
REG = {}  # tên bảng -> list (chuỗi hiển thị, nguồn)

BE = ['torch_pure', 'tv_nms', 'tv_batched', 'ultra_native']
BE_VI = {'torch_pure': 'PyTorch thuần', 'tv_nms': 'torchvision \\texttt{nms}', 'tv_batched': 'torchvision theo lô', 'ultra_native': 'Ultralytics gốc'}
GEOM = ['disjoint', 'mixed', 'dense_cluster']
GEOM_VI = {'disjoint': 'rời nhau', 'mixed': 'hỗn hợp', 'dense_cluster': 'cụm dày đặc'}


def j(rel):
    return json.loads((RES / rel).read_text(encoding='utf-8'))


class Tab:
    def __init__(self, name):
        self.name, self.cells = name, []

    def n(self, x, src, d=None, sig=None):
        """Định dạng số (dấu phẩy thập phân) và ghi nguồn."""
        if isinstance(x, str):
            s = '$>$' + x[1:] if x.startswith('>') else x
        elif isinstance(x, int) and d is None and sig is None:
            s = f'{x}'
        else:
            if sig is not None:
                d = max(sig - 1 - int(math.floor(math.log10(abs(x)))), 0) if x else 0
            s = f'{x:.{d}f}'
        s = s.replace('.', '{,}' if False else ',')
        if s.startswith('-'):
            s = '$-$' + s[1:]
        self.cells.append((s, src))
        return s

    def ci(self, lo, hi, src, d=None, sig=None, sep='--'):
        return self.n(lo, src + '[0]', d, sig) + sep + self.n(hi, src + '[1]', d, sig)


def write(tab, body):
    REG[tab.name] = [dict(text=s, source=src) for s, src in tab.cells]
    return tab.name, body


# ---------------------------------------------------------------- A/A
def t_aa():
    t = Tab('tab_aa')
    f320, f640, f640a = 'e5/AA_P1cpu2_20261101/summary.json', 'e5/AA640_P1cpu2_20261102b/summary.json', 'e5/AA640_P1cpu2_20261102/summary.json'
    a, b, c = (j(f)['profiles']['P1_cpu2'] for f in (f320, f640, f640a))
    rows = [('pre', 'Tiền xử lý'), ('forward', 'Lan truyền thuận'), ('tau', 'Lọc điểm ($\\tau$)'), ('nms_torch_pure', 'NMS (PyTorch thuần)'),
            ('nms_tv_nms', 'NMS (torchvision)'), ('total', 'Toàn trình')]
    lines = []
    for k, lab in rows:
        cells = []
        for f, p in ((f320, a), (f640, b)):
            st = p['stages'][k]
            cells += [t.n(st['mde_ratio_pct'], f'{f}:profiles.P1_cpu2.stages.{k}.mde_ratio_pct', d=2),
                      t.n(st['median_of_image_medians_ms'], f'{f}:profiles.P1_cpu2.stages.{k}.median_of_image_medians_ms', sig=3)]
        lines.append(f'{lab} & ' + ' & '.join(cells) + ' \\\\')
    st = c['stages']['total']
    lines.append('Toàn trình, lần A/A 640 px đầu (bị nhiễu) & & & ' + t.n(st['mde_ratio_pct'], f'{f640a}:profiles.P1_cpu2.stages.total.mde_ratio_pct', d=2)
                 + ' & ' + t.n(st['median_of_image_medians_ms'], f'{f640a}:profiles.P1_cpu2.stages.total.median_of_image_medians_ms', sig=3) + ' \\\\')
    fl = lambda p, f: t.n(len(p['drift']['flagged']), f'{f}:profiles.P1_cpu2.drift.flagged(len)') + '/' + t.n(p['drift']['reference_points'], f'{f}:profiles.P1_cpu2.drift.reference_points')  # noqa: E731
    lines.append('Điểm tham chiếu bị cờ / tổng & ' + fl(a, f320) + ' & & ' + fl(b, f640) + ' & \\\\')
    eff = t.n(a['pin']['effective_cores'], f'{f320}:profiles.P1_cpu2.pin.effective_cores', d=2)
    body = rf"""\begin{{table}}[t]
\centering\small
\caption{{Hiệu chuẩn A/A trên profile laptop đã ghim lõi (CPU logic 2; số lõi hiệu dụng dưới tải {eff} ở 320 px): MDE (\%) và thời gian trung vị mỗi công đoạn, 100 ảnh $\times$ 20 lần lặp. Toàn trình của A/A tính từ ảnh đã nạp, gồm cả tiền xử lý (đổi kích thước); các phép đo patch và tiêm bắt đầu từ tensor đã chuẩn bị nên có $t_{{\mathrm{{total}}}}$ nhỏ hơn. 640 px: lần A/A đo lại. Các khối bị cờ drift vẫn nằm trong phân tích.}}
\label{{tab:aa}}
\begin{{tabular}}{{@{{}}lcccc@{{}}}}
\toprule
 & \multicolumn{{2}}{{c}}{{320 px}} & \multicolumn{{2}}{{c}}{{640 px}} \\
\cmidrule(lr){{2-3}}\cmidrule(lr){{4-5}}
Công đoạn & MDE (\%) & Trung vị (ms) & MDE (\%) & Trung vị (ms) \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


# ---------------------------------------------------------------- E1: đáp ứng liều (4 cài đặt x 3 hình học)
def t_dose():
    t = Tab('tab_dose')
    f = 'e1/E1_P1cpu2_20261101/summary.json'
    s = j(f)
    aa = j('e5/AA_P1cpu2_20261101/summary.json')['profiles']['P1_cpu2']['stages']
    mde = max(aa['nms_torch_pure']['mde_ratio_pct'], aa['nms_tv_nms']['mde_ratio_pct'])
    lines = []
    for be in BE:
        for g in GEOM:
            k = f'P1_cpu2|{be}|{g}'
            v = s['dose_1e2_to_1e4'][k]
            sel = f'{f}:dose_1e2_to_1e4.{k}'
            ok = v['ci95'][0] > 1 + mde / 100
            lines.append(f'{BE_VI[be]} & {GEOM_VI[g]} & ' + t.n(v['median_ms_N1e2'], sel + '.median_ms_N1e2', sig=3) + ' & '
                         + t.n(v['median_ms_N1e4'], sel + '.median_ms_N1e4', sig=3) + ' & ' + t.n(v['ratio'], sel + '.ratio', sig=3)
                         + ' & ' + t.ci(v['ci95'][0], v['ci95'][1], sel + '.ci95', sig=3) + ' & ' + ('có' if ok else 'không') + ' \\\\')
    m = t.n(mde, 'e5/AA_P1cpu2_20261101/summary.json:max(stages.nms_torch_pure.mde_ratio_pct,stages.nms_tv_nms.mde_ratio_pct)', d=2)
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Độ trễ NMS trung vị tại $\Ntau=10^2$ và $10^4$ (head 10\,000 anchor, 80 lớp, không giới hạn) và tỷ số của chúng, đủ bốn cách cài đặt $\times$ ba hình học. Khoảng tin cậy 95\%: bootstrap theo các lần lặp (30 lần mỗi ô). Cột cuối: cận dưới vượt $1+\mathrm{{MDE}}$, với MDE là giá trị lớn hơn trong hai MDE A/A của công đoạn NMS ({m}\%).}}
\label{{tab:dose}}
\begin{{tabular}}{{@{{}}llccccc@{{}}}}
\toprule
Cách cài đặt & Hình học & $t_{{\mathrm{{NMS}}}}(10^2)$ (ms) & $t_{{\mathrm{{NMS}}}}(10^4)$ (ms) & Tỷ số & KTC 95\% & Vượt MDE \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n'
    return write(t, body)


def t_slopes():
    t = Tab('tab_slopes')
    f = 'e1/E1_P1cpu2_20261101/summary.json'
    s = j(f)['loglog_slopes']
    lines = []
    for be in BE:
        cells = []
        for g in ('disjoint', 'dense_cluster', 'mixed'):
            k = f'P1_cpu2|10000|{be}|{g}|80|None'
            cells.append(t.n(s[k]['slope'], f'{f}:loglog_slopes.{k}.slope', d=2) + ' [' + t.ci(s[k]['ci95'][0], s[k]['ci95'][1], f'{f}:loglog_slopes.{k}.ci95', d=2, sep='; ') + ']')
        lines.append(f'{BE_VI[be]} & ' + ' & '.join(cells) + ' \\\\')
    body = r"""\begin{table}[t]
\centering\small
\caption{Độ dốc log--log của độ trễ NMS theo $\Ntau$ trên các mức đã đo $\ge 100$ (head 10\,000 anchor, 80 lớp, không giới hạn); khoảng tin cậy bootstrap 95\% trong ngoặc. Chỉ mang tính mô tả.}
\label{tab:slopes}
\begin{tabular}{@{}lccc@{}}
\toprule
Cách cài đặt & Rời nhau & Cụm dày đặc & Hỗn hợp \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


def t_cap():
    t = Tab('tab_cap')
    f = 'e1/E1_P1cpu2_20261101/summary.json'
    s = j(f)
    lines = []
    for g in GEOM:
        for i, be in enumerate(BE):
            k0, k3 = f'P1_cpu2|10000|{be}|{g}|80|None|10000', f'P1_cpu2|10000|{be}|{g}|80|300|10000'
            kc = f'P1_cpu2|10000|{be}|{g}|80|10000'
            c = s['contrasts']['cap300_over_capNone'][kc]
            sel = f'{f}:1/contrasts.cap300_over_capNone.{kc}'
            lines.append((GEOM_VI[g].capitalize() if i == 0 else '') + f' & {BE_VI[be]} & '
                         + t.n(s['curves'][k0]['median_ms'], f'{f}:curves.{k0}.median_ms', sig=3) + ' & '
                         + t.n(s['curves'][k3]['median_ms'], f'{f}:curves.{k3}.median_ms', sig=3) + ' & '
                         + t.n(1 / c['ratio'], sel + '.ratio', sig=3) + ' (' + t.ci(1 / c['ci95'][1], 1 / c['ci95'][0], sel + '.ci95(đảo)', sig=3) + ') \\\\')
    body = r"""\begin{table}[t]
\centering\small
\caption{Độ trễ NMS trung vị (ms) tại $\Ntau=10^4$ (head 10\,000 anchor, 80 lớp) khi không giới hạn và khi giới hạn top-300, và hệ số giảm (không giới hạn chia giới hạn; KTC 95\% bootstrap theo lần lặp).}
\label{tab:cap}
\begin{tabular}{@{}llccc@{}}
\toprule
Hình học & Cách cài đặt & Không giới hạn & Giới hạn 300 & Hệ số giảm \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


# ---------------------------------------------------------------- E9: ngưỡng N*
def t_nstar():
    t = Tab('tab_nstar')
    fa, fs, fm = 'e9/E9_P1cpu2_20261102/summary_part_a.json', 'e9/E9_P1cpu2_20261102/summary_part_a_sens_aa640b.json', 'amdahl/amdahl_vs_e9_posthoc.json'
    a, s, m = j(fa), j(fs), j(fm)
    lines = []
    for be in BE:
        for i, g in enumerate(GEOM):
            k3, k6 = f'320|{be}|{g}|capNone', f'640|{be}|{g}|capNone'
            row = [BE_VI[be] if i == 0 else '', GEOM_VI[g],
                   t.n(a['n_star'][k3], f'{fa}:n_star.{k3}'), t.n(m['n_star'][k3]['predicted'], f'{fm}:n_star.{k3}.predicted'),
                   t.n(m['n_star_unflagged_blocks'][k3]['measured'], f'{fm}:n_star_unflagged_blocks.{k3}.measured'),
                   t.n(a['n_star'][k6], f'{fa}:n_star.{k6}'), t.n(s['n_star'][k6], f'{fs}:n_star.{k6}'),
                   t.n(m['n_star'][k6]['predicted'], f'{fm}:n_star.{k6}.predicted'),
                   t.n(m['n_star_unflagged_blocks'][k6]['measured'], f'{fm}:n_star_unflagged_blocks.{k6}.measured')]
            lines.append(' & '.join(row) + ' \\\\')
    m3 = t.n(a['mde_total_pct']['320'], f'{fa}:mde_total_pct.320', d=2)
    m6 = t.n(a['mde_total_pct']['640'], f'{fa}:mde_total_pct.640', d=2)
    m6b = t.n(s['mde_total_pct']['640'], f'{fs}:mde_total_pct.640', d=2)
    nf3 = t.n(m['n_star_unflagged_blocks']['320|torch_pure|disjoint|capNone']['n_images'], f'{fm}:n_star_unflagged_blocks.320|torch_pure|disjoint|capNone.n_images')
    nf6 = t.n(m['n_star_unflagged_blocks']['640|torch_pure|disjoint|capNone']['n_images'], f'{fm}:n_star_unflagged_blocks.640|torch_pure|disjoint|capNone.n_images')
    fb = t.n(a['drift']['flagged'], f'{fa}:drift.flagged') + '/' + t.n(a['drift']['points'], f'{fa}:drift.points')
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Ngưỡng $N^{{*}}$: số ứng viên nhỏ nhất trong lưới làm toàn trình tăng vượt MDE (cận dưới KTC 95\% bootstrap theo ảnh $>1+\mathrm{{MDE}}$), tiêm toàn pipeline, 20 ảnh, không giới hạn top-$k$; ``$>$'' nghĩa là không mức nào trong lưới vượt. ``Đo'' là cách tính đăng ký trước (kết quả chính), dùng MDE đăng ký trước ({m3}\% ở 320 px; {m6}\% ở 640 px, từ lần A/A 640 px đầu); cột ``MDE {m6b}\%'' dùng MDE của lần A/A 640 px đo lại (ngoài đăng ký). $^{{\dagger}}$Post hoc: $N^{{*}}$ dự đoán bằng mô hình Amdahl từ đường cong tiêm (head 2100 anchor ở 320 px, 8400 anchor ở 640 px; không dùng head 10\,000) với $t_{{\mathrm{{total}}}}$ sạch cùng phiên và MDE đăng ký. $^{{\S}}$Độ nhạy định trước: bỏ các khối có điểm tham chiếu bị cờ drift ({fb} điểm bị cờ; còn {nf3} ảnh ở 320 px và {nf6} ảnh ở 640 px), MDE đăng ký.}}
\label{{tab:nstar}}
\begin{{tabular}}{{@{{}}llccccccc@{{}}}}
\toprule
 & & \multicolumn{{3}}{{c}}{{320 px (lưới 100, 300, 1000, 2100)}} & \multicolumn{{4}}{{c}}{{640 px (lưới 300, 1000, 3000, 8400)}} \\
\cmidrule(lr){{3-5}}\cmidrule(lr){{6-9}}
Cách cài đặt & Hình học & Đo & Dự đoán$^{{\dagger}}$ & Bỏ khối cờ$^{{\S}}$ & Đo & MDE {m6b}\% & Dự đoán$^{{\dagger}}$ & Bỏ khối cờ$^{{\S}}$ \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n'
    return write(t, body)


def t_amdahl():
    """Bảng 8 theo khung bài: mô hình Amdahl trên phép tiêm (post hoc) và trên tấn công thật (đăng ký trước, đủ 6 ô)."""
    t = Tab('tab_amdahl')
    fm, fe = 'amdahl/amdahl_vs_e9_posthoc.json', 'e10/E10_P1cpu2_20261102/summary.json'
    m, e = j(fm), j(fe)
    lines = []
    for cv, nmax in ((320, 2100), (640, 8400)):
        lines.append(f'\\multicolumn{{6}}{{@{{}}l}}{{\\textit{{A. Tiêm toàn pipeline, \\textbf{{post hoc}}; {cv} px, hộp rời nhau, không giới hạn, $\\Ntau={nmax}$}}}} \\\\')
        for be in BE:
            k = f'{cv}|{be}|disjoint|capNone'
            r = [x for x in m['cells'][k]['rows'] if x['n'] == nmax][0]
            i = m['cells'][k]['rows'].index(r)
            sel = f'{fm}:cells.{k}.rows[{i}]'
            lines.append(f'{BE_VI[be]} & ' + t.n(r['r_pred'], sel + '.r_pred', sig=3) + ' & ' + t.n(r['r_meas'], sel + '.r_meas', sig=3) + ' & '
                         + t.n(r['abs_log_err'], sel + '.abs_log_err', d=3) + ' & ' + t.n(m['n_star'][k]['predicted'], f'{fm}:n_star.{k}.predicted') + ' / '
                         + t.n(m['n_star'][k]['measured'], f'{fm}:n_star.{k}.measured') + ' & -- \\\\')
    lines.append('\\midrule')
    lines.append('\\multicolumn{6}{@{}l}{\\textit{B. Biến thể tấn công toàn ảnh (YOLOv5s, 640 px), mô hình và quy tắc đăng ký trước}} \\\\')
    for mth, mv in (('overload', 'Overload'), ('phantom_sponges', 'Phantom Sponges')):
        for be in ('tv_nms', 'tv_batched', 'ultra_native'):
            k = f'{mth}|{be}'
            am = e['amdahl'][k]
            sel = f'{fe}:amdahl.{k}'
            lines.append(f'{mv}, {BE_VI[be]} & ' + t.n(am['r_pred_mean'], sel + '.r_pred_mean', d=3) + ' & ' + t.n(am['r_meas_mean'], sel + '.r_meas_mean', d=3) + ' & '
                         + t.n(am['median_abs_log_err'], sel + '.median_abs_log_err', d=3) + ' (' + t.ci(*am['ci95'], sel + '.ci95', d=3) + ') & -- & '
                         + ('đạt' if am['passes_prereg_rule'] else '\\textbf{không đạt}') + ' \\\\')
    pa = j('e9/E9_P1cpu2_20261102/summary_part_a.json')['n_star']
    diff = [k for k, v in m['n_star'].items() if v['measured'] != pa[k]]
    nd = t.n(len(diff), f'{fm}:n_star[*].measured != e9/E9_P1cpu2_20261102/summary_part_a.json:n_star[*] (đếm)') + '/' + t.n(len(m['n_star']), f'{fm}:n_star(len)')
    ku = '320|ultra_native|disjoint|capNone'
    du = t.n(m['n_star'][ku]['measured'], f'{fm}:n_star.{ku}.measured') + ' so với ' + t.n(pa[ku], f'e9/E9_P1cpu2_20261102/summary_part_a.json:n_star.{ku}')
    sm = m['summary']
    e1 = t.n(sm['median_abs_log_err'], f'{fm}:summary.median_abs_log_err', d=3)
    e9 = t.n(sm['p90_abs_log_err'], f'{fm}:summary.p90_abs_log_err', d=3)
    nc = t.n(sm['n_cells'], f'{fm}:summary.n_cells')
    ag = t.n(sm['n_star_exact_agreement'], f'{fm}:summary.n_star_exact_agreement')
    npass = sum(v['passes_prereg_rule'] for v in e['amdahl'].values())
    np_ = t.n(npass, f'{fe}:amdahl[*].passes_prereg_rule (đếm)') + '/' + t.n(len(e['amdahl']), f'{fe}:amdahl(len)')
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Mô hình kiểu Amdahl $R_{{\mathrm{{pred}}}} = 1+\Delta t_{{\mathrm{{NMS}}}}/t_{{\mathrm{{total}}}}$ so với tỷ số toàn trình đo $R_{{\mathrm{{meas}}}}$. Sai số là $|\ln(R_{{\mathrm{{meas}}}}/R_{{\mathrm{{pred}}}})|$. \textbf{{Phần A là post hoc}}: mô hình được viết sau khi đã xem phép tiêm toàn pipeline; trên cả {nc} ô (bốn cài đặt, ba hình học, hai giới hạn, hai độ phân giải) sai số trung vị {e1}, phân vị 90 là {e9}, và $N^{{*}}$ dự đoán trùng $N^{{*}}$ đo ở {ag} ô. $N^{{*}}$ đo ở phần A là \textbf{{phân tích độ nhạy}} (cách gộp không đăng ký): nó dùng trung bình log-tỷ số so với trung vị ba ô $\Ntau=0$ (cùng cách tính với dự đoán) nên khác Bảng~\ref{{tab:nstar}} (trung bình tỷ số) ở {nd} ô, ví dụ Ultralytics, rời nhau, 320 px: {du}. Phần B tính riêng cho YOLOv5s: $t_{{\mathrm{{total}}}}$ là toàn trình ảnh sạch của chính phiên YOLOv5s, đường cong NMS là đường cong tiêm tổng hợp (chỉ phụ thuộc tập ứng viên, không phụ thuộc mô hình); đặc tả và quy tắc (cận trên KTC 95\% của sai số trung vị $<0{{,}}05$) đăng ký trước khi đo; đạt {np_} ô, ba ô không đạt được báo đầy đủ.}}
\label{{tab:amdahl}}
\begin{{tabular}}{{@{{}}lccccc@{{}}}}
\toprule
 & $R_{{\mathrm{{pred}}}}$ & $R_{{\mathrm{{meas}}}}$ & Sai số (KTC 95\%) & $N^{{*}}$ dự đoán / đo & Quy tắc \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n'
    return write(t, body)


# ---------------------------------------------------------------- E10: tấn công toàn ảnh
def t_attacks():
    t = Tab('tab_attacks')
    f = 'e10/E10_P1cpu2_20261102/summary.json'
    s = j(f)
    fd = 'e10/E10_P1cpu2_20261102/stage_medians_posthoc.json'
    sd = j(fd)
    lines = []
    for m, mv in (('overload', 'Overload'), ('phantom_sponges', 'Phantom Sponges')):
        nr, nm = s['n_ratio'][f'{m}|tau0.25'], s['n_median'][f'{m}|tau0.25']
        for i, be in enumerate(('tv_nms', 'tv_batched', 'ultra_native')):
            k = f'{m}|{be}'
            tr = s['total_ratio'][k]
            head = (f'{mv} & ' + t.n(nm['clean'], f'{f}:n_median.{m}|tau0.25.clean', d=1) + ' $\\to$ ' + t.n(nm['patched'], f'{f}:n_median.{m}|tau0.25.patched', d=1)
                    + ' & ' + t.n(nr['mean'], f'{f}:n_ratio.{m}|tau0.25.mean', sig=3) + ' (' + t.ci(*nr['ci95'], f'{f}:n_ratio.{m}|tau0.25.ci95', sig=3) + ')') if i == 0 else ' & & '
            # ngưỡng riêng của YOLOv5s (post hoc): Δt* = MDE trong phiên × t_total sạch cùng phiên; ΔNMS = trung vị NMS tấn công − sạch
            tc = sd['total_ms'][f'clean|{be}']['median']
            dstar = s['in_session_mde_pct'][be] / 100 * tc
            dn = sd['nms_ms'][f'{m}|{be}']['median'] - sd['nms_ms'][f'clean|{be}']['median']
            lines.append(head + f' & {BE_VI[be]} & ' + t.n(tr['mean'], f'{f}:total_ratio.{k}.mean', d=3) + ' (' + t.ci(*tr['ci95'], f'{f}:total_ratio.{k}.ci95', d=3) + ') & '
                         + t.n(s['in_session_mde_pct'][be], f'{f}:in_session_mde_pct.{be}', d=2) + ' & ' + ('có' if tr['exceeds_in_session_mde'] else 'không') + ' & '
                         + t.n(dstar, f'{f}:in_session_mde_pct.{be}/100 * {fd}:total_ms.clean|{be}.median', sig=2) + ' & '
                         + t.n(dn, f'{fd}:nms_ms.{m}|{be}.median - nms_ms.clean|{be}.median', sig=2) + ' \\\\')
    ni = t.n(s['n_images'], f'{f}:n_images')
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Biến thể thích nghi của hai tấn công toàn ảnh, theo Overload và Phantom Sponges (YOLOv5s, 640 px, nhiễu loạn cộng toàn ảnh, hộp trắng; {ni} ảnh $\times$ 5 seed), đo trên một lõi CPU ghim, float32. $\Ntau$ trung vị ảnh sạch $\to$ có nhiễu loạn và tỷ số $\Ntau$ trung bình ($\tau=0{{,}}25$); tỷ số toàn trình (KTC 95\% bootstrap hai tầng); MDE toàn trình trong phiên (hai nhánh sạch); ``vượt MDE'' khi cận dưới KTC $>1+\mathrm{{MDE}}$. Mọi đại lượng lấy từ phiên YOLOv5s này; không so với ngưỡng $N^{{*}}$ của YOLOv8n. $^{{\dagger}}$\textbf{{Post hoc}}, mô tả: ngưỡng riêng của YOLOv5s $\Delta t^{{*}}=\mathrm{{MDE}}\times t_{{\mathrm{{total}}}}$ (trung vị toàn trình ảnh sạch cùng phiên) và mức tăng trung vị của công đoạn NMS. Mô hình Amdahl cho các ô này ở Bảng~\ref{{tab:amdahl}}.}}
\label{{tab:attacks}}
\begin{{tabular}}{{@{{}}lcclccccc@{{}}}}
\toprule
Biến thể & $\Ntau$ sạch $\to$ tấn công & Tỷ số $\Ntau$ (KTC 95\%) & Cách cài đặt & Tỷ số toàn trình (KTC 95\%) & MDE (\%) & Vượt MDE & $\Delta t^{{*}}$ (ms)$^{{\dagger}}$ & $\Delta t_{{\mathrm{{NMS}}}}$ (ms)$^{{\dagger}}$ \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n'
    return write(t, body)


# ---------------------------------------------------------------- E7: thiết lập và fitness huấn luyện
E7 = 'e7_gpu/final/runs/e7'
CONDS = ['C1_320_s64_t01', 'C2_640_s128_t01', 'C3_320_s64_t25', 'C4_640_s64_t01', 'B1_ga_center', 'B2_ga_random_location', 'B3_random_search', 'B4_gradient_tanh']
METHOD_VI = {('sg_ga', 'saliency'): 'GA, đặt theo độ nổi bật', ('ga_center', 'center'): 'GA, đặt ở tâm', ('ga_random_location', 'random'): 'GA, đặt ngẫu nhiên',
             ('random_search', 'saliency'): 'tìm kiếm ngẫu nhiên, độ nổi bật', ('gradient_tanh', 'saliency'): 'leo gradient (tanh), độ nổi bật'}


def ckpts(c, q, seed='*'):
    return sorted((RES / E7 / c).glob(f'seed{seed}/checkpoint_q{q}*.json'))


def spec(c):
    return json.loads(ckpts(c, 62500, 0)[0].read_text(encoding='utf-8'))['specification']


def t_spec():
    t = Tab('tab_spec')
    lines = []
    seeds = set()
    for c in CONDS:
        sp = spec(c)
        for p in ckpts(c, 62500):
            seeds.add(int(p.parent.name[4:]))
        src = f'{E7}/{c}/seed0/{ckpts(c, 62500, 0)[0].name}:specification'
        meth = METHOD_VI[(sp['method'], sp['location'])]  # KeyError nếu đặc tả lạ: dừng thay vì đoán
        lines.append(f'{c.split("_")[0]} & {meth} & ' + t.n(sp['canvas'], src + '.canvas') + ' & ' + t.n(sp['size'], src + '.size') + ' & '
                     + t.n(sp['threshold'], src + '.threshold', d=2) + ' & ' + t.n(sp['n_train'], src + '.n_train') + ' \\\\')
    sd = f'{min(seeds)}--{max(seeds)}'
    body = rf"""\begin{{table}}[t]
\centering\small
\caption{{Thiết lập của các điều kiện trong nghiên cứu tình huống, đọc từ đặc tả lưu trong checkpoint của lần sinh patch. $\tau_{{\mathrm{{obj}}}}$ là ngưỡng trong hàm mục tiêu tối ưu. Mọi điều kiện dùng EOT phần mềm, seed {sd} và ba mức ngân sách.}}
\label{{tab:spec}}
\begin{{tabular}}{{@{{}}llcccc@{{}}}}
\toprule
Điều kiện & Phương pháp & Đầu vào (px) & Patch (px) & $\tau_{{\mathrm{{obj}}}}$ & Ảnh tối ưu \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


def t_train():
    t = Tab('tab_train')
    lab = {'C1_320_s64_t01': 'C1 (320 px, $\\tau_{\\mathrm{obj}}$ 0,01)', 'C3_320_s64_t25': 'C3 (320 px, $\\tau_{\\mathrm{obj}}$ 0,25)',
           'C2_640_s128_t01': 'C2 (640 px, patch 128 px)', 'C4_640_s64_t01': 'C4 (640 px, patch 64 px)', 'B1_ga_center': 'B1 (đặt ở tâm)',
           'B2_ga_random_location': 'B2 (đặt ngẫu nhiên)', 'B3_random_search': 'B3 (tìm kiếm ngẫu nhiên)', 'B4_gradient_tanh': 'B4 (gradient, tanh)'}
    lines = []
    for c in ['C1_320_s64_t01', 'C3_320_s64_t25', 'C2_640_s128_t01', 'C4_640_s64_t01', 'B1_ga_center', 'B2_ga_random_location', 'B3_random_search', 'B4_gradient_tanh']:
        cells = []
        for q in (10000, 25000, 62500):
            v = [json.loads(p.read_text(encoding='utf-8'))['best_training_fitness'] for p in ckpts(c, q)]
            src = f'{E7}/{c}/seed*/checkpoint_q{q}*.json:best_training_fitness(n={len(v)})'
            cells.append(t.n(statistics.mean(v), src + '.mean', d=1) + ' (' + t.n(statistics.stdev(v), src + '.sd', d=1) + ')')
        lines.append(lab[c] + ' & ' + ' & '.join(cells) + ' \\\\')
    body = r"""\begin{table}[t]
\centering\small
\caption{Fitness huấn luyện (trung bình trên mười seed, độ lệch chuẩn trong ngoặc) ở ba mức ngân sách (lượt lan truyền thuận ứng viên--ảnh), trường \texttt{best\_training\_fitness} của checkpoint. Với B4, phương pháp gradient cập nhật một patch duy nhất nên giá trị là fitness ở bước cuối của mốc ngân sách.}
\label{tab:train}
\begin{tabular}{@{}lccc@{}}
\toprule
Điều kiện & 10\,000 & 25\,000 & 62\,500 \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


# ---------------------------------------------------------------- E9 phần B
def t_nk():
    t = Tab('tab_nk')
    f = 'e9/E9_P1cpu2_20261102/summary_part_b.json'
    s = j(f)
    lines = []
    for key, lab in (('test2_e6a1_640_confirmatory', '640 px, đánh giá xác nhận'), ('test1_e6_320_posthoc', '320 px, \\textbf{post hoc}')):
        v0 = s[key]['torch_pure']
        lines.append(f'\\multicolumn{{4}}{{@{{}}l}}{{\\textit{{{lab} (' + t.n(v0['n_units'], f'{f}:{key}.torch_pure.n_units') + ' đơn vị, ' + t.n(v0['n_images'], f'{f}:{key}.torch_pure.n_images') + ' ảnh)}} \\\\')
        for be in BE:
            v = s[key][be]
            sel = f'{f}:{key}.{be}'
            lines.append(f'{BE_VI[be]} & ' + t.n(v['median_abs_log_err_M_N'], sel + '.median_abs_log_err_M_N', d=2) + ' & ' + t.n(v['median_abs_log_err_M_NK'], sel + '.median_abs_log_err_M_NK', d=2)
                         + ' & ' + t.n(v['delta'], sel + '.delta', d=2) + ' (' + t.ci(v['delta_ci95'][0], v['delta_ci95'][1], sel + '.delta_ci95', d=2, sep=' đến ') + ') \\\\')
    body = r"""\begin{table}[t]
\centering\small
\caption{Trung vị sai số $|\ln(t_{\mathrm{meas}}/t_{\mathrm{pred}})|$ của $M_N$ và $M_{NK}$ trên các tập ứng viên thật, và chênh lệch $\Delta$ ($M_N$ trừ $M_{NK}$) với KTC 95\% bootstrap hai tầng (ảnh, đơn vị trong ảnh). $\Delta>0$ nghĩa là thêm $K$ làm giảm sai số. Phép xác nhận theo đăng ký dùng lần đo patch 640 px đầu (nhiễu cao).}
\label{tab:nk}
\begin{tabular}{@{}lccc@{}}
\toprule
Cách cài đặt & $M_N$ & $M_{NK}$ & $\Delta$ (KTC 95\%) \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


# ---------------------------------------------------------------- E11: patch, cài đặt, ngưỡng
# ---------------------------------------------------------------- bảng patch từ E6 (N và NMS vi mô hợp lệ) + toàn trình DỰ ĐOÁN
# Lỗi chèn patch (DEVIATIONS 03/11) chỉ ảnh hưởng bộ đếm toàn trình của E6 (studies/e6_remeasure/run.py:198-205);
# bước chèn ở :168 nằm ngoài bộ đếm lọc điểm/NMS (:190-191). E11 lần 1 bị loại vì drift. Nếu sau này có run E11b hợp lệ,
# ghi tên vào E11_ACCEPTED để thay cột dự đoán bằng cột đo (chưa cài đặt nhánh đó: cần duyệt).
E11_ACCEPTED = None
E6_SRC = {'C1': 'e6/E6_P1cpu2_20261102/summary.json', 'C3': 'e6/E6_P1cpu2_20261102/summary.json',
          'B1': 'e6/E6_pooled_baselines_100img/summary.json', 'B2': 'e6/E6_pooled_baselines_100img/summary.json',
          'B3': 'e6/E6_pooled_baselines_100img/summary.json', 'B4': 'e6/E6_pooled_baselines_100img/summary.json',
          'C2': 'e6/E6A1_P1cpu2_20261102b/summary.json', 'C4': 'e6/E6A1_P1cpu2_20261102b/summary.json'}
CANV = dict(C1=320, C3=320, B1=320, B2=320, B3=320, B4=320, C2=640, C4=640)
TC = 'amdahl/threshold_check_posthoc.json'
MDE_SRC = {320: 'e5/AA_P1cpu2_20261101/summary.json', 640: 'e5/AA640_P1cpu2_20261102b/summary.json'}
ARM_VI = [('C1', '320 px, patch 64 px, $\\tau_{\\mathrm{obj}}$ 0,01'), ('C3', '320 px, patch 64 px, $\\tau_{\\mathrm{obj}}$ 0,25'), ('B3', 'Tìm kiếm ngẫu nhiên (320 px)'),
          ('B1', 'GA, đặt ở tâm (320 px)'), ('B2', 'GA, đặt ngẫu nhiên (320 px)'), ('B4', 'Leo gradient (320 px)'),
          ('C2', '640 px, patch 128 px, $\\tau_{\\mathrm{obj}}$ 0,01'), ('C4', '640 px, patch 64 px, $\\tau_{\\mathrm{obj}}$ 0,01')]


def mde_total(cv):
    return j(MDE_SRC[cv])['profiles']['P1_cpu2']['stages']['total']['mde_ratio_pct']


def t_patches():
    t = Tab('tab_patches')
    tc = j(TC)
    lines = []
    for arm, lab in ARM_VI:
        f = E6_SRC[arm]
        a = j(f)['arms'][arm]
        sel = f'{f}:arms.{arm}'
        cv = CANV[arm]
        mde = mde_total(cv)
        cells = [t.n(a['N_tau0.01']['ratio_mean'], sel + '.N_tau0.01.ratio_mean', d=2) + ' (' + t.ci(*a['N_tau0.01']['ratio_ci95'], sel + '.N_tau0.01.ratio_ci95', d=2) + ')',
                 t.n(a['N_tau0.25']['ratio_mean'], sel + '.N_tau0.25.ratio_mean', d=2) + ' (' + t.ci(*a['N_tau0.25']['ratio_ci95'], sel + '.N_tau0.25.ratio_ci95', d=2) + ')',
                 t.n(a['nms_tau0.01_tv_nms']['ratio_mean'], sel + '.nms_tau0.01_tv_nms.ratio_mean', d=3) + ' (' + t.ci(*a['nms_tau0.01_tv_nms']['ratio_ci95'], sel + '.nms_tau0.01_tv_nms.ratio_ci95', d=3) + ')']
        for be in ('tv_nms', 'torch_pure'):
            v = tc['arms'][f'{cv}|{arm}|{be}']
            s2 = f'{TC}:arms.{cv}|{arm}|{be}'
            cells.append(t.n(v['r_pred'], s2 + '.r_pred', d=4) + (' (vượt)' if v['r_pred'] > 1 + mde / 100 else ''))
        cells.append(t.n(1 + mde / 100, f'1 + {MDE_SRC[cv]}:profiles.P1_cpu2.stages.total.mde_ratio_pct/100', d=4))
        lines.append(f'{lab} & ' + ' & '.join(cells) + ' \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{Tác động của các patch đã đóng băng (SHA-256) so với ảnh sạch cùng canvas, 100 ảnh $\times$ 5 seed (0--4, chọn trước). Tỷ số $\Ntau$ và tỷ số công đoạn NMS (torchvision, $\tau=0{,}01$) là \textbf{số đo} của lần đo lại patch trên profile ghim lõi; KTC 95\% bootstrap hai tầng ảnh $\times$ seed. Hai cột $R_{\mathrm{pred}}$ là \textbf{dự đoán, không phải số đo}: $R_{\mathrm{pred}} = 1 + \Delta t_{\mathrm{NMS}}/t_{\mathrm{total}}$ (mô hình ngân sách kiểu Amdahl, post hoc), với $\Delta t_{\mathrm{NMS}}$ đo vi mô theo từng cặp ảnh $\times$ seed và $t_{\mathrm{total}}$ là toàn trình của ảnh sạch cùng phiên. Cột toàn trình đo được không được báo: phép đo toàn trình của lần đo này tính bước chèn patch cho nhánh có patch mà không cho ảnh sạch, và lần đo lại sau khi sửa lỗi bị loại vì drift (Bảng~\ref{tab:dev}). ``(vượt)'': $R_{\mathrm{pred}} > 1+\mathrm{MDE}$, với MDE toàn trình của A/A cùng độ phân giải. Hàng 640 px so với ảnh sạch 640 px (lần đo bổ sung thứ hai); baseline B1--B4 gộp ảnh 1--50 và 51--100 từ hai phiên, mỗi ảnh so với ảnh sạch của chính phiên đó.}
\label{tab:patches}
\begin{tabular}{@{}lcccccc@{}}
\toprule
Điều kiện & Tỷ số $\Ntau$ ($\tau$=0,01) & Tỷ số $\Ntau$ ($\tau$=0,25) & Tỷ số NMS (đo) & $R_{\mathrm{pred}}$, \texttt{nms} & $R_{\mathrm{pred}}$, PyTorch thuần & $1+\mathrm{MDE}$ \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n'
    return write(t, body)


def t_impl():
    t = Tab('tab_impl')
    lines = []
    for arm in ('C1', 'C3', 'B1', 'B2', 'B3', 'B4', 'C2', 'C4'):
        f = E6_SRC[arm]
        a = j(f)['arms'][arm]
        cells = [t.n(a[f'nms_tau0.01_{be}']['ratio_mean'], f'{f}:arms.{arm}.nms_tau0.01_{be}.ratio_mean', d=3) + ' (' + t.ci(*a[f'nms_tau0.01_{be}']['ratio_ci95'], f'{f}:arms.{arm}.nms_tau0.01_{be}.ratio_ci95', d=3) + ')' for be in BE]
        lines.append(f'{arm} ({CANV[arm]} px) & ' + ' & '.join(cells) + ' \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{Tỷ số thời gian công đoạn NMS (đo vi mô, $\tau=0{,}01$) của ảnh có patch so với ảnh sạch cùng canvas, theo cách cài đặt; tỷ số trung bình, KTC 95\% bootstrap hai tầng. Cùng lần đo với bảng patch của bài chính; bước chèn patch nằm ngoài bộ đếm của công đoạn này.}
\label{tab:impl}
\begin{tabular}{@{}lcccc@{}}
\toprule
Điều kiện & PyTorch thuần & \texttt{nms} & Theo lô & Ultralytics \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n'
    return write(t, body)


def t_threshold():
    t = Tab('tab_threshold')
    tc = j(TC)
    lines = []
    for cv in ('320', '640'):
        lines.append(f'$t_{{\\mathrm{{total}}}}$ ảnh sạch, {cv} px (ms) & ' + ' & '.join(t.n(tc['threshold_ms'][be][cv]['t_total_clean_ms'], f'{TC}:threshold_ms.{be}.{cv}.t_total_clean_ms', sig=3) for be in ('tv_nms', 'torch_pure')) + ' \\\\')
        lines.append(f'MDE toàn trình A/A, {cv} px (\\%) & ' + ' & '.join(t.n(tc['mde_total_pct'][cv], f'{TC}:mde_total_pct.{cv}', d=2) for _ in ('tv_nms', 'torch_pure')) + ' \\\\')
        lines.append(f'Ngưỡng $\\Delta t^{{*}}=\\mathrm{{MDE}}\\times t_{{\\mathrm{{total}}}}$, {cv} px (ms) & ' + ' & '.join(t.n(tc['threshold_ms'][be][cv]['threshold_ms'], f'{TC}:threshold_ms.{be}.{cv}.threshold_ms', sig=2) for be in ('tv_nms', 'torch_pure')) + ' \\\\')
    lines.append('\\midrule')
    b = {be: tc['arms'][f'320|B4|{be}'] for be in ('tv_nms', 'torch_pure')}
    sb = lambda be, k: f'{TC}:arms.320|B4|{be}.{k}'  # noqa: E731
    lines.append('$\\Delta t_{\\mathrm{NMS}}$ của baseline gradient, đo (ms) & ' + ' & '.join(t.n(b[be]['delta_nms_ms_mean'], sb(be, 'delta_nms_ms_mean'), sig=2) + ' (' + t.ci(*b[be]['delta_nms_ms_ci95'], sb(be, 'delta_nms_ms_ci95'), sig=2) + ')' for be in b) + ' \\\\')
    lines.append('Vượt $\\Delta t^{*}$ (320 px) & ' + ' & '.join('có' if b[be]['delta_nms_ms_mean'] > tc['threshold_ms'][be]['320']['threshold_ms'] else 'không' for be in b) + ' \\\\')
    lines.append('$R_{\\mathrm{pred}} = 1+\\Delta t_{\\mathrm{NMS}}/t_{\\mathrm{total}}$, dự đoán & ' + ' & '.join(t.n(b[be]['r_pred'], sb(be, 'r_pred'), d=4) + ' (' + t.ci(*b[be]['r_pred_ci95'], sb(be, 'r_pred_ci95'), d=4) + ')' for be in b) + ' \\\\')
    body = r"""\begin{table}[t]
\centering\small
\caption{\textbf{Post hoc.} Ngưỡng $\Delta t^{*}$ để tỷ số toàn trình vượt MDE, và dự đoán cho baseline gradient (B4, 320 px, 100 ảnh $\times$ 5 seed). $t_{\mathrm{total}}$ là toàn trình ảnh sạch của chính phiên đo patch (tensor đã chuẩn bị, không có bước chèn); MDE từ A/A riêng vì phiên này không có hai nhánh sạch. $\Delta t_{\mathrm{NMS}}$ là số đo vi mô; $R_{\mathrm{pred}}$ là dự đoán, không phải số đo.}
\label{tab:threshold}
\begin{tabular}{@{}lcc@{}}
\toprule
 & torchvision \texttt{nms} & PyTorch thuần \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


# ---------------------------------------------------------------- các YOLO mới hơn: số ứng viên trước NMS (X2, lịch sử, post hoc)
def t_x2():
    t = Tab('tab_x2')
    f = 'x2_counts/summary_posthoc.json'
    s = j(f)['detectors']
    name = dict(yolov8n='YOLOv8n', yolov8s='YOLOv8s', yolo11n='YOLO11n', yolo11s='YOLO11s', yolov12n='YOLOv12n')
    lines = []
    for d, v in s.items():
        sel = f'{f}:detectors.{d}'
        lines.append(f'{name[d]} & ' + t.n(v['images'], sel + '.images') + ' & ' + t.n(v['clean_median'], sel + '.clean_median', d=1) + ' & '
                     + t.n(v['patched_median'], sel + '.patched_median', d=1) + ' & ' + t.n(v['ratio_mean'], sel + '.ratio_mean', d=3)
                     + ' (' + t.ci(*v['ratio_ci95'], sel + '.ratio_ci95', d=3) + ') \\\\')
    body = r"""\begin{table}[t]
\centering\small
\caption{\textbf{Post hoc, dữ liệu lịch sử}: số ứng viên trước NMS ($\tau=0{,}01$, 320 px) của năm bộ phát hiện YOLO khi chèn năm patch SG-GA cũ (seed 0--4, tối ưu trên YOLOv8n ở một lần chạy trước, ngân sách 2500 lượt). Chỉ đếm ứng viên, tất định, không đo thời gian; không có tệp đăng ký trước. Tỷ số tính theo ảnh, rồi lấy trung bình; KTC 95\% bootstrap hai tầng ảnh $\times$ seed. Tập ảnh khác tập 100 ảnh của Bảng~\ref{tab:patches}. Các bộ phát hiện hai giai đoạn và SSD của cùng lần chạy đếm sau NMS nội bộ nên không được báo.}
\label{tab:x2}
\begin{tabular}{@{}lcccc@{}}
\toprule
Bộ phát hiện & Ảnh & $\Ntau$ sạch (trung vị) & $\Ntau$ có patch (trung vị) & Tỷ số $\Ntau$ (KTC 95\%) \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return write(t, body)


# ---------------------------------------------------------------- YOLOv5s: phân rã mức tăng toàn trình theo công đoạn (post hoc)
def t_decomp():
    t = Tab('tab_decomp')
    f = 'e10/E10_P1cpu2_20261102/stage_decomp_posthoc.json'
    s = j(f)['cells']
    lines = []
    for m, mv in (('overload', 'Overload'), ('phantom_sponges', 'Phantom Sponges')):
        for be in ('tv_nms', 'tv_batched', 'ultra_native'):
            v = s[f'{m}|{be}']
            sel = f'{f}:cells.{m}|{be}'
            lines.append(f'{mv} & {BE_VI[be]} & ' + t.n(v['d_total_ms'], sel + '.d_total_ms', sig=3) + ' (' + t.ci(*v['d_total_ci95'], sel + '.d_total_ci95', sig=2) + ') & '
                         + t.n(v['d_nms_ms'], sel + '.d_nms_ms', sig=3) + ' (' + t.ci(*v['d_nms_ci95'], sel + '.d_nms_ci95', sig=2) + ') & '
                         + t.n(v['d_rest_ms'], sel + '.d_rest_ms', sig=3) + ' (' + t.ci(*v['d_rest_ci95'], sel + '.d_rest_ci95', sig=2) + ') & '
                         + t.n(100 * v['rest_share_of_d_total'], sel + '.rest_share_of_d_total*100', d=0) + ' \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{\textbf{Post hoc}, YOLOv5s (640 px, một lõi CPU ghim): phân rã mức tăng thời gian của biến thể thích nghi theo hai tấn công toàn ảnh, theo cặp ảnh $\times$ seed so với trung bình hai nhánh sạch cùng ảnh (ms; KTC 95\% bootstrap hai tầng). $\Delta t_{\mathrm{NMS}}$ đo vi mô ở $\tau=0{,}25$. ``Phần còn lại'' $=\Delta t_{\mathrm{total}}-\Delta t_{\mathrm{NMS}}$ gồm lan truyền thuận, giải mã, lọc điểm và dựng đầu vào NMS; bản ghi thô không tách được các công đoạn này với nhau. Không đo mới.}
\label{tab:decomp}
\begin{tabular}{@{}llcccc@{}}
\toprule
Biến thể & Cách cài đặt & $\Delta t_{\mathrm{total}}$ & $\Delta t_{\mathrm{NMS}}$ & Phần còn lại & Phần còn lại / $\Delta t_{\mathrm{total}}$ (\%) \\
\midrule
""" + '\n'.join(lines) + '\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n'
    return write(t, body)


# ---------------------------------------------------------------- số dùng trong văn bản (không sinh .tex; chỉ để check_numbers.py đối chiếu)
def t_text():
    t = Tab('text')
    aa = 'e5/AA_P1cpu2_20261101/summary.json'
    a = j(aa)['profiles']['P1_cpu2']
    t.n(a['pin']['effective_cores'], f'{aa}:profiles.P1_cpu2.pin.effective_cores', d=2)
    t.n(abs(a['drift']['max_abs_rel_change']) * 100, f'{aa}:profiles.P1_cpu2.drift.max_abs_rel_change*100', d=0)
    for f in (aa, 'e5/AA640_P1cpu2_20261102b/summary.json'):
        se = j(f)['profiles']['P1_cpu2']['sensitivity_excluding_flagged_blocks']['total']
        t.n(se['n_images'], f'{f}:profiles.P1_cpu2.sensitivity_excluding_flagged_blocks.total.n_images')
        t.ci(*se['aa_ci95_log'], f'{f}:profiles.P1_cpu2.sensitivity_excluding_flagged_blocks.total.aa_ci95_log', d=3)
    b = j('e5/AA640_P1cpu2_20261102b/summary.json')['profiles']['P1_cpu2']
    t.n(b['pin']['effective_cores'], 'e5/AA640_P1cpu2_20261102b/summary.json:profiles.P1_cpu2.pin.effective_cores', d=2)
    t.n(b['drift']['max_abs_rel_change'] * 100, 'e5/AA640_P1cpu2_20261102b/summary.json:profiles.P1_cpu2.drift.max_abs_rel_change*100', d=1)
    c = j('e5/AA640_P1cpu2_20261102/summary.json')['profiles']['P1_cpu2']
    t.n(len(c['drift']['flagged']), 'e5/AA640_P1cpu2_20261102/summary.json:profiles.P1_cpu2.drift.flagged(len)')
    t.n(c['drift']['max_abs_rel_change'] * 100, 'e5/AA640_P1cpu2_20261102/summary.json:profiles.P1_cpu2.drift.max_abs_rel_change*100', d=0)
    # E1
    e1f = 'e1/E1_P1cpu2_20261101/summary.json'
    e1 = j(e1f)
    p1 = e1['primary_1']
    t.n(p1['median_ms_N2100'], f'{e1f}:primary_1.median_ms_N2100', sig=3)
    t.n(p1['median_ms_N10'], f'{e1f}:primary_1.median_ms_N10', sig=3)
    t.n(p1['R'], f'{e1f}:primary_1.R', sig=3)
    t.ci(*p1['ci95'], f'{e1f}:primary_1.ci95', sig=3)
    p2 = e1['primary_2']
    t.n(p2['misses'], f'{e1f}:primary_2.misses'); t.n(p2['n'], f'{e1f}:primary_2.n')
    t.ci(*p2['wilson95'], f'{e1f}:primary_2.wilson95', d=2)
    for be in ('torch_pure', 'ultra_native', 'tv_batched'):
        k = f'P1_cpu2|2100|{be}|mixed|80|None|300'
        v = e1['contrasts']['backend_over_tv_nms'][k]
        t.n(v['ratio'], f'{e1f}:contrasts.backend_over_tv_nms.{k}.ratio', sig=3); t.ci(*v['ci95'], f'{e1f}:contrasts.backend_over_tv_nms.{k}.ci95', sig=3)
    for be in BE:
        k = f'P1_cpu2|2100|{be}|80|None|2100'
        v = e1['contrasts']['disjoint_over_dense'][k]
        t.n(v['ratio'], f'{e1f}:contrasts.disjoint_over_dense.{k}.ratio', sig=3); t.ci(*v['ci95'], f'{e1f}:contrasts.disjoint_over_dense.{k}.ci95', sig=3)
    for cap in ('None', '300'):
        k = f'P1_cpu2|10000|torch_pure|disjoint|80|{cap}|10000'
        t.n(e1['curves'][k]['tau_median_ms'], f'{e1f}:curves.{k}.tau_median_ms', sig=2)
    u = [v for k, v in e1['curves'].items() if '|ultra_native|' in k]
    t.n(sum(v['over_ultra_time_limit'] for v in u), f'{e1f}:sum(curves[ultra_native].over_ultra_time_limit)')
    t.n(max(v['median_ms'] for v in u), f'{e1f}:max(curves[ultra_native].median_ms)', sig=3)
    # E9 / Amdahl
    fa = 'e9/E9_P1cpu2_20261102/summary_part_a.json'
    a9 = j(fa)
    t.n(a9['pin']['effective_cores'], f'{fa}:pin.effective_cores', d=2); t.n(a9['pin_end']['effective_cores'], f'{fa}:pin_end.effective_cores', d=2)
    t.n(a9['drift']['flagged'], f'{fa}:drift.flagged'); t.n(a9['drift']['points'], f'{fa}:drift.points'); t.n(a9['drift']['max_abs'] * 100, f'{fa}:drift.max_abs*100', d=0)
    for cv, n in (('320', '2100'), ('640', '8400')):
        for be in BE:
            k = f'{cv}|{be}|disjoint|capNone'
            t.n(a9['ratios'][k][n]['ratio'], f'{fa}:ratios.{k}.{n}.ratio', sig=3)
            k3 = f'{cv}|{be}|disjoint|cap300'
            t.n(a9['ratios'][k3][n]['ratio'], f'{fa}:ratios.{k3}.{n}.ratio', sig=3)
    fm = 'amdahl/amdahl_vs_e9_posthoc.json'
    m = j(fm)
    for cv in ('320', '640'):
        v = [x for k, x in m['in_session_mde_pct'].items() if k.startswith(cv)]
        t.n(min(v), f'{fm}:min(in_session_mde_pct[{cv}|*])', d=1); t.n(max(v), f'{fm}:max(in_session_mde_pct[{cv}|*])', d=1)
        tt = [x['t_total_clean_ms'] for k, x in m['cells'].items() if k.startswith(cv)]
        t.n(min(tt), f'{fm}:min(cells[{cv}|*].t_total_clean_ms)', sig=3); t.n(max(tt), f'{fm}:max(cells[{cv}|*].t_total_clean_ms)', sig=3)
    fs = 'e9/E9_P1cpu2_20261102/summary_part_a_sens_aa640b.json'
    s9 = j(fs)
    t.n(sum(1 for k in a9['n_star'] if k.startswith('640') and k.endswith('capNone') and a9['n_star'][k] != s9['n_star'][k]), f'{fa} vs {fs}: số ô 640 px có N* khác nhau (đếm)')
    ag = m['summary']['n_star_exact_agreement'].split('/')
    t.n(int(ag[0]), f'{fm}:summary.n_star_exact_agreement[0]'); t.n(int(ag[1]), f'{fm}:summary.n_star_exact_agreement[1]')
    # E10
    fe = 'e10/E10_P1cpu2_20261102/summary.json'
    e = j(fe)
    t.n(100 * (min(v['mean'] for v in e['total_ratio'].values()) - 1), f'{fe}:100*(min(total_ratio[*].mean)-1)', d=1)
    t.n(100 * (max(v['mean'] for v in e['total_ratio'].values()) - 1), f'{fe}:100*(max(total_ratio[*].mean)-1)', d=1)
    t.n(e['pin']['effective_cores'], f'{fe}:pin.effective_cores', d=2); t.n(e['pin_end']['effective_cores'], f'{fe}:pin_end.effective_cores', d=2)
    t.n(e['drift']['flagged'], f'{fe}:drift.flagged'); t.n(e['drift']['points'], f'{fe}:drift.points'); t.n(e['drift']['max_abs'] * 100, f'{fe}:drift.max_abs*100', d=1)
    for mth in ('overload', 'phantom_sponges'):
        nm = e['n_median'][f'{mth}|tau0.01']
        t.n(nm['clean'], f'{fe}:n_median.{mth}|tau0.01.clean', d=1); t.n(nm['patched'], f'{fe}:n_median.{mth}|tau0.01.patched', d=1)
    tr = [v['mean'] for v in e['total_ratio'].values()]
    t.n(min(tr), f'{fe}:min(total_ratio[*].mean)', d=3); t.n(max(tr), f'{fe}:max(total_ratio[*].mean)', d=3)
    mi = list(e['in_session_mde_pct'].values())
    t.n(min(mi), f'{fe}:min(in_session_mde_pct[*])', d=2); t.n(max(mi), f'{fe}:max(in_session_mde_pct[*])', d=2)
    fd = 'e10/E10_P1cpu2_20261102/stage_medians_posthoc.json'
    sd = j(fd)
    lib = ('tv_nms', 'tv_batched', 'ultra_native')
    for grp in ('clean', 'attack'):
        nv = [v['median'] for k, v in sd['nms_ms'].items() if (k.split('|')[0] == 'clean') == (grp == 'clean') and k.split('|')[1] in lib]
        t.n(min(nv), f'{fd}:min(nms_ms[{grp}|lib].median)', sig=2); t.n(max(nv), f'{fd}:max(nms_ms[{grp}|lib].median)', sig=2)
        tv = [v['median'] for k, v in sd['total_ms'].items() if (k.split('|')[0] == 'clean') == (grp == 'clean')]
        t.n(min(tv), f'{fd}:min(total_ms[{grp}|*].median)', d=0); t.n(max(tv), f'{fd}:max(total_ms[{grp}|*].median)', d=0)
    tp = {k.split('|')[0]: v['median'] for k, v in sd['nms_ms'].items() if k.endswith('|torch_pure')}
    t.n(tp['clean'], f'{fd}:nms_ms.clean|torch_pure.median', d=2)
    t.n(tp['overload'], f'{fd}:nms_ms.overload|torch_pure.median', d=0); t.n(tp['phantom_sponges'], f'{fd}:nms_ms.phantom_sponges|torch_pure.median', d=0)
    tc = sd['total_ms']['clean|tv_nms']['median']
    for mth in ('overload', 'phantom_sponges'):
        t.n(100 * (tp[mth] - tp['clean']) / tc, f'{fd}:100*(nms_ms.{mth}|torch_pure - nms_ms.clean|torch_pure)/total_ms.clean|tv_nms (suy ra)', d=0)
    st = j('e10/E10_P1cpu2_20261102/structural_check_posthoc.json')
    sv = [v['median_abs_log_err_struct'] for v in st.values()]
    t.n(min(sv), 'e10/E10_P1cpu2_20261102/structural_check_posthoc.json:min(*.median_abs_log_err_struct)', d=3); t.n(max(sv), 'e10/...:max(*.median_abs_log_err_struct)', d=3)
    sh = [v['nms_share_patched'] * 100 for v in st.values()]
    t.n(min(sh), 'e10/E10_P1cpu2_20261102/structural_check_posthoc.json:min(*.nms_share_patched)*100', d=1); t.n(max(sh), 'e10/...:max(*.nms_share_patched)*100', d=1)
    npd = e['nms_predictor']
    ip = [v['interp_mixed_median_abs_log_err_N_ge_100'] for v in npd.values()]
    t.n(min(ip), f'{fe}:min(nms_predictor[*].interp_mixed_median_abs_log_err_N_ge_100)', d=2); t.n(max(ip), f'{fe}:max(...)', d=2)
    mn = [v['median_abs_log_err_M_N'] for v in npd.values()]
    t.n(min(mn), f'{fe}:min(nms_predictor[*].median_abs_log_err_M_N)', d=2); t.n(max(mn), f'{fe}:max(...)', d=2)
    v = npd['tv_nms']
    t.n(v['delta'], f'{fe}:nms_predictor.tv_nms.delta', d=2); t.ci(*v['delta_ci95'], f'{fe}:nms_predictor.tv_nms.delta_ci95', d=2)
    # E6 (đo vi mô NMS: không bị lỗi chèn patch) cho Q4
    f6 = 'e6/E6_P1cpu2_20261102/summary.json'
    s6 = j(f6)
    for be, v in s6['n_only_prediction_from_e1'].items():
        sel = f'{f6}:n_only_prediction_from_e1.{be}'
        t.n(v['median_abs_log_error_vs_mixed'], sel + '.median_abs_log_error_vs_mixed', d=2); t.n(v['p90_abs_log_error'], sel + '.p90_abs_log_error', d=2)
        t.n(v['fraction_inside_envelope'], sel + '.fraction_inside_envelope', d=2); t.n(v['n_points'], sel + '.n_points')
    arms320 = ('C1', 'C3', 'B1', 'B2', 'B3', 'B4')
    rb = [s6['arms'][a][f'nms_tau0.01_{be}']['rho_between_clean'] for a in ('C1',) for be in BE] + [s6['arms'][a][f'nms_tau0.01_{be}']['rho_between_clean'] for a in ('B1',) for be in BE]
    t.n(min(rb), f'{f6}:min(arms[C1,B1].nms_tau0.01_*.rho_between_clean)', d=2); t.n(max(rb), f'{f6}:max(...)', d=2)
    rd = [s6['arms'][a][f'nms_tau0.01_{be}']['rho_dN_dt'] for a in arms320 for be in BE]
    t.n(min(rd), f'{f6}:min(arms[C1,C3,B1-B4].nms_tau0.01_*.rho_dN_dt)', d=2); t.n(max(rd), f'{f6}:max(...)', d=2)
    # N trung vị của patch (E6, tất định) để so với N* của YOLOv8n
    for arm, f in E6_SRC.items():
        v = j(f)['arms'][arm]['N_tau0.01']
        t.n(v['clean_median'], f'{f}:arms.{arm}.N_tau0.01.clean_median', d=1); t.n(v['patched_median'], f'{f}:arms.{arm}.N_tau0.01.patched_median', d=1)
    # phân rã YOLOv5s
    fdc = 'e10/E10_P1cpu2_20261102/stage_decomp_posthoc.json'
    dc = j(fdc)['cells']
    rest = [v['d_rest_ms'] for v in dc.values()]
    t.n(min(rest), f'{fdc}:min(cells[*].d_rest_ms)', sig=2); t.n(max(rest), f'{fdc}:max(cells[*].d_rest_ms)', sig=2)
    t.n(sum(1 for v in dc.values() if v['d_rest_ci95'][0] > 0), f'{fdc}:count(cells[*].d_rest_ci95[0] > 0)')
    # E11 lần 1 (bị loại): chỉ để nêu lý do loại trong văn bản
    f11 = 'e11/E11_P1cpu2_20261103/summary.json'
    e11s = j(f11)
    t.n(e11s['drift']['flagged'], f'{f11}:drift.flagged'); t.n(e11s['drift']['points'], f'{f11}:drift.points')
    t.n(e11s['in_session']['320']['tv_nms']['mde_total_pct'], f'{f11}:in_session.320.tv_nms.mde_total_pct', d=1)
    # E1 max Ultralytics trong E1/E9/E10 (từ bản ghi thô) để nói về giới hạn thời gian
    return write(t, None)


BUILDERS = [t_aa, t_dose, t_slopes, t_cap, t_nstar, t_amdahl, t_attacks, t_spec, t_train, t_nk, t_patches, t_impl, t_threshold, t_decomp, t_x2, t_text]


def build():
    return dict(b() for b in BUILDERS)


def main():
    check = '--check' in sys.argv
    tabs = build()
    hdr = '% SINH TỰ ĐỘNG bởi paper_vi/tables/make_tables.py — KHÔNG SỬA TAY.\n'
    bad = []
    for name, body in tabs.items():
        if body is None:  # chỉ đăng ký số dùng trong văn bản
            continue
        p = OUT / f'{name}.tex'
        new = hdr + body
        if check:
            if not p.exists() or p.read_text(encoding='utf-8') != new:
                bad.append(name)
        else:
            p.write_text(new, encoding='utf-8')
    if check:
        print('bảng khác bản sinh lại:', bad or 'không có')
        sys.exit(1 if bad else 0)
    (OUT / 'numbers.json').write_text(json.dumps(REG, indent=1, ensure_ascii=False), encoding='utf-8')
    print('đã ghi', len(tabs), 'bảng,', sum(len(v) for v in REG.values()), 'ô số')


if __name__ == '__main__':
    main()
