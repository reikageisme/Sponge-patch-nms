"""POST-DATA diagnosis of a rejected component session; no new measurement.

Uses ALL20 images/all200 attacked A/B NMS calls. Global vmstat deltas cover
whole mixed-workload image blocks, not individual calls/process attribution.
Previous recorded arm is not necessarily the immediate unclocked predecessor.
No row/image is removed and no registered estimate/gate is changed.
"""
from pathlib import Path
import hashlib
import json
from statistics import median
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).resolve().parent
raw=B/'runs/full_01/stages_PI4/raw.jsonl'
rows=[json.loads(s) for s in raw.read_text(encoding='utf-8').splitlines()]
summary=json.loads((B/'runs/full_01/summary.json').read_text(encoding='utf-8'))['stages_PI4']
assert not summary['quality_pass']
env=[(i,r) for i,r in enumerate(rows,1) if r['kind']=='environment']
assert [r['block'] for _,r in env]==[*range(20),'end']
pre={r['guard_id']:dict(line=i,fast=r['fast']) for i,r in enumerate(rows,1) if r['kind']=='guard' and r['phase']=='pre'}
out=dict(status='POSTDATA_DIAGNOSTIC_REJECTED_COMPONENT_NO_RESCORING',
         raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),registered_quality_pass=False,
         selection='All20 images, all200 nms_adv/nms_adv_B calls; no filtering or retries.',
         cpu_ratio_definition='Whole-process CPU ns / wall ns; can exceed1 with parallel threads. Below1 alone does not identify a cause or exact off-CPU time.',
         page_counter_scope='System /proc/vmstat sampled at block boundaries, including load/reference/counts/warmup/masks/NMS/other system work; no per-call/process attribution.',
         blocks=[])
for (line,start),(endline,end) in zip(env,env[1:]):
    timings=[(i,r) for i,r in enumerate(rows,1) if r['kind']=='timing' and r['block']==start['block']]
    calls=[];previous=None
    for n,r in timings:
        if r['arm'] in ('nms_adv','nms_adv_B'):
            calls.append(dict(raw_line=n,arm=r['arm'],rep=r['rep'],position=r['position'],
                wall_ns=r['ns'],process_cpu_ns=r['process_cpu_ns'],cpu_over_wall=r['process_cpu_ns']/r['ns'],
                previous_recorded_timing_arm=previous,pre_guard_line=pre[r['guard_id']]['line'],
                pre_guard_mem_available_kb=pre[r['guard_id']]['fast']['mem_kb']['MemAvailable']))
        previous=r['arm']
    assert len(calls)==10
    delta=end['vmstat']['pgmajfault']-start['vmstat']['pgmajfault'];assert delta>=0
    out['blocks'].append(dict(index_one_based=start['block']+1,image=timings[0][1]['image'],
        environment_raw_lines=[line,endline],global_pgmajfault_start=start['vmstat']['pgmajfault'],
        global_pgmajfault_end=end['vmstat']['pgmajfault'],global_pgmajfault_delta=delta,
        nms_wall_median_ns=median(c['wall_ns'] for c in calls),nms_wall_max_ns=max(c['wall_ns'] for c in calls),
        cpu_wall_ratio_min=min(c['cpu_over_wall'] for c in calls),
        n_cpu_below_wall=sum(c['process_cpu_ns']<c['wall_ns'] for c in calls),calls=calls))
assert len(out['blocks'])==20 and sum(len(b['calls']) for b in out['blocks'])==200
out['global_pgmajfault_block_sum']=sum(b['global_pgmajfault_delta'] for b in out['blocks'])
out['n_cpu_below_wall']=sum(b['n_cpu_below_wall'] for b in out['blocks'])
out['source_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
with (B/'saved_nms_diagnosis.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True)
x=[b['index_one_based'] for b in out['blocks']]
axes[0].bar(x,[b['global_pgmajfault_delta'] for b in out['blocks']],color='#446e97')
axes[0].set(ylabel='Global pgmajfault delta',title='Whole image block; NOT process/call attribution')
for b in out['blocks']:
    for c in b['calls']:axes[1].scatter(b['index_one_based'],c['wall_ns']/1e6,s=12,color='#b34f38',alpha=.55)
axes[1].set(ylabel='NMS wrapper wall ms',title='All200 attacked A/B calls; rejected component session')
axes[2].plot(x,[b['cpu_wall_ratio_min'] for b in out['blocks']],'o-',color='#287553')
axes[2].axhline(1,color='grey',ls=':');axes[2].set(xlabel='Frozen image index',ylabel='Min process CPU / wall',xticks=x)
fig.suptitle('Post-data diagnostic only: paging counter and NMS waits may co-occur; cause unresolved',fontsize=11)
fig.tight_layout()
for ext in ('png','pdf'):
    dest=B/('saved_nms_diagnosis.'+ext)
    if dest.exists():raise FileExistsError(dest)
    fig.savefig(dest,dpi=180)
print(json.dumps(dict(blocks=20,calls=200,global_pgmajfault_block_sum=out['global_pgmajfault_block_sum'],n_cpu_below_wall=out['n_cpu_below_wall'],
    image77=next(b for b in out['blocks'] if b['image']=='000000000077'))))
