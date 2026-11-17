"""Explicit live-tensor storage model; NOT allocator/RSS/peak-memory measurement."""
import json
from pathlib import Path


def model(k, shape=(640,640), proto_shape=(32,160,160), budget=16_000_000):
    h,w=shape;p=h*w;oldstep=max(1,32_000_000//p);newstep=max(1,budget//p)
    coeff_bytes=k*proto_shape[1]*proto_shape[2]*4
    # During byte conversion old float+uint8 chunks coexist with preceding list.
    old_chunks=[min(oldstep,k-i) for i in range(0,k,oldstep)]
    before=0;oldpeaks=[]
    for size in old_chunks:
        oldpeaks.append((before+5*size)*p);before+=size
    # Concatenation retains the old list while allocating its full-size output.
    oldpeak=coeff_bytes+max([2*k*p,*oldpeaks])
    # copy_(float) casts directly into the destination; no separate byte chunk.
    newpeak=coeff_bytes+k*p+4*min(k,newstep)*p
    return dict(k=k,shape=list(shape),pixel_budget=budget,baseline_step=oldstep,candidate_step=newstep,
                coefficients_bytes=coeff_bytes,baseline_max_modeled_live_bytes=oldpeak,
                candidate_max_modeled_live_bytes=newpeak,
                modeled_difference_bytes=oldpeak-newpeak)


if __name__=='__main__':
    target=Path(__file__).with_name('static_memory.json')
    result=dict(status='STATIC_STORAGE_MODEL_NOT_RSS_OR_SPEED',assumptions=[
        'FP32 coefficients and resized logits, uint8 output, standard dense tensor storage.',
        'Includes coefficient tensor, output/chunks only; excludes model, inputs, prototypes, crop grids, allocator, thread stacks and operator workspaces.',
        'No native profiler or empirical peak-memory measurement; formulas may not predict runtime RSS.',
        'Bilinear interpolation may have unmodeled internal allocations. Small K can regress modeled storage.'],
        rows=[model(k,budget=budget) for budget in (32_000_000,16_000_000) for k in (0,1,39,78,100,300)])
    with target.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))
