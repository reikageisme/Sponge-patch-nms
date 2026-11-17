"""Functional material validation only, no model creation/clock or device launch.

Head/prototype traversal adapts sponge-sim/studies/pi3b_full20_20261114/run.py:228-243;
SHA256 cadc78041d3f4e611c789c76c22b1a885131b9ca632a52a27300a440baa4425f. Require unambiguous outputs and
exact frozen cache content, not merely matching retained counts.
"""
import torch
from cache import validate_case
from kernel_input import capture,MAX_NMS


def tensors(raw):
    if torch.is_tensor(raw):yield raw
    elif isinstance(raw,(tuple,list)):
        for x in raw:yield from tensors(x)
    elif isinstance(raw,dict):
        for x in raw.values():yield from tensors(x)
    elif raw is not None:raise ValueError('unknown model output container')


def prediction_proto(raw):
    values=list({id(x):x for x in tensors(raw)}.values())
    preds=[x for x in values if x.ndim==3 and x.shape[0]==1 and x.shape[1]==116]
    protos=[x for x in values if x.ndim==4 and tuple(x.shape)==(1,32,160,160)]
    if len(preds)!=1 or len(protos)!=1:raise ValueError('ambiguous/missing YOLOv8 segmentation output')
    return preds[0],protos[0][0]


def prepare(raw,cached_case,row,nms,vision_ops):
    k=validate_case(cached_case)
    pred,proto=prediction_proto(raw)
    if pred.requires_grad or proto.requires_grad:raise ValueError('inference outputs must not retain autograd graphs')
    captured=capture(pred,nms,vision_ops)
    det=captured['detections']
    fresh=dict(protos=proto.contiguous(),coefficients=det[:,6:].contiguous(),
               boxes=det[:,:4].contiguous(),shape=(640,640))
    if validate_case(fresh)!=k:raise ValueError('fresh/frozen retained count differs')
    for name in ('protos','coefficients','boxes'):
        if not torch.equal(fresh[name],cached_case[name]):raise ValueError('fresh/frozen tensor content differs: '+name)
    n_tau=int((pred[:,4:84,:].amax(1)>.25).sum())
    counts=dict(k=k,n_tau=n_tau,kernel_n=captured['n_kernel'])
    if counts!=row['counts'] or k!=row['k'] or captured['n_kernel']!=min(n_tau,MAX_NMS):
        raise ValueError('fresh/frozen candidate or kernel counts differ')
    # Return fresh values only after exact parity; caller may release loaded cache
    # tensors before trials instead of retaining a second full prototype stack.
    return dict(prediction=pred,mask_case=fresh,kernel=captured,counts=counts,
        fresh_frozen_tensor_parity=True,material_stage_only=True)
