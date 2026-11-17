# Adapted from sponge-sim/tests/test_pi3b_nms_light.py:1-152
# SHA256 92edc9a357514f565098987a6bf2465e82660ed56ce76490ab7ae1dcf8d49254; old tests/source/data remain unchanged.
"""Synthetic clocks/counters only; never collect host operator performance."""
from pathlib import Path
import gc
import importlib.util
import sys
import types
import weakref

import pytest

P=Path(__file__).parents[1]/'studies/pi3b_nms_predecessor_20261115/bracket.py'
spec=importlib.util.spec_from_file_location('light_bracket',P)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
native_sample=b.sample


def counter(value=10):
    return dict(pid=11,calling_tid=12,process_cpu_ns=value,calling_thread_cpu_ns=value,
                process={k:value for k in b.FIELDS},calling_thread={k:value for k in b.FIELDS})


@pytest.fixture(autouse=True)
def synthetic_only(monkeypatch):
    original=gc.isenabled()
    monkeypatch.setattr(b.platform,'system',lambda:'Linux')
    monkeypatch.setattr(b,'_resource',object())
    clocks=iter([100,150]);monkeypatch.setattr(b.time,'perf_counter_ns',lambda:next(clocks))
    samples=iter([counter(10),counter(12)]);monkeypatch.setattr(b,'sample',lambda:next(samples))
    yield
    if original: gc.enable()
    else: gc.disable()


@pytest.mark.parametrize('instrumented',[False,True])
@pytest.mark.parametrize('gc_before',[False,True])
def test_wall_interval_output_identity_and_gc_preserved(instrumented,gc_before):
    if gc_before:gc.enable()
    else:gc.disable()
    output=[]
    def fn():
        assert not gc.isenabled()
        return output
    value,record=b.measure(fn,instrumented=instrumented)
    assert value is output and record['wall_ns']==50 and gc.isenabled()==gc_before
    if instrumented:
        assert record['increments']['calling_thread']['ru_majflt']==2
        assert record['increments']['observer_work_included']
    else:assert record['before'] is record['after'] is record['increments'] is None


def test_control_mode_never_reads_resources(monkeypatch):
    def forbidden():raise AssertionError('resource observer called in control')
    monkeypatch.setattr(b,'sample',forbidden)
    assert b.measure(lambda:42,instrumented=False)[0]==42


def test_output_alive_through_second_counter_sample(monkeypatch):
    class Output:pass
    holder={};reads=[]
    def fn():
        x=Output();holder['weak']=weakref.ref(x);return x
    def read():
        if reads:assert holder['weak']() is not None
        reads.append(1);return counter(10+len(reads))
    monkeypatch.setattr(b,'sample',read)
    value,record=b.measure(fn,instrumented=True)
    assert holder['weak']() is value and record['output_retained_through_all_endpoints']
    del value
    assert holder['weak']() is None


@pytest.mark.parametrize('gc_before',[False,True])
def test_operator_failure_propagates_and_restores_gc(gc_before):
    if gc_before:gc.enable()
    else:gc.disable()
    def fail():raise LookupError('injected')
    with pytest.raises(LookupError,match='injected'):b.measure(fail,instrumented=True)
    assert gc.isenabled()==gc_before


@pytest.mark.parametrize('point',[1,2])
def test_sampler_failure_never_converted_to_zero_or_success(monkeypatch,point):
    calls=[];executed=[]
    def read():
        calls.append(1)
        if len(calls)==point:raise OSError('injected resource failure')
        return counter()
    monkeypatch.setattr(b,'sample',read)
    with pytest.raises(OSError):b.measure(lambda:executed.append(1),instrumented=True)
    assert len(executed)==(1 if point==2 else 0)


@pytest.mark.parametrize('mutation',['pid','tid','clock','counter','missing','extra','boolean'])
def test_bad_identity_counter_schema_and_reversal_refused(mutation):
    a=counter();z=counter(12)
    if mutation=='pid':z['pid']+=1
    if mutation=='tid':z['calling_tid']+=1
    if mutation=='clock':z['process_cpu_ns']=9
    if mutation=='counter':z['calling_thread']['ru_majflt']=9
    if mutation=='missing':z['process'].pop('ru_minflt')
    if mutation=='extra':z['calling_thread']['invented']=0
    if mutation=='boolean':z['process']['ru_majflt']=False
    with pytest.raises(ValueError):b.increments(a,z)


def test_sequential_process_vs_thread_clock_differences_not_clamped():
    a=counter();z=counter(12);z['calling_thread_cpu_ns']=15
    d=b.increments(a,z)
    assert d['cpu_clocks']==dict(process_cpu_ns=2,calling_thread_cpu_ns=5)
    assert d['sequential_not_identical_clock_intervals'] and not d['unique_wait_cause_identified']


def test_reversed_wall_and_operator_gc_change_fail(monkeypatch):
    seq=iter([150,100]);monkeypatch.setattr(b.time,'perf_counter_ns',lambda:next(seq))
    with pytest.raises(ValueError,match='reversed'):b.measure(lambda:42,instrumented=False)
    seq=iter([100,150]);monkeypatch.setattr(b.time,'perf_counter_ns',lambda:next(seq))
    with pytest.raises(RuntimeError,match='GC'):b.measure(lambda:gc.enable(),instrumented=False)


@pytest.mark.parametrize('mode',[None,1,'yes'])
def test_mode_cannot_silently_coerce(mode):
    with pytest.raises(TypeError):b.measure(lambda:42,instrumented=mode)


def test_non_linux_refuses_before_call(monkeypatch):
    monkeypatch.setattr(b.platform,'system',lambda:'Windows')
    with pytest.raises(RuntimeError):b.measure(lambda:42,instrumented=False)


def test_counter_samples_remain_outside_wall_interval(monkeypatch):
    events=[]
    def sample():events.append('sample');return counter(10+len(events))
    def wall():events.append('wall');return len(events)
    def fn():events.append('call');return 42
    monkeypatch.setattr(b,'sample',sample);monkeypatch.setattr(b.time,'perf_counter_ns',wall)
    assert b.measure(fn,instrumented=True)[0]==42
    assert events==['sample','wall','call','wall','sample']


def test_real_sampler_shape_with_fake_linux_resource_api(monkeypatch):
    calls=[]
    def usage(which):
        calls.append(which);return types.SimpleNamespace(**{k:which for k in b.FIELDS})
    api=types.SimpleNamespace(RUSAGE_SELF=1,RUSAGE_THREAD=2,getrusage=usage)
    monkeypatch.setattr(b,'_resource',api)
    monkeypatch.setattr(b.os,'getpid',lambda:11)
    monkeypatch.setattr(b.threading,'get_native_id',lambda:12)
    monkeypatch.setattr(b.time,'process_time_ns',lambda:30)
    monkeypatch.setattr(b.time,'thread_time_ns',lambda:20)
    x=native_sample()
    assert calls==[1,2] and x['process']['ru_majflt']==1 and x['calling_thread']['ru_majflt']==2
    assert x['process_cpu_ns']==30 and x['calling_thread_cpu_ns']==20
    assert 'ru_maxrss' not in x['process']
