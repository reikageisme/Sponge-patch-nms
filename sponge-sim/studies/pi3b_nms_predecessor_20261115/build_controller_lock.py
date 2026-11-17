"""Freeze prospective QA-only controller sources; never launches any device work."""
from pathlib import Path
import ast
import json
from bindings import HERE,ROOT,SOURCE_FILES,REFERENCES,sha,FULL_LOCK_SHA,CACHE_MANIFEST_SHA


def build():
    original=HERE.parent/'pi3b_renderer_memory_usb_20261115/control.py'
    a=ast.parse(original.read_text(encoding='utf-8'));b=ast.parse((HERE/'control.py').read_text(encoding='utf-8'))
    wanted={'record','System','validate_snapshot','Lease'}
    selected=lambda tree:{n.name:ast.dump(n) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted}
    if selected(a)!=selected(b):raise ValueError('qualified supervisor/lease AST differs')
    if sha(HERE/'full20_lock.json')!=FULL_LOCK_SHA or sha(HERE/'cache_manifest.json')!=CACHE_MANIFEST_SHA:
        raise ValueError('old material reference bytes changed')
    plan=HERE.parents[1]/'prereg/QA_PI3B_NMS_PREDECESSOR_SUPERVISOR_20261115.md'
    lock=dict(workspace=ROOT.as_posix(),qa_tag='qa-pi3b-nms-predecessor-supervisor-20261115',
        empirical_endpoints_enabled=False,scientific_enabled=False,functional_enabled=False,
        source_sha256={n:sha(HERE/n) for n in sorted(SOURCE_FILES)},
        reference_sha256={n:sha(HERE/n) for n in sorted(REFERENCES)},qa_plan_sha256=sha(plan),
        governor='powersave',cpus=[0,1,2,3],gates=dict(clock_hz=[594000000,606000000],abort_temp_c=75,abort_mem_available_kb=40000),
        usb_contract=json.loads((HERE/'usb_contract.json').read_text()),
        old_lease_ast_unchanged=True,model_retained_once=True,clean_adv_materials_resident_together=True,
        functional_worker_present_but_not_enabled=True,no_scientific_worker=True)
    with (HERE/'controller_lock.json').open('x',encoding='utf-8') as f:json.dump(lock,f,indent=2)
    print(json.dumps(dict(status='CONTROLLER_SLEEP_QA_ONLY',source_files=len(SOURCE_FILES),functional_enabled=False,scientific_enabled=False)))


if __name__=='__main__':build()
