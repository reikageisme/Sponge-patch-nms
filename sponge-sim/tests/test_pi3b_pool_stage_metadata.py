"""Synthetic stage mapping/kernel metadata checks; no Torch import or timing."""
from pathlib import Path
import copy
import gzip
import importlib.util
import sys

import pytest

S = Path(__file__).parents[1]/'studies/pi3b_pool_stages_20261115'
saved = {n:sys.modules.get(n) for n in ('counters', 'inventory')}
for name in ('counters', 'inventory'):
    spec=importlib.util.spec_from_file_location(name,S/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sys.modules[name]=m
spec=importlib.util.spec_from_file_location('stage_metadata',S/'metadata.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for name,value in saved.items():
    if value is None: del sys.modules[name]
    else: sys.modules[name]=value


def test_proc_cgroups_keeps_disabled_and_absent_distinct():
    x=m.proc_cgroups('#subsys_name hierarchy num_cgroups enabled\ncpu 0 8 1\nmemory 0 0 0\n')
    assert x['memory']['enabled']==0 and x['cpu']['enabled']==1
    assert 'memory' not in m.proc_cgroups('cpu 0 8 1')


@pytest.mark.parametrize('bad',['', '#header\n', 'cpu 0 2 2', 'cpu -1 2 1', 'cpu 0 1 1\ncpu 0 1 1', 'cpu 0 1'])
def test_bad_proc_cgroups_refused(bad):
    with pytest.raises(ValueError): m.proc_cgroups(bad)


def test_maps_selects_shared_paths_without_inventing_thread_ownership():
    text='''100-200 r-xp 0 00:00 1 /a/libfoo.so.1
200-300 r--p 0 00:00 1 /a/libfoo.so.1
300-400 r-xp 0 00:00 2 /path with spaces/plugin.so (deleted)
400-500 rw-p 0 00:00 0 [heap]
'''
    assert m.library_paths(text)==['/a/libfoo.so.1','/path with spaces/plugin.so (deleted)']


def test_missing_kernel_config_and_memory_controller_stay_unavailable(tmp_path):
    proc,cg,boot=tmp_path/'proc',tmp_path/'cg',tmp_path/'boot'
    proc.mkdir();cg.mkdir();boot.mkdir()
    (proc/'cmdline').write_text('root=/dev/example cgroup_disable=memory')
    (proc/'cgroups').write_text('cpu 0 3 1\nmemory 0 0 0\n')
    (cg/'cgroup.controllers').write_text('cpu pids')
    r=m.kernel_metadata(proc,cg,boot)
    assert r['proc']['cgroups']['rows']['memory']['enabled']==0
    assert all(x['status']=='UNAVAILABLE' for x in r['kernel_config'].values())
    assert r['proc']['self/mountinfo']['status']=='UNAVAILABLE'
    assert not r['configuration_changed']


def stage(label, identities, libraries=()):
    return dict(label=label,complete=True,loaded_libraries=list(libraries),
        inventory=dict(pid=11,start_ticks=5,cgroup_path='/qa',threads={str(t):dict(stat=dict(start_ticks=b)) for t,b in identities}))


def test_transition_tracks_recycled_tid_as_both_gone_and_born():
    a=stage('import_a',[(11,5),(12,6)],['/a/liba.so'])
    b=stage('import_b',[(11,5),(12,9),(13,10)],['/a/liba.so','/b/libb.so'])
    r=m.transitions([a,b])[0]
    assert r['gone_identities']==[dict(tid=12,start_ticks=6)]
    assert r['born_identities']==[dict(tid=12,start_ticks=9),dict(tid=13,start_ticks=10)]
    assert r['newly_mapped_libraries']==['/b/libb.so']
    assert r['temporal_cooccurrence_only'] and not r['library_ownership_identified']


def test_transition_refuses_incomplete_or_different_process():
    a=stage('a',[(11,5)]);b=copy.deepcopy(a)
    b['complete']=False
    with pytest.raises(ValueError):m.transitions([a,b])
    b=copy.deepcopy(a);b['inventory']['start_ticks']+=1
    with pytest.raises(ValueError):m.transitions([a,b])


def test_exposed_kernel_config_preserves_file_hash_and_actual_line_numbers(tmp_path):
    proc,cg,boot=tmp_path/'proc',tmp_path/'cg',tmp_path/'boot'
    proc.mkdir();cg.mkdir();boot.mkdir()
    (proc/'config.gz').write_bytes(gzip.compress(b'CONFIG_OTHER=y\nCONFIG_CGROUPS=y\n# CONFIG_MEMCG is not set\n'))
    r=m.kernel_metadata(proc,cg,boot)
    x=r['kernel_config'][str(proc/'config.gz')]
    assert x['status']=='OK' and len(x['sha256'])==64
    assert x['selected_lines']==[dict(line=2,text='CONFIG_CGROUPS=y'),dict(line=3,text='# CONFIG_MEMCG is not set')]


def test_stage_names_bound_to_observed_birth_and_missing_name_is_incomplete(tmp_path,monkeypatch):
    proc,cg=tmp_path/'proc',tmp_path/'cg';task=proc/'self/task/11';task.mkdir(parents=True);(cg/'qa').mkdir(parents=True)
    (task/'stat').write_text('11 (worker) '+' '.join(['S']+['0']*18+['5']))
    (task/'comm').write_text('worker\n');(proc/'self/maps').write_text('0-1 r-xp 0 00:00 1 /a/library.so\n')
    snap=dict(complete_stable_set=True,tids_before=[11],threads={'11':dict(stat=dict(start_ticks=5))},
              cgroup_path='/qa',cgroup_ancestors=[dict(path='/qa'),dict(path='/')])
    monkeypatch.setattr(m.inventory,'snapshot',lambda *args:snap)
    r=m.stage('a',proc,cg)
    assert r['complete'] and r['thread_names']['11']['comm']=='worker'
    assert r['loaded_libraries']==['/a/library.so']
    assert all(x['status']=='UNAVAILABLE' for x in r['subtree_controls'].values())
    (task/'comm').unlink();r=m.stage('b',proc,cg)
    assert not r['complete'] and r['thread_names']['11']['status']=='UNAVAILABLE'


def test_stage_name_birth_reuse_is_not_accepted(tmp_path,monkeypatch):
    proc,cg=tmp_path/'proc',tmp_path/'cg';task=proc/'self/task/11';task.mkdir(parents=True);(cg/'qa').mkdir(parents=True)
    (task/'stat').write_text('placeholder');(task/'comm').write_text('worker\n');(proc/'self/maps').write_text('')
    snap=dict(complete_stable_set=True,tids_before=[11],threads={'11':dict(stat=dict(start_ticks=5))},
              cgroup_path='/qa',cgroup_ancestors=[dict(path='/qa'),dict(path='/')])
    monkeypatch.setattr(m.inventory,'snapshot',lambda *args:snap)
    sequence=iter([5,6]);monkeypatch.setattr(m,'birth',lambda *args:next(sequence))
    assert not m.stage('a',proc,cg)['complete']
