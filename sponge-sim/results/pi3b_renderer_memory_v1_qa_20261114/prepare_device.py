"""Exclusive new-namespace deployment; no scientific run or package changes."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

B=Path(__file__).resolve().parent
S=B.parents[1]/'studies/pi3b_renderer_memory_v1_20261114'
REMOTE='/home/tanh/sponge-sim/pi3b_renderer_memory_v1_20261114'
PY='/home/tanh/sponge-venv/bin/python'
OPTIONS=['-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10']
TAG='qa-pi3b-renderer-memory-v1-20261114'


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
        frozen=subprocess.check_output(['git','show',f'{commit}:sponge-sim/studies/pi3b_renderer_memory_v1_20261114/{name}'])
        if hashlib.sha256(raw).hexdigest()!=digest or raw!=frozen or raw!=(B/'registered_materials'/name).read_bytes():
            raise ValueError('working/tag/archive bytes differ: '+name)
    code="""from pathlib import Path
import sys,json,subprocess,shutil
old=Path('/home/tanh/sponge-sim/pi3b_full20_20261114');new=Path(REMOTE)
sys.path.insert(0,str(old));import control
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines())
assert service==dict(ActiveState='inactive',MainPID='0'),service
assert not new.exists()
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
    before=remote(code);save('readonly_preflight.json',dict(command=code,result=before))
    mkdir=f"from pathlib import Path\nimport json\np=Path({REMOTE!r});p.mkdir(exist_ok=False)\nprint(json.dumps(dict(created=str(p))))"
    made=remote(mkdir);save('workspace_creation.json',dict(command=mkdir,result=made))
    r=subprocess.run(['scp',*OPTIONS,*[str(S/n) for n in sorted(prep['source_sha256'])],f'tanh@192.168.10.11:{REMOTE}/'],capture_output=True,text=True,timeout=120)
    save('deployment.json',dict(commit=commit,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial deployment retained, no overwrite retry')
    verify=f"""from pathlib import Path
import sys,json,hashlib
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
expected={prep['source_sha256']!r}
observed={{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in b.iterdir() if p.is_file()}}
assert expected==observed
lock=control.locked_materials(b);assert lock['qa_tag']=={TAG!r}
assert not (b/'memory_registration.json').exists() and not (b/'runs').exists()
snapshot=control.System().snapshot();control.validate_snapshot(snapshot)
assert snapshot=={before['snapshot']!r} or all(snapshot[k]=={before['snapshot']!r}[k] for k in ('governor','units','setup','swaps'))
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
print(json.dumps(dict(source_sha256=observed,lock=lock,snapshot=snapshot,scientific_registration_exists=False,torch_imported=False,scipy_imported=False)))
"""
    after=remote(verify);save('registration_check.json',dict(command=verify,result=after))
    print(json.dumps(dict(status='NEW_WORKSPACE_READY_SLEEP_ONLY',commit=commit,source_files=len(after['source_sha256']))))


if __name__=='__main__':main(sys.argv[1])
