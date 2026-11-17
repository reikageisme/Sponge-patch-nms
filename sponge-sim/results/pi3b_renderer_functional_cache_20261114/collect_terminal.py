"""Read-only postterminal collection into fresh destinations; no model/endpoint."""
from pathlib import Path
import hashlib
import json
import subprocess

B=Path(__file__).resolve().parent
SSH=['ssh','-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes',
     '-oConnectTimeout=10','tanh@192.168.10.11']
PROBE='''from pathlib import Path
import sys,json,hashlib,subprocess
b=Path.home()/'sponge-sim/pi3b_renderer_prealloc_20261114';sys.path.insert(0,str(b));import control
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for v in iter(lambda:f.read(1024*1024),b''):h.update(v)
 return h.hexdigest()
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(v.split('=',1) for v in x.stdout.splitlines());assert service['ActiveState']=='inactive' and service['MainPID']=='0'
lock=control.locked_materials(b);s=control.System().snapshot();control.validate_snapshot(s)
assert not any(control.System().current()['masks'].values())
r=b/'runs/cacheprep_01';c=b/'caches/cache_01'
restore=json.loads((r/'restore.json').read_text());assert restore['status']=='RESTORED' and restore['errors']==[]
original=json.loads((r/'lease_state.json').read_text())['original']
norm=lambda rows:[{k:v for k,v in row.items() if k!='used_kb'} for row in rows]
assert s['governor']==original['governor'] and s['units']==original['units'] and s['setup']==original['setup'] and norm(s['swaps'])==norm(original['swaps'])
manifest=json.loads((c/'manifest.json').read_text());terminal=json.loads((c/'terminal.json').read_text())
assert manifest['status']=='COMPLETED_FUNCTIONAL_PARITY_ONLY' and len(manifest['cases'])==40
assert terminal==dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False)
assert json.loads((r/'campaign_terminal.json').read_text())==dict(status='COMPLETED_FUNCTIONAL_ONLY',empirical_endpoint_recorded=False)
known=[str(b/'control.py'),str(b/'memory_campaign.py'),str(b/'memory_worker.py')];workers=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\\0') if v]
   if len(argv)>1 and argv[1] in known:workers.append(dict(pid=int(p.name),argv=argv))
  except OSError:pass
assert not workers
files={}
for prefix in ('runs/cacheprep_01','caches/cache_01'):
 for p in sorted((b/prefix).rglob('*')):
  if p.is_file():files[p.relative_to(b).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
print(json.dumps(dict(service=service,workers=workers,snapshot=s,restore=restore,files=files,
 source_sha256={p.name:sha(p) for p in b.iterdir() if p.is_file()},
 prior_lock_sha256=sha(b/'config_history/engineering_lock_sleepqa_20261114.json'),
 scientific_registration_exists=(b/'memory_registration.json').exists(),torch_imported='torch' in sys.modules)))
'''


def save(name,obj):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)


def probe():
    p=subprocess.run([*SSH,'/home/tanh/sponge-venv/bin/python -'],input=PROBE,text=True,capture_output=True,timeout=100)
    if p.returncode:raise RuntimeError(p.stderr or p.stdout)
    return json.loads(p.stdout)


def main():
    if (B/'runs/cacheprep_01').exists() or (B/'caches/cache_01').exists():raise FileExistsError('No raw overwrite/refetch')
    before=probe();save('remote_before_fetch.json',dict(command=PROBE,result=before))
    for kind in ('runs','caches'):
        (B/kind).mkdir(exist_ok=False)
        remote='tanh@192.168.10.11:/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/'+kind+'/'+('cacheprep_01' if kind=='runs' else 'cache_01')
        p=subprocess.run(['scp','-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-r',remote,str(B/kind)],capture_output=True,text=True,timeout=600)
        save(kind+'_fetch_receipt.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        if p.returncode:raise RuntimeError('Partial fetch retained; no overwrite')
    after=probe();save('remote_after_fetch.json',dict(command=PROBE,result=after))
    local={}
    for kind in ('runs','caches'):
        for p in sorted((B/kind).rglob('*')):
            if p.is_file():
                h=hashlib.sha256()
                with p.open('rb') as f:
                    for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
                local[p.relative_to(B).as_posix()]=dict(sha256=h.hexdigest(),bytes=p.stat().st_size)
    assert before['files']==local==after['files']
    expected=json.loads((B/'source_preparation.json').read_text(encoding='utf-8'))['source_sha256']
    assert before['source_sha256']==after['source_sha256']==expected
    assert after['prior_lock_sha256']==hashlib.sha256((B/'prior_engineering_lock.json').read_bytes()).hexdigest()
    save('transfer_verification.json',dict(status='ALL_ORIGINAL_SHA_REMOTE_BEFORE_LOCAL_REMOTE_AFTER',n_files=len(local),files=local,
        source_unchanged=True,old_engineering_lock_preserved=True,restore_readback_verified=True,
        no_registered_workers=True,scientific_registration_exists=False,empirical_endpoint_recorded=False))
    print(json.dumps(dict(status='VERIFIED_FUNCTIONAL_CACHE_TRANSFER',n_original_files=len(local),bytes=sum(v['bytes'] for v in local.values()))))


if __name__=='__main__':main()
