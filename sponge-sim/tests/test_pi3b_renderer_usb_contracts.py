# Adapted from sponge-sim/tests/test_pi3b_renderer_memory_v1_contracts.py:1-198
# SHA256 158755567f4efb610d0e347110bd6def7812b2ae60f875cb32ba0352806709bc; USB-present integration, older tests unchanged.
# Adapted from sponge-sim/tests/test_pi3b_renderer_cache_collector.py:1-202
# SHA256 37bcdcf70b7536884c64c7889d953e1ae83a69f7352d8949e802a0240b455bdd; new namespace/phase schema only, earlier tests untouched.
"""Host engineering controls only: immutable caches and owned direct children.

No RSS, latency endpoint, Pi execution, cgroup/parent-death qualification or
real-image/model output claim. Synthetic torch tensors are functional fixtures.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import weakref
import pytest
import torch

STUDY=Path(__file__).parents[1]/'studies/pi3b_renderer_memory_usb_20261115'
sys.path.insert(0,str(STUDY))
import cache as renderer_cache
import memory_campaign as campaign
import memory_worker


def example(k=2):
    return dict(protos=torch.zeros(32,160,160),coefficients=torch.ones(k,32),boxes=torch.tensor([[0.,0.,640.,640.]]*k).reshape(k,4),shape=(640,640))


def manifest():
    ids=[f'{n:012d}' for n in range(20)]
    value=dict(status='COMPLETED_FUNCTIONAL_PARITY_ONLY',empirical_endpoint_recorded=False,cases=[
        dict(image=im,condition=a,filename=f'{im}_{a}.pt',sha256='a'*64,mask_sha256='b'*64,k=2,shape=[640,640])
        for im in ids for a in ('clean','adv')])
    return ids,value


def test_cache_roundtrip_and_no_overwrite(tmp_path):
    case=example();digest='b'*64
    row=renderer_cache.save_case(tmp_path,'000000000009','adv',case,digest,dict(k=2,n_tau=5,kernel_n=5))
    loaded=renderer_cache.load_case(tmp_path,row)
    assert all(torch.equal(case[k],loaded[k]) for k in renderer_cache.TENSOR_KEYS)
    data=(tmp_path/row['filename']).read_bytes()
    with pytest.raises(FileExistsError):renderer_cache.save_case(tmp_path,'000000000009','adv',case,digest,dict(k=2))
    assert (tmp_path/row['filename']).read_bytes()==data


@pytest.mark.parametrize('key,bad',[
    ('shape',(320,320)),('protos',torch.zeros(32,80,80)),('coefficients',torch.ones(2,31)),
    ('boxes',torch.zeros(1,4)),('boxes',torch.zeros(2,4,dtype=torch.float64)),
    ('boxes',torch.full((2,4),float('nan'))),('coefficients',torch.zeros(301,32)),
])
def test_malformed_tensor_cache_rejected(key,bad):
    c=example();c[key]=bad
    with pytest.raises(ValueError):renderer_cache.validate_case(c)


def test_changed_cache_fails_before_torch_load(tmp_path,monkeypatch):
    p=tmp_path/'000000000009_adv.pt';p.write_bytes(b'not a tensor')
    row=dict(image='000000000009',condition='adv',filename=p.name,sha256='0'*64)
    monkeypatch.setattr(torch,'load',lambda *a,**k:pytest.fail('must hash before loading'))
    with pytest.raises(ValueError,match='bytes changed'):renderer_cache.load_case(tmp_path,row)


@pytest.mark.parametrize('name',['../000000000009_adv.pt','/tmp/000000000009_adv.pt','000000000009_clean.pt'])
def test_cache_path_and_identity_rejected_before_read(tmp_path,name):
    with pytest.raises(ValueError):renderer_cache.load_case(tmp_path,dict(image='000000000009',condition='adv',filename=name))


def test_cohort_requires_all40_cases_and_never_empty():
    ids,m=manifest();assert len(renderer_cache.validate_manifest(m,ids))==40
    with pytest.raises(ValueError):renderer_cache.validate_manifest(dict(status=m['status'],empirical_endpoint_recorded=False,cases=[]),[])
    for rows in (m['cases'][:-1],m['cases']+[m['cases'][0]],list(reversed(m['cases']))):
        with pytest.raises(ValueError):renderer_cache.validate_manifest(dict(m,cases=rows),ids)


def test_sequential_parity_releases_first_full_output():
    ref=[]
    def a(*args):
        output=torch.zeros(2,640,640,dtype=torch.uint8);ref.append(weakref.ref(output));return output
    def b(*args):
        assert ref[0]() is None
        return torch.zeros(2,640,640,dtype=torch.uint8)
    result=renderer_cache.compare_outputs(example(),a,b)
    assert result==hashlib.sha256(bytes(2*640*640)).hexdigest()


def test_parity_failure_retained_as_failure():
    def a(*args):return torch.zeros(2,640,640,dtype=torch.uint8)
    def b(*args):return torch.ones(2,640,640,dtype=torch.uint8)
    with pytest.raises(ValueError,match='parity failure'):renderer_cache.compare_outputs(example(),a,b)


def test_empty_hash_matches_empty_bytes():
    assert renderer_cache.mask_sha(torch.empty(0,640,640,dtype=torch.uint8))==hashlib.sha256(b'').hexdigest()


def test_collector_import_does_not_load_second_torch_runtime():
    code=f'import sys;sys.path.insert(0,{str(STUDY)!r});import memory_campaign;assert "torch" not in sys.modules'
    p=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,timeout=20)
    assert p.returncode==0,p.stderr


def test_fixed_schedule_balanced_seeded_and_case_complete():
    ids=memory_worker.IMAGE_IDS;jobs=campaign.schedule(ids,20261114)
    assert len(jobs)==360 and [j['index'] for j in jobs]==list(range(360))
    assert jobs==campaign.schedule(ids,20261114)
    assert jobs!=campaign.schedule(ids,20261115)
    for image in ids:
        for condition in ('clean','adv'):
            for arm in memory_worker.ARMS:
                assert sorted(j['rep'] for j in jobs if (j['image'],j['condition'],j['arm'])==(image,condition,arm))==[0,1,2]


def test_direct_child_normal_and_identity_receipts(tmp_path):
    job=tmp_path/'normal'
    assert campaign.run_child([sys.executable,'-c','print("owned QA child")'],job,10,lambda:None,interval=.05)==0
    result=json.loads((job/'terminal.json').read_text())
    assert result['status']=='COMPLETED' and result['direct_child_reaped'] and not result['termination_sent']
    assert 'owned QA child' in (job/'stdout.log').read_text()


def test_direct_child_failure_stops_and_records(tmp_path):
    job=tmp_path/'failed'
    with pytest.raises(RuntimeError,match='child failed'):campaign.run_child([sys.executable,'-c','raise SystemExit(23)'],job,10,lambda:None,interval=.05)
    result=json.loads((job/'terminal.json').read_text())
    assert result['returncode']==23 and result['status']=='FAILED_STOPPED_NO_RETRY' and result['direct_child_reaped']


def test_timeout_kills_and_reaps_owned_sleeping_child(tmp_path):
    job=tmp_path/'timeout'
    with pytest.raises(TimeoutError):campaign.run_child([sys.executable,'-c','import time;time.sleep(60)'],job,.15,lambda:None,interval=.05)
    result=json.loads((job/'terminal.json').read_text())
    assert result['direct_child_reaped'] and result['termination_sent'] and result['failure']['error']=='TimeoutError'


def test_guard_stop_kills_and_reaps_owned_child(tmp_path):
    job=tmp_path/'guard'
    def check():
        if (job/'started.json').exists():raise ValueError('synthetic thermal stop')
    with pytest.raises(ValueError,match='thermal stop'):campaign.run_child([sys.executable,'-c','import time;time.sleep(60)'],job,10,check,interval=.05)
    result=json.loads((job/'terminal.json').read_text())
    assert result['direct_child_reaped'] and result['termination_sent']


def test_journal_error_after_spawn_still_reaps_child(tmp_path,monkeypatch):
    job=tmp_path/'journal';original=campaign.record
    def fail(path,value):
        if Path(path).name=='started.json':raise OSError('synthetic journal failure after spawn')
        return original(path,value)
    monkeypatch.setattr(campaign,'record',fail)
    with pytest.raises(OSError):campaign.run_child([sys.executable,'-c','import time;time.sleep(60)'],job,10,lambda:None,interval=.05)
    result=json.loads((job/'terminal.json').read_text())
    assert result['direct_child_reaped'] and result['termination_sent'] and result['owned_pid']>0


def test_precondition_failure_does_not_spawn(tmp_path):
    job=tmp_path/'pre'
    def fail():raise ValueError('synthetic missing guard')
    with pytest.raises(ValueError):campaign.run_child([sys.executable,'-c','raise SystemExit(99)'],job,10,fail)
    result=json.loads((job/'terminal.json').read_text())
    assert result['owned_pid'] is None and result['direct_child_reaped']


def test_no_reuse_of_an_existing_job(tmp_path):
    job=tmp_path/'existing';job.mkdir();(job/'keep.txt').write_text('preserve')
    with pytest.raises(FileExistsError):campaign.run_child([],job,1,lambda:None)
    assert (job/'keep.txt').read_text()=='preserve'


def registered_fixture():
    ids=memory_worker.IMAGE_IDS
    return dict(experiment='PI3B-RENDERER-MEMORY-USB',status='PREREGISTERED',
        tag='prereg-pi3b-renderer-memory-usb-fixture',arms=list(memory_worker.ARMS),repeats=3,pixel_budget=16_000_000,
        cpus=[0,1,2,3],interop_threads=1,image_ids=ids,seed=20261114,conditions=['clean','adv'],cache_manifest_sha256='61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165',mde_t_critical_sums={'2':14.082586656645868,'20':2.9539746046772377},cache_directory=memory_worker.CACHE_DIRECTORY,phases=copy.deepcopy(memory_worker.PHASES),
        child_timeout_seconds=180,campaign_timeout_seconds=21600,
        versions=dict(torch='2.15.0+cpu',numpy='2.5.4',python='3.13.5'),governor='powersave',
        gates=dict(clock_hz=[594000000,606000000],abort_temp_c=75,abort_mem_available_kb=40000,aa_abs_log=.02,mde_log=.05),
        sample_point='after_render_and_output_digest',warmup='same_renderer_K1_if_available_once',
        usb_contract=json.loads((STUDY/'usb_contract.json').read_text()),usb_contract_sha256=memory_worker.file_sha(STUDY/'usb_contract.json'),
        source_sha256={n:memory_worker.file_sha(STUDY/n) for n in memory_worker.SOURCE_FILES})


@pytest.mark.parametrize('change',[
    {'status':'DRAFT'}, {'arms':['baseline_A','candidate16M']}, {'repeats':4}, {'pixel_budget':32_000_000},
    {'cpus':[3]}, {'conditions':['adv']}, {'child_timeout_seconds':100000}, {'seed':9}, {'source_sha256':{}},
    {'versions':dict(torch='2.13.0+cpu',numpy='2.5.4',python='3.13.5')},
])
def test_unregistered_or_changed_scientific_conditions_refused(tmp_path,change):
    fixture=registered_fixture();fixture.update(change);path=tmp_path/'registration.json';path.write_text(json.dumps(fixture))
    with pytest.raises(ValueError):memory_worker.registration(path,fixture['tag'],'a'*40)


def test_registered_material_source_bytes_are_bound(tmp_path):
    fixture=registered_fixture();path=tmp_path/'registration.json';path.write_text(json.dumps(fixture))
    assert memory_worker.registration(path,fixture['tag'],'a'*40)['pixel_budget']==16_000_000
    fixture['source_sha256']['cache.py']='0'*64;path.write_text(json.dumps(fixture))
    with pytest.raises(ValueError,match='source changed'):memory_worker.registration(path,fixture['tag'],'a'*40)


