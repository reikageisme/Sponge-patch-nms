"""Synthetic counter/ownership cases, no actual trace/model/performance endpoint."""
from pathlib import Path
import copy
import importlib.util
import pytest

P=Path(__file__).parents[1]/'studies/pi3b_nms_trace_20261114/counters.py'
spec=importlib.util.spec_from_file_location('nms_counter_reader',P);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


def stat(pid,ticks):return f'{pid} (comm with ) odd chars) '+' '.join(['S']+['0']*18+[str(ticks)])


def test_proc_birth_handles_spaces_and_closing_parenthesis():
    assert c.birth(stat(12,987),12)==987
    with pytest.raises(ValueError):c.birth(stat(12,987),13)
    with pytest.raises(ValueError):c.birth('12 (short) S 0',12)


def test_unified_group_cannot_traverse_or_escape(tmp_path):
    raw,p=c.unified_group('0::/system.slice/owned.service\n',tmp_path)
    assert p==tmp_path/'system.slice/owned.service' and raw=='/system.slice/owned.service'
    with pytest.raises(ValueError):c.unified_group('0::/../outside',tmp_path)
    with pytest.raises(ValueError):c.unified_group('0::/a\n0::/b',tmp_path)


def test_missing_optional_counter_is_not_zero(tmp_path):
    value=c.optional(tmp_path/'missing');assert value['status']=='UNAVAILABLE' and 'values' not in value
    for text in ('','a 1\na 2\n','x -1\n','x missing\n'):
        with pytest.raises(ValueError):c.integer_rows(text)


def sample():
    return dict(pid=12,start_ticks=987,calling_tid=12,calling_thread_start_ticks=987,cgroup_path='/owned',
        thread_status=dict(voluntary_ctxt_switches=3,nonvoluntary_ctxt_switches=4,Cpus_allowed_list='0-3'),
        process_counters=dict(ru_minflt=10,ru_majflt=2,ru_nvcsw=3,ru_nivcsw=4),process_cpu_ns=100,calling_thread_cpu_ns=70,
        cgroup={'cpu.max':dict(status='OK',text='max 100000\n'),'cpu.stat':dict(status='OK',values=dict(nr_throttled=0,throttled_usec=0)),
                'memory.events':dict(status='UNAVAILABLE',error='FileNotFoundError')})


def test_delta_preserves_unavailable_and_rejects_causal_claim():
    before=sample();after=copy.deepcopy(before);after['process_counters']['ru_majflt']+=2
    after['process_cpu_ns']+=40;after['calling_thread_cpu_ns']+=10
    out=c.increments(before,after)
    assert out['process']['ru_majflt']==2 and out['cpu_clocks']['process_cpu_ns']==40
    assert out['cgroup']['memory.events']['delta'] is None
    assert out['observer_overhead_included'] and not out['unique_wait_cause_identified']


@pytest.mark.parametrize('key,value',[('pid',13),('start_ticks',999),('calling_tid',14),('cgroup_path','/other')])
def test_delta_refuses_recycled_or_different_identity(key,value):
    a=sample();b=copy.deepcopy(a);b[key]=value
    with pytest.raises(ValueError):c.increments(a,b)


def test_delta_refuses_reconfiguration_missing_keys_and_backwards_counts():
    for mutate in (lambda r:r['cgroup']['cpu.max'].update(text='10000 100000'),
                   lambda r:r['process_counters'].update(ru_majflt=1),
                   lambda r:r['cgroup']['cpu.stat']['values'].pop('nr_throttled'),
                   lambda r:r['cgroup']['cpu.stat'].update(status='UNAVAILABLE')):
        a=sample();b=copy.deepcopy(a);mutate(b)
        with pytest.raises(ValueError):c.increments(a,b)


def test_synthetic_proc_snapshot_only_reads_self_and_reports_calling_thread(tmp_path,monkeypatch):
    proc=tmp_path/'proc';cg=tmp_path/'cgroup';task=proc/'self/task/12';task.mkdir(parents=True)
    (proc/'self/stat').write_text(stat(12,987));(task/'stat').write_text(stat(12,988))
    (task/'status').write_text('Cpus_allowed_list:\t0-3\nvoluntary_ctxt_switches:\t3\nnonvoluntary_ctxt_switches:\t4\n')
    (proc/'self/cgroup').write_text('0::/owned\n');group=cg/'owned';group.mkdir(parents=True)
    (group/'cpu.max').write_text('max 100000\n');(group/'cpu.stat').write_text('nr_throttled 0\nthrottled_usec 0\n')
    monkeypatch.setattr(c.platform,'system',lambda:'Linux');monkeypatch.setattr(c.os,'getpid',lambda:12)
    monkeypatch.setattr(c.threading,'get_native_id',lambda:12)
    monkeypatch.setattr(c,'usage_fields',lambda:dict(ru_minflt=1,ru_majflt=0,ru_nvcsw=3,ru_nivcsw=4))
    monkeypatch.setattr(c.time,'process_time_ns',lambda:100);monkeypatch.setattr(c.time,'thread_time_ns',lambda:70)
    value=c.snapshot(proc,cg)
    assert value['calling_thread_start_ticks']==988 and value['start_ticks']==987
    assert 'ru_maxrss' not in value['process_counters']
    assert value['cgroup']['memory.events']['status']=='UNAVAILABLE'
