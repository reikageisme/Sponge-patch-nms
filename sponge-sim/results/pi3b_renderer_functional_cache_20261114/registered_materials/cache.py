"""Immutable renderer-case files and finite parity, never a performance endpoint."""
from pathlib import Path
import gc
import hashlib
import json
import re

CASE_RE=re.compile(r'[0-9]{12}_(?:clean|adv)\.pt')
TENSOR_KEYS=('protos','coefficients','boxes')


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def record(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False)


def mask_sha(mask):
    import torch
    if mask.dtype!=torch.uint8 or mask.device.type!='cpu' or not mask.is_contiguous():
        raise ValueError('hash requires contiguous CPU uint8 output; no full-size conversion')
    # numpy shares storage; avoid .tobytes(), which duplicates a potentially 117MiB mask.
    if mask.numel()==0:return hashlib.sha256(b'').hexdigest()
    return hashlib.sha256(memoryview(mask.numpy()).cast('B')).hexdigest()


def validate_case(case):
    import torch
    if not isinstance(case,dict) or set(case)!=set((*TENSOR_KEYS,'shape')):
        raise ValueError('unexpected cache schema')
    if tuple(case['shape'])!=(640,640):raise ValueError('output resolution differs')
    p,c,b=(case[k] for k in TENSOR_KEYS)
    if not all(torch.is_tensor(v) and v.dtype==torch.float32 and v.device.type=='cpu'
               and v.is_contiguous() and bool(torch.isfinite(v).all()) for v in (p,c,b)):
        raise ValueError('cache requires finite contiguous CPU FP32 tensors')
    if tuple(p.shape)!=(32,160,160) or c.ndim!=2 or c.shape[1]!=32:
        raise ValueError('prototype or coefficient shape differs')
    k=c.shape[0]
    if not 0<=k<=300 or tuple(b.shape)!=(k,4):raise ValueError('box/count contract differs')
    return k


def compare_outputs(case,baseline,candidate,check=lambda:None):
    """Hash sequentially; never retain both full output stacks simultaneously."""
    import torch
    k=validate_case(case)
    results=[]
    for fn in (baseline,candidate):
        check()
        with torch.inference_mode():mask=fn(case['protos'],case['coefficients'],case['boxes'],tuple(case['shape']))
        if tuple(mask.shape)!=(k,640,640):raise ValueError('renderer returned wrong shape')
        results.append(mask_sha(mask))
        del mask
        gc.collect()
        check()
    if results[0]!=results[1]:raise ValueError('baseline/candidate mask parity failure')
    return results[0]


def save_case(directory,image,condition,case,mask_digest,counts):
    import torch
    filename=f'{image}_{condition}.pt'
    if not CASE_RE.fullmatch(filename):raise ValueError('invalid cache identity')
    k=validate_case(case)
    if k!=counts['k'] or not re.fullmatch('[0-9a-f]{64}',mask_digest):raise ValueError('count/hash differs')
    target=Path(directory)/filename
    with target.open('xb') as f:torch.save(case,f)
    return dict(image=image,condition=condition,filename=filename,sha256=sha(target),
                k=k,shape=[640,640],mask_sha256=mask_digest,counts=counts)


def load_case(directory,row):
    import torch
    directory=Path(directory).resolve()
    name=row['filename']
    if not isinstance(name,str) or not CASE_RE.fullmatch(name):raise ValueError('invalid cache path')
    if name!=f"{row['image']}_{row['condition']}.pt":raise ValueError('cache identity differs')
    path=directory/name
    if path.resolve().parent!=directory or path.is_symlink():raise ValueError('cache escapes its directory')
    if sha(path)!=row['sha256']:raise ValueError('cache bytes changed')
    case=torch.load(path,map_location='cpu',weights_only=True)
    if validate_case(case)!=row['k'] or list(case['shape'])!=row['shape']:
        raise ValueError('cache metadata differs')
    return case


def validate_manifest(manifest,expected_ids):
    if len(expected_ids)!=20 or len(set(expected_ids))!=20 or any(not re.fullmatch('[0-9]{12}',im) for im in expected_ids):
        raise ValueError('exactly 20 unique frozen image identities required')
    rows=manifest['cases']
    expected=[(im,arm) for im in expected_ids for arm in ('clean','adv')]
    if [(r['image'],r['condition']) for r in rows]!=expected:
        raise ValueError('cache cohort/order incomplete or duplicated')
    if manifest['status']!='COMPLETED_FUNCTIONAL_PARITY_ONLY' or manifest['empirical_endpoint_recorded'] is not False:
        raise ValueError('not a completed functional-only cache')
    for row in rows:
        if not CASE_RE.fullmatch(row['filename']) or row['filename']!=f"{row['image']}_{row['condition']}.pt":
            raise ValueError('cache filename identity differs')
        if any(not re.fullmatch('[0-9a-f]{64}',row[k]) for k in ('sha256','mask_sha256')):
            raise ValueError('invalid SHA in cache manifest')
        if type(row['k']) is not int or not 0<=row['k']<=300 or row['shape']!=[640,640]:
            raise ValueError('cache shape/count differs')
    return rows
