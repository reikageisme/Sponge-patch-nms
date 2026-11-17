"""One read-only metadata QA; writes results only in the new workspace."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

B=Path(__file__).resolve().parent
SOURCE=B.parents[1]/'studies/pi3b_renderer_memory_usb_20261115/usb_guard.py'
REMOTE='/home/tanh/sponge-sim/pi3b_renderer_memory_usb_20261115'
CACHE='/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114/caches/cache_01'
PY='/home/tanh/sponge-venv/bin/python'
OPTIONS=['-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10']
TAG='qa-pi3b-usb-guard-metadata-20261115'


def save(name,obj):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)


def remote(code):
    p=subprocess.run(['ssh',*OPTIONS,'tanh@192.168.10.11',PY+' -'],input=code,text=True,capture_output=True,timeout=60)
    return dict(command=code,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)


def main(commit):
    if subprocess.check_output(['git','rev-parse',TAG],text=True).strip()!=commit:raise ValueError('tag differs')
    frozen=subprocess.check_output(['git','show',commit+':sponge-sim/studies/pi3b_renderer_memory_usb_20261115/usb_guard.py'])
    assert SOURCE.read_bytes()==frozen;digest=hashlib.sha256(frozen).hexdigest()
    code=f'''from pathlib import Path
import json,subprocess
b=Path({REMOTE!r});assert not b.exists()
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines());assert service==dict(ActiveState='inactive',MainPID='0')
b.mkdir(exist_ok=False)
print(json.dumps(dict(created=str(b),service=service)))
'''
    prep=remote(code);save('deployment_preflight.json',prep)
    if prep['returncode']:raise RuntimeError(prep['stderr'])
    r=subprocess.run(['scp',*OPTIONS,str(SOURCE),f'tanh@192.168.10.11:{REMOTE}/usb_guard.py'],capture_output=True,text=True,timeout=60)
    save('source_deployment.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,source_sha256=digest,commit=commit))
    if r.returncode:raise RuntimeError('partial deployment retained; no overwrite')
    code=f'''from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import os,sys,json,hashlib,traceback,platform
b=Path({REMOTE!r});out=b/'qa_metadata_01.json';assert not out.exists()
assert hashlib.sha256((b/'usb_guard.py').read_bytes()).hexdigest()=={digest!r}
sys.path.insert(0,str(b));import usb_guard as u
def context():
 swaps=Path('/proc/swaps').read_text()
 return dict(governor=Path('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor').read_text(),
  swap_layout=[line.split()[:3]+line.split()[4:] for line in swaps.splitlines()[1:]],affinity=sorted(os.sched_getaffinity(0)))
result=dict(tag={TAG!r},commit={commit!r},source_sha256={digest!r},scope='Read-only USB API QA, no workload',before_context=context(),observed_at_utc=datetime.now(timezone.utc).isoformat())
try:
 assert platform.system()=='Linux' and platform.machine()=='aarch64'
 paths=dict(workspace=b,cache=Path({CACHE!r}))
 result['before']=u.read_snapshot(paths);a=result['before']
 assert set(a['disks'])=={{'sda','sdb'}}
 assert a['disks']['sda']['vendor']=='ADATA SP' and a['disks']['sda']['model']=='900'
 assert a['disks']['sda']['sectors']==250069680 and a['disks']['sdb']['sectors']==0
 assert a['disks']['sda']['partitions']['sda1']['sectors']==250067599
 assert all(p['dev']=='179:2' for p in a['paths'].values())
 result['candidate_contract']=u.make_contract(a)
 result['after']=u.read_snapshot(paths);z=result['after']
 result['pair_errors']=u.validate(z,result['candidate_contract'],a);assert not result['pair_errors']
 cases={{}}
 bad=deepcopy(z);bad['disks']['sda']['model']='synthetic_wrong_model'
 cases['wrong_model']=u.validate(bad,result['candidate_contract'],a);assert 'usb_identity_or_datapath' in cases['wrong_model']
 bad=deepcopy(z);bad['disks']['sda']['stat'][0]+=1
 cases['io_increment']=u.validate(bad,result['candidate_contract'],a);assert 'usb_io_or_counter_reset' in cases['io_increment']
 bad=deepcopy(z);bad['disks']['sda']['stat'][8]=1
 cases['in_flight']=u.validate(bad,result['candidate_contract'],a);assert 'usb_in_flight' in cases['in_flight']
 result['synthetic_negative_checks']=cases
 assert 'torch' not in sys.modules and 'scipy' not in sys.modules
 result['after_context']=context();assert result['before_context']==result['after_context']
 result['status']='PASS_USB_METADATA_API_ONLY'
except BaseException as exc:
 result.update(status='FAIL_STOP_NO_RETRY',error=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),after_context=context())
result['completed_at_utc']=datetime.now(timezone.utc).isoformat()
with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps(dict(status=result['status'],result_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),source_sha256={digest!r})))
raise SystemExit(0 if result['status']=='PASS_USB_METADATA_API_ONLY' else 1)
'''
    actual=remote(code);save('device_invocation.json',actual)
    r=subprocess.run(['scp',*OPTIONS,f'tanh@192.168.10.11:{REMOTE}/qa_metadata_01.json',str(B/'qa_metadata_01.json')],capture_output=True,text=True,timeout=60)
    save('fetch_receipt.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial fetch retained; no overwrite retry')
    advertised=json.loads(actual['stdout']);local=B/'qa_metadata_01.json'
    assert hashlib.sha256(local.read_bytes()).hexdigest()==advertised['result_sha256']
    post=remote(f"from pathlib import Path\nimport json,hashlib\nb=Path({REMOTE!r})\nprint(json.dumps(dict(result_sha256=hashlib.sha256((b/'qa_metadata_01.json').read_bytes()).hexdigest(),source_sha256=hashlib.sha256((b/'usb_guard.py').read_bytes()).hexdigest())))")
    save('post_fetch_verification.json',post)
    assert post['returncode']==0 and json.loads(post['stdout'])==dict(result_sha256=advertised['result_sha256'],source_sha256=digest)
    value=json.loads(local.read_text())
    save('verification.json',dict(status=value['status'],result_sha256=advertised['result_sha256'],remote_local_remote_sha_match=True,
        source_unchanged=True,configuration_unchanged=value['before_context']==value['after_context'],no_model_or_resource_endpoint=True,ssh_kept_open=True))
    print(json.dumps(dict(status=value['status'],remote_local_remote_sha_match=True,no_model_or_resource_endpoint=True)))
    return actual['returncode']


if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
