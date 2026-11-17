"""Prepared reference/warmup controls, no device launcher or implicit benchmark.

Adapts run.py:286-294,320-327,381 in studies/pi3b_full20_20261114,
SHA256 cadc78041d3f4e611c789c76c22b1a885131b9ca632a52a27300a440baa4425f.
Counts/3% drift/max2 flags from its lock.json SHA256
1cd1789d4f30c0a6b708fad907729999f6e6e53d4ba373ce487bc8037d10be0e.
Old sources/results are unchanged; future scientific registration still needed.
"""
from statistics import median
import math
from .schedule import IMAGE_IDS


def baseline_pipeline(net,image,nms,core):
    """Original forward -> fixed NMS -> native mask for global warmups only.

Adapts full() at the same source run.py:248-253. Caller supplies the separately
qualified model/runtime in inference mode; no cache reload or new model here.
"""
    raw=net(image);pred,proto=core.material.prediction_proto(raw)
    if pred.requires_grad or proto.requires_grad:raise ValueError('inference outputs required for global warmup')
    detections=core.kernel_input.suppress(nms,pred)
    return core.baseline_ops.process_mask_native(proto,detections[:,6:],detections[:,:4],(640,640))


def warmup(fn,count,*,label,guard,emit):
    if type(count) is not int or count not in (1,3):raise ValueError('fixed warmup count1 or3 required')
    for repeat in range(count):
        guard('warmup_pre')
        try:output=fn()
        except BaseException as exc:
            emit(dict(kind='warmup_failed',label=label,repeat=repeat,completed=False,error=type(exc).__name__));raise
        del output
        try:guard('warmup_post')
        except BaseException as exc:
            emit(dict(kind='warmup',label=label,repeat=repeat,completed=True,post_guard_ok=False,error=type(exc).__name__))
            raise
        emit(dict(kind='warmup',label=label,repeat=repeat,completed=True,post_guard_ok=True))


def reference(forward,*,label,baseline_ns,measure,guard,emit):
    """One unclocked warmup, three uninstrumented samples; keep first baseline.

Caller binds the frozen bracket and physical guard before native activation.
Output is deleted after bracket endpoints, BEFORE post-guard and serialization.
No sample filtering, adaptive warming or retry; completed failed-post samples
are preserved but never promoted to a successful reference summary.
"""
    if baseline_ns is not None and (type(baseline_ns) not in (int,float) or not math.isfinite(baseline_ns) or baseline_ns<=0):
        raise ValueError('first positive reference baseline required')
    warmup(forward,1,label=label,guard=guard,emit=emit)
    samples=[]
    for repeat in range(3):
        guard('reference_pre')
        try:output,raw=measure(forward,instrumented=False)
        except BaseException as exc:
            emit(dict(kind='reference_failed',label=label,repeat=repeat,measurement=None,error=type(exc).__name__));raise
        del output
        row=dict(kind='reference_sample',label=label,repeat=repeat,measurement=raw)
        try:guard('reference_post')
        except BaseException as exc:
            emit(dict(row,post_guard_ok=False,error=type(exc).__name__));raise
        if (not isinstance(raw,dict) or type(raw.get('wall_ns')) is not int or raw['wall_ns']<=0
            or raw.get('counter_status')!='NOT_RECORDED' or any(raw.get(k) is not None for k in ('before','after','increments'))
            or raw.get('output_retained_through_all_endpoints') is not True):
            emit(dict(row,post_guard_ok=True,valid=False));raise ValueError('invalid reference interval')
        emit(dict(row,post_guard_ok=True,valid=True));samples.append(raw['wall_ns'])
    mid=median(samples);baseline=mid if baseline_ns is None else baseline_ns;ratio=mid/baseline
    row=dict(kind='reference',label=label,samples_ns=samples,median_ns=mid,baseline_ns=baseline,ratio=ratio,
        flagged=abs(ratio-1)>.03,reference_is_not_primary_endpoint=True)
    emit(row)
    return baseline,row


def reference_gate(rows,image_ids):
    """Full cadence required: start, before each selected image, end; <=2 flags."""
    if list(image_ids) not in (list(IMAGE_IDS),[IMAGE_IDS[0],IMAGE_IDS[2]]):
        raise ValueError('only complete fixed full20 or smoke2 reference scope allowed')
    expected=['start',*[f'before_{image}' for image in image_ids],'end']
    selected=[r for r in rows if r.get('kind')=='reference']
    if [r['label'] for r in selected]!=expected:raise ValueError('incomplete/reordered reference series')
    baseline=selected[0]['median_ns'];flags=0
    for row in selected:
        samples=row['samples_ns']
        if len(samples)!=3 or any(type(x) is not int or x<=0 for x in samples):raise ValueError('invalid reference samples')
        if row['baseline_ns']!=baseline or row['median_ns']!=median(samples) or row['ratio']!=row['median_ns']/baseline:
            raise ValueError('reference baseline/median/ratio changed')
        expected_flag=abs(row['ratio']-1)>.03
        if type(row['flagged']) is not bool or row['flagged']!=expected_flag:raise ValueError('saved reference flag differs')
        records=[r for r in rows if r.get('label')==row['label'] and r.get('kind') in ('warmup','reference_sample','reference')]
        if [r['kind'] for r in records]!=['warmup','reference_sample','reference_sample','reference_sample','reference']:
            raise ValueError('reference warmup/sample trace incomplete or repeated')
        if records[0].get('completed') is not True or records[0].get('post_guard_ok') is not True:
            raise ValueError('reference warmup did not complete safely')
        for index,sample in enumerate(records[1:4]):
            if (sample.get('repeat')!=index or sample.get('post_guard_ok') is not True or sample.get('valid') is not True
                or sample['measurement']['wall_ns']!=samples[index]):
                raise ValueError('saved reference sample binding differs')
        flags+=int(expected_flag)
    return dict(reference_flags=flags,max_reference_flags=2,reference_pass=flags<=2,
        campaign_quality_assessed=False)
