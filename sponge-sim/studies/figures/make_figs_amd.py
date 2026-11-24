"""Figures of paper_en/main.tex from the AMD frequency-locked replication (PREREG_AMD_REPLICATION_20261124, session full-01).
Read-only on results; no number is drawn that is not in a saved summary or raw record of that session.

    python make_figs_amd.py OUT_DIR

fig2_dose_response    : NMS latency against N (E1, 10 000-anchor grid, 80 classes, no cap); as make_figs.py, AMD summary.
fig3_pred_vs_measured : measured NMS of real candidate sets (E12 micro records, tau 0.01, 320-px arms) against the
                        N-only prediction from the E1 mixed curve (2100 anchors), as make_figs.py.
fig4_pipeline_nstar   : end-to-end ratio under full-pipeline injection (E9 part A), as make_figs_v3.py.
fig6_patch_effects    : N, NMS stage and MEASURED end-to-end ratios of the 320-px patch arms (E12), with the in-session MDE.
fig9_attacks          : whole-image attack variants (E10), as make_figs_review.py.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import NullFormatter, ScalarFormatter

SIM = Path(__file__).resolve().parents[2]
F = SIM / 'results/amd_20261124/full-01'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 9})
rd = lambda p: json.loads((F / p).read_text(encoding='utf-8'))  # noqa: E731
PROF = 'P1_cpu2'
BE = [('torch_pure', 'Pure PyTorch'), ('tv_nms', 'torchvision nms'), ('tv_batched', 'torchvision batched'), ('ultra_native', 'Ultralytics native')]
GEOM = [('disjoint', 'disjoint'), ('dense_cluster', 'dense cluster'), ('mixed', 'mixed')]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=200)
    plt.close(fig)


curves = rd('e1/run/summary.json')['curves']


def curve(A, be, g, nc=80):
    pts = {}
    for k, v in curves.items():
        p, a, b, gg, c, cp, n = k.split('|')
        if p == PROF and int(a) == A and b == be and gg == g and int(c) == nc and cp == 'None':
            pts[int(n)] = v
    ns = sorted(n for n in pts if n > 0)
    return (np.array(ns), np.array([pts[n]['median_ms'] for n in ns]),
            np.array([pts[n]['ci95'][0] for n in ns]), np.array([pts[n]['ci95'][1] for n in ns]))


# ---- fig2
fig, ax = plt.subplots(1, 4, figsize=(11, 2.8), sharex=True)
for a, (be, lab) in zip(ax, BE):
    for g, gl in GEOM:
        ns, m, lo, hi = curve(10000, be, g)
        a.plot(ns, m, marker='o', ms=3, label=gl)
        a.fill_between(ns, lo, hi, alpha=.2)
    a.set_xscale('log'); a.set_yscale('log'); a.set_title(lab, fontsize=9); a.set_xlabel(r'$N_\tau$')
ax[0].set_ylabel('NMS latency (ms)'); ax[0].legend(fontsize=7)
save(fig, 'fig2_dose_response')

# ---- fig3 (E12 micro, tau 0.01, 320-px arms)
A320 = ('clean_a', 'clean_b', 'C1', 'C3', 'B1', 'B2', 'B3', 'B4')
micro, nmap = defaultdict(list), {}
with open(F / 'e12/run/raw_P1_cpu2.jsonl', encoding='utf-8') as fh:
    for line in fh:
        if '"micro"' not in line[:20]:
            continue
        r = json.loads(line)
        if r['tau'] == 0.01 and r['arm'] in A320:
            micro[(r['image_id'], r['arm'], r['seed'], r['backend'])].append(r['nms_ns'] / 1e6)
            nmap[(r['image_id'], r['arm'], r['seed'])] = r['nms_input']


def predict(ns, ms, n):
    return float(np.exp(np.interp(np.log(n), np.log(ns), np.log(ms))))


fig, ax = plt.subplots(1, 4, figsize=(11, 2.9))
for a, (be, lab) in zip(ax, BE):
    ns, m, _, _ = curve(2100, be, 'mixed')
    for grp, col in (('clean', 'tab:blue'), ('patched', 'tab:red')):
        xs, ys = [], []
        for (i, arm, s, b), v in micro.items():
            if b != be or arm.startswith('clean') != (grp == 'clean'):
                continue
            n = nmap[(i, arm, s)]
            if n <= 0:
                continue
            xs.append(predict(ns, m, n)); ys.append(float(np.median(v)))
        a.scatter(xs, ys, s=3, alpha=.25, c=col, label=grp)
    lim = [min(a.get_xlim()[0], a.get_ylim()[0]), max(a.get_xlim()[1], a.get_ylim()[1])]
    a.plot(lim, lim, 'k--', lw=.8); a.set_xscale('log'); a.set_yscale('log')
    a.set_title(lab, fontsize=9); a.set_xlabel(r'predicted from $N_\tau$ (ms)')
    a.xaxis.set_minor_formatter(NullFormatter()); a.yaxis.set_minor_formatter(NullFormatter())
ax[0].set_ylabel('measured NMS (ms)'); ax[0].legend(fontsize=7, markerscale=3)
save(fig, 'fig3_pred_vs_measured')

# ---- fig4 (E9 part A)
a9 = rd('e9/run/summary_part_a.json')
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
for k, cv in enumerate((320, 640)):
    mde = a9['mde_total_pct'][str(cv)]
    for be, lab in BE:
        s = a9['ratios'][f'{cv}|{be}|disjoint|capNone']
        ns = sorted(int(n) for n in s)
        ax[k].plot(ns, [s[str(n)]['ratio'] for n in ns], marker='o', ms=3, label=lab)
        ax[k].fill_between(ns, [s[str(n)]['ci95'][0] for n in ns], [s[str(n)]['ci95'][1] for n in ns], alpha=.2)
    ax[k].axhline(1 + mde / 100, color='k', ls='--', lw=.8, label=f'1 + MDE ({mde:.2g}%)')
    ax[k].set_xscale('log'); ax[k].set_yscale('log')
    ax[k].set_xticks(ns); ax[k].set_xticklabels([str(n) for n in ns])
    ax[k].xaxis.set_minor_formatter(NullFormatter())
    ax[k].set_yticks([1, 1.5, 2, 3, 5, 7] if cv == 320 else [1, 1.5, 2, 3, 5, 10])
    ax[k].yaxis.set_major_formatter(ScalarFormatter()); ax[k].yaxis.set_minor_formatter(NullFormatter())
    ax[k].set_xlabel(r'injected $N_\tau$'); ax[k].set_title(f'{cv} px, disjoint boxes, no cap')
ax[0].set_ylabel('end-to-end latency ratio vs. $N_\\tau=0$')
ax[0].legend(fontsize=6)
ax[1].legend(handles=ax[1].get_lines()[-1:], fontsize=6)
save(fig, 'fig4_pipeline_nstar')

# ---- fig6 (E12, 320 px, measured end-to-end)
e12 = rd('e12/run/summary.json')
arms = [('C1', r'SG-GA, $\tau_{\mathrm{obj}}=0.01$'), ('C3', r'SG-GA, $\tau_{\mathrm{obj}}=0.25$'), ('B1', 'GA, centre'),
        ('B2', 'GA, random place'), ('B3', 'random search'), ('B4', 'gradient ascent')]
mde = max(e12['in_session']['320'][be]['mde_total_pct'] for be in ('tv_nms', 'torch_pure'))
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=True)
panels = (('N_tau0.01', r'$N_\tau$ ($\tau=0.01$)'), ('nms_tau0.01_tv_nms', 'NMS stage (torchvision)'), ('total', 'end-to-end, measured'))
for k, (key, title) in enumerate(panels):
    for i, (arm, lab) in enumerate(arms):
        col = 'tab:red' if arm == 'B4' else 'tab:blue'
        series = (('total_tv_nms', 'o', -.2), ('total_torch_pure', 's', .2)) if key == 'total' else ((key, 'o', 0),)
        for kk, mk, dy in series:
            v = e12['arms'][arm][kk]
            r, (lo, hi) = v['ratio_mean'], v['ratio_ci95']
            ax[k].errorbar(r, i + dy, xerr=[[r - lo], [hi - r]], fmt=mk, ms=3.5, capsize=2, lw=1, color=col, mfc=col if mk == 'o' else 'white')
    ax[k].axvline(1, color='k', lw=.8)
    if key == 'total':
        ax[k].axvspan(1 - mde / 100, 1 + mde / 100, color='grey', alpha=.25)
        ax[k].legend(handles=[Line2D([], [], marker='o', ls='', color='k', ms=3.5, label='torchvision nms'),
                              Line2D([], [], marker='s', ls='', color='k', mfc='white', ms=3.5, label='pure PyTorch'),
                              Patch(color='grey', alpha=.25, label=r'$\pm$ in-session MDE')], fontsize=6, loc='center right')
    ax[k].set_title(title, fontsize=8)
    ax[k].set_xlabel('patched / clean')
ax[0].set_yticks(range(len(arms)))
ax[0].set_yticklabels([lab for _, lab in arms])
ax[0].set_ylim(len(arms) - .5, -.5)
save(fig, 'fig6_patch_effects')

# ---- fig9 (E10)
e10 = rd('analysis/e10_summary.json')
add = rd('analysis/e10_addon.json')
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw=dict(width_ratios=[1, 2.2]))
meths = [('overload', 'Overload variant'), ('phantom_sponges', 'Phantom Sponges variant')]
cols = ('tab:blue', 'tab:orange')
for i, (m, lab) in enumerate(meths):
    v = e10['n_ratio'][f'{m}|tau0.25']
    ax[0].errorbar(i - .12, v['mean'], yerr=[[v['mean'] - v['ci95'][0]], [v['ci95'][1] - v['mean']]], fmt='o', ms=4, capsize=3, color=cols[i])
    ax[0].plot(i + .12, add['n_ratio'][f'{m}|tau0.25']['ratio_of_medians'], 'D', ms=4, color=cols[i], mfc='white')
ax[0].set_yscale('log')
ax[0].set_xticks([0, 1]); ax[0].set_xticklabels(['Overload', 'Phantom\nSponges'], fontsize=7); ax[0].set_xlim(-.5, 1.5)
ax[0].set_ylabel(r'$N_\tau$ ratio, attacked / clean'); ax[0].set_title(r'candidates ($\tau=0.25$)')
ax[0].legend(handles=[Line2D([], [], marker='o', ls='', color='k', ms=4, label='mean of ratios (95% CI)'),
                      Line2D([], [], marker='D', ls='', color='k', mfc='white', ms=4, label='ratio of medians')], fontsize=6, loc='upper center')
ax[0].set_ylim(60, 3000)
pbe = [('tv_nms', 'torchvision nms'), ('tv_batched', 'torchvision batched'), ('ultra_native', 'Ultralytics native')]
mde = max(e10['in_session_mde_pct'].values())
ax[1].axhspan(1, 1 + mde / 100, color='grey', alpha=.25)
ax[1].axhline(1, color='k', lw=.8)
for j, (m, lab) in enumerate(meths):
    for k, (be, bl) in enumerate(pbe):
        x = k + (j - .5) * .44
        t = e10['total_ratio'][f'{m}|{be}']
        ax[1].errorbar(x - .06, t['mean'], yerr=[[t['mean'] - t['ci95'][0]], [t['ci95'][1] - t['mean']]], fmt='o', ms=4, capsize=2, color=cols[j])
        ax[1].plot(x + .06, e10['amdahl'][f'{m}|{be}']['r_pred_mean'], 'x', color=cols[j], ms=6, mew=1.5)
ax[1].set_xticks(range(3)); ax[1].set_xticklabels([b for _, b in pbe], fontsize=7)
ax[1].set_ylim(0.985, 1.125)
ax[1].set_ylabel('end-to-end ratio, attacked / clean'); ax[1].set_title('end-to-end latency')
ax[1].legend(handles=[Line2D([], [], marker='o', ls='', color=cols[0], ms=4, label='Overload, measured (95% CI)'),
                      Line2D([], [], marker='o', ls='', color=cols[1], ms=4, label='Phantom Sponges, measured (95% CI)'),
                      Line2D([], [], marker='x', ls='', color='k', ms=6, mew=1.5, label='budget estimate'),
                      Patch(color='grey', alpha=.25, label='in-session MDE')], fontsize=6, loc='upper center', ncol=2)
save(fig, 'fig9_attacks')
print('fig2, fig3, fig4, fig6, fig9 drawn from', F)
