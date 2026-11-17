"""Deploy ONE readonly observer sidecar only after specific review/tag binding."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

from run_qualification import B,SSH,PY,PAYLOAD_COMMIT
from readiness_plan import validate_prelaunch

ROOT=B.parents[2]
SIDECAR='/home/tanh/sponge-sim/pi3b_ready_observer_20261115'


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def query(code):
    ast.parse(code)
    r=subprocess.run([*SSH,PY+' -'],input=code.encode(),capture_output=True,timeout=60)
    if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
    return json.loads(r.stdout)


def main(commit):
    lock=validate_prelaunch(B,commit)
    payload=lock['payload_files_sha256'];old_files=lock['original_device_files']
    code=f'''from pathlib import Path
import sys,json,hashlib,subprocess
sys.dont_write_bytecode=True
b=Path('/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115');side=Path({SIDECAR!r})
assert not side.exists(), 'sidecar exists; stop, no overwrite retry'
assert {{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in b.iterdir() if p.is_file()}}=={payload!r}
for name,entry in {old_files!r}.items():
 p=b/'runs'/name
 assert p.stat().st_size==entry['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
for name in {lock['case_names']!r}:assert not (b/'runs'/name).exists()
sys.path.insert(0,str(b));import control
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
assert x.returncode==0
fields=dict(line.split('=',1) for line in x.stdout.splitlines());assert fields==dict(MainPID='0',ActiveState='inactive')
state=control.System().snapshot();control.validate_snapshot(state)
assert not any(control.System().current()['masks'].values())
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
side.mkdir(exist_ok=False)
print(json.dumps(dict(service=fields,original=state,old_failed_files_unchanged=len({old_files!r}),model_imported=False)))
'''
    before=query(code);save('deployment_preflight.json',dict(command=code,result=before))
    source=ROOT/'sponge-sim/studies/pi3b_ready_observer_20261115/probe.py'
    r=subprocess.run(['scp',*SSH[1:-1],str(source),f'tanh@192.168.10.11:{SIDECAR}/probe.py'],capture_output=True,text=True,timeout=120)
    save('deployment_copy.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial sidecar deployment retained; no overwrite retry')
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    after=query(f"from pathlib import Path\nimport hashlib,json\nb=Path({SIDECAR!r})\nassert {{p.name for p in b.iterdir()}}=={{'probe.py'}}\nassert hashlib.sha256((b/'probe.py').read_bytes()).hexdigest()=={digest!r}\nprint(json.dumps(dict(probe_sha256={digest!r},model_run=False)))\n")
    save('deployment_verification.json',dict(status='EXACT_READY_OBSERVER_SIDECAR_DEPLOYED',qualification_commit=commit,
        payload_commit=PAYLOAD_COMMIT,probe_sha256=digest,result=after))


if __name__=='__main__':
    import sys
    main(sys.argv[1])
