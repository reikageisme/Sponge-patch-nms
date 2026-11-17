"""Postterminal schema/identity/guard audit; no renderer/model or resource timing.

Loads cached tensors only for finite FP32/shape validation on the laptop.
It does not rerender them across a different PyTorch version or claim that
the stored device mask digest is a cross-platform numerical equivalence.
"""
from pathlib import Path
import gc
import hashlib
import json
import sys

B=Path(__file__).resolve().parent
S=B.parents[1]/'studies/pi3b_renderer_prealloc_20261114'
sys.path.insert(0,str(S))
from cache import load_case,sha,validate_manifest,record
from memory_worker import IMAGE_IDS
from guard import violations

C=B/'caches/cache_01';R=B/'runs/cacheprep_01'
manifest=json.loads((C/'manifest.json').read_text(encoding='utf-8'))
reg=json.loads((B/'registered_materials/engineering_lock.json').read_text(encoding='utf-8'))
parent=json.loads((B/'registered_materials/full20_summary.json').read_text(encoding='utf-8'))['pipeline_PI4']
transfer=json.loads((B/'transfer_verification.json').read_text(encoding='utf-8'))
assert transfer['n_files']==90 and transfer['source_unchanged'] and transfer['restore_readback_verified']
rows=validate_manifest(manifest,IMAGE_IDS)
assert manifest['reference_summary_sha256']=='34166aa9972cd0ffac8af3524a15565eb2ea94235c3f640de9312603e6799ca3'
assert manifest['source_lock_sha256']=='1cd1789d4f30c0a6b708fad907729999f6e6e53d4ba373ce487bc8037d10be0e'
assert manifest['builder_sha256']==reg['source_sha256']['build_cache.py']
assert manifest['empirical_endpoint_recorded'] is False
input_lock=json.loads((B/'registered_materials/full20_lock.json').read_text(encoding='utf-8'))
expected_source={v['name']:v['sha256'] for v in input_lock['files'] if v['name'] in [input_lock['weights'],*input_lock['inputs']]}
assert manifest['source_material_sha256']==expected_source
assert manifest['versions']==input_lock['versions']
case_records=[]
for ix,row in enumerate(rows):
    receipt_path=C/(row['filename']+'.receipt.json')
    assert json.loads(receipt_path.read_text(encoding='utf-8'))==row
    old=parent['counts'][row['image']][row['condition']]
    assert row['counts']['k']==row['k']==old['k'] and row['counts']['n_tau']==old['n_tau']
    assert row['counts']['kernel_n']==min(row['counts']['n_tau'],30000)
    case=load_case(C,row)
    case_records.append(dict(index=ix,image=row['image'],condition=row['condition'],k=row['k'],n_tau=row['counts']['n_tau'],
        cache_sha256=row['sha256'],device_common_mask_sha256=row['mask_sha256'],
        shapes={k:list(case[k].shape) for k in ('protos','coefficients','boxes')},
        receipt=receipt_path.relative_to(B).as_posix()))
    del case;gc.collect()
guards=[json.loads(line) for line in (R/'functional_guards.jsonl').read_text(encoding='utf-8').splitlines()]
assert guards
baseline=guards[0]['fast']['vmstat']
for row in guards:
    assert row['violations']==[] and not violations(row['fast'],reg['safety'],[0,1,2,3],baseline)
restore=json.loads((R/'restore.json').read_text(encoding='utf-8'))
assert restore['status']=='RESTORED' and restore['errors']==[]
registration=json.loads((R/'registration.json').read_text(encoding='utf-8'))
assert registration['tag']=='qa-pi3b-renderer-cache-20261114' and registration['commit']=='b5304d20ef0dbb6ae82273ec330806502431595a'
assert registration['lock_sha256']==sha(B/'registered_materials/engineering_lock.json')
assert json.loads((C/'terminal.json').read_text(encoding='utf-8'))==dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False)
out=dict(status='FORTY_DEVICE_FUNCTIONAL_PARITY_CASES_AND_CACHED_TENSOR_SCHEMA_VERIFIED',n_images=20,n_cases=len(rows),
         cases=case_records,guard_records=len(guards),guards_all_pass=True,
         min_guard_mem_available_kb=min(r['fast']['mem_kb']['MemAvailable'] for r in guards),
         max_guard_temp_c=max(r['fast']['temp_c'] for r in guards),
         requested_khz_values=sorted({r['fast']['scaling_cur_khz'] for r in guards}),
         requested_clock_not_continuous_actual_clock=True,
         condition_counters_initial=baseline,condition_counters_end=guards[-1]['fast']['vmstat'],
         restore=restore,manifest_sha256=sha(C/'manifest.json'),
         common_digest_interpretation='Device compare_outputs computes both SHA sequentially, rejects inequality, then saves the common digest. No two full masks retained together.',
         schema_validation_on_laptop_only=True,renderer_reexecution_on_laptop=False,
         kernel_count_parity=True,empirical_latency_or_rss_endpoint_recorded=False,
         physical_guard_values_not_peak_rss_or_a_controlled_memory_comparison=True)
record(B/'functional_audit.json',out)
print(json.dumps({k:out[k] for k in ('status','n_cases','guard_records','min_guard_mem_available_kb','max_guard_temp_c','requested_khz_values')}))
