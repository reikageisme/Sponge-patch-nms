# Adapted from sponge-sim/results/pi3b_renderer_usb_integration_qa_20261115/run_device_qa.py:1-154
# SHA256 b8abcbb0c5d33ac285a91f7746d55f04a961cfe8ee10ac327f7c4f3874ca23f7; same five cases/seconds/assessment, new namespace and lock.
# Adapted from sponge-sim/results/pi3b_renderer_memory_v1_qa_20261114/run_device_qa.py:1-150
# SHA256 cf27a09df8c68d16786d901c0589cfe2c77a7e2ae6bbed218d3cac1e34b621d5; USB namespace/tag plus explicit READY baseline verification.
# Adapted from sponge-sim/results/pi3b_renderer_supervisor_qa_20261114/run_device_qa.py:1-148
# SHA256 e8b0a62222af2cd58daebc3ad4047307fd680dd2666fa36f6ad85ae06966286b; new isolated V1 workspace and QA tag only.
# Adapted from sponge-sim/results/pi3b_full20_qa_20261114/run_device_qa.py:1-145
# SHA256 28ca46efda5f3843ce47490666b2a794a4a8a06e7fa2b10d998f88494987a7c4; new paths/tag and explicit no-Torch/no-scipy readiness only.
"""Five finite sleeping-payload cases for the new renderer workspace.

Local orchestration only. Never imports Torch or starts a scientific smoke.
Only the exact owned local SSH client / verified service main or child is
terminated. Any failed assertion stops the remaining cases, preserving files.
"""
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time

B=Path(__file__).resolve().parent
SSH=['ssh','-i',str(Path(os.environ['USERPROFILE'])/'.ssh/pi_spongepi'),
     '-oBatchMode=yes','-oStrictHostKeyChecking=yes','-oConnectTimeout=10','tanh@192.168.10.11']
REMOTE='/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115'
PY='/home/tanh/sponge-venv/bin/python'
SERVICE='sponge-pi3b-swapguard-v2.service'


def save(name,data):
    with (B/name).open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2)


def remote(script):
    p=subprocess.run([*SSH,PY+' -'],input=script,text=True,capture_output=True,timeout=25)
    if p.returncode:
        raise RuntimeError(p.stderr or p.stdout)
    return json.loads(p.stdout)


def script(case,body):
    assert re.fullmatch('[a-z0-9_]+',case)
    return f"from pathlib import Path\nimport sys,json,subprocess,time,os,signal,hashlib\nb=Path({REMOTE!r});sys.path.insert(0,str(b));import control\nr=b/'runs'/{case!r}\n"+body


READY="""
p=r/'qa_ready.json'
if not p.exists():print('null')
else:
 ready=json.loads(p.read_text())
 assert ready['torch_imported'] is False and ready['scipy_imported'] is False
 x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','MainPID','-p','InvocationID','-p','ActiveState'],capture_output=True,text=True,timeout=10)
 fields=dict(line.split('=',1) for line in x.stdout.splitlines())
 assert fields['ActiveState']=='active' and int(fields['MainPID'])==ready['pid'] and fields['InvocationID']==ready['invocation_id']
 assert int(Path(f"/proc/{ready['child_pid']}/stat").read_text().rsplit(')',1)[1].split()[19])==ready['child_start_ticks']
 assert '/system.slice/sponge-pi3b-swapguard-v2.service' in Path(f"/proc/{ready['child_pid']}/cgroup").read_text()
 now=control.System().current()
 assert not now['swaps'] and all(now['masks'].values()) and now['governor']=='powersave'
 header=json.loads((r/'registration.json').read_text())
 assert control.require_phase_storage(r,b/'controller_lock.json',header['tag'],header['commit'],'qa')==hashlib.sha256((r/'usb_preflight.json').read_bytes()).hexdigest()
 print(json.dumps(dict(ready=ready,unit=fields,observed_at_utc=time.time())))
"""

ASSESS="""
restore=json.loads((r/'restore.json').read_text());ready=json.loads((r/'qa_ready.json').read_text())
state=json.loads((r/'lease_state.json').read_text());activation=json.loads((r/'activation_probe.json').read_text())
assert restore['status']=='RESTORED' and not restore['errors'] and activation['returncode']!=0
p=Path(f"/proc/{ready['child_pid']}/stat")
gone=not p.exists() or int(p.read_text().rsplit(')',1)[1].split()[19])!=ready['child_start_ticks']
assert gone
now=control.System().snapshot();control.validate_snapshot(now)
norm=lambda x:[{k:v for k,v in row.items() if k!='used_kb'} for row in x]
assert now['governor']==state['original']['governor'] and now['setup']==state['original']['setup']
assert norm(now['swaps'])==norm(state['original']['swaps'])
assert now['units']==state['original']['units']
start=json.loads((r/'lease_events.jsonl').read_text().splitlines()[0])['wall_utc']
j=subprocess.run(['journalctl','--utc','--since','@'+str(int(start)),'-u','sponge-pi3b-swapguard-v2.service','--no-pager','-o','short-iso'],capture_output=True,text=True,timeout=10)
assert j.returncode==0
print(json.dumps(dict(case=r.name,restore=restore,activation=activation,child_identity_gone=gone,current=now,journal=j.stdout,supervisor_log=(r/'supervisor.log').read_text(),sha256={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file()})))
"""


def wait_ready(name,proc):
    deadline=time.monotonic()+40
    while time.monotonic()<deadline:
        result=remote(script(name,READY))
        if result:
            save(name+'.ready_observation.json',result)
            return result
        if proc.poll() is not None:
            raise RuntimeError('frontend ended before readiness')
        time.sleep(.5)
    raise TimeoutError('QA did not reach READY')


def main(commit):
    if not re.fullmatch('[0-9a-f]{40}',commit):
        raise ValueError('expected frozen QA commit')
    cases=[('qa_normal_01',15,90,'normal'),('qa_mainkill_01',60,120,'main'),
           ('qa_childkill_01',60,120,'child'),('qa_timeout_01',90,45,'timeout'),
           ('qa_disconnect_01',15,90,'disconnect')]
    outcomes={}
    for name,seconds,limit,kind in cases:
        command=f'{PY} {REMOTE}/control.py launch --mode qa --name {name} --tag qa-pi3b-nms-predecessor-supervisor-20261115 --commit {commit} --qa-seconds {seconds} --qa-timeout {limit}'
        with (B/(name+'.frontend.log')).open('xb') as log:
            proc=subprocess.Popen([*SSH,command],stdout=log,stderr=subprocess.STDOUT)
            try:
                observed=wait_ready(name,proc)
                if kind in ('main','child'):
                    action=script(name,READY.replace(" print(json.dumps(dict(ready=ready,unit=fields,observed_at_utc=time.time())))",''))
                    action += "\ncontrol.record(r/'qa_fault_intent.json',dict(action="+repr(kind)+",ready=ready,unit=fields),True)\n"
                    if kind=='main':
                        action += "x=subprocess.run(['sudo','-n','systemctl','kill','--kill-whom=main','--signal=SIGKILL','sponge-pi3b-swapguard-v2.service'],capture_output=True,text=True,timeout=10)\nassert x.returncode==0\n"
                    else:
                        action += "os.kill(ready['child_pid'],signal.SIGKILL)\n"
                    action += "control.record(r/'qa_fault_sent.json',dict(sent=True),True)\nprint(json.dumps(dict(sent=True)))\n"
                    save(name+'.action.json',dict(command=action,result=remote(action)))
                if kind=='disconnect':
                    proc.terminate()  # exact local child created above, never sshd
                    code=proc.wait(timeout=10)
                    save(name+'.disconnect.json',dict(local_ssh_pid=proc.pid,frontend_exit_code=code,observation=observed,sshd_kept_open=True))
                    deadline=time.monotonic()+90
                    terminal=False
                    while time.monotonic()<deadline:
                        result=remote(script(name,"""
p=r/'restore.json'
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','--value'],capture_output=True,text=True,timeout=10)
print(json.dumps(dict(terminal=p.exists() and x.stdout.strip() in ('inactive','failed',''),state=x.stdout.strip())))
"""))
                        if result['terminal']:
                            terminal=True;break
                        time.sleep(1)
                    if not terminal:raise TimeoutError('restore/service completion not observed')
                else:
                    code=proc.wait(timeout=180)
                assessed=remote(script(name,ASSESS))
                text=(B/(name+'.frontend.log')).read_text(encoding='utf-8',errors='replace')
                if kind=='normal':assert code==0 and 'result: success' in text
                elif kind=='main':assert code!=0 and 'status=9/KILL' in text
                elif kind=='child':assert code!=0 and 'QA child exited unexpectedly: -9' in assessed['supervisor_log']
                elif kind=='timeout':assert code!=0 and 'result: timeout' in text
                elif kind=='disconnect':assert 'Deactivated successfully' in assessed['journal']
                assessed.update(status='PASS_'+kind.upper(),frontend_exit_code=code,launch=command)
                save(name+'.assessment.json',assessed)
                outcomes[name]=assessed['status']
                print(json.dumps(dict(case=name,status=assessed['status'])),flush=True)
            finally:
                if proc.poll() is None:
                    proc.wait(timeout=180)  # bounded QA; let manager cleanup, never restart
    save('device_qa_outcomes.json',dict(status='FIVE_ENGINEERING_CASES_PASS',cases=outcomes,commit=commit,model_inference=False))


if __name__=='__main__':
    main(sys.argv[1])
