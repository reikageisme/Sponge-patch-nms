# Postterminal collector adapted from sponge-sim/results/pi3b_predecessor_supervisor_qa_20261115/collect_device_qa.py:1-59
# SHA256 42c787b090380e71123a7ca24474a7402ecb7701ed86a10aa435ab531e3f1f47; copies all six directories, retains original failed normal case unchanged.
"""Collect all terminal sleeping cases once and verify original bytes/readback."""
from pathlib import Path
import hashlib
import json
import subprocess
from run_qualification import B,REMOTE,PY,SSH,save
from prepare_remote import query as remote
from readiness_plan import validate_prelaunch

PROBE=f'''from pathlib import Path
import sys,json,hashlib,subprocess
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
r=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(x.split('=',1) for x in r.stdout.splitlines());assert service.get('MainPID')=='0' and service.get('ActiveState') in ('inactive','failed'),service
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={{p.relative_to(b/'runs').as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted((b/'runs').rglob('*')) if p.is_file()}}
sources={{p.name:sha(p) for p in b.iterdir() if p.is_file()}}
side=Path('/home/tanh/sponge-sim/pi3b_ready_observer_20261115/probe.py')
assert sha(side)=='ad9196e38a2d8336262397b36e05b376e10f75397057e1c284c4abce7e598bde'
snapshot=control.System().snapshot();control.validate_snapshot(snapshot)
masks=control.System().current()['masks'];assert not any(masks.values())
workers=[]
for p in Path('/proc').iterdir():
 if p.name.isdecimal():
  try:
   argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\\0') if x]
   if any(str(b/n) in argv for n in ('control.py','worker.py','campaign.py')):workers.append(dict(pid=int(p.name),argv=argv))
  except OSError:pass
assert not workers,workers
print(json.dumps(dict(service=service,files=files,source_sha256=sources,snapshot=snapshot,masks=masks,workers=workers,torch_imported='torch' in sys.modules)))
'''


def main():
    outcome=json.loads((B/'qualification_outcomes.json').read_text())
    assert outcome['status']=='FIVE_READY_OBSERVER_CASES_PASS' and len(outcome['cases'])==5
    lock=validate_prelaunch(B,outcome['qualification_commit'])
    assert list(outcome['cases'])==lock['case_names']
    assert outcome['qualification_tag']==lock['qualification_tag'] and outcome['payload_commit']==lock['payload_commit']
    assert outcome['payload_tag']==lock['payload_tag']
    if (B/'runs').exists():raise FileExistsError('original local destination exists')
    before=remote(PROBE);save('remote_before_fetch.json',dict(command=PROBE,result=before))
    r=subprocess.run(['scp',*SSH[1:-1],'-r',f'tanh@192.168.10.11:{REMOTE}/runs',str(B/'runs')],capture_output=True,text=True,timeout=120)
    save('fetch_receipt.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial transfer retained, no overwrite retry')
    after=remote(PROBE);save('remote_after_fetch.json',dict(command=PROBE,result=after))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    files={p.relative_to(B/'runs').as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in (B/'runs').rglob('*') if p.is_file()}
    assert files==before['files']==after['files']
    assert {n.split('/')[0] for n in files}=={'qa_normal_01',*lock['case_names']}
    for name,entry in lock['original_device_files'].items():assert files[name]==entry
    prep=dict(source_sha256=json.loads((B/'qualification_lock.json').read_text())['payload_files_sha256'])
    assert before['source_sha256']==after['source_sha256']==prep['source_sha256']
    assert before['torch_imported'] is False and after['torch_imported'] is False
    for case in outcome['cases']:
        d=B/'runs'/case;restore=json.loads((d/'restore.json').read_text());state=json.loads((d/'lease_state.json').read_text())
        assert restore['status']=='RESTORED' and restore['errors']==[]
        original=state['original']
        norm=lambda rows:[{k:v for k,v in row.items() if k!='used_kb'} for row in rows]
        for obs in (before,after):
            assert all(obs['snapshot'][k]==original[k] for k in ('governor','units','setup'))
            assert norm(obs['snapshot']['swaps'])==norm(original['swaps'])
    save('transfer_verification.json',dict(status='FIVE_NEW_METHOD_CASES_ORIGINALS_VERIFIED',files=files,source_sha256=prep['source_sha256'],
        original_files=len(files),remote_local_remote_sha_match=True,source_unchanged=True,restore_readback_verified=True,
        no_model_or_empirical_endpoint=True,ssh_kept_open=True,original_failed_qualification_unchanged=True,functional_activation_authorized=False,qualification_tag=outcome['qualification_tag'],qualification_commit=outcome['qualification_commit']))
    print(json.dumps(dict(status='FIVE_NEW_METHOD_CASES_ORIGINALS_VERIFIED',original_files=len(files),bytes=sum(x['bytes'] for x in files.values()),source_unchanged=True,restore_readback_verified=True)))


if __name__=='__main__':main()
