"""Own-process Linux observations, unrun on A36. No Torch or experiment CLI.

Filesystem reads here are synchronous. A bounded OS reader/watchdog is still
required before deployment; these functions alone are NOT a phone supervisor.
"""
import math
import os
from pathlib import Path
import time

from checks import Reading, parse_stat

PROC_TASK = Path('/proc/self/task')


def cpu_list(text):
    result=set()
    for item in text.strip().split(','):
        pair=item.split('-')
        if len(pair) not in (1,2) or any(not x.isdigit() for x in pair):
            raise ValueError('malformed CPU list')
        lo,hi=int(pair[0]),int(pair[-1])
        if hi<lo:
            raise ValueError('reversed CPU range')
        result.update(range(lo,hi+1))
    return sorted(result)


def collect_threads(clock=time.monotonic):
    """Observe only this process, retaining raw stat/status and incomplete sets.

    Affinity readback and proc status must agree. Stable TID numbers alone do
    not establish identity: stat starttime is checked across each read window.
    An idle last_cpu outside the requested set is preserved, not filtered here.
    """
    started=clock();threads={};errors=[]
    first=sorted(int(p.name) for p in PROC_TASK.iterdir() if p.name.isdigit())
    for tid in first:
        row=dict(tid=tid,read_started_s=clock())
        try:
            path=PROC_TASK/str(tid)
            row['stat_before']=(path/'stat').read_text()
            a=parse_stat(row['stat_before'])
            row['status']=(path/'status').read_text()
            masks=[s.split(':',1)[1] for s in row['status'].splitlines()
                   if s.startswith('Cpus_allowed_list:')]
            if len(masks)!=1:
                raise ValueError('missing or duplicate Cpus_allowed_list')
            row['status_mask']=cpu_list(masks[0])
            row['mask']=sorted(os.sched_getaffinity(tid))
            row['stat_after']=(path/'stat').read_text()
            b=parse_stat(row['stat_after'])
            if any(int(row[k].split(' ',1)[0])!=tid for k in ('stat_before','stat_after')):
                raise ValueError('stat TID differs from directory')
            if a['starttime']!=b['starttime'] or b['ticks']<a['ticks']:
                raise ValueError('TID reused or CPU counter regressed during observation')
            if row['mask']!=row['status_mask'] or not row['mask']:
                raise ValueError('status/scheduler mask disagreement or empty mask')
            row.update(b)
        except (OSError,ValueError,IndexError) as e:
            errors.append(dict(tid=tid,error=type(e).__name__,message=str(e)))
        row['read_finished_s']=clock();threads[tid]=row
    last=sorted(int(p.name) for p in PROC_TASK.iterdir() if p.name.isdigit())
    return dict(started_s=started,finished_s=clock(),threads=threads,errors=errors,
                first_tids=first,last_tids=last,
                complete=bool(first) and first==last and not errors)


def pin_current(cpus):
    """Call in a fresh worker BEFORE importing Torch or creating pools."""
    requested=set(cpus)
    if not requested or any(type(c) is not int or c<0 for c in requested):
        raise ValueError('nonempty nonnegative integer CPU set required')
    os.sched_setaffinity(0,requested)
    actual=set(os.sched_getaffinity(0))
    if actual!=requested:
        raise RuntimeError('main-thread affinity readback mismatch')
    return sorted(actual)


def pin_all_current(cpus):
    """One finite all-TID attempt in this worker, never retries thread churn.

    Caller must preserve partial changes/errors and end the isolated worker on
    failure. This does not pin any parent, SSH, proot or other named process.
    It is a preparation/readback result, not a CPU-load/residency PASS.
    """
    requested=set(cpus)
    if not requested or any(type(c) is not int or c<0 for c in requested):
        raise ValueError('nonempty nonnegative integer CPU set required')
    before=collect_threads();changes=[]
    if before['complete']:
        for tid,row in before['threads'].items():
            event=dict(tid=tid,starttime=row['starttime'],old_mask=row['mask'])
            try:
                current=parse_stat((PROC_TASK/str(tid)/'stat').read_text())
                if current['starttime']!=row['starttime']:
                    raise RuntimeError('TID reused before pin')
                os.sched_setaffinity(tid,requested)
                event['readback']=sorted(os.sched_getaffinity(tid))
                if event['readback']!=sorted(requested):
                    raise RuntimeError('TID mask readback mismatch')
            except (OSError,ValueError,IndexError,RuntimeError) as e:
                event.update(error=type(e).__name__,message=str(e))
            changes.append(event)
    after=collect_threads()
    same_identity=(before['threads'].keys()==after['threads'].keys() and
                   all(a.get('starttime')==after['threads'][tid].get('starttime')
                       for tid,a in before['threads'].items()))
    complete=(before['complete'] and after['complete'] and same_identity and
              len(changes)==len(before['threads']) and not any('error' in e for e in changes) and
              all(set(r['mask'])==requested for r in after['threads'].values()))
    return dict(before=before,changes=changes,after=after,readback_complete=complete)


def sensor_frame(spec,read_text=None,clock=time.monotonic):
    """Explicit locked paths/types/units; missing/unknown values invalidate frame.

    spec: zones=[{id,path,type_path,type_value,unit}], battery={same fields},
    soc_path,status_path,charging_values,known_status_values. No autodiscovery,
    magnitude-based units, missing-sensor zeros or assumed charging state.
    Timestamp is BEFORE any reads, so slow reads cannot masquerade as fresh.
    """
    read_text=read_text or (lambda path:Path(path).read_text())
    frame=dict(started_s=clock(),raw={},errors=[],reading=None)
    def read(path):
        value=read_text(path).strip();frame['raw'][path]=value
        return value
    try:
        zones=spec['zones'];battery=spec['battery']
        ids=[s['id'] for s in zones]+[battery['id']]
        if not zones or len(set(ids))!=len(ids):
            raise ValueError('nonempty zones and unique battery/zone IDs required')
        values={}
        for sensor in [*zones,battery]:
            if read(sensor['type_path'])!=sensor['type_value']:
                raise ValueError('sensor type changed: '+sensor['id'])
            divisor={'celsius':1,'deci_celsius':10,'milli_celsius':1000}[sensor['unit']]
            value=float(read(sensor['path']))/divisor
            if not math.isfinite(value) or value<-273.15:
                raise ValueError('nonfinite or physically invalid temperature')
            values[sensor['id']]=value
        soc=float(read(spec['soc_path']))
        if not math.isfinite(soc) or not 0<=soc<=100:
            raise ValueError('invalid battery percentage')
        known=set(spec['known_status_values']);charging=set(spec['charging_values'])
        if not charging or not charging<=known:
            raise ValueError('explicit known/charging status sets required')
        status=read(spec['status_path'])
        if status not in known:
            raise ValueError('unknown battery status')
        frame['reading']=Reading(frame['started_s'],{s['id']:values[s['id']] for s in zones},
                                 values[battery['id']],soc,status in charging)
    except (OSError,ValueError,KeyError,TypeError) as e:
        frame['errors'].append(dict(error=type(e).__name__,message=str(e)))
    frame['finished_s']=clock()
    return frame
