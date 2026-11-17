"""Metadata only: no Torch import, matrix work, affinity mutation or model.

Sysfs raw inspection is explicit opt-in under approved A0 scope. Returned
power-supply temperature units are UNVERIFIED; never auto-build a safety
registry from raw magnitudes or call unreadable nodes zero degrees.
"""
import argparse
import hashlib
import importlib.metadata
import importlib.util
import os
from pathlib import Path
import platform
import sys

from linux_observe import collect_threads

THERMAL=Path('/sys/class/thermal')
POWER=Path('/sys/class/power_supply')


def node(path):
    record=dict(path=str(path))
    try:
        with path.open() as f:raw=f.read(4097)
        if len(raw)>4096:raise ValueError('metadata field exceeds 4KiB')
        record['raw']=raw.strip();record['readable']=True
    except (OSError,ValueError) as e:
        record.update(readable=False,error=type(e).__name__,message=str(e))
    return record


def inspect_sysfs():
    result=dict(thermal=[],power=[],errors=[],temperature_conversion_performed=False)
    for root,kind,fields in ((THERMAL,'thermal',('type','temp')),
                             (POWER,'power',('type','temp','capacity','status','online'))):
        try:
            paths=sorted(root.iterdir())
            if kind=='thermal':paths=[p for p in paths if p.name.startswith('thermal_zone')]
            for path in paths:
                result[kind].append(dict(id=path.name,nodes={name:node(path/name) for name in fields},
                                         unit_contract='REQUIRES_EXPLICIT_REVIEW_BEFORE_REGISTRY'))
        except OSError as e:result['errors'].append(dict(path=str(root),error=type(e).__name__,message=str(e)))
    return result


def collect(allow_sysfs=False):
    if 'torch' in sys.modules:raise RuntimeError('metadata must start in a fresh process without Torch')
    if not hasattr(os,'sched_getaffinity'):raise RuntimeError('Linux own-process metadata API required')
    result=dict(status='METADATA_ONLY_NOT_LOAD_AUTHORIZATION',python=sys.version,executable=sys.executable,
                architecture=platform.machine(),platform=platform.platform(),allowed_cpus=sorted(os.sched_getaffinity(0)),
                ticks_hz=os.sysconf('SC_CLK_TCK'),thread_snapshot=collect_threads(),
                omp={k:os.environ.get(k) for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS')},
                packages={},torch_imported=False,sysfs_requested=allow_sysfs)
    for name in ('torch','torchvision','ultralytics','scipy','psutil'):
        entry={}
        try:entry['version']=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:entry['version']=None
        spec=importlib.util.find_spec(name)
        if spec is not None and spec.origin:
            entry['init_path']=spec.origin
            try:entry['init_sha256']=hashlib.sha256(Path(spec.origin).read_bytes()).hexdigest()
            except OSError as e:entry.update(error=type(e).__name__,message=str(e))
        result['packages'][name]=entry
    if allow_sysfs:result['sysfs_raw']=inspect_sysfs()
    if 'torch' in sys.modules:raise RuntimeError('unexpected Torch import during metadata collection')
    return result


if __name__=='__main__':
    import json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workspace',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--allow-sysfs',action='store_true')
    args=parser.parse_args();target=args.output.resolve()
    if not target.is_relative_to(args.workspace.resolve()):raise ValueError('output outside declared workspace')
    if target.exists():raise FileExistsError(target)
    result=collect(args.allow_sysfs)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
    print('METADATA_SAVED_NO_TORCH_IMPORT_NO_LOAD',flush=True)
