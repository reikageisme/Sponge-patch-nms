"""Safety/structure regression tests; synthetic data only, no pin/model benchmark."""
from pathlib import Path
import copy
import importlib.util
import json
import random
import sys

import pytest

STUDY=Path(__file__).resolve().parents[1]/'studies'/'pi3b_600mhz_swapguard_v2'
sys.path.insert(0,str(STUDY))
import guard
import control
import audit
import analyze

LOCK=json.loads((STUDY/'lock.json').read_text(encoding='utf-8'))


def fast():
    return dict(governor='powersave',scaling_cur_khz=600000,temp_c=40.,affinity=[0,1,2,3],
                mem_kb=dict(MemAvailable=200000,SwapTotal=0),swaps=[],usb=[],
                masks={u:True for u in guard.UNITS},vmstat=dict(pswpin=10,pswpout=20,oom_kill=0))


@pytest.mark.parametrize('change,reason',[
    (lambda e:e['mem_kb'].update(SwapTotal=10),'swap'),
    (lambda e:e.update(governor='ondemand'),'governor'),
    (lambda e:e.update(affinity=[3]),'affinity'),
    (lambda e:e.update(temp_c=float('nan')),'temperature'),
    (lambda e:e.update(temp_c=75),'temperature'),
    (lambda e:e['mem_kb'].update(MemAvailable=39999),'memory'),
    (lambda e:e.update(usb=['sda']),'usb'),
    (lambda e:e['masks'].update({'dev-zram0.swap':False}),'runtime_mask'),
    (lambda e:e.update(scaling_cur_khz=1200000),'requested_clock'),
    (lambda e:e['vmstat'].update(pswpout=21),'vmstat_change'),
    (lambda e:e.pop('mem_kb'),'invalid_readback')])
def test_guard_stops_on_each_condition(change,reason):
    env=fast(); baseline=copy.deepcopy(env['vmstat']);change(env)
    assert reason in guard.violations(env,LOCK,[0,1,2,3],baseline)


def test_guard_accepts_declared_condition_not_nominal_clock():
    assert guard.violations(fast(),LOCK,[0,1,2,3],fast()['vmstat'])==[]
    assert guard.strict_temp("temp=40.5'C")==40.5
    with pytest.raises(ValueError):guard.strict_temp('ERROR temp -1')
    assert guard.parse_swaps('Filename Type Size Used Priority\n')==[]
    with pytest.raises(ValueError):guard.parse_swaps('unreadable')


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


@pytest.mark.parametrize('swap',[True,False])
@pytest.mark.parametrize('timer',[True,False])
def test_lease_restores_initial_configuration_and_is_idempotent(tmp_path,swap,timer):
    system=FakeSystem(swap,timer); lease=control.Lease(tmp_path,system)
    lease.apply()
    assert not system.now['swaps'] and all(system.now['masks'].values())
    assert lease.restore()['status']=='RESTORED'
    n=len(system.calls)
    assert lease.restore()['status']=='RESTORED' and len(system.calls)==n
    assert system.now['governor']=='ondemand' and system.now['swaps']==system.original['swaps']
    assert ('start','dev-zram0.swap') not in system.calls if not swap else True


@pytest.mark.parametrize('at',range(1,4))
def test_partial_setup_restores_after_intended_action_failure(tmp_path,at):
    system=FakeSystem(fail=at); lease=control.Lease(tmp_path,system)
    with pytest.raises(RuntimeError):lease.apply()
    system.fail=None
    assert control.Lease(tmp_path,system).restore()['status']=='RESTORED'
    assert system.now['swaps']==system.original['swaps'] and not any(system.now['masks'].values())


def test_restore_errors_remain_failed_and_do_not_skip_other_cleanup(tmp_path):
    system=FakeSystem();lease=control.Lease(tmp_path,system);lease.apply()
    system.fail=len(system.calls)+1
    result=lease.restore()
    assert result['status']=='RESTORE_FAILED' and result['errors']
    assert system.now['governor']=='ondemand' and system.now['swaps']==system.original['swaps']
    assert lease.restore()==result  # no second attempt to manufacture a passing receipt


def test_partial_mask_batch_undoes_only_masks_actually_created(tmp_path):
    class Partial(FakeSystem):
        def ctl(self,*argv):
            if argv[0]=='mask':
                self.now['masks']['dev-zram0.swap']=True
                raise RuntimeError('batch interrupted after its first mask')
            return super().ctl(*argv)
    system=Partial();lease=control.Lease(tmp_path,system)
    with pytest.raises(RuntimeError):lease.apply()
    assert lease.restore()['status']=='RESTORED'
    assert ('unmask','--runtime','dev-zram0.swap') in system.calls


def test_setup_unit_failure_is_not_hidden_by_matching_kernel_swap(tmp_path):
    system=FakeSystem();lease=control.Lease(tmp_path,system);lease.apply()
    system.now['setup']['Result']='exit-code'
    result=lease.restore()
    assert system.now['swaps']==system.original['swaps']
    assert result['status']=='RESTORE_FAILED'
    assert 'restored zram setup state differs' in result['errors']


def test_reject_unsafe_snapshot_before_mutation(tmp_path):
    system=FakeSystem();system.original['swaps'][0]['name']='/dev/sda'
    with pytest.raises(ValueError):control.Lease(tmp_path,system).apply()
    assert not system.calls and not (tmp_path/'lease_state.json').exists()


def fixture(tmp_path,mode='pipeline',smoke=True,stage_b_factors=None):
    """A small *smoke* fixture in the real frozen ID/order/guard schema."""
    d=tmp_path/(mode+'_PI4');d.mkdir()
    cfg=LOCK['smoke' if smoke else 'full'];cfg_n=cfg['n_images'];rows=[];gid=0;t=10000
    pins=lambda kind:dict(kind=kind,passed=True,affinity=[0,1,2,3],busy=[.9]*4,inside=3.6,outside=0.,need=2.8)
    env=dict(governor='powersave',arm_clock_hz='frequency(48)=600000000',temp="temp=40.0'C",
             mem_kb=dict(SwapTotal=0,MemAvailable=200000),throttled='throttled=0x50005')
    def measured(ns):
        nonlocal gid,t
        gid+=1;t+=10000
        rows.extend([dict(kind='guard',guard_id=gid,phase='pre',fast=fast(),violations=[]),
                     dict(kind='guard',guard_id=gid,phase='post',fast=fast(),violations=[],ns=ns,t_start_ns=t,process_cpu_ns=ns)])
        return dict(ns=ns,t_start_ns=t,process_cpu_ns=ns,guard_id=gid)
    def reference(block):
        samples=[measured(100)['ns'] for _ in range(cfg['reference_samples'])]
        rows.append(dict(kind='reference',block=block,samples_ns=samples,ratio=1.,flagged=False))
    rows.append(pins('pin_start'));reference('start')
    for ix,name in enumerate(LOCK['inputs'][:cfg_n]):
        im=Path(name).name.split('_')[0]
        rows.append(dict(kind='environment',block=ix,**env))
        rows.append(dict(kind='condition',block=ix,fast=fast(),violations=[]))
        reference(ix)
        c=dict(n_tau=10,kernel_n=10,k=3,prediction_sha256='a'*64)
        a=dict(n_tau=500,kernel_n=500,k=100,prediction_sha256='b'*64)
        rows.append(dict(kind='counts',image=im,block=ix,counts=dict(clean=c,adv=a,advcap=dict(n_tau=500,kernel_n=300,k=60,options=LOCK['defense']))))
        arms=list(audit.ARMS if mode=='pipeline' else audit.STAGES)
        if mode=='stages' and ix<cfg['dose_images']:
            arms += [f'maskdose_{k}' for k in LOCK['dose_levels'] if k<=a['k']]
        for rep in range(cfg['repeats'][mode+'_PI4']):
            order=list(range(len(arms)));random.Random(LOCK['seed']+1000*ix+rep).shuffle(order)
            for pos,j in enumerate(order):
                ns=100 if j<2 else 100+10*j
                if mode=='stages':
                    ns={'nms_clean':100,'nms_adv':200,'nms_adv_B':200,'mask_clean':300,'mask_adv':400,'mask_adv_B':400}.get(arms[j],500)
                    if arms[j].endswith('_B'):
                        ns=int(ns*(stage_b_factors or {}).get(arms[j].split('_')[0],1.))
                rows.append(dict(kind='timing',image=im,block=ix,arm=arms[j],rep=rep,position=pos,**measured(ns)))
        rows.append(dict(kind='memory',image=im))
    reference('end');rows.extend([dict(kind='environment',block='end',**env),dict(kind='condition',block='end',fast=fast(),violations=[]),pins('pin_end'),dict(kind='done',environment_end=env)])
    # Equal clean A/B medians are not necessary for structural checks; gate estimates are separate.
    by={r['name']:r['sha256'] for r in LOCK['files']}
    m=dict(mode=mode,profile='PI4',smoke=smoke,tag=LOCK['registration_tag'],prereg_commit='a'*40,
           lock_sha256=audit.sha(STUDY/'lock.json'),runner_sha256=by['run.py'],versions=LOCK['versions'],config=cfg,
           cpu_set=[0,1,2,3],torch_threads=4,interop_threads=1,weights_sha256=by[LOCK['weights']],initial_fast=fast(),environment_start=env,guard_policy=LOCK['guard_policy'])
    (d/'manifest.json').write_text(json.dumps(m),encoding='utf-8')
    (d/'terminal.json').write_text(json.dumps(dict(status='COMPLETED')),encoding='utf-8')
    (d.parent/'registration.json').write_text(json.dumps(dict(tag=m['tag'],commit=m['prereg_commit'],lock_sha256=m['lock_sha256'],mode='smoke' if smoke else 'full')),encoding='utf-8')
    save_rows(d,rows)
    return d,rows


def save_rows(d,rows):
    (d/'raw.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n',encoding='utf-8')


def test_strict_audit_accepts_complete_schedule(tmp_path):
    d,_=fixture(tmp_path)
    s=audit.audit_session(d,LOCK,audit.sha(STUDY/'lock.json'))
    assert s['structure_ok'] and s['conditions_ok'],s
    assert s['n_timings']==24 and s['n_guards']==72
    assert analyze.gate_session(d,STUDY/'lock.json')['quality_pass'] is True


@pytest.mark.parametrize('change',[
    lambda rows:rows.pop(next(i for i,r in enumerate(rows) if r['kind']=='pin_start')),
    lambda rows:rows.pop(next(i for i,r in enumerate(rows) if r['kind']=='timing')),
    lambda rows:rows.append(copy.deepcopy(next(r for r in rows if r['kind']=='timing'))),
    lambda rows:next(r for r in rows if r['kind']=='timing').update(image='wrong'),
    lambda rows:next(r for r in rows if r['kind']=='timing').update(position=99),
    lambda rows:next(r for r in rows if r['kind']=='timing').update(ns=0),
    lambda rows:rows.pop(next(i for i,r in enumerate(rows) if r['kind']=='guard')),
    lambda rows:next(r for r in rows if r['kind']=='reference').update(flagged=True),
])
def test_strict_audit_refuses_incomplete_or_corrupt_evidence(tmp_path,change):
    d,rows=fixture(tmp_path);change(rows);save_rows(d,rows)
    result=audit.audit_session(d,LOCK,audit.sha(STUDY/'lock.json'))
    assert not result['structure_ok'],result
    assert analyze.gate_session(d,STUDY/'lock.json')['quality_pass'] is False


def test_swap_gate_failure_cannot_be_overridden_by_complete_data(tmp_path):
    d,rows=fixture(tmp_path)
    next(r for r in rows if r['kind']=='guard')['fast']['mem_kb']['SwapTotal']=1
    save_rows(d,rows)
    result=audit.audit_session(d,LOCK,audit.sha(STUDY/'lock.json'))
    assert result['structure_ok'] and not result['conditions_ok']
    assert analyze.gate_session(d,STUDY/'lock.json')['quality_pass'] is False


def test_unsupervised_payload_refused_before_configuration(monkeypatch,tmp_path):
    monkeypatch.delenv('INVOCATION_ID',raising=False)
    with pytest.raises(RuntimeError,match='transient systemd'):control.payload(None)


def test_worker_preparation_failure_preserved_without_torch(tmp_path):
    spec=importlib.util.spec_from_file_location('pi_v2_worker',STUDY/'run.py')
    run=importlib.util.module_from_spec(spec);spec.loader.exec_module(run)
    class Args:
        run_dir=tmp_path/'bad';base=tmp_path;lock=tmp_path/'absent';profile='PI4';mode='pipeline'
    with pytest.raises(FileNotFoundError):run.main(Args())
    assert json.loads((Args.run_dir/'terminal.json').read_text())['status']=='FAILED'
    assert json.loads((Args.run_dir/'raw.jsonl').read_text())['kind']=='preparation_failed'
    with pytest.raises(FileExistsError):run.main(Args())


def test_core_computation_and_estimators_unchanged_from_original():
    import ast
    old=STUDY.with_name('pi3b_600mhz')
    def fn(path,name):
        node=next(n for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.FunctionDef) and n.name==name)
        # Moving an unchanged stats import from module to function enables scipy-free Pi gates.
        node.body=[n for n in node.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
        return node
    for name in ['arm_order','dose_levels','pred_proto','suppress','full','observed_suppression','load_pair','mask_job']:
        assert ast.dump(fn(STUDY/'run.py',name))==ast.dump(fn(old/'run.py',name)),name
    for name in ['medians','ratio_summary','pipeline','stages']:
        assert ast.dump(fn(STUDY/'analyze.py',name))==ast.dump(fn(old/'analyze.py',name)),name
    stats_source=STUDY.parents[1]/'src'/'sponge_sim'/'stats.py'
    for name in ['bootstrap_ci','sign_flip_p','dz','paired_summary','holm','mde_paired']:
        assert ast.dump(fn(STUDY/'stats_frozen.py',name))==ast.dump(fn(stats_source,name)),name


def test_new_lock_binds_all_runtime_sources_and_old_input_identities():
    old=json.loads((STUDY.with_name('pi3b_600mhz')/'lock.json').read_text(encoding='utf-8'))
    assert LOCK['inputs']==old['inputs'] and LOCK['profiles']==old['profiles']
    for key in ['defense','dose_levels','gates','full','smoke','versions','nms_source_sha256','ops_source_sha256']:
        assert LOCK[key]==old[key],key
    by={r['name']:r['sha256'] for r in LOCK['files']}
    for name in ['run.py','guard.py','audit.py','control.py','analyze.py','stats_frozen.py','build_lock.py']:
        assert audit.sha(STUDY/name)==by[name]
    old_by={r['name']:r['sha256'] for r in old['files']}
    assert all(by[n]==old_by[n] for n in LOCK['inputs']+[LOCK['weights']])


@pytest.mark.parametrize('field',['runner_sha256','lock_sha256','weights_sha256','prereg_commit','tag'])
def test_audit_refuses_changed_provenance(tmp_path,field):
    d,_=fixture(tmp_path);p=d/'manifest.json';m=json.loads(p.read_text());m[field]='changed'
    p.write_text(json.dumps(m),encoding='utf-8')
    assert not audit.audit_session(d,LOCK,audit.sha(STUDY/'lock.json'))['structure_ok']


@pytest.mark.parametrize('n',[2,20])
@pytest.mark.parametrize('sd',[0.,.007,.123])
def test_locked_mde_constants_preserve_full_analyzer_formula(n,sd):
    import numpy as np
    import stats_frozen
    assert float(LOCK['mde_t_critical_sums'][str(n)]*sd/np.sqrt(n))==stats_frozen.mde_paired(sd,n)


def test_gate_only_cli_works_with_scipy_import_forbidden(tmp_path):
    import subprocess
    d,_=fixture(tmp_path)
    code="""
import sys,runpy
class NoScipy:
 def find_spec(self, fullname, path=None, target=None):
  if fullname=='scipy' or fullname.startswith('scipy.'):
   raise ImportError('scipy intentionally unavailable')
sys.meta_path.insert(0,NoScipy())
sys.argv=[sys.argv[1],sys.argv[2],'--gate-only']
runpy.run_path(sys.argv[0],run_name='__main__')
"""
    import os
    env=dict(os.environ,PYTHONPATH=str(STUDY))
    r=subprocess.run([sys.executable,'-c',code,str(STUDY/'analyze.py'),str(d)],capture_output=True,text=True,env=env)
    assert r.returncode==0,r.stderr
    assert json.loads((d/'gates.json').read_text())['quality_pass'] is True


@pytest.mark.parametrize('change',[
    lambda r:next(x for x in r if x['kind']=='pin_start').update(busy=[]),
    lambda r:next(x for x in r if x['kind']=='pin_start').update(inside=4),
    lambda r:next(x for x in r if x['kind']=='pin_end').update(need=0),
    lambda r:next(x for x in r if x['kind']=='counts')['counts']['adv'].update(kernel_n=499),
    lambda r:next(x for x in r if x['kind']=='counts')['counts']['advcap'].update(n_tau=1),
    lambda r:next(x for x in r if x['kind']=='counts')['counts']['adv'].update(prediction_sha256='missing')])
def test_recompute_pin_and_count_contracts_rather_than_trust_pass_flag(tmp_path,change):
    d,rows=fixture(tmp_path);change(rows);save_rows(d,rows)
    assert not audit.audit_session(d,LOCK,audit.sha(STUDY/'lock.json'))['structure_ok']


def test_full_components_require_both_new_stage_noise_controls(tmp_path):
    d,_=fixture(tmp_path,mode='stages',smoke=False)
    result=analyze.gate_session(d,STUDY/'lock.json')
    assert result['quality_pass'] and result['stage_aa_enforced'],result
    assert set(result['stage_controls'])=={'nms','mask'}


@pytest.mark.parametrize('stage',['nms','mask'])
def test_bad_component_aa_rejects_full_without_rescuing_images(tmp_path,stage):
    d,_=fixture(tmp_path,mode='stages',smoke=False,stage_b_factors={stage:.7})
    result=analyze.gate_session(d,STUDY/'lock.json')
    assert result['audit']['structure_ok']
    assert not result['quality_pass'] and not result['stage_controls'][stage]['aa_ok']


def test_smoke_component_controls_descriptive_not_full_qualification(tmp_path):
    d,_=fixture(tmp_path,mode='stages',stage_b_factors={'nms':.7})
    result=analyze.gate_session(d,STUDY/'lock.json')
    assert not result['stage_aa_enforced'] and result['quality_pass']
    assert not result['stage_controls']['nms']['aa_ok']
