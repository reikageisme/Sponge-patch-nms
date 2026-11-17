"""Prepare closures/clones BEFORE any predecessor-target pair, no timing here."""
from baseline_ops import process_mask_native
from preallocate import process_mask_preallocated
from kernel_input import suppress,copy_layout,IOU


def predecessor(material,kind,nms):
    case=material['mask_case']
    args=(case['protos'],case['coefficients'],case['boxes'],tuple(case['shape']))
    if kind=='native32M':return lambda:process_mask_native(*args)
    if kind=='candidate16M':return lambda:process_mask_preallocated(*args,pixel_budget=16_000_000)
    if kind=='nms_reference':
        prediction=material['prediction'].clone()
        return lambda:suppress(nms,prediction)
    raise ValueError('unknown registered predecessor')


def target(material,kind,nms):
    if kind=='sham':return lambda:None
    if kind=='wrapper':
        prediction=material['prediction'].clone()
        return lambda:suppress(nms,prediction)
    if kind=='kernel_call':
        kernel=material['kernel']
        boxes,scores=copy_layout(kernel['boxes']),copy_layout(kernel['scores'])
        backend=kernel['backend']
        return lambda:backend(boxes,scores,IOU)
    raise ValueError('unknown registered target')
