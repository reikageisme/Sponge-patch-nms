"""Independent stdlib replay of smoke medians/control numbers; no efficacy test."""
from pathlib import Path
from statistics import median,mean,stdev
from fractions import Fraction
import hashlib
import json
import math

B=Path(__file__).resolve().parent
P=B/'runs/memory_smoke_01';R=P/'original'
SOURCE=B.parents[1]/'studies/pi3b_renderer_memory_usb_20261115'


def main():
    rows=[json.loads(x) for x in (R/'memory/raw.jsonl').read_text().splitlines()]
    summary=json.loads((P/'summary.json').read_text());reg=json.loads((SOURCE/'memory_registration.json').read_text())
    manifest=json.loads((SOURCE/'cache_manifest.json').read_text())
    cases={(r['image'],r['condition']):r for r in manifest['cases']}
    assert len(rows)==36 and summary['technical_smoke_pass'] is True and summary['quality_pass'] is False
    output=[];aa={'clean':[],'adv':[]}
    for image in reg['phases']['smoke']['image_ids']:
        for condition in ('clean','adv'):
            groups={arm:[] for arm in reg['arms']};lines={arm:[] for arm in reg['arms']}
            for line,row in enumerate(rows,1):
                j,x=row['job'],row['result']
                if j['image']==image and j['condition']==condition:
                    assert x['ru_maxrss_bytes']==1024*x['ru_maxrss_kib']
                    assert x['mask_sha256']==cases[(image,condition)]['mask_sha256']
                    groups[j['arm']].append(x['ru_maxrss_bytes']);lines[j['arm']].append(line)
            assert all(len(v)==3 for v in groups.values())
            m={arm:median(v) for arm,v in groups.items()}
            pooled=median(groups['baseline_A']+groups['baseline_B'])
            expected=summary['per_image_median_bytes'][image][condition]
            assert dict(**m,pooled_baseline=pooled)==expected
            aa[condition].append(math.log(m['baseline_A']/m['baseline_B']))
            def kib(value):
                assert int(value)==value
                f=Fraction(int(value),1024)
                return str(f.numerator) if f.denominator==1 else str(float(f))
            output.append(dict(image=image,condition=condition,k=cases[(image,condition)]['k'],
                pooled_baseline_bytes=pooled,candidate_bytes=m['candidate16M'],
                pooled_baseline_kib_exact=kib(pooled),candidate_kib_exact=kib(m['candidate16M']),raw_lines=lines))
    controls={}
    for c,values in aa.items():
        result=dict(mean_log=mean(values),sd_log=stdev(values),mde_log_80pct=reg['mde_t_critical_sums']['2']*stdev(values)/math.sqrt(2))
        for key,v in result.items():assert math.isclose(v,summary['aa_controls'][c][key],rel_tol=1e-12,abs_tol=1e-15)
        controls[c]=result
    result=dict(status='STDLIB_SMOKE_MEDIANS_AA_UNITS_AND_MASK_HASHES_REPLAYED',n_rows=36,unit='image',n_images=2,
        raw_sha256=hashlib.sha256((R/'memory/raw.jsonl').read_bytes()).hexdigest(),
        table=output,aa_independent=controls,no_efficacy_inference=True)
    with (B/'independent_smoke_audit.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))


if __name__=='__main__':main()
