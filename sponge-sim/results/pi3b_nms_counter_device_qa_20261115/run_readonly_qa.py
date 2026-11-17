"""One finite metadata-only API check; no inference workload or configuration change."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

B=Path(__file__).resolve().parent
SOURCE=B.parents[1]/'studies/pi3b_nms_trace_20261114/counters.py'
REMOTE='/home/tanh/sponge-sim/pi3b_nms_trace_20261114'
PY='/home/tanh/sponge-venv/bin/python'
OPTIONS=['-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10']
TAG='qa-pi3b-nms-counters-20261115'


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def remote(script):
    r=subprocess.run(['ssh',*OPTIONS,'tanh@192.168.10.11',PY+' -'],input=script,text=True,capture_output=True,timeout=45)
    return dict(command=script,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)


def main(commit):
    if subprocess.check_output(['git','rev-parse',TAG],text=True).strip()!=commit:raise ValueError('tag differs')
    assert SOURCE.read_bytes()==subprocess.check_output(['git','show',commit+':sponge-sim/studies/pi3b_nms_trace_20261114/counters.py'])
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    prep=remote(f'''from pathlib import Path
import subprocess,json
b=Path({REMOTE!r});assert not b.exists()
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines());assert service==dict(ActiveState='inactive',MainPID='0')
b.mkdir(exist_ok=False)
print(json.dumps(dict(created=str(b),service=service)))
''');save('deployment_preflight.json',prep)
    if prep['returncode']:raise RuntimeError(prep['stderr'])
    r=subprocess.run(['scp',*OPTIONS,str(SOURCE),f'tanh@192.168.10.11:{REMOTE}/counters.py'],capture_output=True,text=True,timeout=45)
    save('source_deployment.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,sha256=digest,commit=commit))
    if r.returncode:raise RuntimeError('partial deployment retained; no overwrite')
    code=f'''from pathlib import Path
import sys,json,os,hashlib,platform,traceback
b=Path({REMOTE!r});out=b/'qa_snapshot_01.json';assert not out.exists()
assert hashlib.sha256((b/'counters.py').read_bytes()).hexdigest()=={digest!r}
sys.path.insert(0,str(b));import counters
gov=Path('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor')
context=lambda:dict(governor=gov.read_text(),swaps=Path('/proc/swaps').read_text(),affinity=sorted(os.sched_getaffinity(0)))
before=context();result=dict(scope='Metadata API QA only, not NMS/RSS/latency',source_sha256={digest!r},tag={TAG!r},commit={commit!r},before_context=before)
try:
 assert platform.system()=='Linux' and platform.machine()=='aarch64'
 result['before']=counters.snapshot();result['after']=counters.snapshot()
 result['increments']=counters.increments(result['before'],result['after'])
 assert result['before']['pid']==os.getpid() and result['before']['calling_tid']==os.getpid()
 assert result['before']['start_ticks']>0 and result['before']['calling_thread_start_ticks']>0
 for snap in (result['before'],result['after']):
  allowed=set()
  for part in snap['thread_status']['Cpus_allowed_list'].split(','):
   first,sep,last=part.partition('-');allowed.update(range(int(first),int(last if sep else first)+1))
  assert sorted(allowed)==before['affinity']
 assert 'ru_maxrss' not in result['before']['process_counters']
 missing=b/'absent_optional_counter';assert not missing.exists()
 result['missing_optional']=counters.optional(missing)
 assert result['missing_optional']['status']=='UNAVAILABLE'
 assert result['increments']['observer_overhead_included'] is True and result['increments']['unique_wait_cause_identified'] is False
 assert 'torch' not in sys.modules and 'scipy' not in sys.modules
 result['after_context']=context();assert result['after_context']==before
 result['status']='PASS_METADATA_API_ONLY'
except BaseException as exc:
 result.update(status='FAIL_STOP_NO_RETRY',error=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
 result['after_context']=context()
with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps(dict(status=result['status'],result_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),source_sha256={digest!r})))
raise SystemExit(0 if result['status']=='PASS_METADATA_API_ONLY' else 1)
'''
    actual=remote(code);save('device_invocation.json',actual)
    r=subprocess.run(['scp',*OPTIONS,f'tanh@192.168.10.11:{REMOTE}/qa_snapshot_01.json',str(B/'qa_snapshot_01.json')],capture_output=True,text=True,timeout=45)
    save('fetch_receipt.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('metadata fetch failed; preserve state, no retry')
    advertised=json.loads(actual['stdout']);p=B/'qa_snapshot_01.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==advertised['result_sha256']
    value=json.loads(p.read_text());assert value['source_sha256']==digest
    check=remote(f"from pathlib import Path\nimport json,hashlib\nb=Path({REMOTE!r})\nprint(json.dumps(dict(result_sha256=hashlib.sha256((b/'qa_snapshot_01.json').read_bytes()).hexdigest(),source_sha256=hashlib.sha256((b/'counters.py').read_bytes()).hexdigest())))")
    save('post_fetch_verification.json',check)
    assert check['returncode']==0 and json.loads(check['stdout'])==dict(result_sha256=advertised['result_sha256'],source_sha256=digest)
    save('verification.json',dict(status=value['status'],remote_local_remote_sha_match=True,source_unchanged=True,
        result_sha256=advertised['result_sha256'],no_model_operator_or_rss=True,configuration_unchanged=value['before_context']==value['after_context'],ssh_kept_open=True))
    print(json.dumps(dict(status=value['status'],remote_local_remote_sha_match=True,no_model_operator_or_rss=True)))
    return actual['returncode']


if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
