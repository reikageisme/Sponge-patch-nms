"""Pi-only functional material preparation; records no latency or RSS endpoint.

Model parsing, NMS observation and input checks adapted from
studies/pi3b_full20_20261114/run.py:224-279,325-338,
SHA256 cadc78041d3f4e611c789c76c22b1a885131b9ca632a52a27300a440baa4425f.
Never modifies that source or its frozen input files. Requires the NEW
supervisor to provide its guarded preparation context; not yet deployed.
"""
from pathlib import Path
import gc
import hashlib
import json
import os
import platform
import sys
from cache import sha,record,compare_outputs,save_case,validate_manifest
from baseline_ops import process_mask_native
from preallocate import process_mask_preallocated

OLD_LOCK_SHA='1cd1789d4f30c0a6b708fad907729999f6e6e53d4ba373ce487bc8037d10be0e'
REFERENCE_SUMMARY_SHA='34166aa9972cd0ffac8af3524a15565eb2ea94235c3f640de9312603e6799ca3'


def pred_proto(torch,raw):
    def tensors(v):
        if torch.is_tensor(v):yield v
        elif isinstance(v,(tuple,list)):
            for x in v:yield from tensors(x)
        elif isinstance(v,dict):
            for x in v.values():yield from tensors(x)
    ts=list(tensors(raw))
    pred=next(x for x in ts if x.ndim==3 and x.shape[1]==116)
    proto=next(x for x in ts if x.ndim==4 and x.shape[1]==32)
    return pred,proto[0]


def build(materials,source_lock,reference_summary,directory,guard):
    """Guard is supplied by the new supervised context, not a no-op CLI flag."""
    if platform.system()!='Linux' or platform.machine()!='aarch64' or not os.environ.get('INVOCATION_ID'):
        raise RuntimeError('actual Pi supervised functional preparation required')
    if sha(source_lock)!=OLD_LOCK_SHA:raise ValueError('wrong source lock')
    if sha(reference_summary)!=REFERENCE_SUMMARY_SHA:raise ValueError('wrong accepted Pi reference summary')
    lock=json.loads(Path(source_lock).read_text(encoding='utf-8'))
    materials=Path(materials).resolve();directory=Path(directory).resolve()
    workspace=Path.home()/'sponge-sim/pi3b_renderer_prealloc_20261114'
    if directory.parent!=workspace/'caches':raise ValueError('new owned cache workspace required')
    if directory==materials or materials in directory.parents:
        raise ValueError('new cache must be outside the old material workspace')
    reference=json.loads(Path(reference_summary).read_text(encoding='utf-8'))['pipeline_PI4']
    if not reference['quality_pass']:raise ValueError('expected accepted full20 reference')
    expected={r['name']:r['sha256'] for r in lock['files']}
    names=lock['inputs'];ids=[Path(n).name.split('_')[0] for n in names]
    if len(ids)!=20 or set(reference['counts'])!=set(ids):raise ValueError('wrong fixed cohort')
    for name in [lock['weights'],*names]:
        if sha(materials/name)!=expected[name]:raise ValueError('source material changed: '+name)
    guard()
    # Affinity and environment/thread settings MUST already be established by supervisor.
    import torch
    import torchvision  # import BEFORE Ultralytics, to bind compiled NMS dispatch
    import ultralytics
    import numpy as np
    from ultralytics import YOLO
    from ultralytics.utils import nms,ops
    versions=dict(torch=str(torch.__version__),torchvision=str(torchvision.__version__),
                  ultralytics=ultralytics.__version__,numpy=np.__version__,python=sys.version.split()[0])
    if versions!=lock['versions']:raise ValueError('Pi runtime version mismatch')
    if sha(ops.__file__)!=lock['ops_source_sha256'] or sha(nms.__file__)!=lock['nms_source_sha256']:
        raise ValueError('runtime NMS/ops differs')
    if sorted(os.sched_getaffinity(0))!=[0,1,2,3] or torch.get_num_threads()!=4 or torch.get_num_interop_threads()!=1:
        raise ValueError('functional preparation thread/affinity context differs')
    directory.mkdir(parents=True,exist_ok=False)
    manifest=dict(status='PREPARING_FUNCTIONAL_ONLY',versions=versions,source_lock_sha256=OLD_LOCK_SHA,
                  reference_summary_sha256=sha(reference_summary),source_material_sha256={n:expected[n] for n in [lock['weights'],*names]},
                  builder_sha256=sha(__file__),empirical_endpoint_recorded=False,cases=[])
    record(directory/'preparation.json',manifest)
    try:
        guard()
        net=YOLO(str(materials/lock['weights'])).model.eval().float().cpu()
        for p in net.parameters():p.requires_grad_(False)
        with torch.inference_mode():
            for name,im in zip(names,ids):
                guard();pair=torch.load(materials/name,map_location='cpu',weights_only=True)
                clean,adv=pair['clean'].contiguous(),pair['attacked'].contiguous()
                if any(tuple(x.shape)!=(1,3,640,640) or x.dtype!=torch.float32 or not bool(torch.isfinite(x).all()) for x in (clean,adv)):
                    raise ValueError('input shape/dtype/finite contract')
                if min(float(clean.min()),float(adv.min()))<0 or max(float(clean.max()),float(adv.max()))>1 or float((adv-clean).abs().max())>16/255+1e-6:
                    raise ValueError('input range/budget differs')
                for arm,image in (('clean',clean),('adv',adv)):
                    guard();pred,proto=pred_proto(torch,net(image));guard()
                    original=torchvision.ops.nms;calls=[]
                    def observed(boxes,scores,iou):
                        calls.append(len(scores));return original(boxes,scores,iou)
                    torchvision.ops.nms=observed
                    try:det=nms.non_max_suppression(pred.clone(),conf_thres=.25,iou_thres=.45,nc=80,max_det=300,max_nms=30000)[0]
                    finally:torchvision.ops.nms=original
                    n_tau=int((pred[:,4:84].amax(1)>.25).sum())
                    counts=dict(k=len(det),n_tau=n_tau,kernel_n=calls[0] if calls else 0)
                    if calls!=([min(n_tau,30000)] if n_tau else []):raise ValueError('fixed kernel invocation contract')
                    if any(counts[k]!=reference['counts'][im][arm][k] for k in ('k','n_tau')):
                        raise ValueError('cache count parity differs from frozen Pi replay')
                    case=dict(protos=proto.detach().contiguous(),coefficients=det[:,6:].detach().contiguous(),
                              boxes=det[:,:4].detach().contiguous(),shape=(640,640))
                    del pred,proto,det
                    digest=compare_outputs(case,process_mask_native,process_mask_preallocated,guard)
                    row=save_case(directory,im,arm,case,digest,counts)
                    manifest['cases'].append(row);record(directory/(row['filename']+'.receipt.json'),row)
                    del case;gc.collect();guard()
                del pair,clean,adv,image;gc.collect()
        manifest['status']='COMPLETED_FUNCTIONAL_PARITY_ONLY';validate_manifest(manifest,ids)
        record(directory/'manifest.json',manifest)
        record(directory/'terminal.json',dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=len(manifest['cases']),empirical_endpoint_recorded=False))
        return manifest
    except BaseException as e:
        record(directory/'terminal.json',dict(status='FAILED_NO_RETRY',error=type(e).__name__,message=str(e),completed_cases=len(manifest['cases'])))
        raise
