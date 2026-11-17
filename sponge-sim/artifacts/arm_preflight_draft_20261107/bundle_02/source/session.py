"""Control-only session coordinator. No model, phone CLI or quality promotion.

read must provide fresh Reading objects AND durably retain every frame (the
BoundedSensors adapter does this before ACK). emit must be deadline-bounded.
All burst identities and factories are supplied before the session starts;
interrupted/not-started bursts are never automatically retried or replaced.
"""
from dataclasses import asdict,dataclass
import math

from checks import supervise_once


@dataclass(frozen=True)
class SessionConfig:
    stable_power_s: float
    poll_s: float

    def __post_init__(self):
        if any(isinstance(v,bool) or not math.isfinite(v) or v<=0
               for v in (self.stable_power_s,self.poll_s)):
            raise ValueError('explicit positive finite stable-power window and cadence required')


def rest(guard,baseline,read,emit,clock,wait,poll_s):
    """Ordinary 60..180s rest; safety cooldown always takes precedence.

    Compare EVERY zone and battery with its own pre-load baseline+1C. At 180s
    safe-but-not-baseline-cooled may proceed only with a flag, as in the old
    rest rule. It never overrides thermal hysteresis or its safety deadline.
    A hot observation is counted once on entry into Guard.COOLING, not per poll.
    """
    started=clock();last_action=None
    emit(dict(kind='rest_started',started_s=started))
    while True:
        reading=read();now=clock();action=guard.observe(reading,now)
        if action!=last_action:
            emit(dict(kind='rest_state',reason=action,state=guard.state,stops=guard.stops))
            last_action=action
        if guard.state=='END':
            return dict(reason=action,ended=True,elapsed_s=now-started,not_cooled=True)
        baseline_cooled=(all(reading.zones_c[k]<=v+1 for k,v in baseline.zones_c.items())
                         and reading.battery_c<=baseline.battery_c+1)
        elapsed=now-started
        if guard.state=='READY' and elapsed>=60 and (baseline_cooled or elapsed>=180):
            result=dict(reason='rest_completed',ended=False,elapsed_s=elapsed,not_cooled=not baseline_cooled)
            emit(dict(kind='rest_completed',**result))
            return result
        wait(poll_s)


def run_session(guard,bursts,read,emit,clock,wait,config):
    """Finite burst ledger + stable power, pre-load baseline and guarded rest.

    A result describes control flow only, never scientific validity. Caller
    must fail the run if terminal journal ACK is missing. Spawn factories must
    immediately return their newly owned child (no logging/throwing afterwards).
    """
    bursts=list(bursts)
    ids=[bid for bid,_ in bursts]
    if (not bursts or any(not isinstance(bid,str) or not bid for bid in ids)
            or len(set(ids))!=len(ids) or any(not callable(spawn) for _,spawn in bursts)):
        raise ValueError('nonempty unique fixed burst IDs/factories required')
    if guard.state!='READY' or guard.stops or guard.session_started:
        raise ValueError('a fresh guard is required for a new session')
    if config.poll_s>guard.policy.max_age_s:
        raise ValueError('poll cadence exceeds telemetry freshness allowance')
    guard.session_started=True
    result=dict(status='control_flow_incomplete',study_quality='NOT_ASSESSED',
                bursts=[dict(id=bid,status='not_started',reason='session_not_reached') for bid in ids],
                terminal_journal_ack=False)
    current=None;spawned=False;fatal=None
    try:
        emit(dict(kind='session_started',planned_bursts=ids,config=asdict(config)))
        initial=None;previous=None;observations=0
        baseline=None
        while True:
            reading=read();now=clock();reason=guard.policy.classify(reading,now)
            if reason!='ok':
                guard.state='END';result.update(status='preflight_rejected',reason=reason)
                break
            if previous is not None and now-previous>guard.policy.max_age_s:
                guard.state='END';result.update(status='preflight_rejected',reason='charging_observation_gap')
                break
            if initial is None:initial=now
            previous=now;observations+=1
            if observations>=2 and now-initial>=config.stable_power_s:
                baseline=reading
                result['baseline']=asdict(baseline)
                result['stable_power_observations']=observations
                emit(dict(kind='baseline_before_load',reading=asdict(baseline),observed_s=now))
                break
            wait(config.poll_s)
        if baseline is not None:
            for index,(bid,factory) in enumerate(bursts):
                current=result['bursts'][index];spawned=False
                emit(dict(kind='burst_planned',burst_id=bid))
                def spawn():
                    nonlocal spawned
                    child=factory();spawned=True
                    return child
                reason=supervise_once(guard,spawn,read,
                                      lambda event:emit(dict(event,burst_id=bid)),clock,wait,poll_s=config.poll_s)
                current.update(status='completed' if reason=='completed' else ('aborted' if spawned else 'not_started'),
                               reason=reason,spawned=spawned,thermal_stops=guard.stops)
                emit(dict(kind='burst_outcome',**current))
                if guard.state=='END':
                    result.update(status='stopped_on_guard',reason=reason)
                    break
                current['rest']=rest(guard,baseline,read,
                                     lambda event:emit(dict(event,burst_id=bid)),clock,wait,config.poll_s)
                if current['rest']['ended']:
                    result.update(status='stopped_on_guard',reason=current['rest']['reason'])
                    break
            else:
                result['status']=('control_flow_completed' if all(b['status']=='completed' for b in result['bursts'])
                                  else 'control_flow_finished_with_incomplete_bursts')
    except BaseException as e:
        guard.state='END'
        result.update(status='runtime_error',error=type(e).__name__,message=str(e))
        if current is not None and current['reason']=='session_not_reached':
            current.update(status='aborted' if spawned else 'not_started',reason='runtime_error',spawned=spawned)
        elif current is not None:
            current['post_burst_error']=dict(error=type(e).__name__,message=str(e))
        if not isinstance(e,Exception):fatal=e
    result['guard_state']=guard.state;result['consecutive_thermal_stops']=guard.stops
    try:
        emit(dict(kind='session_terminal',result={k:v for k,v in result.items() if k!='terminal_journal_ack'}))
        result['terminal_journal_ack']=True
    except Exception as e:
        guard.state='END'
        result.update(status='journal_error',guard_state='END',journal_error=type(e).__name__,journal_message=str(e))
    if fatal is not None:raise fatal
    return result
