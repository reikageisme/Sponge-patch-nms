"""Inventory failure paths and synthetic proc/cgroup fixtures; no performance test."""
from pathlib import Path
import copy
import importlib.util
import sys

import pytest

SOURCE = Path(__file__).parents[1]/'studies/pi3b_nms_observer_20261115'
spec = importlib.util.spec_from_file_location('nms_inventory', SOURCE/'inventory.py')
module = importlib.util.module_from_spec(spec)
# The parser copy has no workload or side effects; do not borrow another study's module.
cspec = importlib.util.spec_from_file_location('counters', SOURCE/'counters.py')
parser = importlib.util.module_from_spec(cspec); cspec.loader.exec_module(parser)
previous = sys.modules.get('counters')
sys.modules['counters'] = parser
spec.loader.exec_module(module)
if previous is None: del sys.modules['counters']
else: sys.modules['counters'] = previous
i = module


def stat(tid, start=123, user=7):
    fields = ['S']+['0']*36
    for ix, value in ((7, 3), (9, 2), (11, user), (12, 4), (19, start), (36, 2)):
        fields[ix] = str(value)
    return f'{tid} (worker ) with spaces) '+' '.join(fields)


def fixture(tmp_path, monkeypatch):
    proc, cg = tmp_path/'proc', tmp_path/'cg'
    for tid in (11, 12):
        task = proc/'self/task'/str(tid); task.mkdir(parents=True)
        (task/'stat').write_text(stat(tid))
        (task/'status').write_text('Cpus_allowed_list:\t0-3\nvoluntary_ctxt_switches:\t4\nnonvoluntary_ctxt_switches:\t5\n')
    (proc/'self/stat').write_text(stat(11)); (proc/'self/cgroup').write_text('0::/system.slice/qa.service\n')
    leaf = cg/'system.slice/qa.service'; leaf.mkdir(parents=True)
    for p in (cg, cg/'system.slice', leaf):
        (p/'cpu.stat').write_text('usage_usec 10\nnr_throttled 0\n')
        (p/'cpu.max').write_text('max 100000\n')
    monkeypatch.setattr(i.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(i.os, 'getpid', lambda: 11)
    monkeypatch.setattr(i.os, 'sched_getaffinity', lambda tid: {0, 1, 2, 3}, raising=False)
    return proc, cg


def test_stat_cpu_indices_and_odd_comm():
    x = i.task_stat(stat(11), 11)
    assert x == dict(start_ticks=123, state='S', minflt=3, majflt=2, utime_ticks=7, stime_ticks=4, processor_at_sample=2)
    with pytest.raises(ValueError): i.task_stat(stat(11), 12)
    with pytest.raises(ValueError): i.task_stat('11 (short) S 0', 11)


@pytest.mark.parametrize('bad', ['', '3-1', '0,,1', '-1', '0-2,2', '3,1', '0--2', '1-1048576'])
def test_cpu_list_rejects_malformed_or_ambiguous(bad):
    with pytest.raises(ValueError): i.cpu_list(bad)


def test_cpu_list_and_ancestor_quotas(tmp_path):
    assert i.cpu_list('0-3,7,9-10') == [0, 1, 2, 3, 7, 9, 10]
    assert [x[0] for x in i.ancestors('/system.slice/qa.service', tmp_path)] == ['/system.slice/qa.service', '/system.slice', '/']
    assert i.quota('50000 100000\n') == dict(quota_us=50000, period_us=100000)
    assert i.quota('max 100000') == dict(quota_us=None, period_us=100000)
    for raw in ('max 0', '-1 10', '0 10', '1 2 3', 'max a'):
        with pytest.raises(ValueError): i.quota(raw)
    with pytest.raises(ValueError): i.ancestors('/../escape', tmp_path)


def test_full_set_and_unavailable_ancestor_counters_are_explicit(tmp_path, monkeypatch):
    proc, cg = fixture(tmp_path, monkeypatch)
    s = i.snapshot(proc, cg)
    assert s['complete_stable_set'] and s['tids_before'] == s['tids_after'] == [11, 12]
    assert s['sequential_not_atomic'] and s['configured_threads_do_not_prove_parallel_execution']
    assert len(s['cgroup_ancestors']) == 3
    assert all(x['files']['memory.events']['status'] == 'UNAVAILABLE' for x in s['cgroup_ancestors'])
    d = i.increments(s, copy.deepcopy(s))
    assert set(d['threads']) == {'11', '12'} and not d['unique_wait_cause_identified']


def test_missing_task_and_affinity_mismatch_not_silently_dropped(tmp_path, monkeypatch):
    proc, cg = fixture(tmp_path, monkeypatch)
    (proc/'self/task/12/status').unlink()
    s = i.snapshot(proc, cg)
    assert not s['complete_stable_set'] and s['threads']['12']['status'] == 'UNAVAILABLE'
    with pytest.raises(ValueError): i.increments(s, s)
    (proc/'self/task/12/status').write_text('Cpus_allowed_list: 1\nvoluntary_ctxt_switches: 4\nnonvoluntary_ctxt_switches: 5\n')
    s = i.snapshot(proc, cg)
    assert not s['complete_stable_set'] and 'affinity' in s['threads']['12']['message']


@pytest.mark.parametrize('change', ['churn', 'birth', 'affinity', 'decrease', 'quota', 'ancestor', 'process'])
def test_delta_refuses_churn_reuse_configuration_or_counter_reversal(tmp_path, monkeypatch, change):
    proc, cg = fixture(tmp_path, monkeypatch)
    a = i.snapshot(proc, cg); b = copy.deepcopy(a)
    if change == 'churn': b['tids_after'] = [11]
    if change == 'birth': b['threads']['12']['stat']['start_ticks'] += 1
    if change == 'affinity': b['threads']['12']['affinity'] = [1]
    if change == 'decrease': b['threads']['12']['stat']['majflt'] -= 1
    if change == 'quota': b['cgroup_ancestors'][1]['files']['cpu.max']['text'] = '10000 100000'
    if change == 'ancestor': b['cgroup_ancestors'].pop()
    if change == 'process': b['pid'] = 999
    with pytest.raises(ValueError): i.increments(a, b)


def test_nested_quota_is_retained_even_when_leaf_unlimited(tmp_path, monkeypatch):
    proc, cg = fixture(tmp_path, monkeypatch)
    (cg/'system.slice/cpu.max').write_text('25000 100000')
    s = i.snapshot(proc, cg)
    assert s['cgroup_ancestors'][0]['files']['cpu.max']['parsed']['quota_us'] is None
    assert s['cgroup_ancestors'][1]['files']['cpu.max']['parsed']['quota_us'] == 25000


def test_reuse_late_in_sampling_is_incomplete_even_with_same_tid_list(tmp_path, monkeypatch):
    proc, cg = fixture(tmp_path, monkeypatch)
    original = i.cgroup_inventory
    def change_birth(group, root):
        value = original(group, root)
        (proc/'self/task/12/stat').write_text(stat(12, start=999))
        return value
    monkeypatch.setattr(i, 'cgroup_inventory', change_birth)
    snap = i.snapshot(proc, cg)
    assert snap['tids_before'] == snap['tids_after']
    assert snap['threads']['12']['stat']['start_ticks'] == 123
    assert snap['end_start_ticks']['12']['start_ticks'] == 999
    assert not snap['complete_stable_set']
