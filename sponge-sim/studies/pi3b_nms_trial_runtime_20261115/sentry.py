"""Prepared three-second CPU-load sentry, not NMS performance or qualification.

Workload/cadence adapts run.py:203-225 in studies/pi3b_full20_20261114,
SHA256 cadc78041d3f4e611c789c76c22b1a885131b9ca632a52a27300a440baa4425f.
Per-CPU Linux counters follow https://psutil.io/api/#psutil.cpu_times :
guest/guest_nice already occur in user/nice; never count them twice. Reject
backwards/missing counters rather than clip or substitute zeros.
"""
import math
from pathlib import Path
import time

CPUS=[0,1,2,3]
FIELDS=('user','nice','system','idle','iowait','irq','softirq','steal','guest','guest_nice')
ONLINE=Path('/sys/devices/system/cpu/online')
DURATION_NS=3_000_000_000
REQUIRED_CPU_EQUIVALENTS=.7*4


def frames(cpu_times):
    values=[dict(x._asdict()) for x in cpu_times(percpu=True)]
    if len(values)!=4:raise ValueError('four online CPU frames required')
    for row in values:
        if set(row)!=set(FIELDS) or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in row.values()):
            raise ValueError('missing/nonfinite Linux CPU counters')
    return values


def busy_fractions(before,after):
    if len(before)!=4 or len(after)!=4:raise ValueError('CPU topology changed')
    result=[]
    for left,right in zip(before,after):
        if set(left)!=set(FIELDS) or set(right)!=set(FIELDS):raise ValueError('CPU counter schema changed')
        delta={key:right[key]-left[key] for key in FIELDS}
        if any(not math.isfinite(x) or x<0 for x in delta.values()):raise ValueError('CPU counter reversed')
        total=sum(delta[k] for k in FIELDS[:8])  # guest is already included.
        if total<=0:raise ValueError('zero CPU-counter interval')
        value=1-(delta['idle']+delta['iowait'])/total
        if not 0<=value<=1:raise ValueError('invalid CPU busy fraction')
        result.append(value)
    return result


def check_pool(frame):
    if (frame['complete_stable_set'] is not True or frame['tids_before']!=frame['tids_after']
        or not frame['threads'] or set(frame['threads'])!={str(t) for t in frame['tids_before']}
        or any(x['status']!='OK' or x['affinity']!=CPUS for x in frame['threads'].values())):
        raise ValueError('incomplete/changing/nonpinned whole thread pool')


def prepare_mm(torch):
    """Allocate fixed FP32 ones256 outside sentry window; caller owns the model."""
    if torch.get_num_threads()!=4 or torch.get_num_interop_threads()!=1 or not torch.is_inference_mode_enabled():
        raise ValueError('qualified four-thread inference context required')
    x=torch.ones((256,256),dtype=torch.float32,device='cpu')
    return lambda:x@x


def run(workload,*,label,inventory,cpu_times,guard,emit):
    """No affinity mutation. Parent supervisor must independently bound hangs.

Needs both system busy>=2.8 and self process CPU/wall>=2.8, plus full pool
identity/config/affinity consistency. This is stronger than the old system
busy gate; it cannot identify simultaneous NMS workers or explain NMS latency.
The helper does not qualify the externally supplied workload or APIs.
"""
    guard('pin_pre_warmup')
    try:output=workload()
    except BaseException as exc:
        emit(dict(kind='pin_warmup_failed',label=label,passed=False,error=type(exc).__name__));raise
    del output;guard('pin_post_warmup')
    first=inventory.snapshot();check_pool(first);online_before=ONLINE.read_text().strip()
    if online_before!='0-3':raise ValueError('unexpected online CPU mask')
    before=frames(cpu_times);guard('pin_pre_load')
    wall_start=time.perf_counter_ns();cpu_start=time.process_time_ns();iterations=0
    try:
        while time.perf_counter_ns()<wall_start+DURATION_NS:
            output=workload();del output;iterations+=1
    except BaseException as exc:
        emit(dict(kind='pin_load_failed',label=label,before_pool=first,before_cpu=before,wall_start_ns=wall_start,process_cpu_start_ns=cpu_start,
            wall_end_ns=None,process_cpu_end_ns=None,iterations=iterations,passed=False,error=type(exc).__name__))
        raise
    cpu_end=time.process_time_ns();wall_end=time.perf_counter_ns()
    after=frames(cpu_times);last=inventory.snapshot();online_after=ONLINE.read_text().strip()
    row=dict(kind='pin_load',label=label,before_cpu=before,after_cpu=after,before_pool=first,after_pool=last,
        wall_start_ns=wall_start,wall_end_ns=wall_end,process_cpu_start_ns=cpu_start,process_cpu_end_ns=cpu_end,
        online_before=online_before,online_after=online_after,iterations=iterations,not_nms_endpoint=True,
        sequential_not_atomic=True,workload_and_runtime_qualification_performed=False)
    try:
        guard('pin_post_load');check_pool(last)
        if online_after!=online_before:raise ValueError('online CPU mask changed')
        delta=inventory.increments(first,last)
        if any(type(x) is not int or x<0 for x in (wall_start,wall_end,cpu_start,cpu_end)):
            raise ValueError('invalid sentry clock')
        wall=wall_end-wall_start;cpu=cpu_end-cpu_start
        if wall<DURATION_NS or cpu<0 or iterations<1:raise ValueError('incomplete sentry window')
        busy=busy_fractions(before,after);ratio=cpu/wall
        passed=sum(busy)>=REQUIRED_CPU_EQUIVALENTS and ratio>=REQUIRED_CPU_EQUIVALENTS
        row.update(busy=busy,inside_cpu_equivalents=sum(busy),process_cpu_over_wall=ratio,pool_delta=delta,
            required_cpu_equivalents=REQUIRED_CPU_EQUIVALENTS,passed=passed,
            all_four_threads_simultaneously_in_nms_proven=False,campaign_quality_assessed=False)
    except BaseException as exc:
        emit(dict(row,passed=False,error=type(exc).__name__,message=str(exc)));raise
    emit(row)
    if not passed:raise RuntimeError('actual-load pin/parallelism gate failed')
    return row
