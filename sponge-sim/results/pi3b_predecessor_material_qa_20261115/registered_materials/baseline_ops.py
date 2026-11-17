# Copied/adapted from sponge-sim/studies/pi3b_renderer_memory_usb_20261115/baseline_ops.py:1-98
# SHA256 a4a2273ceb0adc963344a7ab23707015e5c042caea231acbbfec0164480177ca; older source/tag/data remain immutable.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_memory_v1_20261114/baseline_ops.py:1-96
# SHA256 5bd6f0237b951fa170d299271164c0a388efd8a0bba18600d10235854e3225f3; closed USB-absent V1 source/runs remain immutable.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_prealloc_20261114/baseline_ops.py:1-94
# SHA256 526e2cc5686c4719df2c219401382a9ebb4296d8d020a1ae44609a3fb86e78f5; earlier QA/cache source and runs remain immutable.
# Ultralytics AGPL-3.0 License - https://ultralytics.com/license
# Copied from installed ultralytics/utils/ops.py (same locked Pi baseline source).
# Full source SHA256 828de5d265ab91a792acae836f9380d07abda2a15a501170fc9f49d7a448688d
# Function line ranges in provenance.json. Frozen reference; do not edit.
import torch
import torch.nn.functional as F

def crop_mask(masks: torch.Tensor, boxes: torch.Tensor) -> torch.Tensor:
    """Crop masks to bounding box regions.

    Args:
        masks (torch.Tensor): Masks with shape (N, H, W).
        boxes (torch.Tensor): Bounding box coordinates with shape (N, 4) in xyxy pixel format.

    Returns:
        (torch.Tensor): Cropped masks.
    """
    if boxes.device != masks.device:
        boxes = boxes.to(masks.device)
    _, h, w = masks.shape
    x1, y1, x2, y2 = torch.chunk(boxes[:, :, None], 4, 1)  # each shape (n,1,1)
    r = torch.arange(w, device=masks.device, dtype=x1.dtype)[None, None, :]  # columns (1,1,w)
    c = torch.arange(h, device=masks.device, dtype=x1.dtype)[None, :, None]  # rows (1,h,1)
    # Apply the column and row masks separately and in place: the box region is separable, so this avoids ever
    # materializing the full (n, h, w) boolean grid the combined product would build, and has no per-mask Python loop.
    masks *= (r >= x1) * (r < x2)  # zero columns outside the box
    masks *= (c >= y1) * (c < y2)  # zero rows outside the box
    return masks

def process_mask_native(protos, masks_in, bboxes, shape):
    """Apply masks to bounding boxes using mask head output with native upsampling.

    Args:
        protos (torch.Tensor): Mask prototypes with shape (mask_dim, mask_h, mask_w).
        masks_in (torch.Tensor): Mask coefficients with shape (N, mask_dim) where N is number of masks after NMS.
        bboxes (torch.Tensor): Bounding boxes with shape (N, 4) where N is number of masks after NMS.
        shape (tuple): Input image size as (height, width).

    Returns:
        (torch.Tensor): Binary mask tensor with shape (N, H, W).
    """
    c, mh, mw = protos.shape  # CHW
    h, w = shape
    if masks_in.shape[0] == 0:  # no detections: return a well-formed empty mask stack
        return torch.zeros((0, h, w), dtype=torch.uint8, device=masks_in.device)
    coeffs = masks_in @ protos.float().view(c, -1)  # (N, mh*mw) prototype-resolution mask logits
    # Upsampling all N masks at once allocates an N*H*W float intermediate (~9 GB on a large image with many
    # detections), which OOMs the worker. Upsample in chunks bounded by a pixel budget, thresholding each chunk to
    # uint8 immediately so the float intermediate stays small, then crop the assembled uint8 stack.
    step = max(1, 32_000_000 // (h * w))
    masks = [
        scale_masks(coeffs[i : i + step].view(-1, mh, mw)[None], shape)[0].gt_(0.0).byte()
        for i in range(0, coeffs.shape[0], step)
    ]
    return crop_mask(torch.cat(masks), bboxes)

def scale_masks(
    masks: torch.Tensor,
    shape: tuple[int, int],
    ratio_pad: tuple[tuple[int, int], tuple[int, int]] | None = None,
    padding: bool = True,
    mode: str = "bilinear",
) -> torch.Tensor:
    """Rescale segment masks to target shape.

    Args:
        masks (torch.Tensor): Masks with shape (N, C, H, W).
        shape (tuple[int, int]): Target height and width as (height, width).
        ratio_pad (tuple, optional): Ratio and padding values as ((ratio_h, ratio_w), (pad_w, pad_h)).
        padding (bool): Whether masks are based on YOLO-style augmented images with padding.
        mode (str): Interpolation mode, e.g. 'bilinear' for logits or 'nearest' for integer class maps.

    Returns:
        (torch.Tensor): Rescaled masks.
    """
    im1_h, im1_w = masks.shape[2:]
    im0_h, im0_w = shape[:2]
    if im1_h == im0_h and im1_w == im0_w:
        return masks
    if masks.shape[1] == 0:  # empty mask stack: F.interpolate rejects a 0-length channel dim
        return masks.new_zeros((*masks.shape[:2], im0_h, im0_w), dtype=torch.float32)

    if ratio_pad is None:  # calculate from im0_shape
        gain = min(im1_h / im0_h, im1_w / im0_w)  # gain  = old / new
        pad_w, pad_h = (im1_w - round(im0_w * gain)), (im1_h - round(im0_h * gain))  # wh padding
        if padding:
            pad_w /= 2
            pad_h /= 2
    else:
        pad_w, pad_h = ratio_pad[1]
    top, left = (round(pad_h - 0.1), round(pad_w - 0.1)) if padding else (0, 0)
    bottom = im1_h - round(pad_h + 0.1)
    right = im1_w - round(pad_w + 0.1)
    return F.interpolate(masks[..., top:bottom, left:right].float(), shape, mode=mode)  # NCHW masks
