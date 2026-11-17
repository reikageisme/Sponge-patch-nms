# Adapted from sponge-sim/results/pi3b_renderer_memory_v1_qa_20261114/prepare_device.py:1-79
# SHA256 a1e23392f432d90a10c47ed7f7ecb8f30ef2fae5bf62ac685c2e0dc68a98e85f; preserve qualified USB module/metadata, deploy only absent files.
"""Add absent runtime files, preserving the qualified helper and metadata raw."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

B=Path(__file__).resolve().parent
S=B.parents[1]/'studies/pi3b_renderer_memory_usb_20261115'
REMOTE='/home/tanh/sponge-sim/pi3b_renderer_memory_usb_20261115'
PY='/home/tanh/sponge-venv/bin/python'
OPTIONS=['-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10']
TAG='qa-pi3b-renderer-memory-usb-20261115'


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def remote(code):
    r=subprocess.run(['ssh',*OPTIONS,'tanh@192.168.10.11',PY+' -'],input=code,text=True,capture_output=True,timeout=60)
    if r.returncode:raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)


def main(commit):
    actual=subprocess.check_output(['git','rev-parse',TAG],text=True).strip()
    if actual!=commit:raise ValueError('engineering tag/commit differs')
    prep=json.loads((B/'source_preparation.json').read_text())
    for name,digest in prep['source_sha256'].items():
        raw=(S/name).read_bytes()
        frozen=subprocess.check_output(['git','show',f'{commit}:sponge-sim/studies/pi3b_renderer_memory_usb_20261115/{name}'])
        if hashlib.sha256(raw).hexdigest()!=digest or raw!=frozen or raw!=(B/'registered_materials'/name).read_bytes():
            raise ValueError('working/tag/archive bytes differ: '+name)
    code="""from pathlib import Path
import sys,json,subprocess,shutil,hashlib
old=Path('/home/tanh/sponge-sim/pi3b_full20_20261114');new=Path(REMOTE)
sys.path.insert(0,str(old));import control
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines())
assert service==dict(ActiveState='inactive',MainPID='0'),service
assert new.exists()
assert {p.name for p in new.iterdir() if p.is_file()}=={'usb_guard.py','qa_metadata_01.json'}
assert hashlib.sha256((new/'usb_guard.py').read_bytes()).hexdigest()==USB_SOURCE_HASH
assert hashlib.sha256((new/'qa_metadata_01.json').read_bytes()).hexdigest()==USB_METADATA_HASH
sys.path.insert(0,str(new));import usb_guard
frame=usb_guard.read_snapshot(dict(workspace=new,cache=Path('/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/caches/cache_01')))
assert not usb_guard.validate(frame,USB_CONTRACT)
workers=[]
roots=[old,old.with_name('pi3b_renderer_prealloc_20261114'),new]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\\0') if v]
   if len(argv)>1 and any(argv[1]==str(root/name) for root in roots for name in ('run.py','control.py','memory_campaign.py','memory_worker.py','build_cache.py')):workers.append(argv)
  except OSError:pass
assert not workers
snapshot=control.System().snapshot();control.validate_snapshot(snapshot)
assert not any(control.System().current()['masks'].values())
print(json.dumps(dict(service=service,workers=workers,snapshot=snapshot,disk_free_bytes=shutil.disk_usage(old).free,torch_imported='torch' in sys.modules,new_workspace_exists=new.exists())))
""".replace('Path(REMOTE)',f'Path({REMOTE!r})')
    metadata=S.parents[1]/'results/pi3b_usb_guard_qa_20261115/qa_metadata_01.json'
    contract=json.loads((S/'usb_contract.json').read_text())
    code=code.replace('USB_SOURCE_HASH',repr(prep['source_sha256']['usb_guard.py'])).replace('USB_METADATA_HASH',repr(hashlib.sha256(metadata.read_bytes()).hexdigest())).replace('USB_CONTRACT',repr(contract))
    before=remote(code);save('readonly_preflight.json',dict(command=code,result=before))
    r=subprocess.run(['scp',*OPTIONS,*[str(S/n) for n in sorted(prep['source_sha256']) if n!='usb_guard.py'],f'tanh@192.168.10.11:{REMOTE}/'],capture_output=True,text=True,timeout=120)
    save('deployment.json',dict(commit=commit,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial deployment retained, no overwrite retry')
    verify=f"""from pathlib import Path
import sys,json,hashlib
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
expected={prep['source_sha256']!r}
observed={{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in b.iterdir() if p.is_file()}}
assert {{n:observed[n] for n in expected}}==expected
assert set(observed)==set(expected)|{{'qa_metadata_01.json'}}
assert observed['qa_metadata_01.json']=={hashlib.sha256(metadata.read_bytes()).hexdigest()!r}
lock=control.locked_materials(b);assert lock['qa_tag']=={TAG!r}
assert not (b/'memory_registration.json').exists() and not (b/'runs').exists()
snapshot=control.System().snapshot();control.validate_snapshot(snapshot)
assert all(snapshot[k]=={before['snapshot']!r}[k] for k in ('governor','units','setup'))
norm=lambda rows:[{{k:v for k,v in row.items() if k!='used_kb'}} for row in rows]
assert norm(snapshot['swaps'])==norm({before['snapshot']!r}['swaps'])
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
control.storage_preflight(b/'engineering_lock.json',{TAG!r},{commit!r},'qa')
print(json.dumps(dict(source_sha256=observed,lock=lock,snapshot=snapshot,scientific_registration_exists=False,torch_imported=False,scipy_imported=False)))
"""
    after=remote(verify);save('registration_check.json',dict(command=verify,result=after))
    print(json.dumps(dict(status='NEW_WORKSPACE_READY_SLEEP_ONLY',commit=commit,source_files=len(after['source_sha256']))))


if __name__=='__main__':main(sys.argv[1])
