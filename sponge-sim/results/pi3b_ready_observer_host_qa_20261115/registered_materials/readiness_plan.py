"""Host-only admission gate for a proposed, explicitly reviewed exception.

No approval event exists at preparation. Never infer permission from goal
continuation, old RSS full approval, old native exit0 or synthetic test PASS.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

TAG='qa-pi3b-ready-observer-20261115'
PAYLOAD_COMMIT='925c544f618491e5b21a3621d77804a10686d111'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_prelaunch(base,commit):
    base=Path(base).resolve();root=base.parents[2]
    if not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError('qualification commit required')
    # Required before any query, namespace allocation or lease.
    approval=json.loads((base/'method_approval.json').read_text(encoding='utf-8'))
    lock_path=base/'qualification_lock.json';lock=json.loads(lock_path.read_text())
    if (approval.get('user_approved') is not True
        or approval.get('accepts_new_qualification_after_failed_attempt') is not True
        or approval.get('qualification_tag')!=TAG or approval.get('qualification_commit')!=commit
        or approval.get('qualification_lock_sha256')!=sha(lock_path)
        or approval.get('original_failure_sha256')!=lock['original_failure_sha256']):
        raise ValueError('specific reviewed exception missing or different')
    if (lock['qualification_tag']!=TAG or lock['payload_commit']!=PAYLOAD_COMMIT
        or lock['scientific_enabled'] is not False or lock['functional_model_enabled'] is not False):
        raise ValueError('engineering-only identity differs')
    if subprocess.check_output(['git','rev-parse',TAG],cwd=root,text=True).strip()!=commit:
        raise ValueError('qualification tag differs')
    tagged_lock=subprocess.check_output(['git','show',f'{commit}:{lock_path.relative_to(root).as_posix()}'],cwd=root)
    if hashlib.sha256(tagged_lock).hexdigest()!=sha(lock_path):raise ValueError('tagged qualification lock differs')
    for rel,digest in lock['source_sha256'].items():
        if sha(root/rel)!=digest:raise ValueError('prepared source changed: '+rel)
        blob=subprocess.check_output(['git','show',f'{commit}:{rel}'],cwd=root)
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('qualification tag bytes differ: '+rel)
    if sha(root/lock['plan_path'])!=lock['plan_sha256']:raise ValueError('proposal changed')
    if hashlib.sha256(subprocess.check_output(['git','show',f"{commit}:{lock['plan_path']}"],cwd=root)).hexdigest()!=lock['plan_sha256']:
        raise ValueError('tagged proposal differs')
    if sha(root/lock['original_failure_path'])!=lock['original_failure_sha256']:raise ValueError('closed failure changed')
    payload=root/'sponge-sim/studies/pi3b_nms_predecessor_20261115'
    for name,digest in lock['payload_files_sha256'].items():
        if sha(payload/name)!=digest:raise ValueError('old controller bytes changed')
        rel=(payload/name).relative_to(root).as_posix()
        if hashlib.sha256(subprocess.check_output(['git','show',f'{PAYLOAD_COMMIT}:{rel}'],cwd=root)).hexdigest()!=digest:
            raise ValueError('old controller tag binding differs')
    return lock
