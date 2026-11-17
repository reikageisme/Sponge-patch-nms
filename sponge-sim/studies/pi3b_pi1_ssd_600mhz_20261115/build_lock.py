"""Build lock.json for PI3B-PI1-SSD. Runs on the laptop BEFORE the prereg tag. No timing.

Same frozen materials as pi3b_600mhz/pi3b_full20 (20 PGD pairs + weights), so the PI1
single-thread numbers use byte-identical inputs. The only declared difference from PI4 is
allow_usb_storage=True: a separately powered, idle USB SSD is present and recorded.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIM = HERE.parents[1]
SRC = SIM / 'results' / 'laptop_seg_20261107'
CARRY = json.loads((SIM / 'studies' / 'laptop_seg' / 'lock_carryover_full.json').read_text())
BASE600 = json.loads((SIM / 'studies' / 'pi3b_600mhz' / 'lock.json').read_text())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


inputs = [Path(p).name for p in CARRY['input_paths']]
assert len(inputs) == 20 and inputs == BASE600['inputs']
files = [dict(name=n, sha256=sha(SRC / n), bytes=(SRC / n).stat().st_size) for n in inputs]
files.append(dict(name='yolov8n-seg.pt', sha256=sha(SRC / 'yolov8n-seg.pt'), bytes=(SRC / 'yolov8n-seg.pt').stat().st_size))
files.append(dict(name='run.py', sha256=sha(HERE / 'run.py'), bytes=(HERE / 'run.py').stat().st_size))
files.append(dict(name='campaign_pi1.sh', sha256=sha(HERE / 'campaign_pi1.sh'), bytes=(HERE / 'campaign_pi1.sh').stat().st_size))
carry = {r['path'].split('/')[-1]: r['sha256'] for r in CARRY['files']}
for r in files[:21]:                      # same bytes as the laptop carryover lock and pi3b_600mhz
    assert carry[r['name']] == r['sha256'], r['name']
lock = dict(
    experiment='PI3B-PI1-SSD', seed=20261115, governor='powersave',
    allow_usb_storage=True,
    condition_note=('single CPU thread (logical CPU 3); separately powered idle USB SSD '
                    'attached and recorded; distinct declared condition, NOT pooled with PI4 (no-USB).'),
    weights='yolov8n-seg.pt', inputs=inputs, files=files,
    versions=BASE600['versions'],
    nms_source_sha256=CARRY['nms_source_sha256'], ops_source_sha256=CARRY['ops_source_sha256'],
    laptop_versions=CARRY['versions'],
    base_pi3b_lock_sha256=sha(SIM / 'studies' / 'pi3b_600mhz' / 'lock.json'),
    copied_from=dict(run_py='sponge-sim/studies/pi3b_600mhz/run.py',
                     run_py_sha256='9cc349be2c265fb4615d0016e9dae4a5aef53961df0d603abcb42d7a9fdbec8a',
                     analyze_py='sponge-sim/studies/pi3b_600mhz/analyze.py',
                     analyze_py_sha256='8af562c9bca2b3e5c0889e7d11d271e0cd6d70e0c452028e239741ee002aea58'),
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
print('run.py sha256', sha(HERE / 'run.py'))
print('campaign_pi1.sh sha256', sha(HERE / 'campaign_pi1.sh'))
