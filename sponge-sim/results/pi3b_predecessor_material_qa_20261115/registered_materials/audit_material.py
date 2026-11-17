"""Postterminal functional-only replay. No model/NMS/mask rerun or timing.

Loads exported CPU tensors with weights_only=True; compares bytes/counts/layout
and original frozen tensors. Does not equate host/Pi compiled operators.
"""
from pathlib import Path
import hashlib
import json

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
S=ROOT/'sponge-sim/studies/pi3b_nms_predecessor_20261115'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def inspect_case(payload,row,frozen,frozen_row):
    import torch
    def digest(t):return hashlib.sha256(memoryview(t.detach().contiguous().numpy()).cast('B') if t.numel() else b'').hexdigest()
    def layout(t):return dict(shape=list(t.shape),stride=list(t.stride()),storage_offset=t.storage_offset(),dtype=str(t.dtype),device=str(t.device))
    if set(payload)!={'schema','image','condition','prediction','mask_case','kernel','counts'} or payload['schema']!=1:
        raise ValueError('export payload schema differs')
    if (payload['image'],payload['condition'])!=(row['image'],row['condition']):raise ValueError('payload identity differs')
    pred=payload['prediction'];case=payload['mask_case'];kernel=payload['kernel'];counts=payload['counts']
    if tuple(pred.shape)!=(1,116,8400) or pred.dtype!=torch.float32 or pred.device.type!='cpu' or not bool(torch.isfinite(pred).all()):
        raise ValueError('native prediction contract differs')
    if counts!=frozen_row['counts'] or counts!=row['counts'] or any(type(x) is not int for x in counts.values()):
        raise ValueError('frozen/fresh count metadata differs')
    if int((pred[:,4:84,:].amax(1)>.25).sum())!=counts['n_tau']:raise ValueError('prediction candidate count differs')
    k=counts['k'];n=counts['kernel_n']
    if n!=min(counts['n_tau'],30000) or not 0<=k<=300 or not 0<n<=8400:raise ValueError('count bounds differ')
    if set(case)!={'protos','coefficients','boxes','shape'} or tuple(case['shape'])!=(640,640):raise ValueError('mask case schema differs')
    for key in ('protos','coefficients','boxes'):
        if case[key].dtype!=torch.float32 or not bool(torch.isfinite(case[key]).all()) or not torch.equal(case[key],frozen[key]):
            raise ValueError('fresh/frozen tensor differs: '+key)
    if tuple(case['protos'].shape)!=(32,160,160) or tuple(case['coefficients'].shape)!=(k,32) or tuple(case['boxes'].shape)!=(k,4):
        raise ValueError('mask tensor shapes differ')
    if 'backend' in kernel or tuple(kernel['boxes'].shape)!=(n,4) or tuple(kernel['scores'].shape)!=(n,):raise ValueError('true kernel argument shapes differ')
    keep=kernel['keep'];det=kernel['detections']
    if keep.dtype!=torch.int64 or keep.ndim!=1 or len(keep.unique())!=len(keep) or len(keep)>n or (len(keep) and (int(keep.min())<0 or int(keep.max())>=n)):
        raise ValueError('uncapped keep indices invalid')
    if tuple(det.shape)!=(k,38) or min(len(keep),300)!=k:raise ValueError('capped/uncapped output count differs')
    selected=keep[:300]
    if (not torch.equal(kernel['boxes'][selected],det[:,:4]+det[:,5:6]*7680)
        or not torch.equal(kernel['scores'][selected],det[:,4])
        or not torch.equal(case['coefficients'],det[:,6:]) or not torch.equal(case['boxes'],det[:,:4])):
        raise ValueError('keep/selected/class-offset detection parity differs')
    if (layout(kernel['boxes'])!=row['kernel_box_layout'] or layout(kernel['scores'])!=row['kernel_score_layout']
        or layout(kernel['boxes'])!=kernel['original_box_layout'] or layout(kernel['scores'])!=kernel['original_score_layout']):
        raise ValueError('original/serialized kernel stride or offset differs')
    scores=kernel['scores'];extent=scores.storage_offset()+1+(n-1)*scores.stride()[0]
    backing=scores.as_strided((extent,),(1,),0);padding=torch.ones(extent,dtype=torch.bool)
    padding[scores.storage_offset()+torch.arange(n)*scores.stride()[0]]=False
    if not bool((backing[padding]==0).all()):raise ValueError('serialized score padding not zero initialized')
    hashes=dict(prediction=digest(pred),**{key:digest(case[key]) for key in ('protos','coefficients','boxes')},
        kernel_boxes=digest(kernel['boxes']),kernel_scores=digest(scores),keep=digest(keep),detections=digest(det))
    if hashes!=row['content_sha256']:raise ValueError('logical tensor SHA differs')
    if row['mask_sha256']!=frozen_row['mask_sha256'] or row['frozen_cache_sha256']!=frozen_row['sha256'] or row['functional_only'] is not True:
        raise ValueError('original cache/mask provenance differs')
    return dict(image=row['image'],condition=row['condition'],counts=counts,prediction_shape=list(pred.shape),
        true_kernel_n=n,uncapped_keep_n=len(keep),retained_k=k,layout_preserved=True,fresh_frozen_tensor_parity=True,
        mask_sha256=row['mask_sha256'],local_model_nms_or_mask_rerun=False)


def main():
    original=B/'runs/material_01/original';transfer=load(B/'transfer_verification.json');errors=[];cases=[]
    for name,entry in transfer['files'].items():
        p=original/name
        if sha(p)!=entry['sha256'] or p.stat().st_size!=entry['bytes']:errors.append('changed original: '+name)
    if not transfer['independent_restore_verified']:errors.append('independent restore failed/unavailable')
    if not transfer['source_and_prior_originals_unchanged']:errors.append('source/prior originals changed/unavailable')
    required={'campaign_terminal.json':dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False),
        'functional/terminal.json':dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False)}
    for name,want in required.items():
        if not (original/name).exists() or load(original/name)!=want:errors.append('missing/failed terminal: '+name)
    worker=load(original/'worker_terminal.json') if (original/'worker_terminal.json').exists() else {}
    if worker.get('status')!='COMPLETED' or worker.get('returncode')!=0 or worker.get('direct_child_reaped') is not True or worker.get('termination_sent') is not False:
        errors.append('worker terminal not a clean completion')
    for name in ('parent_guards.jsonl','functional/guards.jsonl'):
        p=original/name
        if not p.exists():errors.append('missing physical guards: '+name);continue
        rows=[json.loads(line) for line in p.read_text().splitlines()]
        if not rows or any(row.get('violations')!=[] for row in rows):errors.append('failed physical guards: '+name)
        if name.startswith('functional/') and any(not 594000000<=row['actual_arm_hz']<=606000000 for row in rows):errors.append('actual ARM clock failed')
    manifest=load(original/'functional/manifest.json') if (original/'functional/manifest.json').exists() else {}
    cache=load(S/'cache_manifest.json');ids=[name.split('_')[0] for name in load(S/'full20_lock.json')['inputs']]
    expected=[(im,condition) for im in ids for condition in ('clean','adv')]
    rows=manifest.get('cases',[])
    if manifest.get('status')!='COMPLETED_FUNCTIONAL_ONLY' or [(row['image'],row['condition']) for row in rows]!=expected:
        errors.append('full40 manifest incomplete/reordered; no subset verdict')
    if not errors:
        import torch
        frozen_root=ROOT/'sponge-sim/results/pi3b_renderer_functional_cache_20261114/caches/cache_01'
        by_key={(row['image'],row['condition']):row for row in cache['cases']}
        for row in rows:
            p=original/'functional'/row['filename'];frozen_row=by_key[(row['image'],row['condition'])];f=frozen_root/frozen_row['filename']
            if sha(p)!=row['sha256'] or p.stat().st_size!=row['bytes'] or load(p.with_suffix('.receipt.json'))!=row:
                errors.append('case receipt/hash differs: '+row['filename']);break
            if sha(f)!=frozen_row['sha256']:errors.append('old frozen cache changed');break
            payload=torch.load(p,map_location='cpu',weights_only=True);frozen=torch.load(f,map_location='cpu',weights_only=True)
            try:cases.append(inspect_case(payload,row,frozen,frozen_row))
            except Exception as exc:errors.append(row['filename']+': '+type(exc).__name__+': '+str(exc));break
            finally:del payload,frozen
        for image in ids:
            p=original/'functional'/f'{image}_pool.json'
            frame=load(p)
            if frame['complete_stable_set'] is not True or not frame['threads'] or any(t['affinity']!=[0,1,2,3] or t['status']!='OK' for t in frame['threads'].values()):
                errors.append('all-thread identity/affinity failed: '+image)
    result=dict(status='FUNCTIONAL40_PARITY_SOURCE_RESTORE_PASS' if not errors and len(cases)==40 else 'FAILED_OR_INCOMPLETE_NO_RETRY',
        errors=errors,cases=cases,complete_case_count=len(cases),unit='functional cases; NOT independent efficacy samples',
        empirical_performance_endpoint_recorded=False,scientific_activation_authorized=False,ssh_kept_open=True)
    with (B/'functional_audit.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(dict(status=result['status'],cases=len(cases),errors=errors)))


if __name__=='__main__':main()
