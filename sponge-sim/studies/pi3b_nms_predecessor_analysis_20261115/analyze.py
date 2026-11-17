"""Strict offline numerical analysis, still awaiting scientific registration.

Input schema is prospective: each raw JSONL row contains exactly `trial`
(the complete frozen schedule cell) and `measurement` (bracket.measure record).
No loading old NMS timing into this schema, subset rescue or device access.
This module deliberately cannot certify campaign quality from timing alone.
"""
import math
from statistics import median

from . import records,statistics
from .schedule import IMAGE_IDS,PREDECESSORS,TARGETS,OBSERVERS,COPIES,schedule

MEASURE_KEYS={'wall_start_ns','wall_end_ns','wall_ns','counter_status','before','after','increments',
    'output_retained_through_all_endpoints','procfs_or_cgroup_reads','interval'}
INTERVAL='perf_counter_ns readings around callable; not bare C++ instruction time'
SMOKE_IDS=(IMAGE_IDS[0],IMAGE_IDS[2])


def validate_measurement(value,observer,target):
    if not isinstance(value,dict) or set(value)!=MEASURE_KEYS:raise ValueError('measurement schema differs')
    for key in ('wall_start_ns','wall_end_ns','wall_ns'):records.nonnegative_integer(value[key])
    if value['wall_end_ns']-value['wall_start_ns']!=value['wall_ns']:raise ValueError('wall interval arithmetic differs')
    if target!='sham' and value['wall_ns']==0:raise ValueError('nonsham interval must be positive')
    if (value['output_retained_through_all_endpoints'] is not True
        or value['procfs_or_cgroup_reads'] is not False or value['interval']!=INTERVAL):
        raise ValueError('endpoint/lifetime contract differs')
    if observer=='uninstrumented':
        if value['counter_status']!='NOT_RECORDED' or any(value[k] is not None for k in ('before','after','increments')):
            raise ValueError('uninstrumented counters must be null, never zero')
    elif observer=='instrumented':
        if value['counter_status']!='RECORDED':raise ValueError('instrumented resource samples missing')
        delta=records.increments(value['before'],value['after'])
        saved=value['increments']
        if (not isinstance(saved,dict) or saved!=delta or any(saved[k] is not True for k in
            ('observer_work_included','sequential_not_identical_clock_intervals'))
            or saved['unique_wait_cause_identified'] is not False):
            raise ValueError('saved resource delta differs')
        for scope in ('cpu_clocks','process','calling_thread'):
            for number in saved[scope].values():records.nonnegative_integer(number)
    else:raise ValueError('unsupported observer')


def audit_rows(rows,phase):
    if phase not in ('smoke','full'):raise ValueError('explicit smoke/full scope required')
    expected=schedule(SMOKE_IDS if phase=='smoke' else IMAGE_IDS)
    errors=[];last_end=None;identity=None
    if len(rows)!=len(expected):errors.append(dict(reason='incomplete_or_extra_rows',expected=len(expected),actual=len(rows)))
    for ix,row in enumerate(rows):
        try:
            if not isinstance(row,dict) or set(row)!={'trial','measurement'}:raise ValueError('row schema differs')
            trial=row['trial']
            if (ix>=len(expected) or trial!=expected[ix] or not isinstance(trial,dict)
                or any(type(trial[k]) is not type(v) for k,v in expected[ix].items())):
                raise ValueError('schedule cell/order/type differs; no renumbering')
            value=row['measurement'];validate_measurement(value,trial['observer'],trial['target'])
            if last_end is not None and value['wall_start_ns']<last_end:raise ValueError('overlapping/reversed trial wall clocks')
            last_end=value['wall_end_ns']
            if trial['observer']=='instrumented':
                current=(value['before']['pid'],value['before']['calling_tid'])
                if identity is not None and current!=identity:raise ValueError('persistent worker/calling thread identity changed')
                identity=current
        except (KeyError,TypeError,ValueError,OverflowError) as exc:
            errors.append(dict(line=ix+1,reason=str(exc)))
    return dict(status='COMPLETE_RAW_NUMERICAL_SCHEMA' if not errors else 'RAW_AUDIT_FAILED_NO_INFERENCE',
        numerical_schema_pass=not errors,phase=phase,expected_trials=len(expected),actual_trials=len(rows),
        errors=errors,campaign_quality_assessed=False,scientific_registration_verified=False)


def summarize(rows,phase,raw_name):
    if not isinstance(raw_name,str) or not raw_name:raise ValueError('explicit raw source name required')
    audit=audit_rows(rows,phase)
    result=dict(audit=audit,campaign_quality_assessed=False,confirmatory_interpretation_authorized=False,
        numerical_controls_pass=None,primary=None,raw_source=raw_name)
    if not audit['numerical_schema_pass']:return result
    images=SMOKE_IDS if phase=='smoke' else IMAGE_IDS
    cells={};counter_rows=[]
    for ix,row in enumerate(rows):
        job,value=row['trial'],row['measurement'];key=tuple(job[k] for k in ('image','predecessor','target','observer','copy'))
        cells.setdefault(key,[]).append((value['wall_ns'],ix+1))
        if job['observer']=='instrumented':
            counter_rows.append(dict(line=ix+1,source=f'{raw_name}:{ix+1}:measurement',trial=job,
                increments=value['increments'],wall_ns=value['wall_ns'],
                process_cpu_over_wall=None if value['wall_ns']==0 else value['increments']['cpu_clocks']['process_cpu_ns']/value['wall_ns'],
                counters_include_observer_work=True,unique_nms_wait_cause_identified=False))
    medians=[]
    def values(image,p,t,o,copies):
        samples=[x for c in copies for x in cells[(image,p,t,o,c)]]
        if len(samples)!=5*len(copies):raise ValueError('incomplete cell cannot contribute')
        return median(x[0] for x in samples),[x[1] for x in samples]
    for key,samples in cells.items():
        medians.append(dict(image=key[0],predecessor=key[1],target=key[2],observer=key[3],copy=key[4],
            median_ns=median(x[0] for x in samples),n_trials=len(samples),lines=[x[1] for x in samples]))
    controls=[]
    for p in PREDECESSORS:
        for t in TARGETS:
            if t=='sham':continue  # No sham ratio or sham subtraction.
            for o in OBSERVERS:
                logs=[];mapping=[]
                for image in images:
                    a,alines=values(image,p,t,o,('A',));b,blines=values(image,p,t,o,('B',))
                    value=math.log(a/b);logs.append(value)
                    mapping.append(dict(image=image,numerator_median_ns=a,denominator_median_ns=b,log_ratio=value,
                        numerator_lines=alines,denominator_lines=blines))
                controls.append(dict(kind='AA',predecessor=p,target=t,observer=o,per_image=mapping,**statistics.moments(logs)))
            logs=[];mapping=[]
            for image in images:
                a,alines=values(image,p,t,'instrumented',COPIES);b,blines=values(image,p,t,'uninstrumented',COPIES)
                value=math.log(a/b);logs.append(value)
                mapping.append(dict(image=image,numerator_median_ns=a,denominator_median_ns=b,log_ratio=value,
                    numerator_lines=alines,denominator_lines=blines))
            controls.append(dict(kind='instrumentation',predecessor=p,target=t,per_image=mapping,**statistics.moments(logs)))
    per_image=[]
    for image in images:
        a,alines=values(image,'candidate16M','wrapper','uninstrumented',COPIES)
        b,blines=values(image,'native32M','wrapper','uninstrumented',COPIES)
        per_image.append(dict(image=image,numerator_median_ns=a,denominator_median_ns=b,ratio=a/b,log_ratio=math.log(a/b),
            numerator_lines=alines,denominator_lines=blines))
    full=phase=='full'
    result.update(status='COMPLETE_FULL_NUMERICAL_DIAGNOSTIC' if full else 'TECHNICAL_SMOKE_DESCRIPTIVE_ONLY',
        cell_medians=medians,counter_rows=counter_rows,controls=controls,
        control_counts=dict(AA=sum(x['kind']=='AA' for x in controls),instrumentation=sum(x['kind']=='instrumentation' for x in controls)),
        numerical_controls_pass=all(x['numerical_gate_pass'] for x in controls) if full else None,
        smoke_control_gates_are_diagnostic_only=not full,
        primary=dict(per_image=per_image,pooled_trials_per_arm_per_image=10,
            statistics=statistics.primary([x['log_ratio'] for x in per_image]) if full else None),
        all_full_controls_required=True,sham_time_subtracted=False,
        interpretation='Numerical diagnostic only. Source, physical, material, reference, pool, restore and registration gates still require independent evidence.')
    return result
