"""Post-hoc audit of saved raw only. Never imports torch or runs inference."""
import argparse
import hashlib
import importlib.util
import json
import statistics
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]
REPO = SIM.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path, selector):
    return dict(path=path.relative_to(REPO).as_posix(), sha256=sha(path), selector=selector)


def audit():
    spec = importlib.util.spec_from_file_location('m4_analysis_readonly', SIM/'studies/m4_nms_dispatch/analyze.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    root = SIM/'results/stability_20261106/stability_full_20261106'
    saved = json.loads((root/'confirmation_summary.json').read_text())
    sessions = []
    for ix in (1, 2, 3):
        run = root/f'session{ix}'
        rows = [json.loads(s) for s in (run/'raw.jsonl').read_text().splitlines()]
        result = mod.analyze(run)  # pure read; does NOT invoke its writing CLI
        refs = []
        for line, row in enumerate(rows, 1):
            if row['kind'] != 'reference':
                continue
            ns = row['samples_ns']
            med = statistics.median(ns)
            baseline = med if not refs else refs[0]['median_ms']*1e6
            ratio = med/baseline
            assert abs(ratio-row['ratio']) < 1e-12
            assert (abs(ratio-1) > .03) == row['flagged']
            refs.append(dict(line=line, block=row['block'], median_ms=med/1e6,
                             ratio=ratio, flagged=row['flagged'], samples=len(ns),
                             first5_ms=statistics.median(ns[:5])/1e6,
                             last5_ms=statistics.median(ns[-5:])/1e6))
        flags = sum(r['flagged'] for r in refs)
        mde = {arm: result['mde'][arm]['mde_frac'] for arm in ('clean', 'attacked')}
        gate = result['complete'] and len(refs) == 22 and flags <= 2 and all(
            v is not None and v <= .01 for v in mde.values())
        old = saved['all_sessions'][ix-1]
        assert flags == len(old['flagged_references'])
        assert gate == old['quality_pass']
        assert result['raw_sha256'] == old['raw_sha256']
        assert mde == {arm: old['mde'][arm]['mde_frac'] for arm in mde}
        timing = [r for r in rows if r['kind'] == 'timing']
        counts = [r for r in rows if r['kind'] == 'counts']
        nms = {}
        for arm in ('clean', 'attacked'):
            vals = [r['ns']/1e6 for r in timing if r['arm'] == arm and r['stage'] == 'nms_tv']
            ns_counts = [r['n_tau'] for r in counts if r['arm'] == arm]
            nms[arm] = dict(min_ms=min(vals), median_ms=statistics.median(vals), max_ms=max(vals),
                            n_tau_min=min(ns_counts), n_tau_max=max(ns_counts))
        sessions.append(dict(session=ix, sources=[source(run/'raw.jsonl', 'kind=reference|timing|counts'),
                                                   source(run/'manifest.json', '$')],
                             complete=result['complete'], references=refs, flags=flags,
                             above_baseline=sum(r['ratio'] > 1.03 for r in refs),
                             below_baseline=sum(r['ratio'] < .97 for r in refs),
                             reference_ratio_range=[min(r['ratio'] for r in refs), max(r['ratio'] for r in refs)],
                             aa_mde_fraction=mde, quality_pass=gate, fixed_tv_nms_descriptive=nms))
    pin = SIM/'results/phone_a36/pin_20261101/pin_verify.json'
    p = json.loads(pin.read_text())
    return dict(status='POSTHOC_OFFLINE_ONLY_NO_NEW_MEASUREMENTS',
                audit_source=source(Path(__file__), '$'),
                analysis_source=source(SIM/'studies/m4_nms_dispatch/analyze.py', 'analyze'),
                sessions=sessions, all_sessions_pass=all(s['quality_pass'] for s in sessions),
                historical_phone=dict(source=source(pin, '$.verify; $.profiles_passed; $.pin_mechanism'),
                                      verify=p['verify'], profiles_passed=p['profiles_passed']),
                limits=['Reference levels are descriptive; saved telemetry does not identify physical cause.',
                        'Historical phone summary lacks per-TID masks/states/tick deltas; cannot recompute active-only residency.',
                        'NMS min/max span images and repetitions, NOT identical candidate sets or kernel-only measurements.',
                        'Existing FAIL decisions are unchanged; counts do not establish latency or DoS.'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    result = audit()
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps([dict(session=s['session'], flags=s['flags'], above=s['above_baseline'],
                           below=s['below_baseline'], ratio_range=s['reference_ratio_range'],
                           mde=s['aa_mde_fraction'], passed=s['quality_pass']) for s in result['sessions']], indent=2))
