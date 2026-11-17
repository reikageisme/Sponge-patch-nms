# Supervisor/Lease prefix copied from sponge-sim/studies/pi3b_renderer_memory_usb_20261115/control.py:1-212
# Full source SHA256 a52289f20dc41a2c4a118aca2a486a8c217863a95bc1180e0b3b89b8d38df359; System/Lease/record/validate_snapshot AST kept.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_memory_v1_20261114/control.py:1-338
# SHA256 4652c4684e2b930529e392f7b4b5f5984c9bbc56846795f0f2dee75d6b9ffa4b; closed USB-absent V1 source/runs remain immutable.
# Copied/adapted from sponge-sim/studies/pi3b_renderer_prealloc_20261114/control.py:1-342
# SHA256 7c0c197ad8689d98c5f4845a4d15fb57bc81d5722a28c100723a263576d15a92; earlier QA/cache source and runs remain immutable.
# Copied from sponge-sim/studies/pi3b_full20_20261114/control.py:1-334
# SHA256 53bb13694bb56a7e5a01a1267c666c397da95bb74aa5c43a77dce529cf518e72; record/System/Lease/validate_snapshot preserved, new prepared entry points below.
# Copied from sponge-sim/studies/pi3b_600mhz_swapguard_v2/control.py:1-325
# SHA256 3204b60139c4b044e185890285e658540e649dbb3bcce711ff2330a75b1ffd38; parent protocol remains CLOSED and immutable.
"""Finite Pi campaign and reversible swap lease, supervised by systemd.

Supersedes studies/pi3b_600mhz/campaign.sh:1-40 (SHA256
262617ea1aecfd8454cdf67deb5144146df3ab2512d9c76d2cb4241528e45095).
Only the three named runtime unit masks and CPU governor may change.
ExecStopPost runs independently after campaign exit/SIGKILL/timeout. No inference
is permitted from an ordinary unsupervised invocation of the payload command.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from guard import UNITS, POLICY, parse_swaps

HERE = Path(__file__).resolve().parent
ROOT = Path.home() / 'sponge-sim' / 'pi3b_nms_predecessor_20261115'
SERVICE = 'sponge-pi3b-swapguard-v2'


def record(path, value, exclusive=False):
    """Exclusive scientific receipts; atomic replace ONLY for the operational journal."""
    path = Path(path)
    if exclusive:
        with path.open('x', encoding='utf-8') as f:
            json.dump(value, f, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
    else:
        temporary = path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as f:
            json.dump(value, f, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
        if os.name == 'posix':
            fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)


class System:
    def command(self, *argv, input=None):
        result = subprocess.run(list(argv), input=input, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(f'{list(argv)}: rc={result.returncode}; {result.stderr.strip()}')
        return result.stdout

    def ctl(self, *argv):
        return self.command('sudo', '-n', 'systemctl', *argv)

    def snapshot(self):
        units = {}
        for u in UNITS:
            text = self.command('systemctl','show',u,'-p','ActiveState','-p','LoadState','-p','FragmentPath')
            units[u] = dict(line.split('=',1) for line in text.splitlines() if '=' in line)
            for base in ('/run/systemd/system','/etc/systemd/system'):
                p = Path(base) / u
                if p.exists() or p.is_symlink():
                    raise RuntimeError(f'preexisting override/mask: {p}; no changes made')
        setup=dict(line.split('=',1) for line in self.command('systemctl','show','systemd-zram-setup@zram0.service',
                   '-p','ActiveState','-p','Result').splitlines() if '=' in line)
        return dict(governor=(POLICY/'scaling_governor').read_text().strip(), units=units,setup=setup,
                    swaps=parse_swaps(Path('/proc/swaps').read_text()),
                    mem_available_kb=next(int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines()
                                          if x.startswith('MemAvailable:')))

    def governor(self, name):
        if name not in ('ondemand','powersave','performance','schedutil','conservative','userspace'):
            raise ValueError('unrecognized governor')
        self.command('sudo','-n','tee',str(POLICY/'scaling_governor'),input=name+'\n')

    def current(self):
        return dict(governor=(POLICY/'scaling_governor').read_text().strip(),
                    swaps=parse_swaps(Path('/proc/swaps').read_text()),
                    masks={u:(Path('/run/systemd/system')/u).is_symlink()
                           and os.readlink(Path('/run/systemd/system')/u)=='/dev/null' for u in UNITS},
                    active={u:self.command('systemctl','show',u,'-p','ActiveState','--value').strip() for u in UNITS},
                    setup=dict(line.split('=',1) for line in self.command('systemctl','show','systemd-zram-setup@zram0.service',
                        '-p','ActiveState','-p','Result').splitlines() if '=' in line))


def validate_snapshot(s):
    if s['governor'] not in ('ondemand','powersave','performance','schedutil','conservative','userspace'):
        raise ValueError('unsupported original governor')
    swaps = s['swaps']
    if len(swaps)>1 or any(r['name']!='/dev/zram0' or r['kind']!='partition' or r['priority']!=100 for r in swaps):
        raise ValueError('unsupported swap topology')
    if s['mem_available_kb'] < 80000 + 2 * sum(r['used_kb'] for r in swaps):
        raise ValueError('insufficient memory to disable swap safely')
    for u in UNITS:
        state=s['units'][u]
        if state['LoadState']!='loaded' or state['ActiveState'] not in ('active','inactive'):
            raise ValueError('unit not in a supported stable state')
    if s['units']['rpi-zram-writeback.service']['ActiveState']!='inactive':
        raise ValueError('writeback currently running; refuse to interrupt')
    if (s['units']['dev-zram0.swap']['ActiveState']=='active') != bool(swaps):
        raise ValueError('kernel/manager swap state disagree')
    if s['setup']['Result']!='success' or s['setup']['ActiveState']!=('active' if swaps else 'inactive'):
        raise ValueError('zram setup unit is not in a consistent successful state')
    if s['units']['dev-zram0.swap']['FragmentPath']!='/run/systemd/generator/dev-zram0.swap':
        raise ValueError('unexpected swap unit origin')


class Lease:
    def __init__(self, directory, system=None):
        self.directory=Path(directory)
        self.path=self.directory/'lease_state.json'
        self.system=system or System()
        self.state=None

    def event(self, action):
        with (self.directory/'lease_events.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(wall_utc=time.time(),action=action))+'\n')
            f.flush(); os.fsync(f.fileno())

    def save(self):
        record(self.path,self.state)

    def apply(self):
        if self.path.exists():
            raise FileExistsError('lease journal exists')
        original=self.system.snapshot()
        validate_snapshot(original)
        self.state=dict(original=original,phase='APPLYING',owned_masks=[])
        self.save()  # durable BEFORE the first mutation
        self.event('stop writeback timer: intent')
        self.system.ctl('stop','rpi-zram-writeback.timer')
        # Stop while the unit still has its What=/dev/zram0 metadata. Masking an
        # active swap first erased that metadata on this system (retained QA failure).
        self.event('stop swap unit: intent')
        self.system.ctl('stop','dev-zram0.swap')
        self.state['owned_masks']=list(UNITS)
        self.save()  # durable intent for even a partially completed batch
        self.event('runtime mask batch: '+','.join(UNITS))
        self.system.ctl('mask','--runtime',*UNITS)
        self.event('set powersave: intent')
        self.system.governor('powersave')
        now=self.system.current()
        if now['swaps'] or now['governor']!='powersave' or not all(now['masks'].values()):
            raise RuntimeError('swap lease readback failed')
        self.state['phase']='READY'
        self.save()
        self.event('READY verified')

    def restore(self):
        receipt=self.directory/'restore.json'
        if receipt.exists():
            return json.loads(receipt.read_text(encoding='utf-8'))
        if not self.path.exists():
            result=dict(status='NO_CHANGES',errors=[])
            record(receipt,result,exclusive=True)
            return result
        self.state=json.loads(self.path.read_text(encoding='utf-8'))
        validate_snapshot(self.state['original'])
        original=self.state['original']
        errors=[]
        def attempt(label,fn):
            self.event('restore intent: '+label)
            try:
                fn()
            except Exception as e:
                errors.append(label+': '+str(e))
        # Undo ONLY masks whose creation was journalled after an absent-path snapshot.
        if any(u not in UNITS for u in self.state['owned_masks']):
            raise ValueError('invalid owned unit')
        def unmask():
            now=self.system.current()
            owned=[u for u in self.state['owned_masks'] if now['masks'][u]]
            if owned:
                self.system.ctl('unmask','--runtime',*owned)
        attempt('owned mask batch',unmask)
        attempt('governor',lambda:self.system.governor(original['governor']))
        attempt('swap state',lambda:self.system.ctl('start' if original['swaps'] else 'stop','dev-zram0.swap'))
        attempt('timer state',lambda:self.system.ctl(
            'start' if original['units']['rpi-zram-writeback.timer']['ActiveState']=='active' else 'stop',
            'rpi-zram-writeback.timer'))
        try:
            now=self.system.current()
            normalize=lambda rows:[{k:v for k,v in r.items() if k!='used_kb'} for r in rows]
            if now['governor']!=original['governor'] or normalize(now['swaps'])!=normalize(original['swaps']):
                errors.append('restored governor/swap readback differs')
            if any(now['masks'].values()) or any(now['active'][u]!=original['units'][u]['ActiveState'] for u in UNITS):
                errors.append('restored mask/unit state differs')
            if now['setup']!=original['setup']:
                errors.append('restored zram setup state differs')
        except Exception as e:
            errors.append('restore readback: '+str(e))
        self.state['phase']='RESTORED' if not errors else 'RESTORE_FAILED'
        self.save()
        result=dict(status=self.state['phase'],errors=errors,wall_utc=time.time())
        record(receipt,result,exclusive=True)
        self.event(result['status'])
        return result


def locked_materials(base):
    from bindings import read_lock
    return read_lock(base)


def storage_preflight(lockpath,tag,commit,phase):
    from guard import read_storage
    import usb_guard
    contract=json.loads((HERE/'usb_contract.json').read_text(encoding='utf-8'))
    frame=read_storage();errors=usb_guard.validate(frame,contract)
    if errors:raise RuntimeError('USB preflight: '+str(errors))
    validate_snapshot(System().snapshot())
    return dict(tag=tag,commit=commit,phase=phase,
        lock_sha256=hashlib.sha256(lockpath.read_bytes()).hexdigest(),
        usb_contract_sha256=hashlib.sha256((HERE/'usb_contract.json').read_bytes()).hexdigest(),snapshot=frame)


def require_phase_storage(directory,lockpath,tag,commit,phase):
    from guard import read_storage
    from bindings import load_usb_preflight
    import usb_guard
    contract=json.loads((HERE/'usb_contract.json').read_text(encoding='utf-8'))
    frame,digest=load_usb_preflight(directory/'usb_preflight.json',tag,commit,phase,
        hashlib.sha256(lockpath.read_bytes()).hexdigest(),contract)
    errors=usb_guard.validate(read_storage(),contract,frame)
    if errors:raise RuntimeError('USB changed since frontend: '+str(errors))
    return digest


def payload(args):
    if args.mode not in ('qa','functional'):raise ValueError('no scientific timing mode implemented')
    if not os.environ.get('INVOCATION_ID'):raise RuntimeError('independent systemd supervision required')
    lock=locked_materials(HERE)
    if args.mode=='qa':
        expected_tag=lock['qa_tag']
        if 'torch' in sys.modules or 'scipy' in sys.modules:raise RuntimeError('sleep-only QA cannot import model runtime')
    elif args.mode=='functional':
        from bindings import activation
        expected_tag=activation()['tag']
    else:raise ValueError('no scientific timing mode implemented')
    if args.tag!=expected_tag or not re.fullmatch('[0-9a-f]{40}',args.commit or ''):raise ValueError('tag/commit differs')
    lockpath=HERE/'controller_lock.json'
    require_phase_storage(args.directory,lockpath,args.tag,args.commit,args.mode)
    Lease(args.directory).apply()
    if args.mode=='qa':
        r=subprocess.run(['sudo','-n','systemctl','start','dev-zram0.swap'],capture_output=True,text=True,timeout=20)
        record(args.directory/'activation_probe.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),True)
        if r.returncode==0 or System().current()['swaps']:raise RuntimeError('masked activation not blocked')
        child=None
        try:
            child=subprocess.Popen([sys.executable,'-c',f'import time; time.sleep({args.qa_seconds+60})'])
            ticks=int(Path(f'/proc/{child.pid}/stat').read_text().rsplit(')',1)[1].split()[19])
            record(args.directory/'qa_ready.json',dict(pid=os.getpid(),child_pid=child.pid,child_start_ticks=ticks,
                invocation_id=os.environ['INVOCATION_ID'],torch_imported='torch' in sys.modules,scipy_imported='scipy' in sys.modules),True)
            try:
                code=child.wait(timeout=args.qa_seconds);raise RuntimeError(f'QA child exited unexpectedly: {code}')
            except subprocess.TimeoutExpired:pass
        finally:
            if child is not None and child.poll() is None:
                child.terminate()
                try:child.wait(timeout=3)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)
        require_phase_storage(args.directory,lockpath,args.tag,args.commit,'qa')
        return 0
    from campaign import collect
    collect(args.directory,args.tag,args.commit)
    record(args.directory/'campaign_terminal.json',dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False),True)
    return 0


def launch(args):
    if args.mode not in ('qa','functional'):raise ValueError('no scientific mode')
    if HERE!=ROOT.resolve():raise ValueError('new owned predecessor workspace required')
    lock=locked_materials(HERE)
    if args.mode=='qa':
        if args.tag!=lock['qa_tag']:raise ValueError('QA tag differs')
        limit=args.qa_timeout
    else:
        from bindings import activation
        act=activation()
        if args.tag!=act['tag'] or args.name!='material_01':raise ValueError('one activated functional name/tag required')
        limit=act['campaign_timeout_seconds']
        import shutil
        if shutil.disk_usage(HERE).free<768*2**20:raise ValueError('functional export needs768MiB free before lease')
    if not re.fullmatch('[0-9a-f]{40}',args.commit or '') or not re.fullmatch('[a-z0-9_]+',args.name or ''):raise ValueError('invalid identity')
    lockpath=HERE/'controller_lock.json'
    frame=storage_preflight(lockpath,args.tag,args.commit,args.mode)
    out=HERE/'runs'/args.name;out.mkdir(parents=True,exist_ok=False)
    record(out/'usb_preflight.json',frame,True)
    record(out/'registration.json',dict(tag=args.tag,commit=args.commit,mode=args.mode,
        lock_sha256=hashlib.sha256(lockpath.read_bytes()).hexdigest()),True)
    (HERE/'ultralytics_config').mkdir(exist_ok=True)
    argv=[sys.executable,str(HERE/'control.py'),'payload','--directory',str(out),'--mode',args.mode,
        '--tag',args.tag,'--commit',args.commit,'--qa-seconds',str(args.qa_seconds)]
    stop=' '.join([sys.executable,str(HERE/'control.py'),'restore','--directory',str(out)])
    if any(not re.fullmatch(r'[/A-Za-z0-9_.-]+',v) for v in (sys.executable,str(HERE),str(out))):raise ValueError('unsafe path spelling')
    result=subprocess.run(['sudo','-n','systemd-run','--unit='+SERVICE,'--wait','--collect',
        '--property=Type=exec','--property=User='+os.environ['USER'],'--property=KillMode=control-group',
        '--property=CPUAffinity=0 1 2 3','--property=TimeoutStopSec=120','--property=RuntimeMaxSec='+str(limit),
        '--property=StandardOutput=append:'+str(out/'supervisor.log'),'--property=StandardError=inherit',
        '--property=ExecStopPost='+stop,'--setenv=OMP_NUM_THREADS=4','--setenv=MKL_NUM_THREADS=4',
        '--setenv=OPENBLAS_NUM_THREADS=4','--setenv=YOLO_OFFLINE=true','--setenv=YOLO_AUTOINSTALL=false',
        '--setenv=YOLO_CONFIG_DIR='+str(HERE/'ultralytics_config'),*argv])
    return result.returncode


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','payload','restore'])
    p.add_argument('--directory',type=Path);p.add_argument('--name');p.add_argument('--mode',choices=['qa','functional'],default='qa')
    p.add_argument('--tag');p.add_argument('--commit');p.add_argument('--qa-seconds',type=int,default=15)
    p.add_argument('--qa-timeout',type=int,default=90);args=p.parse_args()
    if not 1<=args.qa_seconds<=120 or not 1<=args.qa_timeout<=180:raise ValueError('finite QA bounds required')
    if args.action=='launch':return launch(args)
    if args.directory is None or args.directory.resolve().parent!=ROOT.resolve()/'runs':raise ValueError('owned new run required')
    if args.action=='restore':
        r=Lease(args.directory).restore();print(json.dumps(r));return 0 if r['status'] in ('RESTORED','NO_CHANGES') else 70
    return payload(args)


if __name__=='__main__':raise SystemExit(main())


