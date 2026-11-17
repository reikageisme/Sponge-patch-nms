# Candidate adapted from sponge-sim/results/pi3b_predecessor_supervisor_qa_20261115/run_device_qa.py:1-156
# SHA256 87198d9ace7e7e071e0ede70caa9b1342183f646d3c740ed1acd3e50a82ac0e6; original failed driver/tag/raw remain immutable.
# New outer qualification is a reviewed exception to no-retry, not the old five-case PASS.
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
PAYLOAD_COMMIT='925c544f618491e5b21a3621d77804a10686d111'
QUALIFICATION_TAG='qa-pi3b-ready-observer-20261115'
sys.path.insert(0,str(B.parents[1]/'studies/pi3b_ready_observer_20261115'))
from transport import capture
from readiness_plan import validate_prelaunch


def save(name,data):
    with (B/name).open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2)


REMOTE_CALL_INDEX=0
REQUEST_ROOT=B/'requests'/Path(sys.argv[0]).stem


def remote(script,remaining=25):
    global REMOTE_CALL_INDEX
    if REMOTE_CALL_INDEX==0:REQUEST_ROOT.mkdir(parents=True,exist_ok=False)
    out=REQUEST_ROOT/f'{REMOTE_CALL_INDEX:04d}';REMOTE_CALL_INDEX+=1
    return capture(script,remaining,out)


def script(case,body):
    assert re.fullmatch('[a-z0-9_]+',case)
    return f"from pathlib import Path\nimport sys,json,subprocess,time,os,signal,hashlib\nsys.dont_write_bytecode=True\nb=Path({REMOTE!r});sys.path.insert(0,str(b));import control\nr=b/'runs'/{case!r}\n"+body


READY="import importlib.util\nsys.dont_write_bytecode=True\nprobe_path=Path('/home/tanh/sponge-sim/pi3b_ready_observer_20261115/probe.py')\nassert hashlib.sha256(probe_path.read_bytes()).hexdigest()=='ad9196e38a2d8336262397b36e05b376e10f75397057e1c284c4abce7e598bde'\nspec=importlib.util.spec_from_file_location('qualified_ready_candidate',probe_path)\nmodule=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)\nobserved=module.observe(b,r.name,control)\nif observed is None:print('null')\nelse:\n ready=observed['ready'];fields=observed['unit']\n print(json.dumps(observed))\n"

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
        result=remote(script(name,READY),remaining=deadline-time.monotonic())
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
    lock=validate_prelaunch(B,commit)
    deployment=json.loads((B/'deployment_verification.json').read_text())
    if deployment['qualification_commit']!=commit or deployment['status']!='EXACT_READY_OBSERVER_SIDECAR_DEPLOYED':raise ValueError('verified sidecar deployment missing')
    cases=[('observer_normal_01',15,90,'normal'),('observer_mainkill_01',60,120,'main'),
           ('observer_childkill_01',60,120,'child'),('observer_timeout_01',90,45,'timeout'),
           ('observer_disconnect_01',15,90,'disconnect')]
    outcomes={}
    for name,seconds,limit,kind in cases:
        preflight=script(name,"x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)\nassert x.returncode==0\nfields=dict(line.split('=',1) for line in x.stdout.splitlines())\nassert fields==dict(MainPID='0',ActiveState='inactive')\nassert not r.exists()\ncontrol.locked_materials(b)\nstate=control.System().snapshot();control.validate_snapshot(state)\nassert not any(control.System().current()['masks'].values())\nprint(json.dumps(dict(unit=fields,original=state)))\n")
        save(name+'.preflight.json',remote(preflight))
        command=f'{PY} {REMOTE}/control.py launch --mode qa --name {name} --tag qa-pi3b-nms-predecessor-supervisor-20261115 --commit {PAYLOAD_COMMIT} --qa-seconds {seconds} --qa-timeout {limit}'
        with (B/(name+'.frontend.log')).open('xb') as log:
            proc=subprocess.Popen([*SSH,command],stdout=log,stderr=subprocess.STDOUT)
            try:
                observed=wait_ready(name,proc)
                if kind in ('main','child'):
                    action=script(name,READY.replace(" print(json.dumps(observed))",'')+"\nassert observed is not None, 'READY lost before fault'\n")
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
    save('qualification_outcomes.json',dict(status='FIVE_READY_OBSERVER_CASES_PASS',cases=outcomes,qualification_tag=QUALIFICATION_TAG,qualification_commit=commit,payload_tag='qa-pi3b-nms-predecessor-supervisor-20261115',payload_commit=PAYLOAD_COMMIT,model_inference=False))


if __name__=='__main__':
    main(sys.argv[1])
