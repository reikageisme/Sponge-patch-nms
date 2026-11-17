"""Prepare ONE functional material export under standing finite-QA scope only."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
S=ROOT/'sponge-sim/studies/pi3b_nms_predecessor_20261115'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    old=ROOT/'sponge-sim/results/pi3b_predecessor_supervisor_qa_20261115'
    ready=ROOT/'sponge-sim/results/pi3b_ready_observer_host_qa_20261115'
    old_package=json.loads((old/'source_preparation.json').read_text())['source_sha256']
    for name,digest in old_package.items():
        assert sha(S/name)==digest
        rel=(S/name).relative_to(ROOT).as_posix()
        assert hashlib.sha256(subprocess.check_output(['git','show',f'925c544f618491e5b21a3621d77804a10686d111:{rel}'],cwd=ROOT)).hexdigest()==digest
    review=json.loads((S/'supervisor_qa_verification.json').read_text());controller=json.loads((S/'controller_lock.json').read_text())
    assert review['status']=='ALL_FIVE_SLEEP_CASES_PASS' and review['original_failed_verdict_replaced'] is False
    assert review['source_sha256']==controller['source_sha256'] and review['independent_restore_readback_verified']
    # Execute only the original pure activation predicate, with a locally checked
    # controller map: native path admission is verified again on Pi before load.
    tree=ast.parse((S/'bindings.py').read_text());fn=next(x for x in tree.body if getattr(x,'name',None)=='activation')
    scope=dict(Path=Path,HERE=S,load=lambda p:json.loads(Path(p).read_text()),read_lock=lambda base:controller,sha=sha)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(S/'bindings.py'),'exec'),scope)
    activation=scope['activation'](S)
    assert activation['scientific_enabled'] is False and activation['cases']==40 and activation['campaign_timeout_seconds']==3600
    plan=ROOT/activation['plan_path'];assert sha(plan)==activation['plan_sha256']
    package={**old_package,**{n:sha(S/n) for n in ('supervisor_qa_verification.json','functional_activation.json')}}
    host=[B/'device.py',B/'audit_material.py',Path(__file__),ROOT/'sponge-sim/tests/test_pi3b_material_phase.py',B/'authorization_basis.json']
    prior=json.loads((ready/'transfer_verification.json').read_text())['files']
    for name,entry in prior.items():assert sha(ready/'runs'/name)==entry['sha256']
    reg=dict(status='PREPARED_ONE_FUNCTIONAL40_NOT_SCIENTIFIC',tag=activation['tag'],package_sha256=package,
        host_source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in host},plan_path=activation['plan_path'],plan_sha256=sha(plan),
        prior_originals=prior,qualified_method_tag=review['qualification_method_tag'],qualified_method_commit=review['qualification_method_commit'],
        runtime_python_files_unchanged=19,controller_base_functional_scientific_flags_unchanged_false=True,
        scientific_enabled=False,performance_endpoints=False,cases=40,worker_cap_seconds=3600,metadata_query_cap_seconds=300,copy_cap_seconds=1800,
        authorization='standing explicit finite functional/device QA; no expansion of the limited sleeping-only exception',host_tests=12,
        host_log_sha256=sha(B/'host_checks_01.log'))
    with (B/'source_preparation.json').open('x',encoding='utf-8') as f:json.dump(reg,f,indent=2)
    archive=B/'registered_materials';archive.mkdir(exist_ok=False)
    for path in [*[S/n for n in package],*host,plan]:
        with (archive/path.name).open('xb') as f:f.write(path.read_bytes())
    assert not subprocess.check_output(['git','tag','--list',activation['tag']],cwd=ROOT,text=True).strip()
    print(json.dumps(dict(status=reg['status'],package_files=len(package),original_python_files_unchanged=19,host_tests=12,model_not_yet_run=True)))


if __name__=='__main__':main()
