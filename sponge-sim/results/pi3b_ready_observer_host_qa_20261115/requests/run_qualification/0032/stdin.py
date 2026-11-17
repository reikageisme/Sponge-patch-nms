from pathlib import Path
import sys,json,subprocess,time,os,signal,hashlib
sys.dont_write_bytecode=True
b=Path('/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115');sys.path.insert(0,str(b));import control
r=b/'runs'/'observer_disconnect_01'

p=r/'restore.json'
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','--value'],capture_output=True,text=True,timeout=10)
print(json.dumps(dict(terminal=p.exists() and x.stdout.strip() in ('inactive','failed',''),state=x.stdout.strip())))
