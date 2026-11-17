"""Deploy exact QA archive once to an absent workspace; no model/scientific load."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

B=Path(__file__).resolve().parent
S=B.parents[1]/'studies/pi3b_nms_predecessor_20261115'
REMOTE='/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115'
PY='/home/tanh/sponge-venv/bin/python'
TAG='qa-pi3b-nms-predecessor-supervisor-20261115'
OPTIONS=['-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10']


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def remote(code):
    ast.parse(code)
    r=subprocess.run(['ssh',*OPTIONS,'tanh@192.168.10.11',PY+' -'],input=code,text=True,capture_output=True,timeout=60)
    if r.returncode:raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)


def main(commit):
    assert subprocess.check_output(['git','rev-parse',TAG],text=True).strip()==commit
    prep=json.loads((B/'source_preparation.json').read_text())
    for name,digest in prep['source_sha256'].items():
        raw=(S/name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==digest and raw==(B/'registered_materials'/name).read_bytes()
        assert raw==subprocess.check_output(['git','show',f'{commit}:sponge-sim/studies/pi3b_nms_predecessor_20261115/{name}'])
    contract=json.loads((S/'usb_contract.json').read_text())
    code=f'''from pathlib import Path
import sys,json,subprocess,shutil
old=Path('/home/tanh/sponge-sim/pi3b_renderer_memory_usb_20261115');new=Path({REMOTE!r})
assert not new.exists()
sys.path.insert(0,str(old));import control,usb_guard
r=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(x.split('=',1) for x in r.stdout.splitlines());assert service.get('MainPID')=='0' and service.get('ActiveState')=='inactive',service
snapshot=control.System().snapshot();control.validate_snapshot(snapshot);assert not any(control.System().current()['masks'].values())
free=shutil.disk_usage(old).free;assert free>=64*2**20
new.mkdir(exist_ok=False)
frame=usb_guard.read_snapshot(dict(workspace=new,cache=Path('/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/caches/cache_01')))
assert not usb_guard.validate(frame,{contract!r})
print(json.dumps(dict(service=service,snapshot=snapshot,disk_free_bytes=free,static_usb_valid=True,new_workspace=str(new),torch_imported='torch' in sys.modules)))
'''
    before=remote(code);save('readonly_preflight.json',dict(command=code,result=before))
    r=subprocess.run(['scp',*OPTIONS,*[str(S/n) for n in sorted(prep['source_sha256'])],f'tanh@192.168.10.11:{REMOTE}/'],capture_output=True,text=True,timeout=120)
    save('deployment.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,commit=commit))
    if r.returncode:raise RuntimeError('partial deployment retained, no overwrite retry')
    verify=f'''from pathlib import Path
import sys,json,hashlib
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
observed={{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in b.iterdir() if p.is_file()}}
assert observed=={prep['source_sha256']!r}
lock=control.locked_materials(b);assert lock['qa_tag']=={TAG!r}
assert not (b/'runs').exists() and not (b/'functional_activation.json').exists()
snapshot=control.System().snapshot();control.validate_snapshot(snapshot)
assert all(snapshot[k]=={before['snapshot']!r}[k] for k in ('governor','units','setup'))
norm=lambda rows:[{{k:v for k,v in row.items() if k!='used_kb'}} for row in rows]
assert norm(snapshot['swaps'])==norm({before['snapshot']!r}['swaps'])
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
print(json.dumps(dict(source_sha256=observed,original_context_unchanged=True,empirical_endpoints_enabled=False,functional_activation_present=False)))
'''
    after=remote(verify);save('deployment_verification.json',dict(command=verify,result=after))
    print(json.dumps(dict(status='EXACT_NEW_SUPERVISOR_QA_PACKAGE_DEPLOYED',files=len(prep['source_sha256']),no_model_loaded=True)))


if __name__=='__main__':main(sys.argv[1])
