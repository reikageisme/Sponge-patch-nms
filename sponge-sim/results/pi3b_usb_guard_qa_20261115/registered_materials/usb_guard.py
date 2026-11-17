# Metadata routes adapted from the recorded read-only command in
# sponge-sim/results/pi3b_renderer_memory_v1_20261114/readonly_usb_diagnosis.json:2-5
# SHA256 4b1f40faf6562d4ff4dc2f44bca9691161b9b56f7e9b0cb530c1ebe94aa222fc.
"""Read-only USB/storage guard for a prospective USB-present condition.

No lease, disk access, mount/eject, model or performance endpoint. Sysfs and
proc metadata only. Registration fixes static identities; each future phase
fixes its own counter/generation baseline. Old USB-absent guards are untouched.
"""
from copy import deepcopy
import os
from pathlib import Path,PurePosixPath
import re


def uint(text):
    if not re.fullmatch(r'[0-9]+',text.strip()):raise ValueError('invalid unsigned metadata')
    return int(text)


def block_stat(text):
    values=[uint(x) for x in text.split()]
    if len(values) not in (11,15,17):raise ValueError('unsupported block-stat schema')
    return values


def namespace_id(proc):return os.readlink(Path(proc)/'self/ns/mnt')


def path_devices(paths):
    if set(paths)!={'workspace','cache'}:raise ValueError('workspace and cache paths required')
    out={}
    for key,path in paths.items():
        p=Path(path).resolve(strict=True)
        if not p.is_dir():raise ValueError('bound path must be an existing directory')
        dev=p.stat().st_dev
        out[key]=dict(path=str(p),dev=f'{os.major(dev)}:{os.minor(dev)}')
    return out


def usb_descriptor(p):
    ids={k:(p/k).read_text().strip().lower() for k in ('idVendor','idProduct')}
    if any(not re.fullmatch('[0-9a-f]{4}',x) for x in ids.values()):raise ValueError('invalid USB identifier')
    return dict(path=str(p.resolve(strict=True)),**ids)


def usb_inventory(sysroot):
    out={}
    for p in sorted((sysroot/'bus/usb/devices').iterdir()):
        if ':' in p.name:continue  # interfaces are not separate USB devices
        row=usb_descriptor(p)
        row.update(busnum=uint((p/'busnum').read_text()),devnum=uint((p/'devnum').read_text()))
        if row['busnum']==0 or row['devnum']==0:raise ValueError('missing USB bus/address')
        for name in ('manufacturer','product'):
            try:row[name]=(p/name).read_text().strip()
            except FileNotFoundError:row[name]=None  # optional descriptor, not a zero counter
        out[p.name]=row
    if not out:raise ValueError('missing USB device inventory')
    return out


def usb_chain(p):
    device=p/'device'
    node=(device if device.exists() else p).resolve(strict=True)
    return [usb_descriptor(q) for q in (node,*node.parents)
            if (q/'idVendor').exists() or (q/'idProduct').exists()]


def block_node(p):
    dev=(p/'dev').read_text().strip()
    if not re.fullmatch(r'[0-9]+:[0-9]+',dev):raise ValueError('invalid block device number')
    return dict(dev=dev,sectors=uint((p/'size').read_text()),
                holders=sorted(q.name for q in (p/'holders').iterdir()))


def read_snapshot(paths,sysroot=Path('/sys'),procroot=Path('/proc')):
    """One coherent metadata frame; failure/missing required metadata raises."""
    sysroot=Path(sysroot);procroot=Path(procroot)
    namespace=namespace_id(procroot);bindings=path_devices(paths);usb=usb_inventory(sysroot)
    disks={};sd_names=sorted(p.name for p in (sysroot/'block').iterdir() if p.name.startswith('sd'))
    for p in sorted((sysroot/'block').iterdir()):
        chain=usb_chain(p)
        if not chain:
            if p.name.startswith('sd'):raise ValueError('SCSI disk has no readable USB ancestry')
            continue
        generation=uint((p/'diskseq').read_text())
        if generation==0:raise ValueError('invalid block generation')
        row=block_node(p)
        row.update(resolved_path=str(p.resolve(strict=True)),usb_chain=chain,diskseq=generation,
            removable=uint((p/'removable').read_text()),
            vendor=(p/'device/vendor').read_text().strip(),model=(p/'device/model').read_text().strip(),
            state=(p/'device/state').read_text().strip(),stat=block_stat((p/'stat').read_text()),partitions={})
        for child in sorted(p.iterdir()):
            if (child/'partition').is_file():
                part=block_node(child)
                part.update(index=uint((child/'partition').read_text()),start=uint((child/'start').read_text()))
                row['partitions'][child.name]=part
        if uint((p/'diskseq').read_text())!=generation:raise ValueError('block generation changed during sampling')
        disks[p.name]=row
    devices={r['dev'] for r in disks.values()}|{r['dev'] for d in disks.values() for r in d['partitions'].values()}
    mounts=[]
    for line in (procroot/'self/mountinfo').read_text().splitlines():
        fields=line.split()
        if len(fields)<10 or '-' not in fields:raise ValueError('malformed mountinfo')
        if fields[2] in devices:
            mounts.append(dict(dev=fields[2],mountpoint=fields[4],filesystem=fields[fields.index('-')+1]))
    if (usb_inventory(sysroot)!=usb or namespace_id(procroot)!=namespace or path_devices(paths)!=bindings
        or sorted(p.name for p in (sysroot/'block').iterdir() if p.name.startswith('sd'))!=sd_names):
        raise ValueError('topology/namespace/path changed during sampling')
    return dict(schema=1,namespace=namespace,paths=bindings,usb_devices=usb,disks=disks,mounts=mounts)


def identity(snapshot):
    """Exclude phase-lifetime addresses/generations and I/O counters only."""
    return dict(paths=snapshot['paths'],mounts=snapshot['mounts'],
        usb_devices={name:{k:v for k,v in row.items() if k!='devnum'} for name,row in snapshot['usb_devices'].items()},
        disks={name:{k:v for k,v in row.items() if k not in ('diskseq','stat')} for name,row in snapshot['disks'].items()})


def validate(snapshot,contract,baseline=None):
    """Fail closed, return reasons. contract is frozen independently before load."""
    errors=[]
    try:
        if set(snapshot)!={'schema','namespace','paths','usb_devices','disks','mounts'} or type(snapshot['schema']) is not int or snapshot['schema']!=1:
            raise ValueError('snapshot schema')
        if not re.fullmatch(r'mnt:\[[0-9]+\]',snapshot['namespace']):raise ValueError('mount namespace')
        if set(contract)!={'schema','identity'} or type(contract['schema']) is not int or contract['schema']!=1:raise ValueError('contract schema')
        if (set(snapshot['paths'])!={'workspace','cache'} or not snapshot['disks'] or not snapshot['usb_devices']
            or type(snapshot['mounts']) is not list):raise ValueError('missing bindings/inventory')
        for binding in snapshot['paths'].values():
            if (set(binding)!={'path','dev'} or not PurePosixPath(binding['path']).is_absolute()
                or '..' in PurePosixPath(binding['path']).parts or not re.fullmatch(r'[0-9]+:[0-9]+',binding['dev'])):
                raise ValueError('path binding')
        for row in snapshot['usb_devices'].values():
            if set(row)!={'path','idVendor','idProduct','busnum','devnum','manufacturer','product'}:raise ValueError('USB descriptor schema')
            if any(type(row[k]) is not int or row[k]<=0 for k in ('busnum','devnum')):raise ValueError('USB address')
            if any(not re.fullmatch('[0-9a-f]{4}',row[k]) for k in ('idVendor','idProduct')):raise ValueError('USB identifier')
        all_devs=set()
        for row in snapshot['disks'].values():
            required={'dev','sectors','holders','resolved_path','usb_chain','diskseq','removable','vendor','model','state','stat','partitions'}
            if set(row)!=required or not row['usb_chain'] or row['state']!='running':raise ValueError('disk schema/state')
            if type(row['diskseq']) is not int or row['diskseq']<=0:raise ValueError('block generation')
            if type(row['removable']) is not int or row['removable'] not in (0,1):raise ValueError('removable flag')
            stat=row['stat']
            if type(stat) is not list or len(stat) not in (11,15,17) or any(type(v) is not int or v<0 for v in stat):raise ValueError('block counters')
            if stat[8]!=0:errors.append('usb_in_flight')
            for node in [row,*row['partitions'].values()]:
                if not re.fullmatch(r'[0-9]+:[0-9]+',node['dev']) or node['dev'] in all_devs:raise ValueError('duplicate/malformed device number')
                all_devs.add(node['dev'])
                if type(node['sectors']) is not int or node['sectors']<0 or type(node['holders']) is not list:raise ValueError('block node')
                if node['holders']:errors.append('usb_holder')
            for part in row['partitions'].values():
                if set(part)!={'dev','sectors','holders','index','start'} or any(type(part[k]) is not int for k in ('index','start')):
                    raise ValueError('partition schema')
                if part['index']<=0 or part['start']<0 or part['start']+part['sectors']>row['sectors']:raise ValueError('partition layout')
        if snapshot['mounts']:errors.append('usb_mounted')
        if any(p['dev'] in all_devs for p in snapshot['paths'].values()):errors.append('workspace_or_cache_on_usb')
        if identity(snapshot)!=contract['identity']:errors.append('usb_identity_or_datapath')
        if baseline is not None:
            if validate(baseline,contract):errors.append('usb_invalid_baseline')
            if baseline['namespace']!=snapshot['namespace']:errors.append('mount_namespace_changed')
            if identity(baseline)!=identity(snapshot):errors.append('topology_changed')
            if any(baseline['usb_devices'][n]['devnum']!=r['devnum'] for n,r in snapshot['usb_devices'].items()):errors.append('usb_address_changed')
            if any(baseline['disks'][n]['diskseq']!=r['diskseq'] for n,r in snapshot['disks'].items()):errors.append('usb_generation_changed')
            if any(baseline['disks'][n]['stat']!=r['stat'] for n,r in snapshot['disks'].items()):errors.append('usb_io_or_counter_reset')
    except (OSError,KeyError,TypeError,ValueError,AttributeError,IndexError):
        errors.append('usb_invalid_readback_or_contract')
    return sorted(set(errors))


def make_contract(snapshot):
    contract=dict(schema=1,identity=deepcopy(identity(snapshot)))
    if validate(snapshot,contract):raise ValueError('cannot freeze a non-idle/invalid metadata frame')
    return contract
