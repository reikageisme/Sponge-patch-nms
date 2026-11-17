# Copied/adapted from sponge-sim/studies/pi3b_renderer_memory_v1_20261114/memory_worker.py:1-143
# SHA256 19599b0aee6e2bd3f40a75ff336d1680137f035399e8c32c49361f10f6c6d256; closed USB-absent V1 source/runs remain immutable.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_prealloc_20261114/memory_worker.py:1-125
# SHA256 8e0a047a67a1f498ea1257b53e5049add177d3fe738e7d2d352a68c8d5704b5e; earlier QA/cache source and runs remain immutable.
"""One fresh Linux process per case/renderer; no latency endpoint.

Not runnable until a new scientific registration and supervised lease exist.
Endpoint: Linux whole-process high-water RSS sampled AFTER output digest,
including imports, cache load/validation, warm-up, rendering and hashing.
It is not renderer-only or incremental peak memory. No model is loaded here.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import re
import sys

HERE=Path(__file__).resolve().parent
SERVICE='sponge-pi3b-swapguard-v2.service'
ARMS=('baseline_A','baseline_B','candidate16M')
IMAGE_IDS=[f'{n:012d}' for n in (9,25,30,34,36,42,49,61,64,71,72,73,74,77,78,81,86,89,92,94)]
SOURCE_FILES={'memory_worker.py','cache.py','baseline_ops.py','preallocate.py','memory_campaign.py','guard.py',
              'control.py','analyze_memory.py','stats_frozen.py','usb_guard.py'}
CACHE_DIRECTORY='/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/caches/cache_01'
PHASES={
    'smoke':dict(image_ids=[IMAGE_IDS[0],IMAGE_IDS[2]],jobs=36,campaign_timeout_seconds=3600,precision_enforced=False),
    'full':dict(image_ids=IMAGE_IDS,jobs=360,campaign_timeout_seconds=21600,precision_enforced=True)}


def phase_spec(reg,phase):
    if phase not in PHASES or reg['phases']!=PHASES:raise ValueError('registered phase schedule differs')
    return reg['phases'][phase]


def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for v in iter(lambda:f.read(1024*1024),b''):h.update(v)
    return h.hexdigest()


def registration(path,tag,commit):
    value=json.loads(Path(path).read_text(encoding='utf-8'))
    if value['experiment']!='PI3B-RENDERER-MEMORY-USB' or value['status']!='PREREGISTERED':
        raise ValueError('new completed scientific registration required')
    if tag!=value['tag'] or not tag.startswith('prereg-pi3b-renderer-memory-usb-') or not re.fullmatch('[0-9a-f]{40}',commit):
        raise ValueError('registration identity differs')
    if value['arms']!=list(ARMS) or value['repeats']!=3 or value['pixel_budget']!=16_000_000:
        raise ValueError('registered condition differs')
    if value['cpus']!=[0,1,2,3] or value['interop_threads']!=1:
        raise ValueError('registered affinity/threads differ')
    if value['image_ids']!=IMAGE_IDS:
        raise ValueError('registered cohort differs')
    sources=value['source_sha256']
    if set(sources)!=SOURCE_FILES:raise ValueError('incomplete source binding')
    for name,digest in sources.items():
        if file_sha(HERE/name)!=digest:raise ValueError('registered source changed: '+name)
    if value['versions']!=dict(torch='2.15.0+cpu',numpy='2.5.4',python='3.13.5'):
        raise ValueError('actual Pi runtime contract differs')
    if value['governor']!='powersave' or value['gates']['clock_hz']!=[594000000,606000000]:
        raise ValueError('declared frequency condition differs')
    if value['gates']['abort_temp_c']!=75 or value['gates']['abort_mem_available_kb']!=40000:
        raise ValueError('safety thresholds differ')
    if value['sample_point']!='after_render_and_output_digest' or value['warmup']!='same_renderer_K1_if_available_once':
        raise ValueError('RSS endpoint differs')
    if value['conditions']!=['clean','adv'] or value['child_timeout_seconds']!=180 or value['phases']!=PHASES:
        raise ValueError('finite schedule or deadline differs')
    if value['seed']!=20261114 or value['gates']['aa_abs_log']!=.02 or value['gates']['mde_log']!=.05:
        raise ValueError('prospective randomization/precision gates differ')
    if not re.fullmatch('[0-9a-f]{64}',value['cache_manifest_sha256']):raise ValueError('missing cache manifest binding')
    if value['mde_t_critical_sums']!={'2':14.082586656645868,'20':2.9539746046772377}:raise ValueError('MDE constants differ')
    if value['cache_directory']!=CACHE_DIRECTORY or value['cache_manifest_sha256']!='61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165':
        raise ValueError('wrong immutable cache cohort')
    if (value['usb_contract_sha256']!=file_sha(HERE/'usb_contract.json')
        or value['usb_contract']!=json.loads((HERE/'usb_contract.json').read_text(encoding='utf-8'))):
        raise ValueError('USB contract changed')
    return value


def load_usb_preflight(path,tag,commit,phase,lock_sha256,contract):
    """Read the exact frontend frame once; shared by payload/children/auditor."""
    import usb_guard
    raw=Path(path).read_bytes();info=json.loads(raw)
    if info!=dict(tag=tag,commit=commit,phase=phase,lock_sha256=lock_sha256,
                  usb_contract_sha256=file_sha(HERE/'usb_contract.json'),snapshot=info.get('snapshot')):
        raise ValueError('USB preflight binding differs')
    if phase not in ('qa','smoke','full') or usb_guard.validate(info['snapshot'],contract):
        raise ValueError('invalid/non-idle USB preflight')
    return info['snapshot'],hashlib.sha256(raw).hexdigest()


def main(args):
    if args.out.exists() or args.arm not in ARMS:raise ValueError('new output and a registered arm required')
    workspace=Path.home()/'sponge-sim/pi3b_renderer_memory_usb_20261115'
    parts=args.out.resolve().relative_to(workspace).parts
    if len(parts)!=6 or parts[0]!='runs' or parts[2:4]!=('memory','jobs') or not re.fullmatch('[0-9]{4}',parts[4]) or parts[5]!='memory.json':
        raise ValueError('output must be a new owned campaign job receipt')
    names={'memory_smoke_01':'smoke','memory_full_01':'full'}
    if parts[1] not in names:raise ValueError('only one smoke and one full allowed')
    phase=names[parts[1]]
    if platform.system()!='Linux' or platform.machine()!='aarch64' or not os.environ.get('INVOCATION_ID'):
        raise RuntimeError('new Pi systemd-supervised scientific campaign required')
    if SERVICE not in Path('/proc/self/cgroup').read_text():
        raise RuntimeError('outside the registered control group')
    reg=registration(args.registration,args.tag,args.commit)
    usb_baseline,usb_sha=load_usb_preflight(workspace/'runs'/parts[1]/'usb_preflight.json',
        args.tag,args.commit,phase,file_sha(args.registration),reg['usb_contract'])
    if args.image not in phase_spec(reg,phase)['image_ids']:raise ValueError('image outside the prospective phase')
    if args.cache.resolve()!=Path(CACHE_DIRECTORY):raise ValueError('only read the registered cache directory')
    os.sched_setaffinity(0,reg['cpus'])
    for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[name]='4'
    from guard import read_fast,violations
    start=read_fast();problems=violations(start,reg,reg['cpus'],usb_baseline=usb_baseline)
    if problems:raise RuntimeError('memory child pre-import condition: '+str(problems))
    import torch
    import numpy as np
    import resource
    from cache import load_case,mask_sha,validate_manifest,record
    from baseline_ops import process_mask_native
    from preallocate import process_mask_preallocated
    torch.set_num_threads(4);torch.set_num_interop_threads(1)
    if dict(torch=str(torch.__version__),numpy=np.__version__,python=sys.version.split()[0])!=reg['versions']:
        raise ValueError('memory child runtime differs')
    manifest_path=args.cache/'manifest.json'
    if file_sha(manifest_path)!=reg['cache_manifest_sha256']:raise ValueError('cache manifest changed')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    cases=validate_manifest(manifest,reg['image_ids'])
    row=next(r for r in cases if r['image']==args.image and r['condition']==args.condition)
    case=load_case(args.cache,row)
    ready=read_fast();problems=violations(ready,reg,reg['cpus'],start['vmstat'],usb_baseline)
    if problems:raise RuntimeError('memory child pre-render condition: '+str(problems))
    fn=process_mask_preallocated if args.arm=='candidate16M' else process_mask_native
    with torch.inference_mode():
        if row['k']:
            warm=fn(case['protos'],case['coefficients'][:1],case['boxes'][:1],(640,640))
            del warm
        mask=fn(case['protos'],case['coefficients'],case['boxes'],(640,640))
        if tuple(mask.shape)!=(row['k'],640,640):raise ValueError('renderer shape changed')
        digest=mask_sha(mask)
        peak=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        del mask
    if digest!=row['mask_sha256']:raise ValueError('mask parity differs')
    end=read_fast();problems=violations(end,reg,reg['cpus'],start['vmstat'],usb_baseline)
    if problems:raise RuntimeError('memory child postcondition: '+str(problems))
    if peak<=0:raise ValueError('missing Linux RSS high-water value')
    record(args.out,dict(status='COMPLETED',pid=os.getpid(),image=args.image,condition=args.condition,arm=args.arm,
        phase=phase,tag=args.tag,commit=args.commit,registration_sha256=file_sha(args.registration),cache_sha256=row['sha256'],
        usb_preflight_sha256=usb_sha,
        mask_sha256=digest,ru_maxrss_kib=peak,ru_maxrss_bytes=peak*1024,
        sample_point=reg['sample_point'],includes_import_validation_warmup_hash=True,
        incremental_renderer_peak=False,latency_endpoint_recorded=False,guards=dict(start=start,ready=ready,end=end)))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--registration',required=True,type=Path);p.add_argument('--cache',required=True,type=Path)
    p.add_argument('--tag',required=True);p.add_argument('--commit',required=True)
    p.add_argument('--image',required=True);p.add_argument('--condition',choices=('clean','adv'),required=True)
    p.add_argument('--arm',choices=ARMS,required=True);p.add_argument('--out',type=Path,required=True)
    main(p.parse_args())
