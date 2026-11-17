"""Local Linux engineering check: no model, CPU-load benchmark or phone.

Uses only its own worker masks, fixture sensor files and a sleeping child.
Native Linux success does not validate Android/proot or sensor permissions.
"""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import sys
import tempfile
import time

import linux_observe as observe
from checks import Guard,Policy
from posix_runtime import BoundedEvents,BoundedSensors,OwnGroup,stop_group
from session import SessionConfig,run_session


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main(root):
    root=root.resolve();root.mkdir(parents=True,exist_ok=False)
    result=dict(status='INCOMPLETE',scope='LOCAL_LINUX_ENGINEERING_ONLY_NOT_A36_NO_LOAD_BENCHMARK',checks={})
    source=Path(__file__).resolve().parent
    result['source_sha256']={f:sha(source/f) for f in ('checks.py','linux_observe.py','posix_runtime.py','session.py','local_linux_check.py')}
    try:
        before=observe.collect_threads();assert before['complete']
        allowed=sorted(os.sched_getaffinity(0));chosen=allowed[0]
        assert observe.pin_current([chosen])==[chosen]
        readback=observe.pin_all_current([chosen]);assert readback['readback_complete']
        result['checks']['own_thread_mask_readback']=True
        result['original_allowed_cpus']=allowed;result['chosen_virtual_cpu']=chosen
        result['thread_readback']=readback
        for name,value in {'cpu.temp':'50000','cpu.type':'fixture-cpu','battery.temp':'350',
                           'battery.type':'Battery','soc':'50','status':'Charging'}.items():
            (root/name).write_text(value)
        spec=dict(zones=[dict(id='fixture_cpu',path=str(root/'cpu.temp'),type_path=str(root/'cpu.type'),
                              type_value='fixture-cpu',unit='milli_celsius')],
                  battery=dict(id='fixture_battery',path=str(root/'battery.temp'),type_path=str(root/'battery.type'),
                               type_value='Battery',unit='deci_celsius'),
                  soc_path=str(root/'soc'),status_path=str(root/'status'),charging_values=['Charging'],
                  known_status_values=['Charging','Discharging'])
        config=root/'sensor_spec.json';config.write_text(json.dumps(spec))
        reader=BoundedSensors(config,sha(config),root,3,root/'frames')
        reading=reader.read();assert reading.zones_c=={'fixture_cpu':50} and reading.battery_c==35
        result['checks']['bounded_fixture_sensor_read']=True
        result['fixture_frame']=reader.last_frame
        logger=BoundedEvents(root/'events',root,3)
        logger.emit(dict(kind='fixture_reading',reading=asdict(reading)))
        assert json.loads((root/'events/000001.json').read_text())['sequence']==1
        result['checks']['exclusive_event_fsync_ack']=True
        (root/'status').write_text('Unknown')
        try:reader.read()
        except RuntimeError:result['checks']['unknown_power_rejected']=True
        else:raise AssertionError('unknown battery status accepted')
        captures=[json.loads(p.read_text()) for p in sorted((root/'frames').glob('*.json'))]
        assert len(captures)==2 and captures[0]['frame']['reading'] is not None
        assert captures[1]['frame']['errors'] and captures[1]['frame']['reading'] is None
        assert captures[1]['frame']['raw'][str(root/'status')]=='Unknown'
        result['checks']['all_valid_and_invalid_frames_captured']=True
        (root/'status').write_text('Charging')
        # FIFO is in a fresh Linux tmp directory: DrvFS may not support FIFOs.
        fifo=Path(tempfile.mkdtemp(prefix='sponge-local-unit-'))/'blocked_sensor'
        os.mkfifo(fifo);result['preserved_fixture_fifo']=str(fifo)
        spec['zones'][0]['path']=str(fifo)
        blocked=root/'blocked_spec.json';blocked.write_text(json.dumps(spec))
        import subprocess
        try:BoundedSensors(blocked,sha(blocked),root,2,root/'blocked_frames').read()
        except subprocess.TimeoutExpired:result['checks']['sensor_helper_timeout_rejected']=True
        else:raise AssertionError('potentially blocked reader did not time out')
        code=('import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);'
              'print("ready",flush=True);time.sleep(60)')
        child=OwnGroup([sys.executable,'-c',code],root,stdout=subprocess.PIPE)
        try:
            assert select.select([child.process.stdout],[],[],3)[0]
            assert os.read(child.process.stdout.fileno(),100)==b'ready\n'
            stop_group(child,grace_s=.2)
            assert child.process.returncode==-signal.SIGKILL and not child.group_live()
            result['checks']['own_sleeping_child_TERM_to_KILL_and_reap']=True
        finally:
            stop_group(child)
            child.process.stdout.close()
        session_reader=BoundedSensors(config,sha(config),root,3,root/'session_frames')
        session_events=BoundedEvents(root/'session_events',root,3)
        guard=Guard(Policy(frozenset({'fixture_cpu'}),worker_timeout_s=10))
        plan=[('sleeping_fixture',lambda:OwnGroup([sys.executable,'-c','import time;time.sleep(.2)'],root))]
        controlled=run_session(guard,plan,session_reader.read,session_events.emit,
                               time.monotonic,time.sleep,SessionConfig(stable_power_s=2,poll_s=1))
        result['coordinator_result']=controlled
        assert controlled['status']=='control_flow_completed' and controlled['terminal_journal_ack']
        assert controlled['study_quality']=='NOT_ASSESSED' and controlled['bursts'][0]['rest']['elapsed_s']>=60
        result['checks']['session_preload_power_baseline_and_60s_rest']=True
        files=sorted((root/'session_frames').glob('*.json'))
        assert [p.name for p in files]==[f'{i:06d}.json' for i in range(1,session_reader.sequence+1)]
        assert all(json.loads(p.read_text())['config_sha256']==sha(config) for p in files)
        terminal=json.loads(sorted((root/'session_events').glob('*.json'))[-1].read_text())['event']
        assert terminal['kind']=='session_terminal' and terminal['result']['status']=='control_flow_completed'
        assert 'terminal_journal_ack' not in terminal['result']
        result['checks']['session_all_frames_and_terminal_ACK_retained']=True
        logger.emit(dict(kind='engineering_checks_complete'))
        result['status']='LOCAL_ENGINEERING_CHECKS_PASSED_NOT_DEVICE_QUALIFIED'
    except BaseException as e:
        result.update(status='FAILED',error=type(e).__name__,message=str(e))
        raise
    finally:
        with (root/'receipt.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
        print(json.dumps({k:result[k] for k in ('status','scope','checks')},indent=2),flush=True)


if __name__=='__main__':main(Path(sys.argv[1]))
