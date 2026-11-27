"""English tables for paper_en/main.tex, generated from the summary files of the frequency-locked AMD replication.

    python paper_en/tables_q3/make_tables_en.py          # writes paper_en/tables_q3/tab_*.tex and numbers_en.json
    python paper_en/tables_q3/make_tables_en.py --check  # report tables that differ from a fresh build (hand edits) -> exit 1
    python paper_en/tables_q3/make_tables_en.py --text   # also print the labelled numbers of the running text

Since 24/11/2026 the timing numbers come from one session (full-01) on a frequency-locked Linux desktop
(PREREG_AMD_REPLICATION_20261124; A/A from PREREG_AA_LINUX_20261124). The laptop builder of 17/11/2026 is kept in
paper_en/_backup_before_amd_20261124/tables_q3/. Tables that need no timing (tab_spec, tab_x2) still use the shared
helpers of paper/vi/tables/make_tables.py. Do not edit tab_*.tex by hand.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
_spec = importlib.util.spec_from_file_location('mt', ROOT / 'paper/vi/tables/make_tables.py')
mt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mt)
j = mt.j
BE = mt.BE
GEOM = mt.GEOM
BE_EN = {'torch_pure': 'pure PyTorch', 'tv_nms': 'torchvision \\texttt{nms}', 'tv_batched': 'torchvision batched', 'ultra_native': 'Ultralytics native'}
GEOM_EN = {'disjoint': 'disjoint', 'mixed': 'mixed', 'dense_cluster': 'dense cluster'}

# ---- sources (relative to sponge-sim/results)
AA = {cv: f'aa_linux_20261124/x/sponge-aa-20261124/full-01/aa_{cv}/summary.json' for cv in (320, 640)}
F = 'amd_20261124/full-01/'
E1 = F + 'e1/run/summary.json'
NC1 = F + 'e1nc1l/run/summary.json'
E9A = F + 'e9/run/summary_part_a.json'
AMD = F + 'analysis/amdahl_vs_e9_posthoc.json'
E10 = F + 'analysis/e10_summary.json'
SM = F + 'analysis/stage_medians_posthoc.json'
DC = F + 'analysis/stage_decomp_posthoc.json'
ADD = F + 'analysis/e10_addon.json'
E12 = F + 'e12/run/summary.json'
X12 = F + 'analysis/e12_extra.json'
NK = F + 'analysis/e9_part_b_e12.json'
PH = F + 'analysis/posthoc_amd.json'
DEVICE = 'one logical CPU of an AMD Ryzen~5 5500 locked at 3.6~GHz'


class Tab(mt.Tab):
    def n(self, x, src, d=None, sig=None):
        """Format a number (decimal point) and record its source."""
        if isinstance(x, str):
            s = '$>$' + x[1:] if x.startswith('>') else x
        elif isinstance(x, int) and d is None and sig is None:
            s = f'{x}'
        else:
            if sig is not None:
                d = max(sig - 1 - int(math.floor(math.log10(abs(x)))), 0) if x else 0
            s = f'{x:.{d}f}'
        if s.startswith('-'):
            s = '$-$' + s[1:]
        self.cells.append((s, src))
        return s


REG = {}
TXT = {}


def write(t, body):
    REG[t.name] = [dict(text=s, source=src) for s, src in t.cells]
    if body is None:  # numbers of the running text only
        return t.name, None
    body = body.replace('\\begin{tabular}', '\\begin{adjustbox}{max width=\\textwidth}\n\\begin{tabular}', 1)
    body = body.replace('\\end{tabular}', '\\end{tabular}\n\\end{adjustbox}', 1)
    body = body.replace('--', '-')  # house style (supervisor review 16/11): plain hyphens
    return t.name, body


END = '\n\\bottomrule\n\\end{tabular}\n'


def ci(t, v, src, **k):
    return t.ci(v[0], v[1], src, **k)


def t_aa():
    t = Tab('tab_aa')
    a, b = (j(AA[cv])['profiles']['P1_cpu2'] for cv in (320, 640))
    rows = [('pre', 'Pre-processing'), ('forward', 'Forward pass'), ('tau', 'Score filter ($\\tau$)'), ('nms_torch_pure', 'NMS (pure PyTorch)'),
            ('nms_tv_nms', 'NMS (torchvision)'), ('total', 'End-to-end')]
    lines = []
    for k, lab in rows:
        cells = []
        for cv, p in ((320, a), (640, b)):
            st = p['stages'][k]
            cells += [t.n(st['mde_ratio_pct'], f'{AA[cv]}:profiles.P1_cpu2.stages.{k}.mde_ratio_pct', d=3),
                      t.n(st['median_of_image_medians_ms'], f'{AA[cv]}:profiles.P1_cpu2.stages.{k}.median_of_image_medians_ms', sig=3)]
        lines.append(f'{lab} & ' + ' & '.join(cells) + ' \\\\')
    fl = lambda p, f: t.n(len(p['drift']['flagged']), f'{f}:profiles.P1_cpu2.drift.flagged(len)') + '/' + t.n(p['drift']['reference_points'], f'{f}:profiles.P1_cpu2.drift.reference_points')  # noqa: E731
    lines.append('Flagged reference points / total & ' + fl(a, AA[320]) + ' & & ' + fl(b, AA[640]) + ' & \\\\')
    eff = t.n(a['pin']['effective_cores'], f'{AA[320]}:profiles.P1_cpu2.pin.effective_cores', d=2)
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{A/A calibration on the frequency-locked profile ({eff} effective cores under load at 320 px): MDE (\%) and median time of each stage, 100 images $\times$ 20 repetitions. End-to-end time here includes resizing.}}
\label{{tab:aa}}
\begin{{tabular}}{{@{{}}lcccc@{{}}}}
\toprule
 & \multicolumn{{2}}{{c}}{{320 px}} & \multicolumn{{2}}{{c}}{{640 px}} \\
\cmidrule(lr){{2-3}}\cmidrule(lr){{4-5}}
Stage & MDE (\%) & Median (ms) & MDE (\%) & Median (ms) \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def nms_mde():
    aa = j(AA[320])['profiles']['P1_cpu2']['stages']
    return max(aa['nms_torch_pure']['mde_ratio_pct'], aa['nms_tv_nms']['mde_ratio_pct'])


def t_dose():
    t = Tab('tab_dose')
    s = j(E1)
    mde = nms_mde()
    lines = []
    for be in BE:
        for g in GEOM:
            k = f'P1_cpu2|{be}|{g}'
            v = s['dose_1e2_to_1e4'][k]
            sel = f'{E1}:dose_1e2_to_1e4.{k}'
            ok = v['ci95'][0] > 1 + mde / 100
            lines.append(f'{BE_EN[be]} & {GEOM_EN[g]} & ' + t.n(v['median_ms_N1e2'], sel + '.median_ms_N1e2', sig=3) + ' & '
                         + t.n(v['median_ms_N1e4'], sel + '.median_ms_N1e4', sig=3) + ' & ' + t.n(v['ratio'], sel + '.ratio', sig=3)
                         + ' & ' + ci(t, v['ci95'], sel + '.ci95', sig=3) + ' & ' + ('yes' if ok else 'no') + ' \\\\')
    m = t.n(mde, f'{AA[320]}:max(stages.nms_torch_pure.mde_ratio_pct,stages.nms_tv_nms.mde_ratio_pct)', d=3)
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Median NMS latency at $\Ntau=10^2$ and $10^4$ (10\,000-anchor head, 80 classes, no cap) and their ratio, for all four implementations $\times$ three geometries. 95\% CI: bootstrap over repetitions (30 per cell). Last column: lower bound above $1+\mathrm{{MDE}}$, with the larger A/A MDE of the NMS stage ({m}\%).}}
\label{{tab:dose}}
\begin{{tabular}}{{@{{}}llccccc@{{}}}}
\toprule
Implementation & Geometry & $t_{{\mathrm{{NMS}}}}(10^2)$ (ms) & $t_{{\mathrm{{NMS}}}}(10^4)$ (ms) & Ratio & 95\% CI & Above MDE \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def nc1_cells():
    c = j(NC1)['curves']
    out = {}
    for be in BE:
        for g in GEOM:
            key = lambda nc, n: f'P1_cpu2|10000|{be}|{g}|{nc}|None|{n}'  # noqa: E731
            out[(be, g)] = dict(t1_3=c[key(1, 1000)]['median_ms'], t1_4=c[key(1, 10000)]['median_ms'], t80_4=c[key(80, 10000)]['median_ms'],
                                k1_3=key(1, 1000), k1_4=key(1, 10000), k80_4=key(80, 10000))
    return out


def t_nc1():
    t = Tab('tab_nc1')
    lines = []
    for (be, g), v in nc1_cells().items():
        src = lambda k: f'{NC1}:curves.{v[k]}.median_ms'  # noqa: E731
        # Label repeated on every row (review 27/11: blank cells shifted columns in the PDF text layer).
        lines.append(f'{BE_EN[be]} & {GEOM_EN[g]} & ' + t.n(v['t1_3'], src('k1_3'), sig=3) + ' & ' + t.n(v['t1_4'], src('k1_4'), sig=3) + ' & '
                     + t.n(v['t1_4'] / v['t1_3'], f'{src("k1_4")} / {src("k1_3")}', sig=3) + ' & ' + t.n(v['t80_4'], src('k80_4'), sig=3) + ' & '
                     + t.n(v['t1_4'] / v['t80_4'], f'{src("k1_4")} / {src("k80_4")}', sig=3) + ' \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{One-class candidate sets (10\,000-anchor head, no cap): median NMS latency (ms) of one class at $\Ntau=10^3$ and $10^4$, the same $10^4$ boxes spread over 80 classes, and two ratios of medians (descriptive). Same session design as Table~\ref{tab:dose}, 30 repetitions per cell.}
\label{tab:nc1}
\begin{tabular}{@{}llccccc@{}}
\toprule
 & & \multicolumn{3}{c}{One class} & 80 classes & \\
\cmidrule(lr){3-5}\cmidrule(lr){6-6}
Implementation & Geometry & $10^3$ & $10^4$ & Ratio & $10^4$ & One / 80 classes \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def t_cap():
    t = Tab('tab_cap')
    s = j(E1)
    lines = []
    for g in GEOM:
        for i, be in enumerate(BE):
            k0, k3 = f'P1_cpu2|10000|{be}|{g}|80|None|10000', f'P1_cpu2|10000|{be}|{g}|80|300|10000'
            kc = f'P1_cpu2|10000|{be}|{g}|80|10000'
            c = s['contrasts']['cap300_over_capNone'][kc]
            sel = f'{E1}:1/contrasts.cap300_over_capNone.{kc}'
            # Label repeated on every row and CI in its own column, as in tab_dose (review 27/11).
            lines.append(GEOM_EN[g].capitalize() + f' & {BE_EN[be]} & '
                         + t.n(s['curves'][k0]['median_ms'], f'{E1}:curves.{k0}.median_ms', sig=3) + ' & '
                         + t.n(s['curves'][k3]['median_ms'], f'{E1}:curves.{k3}.median_ms', sig=3) + ' & '
                         + t.n(1 / c['ratio'], sel + '.ratio', sig=3) + ' & ' + t.ci(1 / c['ci95'][1], 1 / c['ci95'][0], sel + '.ci95(inverted)', sig=3) + ' \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{Median NMS latency (ms) at $\Ntau=10^4$ (10\,000-anchor head, 80 classes) without a cap and with a top-300 cap, and the reduction factor (uncapped divided by capped; 95\% CI, bootstrap over repetitions).}
\label{tab:cap}
\begin{tabular}{@{}llcccc@{}}
\toprule
Geometry & Implementation & No cap (ms) & Cap 300 (ms) & Reduction & 95\% CI \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def t_nstar():
    t = Tab('tab_nstar')
    a, m = j(E9A), j(AMD)
    lines = []
    for be in BE:
        for i, g in enumerate(GEOM):
            k3, k6 = f'320|{be}|{g}|capNone', f'640|{be}|{g}|capNone'
            row = [BE_EN[be], GEOM_EN[g],  # label repeated on every row (review 27/11)
                   t.n(a['n_star'][k3], f'{E9A}:n_star.{k3}'), t.n(m['n_star'][k3]['predicted'], f'{AMD}:n_star.{k3}.predicted'),
                   t.n(a['n_star'][k6], f'{E9A}:n_star.{k6}'), t.n(m['n_star'][k6]['predicted'], f'{AMD}:n_star.{k6}.predicted')]
            lines.append(' & '.join(row) + ' \\\\')
    m3 = t.n(a['mde_total_pct']['320'], f'{E9A}:mde_total_pct.320', d=3)
    m6 = t.n(a['mde_total_pct']['640'], f'{E9A}:mde_total_pct.640', d=3)
    fb = t.n(a['drift']['flagged'], f'{E9A}:drift.flagged') + '/' + t.n(a['drift']['points'], f'{E9A}:drift.points')
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Threshold $N^{{*}}$: the smallest grid level whose end-to-end ratio has a lower 95\% bound above $1+\mathrm{{MDE}}$ (full-pipeline injection, 20 images, no cap); ``$>$'': not reached. ``Measured'' uses the A/A MDE ({m3}\% at 320 px, {m6}\% at 640 px); {fb} reference points were flagged, so the preregistered analysis without flagged blocks is identical. $^{{\dagger}}$Post hoc budget estimate.}}
\label{{tab:nstar}}
\begin{{tabular}}{{@{{}}llcccc@{{}}}}
\toprule
 & & \multicolumn{{2}}{{c}}{{320 px (grid 100, 300, 1000, 2100)}} & \multicolumn{{2}}{{c}}{{640 px (grid 300, 1000, 3000, 8400)}} \\
\cmidrule(lr){{3-4}}\cmidrule(lr){{5-6}}
Implementation & Geometry & Measured & Predicted$^{{\dagger}}$ & Measured & Predicted$^{{\dagger}}$ \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def t_amdahl():
    t = Tab('tab_amdahl')
    m, e = j(AMD), j(E10)
    lines = []
    for cv, nmax in ((320, 2100), (640, 8400)):
        lines.append(f'\\multicolumn{{6}}{{@{{}}l}}{{\\textit{{A. Full-pipeline injection, \\textbf{{post hoc}}; {cv} px, disjoint boxes, no cap, $\\Ntau={nmax}$}}}} \\\\')
        for be in BE:
            k = f'{cv}|{be}|disjoint|capNone'
            r = [x for x in m['cells'][k]['rows'] if x['n'] == nmax][0]
            i = m['cells'][k]['rows'].index(r)
            sel = f'{AMD}:cells.{k}.rows[{i}]'
            lines.append(f'{BE_EN[be]} & ' + t.n(r['r_pred'], sel + '.r_pred', sig=3) + ' & ' + t.n(r['r_meas'], sel + '.r_meas', sig=3) + ' & '
                         + t.n(r['abs_log_err'], sel + '.abs_log_err', d=3) + ' & ' + t.n(m['n_star'][k]['predicted'], f'{AMD}:n_star.{k}.predicted') + ' / '
                         + t.n(m['n_star'][k]['measured'], f'{AMD}:n_star.{k}.measured') + ' & -- \\\\')
    lines.append('\\midrule')
    lines.append('\\multicolumn{6}{@{}l}{\\textit{B. Whole-image attack variants (YOLOv5s, 640 px), preregistered model and rule}} \\\\')
    for mth, mv in (('overload', 'Overload'), ('phantom_sponges', 'Phantom Sponges')):
        for be in ('tv_nms', 'tv_batched', 'ultra_native'):
            k = f'{mth}|{be}'
            am = e['amdahl'][k]
            sel = f'{E10}:amdahl.{k}'
            lines.append(f'{mv}, {BE_EN[be]} & ' + t.n(am['r_pred_mean'], sel + '.r_pred_mean', d=3) + ' & ' + t.n(am['r_meas_mean'], sel + '.r_meas_mean', d=3) + ' & '
                         + t.n(am['median_abs_log_err'], sel + '.median_abs_log_err', d=3) + ' (' + ci(t, am['ci95'], sel + '.ci95', d=3) + ') & -- & '
                         + ('pass' if am['passes_prereg_rule'] else '\\textbf{fail}') + ' \\\\')
    sm = m['summary']
    e1 = t.n(sm['median_abs_log_err'], f'{AMD}:summary.median_abs_log_err', d=3)
    e9 = t.n(sm['p90_abs_log_err'], f'{AMD}:summary.p90_abs_log_err', d=3)
    nc = t.n(sm['n_cells'], f'{AMD}:summary.n_cells')
    ag = t.n(sm['n_star_exact_agreement'], f'{AMD}:summary.n_star_exact_agreement')
    npass = sum(v['passes_prereg_rule'] for v in e['amdahl'].values())
    np_ = t.n(npass, f'{E10}:amdahl[*].passes_prereg_rule (count)') + '/' + t.n(len(e['amdahl']), f'{E10}:amdahl(len)')
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Budget estimate $R_{{\mathrm{{pred}}}} = 1+\Delta t_{{\mathrm{{NMS}}}}/t_{{\mathrm{{total}}}}$ against the measured ratio $R_{{\mathrm{{meas}}}}$; error is $|\ln(R_{{\mathrm{{meas}}}}/R_{{\mathrm{{pred}}}})|$. Part A (post hoc): full-pipeline injection, {nc} cells, median error {e1}, 90th percentile {e9}; predicted and measured $N^{{*}}$ agree in {ag} cells. Part B: whole-image attack variants on YOLOv5s, preregistered rule (upper 95\% bound of the median error $<0.05$); {np_} cells pass.}}
\label{{tab:amdahl}}
\begin{{tabular}}{{@{{}}lccccc@{{}}}}
\toprule
 & $R_{{\mathrm{{pred}}}}$ & $R_{{\mathrm{{meas}}}}$ & Error (95\% CI) & $N^{{*}}$ predicted / measured & Rule \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def t_attacks():
    t = Tab('tab_attacks')
    s, sd = j(E10), j(SM)
    lines = []
    for m, mv in (('overload', 'Overload'), ('phantom_sponges', 'Phantom Sponges')):
        nr, nm = s['n_ratio'][f'{m}|tau0.25'], s['n_median'][f'{m}|tau0.25']
        for i, be in enumerate(('tv_nms', 'tv_batched', 'ultra_native')):
            k = f'{m}|{be}'
            tr = s['total_ratio'][k]
            head = (f'{mv} & ' + t.n(nm['clean'], f'{E10}:n_median.{m}|tau0.25.clean', d=1) + ' $\\to$ ' + t.n(nm['patched'], f'{E10}:n_median.{m}|tau0.25.patched', d=1)
                    + ' & ' + t.n(nr['mean'], f'{E10}:n_ratio.{m}|tau0.25.mean', sig=3) + ' (' + ci(t, nr['ci95'], f'{E10}:n_ratio.{m}|tau0.25.ci95', sig=3) + ')') if i == 0 else ' & & '
            tc = sd['total_ms'][f'clean|{be}']['median']
            dstar = s['in_session_mde_pct'][be] / 100 * tc
            dn = sd['nms_ms'][f'{m}|{be}']['median'] - sd['nms_ms'][f'clean|{be}']['median']
            lines.append(head + f' & {BE_EN[be]} & ' + t.n(tr['mean'], f'{E10}:total_ratio.{k}.mean', d=3) + ' (' + ci(t, tr['ci95'], f'{E10}:total_ratio.{k}.ci95', d=3) + ') & '
                         + t.n(s['in_session_mde_pct'][be], f'{E10}:in_session_mde_pct.{be}', d=2) + ' & ' + ('yes' if tr['exceeds_in_session_mde'] else 'no') + ' & '
                         + t.n(dstar, f'{E10}:in_session_mde_pct.{be}/100 * {SM}:total_ms.clean|{be}.median', sig=2) + ' & '
                         + t.n(dn, f'{SM}:nms_ms.{m}|{be}.median - nms_ms.clean|{be}.median', sig=2) + ' \\\\')
    ni = t.n(s['n_images'], f'{E10}:n_images')
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Adaptive variants of two whole-image attacks (YOLOv5s, 640 px, {ni} images $\times$ 5 seeds, frequency-locked core). Median $\Ntau$ clean $\to$ perturbed and mean of the per-image $\Ntau$ ratios ($\tau=0.25$); end-to-end ratio (95\% CI, two-level bootstrap); ``above MDE'': lower bound $>1+\mathrm{{MDE}}$ of the session. $^{{\dagger}}$Post hoc: threshold $\Delta t^{{*}}$ and median NMS increase.}}
\label{{tab:attacks}}
\begin{{tabular}}{{@{{}}lcclccccc@{{}}}}
\toprule
Variant & $\Ntau$ clean $\to$ attack & $\Ntau$ ratio (95\% CI) & Implementation & End-to-end ratio (95\% CI) & MDE (\%) & Above MDE & $\Delta t^{{*}}$ (ms)$^{{\dagger}}$ & $\Delta t_{{\mathrm{{NMS}}}}$ (ms)$^{{\dagger}}$ \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


METHOD_EN = {('sg_ga', 'saliency'): 'GA, saliency placement', ('ga_center', 'center'): 'GA, centre placement', ('ga_random_location', 'random'): 'GA, random placement',
             ('random_search', 'saliency'): 'random search, saliency', ('gradient_tanh', 'saliency'): 'gradient ascent (tanh), saliency'}


def t_spec():
    t = Tab('tab_spec')
    lines = []
    seeds = set()
    for c in mt.CONDS:
        sp = mt.spec(c)
        for p in mt.ckpts(c, 62500):
            seeds.add(int(p.parent.name[4:]))
        src = f'{mt.E7}/{c}/seed0/{mt.ckpts(c, 62500, 0)[0].name}:specification'
        meth = METHOD_EN[(sp['method'], sp['location'])]
        lines.append(f'{c.split("_")[0]} & {meth} & ' + t.n(sp['canvas'], src + '.canvas') + ' & ' + t.n(sp['size'], src + '.size') + ' & '
                     + t.n(sp['threshold'], src + '.threshold', d=2) + ' & ' + t.n(sp['n_train'], src + '.n_train') + ' \\\\')
    sd = f'{min(seeds)}--{max(seeds)}'
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Conditions of the case study, read from the specification stored in the checkpoints of the patch generation run. $\tau_{{\mathrm{{obj}}}}$ is the threshold in the optimization objective. All conditions use software EOT, seeds {sd}, and three budget levels.}}
\label{{tab:spec}}
\begin{{tabular}}{{@{{}}llcccc@{{}}}}
\toprule
Condition & Method & Input (px) & Patch (px) & $\tau_{{\mathrm{{obj}}}}$ & Training images \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def t_nk():
    t = Tab('tab_nk')
    s = j(NK)
    key = 'test1_e6_320_posthoc'
    v0 = s[key]['torch_pure']
    lines = ['\\multicolumn{4}{@{}l}{\\textit{Real candidate sets of the patch session, \\textbf{post hoc} (' + t.n(v0['n_units'], f'{NK}:{key}.torch_pure.n_units')
             + ' units, ' + t.n(v0['n_images'], f'{NK}:{key}.torch_pure.n_images') + ' images)}} \\\\']
    for be in BE:
        v = s[key][be]
        sel = f'{NK}:{key}.{be}'
        lines.append(f'{BE_EN[be]} & ' + t.n(v['median_abs_log_err_M_N'], sel + '.median_abs_log_err_M_N', d=2) + ' & ' + t.n(v['median_abs_log_err_M_NK'], sel + '.median_abs_log_err_M_NK', d=2)
                     + ' & ' + t.n(v['delta'], sel + '.delta', d=2) + ' (' + t.ci(v['delta_ci95'][0], v['delta_ci95'][1], sel + '.delta_ci95', d=2, sep=' to ') + ') \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{Median error $|\ln(t_{\mathrm{meas}}/t_{\mathrm{pred}})|$ of $M_N$ and $M_{NK}$, fitted on the injection cells, on the real candidate sets of all arms of the patch session ($\tau=0.01$), and the difference $\Delta$ ($M_N$ minus $M_{NK}$) with a 95\% two-level bootstrap CI (images, units within images). $\Delta>0$ means that adding $K$ reduces the error.}
\label{tab:nk}
\begin{tabular}{@{}lccc@{}}
\toprule
Implementation & $M_N$ & $M_{NK}$ & $\Delta$ (95\% CI) \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


ARM_EN = [('C1', '320 px, 64-px patch, $\\tau_{\\mathrm{obj}}$ 0.01'), ('C3', '320 px, 64-px patch, $\\tau_{\\mathrm{obj}}$ 0.25'), ('B3', 'Random search (320 px)'),
          ('B1', 'GA, centre placement (320 px)'), ('B2', 'GA, random placement (320 px)'), ('B4', 'Gradient ascent (320 px)'),
          ('C2', '640 px, 128-px patch, $\\tau_{\\mathrm{obj}}$ 0.01'), ('C4', '640 px, 64-px patch, $\\tau_{\\mathrm{obj}}$ 0.01')]


def t_patches():
    t = Tab('tab_patches')
    s = j(E12)
    lines = []
    for arm, lab in ARM_EN:
        a = s['arms'][arm]
        sel = f'{E12}:arms.{arm}'
        cv = str(a['canvas'])
        cells = [t.n(a['N_tau0.01']['ratio_mean'], sel + '.N_tau0.01.ratio_mean', d=2) + ' (' + ci(t, a['N_tau0.01']['ratio_ci95'], sel + '.N_tau0.01.ratio_ci95', d=2) + ')',
                 t.n(a['N_tau0.25']['ratio_mean'], sel + '.N_tau0.25.ratio_mean', d=2) + ' (' + ci(t, a['N_tau0.25']['ratio_ci95'], sel + '.N_tau0.25.ratio_ci95', d=2) + ')',
                 t.n(a['nms_tau0.01_tv_nms']['ratio_mean'], sel + '.nms_tau0.01_tv_nms.ratio_mean', d=3) + ' (' + ci(t, a['nms_tau0.01_tv_nms']['ratio_ci95'], sel + '.nms_tau0.01_tv_nms.ratio_ci95', d=3) + ')']
        for be in ('tv_nms', 'torch_pure'):
            v = a[f'total_{be}']
            cells.append(t.n(v['ratio_mean'], f'{sel}.total_{be}.ratio_mean', d=4) + ' (' + ci(t, v['ratio_ci95'], f'{sel}.total_{be}.ratio_ci95', d=4) + ')'
                         + (' (above)' if v['exceeds_in_session_mde'] else ''))
        cells.append(' / '.join(t.n(s['in_session'][cv][be]['mde_total_pct'], f'{E12}:in_session.{cv}.{be}.mde_total_pct', d=2) for be in ('tv_nms', 'torch_pure')))
        lines.append(f'{lab} & ' + ' & '.join(cells) + ' \\\\')
    x = j(X12)['gate']['summary']
    acc = t.n(x['accepted'], f'{X12}:gate.summary.accepted') + '/' + t.n(x['attempts'], f'{X12}:gate.summary.attempts')
    body = rf"""\begin{{table*}}[t]
\centering\small
\caption{{Effect of the frozen patches relative to clean images of the same canvas, 100 images $\times$ 5 seeds, one drift-gated session ({acc} blocks accepted at the first attempt). All ratios are measured: mean over image $\times$ seed pairs, 95\% CI from a two-level bootstrap. NMS: torchvision, $\tau=0.01$. ``(above)'': lower bound $>1+\mathrm{{MDE}}$; MDE in-session (two clean arms), torchvision / pure PyTorch.}}
\label{{tab:patches}}
\begin{{tabular}}{{@{{}}lcccccc@{{}}}}
\toprule
Condition & $\Ntau$ ratio ($\tau$=0.01) & $\Ntau$ ratio ($\tau$=0.25) & NMS ratio & End-to-end, \texttt{{nms}} & End-to-end, pure PyTorch & MDE (\%) \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def t_threshold():
    t = Tab('tab_threshold')
    s = j(E12)
    ins = s['in_session']
    lines = []
    for cv in ('320', '640'):
        src = lambda be, k: f'{E12}:in_session.{cv}.{be}.{k}'  # noqa: E731
        lines.append(f'Clean $t_{{\\mathrm{{total}}}}$, {cv} px (ms) & ' + ' & '.join(t.n(ins[cv][be]['t_total_clean_median_ms'], src(be, 't_total_clean_median_ms'), sig=3) for be in ('tv_nms', 'torch_pure')) + ' \\\\')
        lines.append(f'In-session end-to-end MDE, {cv} px (\\%) & ' + ' & '.join(t.n(ins[cv][be]['mde_total_pct'], src(be, 'mde_total_pct'), d=2) for be in ('tv_nms', 'torch_pure')) + ' \\\\')
        lines.append(f'Threshold $\\Delta t^{{*}}=\\mathrm{{MDE}}\\times t_{{\\mathrm{{total}}}}$, {cv} px (ms) & ' + ' & '.join(t.n(ins[cv][be]['threshold_delta_nms_ms'], src(be, 'threshold_delta_nms_ms'), sig=2) for be in ('tv_nms', 'torch_pure')) + ' \\\\')
    lines.append('\\midrule')
    b = {be: s['arms']['B4'][f'total_{be}'] for be in ('tv_nms', 'torch_pure')}
    sb = lambda be, k: f'{E12}:arms.B4.total_{be}.{k}'  # noqa: E731
    lines.append('$\\Delta t_{\\mathrm{NMS}}$ of the gradient baseline, measured (ms) & ' + ' & '.join(t.n(b[be]['delta_nms_ms_mean'], sb(be, 'delta_nms_ms_mean'), sig=2) + ' (' + ci(t, b[be]['delta_nms_ms_ci95'], sb(be, 'delta_nms_ms_ci95'), sig=2) + ')' for be in b) + ' \\\\')
    lines.append('Above $\\Delta t^{*}$ (320 px) & ' + ' & '.join('yes' if b[be]['delta_nms_ms_mean'] > ins['320'][be]['threshold_delta_nms_ms'] else 'no' for be in b) + ' \\\\')
    lines.append('$R_{\\mathrm{pred}} = 1+\\Delta t_{\\mathrm{NMS}}/t_{\\mathrm{total}}$, budget estimate & ' + ' & '.join(t.n(b[be]['amdahl_pred_mean'], sb(be, 'amdahl_pred_mean'), d=4) for be in b) + ' \\\\')
    lines.append('$R_{\\mathrm{meas}}$, measured (95\\% CI) & ' + ' & '.join(t.n(b[be]['ratio_mean'], sb(be, 'ratio_mean'), d=4) + ' (' + ci(t, b[be]['ratio_ci95'], sb(be, 'ratio_ci95'), d=4) + ')' for be in b) + ' \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{Threshold $\Delta t^{*}$ for the end-to-end ratio to exceed the MDE in the patch session, and the gradient baseline (B4, 320 px, 100 images $\times$ 5 seeds). $t_{\mathrm{total}}$ and the MDE come from the two clean arms of the same session (prepared tensors). $\Delta t_{\mathrm{NMS}}$ is a micro-benchmark measurement; $R_{\mathrm{pred}}$ is the budget estimate and $R_{\mathrm{meas}}$ the end-to-end measurement.}
\label{tab:threshold}
\begin{tabular}{@{}lcc@{}}
\toprule
 & torchvision \texttt{nms} & pure PyTorch \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


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
                     + ' (' + ci(t, v['ratio_ci95'], sel + '.ratio_ci95', d=3) + ') \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{\textbf{Post hoc, historical data}: pre-NMS candidate counts ($\tau=0.01$, 320 px) of five YOLO detectors with five earlier SG-GA patches inserted (seeds 0--4, optimized on YOLOv8n in an earlier run, budget 2500 queries). Counts only, deterministic, no timing; no preregistration. Ratios are computed per image and then averaged; 95\% CI, two-level bootstrap over images $\times$ seeds. The image set differs from the 100 images of Table~\ref{tab:patches}. The two-stage and SSD detectors of the same run count after their internal NMS and are not reported.}
\label{tab:x2}
\begin{tabular}{@{}lcccc@{}}
\toprule
Detector & Images & Clean $\Ntau$ (median) & Patched $\Ntau$ (median) & $\Ntau$ ratio (95\% CI) \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


def t_decomp():
    t = Tab('tab_decomp')
    s = j(DC)['cells']
    lines = []
    for m, mv in (('overload', 'Overload'), ('phantom_sponges', 'Phantom Sponges')):
        for be in ('tv_nms', 'tv_batched', 'ultra_native'):
            v = s[f'{m}|{be}']
            sel = f'{DC}:cells.{m}|{be}'
            lines.append(f'{mv} & {BE_EN[be]} & ' + t.n(v['d_total_ms'], sel + '.d_total_ms', sig=3) + ' (' + ci(t, v['d_total_ci95'], sel + '.d_total_ci95', sig=2) + ') & '
                         + t.n(v['d_nms_ms'], sel + '.d_nms_ms', sig=3) + ' (' + ci(t, v['d_nms_ci95'], sel + '.d_nms_ci95', sig=2) + ') & '
                         + t.n(v['d_rest_ms'], sel + '.d_rest_ms', sig=3) + ' (' + ci(t, v['d_rest_ci95'], sel + '.d_rest_ci95', sig=2) + ') \\\\')
    body = r"""\begin{table*}[t]
\centering\small
\caption{\textbf{Post hoc}, YOLOv5s (640 px): decomposition of the latency increase of the whole-image attack variants per image $\times$ seed pair (ms; 95\% CI, two-level bootstrap). The remainder is $\Delta t_{\mathrm{total}}-\Delta t_{\mathrm{NMS}}$; the raw records do not separate its stages.}
\label{tab:decomp}
\begin{tabular}{@{}llccc@{}}
\toprule
Variant & Implementation & $\Delta t_{\mathrm{total}}$ & $\Delta t_{\mathrm{NMS}}$ & Remainder \\
\midrule
""" + '\n'.join(lines) + END + '\\end{table*}\n'
    return write(t, body)


# ------------------------------------------------------------------ numbers of the running text
def t_text():
    t = Tab('text')

    def x(label, v, src, **k):
        TXT[label] = t.n(v, src, **k)

    def xr(label, vals, src, **k):
        """min and max of a list of values from one source expression."""
        x(label + '_min', min(vals), f'min({src})', **k)
        x(label + '_max', max(vals), f'max({src})', **k)

    # A/A
    for cv in (320, 640):
        p = j(AA[cv])['profiles']['P1_cpu2']
        f = AA[cv]
        x(f'aa{cv}_eff', p['pin']['effective_cores'], f'{f}:profiles.P1_cpu2.pin.effective_cores', d=2)
        x(f'aa{cv}_drift_pct', p['drift']['max_abs_rel_change'] * 100, f'{f}:profiles.P1_cpu2.drift.max_abs_rel_change*100', d=2)
        for st, d in (('total', 3), ('nms_torch_pure', 3), ('nms_tv_nms', 3), ('forward', 3)):
            x(f'aa{cv}_mde_{st}', p['stages'][st]['mde_ratio_pct'], f'{f}:profiles.P1_cpu2.stages.{st}.mde_ratio_pct', d=d)
        x(f'aa{cv}_t_total', p['stages']['total']['median_of_image_medians_ms'], f'{f}:profiles.P1_cpu2.stages.total.median_of_image_medians_ms', sig=3)
        x(f'aa{cv}_t_pre', p['stages']['pre']['median_of_image_medians_ms'], f'{f}:profiles.P1_cpu2.stages.pre.median_of_image_medians_ms', sig=3)
        x(f'aa{cv}_t_fwd', p['stages']['forward']['median_of_image_medians_ms'], f'{f}:profiles.P1_cpu2.stages.forward.median_of_image_medians_ms', sig=3)
    # E1
    e1 = j(E1)
    p1, p2 = e1['primary_1'], e1['primary_2']
    x('e1_t2100', p1['median_ms_N2100'], f'{E1}:primary_1.median_ms_N2100', sig=3)
    x('e1_t10', p1['median_ms_N10'], f'{E1}:primary_1.median_ms_N10', sig=3)
    x('e1_R', p1['R'], f'{E1}:primary_1.R', sig=3)
    x('e1_R_lo', p1['ci95'][0], f'{E1}:primary_1.ci95[0]', sig=3); x('e1_R_hi', p1['ci95'][1], f'{E1}:primary_1.ci95[1]', sig=3)
    x('e1_miss', p2['misses'], f'{E1}:primary_2.misses'); x('e1_miss_n', p2['n'], f'{E1}:primary_2.n')
    x('e1_wil_lo', p2['wilson95'][0], f'{E1}:primary_2.wilson95[0]', d=2); x('e1_wil_hi', p2['wilson95'][1], f'{E1}:primary_2.wilson95[1]', d=2)
    x('e1_miss_total_ms', p2['median_total_ms'], f'{E1}:primary_2.median_total_ms', sig=3)
    dz = e1['dose_1e2_to_1e4']
    xr('e1_dose', [v['ratio'] for v in dz.values()], f'{E1}:dose_1e2_to_1e4[*].ratio', sig=3)
    for be in BE:
        for g in GEOM:
            x(f'e1_t1e4_{be}_{g}', dz[f'P1_cpu2|{be}|{g}']['median_ms_N1e4'], f'{E1}:dose_1e2_to_1e4.P1_cpu2|{be}|{g}.median_ms_N1e4', sig=3)
    cap = e1['contrasts']['cap300_over_capNone']
    xr('e1_cap', [1 / v['ratio'] for k, v in cap.items() if k.endswith('|80|10000') and k.split('|')[1] == '10000'], f'{E1}:1/contrasts.cap300_over_capNone[10000-anchor, N=10000].ratio', sig=3)
    for c in ('None', '300'):
        k = f'P1_cpu2|10000|torch_pure|disjoint|80|{c}|10000'
        x(f'e1_tau_ms_cap{c}', e1['curves'][k]['tau_median_ms'], f'{E1}:curves.{k}.tau_median_ms', sig=2)
    u = [v for k, v in e1['curves'].items() if '|ultra_native|' in k]
    x('e1_ultra_over_limit', sum(v['over_ultra_time_limit'] for v in u), f'{E1}:sum(curves[ultra_native].over_ultra_time_limit)')
    x('e1_ultra_max_ms', max(v['median_ms'] for v in u), f'{E1}:max(curves[ultra_native].median_ms)', sig=3)
    # E1, one class
    nc = nc1_cells()
    xr('nc1_ratio34', [v['t1_4'] / v['t1_3'] for v in nc.values()], f'{NC1}:curves[*|1|None|10000].median_ms / curves[*|1|None|1000].median_ms', sig=3)
    for g in GEOM:
        v = nc[('tv_batched', g)]
        x(f'nc1_tvb_{g}_1', v['t1_4'], f'{NC1}:curves.{v["k1_4"]}.median_ms', sig=3)
        x(f'nc1_tvb_{g}_80', v['t80_4'], f'{NC1}:curves.{v["k80_4"]}.median_ms', sig=3)
        x(f'nc1_tvb_{g}_r', v['t1_4'] / v['t80_4'], f'{NC1}:curves.{v["k1_4"]}.median_ms / curves.{v["k80_4"]}.median_ms', sig=3)
    for be in ('torch_pure', 'tv_nms'):
        xr(f'nc1_r180_{be}', [nc[(be, g)]['t1_4'] / nc[(be, g)]['t80_4'] for g in GEOM], f'{NC1}:one/80 classes at 1e4, {be}, three geometries', d=2)
    v = nc[('ultra_native', 'dense_cluster')]
    x('nc1_ultra_dense_r', v['t1_4'] / v['t80_4'], f'{NC1}:curves.{v["k1_4"]}.median_ms / curves.{v["k80_4"]}.median_ms', d=2)
    # E9
    a9 = j(E9A)
    x('e9_eff0', a9['pin']['effective_cores'], f'{E9A}:pin.effective_cores', d=2); x('e9_eff1', a9['pin_end']['effective_cores'], f'{E9A}:pin_end.effective_cores', d=2)
    x('e9_flag', a9['drift']['flagged'], f'{E9A}:drift.flagged'); x('e9_points', a9['drift']['points'], f'{E9A}:drift.points')
    x('e9_drift_pct', a9['drift']['max_abs'] * 100, f'{E9A}:drift.max_abs*100', d=1)
    for cv, n in (('320', '2100'), ('640', '8400')):
        for be in BE:
            k = f'{cv}|{be}|disjoint|capNone'
            x(f'e9_r_{cv}_{be}', a9['ratios'][k][n]['ratio'], f'{E9A}:ratios.{k}.{n}.ratio', sig=3)
            k3 = f'{cv}|{be}|disjoint|cap300'
            x(f'e9_rcap_{cv}_{be}', a9['ratios'][k3][n]['ratio'], f'{E9A}:ratios.{k3}.{n}.ratio', sig=3)
    m = j(AMD)
    for cv in ('320', '640'):
        xr(f'e9_insess_mde_{cv}', [v for k, v in m['in_session_mde_pct'].items() if k.startswith(cv)], f'{AMD}:in_session_mde_pct[{cv}|*]', d=2)
        xr(f'e9_ttot_{cv}', [v['t_total_clean_ms'] for k, v in m['cells'].items() if k.startswith(cv)], f'{AMD}:cells[{cv}|*].t_total_clean_ms', sig=3)
    ag = m['summary']['n_star_exact_agreement'].split('/')
    x('amd_nstar_agree', int(ag[0]), f'{AMD}:summary.n_star_exact_agreement[0]'); x('amd_nstar_cells', int(ag[1]), f'{AMD}:summary.n_star_exact_agreement[1]')
    x('amd_err_med', m['summary']['median_abs_log_err'], f'{AMD}:summary.median_abs_log_err', d=3)
    x('amd_ncells', m['summary']['n_cells'], f'{AMD}:summary.n_cells')
    x('amd_err_pct', 100 * m['summary']['median_abs_log_err'], f'{AMD}:100*summary.median_abs_log_err', d=1)
    x2 = j('x2_counts/summary_posthoc.json')['detectors']
    xr('x2_ratio', [v['ratio_mean'] for v in x2.values()], 'x2_counts/summary_posthoc.json:detectors[*].ratio_mean', d=3)
    xr('x2_patched', [v['patched_median'] for v in x2.values()], 'x2_counts/summary_posthoc.json:detectors[*].patched_median', d=1)
    # E12
    s12, x12 = j(E12), j(X12)
    g = x12['gate']['summary']
    x('e12_acc', g['accepted'], f'{X12}:gate.summary.accepted'); x('e12_att', g['attempts'], f'{X12}:gate.summary.attempts')
    x('e12_drift_pct', g['max_abs_accepted'] * 100, f'{X12}:gate.summary.max_abs_accepted*100', d=2)
    x('e12_eff', s12['pin']['effective_cores'], f'{E12}:pin.effective_cores', d=2)
    for arm in ('C1', 'C3', 'B1', 'B2', 'B3', 'B4', 'C2', 'C4'):
        for tau in ('0.01', '0.25'):
            nn = s12['arms'][arm][f'N_tau{tau}']
            x(f'e12_N{tau}_{arm}_clean', nn['clean_median'], f'{E12}:arms.{arm}.N_tau{tau}.clean_median', d=1)
            x(f'e12_N{tau}_{arm}_patched', nn['patched_median'], f'{E12}:arms.{arm}.N_tau{tau}.patched_median', d=1)
    tost = x12['P4_tost']
    x('e12_tost1_n', sum(v['0.01']['equivalent'] for v in tost.values()), f'{X12}:count(P4_tost[*].0.01.equivalent)')
    x('e12_tost_cells', len(tost), f'{X12}:P4_tost(len)')
    for be in ('tv_nms', 'torch_pure'):
        v = tost[f'B4|{be}']['0.01']
        x(f'e12_tost_B4_{be}_lo', v['ci90_ratio'][0], f'{X12}:P4_tost.B4|{be}.0.01.ci90_ratio[0]', d=4)
        x(f'e12_tost_B4_{be}_hi', v['ci90_ratio'][1], f'{X12}:P4_tost.B4|{be}.0.01.ci90_ratio[1]', d=4)
    tv = [v['0.01']['ci90_ratio'] for k, v in tost.items() if k != 'B4|torch_pure']
    x('e12_tost_ci_lo', min(c[0] for c in tv), f'{X12}:min(P4_tost[* except B4|torch_pure].0.01.ci90_ratio[0])', d=4)
    x('e12_tost_ci_hi', max(c[1] for c in tv), f'{X12}:max(P4_tost[* except B4|torch_pure].0.01.ci90_ratio[1])', d=4)
    cells = [(arm, be) for arm in s12['arms'] for be in ('torch_pure', 'tv_nms')]
    x('e12_h3_in', sum(s12['arms'][a][f'total_{b}']['amdahl_pred_inside_ci'] for a, b in cells), f'{E12}:count(arms[*].total_*.amdahl_pred_inside_ci)')
    x('e12_h3_n', len(cells), f'{E12}:arms[*].total_[torch_pure,tv_nms](count)')
    x('e12_exceed_n', sum(s12['arms'][a][f'total_{b}']['exceeds_in_session_mde'] for a, b in cells), f'{E12}:count(arms[*].total_*.exceeds_in_session_mde)')
    ga = [s12['arms'][a]['total_tv_nms']['ratio_mean'] for a in ('C1', 'C3', 'B1', 'B2', 'B3', 'C2', 'C4')]
    xr('e12_ga_tv', ga, f'{E12}:arms[C1,C3,B1,B2,B3,C2,C4].total_tv_nms.ratio_mean', d=4)
    ga_cells = [(a, b) for a in ('C1', 'C3', 'B1', 'B2', 'B3', 'C2', 'C4') for b in ('tv_nms', 'torch_pure')]
    x('e12_ga_cells', len(ga_cells), f'{E12}:arms[C1,C3,B1,B2,B3,C2,C4].total_[tv_nms,torch_pure](count)')
    x('e12_ga_excl1', sum(s12['arms'][a][f'total_{b}']['ratio_ci95'][0] > 1 for a, b in ga_cells), f'{E12}:count(arms[GA cells].total_*.ratio_ci95[0] > 1)')
    for a, b in cells:
        v = s12['arms'][a][f'total_{b}']
        if not v['amdahl_pred_inside_ci']:
            x(f'e12_h3_miss_{a}_{b}', 100 * (v['ratio_mean'] - v['amdahl_pred_mean']), f'{E12}:100*(arms.{a}.total_{b}.ratio_mean - amdahl_pred_mean)', d=2)
    b4 = s12['arms']['B4']
    for b, d in (('torch_pure', 1), ('tv_nms', 2)):
        x(f'e12_B4_{b}_pct', 100 * (b4[f'total_{b}']['ratio_mean'] - 1), f'{E12}:100*(arms.B4.total_{b}.ratio_mean-1)', d=d)
    x('e12_B4_nms_tv', b4['nms_tau0.01_tv_nms']['ratio_mean'], f'{E12}:arms.B4.nms_tau0.01_tv_nms.ratio_mean', d=3)
    x('e12_B4_share_tp', b4['total_torch_pure']['nms_share_clean_median'] * 100, f'{E12}:arms.B4.total_torch_pure.nms_share_clean_median*100', d=1)
    x('e12_B4_share_tv', b4['total_tv_nms']['nms_share_clean_median'] * 100, f'{E12}:arms.B4.total_tv_nms.nms_share_clean_median*100', d=2)
    # E10
    e = j(E10)
    x('e10_eff0', e['pin']['effective_cores'], f'{E10}:pin.effective_cores', d=2); x('e10_eff1', e['pin_end']['effective_cores'], f'{E10}:pin_end.effective_cores', d=2)
    x('e10_flag', e['drift']['flagged'], f'{E10}:drift.flagged'); x('e10_points', e['drift']['points'], f'{E10}:drift.points')
    x('e10_drift_pct', e['drift']['max_abs'] * 100, f'{E10}:drift.max_abs*100', d=1)
    for mth in ('overload', 'phantom_sponges'):
        for tau in ('0.01', '0.25'):
            nm = e['n_median'][f'{mth}|tau{tau}']
            x(f'e10_N{tau}_{mth}_clean', nm['clean'], f'{E10}:n_median.{mth}|tau{tau}.clean', d=1)
            x(f'e10_N{tau}_{mth}_patched', nm['patched'], f'{E10}:n_median.{mth}|tau{tau}.patched', d=1)
    ad = j(ADD)
    for mth in ('overload', 'phantom_sponges'):
        x(f'e10_rom_{mth}', ad['n_ratio'][f'{mth}|tau0.25']['ratio_of_medians'], f'{ADD}:n_ratio.{mth}|tau0.25.ratio_of_medians', sig=3)
    tr = e['total_ratio']
    xr('e10_tr', [v['mean'] for v in tr.values()], f'{E10}:total_ratio[*].mean', d=3)
    xr('e10_tr_pct', [100 * (v['mean'] - 1) for v in tr.values()], f'{E10}:100*(total_ratio[*].mean-1)', d=1)
    x('e10_ci_excl1', sum(v['ci95'][0] > 1 for v in tr.values()), f'{E10}:count(total_ratio[*].ci95[0] > 1)')
    x('e10_exceeds', sum(v['exceeds_in_session_mde'] for v in tr.values()), f'{E10}:count(total_ratio[*].exceeds_in_session_mde)')
    xr('e10_mde', list(e['in_session_mde_pct'].values()), f'{E10}:in_session_mde_pct[*]', d=2)
    x('e10_mde_1d', max(e['in_session_mde_pct'].values()), f'{E10}:max(in_session_mde_pct[*]) (one decimal)', d=1)
    sd = j(SM)
    lib = ('tv_nms', 'tv_batched', 'ultra_native')
    for grp in ('clean', 'attack'):
        sel = lambda k: (k.split('|')[0] == 'clean') == (grp == 'clean')  # noqa: E731
        xr(f'e10_nms_{grp}', [v['median'] for k, v in sd['nms_ms'].items() if sel(k) and k.split('|')[1] in lib], f'{SM}:nms_ms[{grp}|lib].median', sig=2)
        xr(f'e10_tot_{grp}', [v['median'] for k, v in sd['total_ms'].items() if sel(k)], f'{SM}:total_ms[{grp}|*].median', d=0)
    tp = {k.split('|')[0]: v['median'] for k, v in sd['nms_ms'].items() if k.endswith('|torch_pure')}
    x('e10_tp_clean', tp['clean'], f'{SM}:nms_ms.clean|torch_pure.median', d=2)
    x('e10_tp_overload', tp['overload'], f'{SM}:nms_ms.overload|torch_pure.median', d=0)
    x('e10_tp_phantom', tp['phantom_sponges'], f'{SM}:nms_ms.phantom_sponges|torch_pure.median', d=0)
    tc = sd['total_ms']['clean|tv_nms']['median']
    for mth in ('overload', 'phantom_sponges'):
        x(f'e10_tp_inferred_{mth}', 100 * (tp[mth] - tp['clean']) / tc, f'{SM}:100*(nms_ms.{mth}|torch_pure - nms_ms.clean|torch_pure)/total_ms.clean|tv_nms', d=0)
    cr = ad['criterion']
    xr('e10_dstar', [v['threshold_ms'] for v in cr.values()], f'{ADD}:criterion[*].threshold_ms', sig=2)
    xr('e10_dtot', [v['d_total_ms'] for v in cr.values()], f'{ADD}:criterion[*].d_total_ms', sig=2)
    xr('e10_dnms', [v['d_nms_ms'] for v in cr.values()], f'{ADD}:criterion[*].d_nms_ms', sig=2)
    x('e10_dtot_above', sum(v['d_total_above_threshold'] for v in cr.values()), f'{ADD}:count(criterion[*].d_total_above_threshold)')
    x('e10_dtot_ci0', sum(v['d_total_ci95'][0] > 0 for v in cr.values()), f'{ADD}:count(criterion[*].d_total_ci95[0] > 0)')
    dc = j(DC)['cells']
    xr('e10_rest', [v['d_rest_ms'] for v in dc.values()], f'{DC}:cells[*].d_rest_ms', sig=2)
    x('e10_rest_ci_pos', sum(v['d_rest_ci95'][0] > 0 for v in dc.values()), f'{DC}:count(cells[*].d_rest_ci95[0] > 0)')
    x('e10_rest_ci_neg', sum(v['d_rest_ci95'][1] < 0 for v in dc.values()), f'{DC}:count(cells[*].d_rest_ci95[1] < 0)')
    ph = j(PH)
    st = ph['structural_check']
    xr('e10_struct_err', [v['median_abs_log_err_struct'] for v in st.values()], f'{PH}:structural_check[*].median_abs_log_err_struct', d=3)
    xr('e10_share', [100 * v['nms_share_patched'] for v in st.values()], f'{PH}:structural_check[*].nms_share_patched*100', d=1)
    tost = ad['tost']
    att = {k: v for k, v in tost.items() if not k.startswith('A/A')}
    x('e10_tost5', sum(v['0.05']['equivalent'] for v in att.values()), f'{ADD}:count(tost[attack cells].0.05.equivalent)')
    x('e10_tost1', sum(v['0.01']['equivalent'] for v in att.values()), f'{ADD}:count(tost[attack cells].0.01.equivalent)')
    x('e10_tost_above1', sum(v['0.01']['above_margin'] for v in att.values()), f'{ADD}:count(tost[attack cells].0.01.above_margin)')
    x('e10_tost_cells', len(att), f'{ADD}:tost[attack cells](len)')
    md = ad['model']
    x('e10_null_pass', sum(v['null_passes'] for v in md.values()), f'{ADD}:count(model[*].null_passes)')
    x('e10_better', sum(v['skill_ci95'][0] > 0 for v in md.values()), f'{ADD}:count(model[*].skill_ci95[0] > 0)')
    xr('e10_skill', [v['skill'] for v in md.values()], f'{ADD}:model[*].skill', d=2)
    xr('e10_null_err', [v['null_median_abs_log_err'] for v in md.values()], f'{ADD}:model[*].null_median_abs_log_err', d=3)
    xr('e10_model_err', [v['model_median_abs_log_err'] for v in md.values()], f'{ADD}:model[*].model_median_abs_log_err', d=3)
    xr('e10_bias', [v['signed_log_bias'] for v in md.values()], f'{ADD}:model[*].signed_log_bias', d=3)
    npd = e['nms_predictor']
    xr('e10_interp', [v['interp_mixed_median_abs_log_err_N_ge_100'] for v in npd.values()], f'{E10}:nms_predictor[*].interp_mixed_median_abs_log_err_N_ge_100', d=2)
    xr('e10_MN', [v['median_abs_log_err_M_N'] for v in npd.values()], f'{E10}:nms_predictor[*].median_abs_log_err_M_N', d=2)
    for be in BE:
        v = npd[be]
        x(f'e10_delta_{be}', v['delta'], f'{E10}:nms_predictor.{be}.delta', d=2)
        x(f'e10_delta_{be}_lo', v['delta_ci95'][0], f'{E10}:nms_predictor.{be}.delta_ci95[0]', d=2)
        x(f'e10_delta_{be}_hi', v['delta_ci95'][1], f'{E10}:nms_predictor.{be}.delta_ci95[1]', d=2)
    # RQ4 on the patch session
    for be, v in ph['n_only_prediction_from_e1'].items():
        sel = f'{PH}:n_only_prediction_from_e1.{be}'
        x(f'nonly_{be}_med', v['median_abs_log_error_vs_mixed'], sel + '.median_abs_log_error_vs_mixed', d=2)
        x(f'nonly_{be}_p90', v['p90_abs_log_error'], sel + '.p90_abs_log_error', d=2)
        x(f'nonly_{be}_in', v['fraction_inside_envelope'], sel + '.fraction_inside_envelope', d=2)
        x('nonly_n', v['n_points'], sel + '.n_points')
    rho = ph['rho']
    xr('rho_between', [v for k, v in rho.items() if k.startswith('between_clean')], f'{PH}:rho.between_clean|*', d=2)
    xr('rho_dN', [v for k, v in rho.items() if k.startswith('dN_dt')], f'{PH}:rho.dN_dt|*', d=2)
    return write(t, None)


BUILDERS = [t_aa, t_dose, t_nc1, t_cap, t_nstar, t_amdahl, t_attacks, t_spec, t_nk, t_patches, t_threshold, t_x2, t_decomp, t_text]


def main():
    check = '--check' in sys.argv
    tabs = dict(b() for b in BUILDERS)
    hdr = '% GENERATED by paper_en/tables_q3/make_tables_en.py -- DO NOT EDIT.\n'
    bad = []
    for name, body in tabs.items():
        if body is None:
            continue
        p = OUT / f'{name}.tex'
        new = hdr + body
        if check:
            if not p.exists() or p.read_text(encoding='utf-8') != new:
                bad.append(name)
        else:
            p.write_text(new, encoding='utf-8')
    if '--text' in sys.argv:
        print(json.dumps(TXT, indent=0, ensure_ascii=False))
    if check:
        print('tables differing from a fresh build:', bad or 'none')
        sys.exit(1 if bad else 0)
    (OUT / 'numbers_en.json').write_text(json.dumps(REG, indent=1, ensure_ascii=False), encoding='utf-8')
    print('wrote', sum(1 for v in tabs.values() if v), 'tables,', sum(len(v) for v in REG.values()), 'numbers')


if __name__ == '__main__':
    main()
