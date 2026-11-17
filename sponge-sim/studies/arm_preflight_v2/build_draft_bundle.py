"""Create a NEW review-only source bundle; never deploy or start a workload."""
import argparse
import hashlib
import json
from pathlib import Path
import random

SOURCE=Path(__file__).resolve().parent
FILES=('checks.py','linux_observe.py','posix_runtime.py','session.py','pin_analysis.py',
       'pin_worker.py','qa_session.py','metadata_only.py')


def build(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    (output/'source').mkdir();(output/'templates').mkdir()
    hashes={}
    for name in FILES:
        data=(SOURCE/name).read_bytes()
        with (output/'source'/name).open('xb') as f:f.write(data)
        hashes['source/'+name]=hashlib.sha256(data).hexdigest()
    order=[(pool,scope) for pool in ('pin_before_pool','pool_before_pin') for scope in ('main','all')]
    random.Random(20261107).shuffle(order)
    cells=[]
    for index,(pool,scope) in enumerate(order):
        cell_id=f'{index+1}_{pool}_{scope}'
        cfg=dict(cell_id=cell_id,allowed_cpus=[],pool_order=pool,pin_scope=scope,torch_threads=2,
                 matrix_size=256,warmup_matmuls=20,intervals=32,interval_s=.1,
                 max_accounting_slack_fraction=.1,expected_torch_version=None,expected_torch_init_sha256=None)
        path=output/'templates'/f'{cell_id}.json'
        with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(cfg,f,indent=2)
        relative=path.relative_to(output).as_posix();hashes[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
        cells.append(relative)
    readme='''# DRAFT: metadata and review only, no load launcher

No phone experiment has been authorized by this bundle. CPU/runtime/sensor
bindings are unresolved; cell templates intentionally FAIL validation. No
standalone matrix/attack command is provided. Do not fill placeholders and
call that a preregistered run.

The callable four-cell controller/owned spawner is included for review. It is
not a qualified device entry. Earlier A0/A0B phone metadata found unresolved
thermal scales and no verified live SOC/charging route; do not repeat those
same failed reads merely to obtain a different snapshot.

First step, only after actual phone-state/A0 scope confirmation: run the
metadata_only.py script in a new process, saving to a NEW path inside the
declared ~/sponge-sim workspace. It does not import Torch or change affinity.
Sysfs raw inspection needs its explicit --allow-sysfs option; no raw magnitude
is converted into a temperature or accepted as a safety sensor registry.

Before any load: verified typed sensor registry, Android/proot group cleanup
and reaction/overhead QA, supervised launcher, current idle/network/charging
state, locked runtime/CPU/config/source, PREREG + tag. The coordinator and
hash-bound fresh-child spawner are present; the registered device entry,
verified telemetry bindings and physical QA are still missing.

The four templates are fixed-order mechanism controls: two intra-op threads
on ONE metadata-selected logical CPU. Select the lowest inherited readable
CPU ID before load, not the fastest CPU or a result-selected profile. Pin
before/after Torch pool creation crossed with main/all-TID pinning. Each cell
once, fresh worker, same raw snapshots scored all-TID and active-only. A
recorded diagnostic FAIL does not select a retry; safety/infra failures retain
partial data and stop. No diagnostic cell qualifies a segmentation profile.

32 x 0.1s is a nominal capture-work budget, not a bound on warmup/import,
observer IO, kernel overshoot, cooldown, or actual reaction time. Values are
draft planning choices, not measured phone feasibility. Every later change
requires a NEW bundle/lock; keep this directory and all older artifacts.
'''
    with (output/'README.md').open('x',encoding='utf-8',newline='\n') as f:f.write(readme)
    hashes['README.md']=hashlib.sha256((output/'README.md').read_bytes()).hexdigest()
    protocol=(SOURCE.parents[1]/'prereg/DRAFT_ARM_POOL_QA_20261107.md').read_bytes()
    with (output/'DRAFT_PROTOCOL.md').open('xb') as f:f.write(protocol)
    hashes['DRAFT_PROTOCOL.md']=hashlib.sha256(protocol).hexdigest()
    manifest=dict(status='DRAFT_UNRUN_NOT_AUTHORIZED_FOR_LOAD',prereg_tag=None,prereg_commit=None,
                  source_root='source',cell_order_seed=20261107,cells=cells,files_sha256=hashes,
                  builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  unresolved=['actual CPU ID','Torch version/init SHA','sensor IDs/type/unit/permissions',
                              'device cleanup and observation overhead','registered/qualified device entry',
                              'actual idle/network/charging state','registered protocol/tag'])
    with (output/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(manifest,f,indent=2)
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=build(args.output)
    print(result['status'],len(result['files_sha256']),'SHA-bound files; no deployment',flush=True)
