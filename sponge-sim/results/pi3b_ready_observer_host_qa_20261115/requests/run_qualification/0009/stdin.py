from pathlib import Path
import sys,json,subprocess,time,os,signal,hashlib
sys.dont_write_bytecode=True
b=Path('/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115');sys.path.insert(0,str(b));import control
r=b/'runs'/'observer_mainkill_01'
import importlib.util
sys.dont_write_bytecode=True
probe_path=Path('/home/tanh/sponge-sim/pi3b_ready_observer_20261115/probe.py')
assert hashlib.sha256(probe_path.read_bytes()).hexdigest()=='ad9196e38a2d8336262397b36e05b376e10f75397057e1c284c4abce7e598bde'
spec=importlib.util.spec_from_file_location('qualified_ready_candidate',probe_path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
observed=module.observe(b,r.name,control)
if observed is None:print('null')
else:
 ready=observed['ready'];fields=observed['unit']
 print(json.dumps(observed))
