"""Post-data audit/planning illustration, not the registered inference runner.

Reads the closed, failed smoke without modifying raw or summary. The sample-size
curve holds the SD observed on TWO images fixed: it is not measured at other n,
not a power guarantee, and not permission to run a cancelled full experiment.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math

import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).resolve().parent
R=B/'runs'/'smoke_01'/'pipeline_PI4'
raw=R/'raw.jsonl'
rows=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines()]
summary=json.loads((R.parent/'summary.json').read_text(encoding='utf-8'))['pipeline_PI4']
lock=json.loads((B/'registered_materials'/'lock.json').read_text(encoding='utf-8'))
by={}
for line,r in enumerate(rows,1):
    if r['kind']=='timing':
        by.setdefault(r['image'],{}).setdefault(r['arm'],[]).append((line,r['ns']))
per_image={}
for image,arms in by.items():
    med={a:float(np.median([v for _,v in x])) for a,x in arms.items()}
    per_image[image]=dict(median_ns=med,raw_lines={a:[line for line,_ in x] for a,x in arms.items()},
                         aa_log=math.log(med['clean_total_A']/med['clean_total_B']))
logs=[per_image[k]['aa_log'] for k in sorted(per_image)]
sd=float(np.std(logs,ddof=1))
mean=float(np.mean(logs))
def mde(n):
    return float((stats.t.ppf(.975,n-1)+stats.t.ppf(.8,n-1))*sd/np.sqrt(n))
assert len(logs)==2 and len([r for r in rows if r['kind']=='timing'])==24
assert math.isclose(sd,summary['aa_cleanA_over_cleanB']['sd'],rel_tol=1e-14)
assert math.isclose(mde(2),summary['mde_log_80pct'],rel_tol=1e-14)
assert not summary['quality_pass']
guards=[r for r in rows if r['kind']=='guard']
assert len(guards)==72 and all(not r['violations'] for r in guards)
curve=[dict(n=n,mde_log_if_sd_unchanged=mde(n),empirically_measured=(n==2)) for n in range(2,21)]
out=dict(status='POSTDATA_DIAGNOSTIC_AND_CONDITIONAL_PLANNING_ONLY',raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
         raw_line_count=len(rows),row_kind_counts=dict(Counter(r['kind'] for r in rows)),per_image=per_image,
         aa_mean_log=mean,aa_sd_log=sd,observed_mde_log=mde(2),mde_ratio=math.exp(mde(2)),
         threshold_log=lock['gates']['mde_log'],planning_curve=curve,
         planning_assumption='Same unknown SD as estimated from only two observed images; no guarantee at n20.',
         other_n_observed=False,all_guard_swap_zero=all(r['fast']['mem_kb']['SwapTotal']==0 and r['fast']['swaps']==[] for r in guards),
         min_fast_mem_available_kb=min(r['fast']['mem_kb']['MemAvailable'] for r in guards),
         max_fast_cpu_temp_c=max(r['fast']['temp_c'] for r in guards),
         pin_rows={r['kind']:dict(line=i,inside=r['inside'],outside=r['outside'],need=r['need'],busy=r['busy'],passed=r['passed']) for i,r in enumerate(rows,1) if r['kind'] in ('pin_start','pin_end')},
         reference_rows=[dict(line=i,block=r['block'],ratio=r['ratio'],flagged=r['flagged']) for i,r in enumerate(rows,1) if r['kind']=='reference'],
         candidate_count_rows=[dict(line=i,image=r['image'],counts=r['counts']) for i,r in enumerate(rows,1) if r['kind']=='counts'],
         summary_sha256=hashlib.sha256((R.parent/'summary.json').read_bytes()).hexdigest(),
         analysis_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
with (B/'closed_smoke_audit.json').open('x',encoding='utf-8') as f:
    json.dump(out,f,indent=2,allow_nan=False)

fig,axes=plt.subplots(1,3,figsize=(12,3.6))
refs=out['reference_rows']
axes[0].plot(range(len(refs)),[100*(r['ratio']-1) for r in refs],'o-',color='#23724d')
axes[0].axhline(3,color='gray',ls='--');axes[0].axhline(-3,color='gray',ls='--')
axes[0].set(xticks=range(len(refs)),xticklabels=[str(r['block']) for r in refs],ylabel='Reference change (%)',title='Observed: references pass')
axes[1].bar(range(len(logs)),[100*x for x in logs],color='#427ba6')
axes[1].set(xticks=range(len(logs)),xticklabels=[k.lstrip('0') or '0' for k in sorted(per_image)],xlabel='Image ID',ylabel='A/A log ratio × 100',title='Observed: only two image units')
axes[2].plot([r['n'] for r in curve],[r['mde_log_if_sd_unchanged'] for r in curve],color='#9c6531',ls='--',label='Planning: hold observed SD fixed')
axes[2].scatter([2],[mde(2)],color='#b63435',s=50,zorder=3,label='Observed smoke MDE')
axes[2].axhline(lock['gates']['mde_log'],color='black',ls=':',label='Registered full gate')
axes[2].set(xlabel='Assumed image count',ylabel='80%-power MDE (log ratio)',title='Other sample sizes are NOT measured',xticks=[2,5,10,15,20])
axes[2].legend(fontsize=7)
fig.suptitle('Pi smoke rejected for MDE; swap/pin/reference checks passed',fontsize=11)
fig.tight_layout()
for ext in ('png','pdf'):
    target=B/('smoke_quality_and_planning.'+ext)
    if target.exists():raise FileExistsError(target)
    fig.savefig(target,dpi=180)
print(json.dumps(dict(observed_mde=mde(2),assumed_mde_at20=mde(20),min_fast_mem_available_kb=out['min_fast_mem_available_kb'],max_fast_temp_c=out['max_fast_cpu_temp_c'],raw_lines=len(rows))))
