# Adapted from sponge-sim/results/pi3b_renderer_memory_v1_20261114/launch_smoke.py:1-53
# SHA256 60916bfeb9dca81f199208b4d1dde9531e9a5f86a7dfb8f89f3912a9f2ef34a7; USB-present source/tag/reference bindings, same one-smoke/no-auto-full boundary.
"""One registered smoke; capture provenance before launch; no automatic full."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from deploy_science import B,SOURCE,REMOTE,PY,OPTIONS,TAG,remote,save


def main(commit):
    if subprocess.check_output(['git','rev-parse',TAG],text=True).strip()!=commit:raise ValueError('tag differs')
    readiness=json.loads((B/'science_readiness.json').read_text())['result']
    reg_path=SOURCE/'memory_registration.json';reg=json.loads(reg_path.read_text())
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert readiness['commit']==commit and readiness['registration_sha256']==sha(reg_path)
    phase=B/'runs/memory_smoke_01';phase.mkdir(parents=True,exist_ok=False)
    value=dict(tag=TAG,commit=commit,config_sha256=sha(reg_path),weights_sha256=reg['weights_sha256'],
        cache_manifest_sha256=reg['cache_manifest_sha256'],protocol=reg['protocol'],phase='smoke',
        created_at_utc=datetime.now(timezone.utc).isoformat(),expected_jobs=36,expected_image_ids=reg['phases']['smoke']['image_ids'],
        original_run_directory=REMOTE+'/runs/memory_smoke_01',original_artifact_subdirectory='original',
        source_sha256=reg['source_sha256'],latency_endpoint_recorded=False,full_not_automatically_authorized=True)
    with (phase/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2)
    prepare=f'''from pathlib import Path
import sys,json,subprocess,hashlib
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
from memory_worker import registration
reg=registration(b/'memory_registration.json',{TAG!r},{commit!r})
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines());assert service==dict(ActiveState='inactive',MainPID='0')
control.locked_materials(b);control.validate_snapshot(control.System().snapshot())
assert not (b/'runs/memory_smoke_01').exists()
assert hashlib.sha256((b/'memory_registration.json').read_bytes()).hexdigest()=={sha(reg_path)!r}
out=b/'launch_manifests/smoke';out.mkdir(parents=True,exist_ok=False)
with (out/'manifest.json').open('x',encoding='utf-8') as f:json.dump({value!r},f,indent=2)
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
print(json.dumps(dict(status='SMOKE_MANIFEST_SAVED_BEFORE_LOAD',manifest_sha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest())))
'''
    saved=remote(prepare);save('smoke_manifest_deployment.json',dict(command=prepare,result=saved))
    assert saved['manifest_sha256']==sha(phase/'manifest.json')
    command=f'{PY} {REMOTE}/control.py launch --mode memory --phase smoke --name memory_smoke_01 --tag {TAG} --commit {commit}'
    with (phase/'frontend.log').open('xb') as log:
        result=subprocess.run(['ssh',*OPTIONS,'-oServerAliveInterval=30','-oServerAliveCountMax=10','tanh@192.168.10.11',command],stdout=log,stderr=subprocess.STDOUT)
    # SSH termination alone does not establish service termination. No fetch/retry here.
    terminal=remote("import subprocess,json\nr=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)\nprint(json.dumps(dict(line.split('=',1) for line in r.stdout.splitlines())))")
    receipt=dict(ssh_returncode=result.returncode,service=terminal,command=command,finished_at_utc=datetime.now(timezone.utc).isoformat(),
        authoritative_service_terminal=terminal.get('MainPID')=='0' and terminal.get('ActiveState') in ('inactive','failed'))
    save('smoke_frontend_terminal.json',receipt);print(json.dumps(receipt))
    if not receipt['authoritative_service_terminal']:raise RuntimeError('service still live; wait same service, do not restart/fetch')
    return result.returncode


if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
