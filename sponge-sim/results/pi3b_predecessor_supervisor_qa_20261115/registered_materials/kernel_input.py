"""Capture true fixed torchvision input outside any timed call.

Interception pattern follows sponge-sim/studies/pi3b_full20_20261114/run.py:255-269;
SHA256 cadc78041d3f4e611c789c76c22b1a885131b9ca632a52a27300a440baa4425f. Old source/data immutable. Installed
Pi nms.py3220699a lines25/143-159 bind max_wh/class offsets/cap ordering.
No hand-built boxes replace the actual kernel arguments. Stride and storage
offset are preserved, including scores viewed through a detection matrix.
"""
import hashlib
import torch

MAX_DET=300
MAX_NMS=30000
MAX_WH=7680
IOU=.45


def suppress(nms,prediction):
    return nms.non_max_suppression(prediction,conf_thres=.25,iou_thres=IOU,nc=80,
        max_det=MAX_DET,max_nms=MAX_NMS,max_wh=MAX_WH,agnostic=False,
        multi_label=False,rotated=False,end2end=False)[0]


def signature(t):
    return dict(shape=list(t.shape),stride=list(t.stride()),storage_offset=t.storage_offset(),
                dtype=str(t.dtype),device=str(t.device))


def copy_layout(t):
    if t.device.type!='cpu' or t.dtype!=torch.float32 or t.requires_grad or t.ndim not in (1,2) or not bool(torch.isfinite(t).all()):
        raise ValueError('finite CPU FP32 kernel arguments required')
    shape,stride,offset=tuple(t.shape),tuple(t.stride()),t.storage_offset()
    if any(d<=0 or d>MAX_NMS for d in shape) or any(s<=0 or s>116 for s in stride) or not 0<=offset<=116:
        raise ValueError('unsupported kernel layout')
    extent=offset+1+sum((d-1)*s for d,s in zip(shape,stride))
    if extent>MAX_NMS*116+116:raise ValueError('kernel storage extent exceeds bound')
    # Views are exported by torch.save with their backing storage. Initialize
    # unused padding so artifacts do not contain indeterminate heap bytes.
    storage=torch.zeros(extent,dtype=t.dtype,device='cpu')
    result=storage.as_strided(shape,stride,offset)
    result.copy_(t)
    if signature(result)!=signature(t):raise ValueError('kernel layout changed')
    return result


def tensor_sha(t):
    x=t.detach().contiguous()
    if x.numel()==0:return hashlib.sha256(b'').hexdigest()
    return hashlib.sha256(memoryview(x.numpy()).cast('B')).hexdigest()


def validate_keep(keep,n):
    if keep.device.type!='cpu' or keep.dtype!=torch.int64 or keep.ndim!=1:
        raise ValueError('unexpected keep indices')
    if len(keep)>n or len(keep.unique())!=len(keep) or (len(keep) and (int(keep.min())<0 or int(keep.max())>=n)):
        raise ValueError('invalid/duplicate keep indices')


def capture(prediction,nms,vision_ops):
    if (prediction.device.type!='cpu' or prediction.dtype!=torch.float32 or prediction.requires_grad or prediction.ndim!=3
        or prediction.shape[0]!=1 or prediction.shape[1]!=116 or not bool(torch.isfinite(prediction).all())):
        raise ValueError('fixed YOLOv8 segmentation head contract differs')
    original=vision_ops.nms
    calls=[]
    def recorded(boxes,scores,threshold):
        if calls:raise ValueError('multiple kernel invocations')
        if scores.ndim!=1 or boxes.ndim!=2 or tuple(boxes.shape)!=(len(scores),4) or not 0<len(scores)<=MAX_NMS or threshold!=IOU:
            raise ValueError('kernel argument contract differs')
        b,s=copy_layout(boxes),copy_layout(scores)
        keep=original(boxes,scores,threshold)
        validate_keep(keep,len(scores))
        calls.append(dict(boxes=b,scores=s,threshold=threshold,keep=keep.detach().clone(),
            original_box_layout=signature(boxes),original_score_layout=signature(scores)))
        return keep
    vision_ops.nms=recorded
    try:
        detections=suppress(nms,prediction.clone())
    finally:
        vision_ops.nms=original
    if len(calls)!=1 or vision_ops.nms is not original:raise ValueError('missing/restoration of backend interception')
    captured=calls[0]
    if detections.ndim!=2 or detections.shape[1]!=38 or len(detections)>MAX_DET or detections.dtype!=torch.float32:
        raise ValueError('fixed detection contract differs')
    selected=captured['keep'][:MAX_DET]
    if len(selected)!=len(detections):raise ValueError('keep/detection count differs')
    boxes=captured['boxes'];scores=captured['scores']
    expected_hashes=dict(boxes=tensor_sha(boxes),scores=tensor_sha(scores))
    if not torch.equal(boxes[selected],detections[:,:4]+detections[:,5:6]*MAX_WH):
        raise ValueError('selected class-offset box parity differs')
    if not torch.equal(scores[selected],detections[:,4]):raise ValueError('selected score parity differs')
    replay=original(boxes,scores,IOU)
    if not torch.equal(replay,captured['keep']):raise ValueError('kernel keep replay differs')
    repeat=suppress(nms,prediction.clone())
    if not torch.equal(repeat,detections):raise ValueError('full detection replay differs')
    if expected_hashes!=dict(boxes=tensor_sha(boxes),scores=tensor_sha(scores)):
        raise ValueError('kernel inputs changed during replay')
    captured.update(detections=detections,backend=original,
        content_sha256=dict(boxes=tensor_sha(boxes),scores=tensor_sha(scores),keep=tensor_sha(replay),detections=tensor_sha(detections)),
        n_kernel=len(scores),n_keep_uncapped=len(replay),n_retained=len(detections),
        kernel_call_is_not_bare_cpp=True,finite_parity_only=True)
    return captured
