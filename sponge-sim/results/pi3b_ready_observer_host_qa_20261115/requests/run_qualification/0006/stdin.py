from pathlib import Path
import sys,json,subprocess,time,os,signal,hashlib
sys.dont_write_bytecode=True
b=Path('/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115');sys.path.insert(0,str(b));import control
r=b/'runs'/'observer_mainkill_01'
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
assert x.returncode==0
fields=dict(line.split('=',1) for line in x.stdout.splitlines())
assert fields==dict(MainPID='0',ActiveState='inactive')
assert not r.exists()
control.locked_materials(b)
state=control.System().snapshot();control.validate_snapshot(state)
assert not any(control.System().current()['masks'].values())
print(json.dumps(dict(unit=fields,original=state)))
