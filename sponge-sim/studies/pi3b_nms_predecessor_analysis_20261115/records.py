# Pure validators copied unchanged from sponge-sim/studies/pi3b_nms_predecessor_20261115/bracket.py; SHA256 157a353fdd33f6725db73f7dc6b6c597d03ae9ef339b5744782686de368c704f.
# Selected source lines: 23-23, 24-24, 43-45, 48-55, 72-81. No sampler, clock or device API.
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

