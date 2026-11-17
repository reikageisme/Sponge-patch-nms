"""Prospective preparation only: freeze source/old failure, never enable native QA."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
S='sponge-sim/studies/pi3b_ready_observer_20261115'
B='sponge-sim/results/pi3b_ready_observer_host_qa_20261115'
OLD='sponge-sim/results/pi3b_predecessor_supervisor_qa_20261115'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    source_paths=[f'{S}/{n}.py' for n in ('probe','transport','readiness_plan','build_lock')]
    source_paths += [f'{B}/{n}.py' for n in ('run_qualification','prepare_remote','collect_qualification')]
    source_paths += ['sponge-sim/tests/test_pi3b_ready_observer.py']
    plan='sponge-sim/prereg/DRAFT_QA_PI3B_READY_OBSERVER_20261115.md'
    failure=OLD+'/device_final_verification.json'
    original=json.loads((ROOT/OLD/'partial_transfer_verification.json').read_text())
    for name,entry in original['files'].items():
        p=ROOT/OLD/'runs'/name
        assert p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256']
    payload=json.loads((ROOT/OLD/'source_preparation.json').read_text())['source_sha256']
    for name,digest in payload.items():assert sha(ROOT/'sponge-sim/studies/pi3b_nms_predecessor_20261115'/name)==digest
    lock=dict(status='PREPARED_PROPOSAL_REQUIRES_SPECIFIC_REVIEW',qualification_tag='qa-pi3b-ready-observer-20261115',
        payload_tag='qa-pi3b-nms-predecessor-supervisor-20261115',payload_commit='925c544f618491e5b21a3621d77804a10686d111',
        source_sha256={p:sha(ROOT/p) for p in source_paths},payload_files_sha256=payload,
        plan_path=plan,plan_sha256=sha(ROOT/plan),original_failure_path=failure,original_failure_sha256=sha(ROOT/failure),
        original_device_files=original['files'],case_names=['observer_'+x+'_01' for x in ('normal','mainkill','childkill','timeout','disconnect')],
        payload_seconds=[15,60,60,90,15],runtime_caps_seconds=[90,120,120,45,90],
        ready_deadline_seconds=40,request_cap_seconds=25,unit_query_cap_seconds=10,
        scientific_enabled=False,functional_model_enabled=False,native_authorized_at_preparation=False,
        prior_failed_qualification_reopened=False,new_attempt_requires_explicit_exception=True,
        changed_method_after_observed_failure=True,observed_timeout_cause_confirmed=False)
    target=ROOT/B/'qualification_lock.json'
    with target.open('x',encoding='utf-8') as f:json.dump(lock,f,indent=2)
    archive=ROOT/B/'registered_materials';archive.mkdir(exist_ok=False)
    for path in [*source_paths,plan]:
        with (archive/Path(path).name).open('xb') as f:f.write((ROOT/path).read_bytes())
    assert not (ROOT/B/'method_approval.json').exists()
    print(json.dumps(dict(status=lock['status'],new_source_files=len(source_paths),payload_files=len(payload),native_run=False)))


if __name__=='__main__':main()
