"""Build lock.json for PI3B-600MHZ. Runs on the laptop BEFORE the prereg tag. No timing."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIM = HERE.parents[1]
SRC = SIM / 'results' / 'laptop_seg_20261107'
CARRY = json.loads((SIM / 'studies' / 'laptop_seg' / 'lock_carryover_full.json').read_text())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


inputs = [Path(p).name for p in CARRY['input_paths']]
assert len(inputs) == 20
files = [dict(name=n, sha256=sha(SRC / n), bytes=(SRC / n).stat().st_size) for n in inputs]
files.append(dict(name='yolov8n-seg.pt', sha256=sha(SRC / 'yolov8n-seg.pt'), bytes=(SRC / 'yolov8n-seg.pt').stat().st_size))
files.append(dict(name='run.py', sha256=sha(HERE / 'run.py'), bytes=(HERE / 'run.py').stat().st_size))
files.append(dict(name='campaign.sh', sha256=sha(HERE / 'campaign.sh'), bytes=(HERE / 'campaign.sh').stat().st_size))
carry = {r['path'].split('/')[-1]: r['sha256'] for r in CARRY['files']}
for r in files[:21]:                      # same bytes as the laptop carryover lock
    assert carry[r['name']] == r['sha256'], r['name']
lock = dict(
    experiment='PI3B-600MHZ', seed=20261114, governor='powersave',
    weights='yolov8n-seg.pt', inputs=inputs, files=files,
    versions=dict(torch='2.15.0+cpu', torchvision='0.29.2+cpu', ultralytics='8.4.90',
                  numpy='2.5.4', python='3.13.5'),
    nms_source_sha256=CARRY['nms_source_sha256'], ops_source_sha256=CARRY['ops_source_sha256'],
    laptop_versions=CARRY['versions'],
    derived_from={p: sha(SIM.parent / p) for p in (
        'sponge-sim/studies/laptop_seg/run.py', 'sponge-sim/studies/laptop_seg/defense_replay.py',
        'sponge-sim/studies/laptop_seg/output_lifetime.py', 'sponge-sim/studies/laptop_seg/lock_carryover_full.json')},
    profiles=dict(PI4=dict(cpus=[0, 1, 2, 3]), PI1=dict(cpus=[3])),
    defense=dict(max_det=300, max_nms=300),
    dose_levels=[1, 10, 30, 100, 300],
    gates=dict(reference_drift=.03, max_reference_flags=2, clock_hz=[594_000_000, 606_000_000],
               abort_temp_c=75.0, abort_mem_available_kb=40_000, aa_abs_log=.02, mde_log=.05),
    full=dict(n_images=20, repeats=dict(pipeline_PI4=6, pipeline_PI1=4, stages_PI4=5), dose_images=5,
              global_warmup=3, reference_warmup=1, reference_samples=3, warmup_per_image=1, pin_seconds=3),
    smoke=dict(n_images=2, repeats=dict(pipeline_PI4=2, pipeline_PI1=2, stages_PI4=2), dose_images=1,
               global_warmup=1, reference_warmup=1, reference_samples=3, warmup_per_image=1, pin_seconds=3),
)
(HERE / 'lock.json').write_text(json.dumps(lock, indent=2) + '\n', encoding='utf-8')
print('lock.json sha256', sha(HERE / 'lock.json'))
