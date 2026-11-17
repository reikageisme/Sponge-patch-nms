"""Prospective functional40 transport/admission/collection, never scientific timing.

Independent restoration/original-preservation predicates adapt the closed
READY collector42c787b0 and its qualified original payload925c544. All new
runtime Python bytes remain unchanged; only two reviewed metadata files added.
"""
from pathlib import Path
import ast
import base64
import hashlib
import json
import subprocess
import sys

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
S=ROOT/'sponge-sim/studies/pi3b_nms_predecessor_20261115'
REMOTE='/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115'
PY='/home/tanh/sponge-venv/bin/python'
TAG='qa-pi3b-nms-predecessor-material-20261115'
SSH=['ssh','-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes',
     '-oConnectTimeout=10','-oServerAliveInterval=15','-oServerAliveCountMax=3','tanh@192.168.10.11']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def admission(commit):
    reg=json.loads((B/'source_preparation.json').read_text())
    if reg['tag']!=TAG or reg['scientific_enabled'] is not False:raise ValueError('functional-only tag required')
    if subprocess.check_output(['git','rev-parse',TAG],cwd=ROOT,text=True).strip()!=commit:raise ValueError('tag mismatch')
    for name,digest in reg['package_sha256'].items():
        rel=(S/name).relative_to(ROOT).as_posix()
        if sha(S/name)!=digest or hashlib.sha256(subprocess.check_output(['git','show',f'{commit}:{rel}'],cwd=ROOT)).hexdigest()!=digest:
            raise ValueError('tagged package differs: '+name)
    for rel,digest in reg['host_source_sha256'].items():
        if sha(ROOT/rel)!=digest or hashlib.sha256(subprocess.check_output(['git','show',f'{commit}:{rel}'],cwd=ROOT)).hexdigest()!=digest:
            raise ValueError('tagged host source differs')
    if sha(ROOT/reg['plan_path'])!=reg['plan_sha256']:raise ValueError('plan changed')
    for rel in [reg['plan_path'],(B/'source_preparation.json').relative_to(ROOT).as_posix()]:
        if (ROOT/rel).read_bytes()!=subprocess.check_output(['git','show',f'{commit}:{rel}'],cwd=ROOT):raise ValueError('tagged plan/manifest differs')
    return reg


def query(code,label):
    ast.parse(code)
    out=B/'requests'/label;out.mkdir(parents=True,exist_ok=False)
    (out/'stdin.py').write_bytes(code.encode())
    stdout=b'';stderr=b'';rc=None;failure=None
    try:
        p=subprocess.run([*SSH,PY+' -'],input=code.encode(),capture_output=True,timeout=300)
        stdout,stderr,rc=p.stdout,p.stderr,p.returncode
        if rc:raise RuntimeError('metadata query failed: '+stderr.decode(errors='replace'))
        return json.loads(stdout)
    except subprocess.TimeoutExpired as exc:
        stdout=exc.stdout or b'';stderr=exc.stderr or b'';failure='TimeoutExpired';raise
    except BaseException as exc:failure=type(exc).__name__;raise
    finally:
        for name,data in (('stdout.bin',stdout),('stderr.bin',stderr)):
            with (out/name).open('xb') as f:f.write(data)
        with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(dict(returncode=rc,error=failure,metadata_timeout_seconds=300,retry=False),f,indent=2)


UNIT_CHECK=f'''from pathlib import Path
import sys,json,hashlib,subprocess,shutil,base64
sys.dont_write_bytecode=True
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
assert x.returncode==0
unit=dict(line.split('=',1) for line in x.stdout.splitlines());assert unit['MainPID']=='0' and unit['ActiveState'] in ('inactive','failed'),unit
'''
COMMON=UNIT_CHECK+'''
state=control.System().snapshot();control.validate_snapshot(state)
assert not any(control.System().current()['masks'].values())
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
'''


def deploy(commit,reg):
    base={k:v for k,v in reg['package_sha256'].items() if k not in ('supervisor_qa_verification.json','functional_activation.json')}
    code=COMMON+f'''assert unit['ActiveState']=='inactive'
assert {{p.name:sha(p) for p in b.iterdir() if p.is_file()}}=={base!r}
assert not (b/'runs/material_01').exists()
assert shutil.disk_usage(b).free>=768*2**20
for name,entry in {reg['prior_originals']!r}.items():
 p=b/'runs'/name
 assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes']
control.storage_preflight(b/'controller_lock.json',{TAG!r},{commit!r},'functional')
print(json.dumps(dict(unit=unit,original=state,free_bytes=shutil.disk_usage(b).free,no_model=True)))
'''
    before=query(code,'deploy_preflight');save('deployment_preflight.json',before)
    additions={name:base64.b64encode((S/name).read_bytes()).decode() for name in ('supervisor_qa_verification.json','functional_activation.json')}
    code=COMMON+f'''for name,value in {additions!r}.items():
 with (b/name).open('xb') as f:f.write(base64.b64decode(value))
assert {{p.name:sha(p) for p in b.iterdir() if p.is_file()}}=={reg['package_sha256']!r}
from bindings import activation
a=activation();assert a['tag']=={TAG!r} and a['scientific_enabled'] is False and a['cases']==40
norm=lambda rows:[{{k:v for k,v in row.items() if k!='used_kb'}} for row in rows]
assert all(state[k]=={before['original']!r}[k] for k in ('governor','units','setup'))
assert norm(state['swaps'])==norm({before['original']!r}['swaps'])
assert 'torch' not in sys.modules and not (b/'runs/material_01').exists()
print(json.dumps(dict(status='FUNCTIONAL_METADATA_DEPLOYED_SOURCE_UNCHANGED',package_files=25,model_run=False)))
'''
    result=query(code,'deploy_metadata')
    save('deployment_verification.json',dict(tag=TAG,commit=commit,result=result))
    print(json.dumps(result))


def launch(commit,reg):
    deployment=json.loads((B/'deployment_verification.json').read_text())
    if deployment['commit']!=commit or deployment['tag']!=TAG:raise ValueError('verified deployment missing')
    command=f'{PY} {REMOTE}/control.py launch --mode functional --name material_01 --tag {TAG} --commit {commit}'
    save('run_manifest.json',dict(tag=TAG,commit=commit,mode='functional',cases=40,worker_cap_seconds=3600,
        command=command,source_preparation_sha256=sha(B/'source_preparation.json'),plan_sha256=reg['plan_sha256'],scientific_enabled=False))
    with (B/'frontend_01.log').open('xb') as log:
        proc=subprocess.Popen([*SSH,command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in proc.stdout:
            log.write(line);log.flush();sys.stdout.buffer.write(line);sys.stdout.buffer.flush()
        code=proc.wait()
    save('frontend_terminal.json',dict(returncode=code,authoritative_service_terminal=False,experiment_restarted=False))
    print(json.dumps(dict(frontend_returncode=code,authoritative_service_terminal=False)))
    return code


def collect(commit,reg):
    code=UNIT_CHECK+f'''
workers=[]
for p in Path('/proc').iterdir():
 if p.name.isdecimal():
  try:
   argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\\0') if x]
   if any(str(b/name) in argv for name in ('control.py','worker.py','campaign.py')):workers.append(int(p.name))
  except OSError:pass
assert not workers
source_unchanged={{p.name:sha(p) for p in b.iterdir() if p.is_file()}}=={reg['package_sha256']!r}
prior_errors=[]
for name,entry in {reg['prior_originals']!r}.items():
 try:
  p=b/'runs'/name
  if sha(p)!=entry['sha256'] or p.stat().st_size!=entry['bytes']:prior_errors.append(name+': changed')
 except OSError as exc:prior_errors.append(name+': '+type(exc).__name__)
r=b/'runs/material_01';assert r.is_dir()
files={{p.relative_to(r).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in r.rglob('*') if p.is_file()}}
restore_ok=False;restore_errors=[];state=None
try:
 state=control.System().snapshot();control.validate_snapshot(state)
 restore=json.loads((r/'restore.json').read_text());lease=json.loads((r/'lease_state.json').read_text())
 norm=lambda rows:[{{k:v for k,v in row.items() if k!='used_kb'}} for row in rows]
 restore_ok=(restore['status']=='RESTORED' and restore['errors']==[]
  and all(state[k]==lease['original'][k] for k in ('governor','units','setup'))
  and norm(state['swaps'])==norm(lease['original']['swaps']) and not any(control.System().current()['masks'].values()))
 if not restore_ok:restore_errors.append('restore status/original-state mismatch')
except Exception as exc:restore_errors.append(type(exc).__name__+': '+str(exc))
assert 'torch' not in sys.modules
print(json.dumps(dict(files=files,unit=unit,original_restored=restore_ok,restore_errors=restore_errors,snapshot=state,
 workers=workers,source_unchanged=source_unchanged,prior_originals_unchanged=not prior_errors,prior_errors=prior_errors)))
'''
    before=query(code,'collect_before');save('remote_before_fetch.json',before)
    destination=B/'runs/material_01/original';destination.parent.mkdir(parents=True,exist_ok=False)
    p=subprocess.run(['scp',*SSH[1:-1],'-r',f'tanh@192.168.10.11:{REMOTE}/runs/material_01',str(destination)],capture_output=True,text=True,timeout=1800)
    save('fetch_receipt.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,copy_timeout_seconds=1800))
    if p.returncode:raise RuntimeError('partial transfer preserved; no experiment/overwrite retry')
    after=query(code,'collect_after');save('remote_after_fetch.json',after)
    files={p.relative_to(destination).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in destination.rglob('*') if p.is_file()}
    if files!=before['files'] or files!=after['files']:raise ValueError('original SHA/bytes mismatch')
    save('transfer_verification.json',dict(status='ORIGINALS_VERIFIED_NOT_A_FUNCTIONAL_VERDICT',files=files,
        remote_local_remote_sha_match=True,independent_restore_verified=before['original_restored'] and after['original_restored'],
        source_and_prior_originals_unchanged=all(x['source_unchanged'] and x['prior_originals_unchanged'] for x in (before,after)),
        scientific_enabled=False,ssh_kept_open=True))
    print(json.dumps(dict(status='ORIGINALS_VERIFIED',files=len(files),bytes=sum(x['bytes'] for x in files.values()),functional_verdict_not_yet_audited=True)))


if __name__=='__main__':
    action,commit=sys.argv[1:];reg=admission(commit)
    if action=='deploy':deploy(commit,reg)
    elif action=='launch':raise SystemExit(launch(commit,reg))
    elif action=='collect':collect(commit,reg)
    else:raise ValueError('only deploy/launch/collect supported')
