"""PI3B-600MHZ contracts on synthetic rows: no model, no device, no timing."""
import importlib.util
import json
import math
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parents[1] / 'studies' / 'pi3b_600mhz'


def load(name):
    spec = importlib.util.spec_from_file_location(f'pi3b_{name}', STUDY / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


run = load('run')
analyze = load('analyze')
LOCK = json.loads((STUDY / 'lock.json').read_text())


def test_arm_order_is_seeded_permutation():
    for ix in range(20):
        for rep in range(6):
            order = run.arm_order(6, ix, rep, LOCK['seed'])
            assert sorted(order) == list(range(6))
            assert order == run.arm_order(6, ix, rep, LOCK['seed'])
    firsts = {run.arm_order(6, ix, rep, LOCK['seed'])[0] for ix in range(20) for rep in range(6)}
    assert firsts == set(range(6))            # every arm leads somewhere


def test_dose_levels_never_exceed_available():
    assert run.dose_levels(300, LOCK['dose_levels']) == [1, 10, 30, 100, 300]
    assert run.dose_levels(57, LOCK['dose_levels']) == [1, 10, 30]
    assert run.dose_levels(0, LOCK['dose_levels']) == []


def test_lock_binds_same_inputs_as_laptop_and_runner_bytes():
    names = {r['name'] for r in LOCK['files']}
    assert len(LOCK['inputs']) == 20 and set(LOCK['inputs']) <= names
    assert {'run.py', 'campaign.sh', 'yolov8n-seg.pt'} <= names
    by = {r['name']: r['sha256'] for r in LOCK['files']}
    assert by['run.py'] == run.sha(STUDY / 'run.py')
    assert by['campaign.sh'] == run.sha(STUDY / 'campaign.sh')
    assert LOCK['profiles'] == {'PI4': {'cpus': [0, 1, 2, 3]}, 'PI1': {'cpus': [3]}}
    assert LOCK['defense'] == {'max_det': 300, 'max_nms': 300}


def env(clock=600_000_000, governor='powersave', swap=0, temp=40.0, throttled='throttled=0x50005'):
    return dict(governor=governor, scaling_cur_khz=600000, arm_clock_hz=f'frequency(48)={clock}',
                temp=f"temp={temp}'C", throttled=throttled,
                mem_kb=dict(MemTotal=927000, MemAvailable=600000, SwapTotal=swap, SwapFree=swap),
                vmstat={}, loadavg=[0, 0, 0])


def synthetic(tmp_path, adv=3.0, cap=0.5, n=20, **bad):
    d = tmp_path / 'pipeline_PI4'
    d.mkdir()
    rows = [dict(kind='pin_start', passed=True), dict(kind='reference', block='start', ratio=1.0, flagged=False)]
    for ix in range(n):
        im = f'{ix:012d}'
        rows.append(dict(kind='environment', block=ix, **env(**bad)))
        rows.append(dict(kind='reference', block=ix, ratio=1.0 + .001 * (ix % 3), flagged=False))
        c = dict(n_tau=10, k=5, kernel_n=10, prediction_sha256='a')
        a = dict(n_tau=900, k=300, kernel_n=900, prediction_sha256='b')
        rows.append(dict(kind='counts', image=im, block=ix, counts=dict(clean=c, adv=a, advcap=dict(n_tau=900, k=300, kernel_n=300))))
        base = 1e9 * (1 + .05 * ix)
        for rep in range(6):
            wob = 1 + .002 * ((rep + ix) % 3 - 1)
            for arm, f in (('clean_total_A', 1.0), ('clean_total_B', 1.0), ('adv_total', adv),
                           ('advcap_total', adv * cap), ('clean_forward', .8), ('adv_forward', .8)):
                rows.append(dict(kind='timing', image=im, block=ix, arm=arm, rep=rep, position=0, ns=int(base * f * wob)))
    rows += [dict(kind='pin_end', passed=True), dict(kind='done', environment_end=env())]
    (d / 'raw.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    (d / 'manifest.json').write_text(json.dumps(dict(profile='PI4', smoke=False, tag='t', lock_sha256='x',
                                                     environment_start=env())))
    return d


def test_pipeline_recovers_known_ratios_and_passes_gates(tmp_path):
    s = analyze.pipeline(synthetic(tmp_path), LOCK)
    assert s['n_images'] == 20 and s['quality_pass']
    assert s['h1_adv_over_clean']['geomean_ratio'] == pytest.approx(3.0, rel=5e-3)
    assert s['h2_advcap_over_adv']['geomean_ratio'] == pytest.approx(0.5, rel=5e-3)
    assert abs(s['aa_cleanA_over_cleanB']['mean']) <= LOCK['gates']['aa_abs_log']
    assert s['h1_adv_over_clean']['p_sign_flip'] == pytest.approx(2 / 2 ** 20)
    assert len(s['holm_h1_h2']) == 2 and s['count_medians']['adv']['k'] == 300
    assert math.isfinite(s['mde_ratio_80pct'])


@pytest.mark.parametrize('bad', [dict(clock=1_200_000_000), dict(governor='ondemand'), dict(swap=926000)])
def test_gate_fails_when_registered_condition_is_broken(tmp_path, bad):
    s = analyze.pipeline(synthetic(tmp_path, **bad), LOCK)
    assert not s['quality_pass']
    assert s['h1_adv_over_clean']['geomean_ratio'] == pytest.approx(3.0, rel=5e-3)   # estimate kept, not hidden


def test_incomplete_session_is_not_a_pass(tmp_path):
    s = analyze.pipeline(synthetic(tmp_path, n=7), LOCK)
    assert s['n_images'] == 7 and not s['gates']['images_complete'] and not s['quality_pass']
