"""Add science configuration to qualified namespace without changing runtime."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

B=Path(__file__).resolve().parent
SIM=B.parents[1]
SOURCE=SIM/'studies/pi3b_renderer_memory_v1_20261114'
REMOTE='/home/tanh/sponge-sim/pi3b_renderer_memory_v1_20261114'
PY='/home/tanh/sponge-venv/bin/python'
OPTIONS=['-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10']
TAG='prereg-pi3b-renderer-memory-v1-20261114'
PROTOCOL='PREREG_PI3B_RENDERER_MEMORY_V1_20261114.md'


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def remote(script):
    r=subprocess.run(['ssh',*OPTIONS,'tanh@192.168.10.11',PY+' -'],input=script,text=True,capture_output=True,timeout=90)
    if r.returncode:raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)


def main(commit):
    if subprocess.check_output(['git','rev-parse',TAG],text=True).strip()!=commit:raise ValueError('tag differs')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    reg=json.loads((SOURCE/'memory_registration.json').read_text())
    protocol=SIM/'prereg'/PROTOCOL
    assert sha(protocol)==reg['protocol']['sha256']
    for p in [SOURCE/'memory_registration.json',protocol]+[SOURCE/n for n in reg['source_sha256']]:
        frozen=subprocess.check_output(['git','show',commit+':'+p.relative_to(SIM.parent).as_posix()])
        if frozen!=p.read_bytes():raise ValueError('working/tag bytes differ: '+str(p))
    known=json.loads((SIM/'results/pi3b_renderer_memory_v1_qa_20261114/source_preparation.json').read_text())['source_sha256']
    code=f'''from pathlib import Path
import sys,json,subprocess,hashlib,shutil
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines())
assert service==dict(ActiveState='inactive',MainPID='0'),service
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={known!r}
assert {{n:sha(b/n) for n in expected}}==expected
control.locked_materials(b)
snapshot=control.System().snapshot();control.validate_snapshot(snapshot)
assert not any(control.System().current()['masks'].values())
assert not (b/'memory_registration.json').exists() and not (b/{PROTOCOL!r}).exists()
assert not (b/'runs/memory_smoke_01').exists() and not (b/'runs/memory_full_01').exists()
workers=[]
knownworkers={{str(b/n) for n in ('control.py','memory_worker.py','memory_campaign.py')}}
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\\0') if v]
   if any(a in knownworkers for a in argv):workers.append(dict(pid=int(p.name),argv=argv))
  except OSError:pass
assert not workers
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
print(json.dumps(dict(service=service,snapshot=snapshot,workers=workers,qualified_files=expected,disk_free_bytes=shutil.disk_usage(b).free,torch_imported=False,scipy_imported=False)))
'''
    save('readonly_science_preflight.json',dict(command=code,result=remote(code)))
    r=subprocess.run(['scp',*OPTIONS,str(SOURCE/'memory_registration.json'),str(protocol),f'tanh@192.168.10.11:{REMOTE}/'],capture_output=True,text=True,timeout=90)
    save('science_deployment.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,tag=TAG,commit=commit))
    if r.returncode:raise RuntimeError('partial science deployment retained; no overwrite retry')
    check=f'''from pathlib import Path
import sys,json,hashlib
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
from memory_worker import registration
reg=registration(b/'memory_registration.json',{TAG!r},{commit!r})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(b/{PROTOCOL!r})==reg['protocol']['sha256']
assert {{n:sha(b/n) for n in {known!r}}}=={known!r}
for n,digest in reg['reference_sha256'].items():assert sha(b/n)==digest
cache=Path(reg['cache_directory']);assert sha(cache/'manifest.json')==reg['cache_manifest_sha256']
manifest=json.loads((cache/'manifest.json').read_text())
for row in manifest['cases']:assert sha(cache/row['filename'])==row['sha256']
assert manifest['source_material_sha256']==reg['source_material_sha256']
assert len(manifest['cases'])==40 and 'torch' not in sys.modules and 'scipy' not in sys.modules
control.validate_snapshot(control.System().snapshot())
print(json.dumps(dict(status='READY_ONE_TECHNICAL_RSS_SMOKE',tag={TAG!r},commit={commit!r},registration_sha256=sha(b/'memory_registration.json'),cache_cases=40,runtime_source_unchanged=True,torch_imported=False,scipy_imported=False)))
'''
    value=remote(check);save('science_readiness.json',dict(command=check,result=value));print(json.dumps(value))


if __name__=='__main__':main(sys.argv[1])
