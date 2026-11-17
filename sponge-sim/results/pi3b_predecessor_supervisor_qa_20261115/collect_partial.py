"""Postterminal evidence collection after driver observation timeout; no retry.

The planned five-case run is not promoted to PASS. Keep all client/remote
originals and independently inspect restore after authoritative MainPID0.
"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

from collect_device_qa import PROBE
from run_device_qa import B,REMOTE,PY,SSH,script,ASSESS


def save(name,value):
    with (B/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)


def remote(code):
    ast.parse(code)
    p=subprocess.run([*SSH,PY+' -'],input=code,text=True,capture_output=True,timeout=60)
    if p.returncode:raise RuntimeError(p.stderr or p.stdout)
    return json.loads(p.stdout)


def main():
    if (B/'runs').exists():raise FileExistsError('never overwrite fetched originals')
    before=remote(PROBE);save('partial_remote_before_fetch.json',dict(command=PROBE,result=before))
    assert before['files'] and {n.split('/')[0] for n in before['files']}=={'qa_normal_01'}
    r=subprocess.run(['scp',*SSH[1:-1],'-r',f'tanh@192.168.10.11:{REMOTE}/runs',str(B/'runs')],capture_output=True,text=True,timeout=120)
    save('partial_fetch_receipt.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial transfer retained, no overwrite retry')
    after=remote(PROBE);save('partial_remote_after_fetch.json',dict(command=PROBE,result=after))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    files={p.relative_to(B/'runs').as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in (B/'runs').rglob('*') if p.is_file()}
    assert files==before['files']==after['files']
    prep=json.loads((B/'source_preparation.json').read_text())
    assert before['source_sha256']==after['source_sha256']==prep['source_sha256']
    d=B/'runs/qa_normal_01';restore=json.loads((d/'restore.json').read_text());state=json.loads((d/'lease_state.json').read_text())
    assert restore['status']=='RESTORED' and restore['errors']==[]
    original=state['original'];norm=lambda rows:[{k:v for k,v in row.items() if k!='used_kb'} for row in rows]
    for obs in (before,after):
        assert not obs['workers'] and not any(obs['masks'].values()) and obs['torch_imported'] is False
        assert all(obs['snapshot'][k]==original[k] for k in ('governor','units','setup'))
        assert norm(obs['snapshot']['swaps'])==norm(original['swaps'])
    assessed=remote(script('qa_normal_01',ASSESS))
    save('qa_normal_01.postterminal_assessment.json',assessed)
    save('partial_transfer_verification.json',dict(status='ORIGINALS_VERIFIED_SUPERVISOR_QA_INCOMPLETE_NO_RETRY',files=files,
        source_sha256=prep['source_sha256'],original_files=len(files),remote_local_remote_sha_match=True,
        source_unchanged=True,restore_readback_verified=True,child_identity_gone=assessed['child_identity_gone'],
        planned_cases=5,allocated_cases=['qa_normal_01'],live_readiness_observation_complete=False,
        five_cases_pass=False,functional_activation_authorized=False,sshd_kept_open=True))
    print(json.dumps(dict(status='PARTIAL_ORIGINALS_VERIFIED_NO_RETRY',original_files=len(files),restore_readback_verified=True,
        child_identity_gone=assessed['child_identity_gone'],five_cases_pass=False)))


if __name__=='__main__':main()
