"""PI3B-PI1-SSD contracts on synthetic rows: no model, no device, no timing.
Focus: the ssd_idle gate for the declared idle-USB-SSD condition."""
import importlib.util
import json
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parents[1] / 'studies' / 'pi3b_pi1_ssd_600mhz_20261115'


def load(name):
    spec = importlib.util.spec_from_file_location(f'pi1ssd_{name}', STUDY / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


analyze = load('analyze')
LOCK = json.loads((STUDY / 'lock.json').read_text())
N = 12   # fewer images keeps the exact sign-flip (2**N) fast; gate logic is n-independent


def test_lock_declares_ssd_condition():
    assert LOCK['allow_usb_storage'] is True
    assert LOCK['profiles']['PI1'] == {'cpus': [3]}
    by = {r['name']: r['sha256'] for r in LOCK['files']}
    assert 'campaign_pi1.sh' in by and 'run.py' in by


def env(written=1000, clock=600_000_000, governor='powersave', swap=0, temp=40.0):
    return dict(governor=governor, scaling_cur_khz=600000, arm_clock_hz=f'frequency(48)={clock}',
                temp=f"temp={temp}'C", throttled='throttled=0x50005',
                mem_kb=dict(MemTotal=927000, MemAvailable=600000, SwapTotal=swap, SwapFree=swap),
                vmstat={}, loadavg=[0, 0, 0],
                usb_disk={'sda': dict(reads=70, sectors_read=2247, writes=0, sectors_written=written, raw='x'),
                          'sdb': dict(reads=0, sectors_read=0, writes=0, sectors_written=0, raw='x')})


def synthetic(tmp_path, adv=3.0, cap=0.5, written_per_block=None):
    d = tmp_path / 'pipeline_PI1'
    d.mkdir()
    rows = [dict(kind='pin_start', passed=True), dict(kind='reference', block='start', ratio=1.0, flagged=False)]
    for ix in range(N):
        w = 1000 if written_per_block is None else written_per_block[ix]
        rows.append(dict(kind='environment', block=ix, **env(written=w)))
        rows.append(dict(kind='reference', block=ix, ratio=1.0 + .001 * (ix % 3), flagged=False))
        c = dict(n_tau=10, k=5, kernel_n=10, prediction_sha256='a')
        a = dict(n_tau=900, k=300, kernel_n=900, prediction_sha256='b')
        rows.append(dict(kind='counts', image=f'{ix:012d}', block=ix,
                         counts=dict(clean=c, adv=a, advcap=dict(n_tau=900, k=300, kernel_n=300))))
        base = 1e10 * (1 + .05 * ix)
        for rep in range(4):
            wob = 1 + .002 * ((rep + ix) % 3 - 1)
            for arm, f in (('clean_total_A', 1.0), ('clean_total_B', 1.0), ('adv_total', adv),
                           ('advcap_total', adv * cap), ('clean_forward', .8), ('adv_forward', .8)):
                rows.append(dict(kind='timing', image=f'{ix:012d}', block=ix, arm=arm, rep=rep, position=0, ns=int(base * f * wob)))
    rows += [dict(kind='pin_end', passed=True), dict(kind='done', environment_end=env(written=(1000 if written_per_block is None else written_per_block[-1])))]
    (d / 'raw.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    (d / 'manifest.json').write_text(json.dumps(dict(profile='PI1', smoke=False, tag='t', lock_sha256='x',
                                                     environment_start=env(written=1000))))
    return d


def test_idle_ssd_passes_and_recovers_ratio(tmp_path):
    lock = dict(LOCK); lock['full'] = dict(LOCK['full']); lock['full']['n_images'] = N
    s = analyze.pipeline(synthetic(tmp_path), lock)
    assert s['n_images'] == N
    assert s['gates']['ssd_idle'] is True
    assert s['gates']['usb_disks'] == ['sda', 'sdb']
    assert s['quality_pass']
    assert s['h1_adv_over_clean']['geomean_ratio'] == pytest.approx(3.0, rel=5e-3)


def test_ssd_write_during_run_fails_gate(tmp_path):
    lock = dict(LOCK); lock['full'] = dict(LOCK['full']); lock['full']['n_images'] = N
    writes = [1000] * N
    writes[6] = 1200   # the SSD did I/O mid-run -> not idle
    s = analyze.pipeline(synthetic(tmp_path, written_per_block=writes + [1200]), lock)
    assert s['gates']['ssd_idle'] is False
    assert not s['quality_pass']
    assert s['h1_adv_over_clean']['geomean_ratio'] == pytest.approx(3.0, rel=5e-3)  # estimate kept, not hidden
