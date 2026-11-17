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
ROOT = Path.home() / 'sponge-sim' / 'pi3b_full20_20261114'
SERVICE = 'sponge-pi3b-swapguard-v2'
SESSIONS = (('PI4','pipeline'),('PI4','stages'),('PI1','pipeline'))


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
    lock=json.loads((base/'lock.json').read_text(encoding='utf-8'))
    for row in lock['files']:
        p=base/row['name']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:
            raise RuntimeError('changed locked material: '+row['name'])
    return lock


def payload(args):
    if not os.environ.get('INVOCATION_ID'):
        raise RuntimeError('payload must run in the transient systemd service')
    if args.mode=='smoke':
        raise ValueError('No repeat smoke: retain the failed v2 pilot')
    lock=locked_materials(HERE)
    expected_tag=lock['qa_tag'] if args.mode=='qa' else lock['registration_tag']
    if args.tag!=expected_tag or not re.fullmatch('[0-9a-f]{40}',args.commit or ''):
        raise ValueError('registration argument mismatch')
    Lease(args.directory).apply()
    if args.mode=='qa':
        # A real manager activation request must fail while the owned mask is in place.
        r=subprocess.run(['sudo','-n','systemctl','start','dev-zram0.swap'],capture_output=True,text=True,timeout=20)
        record(args.directory/'activation_probe.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),True)
        if r.returncode==0 or System().current()['swaps']:
            raise RuntimeError('masked swap activation was not blocked')
        child=subprocess.Popen([sys.executable,'-c',f'import time; time.sleep({args.qa_seconds+60})'])
        try:
            ticks=int(Path(f'/proc/{child.pid}/stat').read_text().rsplit(')',1)[1].split()[19])
            record(args.directory/'qa_ready.json',dict(pid=os.getpid(),child_pid=child.pid,child_start_ticks=ticks,
                   invocation_id=os.environ['INVOCATION_ID']),True)
            try:
                code=child.wait(timeout=args.qa_seconds)
                raise RuntimeError(f'QA child exited unexpectedly: {code}')
            except subprocess.TimeoutExpired:
                pass  # normal bounded sleeping-payload completion; no scientific timing
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)
        return 0
    results=[]
    flag=['--smoke'] if args.mode=='smoke' else []
    if lock['campaign']['session_order'] != [list(pair) for pair in SESSIONS]:
        raise ValueError('declared session order differs from the fixed full20 schedule')
    for profile,mode in SESSIONS:
        name=mode+'_'+profile
        time.sleep(lock['campaign']['settle_seconds'][args.mode])
        argv=[sys.executable,str(HERE/'run.py'),'--lock',str(HERE/'lock.json'),'--base',str(HERE),
              '--run-dir',str(args.directory/name),'--tag',args.tag,'--commit',args.commit,
              '--profile',profile,'--mode',mode,*flag]
        with (args.directory/(name+'.log')).open('x',encoding='utf-8') as log:
            try:
                r=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,timeout=lock['campaign']['session_timeout_seconds'])
                code=r.returncode
            except subprocess.TimeoutExpired:
                code=124
        result=dict(session=name,returncode=code)
        if code==0:
            with (args.directory/(name+'.gate.log')).open('x',encoding='utf-8') as log:
                g=subprocess.run([sys.executable,str(HERE/'analyze.py'),str(args.directory/name),'--gate-only'],
                                 stdout=log,stderr=subprocess.STDOUT,timeout=180)
            result['gate_returncode']=g.returncode
            code=g.returncode
        results.append(result)
        record(args.directory/'status.json',results)
        if code:
            record(args.directory/'campaign_terminal.json',dict(status='FAILED_STOPPED_NO_RETRY',sessions=results),True)
            return code
    record(args.directory/'campaign_terminal.json',dict(status='COMPLETED',sessions=results),True)
    return 0


def launch(args):
    if args.mode=='smoke':
        raise ValueError('No repeat smoke: retain the failed v2 pilot')
    if HERE!=ROOT.resolve():
        raise ValueError('deploy only at the registered Pi workspace')
    lock=locked_materials(HERE)
    if not re.fullmatch('[a-z0-9_]+',args.name):
        raise ValueError('invalid unique run name')
    out=HERE/'runs'/args.name
    out.mkdir(parents=True,exist_ok=False)
    record(out/'registration.json',dict(tag=args.tag,commit=args.commit,mode=args.mode,
           lock_sha256=hashlib.sha256((HERE/'lock.json').read_bytes()).hexdigest()),True)
    argv=[sys.executable,str(HERE/'control.py'),'payload','--directory',str(out),
          '--mode',args.mode,'--tag',args.tag,'--commit',args.commit,'--qa-seconds',str(args.qa_seconds)]
    stop=' '.join([sys.executable,str(HERE/'control.py'),'restore','--directory',str(out)])
    # Paths below the fixed workspace contain no spaces/metacharacters. No shell is invoked.
    if any(not re.fullmatch(r'[/A-Za-z0-9_.-]+',x) for x in [sys.executable,str(HERE),str(out)]):
        raise ValueError('unsupported path spelling')
    command=['sudo','-n','systemd-run','--unit='+SERVICE,'--wait','--collect',
             '--property=Type=exec','--property=User='+os.environ['USER'],
             '--property=KillMode=control-group','--property=TimeoutStopSec=120',
             '--property=StandardOutput=append:'+str(out/'supervisor.log'),'--property=StandardError=inherit',
             '--property=RuntimeMaxSec='+str(args.qa_timeout if args.mode=='qa' else lock['campaign']['total_timeout_seconds']),
             '--property=ExecStopPost='+stop,*argv]
    result=subprocess.run(command)
    return result.returncode


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=['launch','payload','restore'])
    ap.add_argument('--directory',type=Path)
    ap.add_argument('--name')
    ap.add_argument('--mode',choices=['qa','smoke','full'],default='qa')
    ap.add_argument('--tag',required=False)
    ap.add_argument('--commit',required=False)
    ap.add_argument('--qa-seconds',type=int,default=5)
    ap.add_argument('--qa-timeout',type=int,default=30)
    args=ap.parse_args()
    if not 1<=args.qa_seconds<=120 or not 1<=args.qa_timeout<=180:
        raise ValueError('QA durations outside finite engineering bounds')
    if args.action=='launch':
        return launch(args)
    if args.directory is None or args.directory.resolve().parent!=ROOT.resolve()/'runs':
        raise ValueError('directory must be one campaign under the registered workspace')
    if args.action=='restore':
        r=Lease(args.directory).restore()
        print(json.dumps(r))
        return 0 if r['status'] in ('RESTORED','NO_CHANGES') else 70
    return payload(args)


if __name__=='__main__':
    raise SystemExit(main())
