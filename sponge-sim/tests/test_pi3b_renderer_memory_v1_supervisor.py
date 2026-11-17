# Adapted from sponge-sim/tests/test_pi3b_renderer_supervisor_analysis.py:1-238
# SHA256 20a048a79d2434348adfb3a458aaf9f7671226fcd29a4e8f385b359b9c8d5bb1; new namespace/phase schema only, earlier tests untouched.
# FakeSystem copied from sponge-sim/tests/test_pi3b_swapguard_v2.py:52-80
# Source SHA256 245be368df4250375df5980292de2cb4a8c788f87188a2f522366076f7910715; synthetic only, no hardware calls.
import ast
import copy
import json
import math
from pathlib import Path
import sys
import pytest
STUDY=Path(__file__).parents[1]/"studies/pi3b_renderer_memory_v1_20261114"
sys.path.insert(0,str(STUDY))
import control
import guard
import analyze_memory as analysis
import memory_worker
from memory_campaign import schedule

class FakeSystem:
    def __init__(self,swap=True,timer=True,fail=None):
        self.rows=[dict(name='/dev/zram0',kind='partition',size_kb=926716,used_kb=16,priority=100)] if swap else []
        self.original=dict(governor='ondemand',swaps=copy.deepcopy(self.rows),mem_available_kb=200000,
                           setup=dict(ActiveState='active' if swap else 'inactive',Result='success'),
                           units={u:dict(ActiveState='inactive',LoadState='loaded',FragmentPath='/usr/lib/'+u) for u in guard.UNITS})
        self.original['units']['dev-zram0.swap'].update(ActiveState='active' if swap else 'inactive',FragmentPath='/run/systemd/generator/dev-zram0.swap')
        self.original['units']['rpi-zram-writeback.timer']['ActiveState']='active' if timer else 'inactive'
        self.now=dict(governor='ondemand',swaps=copy.deepcopy(self.rows),masks={u:False for u in guard.UNITS},
                      setup=copy.deepcopy(self.original['setup']),
                      active={u:v['ActiveState'] for u,v in self.original['units'].items()})
        self.calls=[];self.fail=fail

    def snapshot(self):return copy.deepcopy(self.original)
    def current(self):return copy.deepcopy(self.now)
    def governor(self,value):self.now['governor']=value
    def ctl(self,*argv):
        self.calls.append(argv)
        if len(self.calls)==self.fail:raise RuntimeError('injected systemctl failure')
        action,unit=argv[0],argv[-1]
        if action in ('mask','unmask'):
            for u in argv[1:]:
                if not u.startswith('-'):self.now['masks'][u]=action=='mask'
        elif action in ('start','stop'):
            self.now['active'][unit]='active' if action=='start' else 'inactive'
            if unit=='dev-zram0.swap':
                if action=='stop' and self.now['masks'][unit]:raise RuntimeError('masked active swap loses What metadata')
                self.now['swaps']=copy.deepcopy(self.rows) if action=='start' else []
                self.now['setup']['ActiveState']='active' if action=='start' else 'inactive'


def test_lease_and_guard_ast_match_previously_qualified_full20_source():
    old=STUDY.parent/'pi3b_full20_20261114'
    a=ast.parse((old/'control.py').read_text(encoding='utf-8'));b=ast.parse((STUDY/'control.py').read_text(encoding='utf-8'))
    for name in ('record','validate_snapshot','System','Lease'):
        get=lambda tree:next(n for n in tree.body if getattr(n,'name',None)==name)
        assert ast.dump(get(a))==ast.dump(get(b))
    assert ast.dump(ast.parse((old/'guard.py').read_text()))==ast.dump(ast.parse((STUDY/'guard.py').read_text()))


@pytest.mark.parametrize('swap',[True,False])
@pytest.mark.parametrize('timer',[True,False])
def test_new_supervisor_lease_exact_restore_and_no_repeat(tmp_path,swap,timer):
    s=FakeSystem(swap,timer);lease=control.Lease(tmp_path,s);lease.apply()
    assert all(s.now['masks'].values()) and not s.now['swaps']
    receipt=lease.restore();assert receipt['status']=='RESTORED'
    calls=list(s.calls);assert lease.restore()==receipt and s.calls==calls
    assert s.now['governor']=='ondemand' and s.now['swaps']==s.original['swaps']


@pytest.mark.parametrize('at',[1,2,3])
def test_partial_mutation_failure_restore(tmp_path,at):
    s=FakeSystem(fail=at);lease=control.Lease(tmp_path,s)
    with pytest.raises(RuntimeError):lease.apply()
    s.fail=None
    assert control.Lease(tmp_path,s).restore()['status']=='RESTORED'
    assert not any(s.now['masks'].values()) and s.now['swaps']==s.original['swaps']


def test_restore_failure_never_retried_to_pass(tmp_path):
    s=FakeSystem();lease=control.Lease(tmp_path,s);lease.apply();s.fail=len(s.calls)+1
    receipt=lease.restore();assert receipt['status']=='RESTORE_FAILED'
    s.fail=None;assert lease.restore()==receipt


def test_unprepared_payload_modes_cannot_mutate(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv('INVOCATION_ID','synthetic')
    monkeypatch.setattr(control,'locked_materials',lambda *_:pytest.fail('reject before any context/config work'))
    with pytest.raises(ValueError):control.payload(SimpleNamespace(mode='smoke'))


def state():
    return dict(governor='powersave',scaling_cur_khz=600000,temp_c=40.,affinity=[0,1,2,3],mem_kb=dict(MemAvailable=200000,SwapTotal=0),
                swaps=[],usb=[],masks={u:True for u in guard.UNITS},vmstat=dict(pswpin=0,pswpout=0,oom_kill=0))


def synthetic(phase='full'):
    reg=dict(image_ids=memory_worker.IMAGE_IDS,seed=20261114,tag='prereg-pi3b-renderer-memory-fixture',cpus=[0,1,2,3],
             governor='powersave',cache_manifest_sha256='a'*64,sample_point='after_render_and_output_digest',
             phases=copy.deepcopy(memory_worker.PHASES),mde_t_critical_sums={'2':14.082586656645868,'20':2.9539746046772377},
             gates=dict(clock_hz=[594000000,606000000],abort_temp_c=75,abort_mem_available_kb=40000,aa_abs_log=.02,mde_log=.05))
    manifest=dict(status='COMPLETED_FUNCTIONAL_PARITY_ONLY',empirical_endpoint_recorded=False,cases=[
        dict(image=im,condition=c,filename=f'{im}_{c}.pt',sha256='b'*64,mask_sha256='c'*64,k=3,shape=[640,640])
        for im in reg['image_ids'] for c in ('clean','adv')])
    meta=dict(tag=reg['tag'],commit='d'*40,lock_sha256='e'*64,cache_manifest_sha256='a'*64,parent_torch_imported=False,phase=phase)
    rows=[];receipts={}
    jobs=schedule(reg['phases'][phase]['image_ids'],reg['seed'])
    for j in jobs:
        pid=1000+j['index'];base=300000+1000*reg['image_ids'].index(j['image'])
        peak=int(base*(.8 if j['arm']=='candidate16M' and j['condition']=='adv' else 1.0))
        r=dict(status='COMPLETED',phase=phase,pid=pid,image=j['image'],condition=j['condition'],arm=j['arm'],tag=reg['tag'],commit='d'*40,
               registration_sha256='e'*64,cache_sha256='b'*64,mask_sha256='c'*64,ru_maxrss_kib=peak,ru_maxrss_bytes=peak*1024,
               sample_point=reg['sample_point'],includes_import_validation_warmup_hash=True,incremental_renderer_peak=False,
               latency_endpoint_recorded=False,guards=dict(start=state(),ready=state(),end=state()))
        rows.append(dict(job=j,result=r));receipts[j['index']]=dict(memory=copy.deepcopy(r),started=dict(pid=pid),
            terminal=dict(status='COMPLETED',returncode=0,direct_child_reaped=True,failure=None,termination_sent=False,owned_pid=pid))
    guards=[dict(fast=state(),violations=[]) for _ in range(4*len(jobs)+1)]+[dict(actual_arm_hz=600000000) for _ in range(2*len(jobs))]
    terminal=dict(status='COMPLETED_PENDING_AUDIT',jobs=len(jobs),latency_endpoint_recorded=False)
    return rows,reg,manifest,meta,terminal,guards,receipts


def audit(fixture):
    rows,reg,manifest,meta,terminal,guards,receipts=fixture
    return analysis.audit_rows(rows,reg,manifest,meta,terminal,guards,lambda i:receipts[i],'e'*64)


def test_complete_synthetic_20_image_schedule_audits_without_empirical_claim():
    f=synthetic();a=audit(f)
    assert a['structure_ok'] and a['conditions_ok'] and a['n_jobs']==360
    endpoints,aa,med,source=analysis.per_image(f[0],f[1]['image_ids'])
    assert len(endpoints['adv'])==20 and all(math.isclose(math.exp(v),.8) for v in endpoints['adv'])
    assert all(v==0 for v in aa['clean']+aa['adv'])
    assert len(source[memory_worker.IMAGE_IDS[0]]['adv']['candidate16M'])==3


@pytest.mark.parametrize('which',['partial','duplicate','order','rss_units','mask_digest','child_alive','pid','missing_guard','endpoint','terminal'])
def test_corrupt_or_partial_cohort_never_audits_pass(which):
    f=synthetic();rows,reg,manifest,meta,terminal,guards,receipts=f
    if which=='partial':rows.pop()
    elif which=='duplicate':rows.append(copy.deepcopy(rows[0]))
    elif which=='order':rows.reverse()
    elif which=='rss_units':rows[0]['result']['ru_maxrss_bytes']=9
    elif which=='mask_digest':rows[0]['result']['mask_sha256']='0'*64
    elif which=='child_alive':receipts[0]['terminal']['direct_child_reaped']=False
    elif which=='pid':receipts[0]['started']['pid']+=1
    elif which=='missing_guard':guards.clear()
    elif which=='endpoint':rows[0]['result']['incremental_renderer_peak']=True
    elif which=='terminal':terminal['status']='FAILED_STOPPED_NO_RETRY'
    assert not audit(f)['structure_ok']


def test_physical_condition_violation_remains_failed():
    f=synthetic();f[5][0]['fast']['temp_c']=75
    assert audit(f)['structure_ok'] and not audit(f)['conditions_ok']


def test_zero_variance_precision_has_zero_mde_but_not_equivalence():
    f=synthetic();p=analysis.precision([0.]*20,f[1])
    assert p['aa_ok'] and p['mde_ok'] and p['mde_log_80pct']==0
    s=analysis.ratio_summary([0.]*20,2026111403)
    assert s['dz'] is None and not s['dz_defined'] and s['p_sign_flip']==1
    json.dumps(s,allow_nan=False)


def test_missing_artifacts_produce_failed_audit_without_ci(tmp_path):
    result=analysis.analyze(tmp_path,tmp_path/'missing.json',tmp_path/'cache')
    assert not result['quality_pass'] and not result['audit']['structure_ok']
    assert 'primary_adv_candidate_over_baseline' not in result


def archive_fixture(root,phase='full',aa_failure=False):
    # Synthetic measurements under pytest temp; real frozen caches read-only for SHA validation.
    import test_pi3b_renderer_memory_v1_contracts as contracts
    from cache import record,sha
    f=synthetic(phase);rows,reg,manifest,meta,terminal,guards,receipts=f
    campaign=root/'synthetic_campaign';data=campaign/'memory';data.mkdir(parents=True)
    cache=STUDY.parents[1]/'results/pi3b_renderer_functional_cache_20261114/caches/cache_01'
    manifest=json.loads((cache/'manifest.json').read_text(encoding='utf-8'))
    realcases={(r['image'],r['condition']):r for r in manifest['cases']}
    fullreg=contracts.registered_fixture();fullreg['cache_manifest_sha256']=sha(cache/'manifest.json')
    path=root/'registration.json';record(path,fullreg);regsha=sha(path)
    meta['cache_manifest_sha256']=fullreg['cache_manifest_sha256'];meta['lock_sha256']=regsha
    record(data/'registration.json',meta);record(data/'terminal.json',terminal)
    for row in rows:
        if aa_failure and row['job']['arm']=='baseline_B':
            row['result']['ru_maxrss_kib']*=2
            row['result']['ru_maxrss_bytes']*=2
        actual=realcases[(row['job']['image'],row['job']['condition'])]
        row['result']['cache_sha256']=actual['sha256'];row['result']['mask_sha256']=actual['mask_sha256'];row['result']['registration_sha256']=regsha
        receipts[row['job']['index']]['memory']=copy.deepcopy(row['result'])
    (data/'raw.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n',encoding='utf-8')
    (data/'guards.jsonl').write_text('\n'.join(json.dumps(r) for r in guards)+'\n',encoding='utf-8')
    for i,values in receipts.items():
        d=data/'jobs'/f'{i:04d}';d.mkdir(parents=True)
        for name,value in values.items():record(d/(name+'.json'),value)
    return campaign,path,cache


def test_file_based_gate_never_qualifies_before_restore(tmp_path,monkeypatch):
    campaign,path,cache=archive_fixture(tmp_path)
    result=analysis.analyze(campaign,path,cache,True)
    assert result['session_gate_pass'] and result['restore_pending'] and not result['quality_pass']
    monkeypatch.setattr(analysis,'ratio_summary',lambda *_:dict(synthetic_stats_stub=True))
    result=analysis.analyze(campaign,path,cache)
    assert result['session_gate_pass'] and not result['restore_ok'] and not result['quality_pass']
    (campaign/'restore.json').write_text(json.dumps(dict(status='RESTORED',errors=[])))
    result=analysis.analyze(campaign,path,cache)
    assert not result['controller_terminal_ok'] and not result['quality_pass']
    (campaign/'campaign_terminal.json').write_text(json.dumps(dict(status='COMPLETED',gate_returncode=0)))
    assert analysis.analyze(campaign,path,cache)['quality_pass']


def test_partial_archive_produces_audit_without_filtered_ci(tmp_path,monkeypatch):
    campaign,path,cache=archive_fixture(tmp_path);raw=campaign/'memory/raw.jsonl';lines=raw.read_text().splitlines()
    raw.write_text('\n'.join(lines[:-1])+'\n')
    monkeypatch.setattr(analysis,'ratio_summary',lambda *_:pytest.fail('no inferential CI for incomplete cohort'))
    result=analysis.analyze(campaign,path,cache)
    assert not result['quality_pass'] and not result['audit']['structure_ok']
    assert 'primary_adv_candidate_over_baseline' not in result


def test_clean_and_attacked_precision_controls_each_enforced():
    f=synthetic();reg=f[1]
    assert not analysis.precision([.1]*20,reg)['aa_ok']
    assert not analysis.precision([0.]*19+[1.],reg)['mde_ok']


def test_invalid_restore_type_cannot_qualify_complete_data(tmp_path,monkeypatch):
    campaign,path,cache=archive_fixture(tmp_path)
    (campaign/'restore.json').write_text('[]')
    monkeypatch.setattr(analysis,'ratio_summary',lambda *_:dict(synthetic_stats_stub=True))
    result=analysis.analyze(campaign,path,cache)
    assert result['session_gate_pass'] and not result['restore_ok'] and not result['quality_pass']


def test_sleep_qa_rejects_imported_model_runtime_before_configuration(tmp_path,monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv('INVOCATION_ID','synthetic')
    monkeypatch.setitem(sys.modules,'torch',object())
    monkeypatch.setattr(control,'locked_materials',lambda *_:dict(qa_tag='qa-fixture'))
    monkeypatch.setattr(control,'Lease',lambda *_:pytest.fail('no configuration changes with an imported model runtime'))
    with pytest.raises(RuntimeError,match='sleep-only QA'):
        control.payload(SimpleNamespace(mode='qa',tag='qa-fixture',commit='a'*40,directory=tmp_path))


def test_smoke_schedule_preserves_master_image_seed_and_contains_k300():
    smoke=schedule(memory_worker.PHASES['smoke']['image_ids'],20261114)
    full=schedule(memory_worker.IMAGE_IDS,20261114)
    assert len(smoke)==36
    strip_index=lambda rows:[{k:v for k,v in j.items() if k!='index'} for j in rows]
    assert strip_index(smoke)==strip_index([j for j in full if j['image'] in memory_worker.PHASES['smoke']['image_ids']])
    cache=STUDY.parents[1]/'results/pi3b_renderer_functional_cache_20261114/caches/cache_01/manifest.json'
    cases=json.loads(cache.read_text())['cases']
    assert any(c['image'] in memory_worker.PHASES['smoke']['image_ids'] and c['k']==300 for c in cases)


@pytest.mark.parametrize('phase',['smoke','full'])
def test_prospective_precision_policy_and_smoke_never_produce_efficacy(tmp_path,monkeypatch,phase):
    campaign,path,cache=archive_fixture(tmp_path,phase,aa_failure=True)
    (campaign/'restore.json').write_text(json.dumps(dict(status='RESTORED',errors=[])))
    (campaign/'campaign_terminal.json').write_text(json.dumps(dict(status='COMPLETED',gate_returncode=0)))
    monkeypatch.setattr(analysis,'ratio_summary',lambda *_:dict(synthetic_stats_stub=True))
    result=analysis.analyze(campaign,path,cache)
    assert result['audit']['structure_ok'] and result['audit']['conditions_ok']
    assert not result['aa_controls']['adv']['aa_ok'] and not result['aa_controls']['clean']['aa_ok']
    assert result['session_gate_pass']==(phase=='smoke')
    assert result['technical_smoke_pass']==(phase=='smoke')
    assert not result['quality_pass']
    if phase=='smoke':assert 'primary_adv_candidate_over_baseline' not in result


@pytest.mark.parametrize('failure',['none','missing_review','raw_changed','gate_changed','restore_failed','controller_failed','wrong_phase','truthy_gate','structure_failed'])
def test_full_launch_requires_bound_smoke_and_independent_review(tmp_path,failure):
    from cache import record,sha
    tag='prereg-pi3b-renderer-memory-fixture';commit='d'*40
    reg=tmp_path/'registration.json';record(reg,dict(synthetic=True))
    smoke=tmp_path/'runs/memory_smoke_01';(smoke/'memory').mkdir(parents=True)
    record(smoke/'registration.json',dict(tag=tag,commit=commit,mode='memory',phase='smoke',lock_sha256=sha(reg)))
    record(smoke/'gates.json',dict(phase='smoke',precision_enforced=False,session_gate_pass=True,
        audit=dict(structure_ok=True,conditions_ok=True)))
    record(smoke/'restore.json',dict(status='RESTORED',errors=[]))
    record(smoke/'campaign_terminal.json',dict(status='COMPLETED',gate_returncode=0))
    (smoke/'memory/raw.jsonl').write_text('{"synthetic": true}\n')
    record(tmp_path/'smoke_review.json',dict(technical_smoke_pass=True,tag=tag,commit=commit,registration_sha256=sha(reg),
        smoke_raw_sha256=sha(smoke/'memory/raw.jsonl'),smoke_gate_sha256=sha(smoke/'gates.json'),
        smoke_restore_sha256=sha(smoke/'restore.json')))
    if failure=='missing_review':(tmp_path/'smoke_review.json').unlink()
    elif failure=='raw_changed':(smoke/'memory/raw.jsonl').write_text('{}\n')
    elif failure=='gate_changed':(smoke/'gates.json').write_text('{}')
    elif failure=='restore_failed':(smoke/'restore.json').write_text(json.dumps(dict(status='RESTORE_FAILED',errors=['test'])))
    elif failure=='controller_failed':(smoke/'campaign_terminal.json').write_text(json.dumps(dict(status='FAILED_STOPPED_NO_RETRY',gate_returncode=66)))
    elif failure in ('wrong_phase','truthy_gate','structure_failed'):
        path=smoke/'gates.json';gate=json.loads(path.read_text())
        if failure=='wrong_phase':gate['phase']='full'
        elif failure=='truthy_gate':gate['session_gate_pass']='yes'
        else:gate['audit']['structure_ok']=False
        path.write_text(json.dumps(gate))
    if failure=='none':assert control.full_eligible(tmp_path,reg,tag,commit)
    else:
        with pytest.raises((ValueError,KeyError,OSError)):control.full_eligible(tmp_path,reg,tag,commit)
