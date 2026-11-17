"""Laptop reference counts for the 20 frozen pairs (same pipeline as run.py). NO timing.

Purpose: descriptive cross-runtime parity of N_tau / K between the laptop stack
(torch 2.13.0) and the Pi stack (torch 2.15.0). Not a gate; mismatches are reported.
"""
import hashlib
import json
import sys
from pathlib import Path

import torch
import torchvision                         # before Ultralytics, as in the runners
import ultralytics
from ultralytics import YOLO
from ultralytics.utils import nms

HERE = Path(__file__).resolve().parent
SIM = HERE.parents[1]
SRC = SIM / 'results' / 'laptop_seg_20261107'
lock = json.loads((HERE / 'lock.json').read_text())
torch.manual_seed(lock['seed'])
net = YOLO(str(SRC / lock['weights'])).model.eval().float().cpu()


def tensors(raw):
    if torch.is_tensor(raw):
        yield raw
    elif isinstance(raw, (tuple, list)):
        for x in raw:
            yield from tensors(x)
    elif isinstance(raw, dict):
        for x in raw.values():
            yield from tensors(x)


def suppress(pred, max_det=300, max_nms=30000):
    return nms.non_max_suppression(pred, conf_thres=.25, iou_thres=.45, nc=80, max_det=max_det, max_nms=max_nms)[0]


out = {}
with torch.inference_mode():
    for name in lock['inputs']:
        pair = torch.load(SRC / name, map_location='cpu', weights_only=True)
        row = {}
        for arm, key in (('clean', 'clean'), ('adv', 'attacked')):
            pred = next(t for t in tensors(net(pair[key])) if t.ndim == 3 and t.shape[1] == 116)
            row[arm] = dict(n_tau=int((pred[:, 4:84].amax(1) > .25).sum()), k=len(suppress(pred.clone())),
                            prediction_sha256=hashlib.sha256(pred.numpy().tobytes()).hexdigest())
            if arm == 'adv':
                row['advcap'] = dict(k=len(suppress(pred.clone(), **lock['defense'])))
        out[name.split('_')[0]] = row
dest = Path(sys.argv[1])
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(dict(versions=dict(torch=torch.__version__, torchvision=torchvision.__version__,
                                              ultralytics=ultralytics.__version__), counts=out), indent=2) + '\n')
print('written', dest, 'images', len(out))
