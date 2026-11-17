"""Linux engineering check of QA composition with NO Torch/model/load.

Only new owned stub workers, local typed sensor fixtures and event helpers.
Copies the two real child-exit functions verbatim into a stub worker. The stub
does no affinity change or matrix work. This is not Android/proot/device QA
and records no latency/CPU benchmark endpoint.
"""
import hashlib
import inspect
import json
import os
from pathlib import Path
import platform
import random
import sys
import time

from checks import Guard,Policy
import pin_worker
from posix_runtime import BoundedEvents,BoundedSensors,write_new_json
import qa_session as qa
from session import SessionConfig


def main(root):
    if os.name!='posix':raise RuntimeError('local POSIX engineering check only')
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).resolve().parent
    executed=root/'executed_source';executed.mkdir()
    source_hashes={}
    for name in qa.SOURCE_FILES:
        data=(source/name).read_bytes();(executed/name).write_bytes(data)
        source_hashes[name]=hashlib.sha256(data).hexdigest()
    data=Path(__file__).read_bytes();(executed/Path(__file__).name).write_bytes(data)
    source_hashes[Path(__file__).name]=hashlib.sha256(data).hexdigest()
    result=dict(status='INCOMPLETE',scope='LOCAL_FIXTURE_QA_CONTROL_NOT_ANDROID_NOT_TORCH_NOT_AFFINITY_OR_PERFORMANCE',
                platform=platform.platform(),source_sha256=source_hashes,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),checks={})
    try:
        order=[(p,s) for p in ('pin_before_pool','pool_before_pin') for s in ('main','all')]
        random.Random(20261107).shuffle(order)
        cells=[dict(cell_id=f'{i}_{p}_{s}',allowed_cpus=[0],pool_order=p,pin_scope=s,torch_threads=2,
                    matrix_size=256,warmup_matmuls=20,intervals=32,interval_s=.1,
                    max_accounting_slack_fraction=.1,expected_torch_version='NO_TORCH_FIXTURE',
                    expected_torch_init_sha256='a'*64) for i,(p,s) in enumerate(order,1)]
        stub=root/'stub_source';stub.mkdir()
        for name in qa.SOURCE_FILES:(stub/name).write_text('# Engineering stub only. No load or device qualification.\n')
        code='import json,math,sys\nfrom pathlib import Path\n'
        code+=f'FAIL_ID={cells[0]["cell_id"]!r}\n'
        code+='''def execute_to_raw(cfg,path):
    assert 'torch' not in sys.modules
    if cfg['cell_id']==FAIL_ID:
        result=dict(status='preparation_failed',reason='engineering_fixture',profile_qualified=False)
        kind='cell_failed'
    else:
        result=dict(status='diagnostic_recorded',profile_qualified=False,output_finite=True,checksum=1.,
                    qa=dict(decision='FAIL',passed=False,reason='engineering_fixture'))
        kind='cell_done'
    with Path(path).open('x') as f:json.dump(dict(kind=kind,result=result,torch_imported=False,fixture=True),f)
    return result
'''
        code+=inspect.getsource(pin_worker.child_exit_code)+'\n'+inspect.getsource(pin_worker.execute_child)
        (stub/'pin_worker.py').write_text(code)
        hashes={name:hashlib.sha256((stub/name).read_bytes()).hexdigest() for name in qa.SOURCE_FILES}
        values={'cpu.type':'fixture_cpu','cpu.temp':'45000','battery.type':'fixture_battery',
                'battery.temp':'350','soc':'50','status':'Charging'}
        for name,value in values.items():(root/name).write_text(value)
        spec=dict(zones=[dict(id='fixture_cpu',path=str(root/'cpu.temp'),type_path=str(root/'cpu.type'),
                             type_value='fixture_cpu',unit='milli_celsius')],
                  battery=dict(id='fixture_battery',path=str(root/'battery.temp'),type_path=str(root/'battery.type'),
                               type_value='fixture_battery',unit='deci_celsius'),
                  soc_path=str(root/'soc'),status_path=str(root/'status'),
                  charging_values=['Charging'],known_status_values=['Charging','Discharging'])
        config=root/'sensors.json';digest=write_new_json(config,spec)
        reader=BoundedSensors(config,digest,root,5,root/'frames')
        events=BoundedEvents(root/'events',root,5)
        guard=Guard(Policy(frozenset({'fixture_cpu'}),worker_timeout_s=10))
        with qa.CellSpawner(cells,root,root/'preparation_failure',stub,hashes) as spawner:
            controlled=qa.run_cells(cells,guard,spawner.spawn,reader.read,events.emit,
                                    time.monotonic,time.sleep,SessionConfig(.05,.02))
            first=spawner.rows[cells[0]['cell_id']]['child']
            assert first.process.returncode==65 and first.poll()==65 and not first.group_live()
            assert sum(row['started'] for row in spawner.rows.values())==1
        result['checks']['preparation_failure_maps_to_real_exit65_and_group_gone']=True
        assert controlled['status']=='stopped_on_guard' and controlled['reason']=='worker_error'
        assert [b['status'] for b in controlled['bursts']]==['aborted','not_started','not_started','not_started']
        result['checks']['guard_stops_remaining_cells_without_retry']=True
        assert controlled['terminal_journal_ack'] and controlled['qa_terminal_journal_ack']
        terminal=json.loads(sorted((root/'events').glob('*.json'))[-1].read_text())['event']
        assert terminal['kind']=='qa_terminal' and terminal['result']['profile_qualified'] is False
        result['checks']['separate_post_cleanup_terminal_ACK_retained']=True
        frames=sorted((root/'frames').glob('*.json'))
        assert [p.name for p in frames]==[f'{i:06d}.json' for i in range(1,reader.sequence+1)]
        assert all(json.loads(p.read_text())['config_sha256']==digest for p in frames)
        result['checks']['all_fixture_sensor_frames_hash_bound']=True
        with qa.CellSpawner(cells,root,root/'diagnostic_failure',stub,hashes) as spawner:
            # Direct adapter test uses only the no-load stub, not the real worker.
            child=spawner.spawn(cells[1]);child.process.wait(timeout=5)
            assert child.poll()==0 and not child.group_live()
            payload=json.loads(spawner.rows[cells[1]['cell_id']]['raw'].read_text())
            assert payload['result']['qa']['decision']=='FAIL' and payload['result']['profile_qualified'] is False
        result['checks']['complete_diagnostic_FAIL_maps_to_exit0_without_promotion']=True
        assert 'torch' not in sys.modules
        assert all(hashlib.sha256((source/name).read_bytes()).hexdigest()==h for name,h in source_hashes.items())
        result['checks']['parent_sources_unchanged_and_Torch_not_imported']=True
        result.update(status='LOCAL_ENGINEERING_CHECKS_PASS_NOT_DEVICE_QUALIFIED',coordinator_result=controlled,
                      captured_sensor_frames=reader.sequence)
    except BaseException as e:
        result.update(status='FAILED',error=type(e).__name__,message=str(e));raise
    finally:
        result['artifact_sha256']={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(root.rglob('*')) if p.is_file()}
        write_new_json(root/'receipt.json',result)
        print(json.dumps({k:result[k] for k in ('status','scope','checks')},indent=2),flush=True)


if __name__=='__main__':main(sys.argv[1])
