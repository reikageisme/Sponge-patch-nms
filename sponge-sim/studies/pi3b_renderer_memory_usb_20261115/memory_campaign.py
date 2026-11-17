# Copied/adapted from sponge-sim/studies/pi3b_renderer_memory_v1_20261114/memory_campaign.py:1-140
# SHA256 205e656469372f688088b0dc1d40b119fe6334b87304c284117a9bb6f859aa5e; closed USB-absent V1 source/runs remain immutable.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_prealloc_20261114/memory_campaign.py:1-133
# SHA256 919e518e62eb234efac35316d6b2e1cffc077cf77dcaae3f16f342cc6d85cc66; earlier QA/cache source and runs remain immutable.
"""Prepared memory-only orchestrator, no performance data recorded yet.

Parent deliberately never imports torch: two resident runtimes would compete
for Pi RAM and change the condition. Each audited worker has no child-process
creation; run_child owns and reaps that direct Popen child. Whole-campaign
parent-death/descendant cleanup still REQUIRES the independent systemd wrapper
and actual-device QA, not supplied or claimed by the host direct-child tests.
"""
from pathlib import Path
import json
import os
import platform
import random
import subprocess
import sys
import time
from cache import record,sha,validate_manifest
from memory_worker import registration,ARMS,SERVICE,IMAGE_IDS,phase_spec,CACHE_DIRECTORY,load_usb_preflight


def schedule(image_ids,seed):
    jobs=[]
    for image in image_ids:
        ix=IMAGE_IDS.index(image)
        for rep in range(3):
            block=[(condition,arm) for condition in ('clean','adv') for arm in ARMS]
            random.Random(seed+1000*ix+rep).shuffle(block)
            jobs += [dict(index=len(jobs)+j,image=image,condition=c,arm=a,rep=rep) for j,(c,a) in enumerate(block)]
    return jobs


def run_child(argv,jobdir,timeout_seconds,check,interval=2.0):
    """Bounded direct-child lease. On any failure terminate/kill and always wait."""
    jobdir=Path(jobdir);jobdir.mkdir(parents=True,exist_ok=False)
    record(jobdir/'intent.json',dict(argv=list(argv),timeout_seconds=timeout_seconds,direct_child_only=True))
    proc=None;reason=None;code=None;forced=False
    try:
        if timeout_seconds<=0 or interval<=0:raise ValueError('positive finite watchdog bounds required')
        check()
        with (jobdir/'stdout.log').open('x',encoding='utf-8') as out:
            proc=subprocess.Popen(argv,stdout=out,stderr=subprocess.STDOUT)
            record(jobdir/'started.json',dict(pid=proc.pid,owned_direct_child=True))
            deadline=time.monotonic()+timeout_seconds
            while True:
                check()
                remaining=deadline-time.monotonic()
                if remaining<=0:raise TimeoutError('child exceeded registered deadline')
                try:
                    code=proc.wait(timeout=min(interval,remaining));break
                except subprocess.TimeoutExpired:pass
            check()
            if code!=0:raise RuntimeError('memory child failed: '+str(code))
    except BaseException as exc:
        reason=dict(error=type(exc).__name__,message=str(exc))
        raise
    finally:
        try:
            if proc is not None and proc.poll() is None:
                forced=True;proc.terminate()
                try:proc.wait(timeout=3)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=3)
            if proc is not None:code=proc.returncode
        finally:
            record(jobdir/'terminal.json',dict(status='FAILED_STOPPED_NO_RETRY' if reason else 'COMPLETED',
                returncode=code,owned_pid=proc.pid if proc else None,direct_child_reaped=proc is None or proc.poll() is not None,
                termination_sent=forced,failure=reason,latency_endpoint_recorded=False))
    return code


def collect(args):
    workspace=Path.home()/'sponge-sim/pi3b_renderer_memory_usb_20261115'
    if args.output.resolve().parent.parent!=workspace/'runs' or args.output.name!='memory':raise ValueError('new campaign output workspace required')
    if platform.system()!='Linux' or platform.machine()!='aarch64' or not os.environ.get('INVOCATION_ID'):
        raise RuntimeError('new supervised Pi scientific campaign required')
    if SERVICE not in Path('/proc/self/cgroup').read_text():raise RuntimeError('outside scientific cgroup')
    reg=registration(args.registration,args.tag,args.commit)
    phase=getattr(args,'phase','smoke');spec=phase_spec(reg,phase)
    usb_baseline,usb_sha=load_usb_preflight(args.output.parent/'usb_preflight.json',
        args.tag,args.commit,phase,sha(args.registration),reg['usb_contract'])
    if args.output.parent.name!='memory_'+phase+'_01':raise ValueError('one fixed run per phase')
    if args.cache.resolve()!=Path(CACHE_DIRECTORY):raise ValueError('registered cache directory required')
    if sha(args.cache/'manifest.json')!=reg['cache_manifest_sha256']:raise ValueError('cache manifest differs')
    manifest=json.loads((args.cache/'manifest.json').read_text(encoding='utf-8'))
    cases=validate_manifest(manifest,reg['image_ids']);case_by={(r['image'],r['condition']):r for r in cases}
    os.sched_setaffinity(0,reg['cpus'])
    from guard import read_fast,violations
    initial=read_fast()
    args.output.mkdir(parents=True,exist_ok=False)
    record(args.output/'registration.json',dict(tag=args.tag,commit=args.commit,lock_sha256=sha(args.registration),
        cache_manifest_sha256=reg['cache_manifest_sha256'],parent_torch_imported='torch' in sys.modules,phase=phase,
        usb_preflight_sha256=usb_sha))
    if 'torch' in sys.modules:raise RuntimeError('collector must not retain a second torch runtime')
    jobs=schedule(spec['image_ids'],reg['seed']);record(args.output/'schedule.json',jobs)
    done=[];deadline=time.monotonic()+spec['campaign_timeout_seconds']
    with (args.output/'raw.jsonl').open('x',encoding='utf-8') as raw, (args.output/'guards.jsonl').open('x',encoding='utf-8') as log:
        def check():
            fast=read_fast();problems=violations(fast,reg,reg['cpus'],initial['vmstat'],usb_baseline)
            log.write(json.dumps(dict(wall_utc=time.time(),fast=fast,violations=problems))+'\n');log.flush()
            if problems:raise RuntimeError('parent condition guard: '+str(problems))
            if time.monotonic()>=deadline:raise TimeoutError('memory campaign deadline')
        def actual_clock():
            r=subprocess.run(['vcgencmd','measure_clock','arm'],capture_output=True,text=True,timeout=5)
            hz=int(r.stdout.strip().split('=')[1])
            if r.returncode or not reg['gates']['clock_hz'][0]<=hz<=reg['gates']['clock_hz'][1]:
                raise RuntimeError('actual clock outside registered band')
            log.write(json.dumps(dict(wall_utc=time.time(),actual_arm_hz=hz))+'\n');log.flush()
        try:
            check()
            for job in jobs:
                check();actual_clock();jobdir=args.output/'jobs'/f"{job['index']:04d}";out=jobdir/'memory.json'
                argv=[sys.executable,str(Path(__file__).with_name('memory_worker.py')),'--registration',str(args.registration),
                      '--cache',str(args.cache),'--tag',args.tag,'--commit',args.commit,'--image',job['image'],
                      '--condition',job['condition'],'--arm',job['arm'],'--out',str(out)]
                run_child(argv,jobdir,min(reg['child_timeout_seconds'],deadline-time.monotonic()),check)
                result=json.loads(out.read_text(encoding='utf-8'))
                started=json.loads((jobdir/'started.json').read_text(encoding='utf-8'))
                expected=case_by[(job['image'],job['condition'])]
                if (result['status']!='COMPLETED' or any(result[k]!=job[k] for k in ('image','condition','arm'))
                    or result['cache_sha256']!=expected['sha256'] or result['mask_sha256']!=expected['mask_sha256']
                    or result['tag']!=args.tag or result['commit']!=args.commit
                    or result['registration_sha256']!=sha(args.registration)
                    or result['phase']!=phase
                    or result['usb_preflight_sha256']!=usb_sha
                    or result['pid']!=started['pid'] or result['sample_point']!=reg['sample_point']
                    or result['incremental_renderer_peak'] is not False or result['latency_endpoint_recorded'] is not False
                    or type(result['ru_maxrss_kib']) is not int or result['ru_maxrss_kib']<=0
                    or result['ru_maxrss_bytes']!=1024*result['ru_maxrss_kib']):
                    raise ValueError('child result identity/RSS/parity contract differs')
                actual_clock();check()
                raw.write(json.dumps(dict(job=job,result=result))+'\n');raw.flush();os.fsync(raw.fileno())
                done.append(job['index'])
            record(args.output/'terminal.json',dict(status='COMPLETED_PENDING_AUDIT',jobs=len(done),latency_endpoint_recorded=False))
        except BaseException as exc:
            record(args.output/'terminal.json',dict(status='FAILED_STOPPED_NO_RETRY',completed_jobs=done,error=type(exc).__name__,message=str(exc)))
            raise


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--registration',required=True,type=Path);p.add_argument('--cache',required=True,type=Path)
    p.add_argument('--tag',required=True);p.add_argument('--commit',required=True);p.add_argument('--output',required=True,type=Path);p.add_argument('--phase',choices=('smoke','full'),default='smoke')
    collect(p.parse_args())
