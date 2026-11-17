# FakeSystem copied from sponge-sim/tests/test_pi3b_renderer_memory_v1_supervisor.py:20-48
# SHA256 2ae1725ffce307644cf729082ea69f2a61b7af9be68783e0234d23c983e9610c; original tests unchanged.
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import pytest
import torch

S=Path(__file__).parents[1]/'studies/pi3b_nms_predecessor_20261115'
NAMES=('usb_guard','guard','bindings','cache','control','kernel_input','exports')
saved={n:sys.modules.get(n) for n in NAMES};modules={}
for name in NAMES:
 spec=importlib.util.spec_from_file_location(name,S/(name+'.py'))
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 modules[name]=module;sys.modules[name]=module
for name,value in saved.items():
 if value is None:del sys.modules[name]
 else:sys.modules[name]=value
control=modules['control'];guard=modules['guard'];bindings=modules['bindings'];exports=modules['exports'];kernel=modules['kernel_input']

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


def test_qualified_lease_and_guard_asts_unchanged():
    old=S.parent/'pi3b_renderer_memory_usb_20261115'
    a=ast.parse((old/'control.py').read_text(encoding='utf-8'));b=ast.parse((S/'control.py').read_text(encoding='utf-8'))
    for name in ('record','System','validate_snapshot','Lease'):
        get=lambda tree:next(x for x in tree.body if getattr(x,'name',None)==name)
        assert ast.dump(get(a))==ast.dump(get(b))
    for name in ('guard.py','usb_guard.py'):
        assert ast.dump(ast.parse((S/name).read_text(encoding='utf-8')))==ast.dump(ast.parse((old/name).read_text(encoding='utf-8')))


@pytest.mark.parametrize('swap',[False,True])
@pytest.mark.parametrize('timer',[False,True])
def test_exact_restore_and_idempotent_original_receipt(tmp_path,swap,timer):
    system=FakeSystem(swap,timer);lease=control.Lease(tmp_path,system)
    lease.apply();assert not system.now['swaps'] and all(system.now['masks'].values())
    receipt=lease.restore();assert receipt['status']=='RESTORED'
    calls=list(system.calls);assert lease.restore()==receipt and system.calls==calls
    assert system.now['governor']=='ondemand' and system.now['swaps']==system.original['swaps']


@pytest.mark.parametrize('at',[1,2,3])
def test_partial_mutation_restores_original_state(tmp_path,at):
    system=FakeSystem(fail=at);lease=control.Lease(tmp_path,system)
    with pytest.raises(RuntimeError):lease.apply()
    system.fail=None
    assert control.Lease(tmp_path,system).restore()['status']=='RESTORED'


def test_failed_restore_is_not_automatically_retried(tmp_path):
    system=FakeSystem();lease=control.Lease(tmp_path,system);lease.apply()
    system.fail=len(system.calls)+1;receipt=lease.restore();assert receipt['status']=='RESTORE_FAILED'
    system.fail=None;calls=list(system.calls)
    assert lease.restore()==receipt and system.calls==calls


def test_unimplemented_timing_mode_rejected_before_source_or_mutation(monkeypatch):
    monkeypatch.setattr(control,'locked_materials',lambda *_:pytest.fail('config touched for unsupported mode'))
    with pytest.raises(ValueError):control.payload(types.SimpleNamespace(mode='timing'))
    with pytest.raises(ValueError):control.launch(types.SimpleNamespace(mode='timing'))


def test_functional_activation_missing_blocks_before_run_allocation(monkeypatch,tmp_path):
    monkeypatch.setitem(sys.modules,'bindings',bindings)
    monkeypatch.setattr(control,'HERE',tmp_path);monkeypatch.setattr(control,'ROOT',tmp_path)
    monkeypatch.setattr(control,'locked_materials',lambda *_:dict(qa_tag='qa'))
    def absent():raise FileNotFoundError('no actual qualified activation')
    monkeypatch.setattr(bindings,'activation',absent)
    monkeypatch.setattr(control,'storage_preflight',lambda *a:pytest.fail('preflight after unqualified activation'))
    with pytest.raises(FileNotFoundError):control.launch(types.SimpleNamespace(mode='functional',tag='x',name='material_01'))
    assert not (tmp_path/'runs').exists()


def test_storage_preflight_precedes_any_run_or_lease(monkeypatch,tmp_path):
    monkeypatch.setattr(control,'HERE',tmp_path);monkeypatch.setattr(control,'ROOT',tmp_path)
    monkeypatch.setattr(control,'locked_materials',lambda *_:dict(qa_tag='qa'))
    def fail(*args):raise RuntimeError('bad USB before lease')
    monkeypatch.setattr(control,'storage_preflight',fail)
    a=types.SimpleNamespace(mode='qa',tag='qa',commit='a'*40,name='qa_normal_01',qa_timeout=90)
    with pytest.raises(RuntimeError,match='USB'):control.launch(a)
    assert not (tmp_path/'runs').exists()


def test_score_padding_initialized_and_tensor_export_preserves_layout(tmp_path):
    scores=kernel.copy_layout(torch.arange(6*38,dtype=torch.float32).view(6,38)[:,4])
    extent=scores.storage_offset()+(len(scores)-1)*scores.stride()[0]+1
    full=scores.as_strided((extent,),(1,),0);padding=torch.ones(extent,dtype=torch.bool)
    padding[scores.storage_offset()+torch.arange(len(scores))*scores.stride()[0]]=False
    assert bool((full[padding]==0).all())
    case=dict(protos=torch.zeros(32,160,160),coefficients=torch.zeros(2,32),boxes=torch.zeros(2,4),shape=(640,640))
    material=dict(prediction=torch.zeros(1,116,7),mask_case=case,counts=dict(k=2,n_tau=6,kernel_n=6),
        kernel=dict(boxes=torch.zeros(6,4),scores=scores,keep=torch.arange(6),detections=torch.zeros(2,38),backend=lambda:None))
    row=exports.save(tmp_path,'000000000009','adv',material,'a'*64,dict(sha256='b'*64))
    loaded=torch.load(tmp_path/row['filename'],map_location='cpu',weights_only=True)
    assert 'backend' not in loaded['kernel'] and kernel.signature(loaded['kernel']['scores'])==kernel.signature(scores)
    assert torch.equal(loaded['kernel']['scores'],scores)
    before=(tmp_path/row['filename']).read_bytes()
    with pytest.raises(FileExistsError):exports.save(tmp_path,'000000000009','adv',material,'a'*64,dict(sha256='b'*64))
    assert (tmp_path/row['filename']).read_bytes()==before
