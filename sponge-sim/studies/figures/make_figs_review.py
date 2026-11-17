"""Redraw of two figures after the supervisor review of 16/11/2026 (read-only on results).

    python make_figs_review.py OUT_DIR

fig6_patch_effects : same data as make_figs_v3.py:75-104 (copied), with a legend instead of symbols in the title,
                     wider separation of the two predicted markers and math-mode condition labels.
fig9_attacks       : same data as make_figs_v3.py:141-162 (copied); the model prediction is drawn beside the
                     measurement instead of on top of it, and the candidate panel shows both the mean of the
                     per-image ratios and the ratio of medians (results/review_20261117/e10_addon.json).
No number is computed here that is not already in the saved summaries.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

SIM = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 9})
rd = lambda p: json.loads((SIM / p).read_text(encoding='utf-8'))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=200)
    plt.close(fig)


# ---- fig6: patch effects at 320 px
e6 = rd('results/e6/E6_P1cpu2_20261102/summary.json')
_pool = rd('results/e6/E6_pooled_baselines_100img/summary.json')['arms']
for _a in ('B1', 'B2', 'B3', 'B4'):
    e6['arms'][_a] = _pool[_a]
_thr = rd('results/amdahl/threshold_check_posthoc.json')['arms']
for _a in ('C1', 'C3', 'B1', 'B2', 'B3', 'B4'):
    for _be in ('tv_nms', 'torch_pure'):
        _v = _thr[f'320|{_a}|{_be}']
        e6['arms'][_a][f'pred_{_be}'] = dict(ratio_mean=_v['r_pred'], ratio_ci95=_v['r_pred_ci95'])
arms = [('C1', r'SG-GA, $\tau_{\mathrm{obj}}=0.01$'), ('C3', r'SG-GA, $\tau_{\mathrm{obj}}=0.25$'), ('B1', 'GA, centre'),
        ('B2', 'GA, random place'), ('B3', 'random search'), ('B4', 'gradient ascent')]
mde_total = e6['mde_aa_pct']['total']
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=True)
panels = (('N_tau0.01', r'$N_\tau$ ($\tau=0.01$), measured'), ('nms_tau0.01_tv_nms', 'NMS stage (torchvision), measured'),
          ('pred', 'end-to-end, budget estimate'))
for k, (key, title) in enumerate(panels):
    for i, (arm, lab) in enumerate(arms):
        col = 'tab:red' if arm == 'B4' else 'tab:blue'
        series = (('pred_tv_nms', 'o', -.2), ('pred_torch_pure', 's', .2)) if key == 'pred' else ((key, 'o', 0),)
        for kk, mk, dy in series:
            v = e6['arms'][arm][kk]
            r, (lo, hi) = v['ratio_mean'], v['ratio_ci95']
            ax[k].errorbar(r, i + dy, xerr=[[r - lo], [hi - r]], fmt=mk, ms=3.5, capsize=2, lw=1, color=col,
                           mfc=col if mk == 'o' else 'white')
    ax[k].axvline(1, color='k', lw=.8)
    if key == 'pred':
        ax[k].axvspan(1 - mde_total / 100, 1 + mde_total / 100, color='grey', alpha=.25)
        ax[k].legend(handles=[Line2D([], [], marker='o', ls='', color='k', ms=3.5, label='torchvision nms'),
                              Line2D([], [], marker='s', ls='', color='k', mfc='white', ms=3.5, label='pure PyTorch'),
                              Patch(color='grey', alpha=.25, label=r'$\pm$ A/A MDE')], fontsize=6, loc='center right')
    ax[k].set_title(title, fontsize=8)
    ax[k].set_xlabel('patched / clean')
ax[0].set_yticks(range(len(arms)))
ax[0].set_yticklabels([l for _, l in arms])
ax[0].set_ylim(len(arms) - .5, -.5)
save(fig, 'fig6_patch_effects')

# ---- fig9: whole-image attack variants
e10 = rd('results/e10/E10_P1cpu2_20261102/summary.json')
add = rd('results/review_20261117/e10_addon.json')
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw=dict(width_ratios=[1, 2.2]))
meths = [('overload', 'Overload variant'), ('phantom_sponges', 'Phantom Sponges variant')]
cols = ('tab:blue', 'tab:orange')
for i, (m, lab) in enumerate(meths):
    v = e10['n_ratio'][f'{m}|tau0.25']
    ax[0].errorbar(i - .12, v['mean'], yerr=[[v['mean'] - v['ci95'][0]], [v['ci95'][1] - v['mean']]], fmt='o', ms=4, capsize=3, color=cols[i])
    ax[0].plot(i + .12, add['n_ratio'][f'{m}|tau0.25']['ratio_of_medians'], 'D', ms=4, color=cols[i], mfc='white')
ax[0].set_yscale('log')
ax[0].set_xticks([0, 1])
ax[0].set_xticklabels(['Overload', 'Phantom\nSponges'], fontsize=7)
ax[0].set_xlim(-.5, 1.5)
ax[0].set_ylabel(r'$N_\tau$ ratio, attacked / clean')
ax[0].set_title(r'candidates ($\tau=0.25$)')
ax[0].legend(handles=[Line2D([], [], marker='o', ls='', color='k', ms=4, label='mean of ratios (95% CI)'),
                      Line2D([], [], marker='D', ls='', color='k', mfc='white', ms=4, label='ratio of medians')], fontsize=6, loc='upper center')
ax[0].set_ylim(80, 3000)
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
ax[1].set_xticks(range(3))
ax[1].set_xticklabels([b for _, b in pbe], fontsize=7)
ax[1].set_ylim(0.995, 1.125)
ax[1].set_ylabel('end-to-end ratio, attacked / clean')
ax[1].set_title('end-to-end latency')
ax[1].legend(handles=[Line2D([], [], marker='o', ls='', color=cols[0], ms=4, label='Overload, measured (95% CI)'),
                      Line2D([], [], marker='o', ls='', color=cols[1], ms=4, label='Phantom Sponges, measured (95% CI)'),
                      Line2D([], [], marker='x', ls='', color='k', ms=6, mew=1.5, label='budget estimate'),
                      Patch(color='grey', alpha=.25, label='in-session MDE')], fontsize=6, loc='upper center', ncol=2)
save(fig, 'fig9_attacks')
print('fig6, fig9 redrawn')
