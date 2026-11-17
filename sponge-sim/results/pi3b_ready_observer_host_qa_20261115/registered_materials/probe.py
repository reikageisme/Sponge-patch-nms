"""Prepared readonly READY probe, not a replacement qualification or launcher.

Adapts READY in results/pi3b_predecessor_supervisor_qa_20261115/run_device_qa.py:48-64,
SHA256 87198d9ace7e7e071e0ede70caa9b1342183f646d3c740ed1acd3e50a82ac0e6.
Direct required-state reads adapt control.py:92-99 in
studies/pi3b_nms_predecessor_20261115, SHA256
2bf1de637d0cc317a81109773d2b915cec90bbf46337ae877db9f75c2c0251c6.
The failed source/tag/raw stay immutable. This probe never starts a process
except one readonly systemctl show. It neither sends a fault nor writes files.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

PROC=Path('/proc')
MASK_ROOT=Path('/run/systemd/system')
SERVICE='sponge-pi3b-swapguard-v2.service'


def required_state(control):
    """Read only fields actually asserted by the old READY predicate.

Do not call System.current(): it also launches four manager queries for unit
and setup fields that the old READY predicate never inspected.
"""
    return dict(governor=(control.POLICY/'scaling_governor').read_text().strip(),
        swaps=control.parse_swaps((PROC/'swaps').read_text()),
        masks={u:(MASK_ROOT/u).is_symlink() and os.readlink(MASK_ROOT/u)=='/dev/null' for u in control.UNITS})


def child_identity(ready):
    child=PROC/str(ready['child_pid'])
    stat=(child/'stat').read_text()
    head,tail=stat.rsplit(')',1)
    if int(head.split('(',1)[0])!=ready['child_pid'] or int(tail.split()[19])!=ready['child_start_ticks']:
        raise ValueError('owned child PID/birth differs')
    if (child/'cgroup').read_text().splitlines()!=['0::/system.slice/'+SERVICE]:
        raise ValueError('owned child is outside exact service cgroup')


def observe(base,name,control):
    """Return None until receipt exists; thereafter validate or raise, never PASS.

Control must be the externally verified controller package. This API does not
qualify its own source or retrofit the closed five-case result. Files/unit are
read sequentially; no atomic-snapshot or absence-of-races claim is made.
"""
    base=Path(base).resolve()
    if base!=control.HERE.resolve() or base!=control.ROOT.resolve() or not re.fullmatch('[a-z0-9_]+',name):
        raise ValueError('wrong controller workspace/case identity')
    directory=base/'runs'/name
    if directory.is_symlink() or directory.resolve().parent!=base/'runs':raise ValueError('run escapes workspace')
    path=directory/'qa_ready.json'
    if not path.exists():return None
    ready=json.loads(path.read_bytes())
    if (set(ready)!={'pid','child_pid','child_start_ticks','invocation_id','torch_imported','scipy_imported'}
        or ready['torch_imported'] is not False or ready['scipy_imported'] is not False
        or any(type(ready[k]) is not int or ready[k]<=0 for k in ('pid','child_pid','child_start_ticks'))
        or ready['pid']==ready['child_pid'] or not re.fullmatch('[0-9a-f]{32}',ready['invocation_id'])):
        raise ValueError('invalid/non-sleeping readiness receipt')
    result=subprocess.run(['systemctl','show',SERVICE,'-p','MainPID','-p','InvocationID','-p','ActiveState'],
        capture_output=True,text=True,timeout=10)
    if result.returncode:raise RuntimeError('readonly unit query failed: '+result.stderr)
    fields=dict(line.split('=',1) for line in result.stdout.splitlines())
    if (len(result.stdout.splitlines())!=3 or set(fields)!={'MainPID','InvocationID','ActiveState'}
        or fields['ActiveState']!='active' or fields['MainPID']!=str(ready['pid'])
        or fields['InvocationID']!=ready['invocation_id']):
        raise ValueError('live unit identity/state differs')
    child_identity(ready)
    now=required_state(control)
    if (now['governor']!='powersave' or now['swaps'] or set(now['masks'])!=set(control.UNITS)
        or any(x is not True for x in now['masks'].values())):
        raise ValueError('required live lease state differs')
    header=json.loads((directory/'registration.json').read_bytes())
    lock=base/'controller_lock.json'
    if (set(header)!={'tag','commit','mode','lock_sha256'} or header['mode']!='qa'
        or not re.fullmatch('[a-z0-9-]+',header['tag']) or not re.fullmatch('[0-9a-f]{40}',header['commit'])
        or header['lock_sha256']!=hashlib.sha256(lock.read_bytes()).hexdigest()):
        raise ValueError('QA registration/source binding differs')
    usb_sha=control.require_phase_storage(directory,lock,header['tag'],header['commit'],'qa')
    if usb_sha!=hashlib.sha256((directory/'usb_preflight.json').read_bytes()).hexdigest():
        raise ValueError('original USB phase receipt differs')
    child_identity(ready)  # Refuse child exit/reuse while reading the phase.
    return dict(ready=ready,unit=fields,required_state=now,usb_preflight_sha256=usb_sha,
        observed_at_utc=time.time(),sequential_not_atomic=True,manager_queries=1,
        source_qualification_performed=False)
