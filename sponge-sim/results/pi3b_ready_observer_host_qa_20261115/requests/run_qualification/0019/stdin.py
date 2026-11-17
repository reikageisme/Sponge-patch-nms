from pathlib import Path
import sys,json,subprocess,time,os,signal,hashlib
sys.dont_write_bytecode=True
b=Path('/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115');sys.path.insert(0,str(b));import control
r=b/'runs'/'observer_childkill_01'

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
