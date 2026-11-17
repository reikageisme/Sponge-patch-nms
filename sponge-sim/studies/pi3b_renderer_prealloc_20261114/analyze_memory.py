"""Prospective memory-only audit/analysis; no model, timing, or device mutation.

Missing/partial/corrupt cohorts produce an audit, never an image-filtered CI.
Final eligibility also requires the independent campaign restore receipt.
Full statistics use unchanged copied helpers; gate-only avoids scipy on Pi.
"""
from pathlib import Path
from statistics import median
import argparse
import json
import math
from cache import sha,record,validate_manifest
from memory_campaign import schedule
from memory_worker import ARMS
from guard import violations

SEEDS={'adv':2026111401,'clean':2026111402,'aa_clean':2026111403,'aa_adv':2026111404}


def audit_rows(rows,reg,manifest,meta,terminal,guards,job_reader,registration_sha):
    errors=[];conditions=[]
    try:
        cases=validate_manifest(manifest,reg['image_ids'])
        expected=schedule(reg['image_ids'],reg['seed'])
        if [r['job'] for r in rows]!=expected:errors.append('schedule_or_incomplete_cohort')
        if terminal!={'status':'COMPLETED_PENDING_AUDIT','jobs':360,'latency_endpoint_recorded':False}:
            errors.append('terminal')
        if meta!={'tag':reg['tag'],'commit':meta.get('commit'),'lock_sha256':registration_sha,
                  'cache_manifest_sha256':reg['cache_manifest_sha256'],'parent_torch_imported':False}:
            errors.append('collector_registration')
        import re
        if not re.fullmatch('[0-9a-f]{40}',meta.get('commit','')):errors.append('commit')
        by_case={(r['image'],r['condition']):r for r in cases}
        fasts=[r['fast'] for r in guards if 'fast' in r]
        clocks=[r['actual_arm_hz'] for r in guards if 'actual_arm_hz' in r]
        if len(fasts)<4*360+1 or len(clocks)!=720:errors.append('guard_or_clock_schedule')
        if len(fasts)!=len([r for r in guards if 'violations' in r]):errors.append('guard_rows')
        baseline=fasts[0]['vmstat']
        if any(r.get('violations') for r in guards):conditions.append('logged_guard_violation')
        if any(type(c) is not int or not reg['gates']['clock_hz'][0]<=c<=reg['gates']['clock_hz'][1] for c in clocks):
            conditions.append('actual_clock')
        for fast in fasts:conditions.extend(violations(fast,reg,reg['cpus'],baseline))
        for row in rows:
            job,result=row['job'],row['result'];case=by_case[(job['image'],job['condition'])]
            receipts=job_reader(job['index'])
            if result!=receipts['memory']:errors.append('child_raw_receipt_differs')
            done=receipts['terminal']
            if (done['status']!='COMPLETED' or done['returncode']!=0 or done['direct_child_reaped'] is not True
                or done['failure'] is not None or done['termination_sent'] is not False):errors.append('child_not_normally_reaped')
            if result['pid']!=receipts['started']['pid'] or result['pid']!=done['owned_pid']:
                errors.append('child_identity')
            if (result['status']!='COMPLETED' or any(result[k]!=job[k] for k in ('image','condition','arm'))
                or result['tag']!=reg['tag'] or result['commit']!=meta['commit']
                or result['registration_sha256']!=registration_sha or result['cache_sha256']!=case['sha256']
                or result['mask_sha256']!=case['mask_sha256']):errors.append('result_identity_or_parity')
            if (type(result['ru_maxrss_kib']) is not int or result['ru_maxrss_kib']<=0
                or result['ru_maxrss_bytes']!=1024*result['ru_maxrss_kib']):errors.append('rss_type_or_units')
            if (result['sample_point']!=reg['sample_point'] or result['includes_import_validation_warmup_hash'] is not True
                or result['incremental_renderer_peak'] is not False or result['latency_endpoint_recorded'] is not False):
                errors.append('endpoint')
            if set(result['guards'])!={'start','ready','end'}:errors.append('child_guard_schedule')
            for fast in result['guards'].values():conditions.extend(violations(fast,reg,reg['cpus'],baseline))
    except (KeyError,ValueError,TypeError,IndexError,OSError,AttributeError) as e:
        errors.append(type(e).__name__+': '+str(e))
    return dict(structure_ok=not errors,conditions_ok=not conditions,errors=sorted(set(errors)),
                condition_errors=sorted(set(conditions)),n_jobs=len(rows),unit='image',n_expected_images=20)


def per_image(rows,ids):
    values={im:{c:{a:[] for a in ARMS} for c in ('clean','adv')} for im in ids}
    source_map={im:{c:{a:[] for a in ARMS} for c in ('clean','adv')} for im in ids}
    for line,row in enumerate(rows,1):
        j=row['job'];values[j['image']][j['condition']][j['arm']].append(row['result']['ru_maxrss_bytes'])
        source_map[j['image']][j['condition']][j['arm']].append(dict(raw_line=line,job_index=j['index'],rep=j['rep']))
    endpoints={c:[] for c in ('clean','adv')};aa={c:[] for c in ('clean','adv')};med={}
    for im in ids:
        med[im]={}
        for c,arms in values[im].items():
            if any(len(v)!=3 for v in arms.values()):raise ValueError('all repetitions required')
            m={a:median(v) for a,v in arms.items()};base=median(arms['baseline_A']+arms['baseline_B'])
            med[im][c]=dict(**m,pooled_baseline=base)
            endpoints[c].append(math.log(m['candidate16M']/base))
            aa[c].append(math.log(m['baseline_A']/m['baseline_B']))
    return endpoints,aa,med,source_map


def precision(logs,reg):
    import numpy as np
    sd=float(np.std(logs,ddof=1));mean=float(np.mean(logs))
    mde=float(reg['mde_t_critical_sum_n20']*sd/np.sqrt(len(logs)))
    return dict(n_images=len(logs),mean_log=mean,sd_log=sd,geomean_ratio=math.exp(mean),mde_log_80pct=mde,
                aa_ok=abs(mean)<=reg['gates']['aa_abs_log'],mde_ok=math.isfinite(mde) and mde<=reg['gates']['mde_log'])


def ratio_summary(logs,seed):
    import numpy as np
    import stats_frozen as stats
    x=np.array(logs,dtype=float);lo,hi=stats.bootstrap_ci(x,seed);sd=float(x.std(ddof=1));mean=float(x.mean())
    return dict(n_images=len(x),unit='image',mean_log=mean,sd_log=sd,geomean_ratio=math.exp(mean),
        ratio_ci95=[math.exp(lo),math.exp(hi)],p_sign_flip=stats.sign_flip_p(x),
        dz=None if sd==0 else mean/sd,dz_defined=sd!=0,bootstrap_seed=seed,n_boot=20000,
        min_exact_two_sided_p=2/2**20)


def _analyze(campaign,registration_path,cache_dir,gate_only=False):
    campaign=Path(campaign);data=campaign/'memory';registration_path=Path(registration_path)
    reg=json.loads(registration_path.read_text(encoding='utf-8'))
    manifest_path=Path(cache_dir)/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    meta=json.loads((data/'registration.json').read_text(encoding='utf-8'))
    from memory_worker import registration
    registration(registration_path,reg['tag'],meta['commit'])
    rows=[json.loads(s) for s in (data/'raw.jsonl').read_text(encoding='utf-8').splitlines()]
    guards=[json.loads(s) for s in (data/'guards.jsonl').read_text(encoding='utf-8').splitlines()]
    terminal=json.loads((data/'terminal.json').read_text(encoding='utf-8'))
    def job_reader(i):
        root=data/'jobs'/f'{i:04d}'
        return {name:json.loads((root/(name+'.json')).read_text(encoding='utf-8')) for name in ('memory','terminal','started')}
    audit=audit_rows(rows,reg,manifest,meta,terminal,guards,job_reader,sha(registration_path))
    if not audit['structure_ok']:
        return dict(audit=audit,session_gate_pass=False,quality_pass=False,gate_only=gate_only)
    if sha(manifest_path)!=reg['cache_manifest_sha256']:
        audit['structure_ok']=False;audit['errors'].append('cache_manifest_hash')
    for row in manifest['cases']:
        if sha(Path(cache_dir)/row['filename'])!=row['sha256']:
            audit['structure_ok']=False;audit['errors'].append('cache_file_hash')
    out=dict(audit=audit,session_gate_pass=False,quality_pass=False,gate_only=gate_only,
        interpretation='Whole-process high-water RSS through output digest; not isolated renderer peak, not latency.',
        counter_resolution_bytes=1024)
    if not audit['structure_ok']:return out
    endpoints,aa,med,source=per_image(rows,reg['image_ids'])
    out.update(per_image_median_bytes=med,raw_source_map=source,
        aa_controls={c:precision(aa[c],reg) for c in ('clean','adv')})
    out['session_gate_pass']=audit['conditions_ok'] and all(v['aa_ok'] and v['mde_ok'] for v in out['aa_controls'].values())
    if gate_only:
        out['restore_pending']=True;return out
    restore=json.loads((campaign/'restore.json').read_text(encoding='utf-8')) if (campaign/'restore.json').exists() else {}
    out['restore_ok']=isinstance(restore,dict) and restore.get('status')=='RESTORED' and restore.get('errors')==[]
    controller_path=campaign/'campaign_terminal.json'
    controller=json.loads(controller_path.read_text(encoding='utf-8')) if controller_path.exists() else {}
    out['controller_terminal_ok']=controller==dict(status='COMPLETED',gate_returncode=0)
    out['quality_pass']=out['session_gate_pass'] and out['restore_ok'] and out['controller_terminal_ok']
    out['primary_adv_candidate_over_baseline']=ratio_summary(endpoints['adv'],SEEDS['adv'])
    out['secondary_clean_candidate_over_baseline']=ratio_summary(endpoints['clean'],SEEDS['clean'])
    out['aa_intervals']={c:ratio_summary(aa[c],SEEDS['aa_'+c]) for c in ('clean','adv')}
    out['zero_variance_note']='Zero observed SD gives MDE0 and undefined d_z(null); finite KiB resolution/startup floor may conceal differences. Not equivalence.'
    return out


def analyze(campaign,registration_path,cache_dir,gate_only=False):
    try:return _analyze(campaign,registration_path,cache_dir,gate_only)
    except (OSError,ValueError,KeyError,TypeError,IndexError,AttributeError) as exc:
        return dict(audit=dict(structure_ok=False,conditions_ok=False,errors=[type(exc).__name__+': '+str(exc)]),
                    session_gate_pass=False,quality_pass=False,gate_only=gate_only)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('campaign',type=Path);p.add_argument('--registration',required=True,type=Path)
    p.add_argument('--cache',required=True,type=Path);p.add_argument('--gate-only',action='store_true');args=p.parse_args()
    result=analyze(args.campaign,args.registration,args.cache,args.gate_only)
    record(args.campaign/('gates.json' if args.gate_only else 'summary.json'),result)
    print(json.dumps({k:result[k] for k in ('audit','session_gate_pass','quality_pass')}))
    raise SystemExit(0 if (result['session_gate_pass'] if args.gate_only else result['quality_pass']) else 66)
