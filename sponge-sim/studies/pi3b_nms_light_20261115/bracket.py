# Timing/lifetime adapted from sponge-sim/studies/laptop_seg/output_lifetime.py:1-21;
# SHA256 661537e75392a8951429bf18f141f9832f36b22cba676fe67949d47be1393293.
# Resource fields follow sponge-sim/studies/pi3b_nms_trace_20261114/counters.py:1-109;
# SHA256 4c18b03e448a241a2a4c551db09337f8a37da2d0ef306f315574cc9fb2f066f4.
# this module deliberately performs no procfs/cgroup/inventory I/O around a call.
"""Prepared call bracket, not deployed for any scientific timing yet.

Read Linux process/current-thread counters sequentially outside the perf
interval. Their deltas include observer work, not exact operator-only events.
No files, Torch, inventory or logging occur inside this module. Actual observer
cost/effect still needs registered sham and instrumented/uninstrumented control.
"""
import gc
import os
import platform
import threading
import time

FIELDS = ('ru_minflt', 'ru_majflt', 'ru_nvcsw', 'ru_nivcsw')
SAMPLE_KEYS = {'pid', 'calling_tid', 'process_cpu_ns', 'calling_thread_cpu_ns', 'process', 'calling_thread'}


def nonnegative_integer(value):
    if type(value) is not int or value < 0: raise ValueError('nonnegative integer required')
    return value


def validate(sample):
    if set(sample) != SAMPLE_KEYS: raise ValueError('counter schema differs')
    for name in ('pid', 'calling_tid', 'process_cpu_ns', 'calling_thread_cpu_ns'):
        nonnegative_integer(sample[name])
    if sample['pid'] == 0 or sample['calling_tid'] == 0: raise ValueError('invalid identity')
    for scope in ('process', 'calling_thread'):
        if set(sample[scope]) != set(FIELDS): raise ValueError('missing/extra resource counters')
        for value in sample[scope].values(): nonnegative_integer(value)


def sample():
    if platform.system() != 'Linux': raise RuntimeError('Linux RUSAGE_THREAD required')
    import resource
    process_cpu = time.process_time_ns()
    thread_cpu = time.thread_time_ns()
    process = resource.getrusage(resource.RUSAGE_SELF)
    thread = resource.getrusage(resource.RUSAGE_THREAD)
    value = dict(pid=os.getpid(), calling_tid=threading.get_native_id(),
        process_cpu_ns=process_cpu, calling_thread_cpu_ns=thread_cpu,
        process={k:getattr(process,k) for k in FIELDS}, calling_thread={k:getattr(thread,k) for k in FIELDS})
    validate(value)
    return value


def increments(before, after):
    validate(before); validate(after)
    if (before['pid'],before['calling_tid']) != (after['pid'],after['calling_tid']):
        raise ValueError('process/calling thread changed')
    clocks = {k:after[k]-before[k] for k in ('process_cpu_ns','calling_thread_cpu_ns')}
    counters = {scope:{k:after[scope][k]-before[scope][k] for k in FIELDS} for scope in ('process','calling_thread')}
    for x in [*clocks.values(), *counters['process'].values(), *counters['calling_thread'].values()]:
        nonnegative_integer(x)
    return dict(cpu_clocks=clocks, **counters, observer_work_included=True,
        sequential_not_identical_clock_intervals=True, unique_wait_cause_identified=False)


def measure(fn, *, instrumented):
    """Return (live output, raw record); caller owns release after all endpoints.

Uninstrumented mode does not sample resource/CPU counters; missing counters
are null, not0. Both modes share the same wall interval and GC discipline.
Exceptions propagate: no successful record is fabricated for a failed call.
"""
    if type(instrumented) is not bool: raise TypeError('explicit boolean instrumented mode required')
    if platform.system() != 'Linux': raise RuntimeError('Linux call bracket required')
    enabled = gc.isenabled()
    gc.disable()
    try:
        before = sample() if instrumented else None
        start = time.perf_counter_ns()
        output = fn()
        end = time.perf_counter_ns()
        after = sample() if instrumented else None
        if gc.isenabled(): raise RuntimeError('operator changed GC state')
        nonnegative_integer(start); nonnegative_integer(end)
        if end < start: raise ValueError('wall clock reversed')
        delta = increments(before,after) if instrumented else None
        record = dict(wall_start_ns=start, wall_end_ns=end, wall_ns=end-start,
            counter_status='RECORDED' if instrumented else 'NOT_RECORDED',
            before=before, after=after, increments=delta,
            output_retained_through_all_endpoints=True, procfs_or_cgroup_reads=False,
            interval='perf_counter_ns readings around callable; not bare C++ instruction time')
        return output, record
    finally:
        if enabled: gc.enable()
        else: gc.disable()
