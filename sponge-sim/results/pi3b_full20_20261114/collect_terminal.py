"""Post-terminal read-only collection. Never launches or changes a Pi run."""
from pathlib import Path
import hashlib
import json
import subprocess

B = Path(__file__).resolve().parent
REMOTE = '/home/tanh/sponge-sim/pi3b_full20_20261114'
SSH = ['ssh', '-i', str(Path.home()/'.ssh/pi_spongepi'), '-oBatchMode=yes',
       '-oStrictHostKeyChecking=yes', '-oConnectTimeout=10', 'tanh@192.168.10.11']
PROBE = '''from pathlib import Path
import sys,json,hashlib,subprocess,time
b=Path('/home/tanh/sponge-sim/pi3b_full20_20261114');sys.path.insert(0,str(b));import control
r=b/'runs/full_01'
service=subprocess.run(['systemctl','show',control.SERVICE,'-p','MainPID','-p','ActiveState','-p','SubState','-p','LoadState'],capture_output=True,text=True,timeout=10)
fields=dict(line.split('=',1) for line in service.stdout.splitlines())
assert fields.get('ActiveState') in ('inactive','failed') and fields.get('MainPID')=='0',fields
workers=[]
known=[str(b/'control.py'),str(b/'run.py')]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   args=[a.decode(errors='replace') for a in (p/'cmdline').read_bytes().split(b'\\0') if a]
   if len(args)>1 and args[1] in known:workers.append(dict(pid=int(p.name),argv=args))
  except OSError:pass
assert not workers,workers
lock=control.locked_materials(b)
restore=json.loads((r/'restore.json').read_text());assert restore['status']=='RESTORED' and restore['errors']==[]
state=json.loads((r/'lease_state.json').read_text());now=control.System().snapshot();control.validate_snapshot(now)
normalize=lambda rows:[{k:v for k,v in row.items() if k!='used_kb'} for row in rows]
assert now['governor']==state['original']['governor'] and now['setup']==state['original']['setup']
assert now['units']==state['original']['units'] and normalize(now['swaps'])==normalize(state['original']['swaps'])
assert not any(control.System().current()['masks'].values())
files={}
for p in sorted(r.rglob('*')):
 if p.is_file():
  raw=p.read_bytes();files[str(p.relative_to(r))]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),lines=len(raw.splitlines()))
print(json.dumps(dict(wall_utc=time.time(),service=fields,registered_workers=workers,restore=restore,current=now,source_verified_files=len(lock['files']),lock_sha256=hashlib.sha256((b/'lock.json').read_bytes()).hexdigest(),full02_exists=(b/'runs/full_02').exists(),files=files)))
'''

def save(name, value):
    with (B/name).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)

def probe():
    p = subprocess.run([*SSH, '/home/tanh/sponge-venv/bin/python -'], input=PROBE,
                       text=True, capture_output=True, timeout=90)
    if p.returncode:
        raise RuntimeError(p.stderr or p.stdout)
    return json.loads(p.stdout)

def main():
    target=B/'runs/full_01'
    if target.exists():
        raise FileExistsError('No overwrite: local full_01 already exists')
    before=probe()
    save('remote_before_fetch.json',dict(command=PROBE,result=before))
    p=subprocess.run(['scp','-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes',
                      '-oStrictHostKeyChecking=yes','-r',
                      'tanh@192.168.10.11:'+REMOTE+'/runs/full_01',str(B/'runs')],
                     capture_output=True,text=True,timeout=180)
    save('fetch_receipt.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode:raise RuntimeError('Fetch failed; preserve partial local target')
    after=probe()
    save('remote_after_fetch.json',dict(command=PROBE,result=after))
    local={}
    for f in sorted(target.rglob('*')):
        if f.is_file():
            raw=f.read_bytes()
            local[f.relative_to(target).as_posix()]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),lines=len(raw.splitlines()))
    assert before['files']==local==after['files']
    save('transfer_verification.json',dict(status='ALL_ORIGINAL_FILES_MATCH_REMOTE_BEFORE_LOCAL_REMOTE_AFTER',
         n_files=len(local),files=local,source_verified_files=after['source_verified_files'],
         service_terminal=True,restore_verified=True,no_registered_workers=True,full02_exists=after['full02_exists']))
    print(json.dumps(dict(status='VERIFIED',n_files=len(local),restore=after['restore'])))

if __name__=='__main__':main()
