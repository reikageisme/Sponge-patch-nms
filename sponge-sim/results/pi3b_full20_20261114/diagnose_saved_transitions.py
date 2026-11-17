"""Post-data description of recorded predecessor categories; no causal test.

All200 calls kept. Classification was chosen after seeing the rejected
session. No p-values, equivalence, gate rescoring or new device workload.
"""
from collections import defaultdict
from pathlib import Path
from statistics import median
import hashlib
import json

B=Path(__file__).resolve().parent
source=B/'saved_nms_diagnosis.json'
data=json.loads(source.read_text(encoding='utf-8'))
groups=defaultdict(list)
for block in data['blocks']:
    for call in block['calls']:
        prev=call['previous_recorded_timing_arm']
        category=('first_trial_after_unclocked_warmups' if prev is None else
                  'after_attacked_mask' if prev in ('mask_adv','mask_adv_B') else
                  'after_maskdose' if prev.startswith('maskdose_') else
                  'after_clean_mask' if prev=='mask_clean' else 'after_NMS')
        groups[category].append(dict(image=block['image'],index_one_based=block['index_one_based'],**call))
summary={name:dict(n_calls=len(rows),cpu_below_wall=sum(c['cpu_over_wall']<1 for c in rows),
    median_process_cpu_over_wall=median(c['cpu_over_wall'] for c in rows),
    max_wall_ns=max(c['wall_ns'] for c in rows),raw_lines=[c['raw_line'] for c in rows]) for name,rows in groups.items()}
assert sum(v['n_calls'] for v in summary.values())==200
assert sum(v['cpu_below_wall'] for v in summary.values())==data['n_cpu_below_wall']
out=dict(status='POSTDATA_PREDECESSOR_DESCRIPTION_ONLY_NO_CAUSAL_TEST',
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),raw_sha256=data['raw_sha256'],
    classification_after_outcome_inspection=True,all_calls_kept=True,registered_component_gate_still_false=True,
    groups=summary,calls_by_group=dict(groups),
    largest_global_counter_blocks=sorted([{k:b[k] for k in ('image','index_one_based','global_pgmajfault_delta','environment_raw_lines')}
        for b in data['blocks']],key=lambda b:b['global_pgmajfault_delta'],reverse=True),
    limits=['Recorded predecessor excludes guard/clone/setup/release and may omit unclocked work.',
            'Image/workload/order/time/system activity confound the pooled groups; no controlled treatment contrast.',
            'Global major-page counter changes cannot be assigned to this process or a particular NMS call.',
            'Process CPU / wall below1 indicates a gap in aggregate CPU consumption, not a uniquely identified wait cause.'])
with (B/'saved_nms_transitions.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(groups=summary,largest_global_counter_blocks=out['largest_global_counter_blocks'][:4])))
