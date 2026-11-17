"""Torch-free parent with watchdog guards for one functional material worker."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
from bindings import HERE,sha,load,load_usb_preflight
from guard import read_fast,violations
from cache import record


def collect(directory,tag,commit):
    directory=Path(directory)
    lock=load(HERE/'controller_lock.json');contract=load(HERE/'usb_contract.json')
    usb,usb_sha=load_usb_preflight(directory/'usb_preflight.json',tag,commit,'functional',sha(HERE/'controller_lock.json'),contract)
    baseline=read_fast()['vmstat']
    record(directory/'worker_context.json',dict(tag=tag,commit=commit,baseline_vmstat=baseline,usb_preflight_sha256=usb_sha))
    def check():
        frame=read_fast();errors=violations(frame,lock,[0,1,2,3],baseline,usb)
        with (directory/'parent_guards.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(wall_utc=time.time(),fast=frame,violations=errors))+'\n');f.flush()
        if errors:raise RuntimeError('parent physical guard: '+str(errors))
    check();proc=None;error=None;returncode=None;forced=False
    try:
        argv=[sys.executable,str(HERE/'worker.py'),'--directory',str(directory/'functional'),'--tag',tag,'--commit',commit]
        with (directory/'worker.stdout.log').open('x',encoding='utf-8') as log:
            proc=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT)
            ticks=int(Path(f'/proc/{proc.pid}/stat').read_text().rsplit(')',1)[1].split()[19])
            record(directory/'worker_started.json',dict(pid=proc.pid,start_ticks=ticks,argv=argv))
            deadline=time.monotonic()+3600
            while True:
                check();left=deadline-time.monotonic()
                if left<=0:raise TimeoutError('functional worker campaign limit')
                try:returncode=proc.wait(timeout=min(2,left));break
                except subprocess.TimeoutExpired:pass
            check()
            if returncode!=0:raise RuntimeError('functional worker failed: '+str(returncode))
    except BaseException as exc:
        error=dict(error=type(exc).__name__,message=str(exc));raise
    finally:
        if proc is not None and proc.poll() is None:
            forced=True;proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=3)
        record(directory/'worker_terminal.json',dict(status='COMPLETED' if error is None and returncode==0 else 'FAILED_NO_RETRY',
            returncode=None if proc is None else proc.returncode,error=error,termination_sent=forced,direct_child_reaped=proc is not None and proc.poll() is not None))
    if 'torch' in sys.modules:raise RuntimeError('parent imported Torch')
    result=load(directory/'functional/terminal.json')
    if result!=dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False):
        raise ValueError('functional cohort did not complete')
