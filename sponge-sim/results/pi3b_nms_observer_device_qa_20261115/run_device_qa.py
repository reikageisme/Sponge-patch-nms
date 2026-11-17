# SSH/receipt pattern adapted from sponge-sim/results/pi3b_nms_counter_device_qa_20261115/run_readonly_qa.py:1-91
# SHA256 6a2999a4b0e41ac2bc9614c2201e2c50592e50a5ad7e53c9d00347ce07524f51; old data/source unchanged.
"""One exclusive service API/functional QA; no model/NMS/timing benchmark.

SSH/exclusive-receipt pattern adapted from
sponge-sim/results/pi3b_nms_counter_device_qa_20261115/run_readonly_qa.py;
the earlier source/data remain unchanged. Deployment, terminal waiting and
postterminal collection are separate; never relaunch after transport loss.
"""
from datetime import datetime, timezone
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

B = Path(__file__).resolve().parent
ROOT = B.parents[2]
SOURCE = ROOT/'sponge-sim/studies/pi3b_nms_observer_20261115'
REMOTE = '/home/tanh/sponge-sim/pi3b_nms_observer_20261115'
PY = '/home/tanh/sponge-venv/bin/python'
OPTIONS = ['-i', str(Path.home()/'.ssh/pi_spongepi'), '-oBatchMode=yes',
           '-oStrictHostKeyChecking=yes', '-oConnectTimeout=10']
TAG = 'qa-pi3b-nms-observer-service-20261115'
UNIT = 'sponge-pi3b-nms-observer-qa-20261115.service'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    with (B/name).open('x', encoding='utf-8') as f: json.dump(value, f, indent=2)


def remote(script, timeout=45):
    ast.parse(script)
    r = subprocess.run(['ssh', *OPTIONS, 'tanh@192.168.10.11', PY+' -'],
        input=script, text=True, capture_output=True, timeout=timeout)
    return dict(command=script, returncode=r.returncode, stdout=r.stdout, stderr=r.stderr)


PREFLIGHT = f'''from pathlib import Path
import json,subprocess
b=Path({REMOTE!r});assert not b.exists()
services={{}}
for unit in ('sponge-pi3b-swapguard-v2.service',{UNIT!r}):
 r=subprocess.run(['systemctl','show',unit,'-p','MainPID','-p','ActiveState'],capture_output=True,text=True,timeout=10)
 s=dict(x.split('=',1) for x in r.stdout.splitlines());assert s.get('MainPID')=='0' and s.get('ActiveState')=='inactive',s
 services[unit]=s
b.mkdir(exist_ok=False)
print(json.dumps(dict(created=str(b),services=services)))
'''

PROBE = f'''from pathlib import Path
import json,hashlib,subprocess
b=Path({REMOTE!r})
r=subprocess.run(['systemctl','show',{UNIT!r},'-p','MainPID','-p','ActiveState'],capture_output=True,text=True,timeout=10)
service=dict(x.split('=',1) for x in r.stdout.splitlines())
assert service.get('MainPID')=='0' and service.get('ActiveState') in ('inactive','failed'),service
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((b/'qa_config.json').read_text())
files={{n:dict(sha256=sha(b/n),bytes=(b/n).stat().st_size) for n in ('qa_result_01.json','qa_manifest.json') if (b/n).exists()}}
workers=[]
for p in Path('/proc').iterdir():
 if p.name.isdecimal():
  try:
   argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\\0') if x]
   if str(b/'qa_worker.py') in argv:workers.append(dict(pid=int(p.name),argv=argv))
  except OSError:pass
assert not workers,workers
print(json.dumps(dict(service=service,workers=workers,files=files,
 source_sha256={{n:sha(b/n) for n in config['source_sha256']}},config_sha256=sha(b/'qa_config.json'),
 governor=Path('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor').read_text(),swaps=Path('/proc/swaps').read_text())))
'''


def launch_code(manifest, digests):
    return f'''from pathlib import Path
import json,hashlib,subprocess
b=Path({REMOTE!r});sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert {{n:sha(b/n) for n in {list(digests)!r}}}=={digests!r}
with (b/'qa_manifest.json').open('x',encoding='utf-8') as f:json.dump({manifest!r},f,indent=2)
argv=['sudo','-n','systemd-run','--unit={UNIT}','--wait','--collect',
 '--property=Type=exec','--property=User=tanh','--property=KillMode=control-group',
 '--property=CPUAffinity=0 1 2 3','--property=RuntimeMaxSec=180','--property=TimeoutStopSec=10',
 '--setenv=OMP_NUM_THREADS=4','--setenv=MKL_NUM_THREADS=4','--setenv=OPENBLAS_NUM_THREADS=4',
 {PY!r},str(b/'qa_worker.py'),'--tag',{TAG!r},'--commit',{manifest['commit']!r}]
r=subprocess.run(argv,capture_output=True,text=True,timeout=220)
print(json.dumps(dict(unit_returncode=r.returncode,unit_stdout=r.stdout,unit_stderr=r.stderr,argv=argv)))
'''


def main(commit):
    assert subprocess.check_output(['git', 'rev-parse', TAG], cwd=ROOT, text=True).strip() == commit
    reg = json.loads((SOURCE/'qa_config.json').read_text())
    names = [*reg['source_sha256'], 'qa_config.json']
    for name in names:
        tagged = subprocess.check_output(['git', 'show', f'{commit}:sponge-sim/studies/pi3b_nms_observer_20261115/{name}'], cwd=ROOT)
        assert tagged == (SOURCE/name).read_bytes()
    plan = ROOT/'sponge-sim/prereg/QA_PI3B_NMS_OBSERVER_SERVICE_20261115.md'
    assert sha(plan) == reg['plan_sha256']
    digests = {name: sha(SOURCE/name) for name in names}
    manifest = dict(tag=TAG, commit=commit, config_sha256=sha(SOURCE/'qa_config.json'),
        source_sha256=reg['source_sha256'], created_at_utc=datetime.now(timezone.utc).isoformat(),
        scientific_endpoint_enabled=False, model_or_weights_loaded=False, unit=UNIT)
    save('qa_manifest.json', manifest)
    before = remote(PREFLIGHT); save('deployment_preflight.json', before)
    if before['returncode']: raise RuntimeError('Preflight failed; no retry')
    r = subprocess.run(['scp', *OPTIONS, *[str(SOURCE/n) for n in names], f'tanh@192.168.10.11:{REMOTE}/'], capture_output=True, text=True, timeout=60)
    save('source_deployment.json', dict(returncode=r.returncode, stdout=r.stdout, stderr=r.stderr, sha256=digests))
    if r.returncode: raise RuntimeError('Partial deployment retained; no overwrite retry')
    actual = remote(launch_code(manifest, digests), timeout=240)
    save('device_invocation.json', actual)
    # A failed SSH frontend is not proof of service termination. Probe only state
    # and refuse collection if still live; follow up on the same owned unit.
    terminal = remote(PROBE); save('terminal_before_fetch.json', terminal)
    if terminal['returncode']: raise RuntimeError('No authoritative service terminal; wait same unit, do not restart/fetch')
    first = json.loads(terminal['stdout'])
    assert first['source_sha256'] == reg['source_sha256'] and first['config_sha256'] == manifest['config_sha256']
    if 'qa_result_01.json' not in first['files']: raise RuntimeError('Terminal but no result; retain partial/FAIL, no retry')
    original = B/'original'; original.mkdir(exist_ok=False)
    for name in first['files']:
        r = subprocess.run(['scp', *OPTIONS, f'tanh@192.168.10.11:{REMOTE}/{name}', str(original/name)], capture_output=True, text=True, timeout=45)
        save('fetch_'+name+'.json', dict(returncode=r.returncode, stdout=r.stdout, stderr=r.stderr))
        if r.returncode: raise RuntimeError('Partial fetch retained; no overwrite retry')
    final = remote(PROBE); save('terminal_after_fetch.json', final)
    assert final['returncode'] == 0
    second = json.loads(final['stdout'])
    assert second['files'] == first['files'] and second['source_sha256'] == reg['source_sha256']
    for name, record in first['files'].items():
        assert sha(original/name) == record['sha256'] and (original/name).stat().st_size == record['bytes']
    assert json.loads((original/'qa_manifest.json').read_text()) == manifest
    result = json.loads((original/'qa_result_01.json').read_text())
    assert result['tag'] == TAG and result['commit'] == commit and result['source_sha256'] == reg['source_sha256']
    context = result['before_context']
    assert first['governor'] == second['governor'] == context['governor']
    assert first['swaps'] == second['swaps'] == context['swaps']
    verification = dict(status=result['status'], original_files=first['files'],
        remote_local_remote_sha_match=True, source_unchanged=True,
        context_unchanged=result['after_context'] == context, no_owned_workers=True,
        service_terminal=True, ssh_kept_open=True, no_nms_rss_or_latency_endpoint=True,
        simultaneous_parallel_utilization_qualified=False, observer_sham_qualified=False)
    save('verification.json', verification)
    print(json.dumps(verification))
    return 0 if result['status'] == 'PASS_SERVICE_POOL_INVENTORY_API_ONLY' else 1


if __name__ == '__main__': raise SystemExit(main(sys.argv[1]))
