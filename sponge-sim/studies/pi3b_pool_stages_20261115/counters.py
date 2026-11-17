# Copied unchanged from sponge-sim/studies/pi3b_nms_observer_20261115/counters.py:1-111
# SHA256 42a2ed7ba8ff7f709428ef3caefe5e14f7f21baad9659ca16b0d0a01ecc22b07; earlier observer QA source and data stay immutable.
# Copied unchanged from sponge-sim/studies/pi3b_nms_trace_20261114/counters.py:1-109
# SHA256 4c18b03e448a241a2a4c551db09337f8a37da2d0ef306f315574cc9fb2f066f4; original engineering source/tag retained.
"""Prepared self-process trace counters. No NMS, benchmark, model or mutation.

For a future registered runner only. Counter deltas include observer work
outside the perf interval; use a sham bracket. They are not exact NMS-only
faults/wait duration and do not establish a scheduler or paging cause.
Optional cgroup files remain explicitly unavailable, never replaced by zero.
"""
from pathlib import Path,PurePosixPath
import os
import platform
import threading
import time


def birth(text,expected_pid):
    head,tail=text.rsplit(')',1)
    if int(head.split('(',1)[0].strip())!=expected_pid:raise ValueError('PID identity differs')
    fields=tail.split()
    if len(fields)<20:raise ValueError('truncated proc stat')
    ticks=int(fields[19])
    if ticks<0:raise ValueError('invalid process start ticks')
    return ticks


def thread_status(text):
    fields=dict(line.split(':',1) for line in text.splitlines() if ':' in line)
    keys=('Cpus_allowed_list','voluntary_ctxt_switches','nonvoluntary_ctxt_switches')
    if any(k not in fields for k in keys):raise ValueError('missing thread identity/counters')
    out={k:fields[k].strip() for k in keys}
    for k in keys[1:]:
        out[k]=int(out[k])
        if out[k]<0:raise ValueError('negative context-switch counter')
    return out


def unified_group(text,root):
    matches=[line[3:] for line in text.splitlines() if line.startswith('0::')]
    if len(matches)!=1:raise ValueError('one unified cgroup-v2 path required')
    relative=PurePosixPath(matches[0])
    if not relative.is_absolute() or '..' in relative.parts:raise ValueError('invalid cgroup path')
    root=Path(root).resolve();target=root.joinpath(*relative.parts[1:]).resolve()
    if not target.is_relative_to(root):raise ValueError('cgroup escapes mount')
    return matches[0],target


def optional(path):
    try:return dict(status='OK',text=Path(path).read_text(encoding='utf-8'))
    except OSError as exc:return dict(status='UNAVAILABLE',error=type(exc).__name__)


def integer_rows(text):
    out={}
    for line in text.splitlines():
        key,value=line.split()
        if key in out:raise ValueError('duplicate cgroup key')
        out[key]=int(value)
        if out[key]<0:raise ValueError('negative cgroup counter')
    if not out:raise ValueError('empty cgroup counter file')
    return out


def usage_fields():
    import resource
    r=resource.getrusage(resource.RUSAGE_SELF)
    # Deliberately exclude ru_maxrss: this helper is not a memory benchmark.
    return {k:int(getattr(r,k)) for k in ('ru_minflt','ru_majflt','ru_nvcsw','ru_nivcsw')}


def snapshot(proc_root=Path('/proc'),cgroup_root=Path('/sys/fs/cgroup')):
    if platform.system()!='Linux':raise RuntimeError('Linux self-process counters required')
    pid=os.getpid();tid=threading.get_native_id();base=Path(proc_root)/'self'
    proc_start=birth((base/'stat').read_text(),pid)
    task=base/'task'/str(tid);thread_start=birth((task/'stat').read_text(),tid)
    status=thread_status((task/'status').read_text())
    group,target=unified_group((base/'cgroup').read_text(),cgroup_root)
    cg={name:optional(target/name) for name in ('cpu.max','cpu.stat','memory.events','memory.pressure')}
    for name in ('cpu.stat','memory.events'):
        if cg[name]['status']=='OK':cg[name]['values']=integer_rows(cg[name]['text'])
    if birth((base/'stat').read_text(),pid)!=proc_start or birth((task/'stat').read_text(),tid)!=thread_start:
        raise ValueError('process/thread identity changed while sampling')
    usage=usage_fields()
    if any(v<0 for v in usage.values()):raise ValueError('negative process counters')
    return dict(pid=pid,start_ticks=proc_start,calling_tid=tid,calling_thread_start_ticks=thread_start,
        thread_status=status,cgroup_path=group,cgroup=cg,process_counters=usage,
        process_cpu_ns=time.process_time_ns(),calling_thread_cpu_ns=time.thread_time_ns(),
        scope='Self-process/thread + cgroup; includes observer work, not pure operator time')


def increments(before,after):
    for key in ('pid','start_ticks','calling_tid','calling_thread_start_ticks','cgroup_path'):
        if before[key]!=after[key]:raise ValueError('cannot compare different identity: '+key)
    def delta(a,b):
        if set(a)!=set(b):raise ValueError('counter keys changed')
        values={k:b[k]-a[k] for k in a}
        if any(v<0 for v in values.values()):raise ValueError('counter decreased')
        return values
    cgroup={}
    for name in ('cpu.stat','memory.events'):
        a,b=before['cgroup'][name],after['cgroup'][name]
        if a['status']!=b['status']:raise ValueError('cgroup availability changed')
        cgroup[name]=dict(status=a['status'],delta=delta(a['values'],b['values']) if a['status']=='OK' else None)
    if before['cgroup']['cpu.max']!=after['cgroup']['cpu.max']:raise ValueError('CPU quota configuration changed')
    clocks=delta({k:before[k] for k in ('process_cpu_ns','calling_thread_cpu_ns')},
                 {k:after[k] for k in ('process_cpu_ns','calling_thread_cpu_ns')})
    return dict(process=delta(before['process_counters'],after['process_counters']),cpu_clocks=clocks,cgroup=cgroup,
        cpu_quota_raw=after['cgroup']['cpu.max'],calling_thread_context=delta(
            {k:before['thread_status'][k] for k in ('voluntary_ctxt_switches','nonvoluntary_ctxt_switches')},
            {k:after['thread_status'][k] for k in ('voluntary_ctxt_switches','nonvoluntary_ctxt_switches')}),
        observer_overhead_included=True,unique_wait_cause_identified=False)
