"""Exclusive functional tensor exports; no measurement/timing or model creation."""
from pathlib import Path
import json
import re
import torch
from cache import record,sha
from kernel_input import tensor_sha,signature


def save(directory,image,condition,material,mask_sha256,frozen_row):
    if not re.fullmatch('[0-9]{12}',image) or condition not in ('clean','adv'):
        raise ValueError('invalid material identity')
    filename=f'{image}_{condition}.pt';path=Path(directory)/filename
    kernel={key:value for key,value in material['kernel'].items() if key!='backend'}
    payload=dict(schema=1,image=image,condition=condition,prediction=material['prediction'].detach().contiguous().clone(),
        mask_case={k:(v.detach().contiguous().clone() if torch.is_tensor(v) else v) for k,v in material['mask_case'].items()},
        kernel=kernel,counts=material['counts'])
    with path.open('xb') as f:torch.save(payload,f)
    hashes=dict(prediction=tensor_sha(payload['prediction']),
        **{k:tensor_sha(payload['mask_case'][k]) for k in ('protos','coefficients','boxes')},
        kernel_boxes=tensor_sha(kernel['boxes']),kernel_scores=tensor_sha(kernel['scores']),
        keep=tensor_sha(kernel['keep']),detections=tensor_sha(kernel['detections']))
    row=dict(image=image,condition=condition,filename=filename,sha256=sha(path),bytes=path.stat().st_size,
        counts=material['counts'],mask_sha256=mask_sha256,frozen_cache_sha256=frozen_row['sha256'],
        content_sha256=hashes,kernel_box_layout=signature(kernel['boxes']),kernel_score_layout=signature(kernel['scores']),
        prediction_shape=list(payload['prediction'].shape),functional_only=True)
    record(path.with_suffix('.receipt.json'),row)
    return row
