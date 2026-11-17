"""Entirely synthetic rows: no device, true operator clock or measured result."""
import ast
import copy
import importlib.util
import itertools
import math
from pathlib import Path
import sys
from statistics import median,stdev

import numpy as np
import pytest
from scipy.stats import t

S=Path(__file__).parents[1]/'studies/pi3b_nms_predecessor_analysis_20261115'
spec=importlib.util.spec_from_file_location('_pi_predecessor_analysis',S/'__init__.py',submodule_search_locations=[str(S)])
package=importlib.util.module_from_spec(spec);sys.modules[spec.name]=package;spec.loader.exec_module(package)
from _pi_predecessor_analysis import analyze as a,statistics as stats


def synthetic_rows(phase='full',duration=None):
    ids=a.SMOKE_IDS if phase=='smoke' else a.IMAGE_IDS
    rows=[];clock=1000
    for cell in a.schedule(ids):
        ns=duration(cell) if duration else (0 if cell['target']=='sham' else 100)
        value=dict(wall_start_ns=clock,wall_end_ns=clock+ns,wall_ns=ns,
            counter_status='NOT_RECORDED',before=None,after=None,increments=None,
            output_retained_through_all_endpoints=True,procfs_or_cgroup_reads=False,interval=a.INTERVAL)
        if cell['observer']=='instrumented':
            def sample(x):return dict(pid=123,calling_tid=124,process_cpu_ns=x,calling_thread_cpu_ns=x,
                process={k:x for k in a.records.FIELDS},calling_thread={k:x for k in a.records.FIELDS})
            value.update(counter_status='RECORDED',before=sample(10),after=sample(12))
            value['increments']=a.records.increments(value['before'],value['after'])
        rows.append(dict(trial=cell,measurement=value));clock+=ns+10
    return rows


def test_schedule_and_counter_validator_copies_ast_equal():
    original=S.parent/'pi3b_nms_predecessor_20261115'
    assert ast.dump(ast.parse((S/'schedule.py').read_text()))==ast.dump(ast.parse((original/'schedule.py').read_text()))
    full=ast.parse((original/'bracket.py').read_text());subset=ast.parse((S/'records.py').read_text())
    for name in ('nonnegative_integer','validate','increments'):
        find=lambda tree:next(x for x in tree.body if getattr(x,'name',None)==name)
        assert ast.dump(find(full))==ast.dump(find(subset))


def test_complete_full_all18_controls_and_image_unit_inference():
    def ns(c):return 0 if c['target']=='sham' else (50 if c['predecessor']=='candidate16M' else 100)
    result=a.summarize(synthetic_rows(duration=ns),'full','SYNTHETIC_ONLY.jsonl')
    assert result['audit']['actual_trials']==3600 and result['numerical_controls_pass']
    assert result['control_counts']==dict(AA=12,instrumentation=6)
    primary=result['primary']['statistics']
    assert primary['n_images']==20 and primary['geomean_ratio']==pytest.approx(.5)
    assert primary['ratio_ci95']==pytest.approx([.5,.5])
    assert primary['exact_sign_patterns']==2**20 and primary['p_sign_flip']==2/2**20
    assert primary['dz'] is None and primary['mde_log_80pct']==0
    assert not result['campaign_quality_assessed'] and not result['confirmatory_interpretation_authorized']
    assert not primary['confirmatory_interpretation_authorized']
    assert len(result['counter_rows'])==1800 and any(x['process_cpu_over_wall'] is None for x in result['counter_rows'])
    assert not result['sham_time_subtracted']


def test_smoke_master_indices_mapping_no_efficacy_ci_or_gate_pass():
    rows=synthetic_rows('smoke');result=a.summarize(rows,'smoke','SYNTHETIC_ONLY.jsonl')
    assert result['audit']['expected_trials']==360 and {r['trial']['master_index'] for r in rows}=={0,2}
    assert result['status']=='TECHNICAL_SMOKE_DESCRIPTIVE_ONLY' and result['numerical_controls_pass'] is None
    assert result['primary']['statistics'] is None and len(result['primary']['per_image'])==2
    for cell in result['cell_medians']:
        times=[rows[line-1]['measurement']['wall_ns'] for line in cell['lines']]
        assert len(times)==5 and cell['median_ns']==median(times)
    for row in result['counter_rows']:
        assert row['increments']==rows[row['line']-1]['measurement']['increments']
        assert row['source']==f"SYNTHETIC_ONLY.jsonl:{row['line']}:measurement"


@pytest.mark.parametrize('change',['partial','extra','reordered','duplicate','renumber','bool_index','unknown_field',
    'zero_nonsham','negative','nan','wall_arithmetic','overlap','missing_sample','false_delta','identity','counters_in_control','bool_delta'])
def test_corrupt_or_partial_raw_never_yields_inference(change):
    rows=synthetic_rows('smoke')
    ix=next(i for i,r in enumerate(rows) if r['trial']['observer']=='instrumented' and r['trial']['target']!='sham')
    m=rows[ix]['measurement']
    if change=='partial':rows.pop()
    elif change=='extra':rows.append(copy.deepcopy(rows[-1]))
    elif change=='reordered':rows[0],rows[1]=rows[1],rows[0]
    elif change=='duplicate':rows[1]=copy.deepcopy(rows[0])
    elif change=='renumber':rows[0]['trial']['index']=99
    elif change=='bool_index':rows[0]['trial']['index']=False
    elif change=='unknown_field':rows[0]['debug_extra']=True
    elif change=='zero_nonsham':m['wall_ns']=0;m['wall_end_ns']=m['wall_start_ns']
    elif change=='negative':m['wall_ns']=-1
    elif change=='nan':m['wall_ns']=float('nan')
    elif change=='wall_arithmetic':m['wall_ns']+=1
    elif change=='overlap':rows[-1]['measurement']['wall_start_ns']=0;rows[-1]['measurement']['wall_end_ns']=rows[-1]['measurement']['wall_ns']
    elif change=='missing_sample':m['before']=None
    elif change=='false_delta':m['increments']['process']['ru_majflt']=0
    elif change=='bool_delta':m['increments']['observer_work_included']=1
    elif change=='identity':m['before']['pid']=m['after']['pid']=987
    elif change=='counters_in_control':
        next(r for r in rows if r['trial']['observer']=='uninstrumented')['measurement']['increments']=0
    result=a.summarize(rows,'smoke','SYNTHETIC_ONLY.jsonl')
    assert not result['audit']['numerical_schema_pass'] and result['audit']['errors']
    assert result['primary'] is None and result['numerical_controls_pass'] is None
    assert not result['confirmatory_interpretation_authorized'] and 'controls' not in result


def test_pooled10_uses_raw_observations_not_average_of_cell_medians():
    seq={'A':[1000,2000,3000,4000,100000],'B':[5000,6000,7000,8000,9000]}
    def duration(c):
        if c['target']=='wrapper' and c['observer']=='uninstrumented':
            if c['predecessor']=='native32M':return seq[c['copy']][c['rep']]
            if c['predecessor']=='candidate16M':return 11000
        return 1 if c['target']=='sham' else 100
    result=a.summarize(synthetic_rows('smoke',duration),'smoke','SYNTHETIC_ONLY.jsonl')
    for image in result['primary']['per_image']:
        assert image['denominator_median_ns']==5500 and image['ratio']==2
        assert len(image['numerator_lines'])==len(image['denominator_lines'])==10


def test_aa_mean_near_zero_does_not_rescue_failed_mde():
    def duration(c):
        if (c['predecessor'],c['target'],c['observer'],c['copy'])==('native32M','wrapper','uninstrumented','A'):
            return round(100000*math.exp(.2 if c['master_index']<10 else -.2))
        return 1 if c['target']=='sham' else 100000
    result=a.summarize(synthetic_rows(duration=duration),'full','SYNTHETIC_ONLY.jsonl')
    control=next(x for x in result['controls'] if x['kind']=='AA' and (x['predecessor'],x['target'],x['observer'])==('native32M','wrapper','uninstrumented'))
    assert control['abs_mean_log_pass'] and not control['mde_log_pass']
    assert not result['numerical_controls_pass'] and result['primary']['statistics'] is not None
    assert not result['confirmatory_interpretation_authorized']  # Complete rejected data remain diagnostic.


def test_one_instrumentation_bias_cannot_borrow_other_passing_controls():
    def duration(c):
        if (c['predecessor'],c['target'],c['observer'])==('nms_reference','kernel_call','instrumented'):return 125
        return 1 if c['target']=='sham' else 100
    result=a.summarize(synthetic_rows(duration=duration),'full','SYNTHETIC_ONLY.jsonl')
    failed=[x for x in result['controls'] if not x['numerical_gate_pass']]
    assert len(failed)==1 and failed[0]['kind']=='instrumentation'
    assert not result['numerical_controls_pass']


@pytest.mark.parametrize('logs',[[0.,0.],[.1,-.1],[.2,.4,.8],[-.3,0.,.7,.9],[1e-14,-1e-14]])
def test_exact_sign_flip_against_independent_brute_force(logs):
    observed=abs(sum(logs)/len(logs));hits=0
    for signs in itertools.product((-1,1),repeat=len(logs)):
        hits+=abs(sum(s*x for s,x in zip(signs,logs))/len(logs))>=observed-1e-12
    assert stats.exact_sign_flip(logs)['p_sign_flip']==hits/2**len(logs)


def test_bootstrap_mde_dz_against_independent_fixed_seed_calculation():
    logs=[math.log((80+i)/(100+i)) for i in range(20)]
    result=stats.primary(logs)
    rng=np.random.default_rng(2026111501)
    means=[sum(logs[i] for i in rng.integers(0,20,20))/20 for _ in range(20000)]
    ci=np.exp(np.percentile(means,[2.5,97.5]))
    assert result['ratio_ci95']==pytest.approx(ci,rel=1e-13)
    assert result['mde_log_80pct']==pytest.approx((t.ppf(.975,19)+t.ppf(.8,19))*stdev(logs)/math.sqrt(20))
    assert result['dz']==pytest.approx((sum(logs)/20)/stdev(logs))


def test_full20_sign_flip_matches_binomial_tail_without_pattern_replay():
    logs=[1.]*15+[-1.]*5
    hits=2*sum(math.comb(20,k) for k in range(6))
    result=stats.exact_sign_flip(logs)
    assert result['exact_sign_patterns']==2**20
    assert result['exact_extreme_patterns']==hits and result['p_sign_flip']==hits/2**20


def test_process_cpu_over_wall_above_one_preserved_without_attribution():
    rows=synthetic_rows('smoke')
    row=next(r for r in rows if r['trial']['observer']=='instrumented' and r['trial']['target']!='sham')
    m=row['measurement'];m['after']['process_cpu_ns']=m['before']['process_cpu_ns']+2*m['wall_ns']
    m['increments']=a.records.increments(m['before'],m['after'])
    result=a.summarize(rows,'smoke','SYNTHETIC_ONLY.jsonl')
    saved=next(x for x in result['counter_rows'] if x['trial']==row['trial'])
    assert saved['process_cpu_over_wall']==2 and not saved['unique_nms_wait_cause_identified']
