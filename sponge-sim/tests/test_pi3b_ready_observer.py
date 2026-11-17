"""Fake unit/procfs/SSH only; never issue a live query or benchmark."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types

import pytest

S=Path(__file__).parents[1]/'studies/pi3b_ready_observer_20261115'
modules={}
for name in ('probe','transport'):
    spec=importlib.util.spec_from_file_location('prepared_ready_'+name,S/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);modules[name]=module
probe=modules['probe'];transport=modules['transport']


@pytest.fixture
def ready_context(tmp_path,monkeypatch):
    base=tmp_path/'workspace';directory=base/'runs/qa_new_normal_01';directory.mkdir(parents=True)
    (base/'controller_lock.json').write_text('{"qa_tag":"qa"}')
    ready=dict(pid=12,child_pid=13,child_start_ticks=22,invocation_id='a'*32,torch_imported=False,scipy_imported=False)
    (directory/'qa_ready.json').write_text(json.dumps(ready))
    header=dict(tag='qa',commit='b'*40,mode='qa',lock_sha256=hashlib.sha256((base/'controller_lock.json').read_bytes()).hexdigest())
    (directory/'registration.json').write_text(json.dumps(header));(directory/'usb_preflight.json').write_bytes(b'{"fake":true}')
    proc=tmp_path/'proc';(proc/'13').mkdir(parents=True)
    (proc/'13/stat').write_text('13 (child) '+' '.join(['S']+['0']*18+['22']))
    (proc/'13/cgroup').write_text('0::/system.slice/'+probe.SERVICE+'\n')
    (proc/'swaps').write_text('Filename Type Size Used Priority\n')
    policy=tmp_path/'policy';policy.mkdir();(policy/'scaling_governor').write_text('powersave\n')
    units=('dev-zram0.swap','rpi-zram-writeback.service','rpi-zram-writeback.timer');masks={x:True for x in units}
    class Link:
        def __init__(self,name):self.name=name
        def is_symlink(self):return masks[self.name]
    class MaskRoot:
        def __truediv__(self,name):return Link(name)
    monkeypatch.setattr(probe,'PROC',proc);monkeypatch.setattr(probe,'MASK_ROOT',MaskRoot())
    monkeypatch.setattr(probe.os,'readlink',lambda link:'/dev/null')
    monkeypatch.setattr(probe.time,'time',lambda:1234.5)
    calls=[];phase_calls=[]
    def unit_query(argv,**kwargs):
        calls.append(dict(argv=argv,kwargs=kwargs))
        assert kwargs['timeout']==10
        return types.SimpleNamespace(returncode=0,stdout='MainPID=12\nInvocationID='+'a'*32+'\nActiveState=active\n',stderr='')
    monkeypatch.setattr(probe.subprocess,'run',unit_query)
    def phase(*args):
        phase_calls.append(args)
        return hashlib.sha256((directory/'usb_preflight.json').read_bytes()).hexdigest()
    control=types.SimpleNamespace(HERE=base,ROOT=base,POLICY=policy,UNITS=units,
        parse_swaps=lambda text:[] if text=='Filename Type Size Used Priority\n' else ['swap_on'],
        require_phase_storage=phase,System=lambda:pytest.fail('old expensive System.current() must not run'))
    return types.SimpleNamespace(base=base,directory=directory,ready=ready,header=header,control=control,
        proc=proc,policy=policy,masks=masks,calls=calls,phase_calls=phase_calls)


def observe(c):return probe.observe(c.base,'qa_new_normal_01',c.control)


def test_readiness_required_state_and_one_manager_query(ready_context):
    c=ready_context;result=observe(c)
    assert result['ready']==c.ready and result['observed_at_utc']==1234.5
    assert result['sequential_not_atomic'] and result['source_qualification_performed'] is False
    assert len(c.calls)==result['manager_queries']==1 and len(c.phase_calls)==1
    assert c.calls[0]['argv']==['systemctl','show',probe.SERVICE,'-p','MainPID','-p','InvocationID','-p','ActiveState']


def test_missing_receipt_is_not_ready_and_has_no_manager_query(ready_context):
    c=ready_context;(c.directory/'qa_ready.json').unlink()
    assert observe(c) is None and c.calls==[]


@pytest.mark.parametrize('change',['torch','scipy','bool_pid','same_pids','bad_invocation','extra_field','child_reused',
    'cgroup_substring','child_wrong_pid','swap_on','wrong_governor','missing_mask','wrong_mode','wrong_lock','bad_commit'])
def test_bad_readiness_cannot_be_promoted(ready_context,change):
    c=ready_context
    if change=='torch':c.ready['torch_imported']=True
    elif change=='scipy':c.ready['scipy_imported']=True
    elif change=='bool_pid':c.ready['pid']=True
    elif change=='same_pids':c.ready['pid']=c.ready['child_pid']
    elif change=='bad_invocation':c.ready['invocation_id']=''
    elif change=='extra_field':c.ready['extra']=0
    elif change=='child_reused':(c.proc/'13/stat').write_text('13 (reused) '+' '.join(['S']+['0']*18+['23']))
    elif change=='child_wrong_pid':(c.proc/'13/stat').write_text('99 (wrong) '+' '.join(['S']+['0']*18+['22']))
    elif change=='cgroup_substring':(c.proc/'13/cgroup').write_text('0::/system.slice/'+probe.SERVICE+'-other\n')
    elif change=='swap_on':(c.proc/'swaps').write_text('enabled')
    elif change=='wrong_governor':(c.policy/'scaling_governor').write_text('ondemand')
    elif change=='missing_mask':c.masks['dev-zram0.swap']=False
    elif change=='wrong_mode':c.header['mode']='functional'
    elif change=='wrong_lock':c.header['lock_sha256']='f'*64
    elif change=='bad_commit':c.header['commit']='not-a-commit'
    (c.directory/'qa_ready.json').write_text(json.dumps(c.ready))
    (c.directory/'registration.json').write_text(json.dumps(c.header))
    with pytest.raises(ValueError):observe(c)


@pytest.mark.parametrize('unit_change',['pid','invocation','inactive','duplicate','nonzero','timeout'])
def test_unit_query_failures_propagate_without_retry(ready_context,monkeypatch,unit_change):
    c=ready_context;calls=[]
    def run(*args,**kwargs):
        calls.append(1)
        if unit_change=='timeout':raise subprocess.TimeoutExpired(args[0],10)
        fields={'MainPID':'12','InvocationID':'a'*32,'ActiveState':'active'}
        if unit_change=='pid':fields['MainPID']='99'
        if unit_change=='invocation':fields['InvocationID']='c'*32
        if unit_change=='inactive':fields['ActiveState']='inactive'
        stdout=''.join(f'{k}={v}\n' for k,v in fields.items())
        if unit_change=='duplicate':stdout+='MainPID=12\n'
        return types.SimpleNamespace(returncode=1 if unit_change=='nonzero' else 0,stdout=stdout,stderr='fake error')
    monkeypatch.setattr(probe.subprocess,'run',run)
    with pytest.raises((ValueError,RuntimeError,subprocess.TimeoutExpired)):observe(c)
    assert calls==[1]


def test_child_dies_during_phase_validation_is_not_ready(ready_context):
    c=ready_context;original=c.control.require_phase_storage
    def phase(*args):
        result=original(*args);(c.proc/'13/stat').unlink();return result
    c.control.require_phase_storage=phase
    with pytest.raises(FileNotFoundError):observe(c)


def test_usb_phase_failure_and_hash_mismatch_propagate(ready_context):
    c=ready_context;c.control.require_phase_storage=lambda *args:'f'*64
    with pytest.raises(ValueError,match='USB'):observe(c)


def test_wrong_workspace_or_traversal_refused_before_query(ready_context):
    c=ready_context
    with pytest.raises(ValueError):probe.observe(c.base,'../other',c.control)
    with pytest.raises(ValueError):probe.observe(c.base.parent,'qa_new_normal_01',c.control)
    assert c.calls==[]


def test_transport_valid_null_preserves_original_streams(tmp_path,monkeypatch):
    calls=[]
    def run(argv,**kwargs):
        calls.append(kwargs);return types.SimpleNamespace(returncode=0,stdout=b'null\n',stderr=b'warning\r\n')
    monkeypatch.setattr(transport.subprocess,'run',run)
    out=tmp_path/'query';assert transport.capture("print('null')",40,out) is None
    assert calls[0]['timeout']==25 and calls[0]['input']==b"print('null')"
    assert (out/'stdout.bin').read_bytes()==b'null\n' and (out/'stderr.bin').read_bytes()==b'warning\r\n'
    receipt=json.loads((out/'receipt.json').read_text());assert receipt['response_received'] and not receipt['automatic_retry']


def test_timeout_saves_byte_exact_prefix_and_original_exception(tmp_path,monkeypatch):
    calls=[];exc=subprocess.TimeoutExpired('fake SSH',7,output=b'partial\xff',stderr=b'error\r\n')
    def fail(*args,**kwargs):calls.append(kwargs);raise exc
    monkeypatch.setattr(transport.subprocess,'run',fail)
    out=tmp_path/'query'
    with pytest.raises(subprocess.TimeoutExpired) as caught:transport.capture("print('null')",7,out)
    assert caught.value is exc and len(calls)==1 and calls[0]['timeout']==7
    assert (out/'stdout.bin').read_bytes()==b'partial\xff' and (out/'stderr.bin').read_bytes()==b'error\r\n'
    assert json.loads((out/'receipt.json').read_text())['status']=='TIMEOUT_NO_RETRY'


@pytest.mark.parametrize('mode',['nonzero','invalid_json','nan','launch_error'])
def test_query_or_parse_error_keeps_evidence_and_never_retries(tmp_path,monkeypatch,mode):
    calls=[]
    def run(*args,**kwargs):
        calls.append(kwargs)
        if mode=='launch_error':raise OSError('fake launch error')
        return types.SimpleNamespace(returncode=3 if mode=='nonzero' else 0,
            stdout=b'NaN' if mode=='nan' else b'{broken',stderr=b'original stderr')
    monkeypatch.setattr(transport.subprocess,'run',run)
    out=tmp_path/'query'
    with pytest.raises((RuntimeError,ValueError,OSError)):transport.capture("print('null')",40,out)
    assert len(calls)==1 and (out/'stdin.py').read_bytes()==b"print('null')"
    assert (out/'stdout.bin').is_file() and (out/'stderr.bin').is_file()
    assert not json.loads((out/'receipt.json').read_text())['response_received']


@pytest.mark.parametrize('remaining',[0,-1,True,float('nan'),float('inf')])
def test_expired_or_invalid_budget_never_launches_or_allocates(tmp_path,monkeypatch,remaining):
    monkeypatch.setattr(transport.subprocess,'run',lambda *a,**k:pytest.fail('no request permitted'))
    out=tmp_path/'query'
    with pytest.raises(ValueError):transport.capture("print('null')",remaining,out)
    assert not out.exists()


def test_existing_query_destination_refuses_before_request(tmp_path,monkeypatch):
    out=tmp_path/'query';out.mkdir()
    monkeypatch.setattr(transport.subprocess,'run',lambda *a,**k:pytest.fail('existing destination must not issue request'))
    with pytest.raises(FileExistsError):transport.capture("print('null')",25,out)


def test_old_current_executes_four_unused_manager_queries_without_timing_claim():
    """Execute ONLY the old AST method against all-fake readers/commands."""
    path=S.parent/'pi3b_nms_predecessor_20261115/control.py'
    tree=ast.parse(path.read_text());system=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='System')
    method=next(n for n in system.body if isinstance(n,ast.FunctionDef) and n.name=='current')
    class FakePath:
        def __init__(self,*args):pass
        def __truediv__(self,name):return self
        def read_text(self):return 'powersave'
        def is_symlink(self):return True
    scope=dict(POLICY=FakePath(),Path=FakePath,parse_swaps=lambda text:[],
        UNITS=('dev-zram0.swap','rpi-zram-writeback.service','rpi-zram-writeback.timer'),os=types.SimpleNamespace(readlink=lambda path:'/dev/null'))
    exec(compile(ast.Module(body=[method],type_ignores=[]),str(path),'exec'),scope)
    calls=[]
    def command(*args):calls.append(args);return 'ActiveState=active\nResult=success\n'
    result=scope['current'](types.SimpleNamespace(command=command))
    assert len(calls)==4 and set(result)=={'governor','swaps','masks','active','setup'}


@pytest.fixture
def driver(monkeypatch):
    monkeypatch.syspath_prepend(str(S))
    b=S.parents[1]/'results/pi3b_ready_observer_host_qa_20261115'
    monkeypatch.syspath_prepend(str(b))
    spec=importlib.util.spec_from_file_location('prepared_qualification_driver',b/'run_qualification.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_prelaunch_missing_specific_review_blocks_before_process_or_query(driver,tmp_path,monkeypatch):
    monkeypatch.setattr(driver,'B',tmp_path)
    monkeypatch.setattr(driver.subprocess,'Popen',lambda *a,**k:pytest.fail('no native process without review'))
    with pytest.raises(FileNotFoundError):driver.main('c'*40)
    assert list(tmp_path.iterdir())==[]


def test_false_review_blocks_before_tag_lookup(driver,tmp_path,monkeypatch):
    import readiness_plan
    (tmp_path/'method_approval.json').write_text('{"user_approved": false}')
    (tmp_path/'qualification_lock.json').write_text('{}')
    monkeypatch.setattr(readiness_plan.subprocess,'check_output',lambda *a,**k:pytest.fail('unapproved method cannot query tags'))
    with pytest.raises(ValueError,match='reviewed'):readiness_plan.validate_prelaunch(tmp_path,'c'*40)


def test_proposed_driver_scripts_compile_and_assessment_unchanged(driver):
    ast.parse(driver.script('observer_normal_01',driver.READY))
    ast.parse(driver.script('observer_normal_01',driver.ASSESS))
    old=S.parents[1]/'results/pi3b_predecessor_supervisor_qa_20261115/run_device_qa.py'
    tree=ast.parse(old.read_text());value=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id',None)=='ASSESS')
    assert driver.ASSESS==value
    assert 'sys.dont_write_bytecode=True' in driver.script('observer_normal_01',driver.READY)


@pytest.mark.parametrize('fail_ready',[False,True])
def test_fake_five_case_orchestration_and_stop_on_first_observation_failure(driver,tmp_path,monkeypatch,fail_ready):
    d=driver;monkeypatch.setattr(d,'B',tmp_path)
    (tmp_path/'deployment_verification.json').write_text(json.dumps(dict(qualification_commit='c'*40,status='EXACT_READY_OBSERVER_SIDECAR_DEPLOYED')))
    monkeypatch.setattr(d,'validate_prelaunch',lambda *a:{})
    created=[];actions=[];queries=[]
    class Client:
        pid=900
        def __init__(self,argv,stdout,stderr):
            command=argv[-1];self.name=command.split('--name ')[1].split()[0];self.code=None;created.append(self)
            if 'normal' in self.name:message=b'Finished with result: success\n'
            elif 'mainkill' in self.name:message=b'status=9/KILL\n'
            elif 'timeout' in self.name:message=b'Finished with result: timeout\n'
            else:message=b'fake frontend\n'
            stdout.write(message);stdout.flush()
            assert '--commit '+d.PAYLOAD_COMMIT in command and '--mode qa' in command
        def poll(self):return self.code
        def wait(self,timeout):self.code=0 if 'normal' in self.name else 1;return self.code
        def terminate(self):actions.append(('terminate_only_owned_ssh',self.name))
    monkeypatch.setattr(d.subprocess,'Popen',Client)
    def query(code,remaining=25):
        ast.parse(code);queries.append((code,remaining))
        if 'qa_fault_intent.json' in code:
            actions.append(('verified_fault','main' if "action='main'" in code else 'child'));return dict(sent=True)
        if 'module.observe' in code:
            if fail_ready:raise subprocess.TimeoutExpired('fake SSH',25)
            return dict(ready={'pid':12,'child_pid':13},unit={'MainPID':'12'})
        if 'restore=json.loads' in code:return dict(supervisor_log='QA child exited unexpectedly: -9',journal='Deactivated successfully')
        if 'terminal=p.exists()' in code:return dict(terminal=True,state='inactive')
        if 'control.locked_materials' in code:return dict(unit={'MainPID':'0','ActiveState':'inactive'},original={})
        pytest.fail('unexpected prepared query')
    monkeypatch.setattr(d,'remote',query)
    if fail_ready:
        with pytest.raises(subprocess.TimeoutExpired):d.main('c'*40)
        assert len(created)==1 and not (tmp_path/'qualification_outcomes.json').exists() and actions==[]
    else:
        d.main('c'*40)
        result=json.loads((tmp_path/'qualification_outcomes.json').read_text())
        assert len(created)==len(result['cases'])==5
        assert result['qualification_commit']=='c'*40 and result['payload_commit']==d.PAYLOAD_COMMIT
        assert result['status']=='FIVE_READY_OBSERVER_CASES_PASS'
        assert actions==[('verified_fault','main'),('verified_fault','child'),('terminate_only_owned_ssh','observer_disconnect_01')]
        assert [name for name in result['cases']]==['observer_normal_01','observer_mainkill_01','observer_childkill_01','observer_timeout_01','observer_disconnect_01']


def test_remaining40s_budget_can_only_shorten_25s_request_cap(driver,tmp_path,monkeypatch):
    d=driver;monkeypatch.setattr(d,'B',tmp_path)
    times=iter([0,1,17]);monkeypatch.setattr(d.time,'monotonic',lambda:next(times))
    budgets=[]
    def query(code,remaining):budgets.append(remaining);return {'ready':'fake'}
    monkeypatch.setattr(d,'remote',query)
    assert d.wait_ready('observer_normal_01',types.SimpleNamespace(poll=lambda:None))=={'ready':'fake'}
    assert budgets==[23]


def test_prepared_deployer_compiles_remote_scripts_without_query_or_lease(driver,tmp_path,monkeypatch):
    b=S.parents[1]/'results/pi3b_ready_observer_host_qa_20261115'
    spec=importlib.util.spec_from_file_location('prepared_ready_deployment',b/'prepare_remote.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    monkeypatch.setattr(m,'B',tmp_path)
    lock=dict(payload_files_sha256={'control.py':'a'*64},original_device_files={},case_names=['observer_normal_01'])
    monkeypatch.setattr(m,'validate_prelaunch',lambda *args:lock)
    code_queries=[]
    def fake_query(code):
        ast.parse(code);code_queries.append(code)
        return dict(fake=True)
    monkeypatch.setattr(m,'query',fake_query)
    copies=[]
    def fake_copy(argv,**kwargs):
        assert argv[0]=='scp' and argv[-1].endswith('/probe.py')
        copies.append(argv);return types.SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(m.subprocess,'run',fake_copy)
    m.main('c'*40)
    assert len(code_queries)==2 and len(copies)==1
    assert 'side.mkdir(exist_ok=False)' in code_queries[0] and 'Lease(' not in code_queries[0]
    assert json.loads((tmp_path/'deployment_verification.json').read_text())['status']=='EXACT_READY_OBSERVER_SIDECAR_DEPLOYED'
    spec=importlib.util.spec_from_file_location('prepared_ready_collection',b/'collect_qualification.py')
    collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
    ast.parse(collector.PROBE)
