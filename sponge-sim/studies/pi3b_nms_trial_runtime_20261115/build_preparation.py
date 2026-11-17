"""Snapshot host-qualified control helpers; NEVER enables a device campaign."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
B=ROOT/'sponge-sim/results/pi3b_trial_runtime_host_qa_20261115'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    files=sorted(p for p in HERE.iterdir() if p.is_file())
    test=ROOT/'sponge-sim/tests/test_pi3b_trial_runtime.py'
    review=ROOT/'sponge-sim/results/pi3b_ready_observer_host_qa_20261115'
    frozen=json.loads((review/'qualification_lock.json').read_text())
    for rel,digest in {**frozen['source_sha256'],frozen['plan_path']:frozen['plan_sha256']}.items():
        assert sha(ROOT/rel)==digest
        blob=subprocess.check_output(['git','show',f"{frozen['qualification_tag']}:{rel}"],cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest()==digest
    assert not (review/'method_approval.json').exists()
    assert not (review/'requests').exists() and not (review/'qualification_outcomes.json').exists()
    old=ROOT/'sponge-sim/results/pi3b_predecessor_supervisor_qa_20261115'
    payload=json.loads((old/'source_preparation.json').read_text())['source_sha256']
    for name,digest in payload.items():assert sha(ROOT/'sponge-sim/studies/pi3b_nms_predecessor_20261115'/name)==digest
    originals=json.loads((old/'partial_transfer_verification.json').read_text())['files']
    for name,entry in originals.items():assert sha(old/'runs'/name)==entry['sha256']
    lock=dict(status='PREPARED_FULL_SESSION_CONTROLS_HOST_ONLY',source_sha256={p.name:sha(p) for p in files},
        test_source_sha256=sha(test),new_host_tests=53,combined_host_tests=199,
        host_log='host_checks_07.log',host_log_sha256=sha(B/'host_checks_07.log'),
        scientific_registration_exists=False,native_activation_supported=False,native_workload_or_query_executed=False,
        source_bound_model_material_provider_implemented=False,whole_campaign_audit_implemented=False,
        old_payload_files_unchanged=len(payload),old_failed_raw_files_unchanged=len(originals),
        frozen_readiness_review_tag=frozen['qualification_tag'],frozen_readiness_review_sources_and_plan_unchanged=True,
        specific_readiness_approval_received=False,
        known_host_failures_retained=['host_checks_01.log','host_checks_04.log','host_checks_06_lifetime_regression.log'],
        actual_pi_api_version_schema_and_parallelism_still_unqualified=True)
    with (B/'preparation_lock.json').open('x',encoding='utf-8') as f:json.dump(lock,f,indent=2)
    archive=B/'registered_materials';archive.mkdir(exist_ok=False)
    for path in [*files,test]:
        with (archive/path.name).open('xb') as f:f.write(path.read_bytes())
    print(json.dumps(dict(status=lock['status'],source_files=len(files),new_tests=53,combined_tests=199,native_actions=0)))


if __name__=='__main__':main()
