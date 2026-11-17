"""Postterminal immutable-data/source/paper checks, explicit UTF-8 on Windows."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
B=Path(__file__).resolve().parent
ROOT=B.parents[2]
study=ROOT/'sponge-sim/studies/pi3b_full20_20261114'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
transfer=load(B/'transfer_verification.json')
for name,item in transfer['files'].items():assert sha(B/'runs/full_01'/name)==item['sha256']
locked={}
for p in study.iterdir():
    if not p.is_file():continue
    blob=subprocess.run(['git','show','prereg-pi3b-full20-after-pilot-20261114:'+p.relative_to(ROOT).as_posix()],capture_output=True,check=True,cwd=ROOT).stdout
    assert hashlib.sha256(blob).hexdigest()==sha(p)
    locked[p.name]=sha(p)
for p in (B/'registered_materials').iterdir():
    if (study/p.name).is_file():assert sha(p)==sha(study/p.name)
receipt=load(B/'paper_integration_receipt.json')
for name,digest in receipt['protected_sha256'].items():assert sha(ROOT/name)==digest
assert sha(ROOT/'paper_en/main.tex')==receipt['main_after_sha256']
report=ROOT/'docs/reports/PI3B_FULL20_RESULTS_20261114.md'
text=report.read_text(encoding='utf-8');summary=load(B/'runs/full_01/summary.json')
for key in ('h1_adv_over_clean','h2_advcap_over_adv','advcap_over_clean','forward_adv_over_clean'):
    assert str(summary['pipeline_PI4'][key]['geomean_ratio']) in text
assert not (B/'runs/full_02').exists()
result=dict(status='CLOSED_PRIMARY_PASS_STAGE_FAIL_COMPLETE_AUDIT',original_files_verified=len(transfer['files']),locked_study_equal_tag=locked,
    summary_sha256=sha(B/'runs/full_01/summary.json'),independent_audit_sha256=sha(B/'independent_audit.json'),raw_source_map_sha256=sha(B/'raw_source_map.json'),
    report_sha256=sha(report),paper_checks_sha256=sha(B/'document_checks.json'),protected_paper_artifacts_unchanged=True,main_left_unstaged=True,
    both_pngs_visually_inspected=True,full_pdf_compiled=False,no_new_model_measurement_after_terminal=True,ssh_kept_open=True,
    postdata_tooling_notes=['Initial collector manifest required POSIX key normalization, no byte mismatch.',
                           'Initial ad-hoc final checker used platform cp1252 on Vietnamese report; explicit UTF-8 used here.',
                           'Generated text metadata uses explicit LF; no original raw or locked measurement code edited.'])
with (B/(sys.argv[1] if len(sys.argv)>1 else 'final_verification.json')).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print('Final original-data, tag-source, protected-paper and report-number checks PASS.')
