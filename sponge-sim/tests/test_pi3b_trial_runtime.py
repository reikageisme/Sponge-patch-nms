"""Synthetic clocks/counters/outputs only; never load model or run device work."""
import ast
import copy
from contextlib import contextmanager
import gc
import importlib.util
import json
from pathlib import Path
import sys
import types
import weakref

import pytest

S=Path(__file__).parents[1]/'studies/pi3b_nms_trial_runtime_20261115'
CORE=S.parent/'pi3b_nms_predecessor_20261115'
spec=importlib.util.spec_from_file_location('_trial_prepared',S/'__init__.py',submodule_search_locations=[str(S)])
package=importlib.util.module_from_spec(spec);sys.modules[spec.name]=package;spec.loader.exec_module(package)
from _trial_prepared import reference as ref,sentry,engine


class Output:pass


def raw_measure(ns=100):
    return dict(wall_ns=ns,counter_status='NOT_RECORDED',before=None,after=None,increments=None,
        output_retained_through_all_endpoints=True)


def pool():
    threads={str(t):dict(status='OK',affinity=[0,1,2,3],stat=dict(start_ticks=t,minflt=0,majflt=0,utime_ticks=0,stime_ticks=0),
        thread_status=dict(voluntary_ctxt_switches=0,nonvoluntary_ctxt_switches=0)) for t in (11,12)}
    return dict(pid=11,start_ticks=11,cgroup_path='/system.slice/owned.service',threads=threads,
        tids_before=[11,12],tids_after=[11,12],complete_stable_set=True,
        cgroup_ancestors=[dict(path='/',files={k:dict(status='UNAVAILABLE',error='FileNotFoundError')
            for k in ('cpu.max','cpu.weight','memory.max','memory.high')})])


tree=ast.parse((CORE/'inventory.py').read_text());node=next(n for n in tree.body if getattr(n,'name',None)=='increments')
scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(CORE/'inventory.py'),'exec'),scope)
pool_increments=scope['increments']  # Actual frozen PURE validator, fake frames.


def test_schedule_copy_ast_unchanged():
    assert ast.dump(ast.parse((S/'schedule.py').read_text()))==ast.dump(ast.parse((CORE/'schedule.py').read_text()))


def test_reference_baseline_samples_and_output_release():
    outputs=[];rows=[];durations=iter([100,110,105]);guards=[]
    def forward():
        out=Output();outputs.append(weakref.ref(out));return out
    def measure(fn,*,instrumented):
        assert instrumented is False
        out=fn();assert outputs[-1]() is out
        return out,raw_measure(next(durations))
    def guard(label):
        guards.append(label)
        if label.endswith('post'):assert outputs[-1]() is None
    baseline,row=ref.reference(forward,label='start',baseline_ns=None,measure=measure,guard=guard,emit=rows.append)
    assert baseline==105 and row['ratio']==1 and not row['flagged']
    assert len(outputs)==4 and len([r for r in rows if r['kind']=='reference_sample'])==3
    assert all(x() is None for x in outputs)


@pytest.mark.parametrize('autograd',[False,True])
def test_global_warmup_pipeline_binds_exact_operations_without_a_new_model(autograd):
    events=[];pred=types.SimpleNamespace(requires_grad=autograd);proto=types.SimpleNamespace(requires_grad=False)
    class Detections:
        def __getitem__(self,key):return 'coefficients' if key[1].start==6 else 'boxes'
    def net(image):events.append('forward');return 'fake_raw'
    def suppress(nms,value):
        assert nms=='fixed_nms' and value is pred;events.append('nms');return Detections()
    def masks(p,c,b,shape):
        assert p is proto and c=='coefficients' and b=='boxes' and shape==(640,640)
        events.append('native_mask');return Output()
    core=types.SimpleNamespace(material=types.SimpleNamespace(prediction_proto=lambda raw:(pred,proto)),
        kernel_input=types.SimpleNamespace(suppress=suppress),baseline_ops=types.SimpleNamespace(process_mask_native=masks))
    if autograd:
        with pytest.raises(ValueError):ref.baseline_pipeline(net,'fixed_reference','fixed_nms',core)
        assert events==['forward']
    else:
        assert isinstance(ref.baseline_pipeline(net,'fixed_reference','fixed_nms',core),Output)
        assert events==['forward','nms','native_mask']


@pytest.mark.parametrize('bad',[0,-1,True,float('nan')])
def test_bad_reference_baseline_stops_before_work(bad):
    def forbidden(*a,**k):pytest.fail('invalid baseline cannot trigger a warmup/measurement')
    with pytest.raises(ValueError):ref.reference(forbidden,label='start',baseline_ns=bad,measure=forbidden,guard=forbidden,emit=forbidden)


@pytest.mark.parametrize('bad',[0,2,-1,True])
def test_warmup_count_fixed_before_work(bad):
    with pytest.raises(ValueError):ref.warmup(lambda:pytest.fail('no work'),bad,label='global',guard=lambda *_:None,emit=lambda *_:None)


@pytest.mark.parametrize('fault',['post_guard','measure','zero'])
def test_reference_failure_keeps_completed_prefix_without_retry(fault):
    rows=[];calls=[]
    def measure(fn,**kwargs):
        calls.append(1)
        if fault=='measure':raise RuntimeError('fake operator failure')
        return Output(),raw_measure(0 if fault=='zero' else 100)
    def guard(label):
        if fault=='post_guard' and label=='reference_post':raise RuntimeError('fake physical stop')
    with pytest.raises((ValueError,RuntimeError)):
        ref.reference(lambda:Output(),label='start',baseline_ns=None,measure=measure,guard=guard,emit=rows.append)
    assert len(calls)==1 and not any(r['kind']=='reference' for r in rows)
    if fault=='post_guard':assert rows[-1]['measurement']['wall_ns']==100 and not rows[-1]['post_guard_ok']
    elif fault=='measure':assert rows[-1]['kind']=='reference_failed' and rows[-1]['measurement'] is None
    else:assert not rows[-1]['valid']


def reference_series(flagged=0):
    rows=[];baseline=None
    for ix,label in enumerate(['start','before_000000000009','before_000000000030','end']):
        ns=104 if 0<ix<=flagged else 100
        baseline,_=ref.reference(lambda:Output(),label=label,baseline_ns=baseline,
            measure=lambda fn,**kwargs:(fn(),raw_measure(ns)),guard=lambda *_:None,emit=rows.append)
    return rows


def test_reference_all_flags_retained_and_complete_cadence_required():
    ids=['000000000009','000000000030']
    assert ref.reference_gate(reference_series(2),ids)['reference_pass']
    result=ref.reference_gate(reference_series(3),ids)
    assert result['reference_flags']==3 and not result['reference_pass'] and not result['campaign_quality_assessed']


@pytest.mark.parametrize('fault',['missing','duplicate','reorder','baseline','flag','missing_sample','bad_sample','failed_post'])
def test_reference_summary_cannot_rescue_missing_or_bad_raw_trace(fault):
    rows=reference_series(1);summaries=[r for r in rows if r['kind']=='reference']
    if fault=='missing':rows.remove(summaries[-1])
    elif fault=='duplicate':rows.append(copy.deepcopy(summaries[-1]))
    elif fault=='reorder':
        first,second=rows.index(summaries[0]),rows.index(summaries[1])
        rows[first],rows[second]=rows[second],rows[first]
    elif fault=='baseline':summaries[1]['baseline_ns']=104
    elif fault=='flag':summaries[1]['flagged']=False
    elif fault=='missing_sample':rows.pop(next(i for i,r in enumerate(rows) if r['kind']=='reference_sample'))
    elif fault=='bad_sample':next(r for r in rows if r['kind']=='reference_sample')['measurement']['wall_ns']=101
    elif fault=='failed_post':next(r for r in rows if r['kind']=='reference_sample')['post_guard_ok']=False
    with pytest.raises(ValueError):ref.reference_gate(rows,['000000000009','000000000030'])


def cpu_row(**kwargs):return {k:kwargs.get(k,0.) for k in sentry.FIELDS}


def test_guest_time_not_double_counted():
    before=[cpu_row() for _ in range(4)]
    after=[cpu_row(user=80,nice=20,idle=100,guest=80,guest_nice=20) for _ in range(4)]
    assert sentry.busy_fractions(before,after)==[.5]*4


@pytest.mark.parametrize('fault',['zero','reverse','missing','topology'])
def test_cpu_frames_do_not_turn_unavailable_or_reversed_counters_into_zero(fault):
    before=[cpu_row() for _ in range(4)];after=[cpu_row(user=3) for _ in range(4)]
    if fault=='zero':after=copy.deepcopy(before)
    elif fault=='reverse':after[0]['iowait']=-1
    elif fault=='missing':del after[0]['guest']
    elif fault=='topology':after.pop()
    with pytest.raises(ValueError):sentry.busy_fractions(before,after)


@pytest.fixture
def fake_sentry(monkeypatch,tmp_path):
    before=pool();after=copy.deepcopy(before);row0=[cpu_row() for _ in range(4)];row1=[cpu_row(user=3) for _ in range(4)]
    pool_values=iter([before,after]);frames_values=iter([row0,row1]);rows=[];calls=[];outputs=[]
    online=tmp_path/'online';online.write_text('0-3\n');monkeypatch.setattr(sentry,'ONLINE',online)
    wall_values=iter([0,1,1_000_000_000,3_000_000_000,3_000_000_000])
    cpu_values=iter([1000,9_000_001_000])
    monkeypatch.setattr(sentry.time,'perf_counter_ns',lambda:next(wall_values))
    monkeypatch.setattr(sentry.time,'process_time_ns',lambda:next(cpu_values))
    def times(*,percpu):
        assert percpu is True
        return [types.SimpleNamespace(_asdict=lambda row=row:row) for row in next(frames_values)]
    def work():
        calls.append(1);out=Output();outputs.append(weakref.ref(out));return out
    return types.SimpleNamespace(before=before,after=after,row0=row0,row1=row1,rows=rows,calls=calls,outputs=outputs,work=work,times=times,
        inventory=types.SimpleNamespace(snapshot=lambda:next(pool_values),increments=pool_increments))


def run_sentry(c,guard=lambda *_:None):
    return sentry.run(c.work,label='pin_start',inventory=c.inventory,cpu_times=c.times,guard=guard,emit=c.rows.append)


def test_actual_load_sentry_with_fake_apis_checks_self_cpu_not_just_system(fake_sentry):
    c=fake_sentry;result=run_sentry(c)
    assert result['passed'] and result['inside_cpu_equivalents']==4 and result['process_cpu_over_wall']==3
    assert result['iterations']==2 and len(c.calls)==3 and all(w() is None for w in c.outputs)
    assert not result['all_four_threads_simultaneously_in_nms_proven'] and not result['campaign_quality_assessed']
    assert result['before_pool']['cgroup_ancestors'][0]['files']['memory.max']['status']=='UNAVAILABLE'


@pytest.mark.parametrize('fault',['background_only','system_not_busy','late_tid','reused_tid','wrong_affinity','changed_quota','post_guard'])
def test_sentry_cannot_borrow_background_cpu_or_filter_changed_threads(fake_sentry,monkeypatch,fault):
    c=fake_sentry
    if fault=='background_only':
        values=iter([1000,1_000_001_000]);monkeypatch.setattr(sentry.time,'process_time_ns',lambda:next(values))
    elif fault=='system_not_busy':
        for row in c.row1:row.update(user=.3,idle=2.7)
    elif fault=='late_tid':
        c.after['threads']['13']=copy.deepcopy(c.after['threads']['12']);c.after['tids_before'].append(13);c.after['tids_after'].append(13)
    elif fault=='reused_tid':c.after['threads']['12']['stat']['start_ticks']=99
    elif fault=='wrong_affinity':c.after['threads']['12']['affinity']=[0]
    elif fault=='changed_quota':c.after['cgroup_ancestors'][0]['files']['cpu.max']={'status':'OK','text':'100000 100000'}
    def guard(label):
        if fault=='post_guard' and label=='pin_post_load':raise RuntimeError('fake stop')
    with pytest.raises((ValueError,RuntimeError)):run_sentry(c,guard)
    assert c.rows[-1]['passed'] is False and c.rows[-1]['not_nms_endpoint']


def test_failed_load_keeps_null_unfinished_endpoints_without_retry(fake_sentry):
    c=fake_sentry;calls=[]
    def fail():
        calls.append(1)
        if len(calls)==2:raise RuntimeError('fake operator error')
        return Output()
    c.work=fail
    with pytest.raises(RuntimeError):run_sentry(c)
    assert len(calls)==2 and c.rows[-1]['kind']=='pin_load_failed'
    assert c.rows[-1]['wall_end_ns'] is None and c.rows[-1]['process_cpu_end_ns'] is None


def test_fixed_mm_preparation_refuses_wrong_thread_or_grad_context():
    calls=[]
    torch=types.SimpleNamespace(get_num_threads=lambda:1,get_num_interop_threads=lambda:1,is_inference_mode_enabled=lambda:True,
        ones=lambda *a,**k:calls.append(1),float32='float32')
    with pytest.raises(ValueError):sentry.prepare_mm(torch)
    assert calls==[]
    class Tensor:
        def __matmul__(self,other):assert other is self;return 256
    def ones(shape,**kwargs):
        calls.append((shape,kwargs));return Tensor()
    torch.get_num_threads=lambda:4;torch.ones=ones
    work=sentry.prepare_mm(torch);assert work()==256 and len(calls)==1


@pytest.fixture
def trial_context(monkeypatch):
    events=[];controls=[];trials=[];outputs=[];pred_outputs=[];calls=[];snapshots=iter([pool(),pool()])
    def measure(fn,*,instrumented):
        events.append('measure');out=fn();outputs.append(weakref.ref(out));return out,raw_measure()
    bracket=types.SimpleNamespace(require_setup=lambda:None,measure=measure)
    monkeypatch.setitem(sys.modules,'bracket',bracket)
    spec=importlib.util.spec_from_file_location('frozen_pair_for_trial_test',CORE/'pairs.py')
    pairs=importlib.util.module_from_spec(spec);spec.loader.exec_module(pairs)
    def prepare(p,t):
        events.append('prepare');calls.append((p,t))
        def predecessor():
            assert not gc.isenabled();events.append('predecessor');out=Output();pred_outputs.append(weakref.ref(out));return out
        def target():
            assert not gc.isenabled() and pred_outputs[-1]() is None
            events.append('target');return Output()
        return predecessor,target
    def guard(label):
        events.append('guard_'+label)
        if label.endswith('post'):assert outputs[-1]() is None
    def control(row):events.append('emit_control');controls.append(row)
    def trial(row):
        assert outputs[-1]() is None and set(row)=={'trial','measurement'}
        events.append('emit_trial');trials.append(row)
    def snapshot():events.append('snapshot');return next(snapshots)
    return types.SimpleNamespace(events=events,controls=controls,trials=trials,outputs=outputs,calls=calls,prepare=prepare,
        pair=pairs.execute,guard=guard,emit_control=control,emit_trial=trial,
        inventory=types.SimpleNamespace(snapshot=snapshot,increments=pool_increments))


def run_image(c,phase='smoke',image=None,jobs=None):
    image=image or engine.IMAGE_IDS[2]
    ids=engine.IMAGE_IDS if phase=='full' else (engine.IMAGE_IDS[0],engine.IMAGE_IDS[2])
    if jobs is None:jobs=[j for j in engine.schedule(ids) if j['image']==image]
    return engine.run_image(image,jobs,phase,prepare_pair=c.prepare,execute_pair=c.pair,guard=c.guard,inventory=c.inventory,
        emit_control=c.emit_control,emit_trial=c.emit_trial)


@pytest.mark.parametrize('phase,first_index',[('smoke',180),('full',360)])
def test_engine_preserves_master_indices_pair_gap_and_output_lifetime(trial_context,phase,first_index):
    c=trial_context;run_image(c,phase)
    assert len(c.trials)==180 and c.trials[0]['trial']['index']==first_index
    assert len(c.calls)==198 and len([x for x in c.controls if x['kind']=='pair_warmup'])==18
    assert c.controls[-1]['kind']=='image_complete'
    for i,event in enumerate(c.events):
        if event=='predecessor':assert c.events[i+1:i+3]==['measure','target']
    assert all(w() is None for w in c.outputs)


@pytest.mark.parametrize('fault',['missing','reorder','renumber','bool_index','foreign_image'])
def test_engine_refuses_bad_schedule_before_any_callback(trial_context,fault):
    c=trial_context;ids=(engine.IMAGE_IDS[0],engine.IMAGE_IDS[2]);jobs=[j for j in engine.schedule(ids) if j['image']==ids[1]]
    if fault=='missing':jobs.pop()
    elif fault=='reorder':jobs[0],jobs[1]=jobs[1],jobs[0]
    elif fault=='renumber':jobs[0]['index']=0
    elif fault=='bool_index':jobs[0]['rep']=False
    elif fault=='foreign_image':jobs[0]['image']=engine.IMAGE_IDS[1]
    with pytest.raises(ValueError):run_image(c,jobs=jobs)
    assert c.events==[]


def test_completed_trial_preserved_when_post_guard_fails(trial_context):
    c=trial_context;original=c.guard
    def guard(label):
        original(label)
        if label=='trial_post':raise RuntimeError('fake physical stop')
    c.guard=guard
    with pytest.raises(RuntimeError):run_image(c)
    assert len(c.trials)==1 and c.trials[0]['measurement']['wall_ns']==100
    assert c.controls[-1]['kind']=='trial_post_failed' and len(c.calls)==19


def test_operator_failure_never_becomes_zero_or_retried(trial_context):
    c=trial_context;pair=c.pair;count=[]
    def execute(*args,**kwargs):
        count.append(1)
        if len(count)==19:raise RuntimeError('fake target error')
        return pair(*args,**kwargs)
    c.pair=execute
    with pytest.raises(RuntimeError):run_image(c)
    assert len(count)==19 and c.trials==[]
    assert c.controls[-1]['kind']=='trial_failed' and c.controls[-1]['measurement'] is None


def test_pool_change_after_complete_block_preserves_all_trials_but_no_completion(trial_context):
    c=trial_context
    def fail(*args):raise ValueError('fake TID churn')
    c.inventory.increments=fail
    with pytest.raises(ValueError):run_image(c)
    assert len(c.trials)==180 and not any(r['kind']=='image_complete' for r in c.controls)


def test_full20_engine_rows_feed_strict_numerical_audit_without_qualification(trial_context):
    """End-to-end schema/schedule with fake operators/endpoints; no data file."""
    c=trial_context;count=0;original=c.pair
    def pair(*args,instrumented):
        nonlocal count
        output,_=original(*args,instrumented=instrumented);count+=1
        def sample(value):
            return dict(pid=11,calling_tid=12,process_cpu_ns=value,calling_thread_cpu_ns=value,
                process={k:value for k in ('ru_minflt','ru_majflt','ru_nvcsw','ru_nivcsw')},
                calling_thread={k:value for k in ('ru_minflt','ru_majflt','ru_nvcsw','ru_nivcsw')})
        before=sample(count*10) if instrumented else None;after=sample(count*10+2) if instrumented else None
        raw=dict(wall_start_ns=count*1000,wall_end_ns=count*1000+100,wall_ns=100,
            counter_status='RECORDED' if instrumented else 'NOT_RECORDED',before=before,after=after,
            increments=dict(cpu_clocks=dict(process_cpu_ns=2,calling_thread_cpu_ns=2),
                process={k:2 for k in before['process']},calling_thread={k:2 for k in before['calling_thread']},
                observer_work_included=True,sequential_not_identical_clock_intervals=True,unique_wait_cause_identified=False) if instrumented else None,
            output_retained_through_all_endpoints=True,procfs_or_cgroup_reads=False,
            interval='perf_counter_ns readings around callable; not bare C++ instruction time')
        return output,raw
    c.pair=pair;c.inventory.snapshot=pool
    for image in engine.IMAGE_IDS:run_image(c,'full',image)
    analysis=S.parent/'pi3b_nms_predecessor_analysis_20261115'
    spec=importlib.util.spec_from_file_location('_trial_schema_analysis',analysis/'__init__.py',submodule_search_locations=[str(analysis)])
    pkg=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pkg;spec.loader.exec_module(pkg)
    from _trial_schema_analysis.analyze import audit_rows
    result=audit_rows(c.trials,'full')
    assert len(c.trials)==3600 and count==3960 and result['numerical_schema_pass']
    assert not result['campaign_quality_assessed'] and not result['scientific_registration_verified']


@pytest.mark.parametrize('phase,n_images,n_global',[('smoke',2,1),('full',20,3)])
def test_session_full_cadence_and_material_lifetime_without_native_work(trial_context,monkeypatch,phase,n_images,n_global):
    c=trial_context;c.inventory.snapshot=pool;active=[];released=[];events=[];global_calls=[];materials_refs=[]
    def pin(workload,*,label,**kwargs):
        assert not active and all(w() is None for w in materials_refs)
        events.append(label);return {'passed':True}
    monkeypatch.setattr(engine.sentry,'run',pin)  # The sentry itself has fake-clock tests above.
    @contextmanager
    def materials(image):
        assert not active;active.append(image);events.append('enter_'+image)
        material=Output();materials_refs.append(weakref.ref(material))
        def make_pair(p,t):
            assert material is not None
            return c.prepare(p,t)
        try:yield make_pair
        finally:released.append(active.pop());events.append('exit_'+image)
    def forward():
        assert not active  # Never forward reference while material buffers are retained.
        assert all(w() is None for w in materials_refs)
        events.append('reference_forward');out=Output();c.outputs.append(weakref.ref(out));return out
    def measure(fn,*,instrumented):assert not instrumented;return fn(),raw_measure()
    def global_pipeline():
        global_calls.append(1);assert not active
        out=Output();c.outputs.append(weakref.ref(out));return out
    engine.run_session(phase,global_pipeline=global_pipeline,forward_reference=forward,prepare_image=materials,
        execute_pair=c.pair,measure=measure,guard=c.guard,inventory=c.inventory,cpu_times=lambda **kw:pytest.fail('mock sentry owns clocks'),
        prepare_pin_workload=lambda:lambda:Output(),emit_control=c.emit_control,emit_trial=c.emit_trial)
    assert len(global_calls)==n_global and len(released)==n_images and len(c.trials)==180*n_images
    refs=[r for r in c.controls if r['kind']=='reference']
    assert len(refs)==n_images+2 and all(r['baseline_ns']==100 for r in refs)
    assert events[0]=='pin_start' and events[-1]=='pin_end'
    assert c.controls[-1]['kind']=='session_control_sequence_complete'
    assert not c.controls[-1]['model_material_source_and_campaign_quality_qualified']


def test_session_material_context_releases_on_target_failure(trial_context,monkeypatch):
    c=trial_context;active=[];released=[];calls=[]
    monkeypatch.setattr(engine.sentry,'run',lambda *a,**k:None)
    @contextmanager
    def materials(image):
        active.append(image)
        try:yield c.prepare
        finally:released.append(active.pop())
    def fail(*args,**kwargs):calls.append(1);raise RuntimeError('fake warmup failure')
    with pytest.raises(RuntimeError):
        engine.run_session('smoke',global_pipeline=lambda:Output(),forward_reference=lambda:Output(),prepare_image=materials,
            execute_pair=fail,measure=lambda fn,**kw:(fn(),raw_measure()),guard=lambda *_:None,inventory=c.inventory,
            cpu_times=None,prepare_pin_workload=lambda:None,emit_control=c.emit_control,emit_trial=c.emit_trial)
    assert not active and len(released)==len(calls)==1
    assert not any(r['kind']=='session_control_sequence_complete' for r in c.controls)
