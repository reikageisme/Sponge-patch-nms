# Adapted from sponge-sim/studies/pi3b_renderer_prealloc_20261114/build_cache.py:1-115
# SHA256 fd6bb449fc6c14215fac98c7893d4d33c3f510557c7e475308e7db94c5b5d5c6; previous cache files/source immutable.
"""Prepared ONE persistent-model functional export, never a timing worker.

Model/input preparation adapts pi3b_renderer_prealloc_20261114/build_cache.py;
file/range/SHA are frozen by build_controller_lock.py before device access.
Both clean+adv materials remain resident within each image's export block.
"""
from pathlib import Path
import argparse
import gc
import json
import os
import platform
import re
import shutil
import subprocess
import time
from bindings import HERE,ROOT,SERVICE,sha,load,read_lock,activation,load_usb_preflight,valid_identity
from cache import record,load_case,validate_manifest,compare_outputs
from guard import read_fast,violations
from schedule import IMAGE_IDS


def actual_clock():
    r=subprocess.run(['vcgencmd','measure_clock','arm'],capture_output=True,text=True,timeout=5)
    match=re.fullmatch(r'frequency\(48\)=([0-9]+)\n?',r.stdout)
    if r.returncode or not match:raise ValueError('actual clock readback failed')
    return int(match.group(1))


def main(directory,tag,commit):
    directory=Path(directory).resolve();valid_identity(tag,commit)
    if (HERE!=ROOT.resolve() or directory!=ROOT/'runs/material_01/functional'
        or directory.exists() or not os.environ.get('INVOCATION_ID')
        or platform.system()!='Linux' or platform.machine()!='aarch64'):
        raise RuntimeError('one new native supervised functional workspace required')
    lock=read_lock();act=activation()
    if tag!=act['tag']:raise ValueError('functional tag differs')
    group=Path('/proc/self/cgroup').read_text()
    if '/'+SERVICE not in group:raise ValueError('functional child is outside owned service')
    parent=directory.parent;context=load(parent/'worker_context.json')
    if context['tag']!=tag or context['commit']!=commit:raise ValueError('worker context identity differs')
    usb,usb_sha=load_usb_preflight(parent/'usb_preflight.json',tag,commit,'functional',sha(HERE/'controller_lock.json'),lock['usb_contract'])
    if usb_sha!=context['usb_preflight_sha256']:raise ValueError('worker USB context differs')
    directory.mkdir(exist_ok=False)
    checks=0;rows=[]
    def check(label='functional_step'):
        nonlocal checks
        frame=read_fast();errors=violations(frame,lock,[0,1,2,3],context['baseline_vmstat'],usb)
        clock=actual_clock()
        if not lock['gates']['clock_hz'][0]<=clock<=lock['gates']['clock_hz'][1]:errors.append('actual_clock')
        if shutil.disk_usage(directory).free<128*2**20:errors.append('disk_space')
        with (directory/'guards.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(wall_utc=time.time(),sequence=checks,label=label,fast=frame,actual_arm_hz=clock,violations=errors))+'\n');f.flush()
        checks+=1
        if errors:raise RuntimeError('functional child guard: '+str(errors))
    try:
        check('start')
        source=load(HERE/'full20_lock.json');cache_manifest=load(HERE/'cache_manifest.json')
        expected={x['name']:x['sha256'] for x in source['files']}
        materials=Path('/home/tanh/sponge-sim/pi3b_full20_20261114')
        cache=Path('/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/caches/cache_01')
        cases=validate_manifest(cache_manifest,list(IMAGE_IDS));by_case={(x['image'],x['condition']):x for x in cases}
        if [x.split('_')[0] for x in source['inputs']]!=list(IMAGE_IDS):raise ValueError('source cohort differs')
        for name in [source['weights'],*source['inputs']]:
            if sha(materials/name)!=expected[name]:raise ValueError('old source material changed: '+name)
            check('material_hash')
        if sha(cache/'manifest.json')!=sha(HERE/'cache_manifest.json'):raise ValueError('original cache manifest changed')
        import bracket
        bracket.setup_resources()
        import torch
        torch.set_num_threads(4);torch.set_num_interop_threads(1)
        import torchvision
        import ultralytics
        import numpy as np
        from ultralytics import YOLO
        from ultralytics.utils import nms,ops
        from baseline_ops import process_mask_native
        from preallocate import process_mask_preallocated
        import material,exports,inventory
        versions=dict(torch=str(torch.__version__),torchvision=str(torchvision.__version__),ultralytics=ultralytics.__version__,numpy=np.__version__,python=platform.python_version())
        if versions!=source['versions'] or sha(nms.__file__)!=source['nms_source_sha256'] or sha(ops.__file__)!=source['ops_source_sha256']:
            raise ValueError('actual loaded Pi runtime/source differs')
        if not hasattr(torch.ops.torchvision,'nms'):raise ValueError('fixed backend unavailable')
        record(directory/'registration.json',dict(tag=tag,commit=commit,mode='functional',versions=versions,
            controller_lock_sha256=sha(HERE/'controller_lock.json'),activation_sha256=sha(HERE/'functional_activation.json'),
            usb_preflight_sha256=usb_sha,model_resident=True,clean_adv_materials_resident_together=True,
            resource_bound_before_torch=True,empirical_endpoint_recorded=False))
        check('before_model')
        net=YOLO(str(materials/source['weights'])).model.eval().float().cpu()
        for p in net.parameters():p.requires_grad_(False)
        with torch.inference_mode():
            for image,name in zip(IMAGE_IDS,source['inputs']):
                check('before_pair_load')
                pair=torch.load(materials/name,map_location='cpu',weights_only=True)
                clean,adv=pair['clean'].contiguous(),pair['attacked'].contiguous()
                if any(tuple(t.shape)!=(1,3,640,640) or t.dtype!=torch.float32 or t.device.type!='cpu' or not bool(torch.isfinite(t).all()) for t in (clean,adv)):
                    raise ValueError('frozen image tensor contract differs')
                if min(float(clean.min()),float(adv.min()))<0 or max(float(clean.max()),float(adv.max()))>1 or float((adv-clean).abs().max())>16/255+1e-6:
                    raise ValueError('frozen range/perturbation differs')
                prepared={}
                for condition,tensor in (('clean',clean),('adv',adv)):
                    check('before_forward')
                    raw=net(tensor);check('after_forward')
                    frozen=load_case(cache,by_case[(image,condition)])
                    prepared[condition]=material.prepare(raw,frozen,by_case[(image,condition)],nms,torchvision.ops)
                    if tuple(prepared[condition]['prediction'].shape)!=(1,116,8400):raise ValueError('native anchor shape differs')
                    del raw,frozen;gc.collect();check('material_prepared')
                pool=inventory.snapshot()
                if not pool['complete_stable_set'] or any(t['affinity']!=[0,1,2,3] for t in pool['threads'].values()):
                    raise ValueError('functional all-thread affinity/identity differs')
                record(directory/f'{image}_pool.json',pool)
                for condition in ('clean','adv'):
                    item=prepared[condition];row=by_case[(image,condition)]
                    digest=compare_outputs(item['mask_case'],process_mask_native,process_mask_preallocated,check)
                    if digest!=row['mask_sha256']:raise ValueError('fresh renderer digest differs from frozen cache')
                    rows.append(exports.save(directory,image,condition,item,digest,row));check('exported')
                del prepared,pair,clean,adv,item,tensor;gc.collect();check('block_end')
        if [(r['image'],r['condition']) for r in rows]!=[(im,c) for im in IMAGE_IDS for c in ('clean','adv')]:raise ValueError('incomplete material export')
        record(directory/'manifest.json',dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=rows,empirical_endpoint_recorded=False,
            source_lock_sha256=sha(HERE/'full20_lock.json'),cache_manifest_sha256=sha(HERE/'cache_manifest.json'),versions=versions))
        check('end')
        record(directory/'terminal.json',dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False))
        return 0
    except BaseException as exc:
        record(directory/'terminal.json',dict(status='FAILED_NO_RETRY',error=type(exc).__name__,message=str(exc),completed_cases=len(rows)))
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',required=True);p.add_argument('--tag',required=True);p.add_argument('--commit',required=True)
    a=p.parse_args();raise SystemExit(main(a.directory,a.tag,a.commit))
