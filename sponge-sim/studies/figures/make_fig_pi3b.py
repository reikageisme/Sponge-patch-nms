"""Figure for the Raspberry Pi 3B cross-check, drawn from the saved raw records (read-only).

    python make_fig_pi3b.py OUT_DIR

fig10_pi3b : per-image median end-to-end time (clean / attacked / attacked with a 300-candidate cap) for the
             two qualified sessions, and the per-image attacked/clean ratio against the retained count.

Sources (not modified):
  results/pi3b_full20_20261114/runs/full_01/pipeline_PI4/raw.jsonl      four threads, no USB device
  results/pi3b_pi1_ssd_20261115/runs/full_01/pipeline_PI1/raw.jsonl     one thread, idle USB SSD attached
Per-image medians follow studies/pi3b_pi1_ssd_600mhz_20261115/analyze.py: the clean time pools the two
clean labels (A and B); every other arm is the median of its own repetitions. The script recomputes the
registered geometric-mean ratios and stops if they differ from the saved summary.json.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SIM = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 9})

RUNS = [
    ('Four threads, no USB device', 'results/pi3b_full20_20261114/runs/full_01', 'pipeline_PI4'),
    ('One thread, idle USB SSD', 'results/pi3b_pi1_ssd_20261115/runs/full_01', 'pipeline_PI1'),
]


def load(run, profile):
    acc, counts = defaultdict(lambda: defaultdict(list)), {}
    with open(SIM / run / profile / 'raw.jsonl', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r['kind'] == 'timing':
                acc[r['image']][r['arm']].append(int(r['ns']))
            elif r['kind'] == 'counts':
                counts[r['image']] = r['counts']
    images = sorted(acc)
    clean = {im: float(np.median(acc[im]['clean_total_A'] + acc[im]['clean_total_B'])) for im in images}
    adv = {im: float(np.median(acc[im]['adv_total'])) for im in images}
    cap = {im: float(np.median(acc[im]['advcap_total'])) for im in images}
    summ = json.loads((SIM / run / 'summary.json').read_text(encoding='utf-8'))[profile]
    g = lambda a, b: float(np.exp(np.mean([np.log(a[im] / b[im]) for im in images])))
    assert abs(g(adv, clean) - summ['h1_adv_over_clean']['geomean_ratio']) < 1e-9, (g(adv, clean), profile)
    assert abs(g(cap, adv) - summ['h2_advcap_over_adv']['geomean_ratio']) < 1e-9, (g(cap, adv), profile)
    assert summ['quality_pass'] is True
    k = {im: counts[im]['adv']['k'] for im in images}
    return images, clean, adv, cap, k, g(adv, clean)


data = [(lab,) + load(run, prof) for lab, run, prof in RUNS]
assert data[0][1] == data[1][1], 'the two sessions must use the same 20 images'
order = sorted(data[0][1], key=lambda im: (data[0][5][im], im))

fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5), gridspec_kw={'width_ratios': [1, 1, 0.9]})
x = np.arange(1, len(order) + 1)
for j, (lab, images, clean, adv, cap, k, geo) in enumerate(data):
    ax[j].plot(x, [clean[im] / 1e9 for im in order], marker='o', ms=3, lw=.8, color='C0', label='clean')
    ax[j].plot(x, [adv[im] / 1e9 for im in order], marker='s', ms=3, lw=.8, color='C3', label='attacked')
    ax[j].plot(x, [cap[im] / 1e9 for im in order], marker='^', ms=3, lw=.8, color='C2', label='attacked, cap 300')
    ax[j].set_title(lab)
    ax[j].set_xlabel('image, ordered by retained count')
    ax[j].set_xticks([1, 5, 10, 15, 20])
    ax[j].set_ylim(bottom=0)
ax[0].set_ylabel('median end-to-end time (s)')
ax[0].legend(fontsize=6, loc='lower right')
for (lab, images, clean, adv, cap, k, geo), mk, col in zip(data, ('o', 'D'), ('C1', 'C4')):
    ax[2].scatter([k[im] for im in images], [adv[im] / clean[im] for im in images], s=12, marker=mk, color=col,
                  label=lab.split(',')[0].lower(), zorder=3)
ax[2].axhline(1, color='k', ls='--', lw=.8)
ax[2].set_xlabel('retained detections under attack')
ax[2].set_ylabel('attacked / clean time ratio')
ax[2].set_title('per-image ratio')
ax[2].set_ylim(bottom=0.9)
ax[2].legend(fontsize=6, loc='upper left')
fig.tight_layout()
fig.savefig(OUT / 'fig10_pi3b.pdf')
fig.savefig(OUT / 'fig10_pi3b.png', dpi=200)
for lab, images, clean, adv, cap, k, geo in data:
    r = [adv[im] / clean[im] for im in images]
    print(f'{lab}: n={len(images)} geomean adv/clean={geo:.6f} per-image ratio min={min(r):.3f} max={max(r):.3f} '
          f'K under attack min={min(k.values())} max={max(k.values())}')
