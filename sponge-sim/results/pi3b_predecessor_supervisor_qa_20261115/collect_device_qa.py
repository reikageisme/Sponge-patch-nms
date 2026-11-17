"""Collect all terminal sleeping cases once and verify original bytes/readback."""
from pathlib import Path
import hashlib
import json
import subprocess
from run_device_qa import B,REMOTE,PY,SSH,remote,save

PROBE=f'''from pathlib import Path
import sys,json,hashlib,subprocess
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
r=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(x.split('=',1) for x in r.stdout.splitlines());assert service.get('MainPID')=='0' and service.get('ActiveState') in ('inactive','failed'),service
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={{p.relative_to(b/'runs').as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted((b/'runs').rglob('*')) if p.is_file()}}
sources={{p.name:sha(p) for p in b.iterdir() if p.is_file()}}
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
    outcome=json.loads((B/'device_qa_outcomes.json').read_text())
    assert outcome['status']=='FIVE_ENGINEERING_CASES_PASS' and len(outcome['cases'])==5
    if (B/'runs').exists():raise FileExistsError('original local destination exists')
    before=remote(PROBE);save('remote_before_fetch.json',dict(command=PROBE,result=before))
    r=subprocess.run(['scp',*SSH[1:-1],'-r',f'tanh@192.168.10.11:{REMOTE}/runs',str(B/'runs')],capture_output=True,text=True,timeout=120)
    save('fetch_receipt.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial transfer retained, no overwrite retry')
    after=remote(PROBE);save('remote_after_fetch.json',dict(command=PROBE,result=after))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    files={p.relative_to(B/'runs').as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in (B/'runs').rglob('*') if p.is_file()}
    assert files==before['files']==after['files']
    prep=json.loads((B/'source_preparation.json').read_text())
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
    save('transfer_verification.json',dict(status='ALL_FIVE_SLEEP_CASES_PASS',files=files,source_sha256=prep['source_sha256'],
        original_files=len(files),remote_local_remote_sha_match=True,source_unchanged=True,restore_readback_verified=True,
        no_model_or_empirical_endpoint=True,ssh_kept_open=True))
    print(json.dumps(dict(status='ALL_FIVE_SLEEP_CASES_PASS',original_files=len(files),bytes=sum(x['bytes'] for x in files.values()),source_unchanged=True,restore_readback_verified=True)))


if __name__=='__main__':main()
