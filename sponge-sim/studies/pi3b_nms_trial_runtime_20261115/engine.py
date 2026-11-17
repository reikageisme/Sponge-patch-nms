"""Prepared per-image orchestration, no model loader, CLI or device activation.

Immediate pair/lifetime delegates to frozen pairs.py:12-22 in
studies/pi3b_nms_predecessor_20261115, SHA256
bd55f9e8f984b160e78da46f4eaa835c4a45d72a31ea24bb44dd8c0460f6b5fc.
Caller MUST separately bind qualified factories/pair/physical guard/inventory.
Only those bound pair functions execute between predecessor and target; this
module adds no filesystem/guard/serialization hook inside that interval.
"""
from .schedule import IMAGE_IDS,PREDECESSORS,TARGETS,OBSERVERS,schedule
from .sentry import check_pool
from . import sentry,reference as controls


def run_image(image,jobs,phase,*,prepare_pair,execute_pair,guard,inventory,emit_control,emit_trial):
    ids=IMAGE_IDS if phase=='full' else (IMAGE_IDS[0],IMAGE_IDS[2]) if phase=='smoke' else None
    if ids is None or image not in ids:raise ValueError('explicit frozen phase/image required')
    expected=[row for row in schedule(ids) if row['image']==image]
    if jobs!=expected or any(any(type(row[k]) is not type(v) for k,v in want.items()) for row,want in zip(jobs,expected)):
        raise ValueError('exact ordered image schedule required; no renumbering')
    # One warmup of every unique p x target x observer context; A/B share work.
    for p in PREDECESSORS:
        for t in TARGETS:
            for o in OBSERVERS:
                guard('pair_warmup_pre')
                predecessor,target=prepare_pair(p,t)
                try:output,raw=execute_pair(predecessor,target,instrumented=o=='instrumented')
                except BaseException as exc:
                    del predecessor,target
                    emit_control(dict(kind='pair_warmup_failed',image=image,predecessor=p,target=t,observer=o,error=type(exc).__name__));raise
                del output,predecessor,target
                row=dict(kind='pair_warmup',image=image,predecessor=p,target=t,observer=o,measurement=raw)
                try:guard('pair_warmup_post')
                except BaseException as exc:emit_control(dict(row,post_guard_ok=False,error=type(exc).__name__));raise
                emit_control(dict(row,post_guard_ok=True))
    before=inventory.snapshot();emit_control(dict(kind='pool_before',image=image,snapshot=before))
    check_pool(before)
    for job in jobs:
        emit_control(dict(kind='trial_intent',trial=job));guard('trial_pre')
        predecessor,target=prepare_pair(job['predecessor'],job['target'])
        try:output,raw=execute_pair(predecessor,target,instrumented=job['observer']=='instrumented')
        except BaseException as exc:
            del predecessor,target
            emit_control(dict(kind='trial_failed',trial=job,measurement=None,error=type(exc).__name__));raise
        del output,predecessor,target
        row=dict(trial=job,measurement=raw)
        try:guard('trial_post')
        except BaseException as exc:
            emit_trial(row)  # Preserve completed endpoints, even when quality fails.
            emit_control(dict(kind='trial_post_failed',trial=job,error=type(exc).__name__));raise
        emit_trial(row)
    after=inventory.snapshot();emit_control(dict(kind='pool_after',image=image,snapshot=after))
    check_pool(after)
    delta=inventory.increments(before,after)
    emit_control(dict(kind='image_complete',image=image,trials=len(jobs),pool_delta=delta))


def run_session(phase,*,global_pipeline,forward_reference,prepare_image,execute_pair,measure,
                guard,inventory,cpu_times,prepare_pin_workload,emit_control,emit_trial):
    """Fixed whole-session control flow, still NO loader/admission/registration.

Caller owns ONE qualified resident model and persistent first-clean reference
input. prepare_image is a context manager: load/validate both clean+adv materials,
yield a factory bound to the ADV material, release all image buffers on exit.
Reference forward happens BEFORE entering that context, never against retained
material outputs. No callbacks run between predecessor and target here.
"""
    ids=IMAGE_IDS if phase=='full' else (IMAGE_IDS[0],IMAGE_IDS[2]) if phase=='smoke' else None
    if ids is None:raise ValueError('explicit complete smoke/full phase required')
    jobs=schedule(ids)
    workload=prepare_pin_workload()
    sentry.run(workload,label='pin_start',inventory=inventory,cpu_times=cpu_times,guard=guard,emit=emit_control)
    del workload
    controls.warmup(global_pipeline,3 if phase=='full' else 1,label='global',guard=guard,emit=emit_control)
    baseline=None
    def sample_reference(label):
        nonlocal baseline
        baseline,_=controls.reference(forward_reference,label=label,baseline_ns=baseline,
            measure=measure,guard=guard,emit=emit_control)
    sample_reference('start')
    for image in ids:
        sample_reference('before_'+image)
        with prepare_image(image) as make_pair:
            try:
                run_image(image,[row for row in jobs if row['image']==image],phase,prepare_pair=make_pair,
                    execute_pair=execute_pair,guard=guard,inventory=inventory,emit_control=emit_control,emit_trial=emit_trial)
            finally:
                del make_pair  # Do not retain its captured material after context exit.
    sample_reference('end')
    workload=prepare_pin_workload()
    sentry.run(workload,label='pin_end',inventory=inventory,cpu_times=cpu_times,guard=guard,emit=emit_control)
    del workload
    emit_control(dict(kind='session_control_sequence_complete',phase=phase,scheduled_image_ids=list(ids),
        scheduled_target_trials=len(jobs),model_material_source_and_campaign_quality_qualified=False))
