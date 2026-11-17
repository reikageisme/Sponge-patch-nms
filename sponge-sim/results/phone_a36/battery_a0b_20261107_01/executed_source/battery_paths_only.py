"""One fixed-path RAW battery metadata read, no load, conversion or discovery.

Directory-list permission and named-file read permission are different. Only
normal Path.open reads are attempted: no root, permission change or bypass.
"""
import argparse
import hashlib
import json
from pathlib import Path

BASE=Path('/sys/class/power_supply/battery')


def collect():
    rows=[]
    for name in ('type','capacity','status','temp'):
        path=BASE/name;row=dict(field=name,path=str(path))
        try:
            with path.open() as f:raw=f.read(4097)
            if len(raw)>4096:raise ValueError('metadata exceeds 4KiB')
            row.update(readable=True,raw=raw.strip())
        except (OSError,ValueError) as e:row.update(readable=False,error=type(e).__name__,message=str(e))
        rows.append(row)
    return dict(status='READ_ONLY_FIXED_PATHS_NOT_LOAD_AUTHORIZATION',rows=rows,
                units='RAW_UNVERIFIED',temperature_conversion_performed=False,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workspace',type=Path,required=True);a=p.parse_args();target=a.output.resolve()
    if not target.is_relative_to(a.workspace.resolve()):raise ValueError('output outside workspace')
    if target.exists():raise FileExistsError(target)
    result=collect();target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
    print('FIXED_BATTERY_PATHS_SAVED_NO_LOAD',flush=True)
