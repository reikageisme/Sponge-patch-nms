"""Saved-data diagnostics only: rejected component session, no device access."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parent
audit=json.loads((B/'independent_audit.json').read_text())
summary=json.loads((B/'runs/full_01/summary.json').read_text())['stages_PI4']
assert not summary['quality_pass']
fig,axes=plt.subplots(1,2,figsize=(11,4))
for ix,(im,arms) in enumerate(audit['sessions']['stages_PI4']['nms_samples_ms'].items(),1):
    for arm,offset,color in [('nms_adv',-.12,'#26729e'),('nms_adv_B',.12,'#ba503b')]:
        axes[0].scatter([ix+offset]*len(arms[arm]),arms[arm],color=color,s=13,alpha=.7,
                        label=arm if ix==1 else None)
index77=list(audit['sessions']['stages_PI4']['nms_samples_ms']).index('000000000077')+1
axes[0].set(xlabel=f'Frozen image index ({index77} = image 77)',ylabel='NMS wrapper wall time (ms)',title='All attacked NMS A/B calls; no filtering')
axes[0].legend(fontsize=8)
for im,dose in summary['mask_dose_ms'].items():
    keys=sorted(dose,key=int)
    axes[1].plot([int(k) for k in keys],[dose[k] for k in keys],'o-',label='Image '+str(int(im)))
axes[1].set(xlabel='Available retained mask count K',ylabel='Median mask time (ms)',title='Five planned images; available K only')
axes[1].legend(fontsize=8)
fig.suptitle('Diagnostic only: joint component gate FAIL; no complexity or qualified latency claim',fontsize=10)
fig.tight_layout()
for ext in ('png','pdf'):
    dest=B/('component_diagnostics_corrected.'+ext)
    if dest.exists():raise FileExistsError(dest)
    fig.savefig(dest,dpi=180)
