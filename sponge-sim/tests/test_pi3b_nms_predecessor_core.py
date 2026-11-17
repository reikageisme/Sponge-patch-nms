"""Prepared integration core: synthetic clocks and finite CPU function checks.

Real small torchvision/Ultralytics calls test extraction/parity only. No
latency/performance endpoints or model/weights/downloads are invoked.
"""
from pathlib import Path
import ast
import builtins
import collections
import gc
import hashlib
import importlib.util
import sys
import types
import weakref

import pytest
import torch

S=Path(__file__).parents[1]/'studies/pi3b_nms_predecessor_20261115'


def load(name):
    spec=importlib.util.spec_from_file_location('predecessor_'+name,S/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


b=load('bracket')
prior=sys.modules.get('bracket');sys.modules['bracket']=b
pairs=load('pairs')
if prior is None:del sys.modules['bracket']
else:sys.modules['bracket']=prior
k=load('kernel_input');sch=load('schedule')
saved={name:sys.modules.get(name) for name in ('cache','kernel_input','baseline_ops','preallocate')}
sys.modules['cache']=load('cache');sys.modules['kernel_input']=k
sys.modules['baseline_ops']=load('baseline_ops');sys.modules['preallocate']=load('preallocate')
material=load('material');factories=load('factories')
for name,old in saved.items():
    if old is None:del sys.modules[name]
    else:sys.modules[name]=old


@pytest.fixture
def fake_api(monkeypatch):
    api=types.SimpleNamespace(RUSAGE_SELF=0,RUSAGE_THREAD=1,
        getrusage=lambda mode:types.SimpleNamespace(**{x:0 for x in b.FIELDS}))
    monkeypatch.setattr(b.platform,'system',lambda:'Linux')
    monkeypatch.setattr(b,'_resource',None)
    monkeypatch.setitem(sys.modules,'resource',api)
    monkeypatch.setattr(b.time,'process_time_ns',lambda:100)
    monkeypatch.setattr(b.time,'thread_time_ns',lambda:100)
    return api


def test_explicit_initialization_required_before_any_predecessor(fake_api):
    ran=[]
    with pytest.raises(RuntimeError,match='setup'):b.sample()
    with pytest.raises(RuntimeError,match='setup'):b.measure(lambda:ran.append('target'),instrumented=False)
    with pytest.raises(RuntimeError,match='setup'):pairs.execute(lambda:ran.append('pred'),lambda:None,instrumented=False)
    assert not ran
    b.setup_resources();assert b._resource is fake_api
    with pytest.raises(RuntimeError,match='already'):b.setup_resources()


def test_no_import_or_explicit_file_api_in_initialized_sampler_path(fake_api,monkeypatch):
    b.setup_resources()
    def forbidden(*args,**kwargs):raise AssertionError('import/file API after initialization')
    with monkeypatch.context() as scoped:
        scoped.setattr(builtins,'open',forbidden);scoped.setattr(builtins,'__import__',forbidden)
        a=b.sample();z=b.sample();d=b.increments(a,z)
    assert d['observer_work_included']
    tree=ast.parse((S/'bracket.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name!='setup_resources':
            assert not any(isinstance(x,(ast.Import,ast.ImportFrom)) for x in ast.walk(node))


@pytest.mark.parametrize('enabled',[False,True])
def test_immediate_pair_releases_predecessor_and_keeps_target_through_endpoints(fake_api,monkeypatch,enabled):
    b.setup_resources();original=gc.isenabled();events=[];refs={}
    class Output:
        def __init__(self,label):self.label=label
        def __del__(self):events.append(self.label+'_released')
    def predecessor():
        assert not gc.isenabled();events.append('pred');return Output('pred')
    def target():
        assert 'pred_released' in events and not gc.isenabled()
        events.append('target');x=Output('target');refs['target']=weakref.ref(x);return x
    def measured(fn,*,instrumented):
        assert events==['pred','pred_released'];events.append('wall_start')
        x=fn();events.append('wall_end');assert refs['target']() is x
        events.append('counter_end');return x,dict(synthetic=True)
    monkeypatch.setattr(b,'measure',measured)
    try:
        gc.enable() if enabled else gc.disable()
        result,record=pairs.execute(predecessor,target,instrumented=True)
        assert gc.isenabled()==enabled and refs['target']() is result and record['synthetic']
        assert events==['pred','pred_released','wall_start','target','wall_end','counter_end']
        del result;assert events[-1]=='target_released'
    finally:gc.enable() if original else gc.disable()


def test_pair_failure_does_not_call_target_or_leave_gc_changed(fake_api):
    b.setup_resources();original=gc.isenabled();ran=[]
    def fail():raise LookupError('predecessor failed')
    with pytest.raises(LookupError):pairs.execute(fail,lambda:ran.append(1),instrumented=False)
    assert not ran and gc.isenabled()==original
    with pytest.raises(RuntimeError,match='GC'):pairs.execute(lambda:gc.enable(),lambda:ran.append(1),instrumented=False)
    assert not ran and gc.isenabled()==original


def test_schedule_exact_factorial_and_subset_master_seed():
    full=sch.schedule(sch.IMAGE_IDS);smoke=sch.schedule([sch.IMAGE_IDS[0],sch.IMAGE_IDS[2]])
    assert len(full)==3600 and len(smoke)==360
    for image in sch.IMAGE_IDS:
        selected=[x for x in full if x['image']==image]
        counts=collections.Counter((x['predecessor'],x['target'],x['observer'],x['copy']) for x in selected)
        assert len(counts)==36 and set(counts.values())=={5}
        for rep in range(5):assert len([x for x in selected if x['rep']==rep])==36
    rows=lambda xs,image:[{a:b for a,b in x.items() if a!='index'} for x in xs if x['image']==image]
    assert rows(full,sch.IMAGE_IDS[2])==rows(smoke,sch.IMAGE_IDS[2])
    for ids in ([],['unknown'],[sch.IMAGE_IDS[0]]*2,list(reversed(sch.IMAGE_IDS))):
        with pytest.raises(ValueError):sch.schedule(ids)


def test_strided_scores_copy_preserves_storage_offset_and_values():
    matrix=torch.arange(6*38,dtype=torch.float32).view(6,38)
    scores=matrix[:,4];copied=k.copy_layout(scores)
    assert scores.stride()==(38,) and scores.storage_offset()==4
    assert k.signature(copied)==k.signature(scores) and torch.equal(copied,scores)
    copied[0]=-1;assert scores[0]!=-1
    assert k.signature(scores.contiguous())!=k.signature(scores)


@pytest.fixture
def real_backend(tmp_path,monkeypatch):
    monkeypatch.setenv('YOLO_OFFLINE','true');monkeypatch.setenv('YOLO_AUTOINSTALL','false')
    config=tmp_path/'ultralytics';config.mkdir()
    monkeypatch.setenv('YOLO_CONFIG_DIR',str(config))
    import torchvision
    from ultralytics.utils import nms
    return nms,torchvision.ops


def prediction():
    x=torch.zeros((1,116,7),dtype=torch.float32)
    x[0,:4]=torch.tensor([[20,21,100,200,300,400,500],[20,21,100,200,300,400,500],[10,10,15,20,20,30,30],[10,10,15,20,20,30,30]])
    for j in range(7):x[0,4+j%2,j]=.95-j*.05
    x[0,84:,:]=torch.arange(32,dtype=torch.float32)[:,None]/32
    return x


def test_real_finite_kernel_input_and_full_detection_parity(real_backend):
    nms,ops=real_backend;original=ops.nms;x=prediction();before=x.clone()
    result=k.capture(x,nms,ops)
    assert ops.nms is original and torch.equal(x,before)
    assert result['n_kernel']==7 and 0<result['n_retained']<=7
    assert k.signature(result['scores'])==result['original_score_layout']
    assert result['original_score_layout']['stride']==[38]
    assert len(result['content_sha256']['detections'])==64
    assert result['finite_parity_only'] and result['kernel_call_is_not_bare_cpp']


def test_six_anchor_shortcut_without_true_kernel_is_rejected(real_backend):
    nms,ops=real_backend;original=ops.nms
    with pytest.raises(ValueError,match='missing'):k.capture(prediction()[:,:,:6],nms,ops)
    assert ops.nms is original


def test_kernel_keeps_uncapped_indices_while_wrapper_caps_outputs(real_backend):
    nms,ops=real_backend
    x=torch.zeros((1,116,320),dtype=torch.float32)
    index=torch.arange(320)
    x[0,0]=(index%20)*20+10;x[0,1]=(index//20)*20+10
    x[0,2:4]=2;x[0,4]=.95-index.float()/10000
    result=k.capture(x,nms,ops)
    assert result['n_kernel']==result['n_keep_uncapped']==320
    assert result['n_retained']==300 and len(result['detections'])==300
    assert len(result['keep'])==320 and result['scores'].stride()==(38,)


@pytest.mark.parametrize('kind',['half','nan','broadcast','offset','gradient'])
def test_kernel_layout_validation_rejects_unsupported_inputs(kind):
    if kind=='half':x=torch.ones(3,dtype=torch.float16)
    if kind=='nan':x=torch.tensor([float('nan')])
    if kind=='broadcast':x=torch.ones(1).expand(3)
    if kind=='offset':x=torch.ones(128).as_strided((3,),(1,),117)
    if kind=='gradient':x=torch.ones(3,requires_grad=True)
    with pytest.raises(ValueError):k.copy_layout(x)


@pytest.mark.parametrize('error',['before','after','double','none'])
def test_interception_always_restored_and_bad_kernel_call_count_refused(real_backend,error):
    nms,ops=real_backend;original=ops.nms
    def wrapper(prediction,**kwargs):
        if error=='before':raise LookupError('before backend')
        if error=='none':return [torch.empty((0,38))]
        boxes=torch.tensor([[0,0,10,10]],dtype=torch.float32);scores=torch.tensor([.9])
        ops.nms(boxes,scores,.45)
        if error=='after':raise LookupError('after backend')
        ops.nms(boxes,scores,.45)
    fake=types.SimpleNamespace(non_max_suppression=wrapper)
    with pytest.raises((LookupError,ValueError)):k.capture(prediction(),fake,ops)
    assert ops.nms is original


def test_renderer_and_cache_function_asts_remain_qualified():
    old=S.parent/'pi3b_renderer_memory_usb_20261115'
    for name in ('baseline_ops.py','preallocate.py','cache.py'):
        assert ast.dump(ast.parse((S/name).read_text(encoding='utf-8')))==ast.dump(ast.parse((old/name).read_text(encoding='utf-8')))


def toy_material(real_backend):
    nms,ops=real_backend;x=prediction();proto=torch.zeros((1,32,160,160),dtype=torch.float32)
    det=k.suppress(nms,x.clone())
    case=dict(protos=proto[0].clone(),coefficients=det[:,6:].contiguous(),boxes=det[:,:4].contiguous(),shape=(640,640))
    row=dict(k=len(det),counts=dict(k=len(det),n_tau=7,kernel_n=7))
    return (x,dict(prototype=proto)),case,row


def test_fresh_material_requires_exact_cached_tensor_and_count_parity(real_backend):
    raw,case,row=toy_material(real_backend);nms,ops=real_backend
    result=material.prepare(raw,case,row,nms,ops)
    assert result['fresh_frozen_tensor_parity'] and result['counts']==row['counts']
    bad=dict(case);bad['protos']=case['protos']+1
    with pytest.raises(ValueError,match='tensor content'):material.prepare(raw,bad,row,nms,ops)
    badrow=dict(row,counts=dict(row['counts'],n_tau=8))
    with pytest.raises(ValueError,match='counts'):material.prepare(raw,case,badrow,nms,ops)


def test_model_output_traversal_refuses_ambiguity_but_deduplicates_aliases():
    pred=prediction();proto=torch.zeros((1,32,160,160))
    p,q=material.prediction_proto((pred,pred,dict(proto=proto)))
    assert p is pred and torch.equal(q,proto[0])
    with pytest.raises(ValueError,match='ambiguous'):material.prediction_proto((pred,pred.clone(),proto))
    with pytest.raises(ValueError):material.prediction_proto((pred,dict(unexpected=42)))


@pytest.mark.parametrize('part',['prediction','prototype'])
def test_material_rejects_autograd_before_kernel_capture(real_backend,monkeypatch,part):
    raw,case,row=toy_material(real_backend);nms,ops=real_backend
    tensor=raw[0] if part=='prediction' else raw[1]['prototype']
    tensor.requires_grad_(True)
    def forbidden(*args):raise AssertionError('kernel capture reached with retained graph')
    monkeypatch.setattr(material,'capture',forbidden)
    with pytest.raises(ValueError,match='autograd'):material.prepare(raw,case,row,nms,ops)


def test_factories_prepare_clones_before_pair_and_replay_true_inputs(real_backend):
    raw,case,row=toy_material(real_backend);nms,ops=real_backend
    m=material.prepare(raw,case,row,nms,ops)
    before=m['prediction'].clone()
    wrapper=factories.target(m,'wrapper',nms);kernel=factories.target(m,'kernel_call',nms)
    assert torch.equal(wrapper(),m['kernel']['detections'])
    assert torch.equal(kernel(),m['kernel']['keep'])
    assert factories.target(m,'sham',nms)() is None
    assert torch.equal(factories.predecessor(m,'nms_reference',nms)(),m['kernel']['detections'])
    assert torch.equal(before,m['prediction'])
    for fn in (factories.target,factories.predecessor):
        with pytest.raises(ValueError):fn(m,'unknown',nms)


def test_mask_factories_keep_exact_output_parity_on_small_functional_case():
    gen=torch.Generator().manual_seed(20261115)
    case=dict(protos=torch.randn((4,5,7),generator=gen),coefficients=torch.randn((3,4),generator=gen),
              boxes=torch.tensor([[0,0,17,13],[-1,-1,18,14],[3,2,9,8]],dtype=torch.float32),shape=(13,17))
    m=dict(mask_case=case)
    a=factories.predecessor(m,'native32M',None)()
    z=factories.predecessor(m,'candidate16M',None)()
    assert torch.equal(a,z) and tuple(a.shape)==(3,13,17)
