"""Post-data independent arithmetic audit; not a new estimator or measurement.

Rebuilds registered image medians, bootstrap and exhaustive sign-flip counts.
Never changes raw, locked study source, configuration or the original summary.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import t


def main():
    root = Path(__file__).resolve().parents[1]
    campaign = root/'runs/full_01'
    raw = campaign/'pipeline_PI4/raw.jsonl'
    rows = [json.loads(line) for line in raw.read_bytes().splitlines()]
    summary_path = campaign/'summary.json'
    summary = json.loads(summary_path.read_bytes())['pipeline_PI4']
    group = {}
    for row in rows:
        if row['kind'] == 'timing':
            group.setdefault(row['image'], {}).setdefault(row['arm'], []).append(row['ns'])
    images = sorted(group)
    assert len(images) == 20
    columns = {arm: np.array([np.median(group[im][arm]) for im in images])
               for arm in group[images[0]]}
    clean = np.array([np.median(group[im]['clean_total_A']+group[im]['clean_total_B']) for im in images])
    definitions = [
        ('h1_adv_over_clean', columns['adv_total'], clean, 20261115),
        ('h2_advcap_over_adv', columns['advcap_total'], columns['adv_total'], 20261116),
        ('aa_cleanA_over_cleanB', columns['clean_total_A'], columns['clean_total_B'], 20261117),
        ('advcap_over_clean', columns['advcap_total'], clean, 20261118),
        ('forward_adv_over_clean', columns['adv_forward'], columns['clean_forward'], 20261119),
    ]
    checks = {}
    logs_by_endpoint = {}
    for name, numerator, denominator, seed in definitions:
        # math.log preserves the original scalar operation before array reduction.
        logs = np.array([math.log(a/b) for a,b in zip(numerator,denominator)])
        logs_by_endpoint[name] = logs
        draws = np.random.default_rng(seed).integers(0,20,(20000,20))
        a = (1-.95)/2
        ci = np.quantile(logs[draws].mean(axis=1),[a,1-a])
        mean = float(logs.mean()); sd = float(logs.std(ddof=1)); hits = 0
        for start in range(0,2**20,8192):
            indices = np.arange(start,start+8192,dtype=np.uint64)
            signs = (((indices[:,None] >> np.arange(20,dtype=np.uint64)) & 1).astype(np.int8)*2-1)
            means = (signs*logs).mean(axis=1)
            hits += int(np.count_nonzero(np.abs(means) >= abs(mean)-1e-12))
        values = dict(mean=mean,sd=sd,ci95=ci.tolist(),p_sign_flip=hits/2**20,
                      geomean_ratio=math.exp(mean),ratio_ci95=[math.exp(v) for v in ci])
        for key,value in values.items():
            assert np.allclose(value,summary[name][key],rtol=0,atol=1e-14),(name,key)
        checks[name] = dict(values_match=True,exact_sign_flip_hits=hits,assignments=2**20)
    aa = logs_by_endpoint['aa_cleanA_over_cleanB']
    mde = float((t.ppf(.975,19)+t.ppf(.8,19))*aa.std(ddof=1)/np.sqrt(20))
    assert abs(mde-summary['mde_log_80pct']) < 1e-14
    medians = dict(clean_total=float(np.median(clean))/1e6,
                   **{name:float(np.median(columns[name]))/1e6
                      for name in ('adv_total','advcap_total','clean_forward','adv_forward')})
    assert medians == summary['median_ms_across_images']
    shares = dict(clean=float(np.median(columns['clean_forward']/clean)),
                  adv=float(np.median(columns['adv_forward']/columns['adv_total'])))
    assert shares == summary['forward_share']
    reference = json.loads((root/'laptop_reference_counts.json').read_bytes())['counts']
    counts = {r['image']:r['counts'] for r in rows if r['kind']=='counts'}
    assert all(counts[im][arm][key] == reference[im][arm][key]
               for im in images for arm in ('clean','adv') for key in ('n_tau','k'))
    assert all(counts[im]['advcap']['k'] == reference[im]['advcap']['k'] for im in images)
    assert summary['quality_pass'] is False and summary['gates']['swap_off'] is False
    result = dict(status='REGISTERED_SUMMARY_RECOMPUTED_FROM_ALL20_IMAGES',
                  raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                  summary_sha256=hashlib.sha256(summary_path.read_bytes()).hexdigest(),
                  verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  endpoint_checks=checks,mde_matches=True,medians_and_shares_match=True,
                  registered_quality_pass=False,diagnostic_only=True,
                  drop_image_or_filter_applied=False)
    with (Path(__file__).parent/'independent_summary_check.json').open('x',encoding='utf-8',newline='\n') as f:
        json.dump(result,f,indent=2)
    print(result['status'], 'quality remains FAIL; no data filtered')


if __name__ == '__main__':
    main()
