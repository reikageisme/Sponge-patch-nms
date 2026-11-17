"""Synthetic filesystem/metadata regression only; no device or performance data."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

FILE=Path(__file__).parents[1]/'studies/pi3b_renderer_memory_usb_20261115/usb_guard.py'
spec=importlib.util.spec_from_file_location('prospective_usb_guard',FILE)
u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)


def frame():
    usb=dict(path='/sys/devices/usb1/1-1',idVendor='174c',idProduct='0829',busnum=1,devnum=3,manufacturer='SupTronics',product='X89')
    common=dict(resolved_path='/sys/devices/usb1/1-1/block',usb_chain=[dict(path='/sys/devices/usb1/1-1',idVendor='174c',idProduct='0829')],
        removable=0,vendor='ADATA SP',model='900',state='running',stat=[0]*17,holders=[])
    disk=dict(common,dev='8:0',sectors=100000,diskseq=12,partitions={'sda1':dict(dev='8:1',sectors=90000,start=2048,index=1,holders=[])})
    empty=dict(deepcopy(common),dev='8:16',sectors=0,diskseq=13,partitions={},removable=1,model='X89')
    return dict(schema=1,namespace='mnt:[123]',paths={k:dict(path=p,dev='179:2') for k,p in
        [('workspace','/home/tanh/sponge-sim/new'),('cache','/home/tanh/sponge-sim/old/cache_01')]},
        usb_devices={'1-1':usb},disks={'sda':disk,'sdb':empty},mounts=[])


def test_idle_pair_and_frozen_contract_do_not_alias_live_input():
    a=frame();contract=u.make_contract(a);b=deepcopy(a)
    assert not u.validate(a,contract) and not u.validate(b,contract,a)
    a['disks']['sda']['model']='different'
    assert contract['identity']['disks']['sda']['model']=='900'
    assert u.validate(a,contract)


def test_counters_may_change_outside_phase_but_not_inside_it():
    a=frame();contract=u.make_contract(a);new=deepcopy(a)
    new['disks']['sda']['stat'][0]=70
    new['disks']['sda']['diskseq']=50;new['usb_devices']['1-1']['devnum']=10;new['namespace']='mnt:[456]'
    assert not u.validate(new,contract)  # new independently-bound phase lifetime
    assert not u.validate(new,contract,deepcopy(new))
    errors=u.validate(new,contract,a)
    assert {'usb_io_or_counter_reset','usb_generation_changed','usb_address_changed','mount_namespace_changed'}<=set(errors)


@pytest.mark.parametrize('change',[
    lambda s:s['disks'].pop('sdb'),
    lambda s:s['disks'].update(sdc=deepcopy(s['disks']['sdb'])),
    lambda s:s['disks']['sda'].update(model='other'),
    lambda s:s['disks']['sda']['partitions']['sda1'].update(start=1024),
    lambda s:s['usb_devices']['1-1'].update(idProduct='1234'),
    lambda s:s['usb_devices'].update({'1-2':deepcopy(s['usb_devices']['1-1'])}),
    lambda s:s['paths']['workspace'].update(path='/new/path'),
    lambda s:s['paths']['cache'].update(dev='8:1'),
])
def test_identity_topology_partition_and_datapath_changes_refused(change):
    a=frame();contract=u.make_contract(a);b=deepcopy(a);change(b)
    assert u.validate(b,contract,a)


@pytest.mark.parametrize('change,reason',[
    (lambda s:s['disks']['sda']['stat'].__setitem__(8,1),'usb_in_flight'),
    (lambda s:s['disks']['sda']['holders'].append('dm-0'),'usb_holder'),
    (lambda s:s['disks']['sda']['partitions']['sda1']['holders'].append('dm-1'),'usb_holder'),
    (lambda s:s['mounts'].append(dict(dev='8:1',mountpoint='/mnt/ssd',filesystem='ext4')),'usb_mounted'),
    (lambda s:s['paths']['workspace'].update(dev='8:0'),'workspace_or_cache_on_usb'),
])
def test_non_idle_conditions_cannot_be_frozen_or_admitted(change,reason):
    a=frame();contract=u.make_contract(a);change(a)
    assert reason in u.validate(a,contract)
    with pytest.raises(ValueError):u.make_contract(a)


@pytest.mark.parametrize('change',[
    lambda s:s.pop('disks'),lambda s:s.update(schema=True),lambda s:s.update(mounts={}),
    lambda s:s['disks']['sda'].pop('stat'),lambda s:s['disks']['sda'].update(stat=[0]*10),
    lambda s:s['disks']['sda']['stat'].__setitem__(0,-1),lambda s:s['disks']['sda']['stat'].__setitem__(0,False),
    lambda s:s['disks']['sda'].update(diskseq=0),lambda s:s['disks']['sda'].update(state='offline'),
    lambda s:s['disks']['sda']['partitions']['sda1'].update(sectors=100000),
    lambda s:s['usb_devices']['1-1'].update(devnum=True),lambda s:s['paths']['cache'].update(path='../escape'),
])
def test_missing_malformed_or_false_zero_readbacks_fail_closed(change):
    a=frame();contract=u.make_contract(a);change(a)
    assert 'usb_invalid_readback_or_contract' in u.validate(a,contract)


def test_invalid_baseline_and_counter_decrease_are_not_silently_accepted():
    a=frame();contract=u.make_contract(a);base=deepcopy(a);base['schema']=2
    assert 'usb_invalid_baseline' in u.validate(a,contract,base)
    base=deepcopy(a);base['disks']['sda']['stat'][0]=100
    assert 'usb_io_or_counter_reset' in u.validate(a,contract,base)


@pytest.mark.parametrize('text',['',' '.join(['0']*10),' '.join(['0']*12),' '.join(['0']*16),' '.join(['0']*16+['-1']), ' '.join(['0']*16+['nan'])])
def test_malformed_block_statistics_never_become_zero(text):
    with pytest.raises(ValueError):u.block_stat(text)


def fixture_tree(tmp_path,monkeypatch):
    sysroot=tmp_path/'sys';proc=tmp_path/'proc'
    usb=sysroot/'bus/usb/devices/1-1';usb.mkdir(parents=True)
    for name,value in dict(idVendor='174c',idProduct='0829',busnum='1',devnum='3',manufacturer='SupTronics',product='X89').items():
        (usb/name).write_text(value)
    disk=sysroot/'block/sda';(disk/'device').mkdir(parents=True);(disk/'holders').mkdir()
    for name,value in dict(dev='8:0',size='100000',diskseq='12',removable='0',stat=' '.join(['0']*17)).items():(disk/name).write_text(value)
    for name,value in dict(idVendor='174c',idProduct='0829',vendor='ADATA SP',model='900',state='running').items():(disk/'device'/name).write_text(value)
    part=disk/'sda1';(part/'holders').mkdir(parents=True)
    for name,value in dict(dev='8:1',size='90000',partition='1',start='2048').items():(part/name).write_text(value)
    (proc/'self').mkdir(parents=True);(proc/'self/mountinfo').write_text('1 0 179:2 / / rw - ext4 /dev/mmcblk0p2 rw\n')
    monkeypatch.setattr(u,'namespace_id',lambda _: 'mnt:[123]')
    monkeypatch.setattr(u,'path_devices',lambda _:deepcopy(frame()['paths']))
    return sysroot,proc,disk,usb


def test_filesystem_reader_observes_partition_mount_and_holders(tmp_path,monkeypatch):
    sysroot,proc,disk,_=fixture_tree(tmp_path,monkeypatch)
    a=u.read_snapshot({},sysroot,proc);contract=u.make_contract(a)
    assert not u.validate(a,contract) and a['disks']['sda']['diskseq']==12
    assert a['disks']['sda']['partitions']['sda1']['dev']=='8:1'
    (proc/'self/mountinfo').write_text('2 1 8:1 / /mnt/ssd rw - ext4 /dev/sda1 rw\n')
    (disk/'sda1/holders/dm-0').mkdir()
    b=u.read_snapshot({},sysroot,proc)
    assert {'usb_mounted','usb_holder'}<=set(u.validate(b,contract,a))


@pytest.mark.parametrize('missing',['diskseq','stat','holders','device/idVendor','sda1/start'])
def test_reader_missing_required_metadata_raises(tmp_path,monkeypatch,missing):
    sysroot,proc,disk,_=fixture_tree(tmp_path,monkeypatch);path=disk/missing
    if path.is_dir():path.rmdir()
    else:path.unlink()
    with pytest.raises((OSError,ValueError)):u.read_snapshot({},sysroot,proc)


def test_reader_refuses_usb_address_change_during_snapshot(tmp_path,monkeypatch):
    sysroot,proc,disk,usb=fixture_tree(tmp_path,monkeypatch);read=u.block_stat
    def mutate(text):
        (usb/'devnum').write_text('4');return read(text)
    monkeypatch.setattr(u,'block_stat',mutate)
    with pytest.raises(ValueError,match='changed during sampling'):u.read_snapshot({},sysroot,proc)
