"""Consolidated Pi 3B (600 MHz) mechanism figure from qualified full20 raw. No new measurement.

Reads the frozen raw of the qualified campaign and draws the verified causal chain:
mask-building time is linear in retained-object count K; the attack inflates K; the
pre-NMS cap removes the inflation. Every number comes from raw.jsonl medians.
"""
import json
import statistics as st
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    'sponge-sim/results/pi3b_full20_20261114/runs/full_01')
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
    'sponge-sim/results/pi3b_full20_20261114/pi3b_mask_mechanism.png')


def rows(p):
    return [json.loads(l) for l in (RUN / p).read_text().splitlines() if l.strip()]


def medians(rs):
    t = {}
    for r in rs:
        if r.get('kind') == 'timing':
            t.setdefault(r['image'], {}).setdefault(r['arm'], []).append(r['ns'])
    return t


stage = rows('stages_PI4/raw.jsonl')
pipe = rows('pipeline_PI4/raw.jsonl')
ts, tp = medians(stage), medians(pipe)
counts = {r['image']: r['counts'] for r in stage if r.get('kind') == 'counts'}
imgs = sorted(ts)

K = [counts[im]['adv']['k'] for im in imgs]
mask_adv = [st.median(ts[im]['mask_adv']) / 1e6 for im in imgs]
mask_clean = [st.median(ts[im]['mask_clean']) / 1e6 for im in imgs]
Kc = [counts[im]['clean']['k'] for im in imgs]

dose = {}
for im in imgs:
    for arm, v in ts[im].items():
        if arm.startswith('maskdose_'):
            dose.setdefault(im, {})[int(arm.split('_')[1])] = st.median(v) / 1e6

# across-image linear fit mask_adv ~ K
n = len(K); sx = sum(K); sy = sum(mask_adv); sxx = sum(x * x for x in K); sxy = sum(x * y for x, y in zip(K, mask_adv))
slope = (n * sxy - sx * sy) / (n * sxx - sx * sx); icpt = (sy - slope * sx) / n

fig, ax = plt.subplots(1, 2, figsize=(11, 4.4), dpi=130)
fig.patch.set_facecolor('white')

# Left: within-image dose-response (controlled K sweep) + across-image points
axL = ax[0]
for im, d in dose.items():
    xs = sorted(d)
    axL.plot(xs, [d[k] for k in xs], '-o', ms=4, lw=1.3, alpha=.85, label=f'ảnh {im[-4:]}')
axL.scatter(K, mask_adv, c='#444', s=22, zorder=5, label='20 ảnh nhiễu (K thật)')
xx = [0, max(K)]
axL.plot(xx, [slope * x + icpt for x in xx], '--', c='crimson', lw=1.4,
         label=f'tuyến tính: {slope:.1f} ms/vật thể')
axL.set_xlabel('Số vật thể giữ lại K (sau NMS)')
axL.set_ylabel('Thời gian dựng mask (ms)')
axL.set_title('Chi phí mask tuyến tính theo K\nPi 3B @ 600 MHz, 4 luồng')
axL.legend(fontsize=7, ncol=2)
axL.grid(alpha=.25)

# Right: clean vs attacked vs capped mask time (bar) with K annotation
axR = ax[1]
clean_t = [st.median([*tp[im]['clean_total_A'], *tp[im]['clean_total_B']]) / 1e6 for im in imgs]
adv_t = [st.median(tp[im]['adv_total']) / 1e6 for im in imgs]
cap_t = [st.median(tp[im]['advcap_total']) / 1e6 for im in imgs]
vals = [st.median(clean_t), st.median(adv_t), st.median(cap_t)]
labels = [f'sạch\nK≈{int(st.median(Kc))}', f'nhiễu\nK≈{int(st.median(K))}',
          f'nhiễu+chặn\nK≈{int(st.median([counts[im]["advcap"]["k"] for im in imgs]))}']
bars = axR.bar(labels, vals, color=['#2e7d32', '#c62828', '#1565c0'], width=.6)
for b, v in zip(bars, vals):
    axR.text(b.get_x() + b.get_width() / 2, v + 40, f'{v/1000:.2f}s', ha='center', fontsize=9)
axR.set_ylabel('Thời gian toàn trình (ms), trung vị 20 ảnh')
fwd_share = st.median([(st.median(tp[im]['clean_forward']) / 1e6) / clean_t[i] for i, im in enumerate(imgs)])
axR.set_title('Toàn trình: nhiễu ×%.2f, chặn ×%.2f\n(forward chiếm ~%.0f%% thời gian ảnh sạch)' % (
    st.median(adv_t) / st.median(clean_t), st.median(cap_t) / st.median(adv_t), 100 * fwd_share))
axR.grid(alpha=.25, axis='y')

fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, facecolor='white')
print('written', OUT)
print('across-image slope %.3f ms/object intercept %.1f' % (slope, icpt))
print('within-image dose slopes', [round((lambda d: (len(d)*sum(k*d[k] for k in d)-sum(d)*sum(d.values()))/(len(d)*sum(k*k for k in d)-sum(d)**2))(d), 2) for d in dose.values()])
print('median ms clean/adv/cap', [round(v, 1) for v in vals])
