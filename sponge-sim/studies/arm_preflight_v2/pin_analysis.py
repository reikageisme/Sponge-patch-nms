"""Prospective-candidate all-TID pin QA analysis; no OS reads or load.

This cannot re-score historical A36 records, which lack these raw snapshots.
Last-CPU observations remain diagnostics, not continuous scheduler residency.
The accounting-slack fraction MUST be locked before any new device QA.
"""
import math

from checks import thread_interval


def analyze(frames,allowed,window_start_s,window_end_s,process_cpu_s,ticks_hz,*,max_accounting_slack_fraction):
    result=dict(decision='INCONCLUSIVE',passed=False,scope='new snapshot QA only; no historical FAIL promotion')
    allowed=set(allowed);frames=list(frames)
    numbers=(window_start_s,window_end_s,process_cpu_s,ticks_hz,max_accounting_slack_fraction)
    if (not allowed or any(type(c) is not int or c<0 for c in allowed)
            or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in numbers)
            or window_end_s<=window_start_s or process_cpu_s<0 or ticks_hz<=0
            or not 0<max_accounting_slack_fraction<=1):
        result['reason']='invalid_inputs'
        return result
    wall=window_end_s-window_start_s;effective=process_cpu_s/wall
    lower=.5 if len(allowed)==1 else .7*len(allowed)
    result.update(effective_cores=effective,upper_ok=effective<=len(allowed)+.15,lower_ok=effective>=lower)
    known_failure=not result['upper_ok'] or not result['lower_ok']
    if len(frames)<2:
        result.update(reason='insufficient_snapshots',decision='FAIL' if known_failure else 'INCONCLUSIVE')
        return result
    try:
        complete=all(f['complete'] is True and bool(f['threads'])
                     and isinstance(f['errors'],list) and not f['errors'] for f in frames)
        times=[(f['started_s'],f['finished_s']) for f in frames]
        time_ok=(all(not isinstance(a,bool) and not isinstance(b,bool) and math.isfinite(a) and math.isfinite(b)
                     and window_start_s<=a<=b<=window_end_s
                     for a,b in times) and all(a[1]<=b[0] for a,b in zip(times,times[1:])))
        result['snapshot_coverage_complete']=bool(complete and time_ok)
        masks_ok=all(set(t['mask'])==allowed for f in frames for t in f['threads'].values() if 'mask' in t)
        result['masks_ok']=masks_ok
        known_failure|=not masks_ok
        if not complete or not time_ok:
            result.update(reason='incomplete_or_overlapping_snapshots',decision='FAIL' if known_failure else 'INCONCLUSIVE')
            return result
        if any(type(t[k]) is not int or t[k]<0 for f in frames for t in f['threads'].values()
               for k in ('starttime','ticks','last_cpu')):
            raise ValueError('integer nonnegative thread identity/counters required')
        intervals=[thread_interval(a['threads'],b['threads'],allowed) for a,b in zip(frames,frames[1:])]
        result['intervals']=intervals
        identities_ok=all(i['complete'] for i in intervals)
        active=sum(i['active_samples'] for i in intervals);inside=sum(i['active_inside'] for i in intervals)
        active_share=None if not active else inside/active
        observations=[t for f in frames[1:] for t in f['threads'].values()]
        result.update(stable_identities=identities_ok,active_samples=active,active_share=active_share,
                      all_tid_last_cpu_share_same_snapshots=sum(t['last_cpu'] in allowed for t in observations)/len(observations),
                      all_tid_last_cpu_observations=len(observations))
        enough_active=active>=20
        share_ok=enough_active and active_share>=.99
        known_failure|=enough_active and not share_ok
        thread_cpu=sum(i['active_ticks'] for i in intervals)/ticks_hz
        # Each TID's delta(utime+stime) has <2 ticks rounding uncertainty.
        quantization=2*len(frames[0]['threads'])/ticks_hz
        # Process-clock endpoints bracket all snapshots. TID tick endpoints
        # lie inside the first/last read spans, which are not instantaneous.
        edge_span=len(allowed)*((times[0][1]-window_start_s)+(window_end_s-times[-1][0]))
        slack=quantization+edge_span;difference=process_cpu_s-thread_cpu
        accounting_ok=(-quantization-1e-9<=difference<=slack+1e-9 and process_cpu_s>0
                       and slack/process_cpu_s<=max_accounting_slack_fraction)
        result['accounting']=dict(process_cpu_s=process_cpu_s,tid_cpu_s=thread_cpu,difference_s=difference,
                                  tick_quantization_slack_s=quantization,edge_span_slack_s=edge_span,
                                  max_slack_fraction=max_accounting_slack_fraction,passed=accounting_ok,
                                  assumption='process clock brackets snapshots; unchanged worker masks; stable TID coverage')
        passed=identities_ok and masks_ok and enough_active and share_ok and accounting_ok and not known_failure
        result.update(passed=passed,decision='PASS' if passed else ('FAIL' if known_failure else 'INCONCLUSIVE'),
                      reason='all_new_QA_gates' if passed else 'see_checks')
        return result
    except (KeyError,TypeError,ValueError,ZeroDivisionError) as e:
        result.update(reason='malformed_snapshots',error=type(e).__name__,
                      decision='FAIL' if known_failure else 'INCONCLUSIVE')
        return result
