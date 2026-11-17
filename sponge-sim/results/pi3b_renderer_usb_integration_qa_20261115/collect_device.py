# Adapted from sponge-sim/results/pi3b_renderer_memory_v1_qa_20261114/collect_device.py:1-76
# SHA256 5c81fe6337f8c7ce90aca6bd397ccb3769edc867faf2b315c4e3742aae29f19b; USB namespace and preserve old metadata artifact as an extra hashed root file.
"""Read-only collection after sleeping-QA terminal; fresh destinations only."""
from pathlib import Path
import hashlib
import json
import subprocess

B=Path(__file__).resolve().parent
OPTIONS=['-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10']
REMOTE='/home/tanh/sponge-sim/pi3b_renderer_memory_usb_20261115'
PROBE=f'''from pathlib import Path
import sys,json,subprocess,hashlib
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines())
assert service==dict(ActiveState='inactive',MainPID='0'),service
lock=control.locked_materials(b);snapshot=control.System().snapshot();control.validate_snapshot(snapshot)
assert not any(control.System().current()['masks'].values())
workers=[]
known={{str(b/n) for n in ('control.py','memory_campaign.py','memory_worker.py')}}
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\\0') if v]
   if any(v in known for v in argv):workers.append(dict(pid=int(p.name),argv=argv))
  except OSError:pass
assert not workers
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={{p.relative_to(b).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted((b/'runs').rglob('*')) if p.is_file()}}
assert not (b/'memory_registration.json').exists()
assert 'torch' not in sys.modules and 'scipy' not in sys.modules
print(json.dumps(dict(service=service,snapshot=snapshot,workers=workers,files=files,
 source_sha256={{p.name:sha(p) for p in b.iterdir() if p.is_file()}},scientific_registration_exists=False,torch_imported=False,scipy_imported=False)))
'''


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def probe():
    r=subprocess.run(['ssh',*OPTIONS,'tanh@192.168.10.11','/home/tanh/sponge-venv/bin/python -'],input=PROBE,text=True,capture_output=True,timeout=90)
    if r.returncode:raise RuntimeError(r.stderr or r.stdout)
    return json.loads(r.stdout)


def main():
    if (B/'runs').exists():raise FileExistsError('raw destination exists; no overwrite')
    before=probe();save('remote_before_fetch.json',dict(command=PROBE,result=before))
    r=subprocess.run(['scp',*OPTIONS,'-r',f'tanh@192.168.10.11:{REMOTE}/runs',str(B)],capture_output=True,text=True,timeout=180)
    save('fetch_receipt.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial transfer retained, no overwrite retry')
    after=probe();save('remote_after_fetch.json',dict(command=PROBE,result=after))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    local={p.relative_to(B).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted((B/'runs').rglob('*')) if p.is_file()}
    assert before['files']==local==after['files']
    prepared=json.loads((B/'source_preparation.json').read_text())
    expected=dict(prepared['source_sha256'])
    prior=Path('sponge-sim/results/pi3b_usb_guard_qa_20261115/qa_metadata_01.json')
    expected['qa_metadata_01.json']=hashlib.sha256(prior.read_bytes()).hexdigest()
    assert before['source_sha256']==after['source_sha256']==expected
    expected=json.loads((B/'readonly_preflight.json').read_text())['result']['snapshot']
    norm=lambda rows:[{k:v for k,v in r.items() if k!='used_kb'} for r in rows]
    for result in (before,after):
        now=result['snapshot']
        assert all(now[k]==expected[k] for k in ('governor','units','setup'))
        assert norm(now['swaps'])==norm(expected['swaps'])
    outcomes=json.loads((B/'device_qa_outcomes.json').read_text())
    assert outcomes['status']=='FIVE_ENGINEERING_CASES_PASS' and len(outcomes['cases'])==5
    for case in outcomes['cases']:
        assessed=json.loads((B/(case+'.assessment.json')).read_text())
        assert assessed['restore']==json.loads((B/'runs'/case/'restore.json').read_text())
        assert assessed['child_identity_gone'] is True
        assert assessed['sha256']=={p.relative_to(B/'runs'/case).as_posix():sha(p) for p in (B/'runs'/case).rglob('*') if p.is_file()}
    save('transfer_verification.json',dict(status='FIVE_SLEEP_CASES_AND_ALL_ORIGINAL_SHAS_VERIFIED',original_files=len(local),files=local,
        source_unchanged=True,restore_independent_readback=True,ssh_kept_open=True,scientific_registration_exists=False,empirical_endpoint_recorded=False))
    print(json.dumps(dict(status='VERIFIED_SLEEP_QA_TRANSFER',original_files=len(local),bytes=sum(v['bytes'] for v in local.values()))))


if __name__=='__main__':main()
