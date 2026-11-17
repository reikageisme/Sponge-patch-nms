# Copied/adapted from sponge-sim/studies/pi3b_renderer_prealloc_20261114/preallocate.py:1-29
# SHA256 795aa41ec26b0429f27c0ebb27ca444aa56134324eedf9477af7fa5ffbd6d83c; earlier QA/cache source and runs remain immutable.
"""Inference-only renderer candidate, NOT deployed in any measured protocol.

Adapted from baseline_ops.process_mask_native, originally Ultralytics ops.py
lines 513-538, SHA256 828de5d265ab91a792acae836f9380d07abda2a15a501170fc9f49d7a448688d.
AGPL-3.0: https://ultralytics.com/license

Retain the coefficient matmul, threshold, resize and crop. Preallocate uint8
output; directly copy thresholded float chunks into it. A 16M pixel budget
reduces float scratch. Merely preallocating at the old 32M budget may INCREASE
the theoretical live-tensor maximum: see static_memory.py, not measured RSS.
"""
import torch
from baseline_ops import crop_mask, scale_masks


def process_mask_preallocated(protos, masks_in, bboxes, shape, *, pixel_budget=16_000_000):
    c, mh, mw = protos.shape
    h, w = shape
    if masks_in.shape[0] == 0:
        return torch.zeros((0, h, w), dtype=torch.uint8, device=masks_in.device)
    coeffs = masks_in @ protos.float().view(c, -1)
    step = max(1, pixel_budget // (h * w))
    output = torch.empty((masks_in.shape[0], h, w), dtype=torch.uint8, device=masks_in.device)
    for i in range(0, coeffs.shape[0], step):
        chunk = scale_masks(coeffs[i:i+step].view(-1, mh, mw)[None], shape)[0]
        chunk.gt_(0.0)
        output[i:i+step].copy_(chunk)
        del chunk
    return crop_mask(output, bboxes)
