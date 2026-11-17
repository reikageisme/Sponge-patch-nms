"""Independent post-data arithmetic/row map; no inference or device access.

Registered analysis remains immutable. This audit enumerates sign flips using
bit matrices and uses scipy directly, rather than importing its frozen helpers.
"""
from pathlib import Path
from collections import Counter
from statistics import median
import hashlib
import json
import math
import random
import numpy as np
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).resolve().parent
C=B/'runs/full_01'
summary=json.loads((C/'summary.json').read_text())
lock=json.loads((B/'registered_materials/lock.json').read_text())
names=[Path(p).name.split('_')[0] for p in lock['inputs']]
assert len(names)==20

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,allow_nan=False)

def mde(x):
    return float((t.ppf(.975,len(x)-1)+t.ppf(.8,len(x)-1))*np.std(x,ddof=1)/np.sqrt(len(x)))

def inference(logs,seed,registered):
    x=np.array(logs);n=len(x)
    draws=np.random.default_rng(seed).integers(0,n,(20000,n))
    ci=np.quantile(x[draws].mean(axis=1),[.025,.975])
    hits=0
    for start in range(0,2**n,65536):
        bits=(np.arange(start,min(start+65536,2**n),dtype=np.uint32)[:,None]>>np.arange(n))&1
        vals=((bits.astype(np.float64)*2-1)*x).mean(axis=1)
        hits+=int(np.count_nonzero(np.abs(vals)>=abs(x.mean())-1e-12))
    r=dict(n=n,mean=float(x.mean()),sd=float(x.std(ddof=1)),ci95=ci.tolist(),p_sign_flip=hits/2**n,
           dz=float(x.mean()/x.std(ddof=1)),geomean_ratio=math.exp(x.mean()),ratio_ci95=np.exp(ci).tolist())
    for k,v in r.items():assert np.allclose(v,registered[k],rtol=1e-12,atol=1e-14),(k,v,registered[k])
    return r

out=dict(status='INDEPENDENT_RAW_SCHEDULE_ARITHMETIC_VERIFIED',sessions={},summary_sha256=sha(C/'summary.json'))
maps={}
for session in ('pipeline_PI4','stages_PI4'):
    d=C/session;raw=d/'raw.jsonl';rows=[json.loads(x) for x in raw.read_text().splitlines()]
    timing=[r for r in rows if r['kind']=='timing']
    cnt={r['image']:r['counts'] for r in rows if r['kind']=='counts'}
    assert list(cnt)==names
    med={};sources={}
    for line,r in enumerate(rows,1):
        if r['kind']=='timing':sources.setdefault(r['image'],{}).setdefault(r['arm'],[]).append(dict(line=line,ns=r['ns'],process_cpu_ns=r['process_cpu_ns'],rep=r['rep'],position=r['position']))
    for im,arms in sources.items():med[im]={a:median(v['ns'] for v in vals) for a,vals in arms.items()}
    expected=[]
    pipeline=session.startswith('pipeline')
    for ix,im in enumerate(names):
        arms=['clean_total_A','clean_total_B','adv_total','advcap_total','clean_forward','adv_forward'] if pipeline else ['nms_clean','nms_adv','mask_clean','mask_adv','nms_adv_B','mask_adv_B']
        if not pipeline and ix<5:arms += ['maskdose_'+str(k) for k in lock['dose_levels'] if k<=cnt[im]['adv']['k']]
        for rep in range(6 if pipeline else 5):
            order=list(range(len(arms)));random.Random(lock['seed']+1000*ix+rep).shuffle(order)
            expected += [(im,ix,arms[j],rep,pos) for pos,j in enumerate(order)]
    assert [(r['image'],r['block'],r['arm'],r['rep'],r['position']) for r in timing]==expected
    refs=[dict(line=i,**r) for i,r in enumerate(rows,1) if r['kind']=='reference']
    assert [r['block'] for r in refs]==['start',*range(20),'end']
    for r in refs:
        ratio=median(r['samples_ns'])/median(refs[0]['samples_ns'])
        assert math.isclose(r['ratio'],ratio,rel_tol=1e-14) and r['flagged']==(abs(ratio-1)>.03)
    guards=[r for r in rows if r['kind']=='guard']
    assert len(guards)==2*(len(timing)+22*3)
    assert all(not r['violations'] and r['fast']['mem_kb']['SwapTotal']==0 and r['fast']['swaps']==[] and all(r['fast']['masks'].values()) for r in guards)
    assert rows[-1]['kind']=='done'
    s=dict(raw_sha256=sha(raw),raw_lines=len(rows),row_kinds=dict(Counter(r['kind'] for r in rows)),n_timings=len(timing),
           min_fast_mem_available_kb=min(r['fast']['mem_kb']['MemAvailable'] for r in guards),
           max_fast_temp_c=max(r['fast']['temp_c'] for r in guards),
           sampled_block_rss_bytes=[r['info']['rss'] for r in rows if r['kind']=='memory'],
           sampled_block_rss_is_peak=False,refs=refs,
           pins=[dict(line=i,**r) for i,r in enumerate(rows,1) if r['kind'] in ('pin_start','pin_end')],
           counts=cnt,per_image_medians_ns=med,inference={})
    for p in s['pins']:assert math.isclose(sum(p['busy']),p['inside'],abs_tol=1e-12) and p['inside']>=2.8
    if pipeline:
        clean={im:median([v['ns'] for a in ('clean_total_A','clean_total_B') for v in sources[im][a]]) for im in names}
        endpoints=[('h1_adv_over_clean','adv_total',None,20261115),('h2_advcap_over_adv','advcap_total','adv_total',20261116),
                   ('aa_cleanA_over_cleanB','clean_total_A','clean_total_B',20261117),('advcap_over_clean','advcap_total',None,20261118),
                   ('forward_adv_over_clean','adv_forward','clean_forward',20261119)]
        for key,a,b,seed in endpoints:
            logs=[math.log(med[im][a]/(clean[im] if b is None else med[im][b])) for im in sorted(names)]
            s['inference'][key]=inference(logs,seed,summary[session][key])
            if key.startswith('aa_'):
                s['aa_mde_log']=mde(logs);assert math.isclose(s['aa_mde_log'],summary[session]['mde_log_80pct'],rel_tol=1e-14)
        ps=[s['inference'][k]['p_sign_flip'] for k in ('h1_adv_over_clean','h2_advcap_over_adv')]
        order=np.argsort(ps);adj=[0.,0.];prev=0
        for rank,i in enumerate(order):prev=max(prev,min(1.,(2-rank)*ps[i]));adj[i]=prev
        assert adj==summary[session]['holm_h1_h2'];s['holm_h1_h2']=adj
        shares={a:float(np.median([med[im][a+'_forward']/(clean[im] if a=='clean' else med[im]['adv_total']) for im in names])) for a in ('clean','adv')}
        assert shares==summary[session]['forward_share'];s['forward_share']=shares
    else:
        controls={}
        for stage,seed in (('mask',20261120),('nms',20261121)):
            logs=[math.log(med[im][stage+'_adv']/med[im][stage+'_clean']) for im in sorted(names)]
            key=stage+'_adv_over_clean';s['inference'][key]=inference(logs,seed,summary[session][key])
            aa={im:math.log(med[im][stage+'_adv']/med[im][stage+'_adv_B']) for im in names}
            controls[stage]=dict(mean_log=float(np.mean(list(aa.values()))),mde_log_80pct=mde(list(aa.values())),per_image_aa_log=aa)
            for k in ('mean_log','mde_log_80pct'):assert math.isclose(controls[stage][k],summary[session]['stage_controls'][stage][k],rel_tol=1e-13)
        s['controls']=controls
        s['nms_samples_ms']={im:{a:[v['ns']/1e6 for v in sources[im][a]] for a in ('nms_adv','nms_adv_B')} for im in names}
    maps[session]=dict(raw_sha256=sha(raw),timing_lines_by_image_arm=sources,
                       count_rows=[dict(line=i,image=r['image']) for i,r in enumerate(rows,1) if r['kind']=='counts'],
                       memory_rows=[dict(line=i,image=r['image']) for i,r in enumerate(rows,1) if r['kind']=='memory'],
                       references=[r['line'] for r in refs],pins=[p['line'] for p in s['pins']],done_line=len(rows))
    out['sessions'][session]=s
assert out['sessions']['pipeline_PI4']['counts']==out['sessions']['stages_PI4']['counts']
assert summary['pipeline_PI4']['quality_pass'] and not summary['stages_PI4']['quality_pass'] and summary['pipeline_PI1']['missing']
assert json.loads((C/'restore.json').read_text())['status']=='RESTORED'
out['stage_claims_quality_qualified']=False
out['pipeline_PI1_status']='CANCELLED_NOT_STARTED_AFTER_STAGE_GATE_FAILURE'
out['monitoring_context']='Read-only screenshot commands were supplied to the user during the run. Whether/when they were executed is unknown; no causal attribution or assumed execution. Assistant waited only on frontend until terminal.'
save('independent_audit.json',out);save('raw_source_map.json',maps)

fig,axes=plt.subplots(1,3,figsize=(12,3.8))
p=out['sessions']['pipeline_PI4'];st=out['sessions']['stages_PI4']
for ax,key,title in zip(axes[:2],('h1_adv_over_clean','h2_advcap_over_adv'),('Qualified total: attacked / clean','Qualified total: cap / attacked')):
    mm=p['per_image_medians_ns'];clean={im:median([v['ns'] for a in ('clean_total_A','clean_total_B') for v in maps['pipeline_PI4']['timing_lines_by_image_arm'][im][a]]) for im in names}
    ratios=[mm[im]['adv_total']/clean[im] if key.startswith('h1') else mm[im]['advcap_total']/mm[im]['adv_total'] for im in names]
    ax.scatter(range(1,21),ratios,s=20);ax.axhline(1,color='grey',ls=':');ax.set(title=title,xlabel='Frozen image index',ylabel='Per-image median ratio')
for stage,color in (('nms','#b64937'),('mask','#23765b')):
    axes[2].scatter(range(1,21),[st['controls'][stage]['per_image_aa_log'][im] for im in names],label=stage.upper(),s=20,color=color)
axes[2].axhline(0,color='grey',ls=':');axes[2].set(title='Diagnostic stage A/A; joint gate FAIL',xlabel='Frozen image index',ylabel='Per-image log(A/B)');axes[2].legend()
fig.suptitle('Pi 3B, declared 600 MHz condition; one full campaign, no retry',fontsize=11);fig.tight_layout()
for ext in ('png','pdf'):
    dest=B/('full20_quality_and_effects.'+ext)
    if dest.exists():raise FileExistsError(dest)
    fig.savefig(dest,dpi=180)
plt.close(fig)
print(json.dumps(dict(status=out['status'],main_quality=summary['pipeline_PI4']['quality_pass'],stages_quality=summary['stages_PI4']['quality_pass'])))
