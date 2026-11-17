"""Host watchdog fault injection only; no SSH, model, live clock or workload."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types

import pytest

S=Path(__file__).parents[1]/'studies/pi3b_nms_predecessor_20261115'


@pytest.fixture
def campaign(monkeypatch):
    # Bind dependencies locally, without polluting other study modules.
    for name in ('usb_guard','guard','bindings','cache'):
        spec=importlib.util.spec_from_file_location(name,S/(name+'.py'))
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        monkeypatch.setitem(sys.modules,name,mod)
    spec=importlib.util.spec_from_file_location('predecessor_campaign',S/'campaign.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize('failure',[None,'nonzero','timeout','guard','kill_escalation'])
def test_worker_terminal_and_bounded_reaping(campaign,monkeypatch,tmp_path,failure):
    m=campaign;calls=[]
    class Child:
        pid=1234
        returncode=None
        def poll(self):return self.returncode
        def wait(self,timeout):
            calls.append(('wait',timeout))
            if failure=='kill_escalation' and self.returncode is None and ('terminate',) in calls:
                raise subprocess.TimeoutExpired('fake worker',timeout)
            self.returncode=4 if failure=='nonzero' else (-15 if ('terminate',) in calls else 0)
            return self.returncode
        def terminate(self):calls.append(('terminate',))
        def kill(self):calls.append(('kill',));self.returncode=-9
    child=Child()
    monkeypatch.setattr(m.subprocess,'Popen',lambda *a,**k:child)
    monkeypatch.setattr(m,'sys',types.SimpleNamespace(executable=sys.executable,modules={}))
    real_path=Path
    monkeypatch.setattr(m,'Path',lambda x:types.SimpleNamespace(read_text=lambda: '1234 (fake) '+ ' '.join(['S']+['0']*18+['4321']))
        if str(x)=='/proc/1234/stat' else real_path(x))
    monkeypatch.setattr(m,'sha',lambda _: 'a'*64)
    monkeypatch.setattr(m,'load_usb_preflight',lambda *a:({},'b'*64))
    monkeypatch.setattr(m,'load',lambda p: dict(status='COMPLETED_FUNCTIONAL_ONLY',cases=40,empirical_endpoint_recorded=False)
        if str(p).endswith('terminal.json') else {})
    monkeypatch.setattr(m,'read_fast',lambda:dict(vmstat={'pswpin':0,'pswpout':0,'oom_kill':0}))
    checks=[]
    def violations(*a):
        checks.append(1)
        return ['injected_memory_guard'] if failure in ('guard','kill_escalation') and len(checks)==2 else []
    monkeypatch.setattr(m,'violations',violations)
    ticks=iter([0,3601] if failure=='timeout' else [0,1])
    monkeypatch.setattr(m.time,'monotonic',lambda:next(ticks))
    if failure is None:m.collect(tmp_path,'qa','a'*40)
    else:
        with pytest.raises((RuntimeError,TimeoutError)):m.collect(tmp_path,'qa','a'*40)
    receipt=json.loads((tmp_path/'worker_terminal.json').read_text())
    assert receipt['status']==('COMPLETED' if failure is None else 'FAILED_NO_RETRY')
    assert receipt['direct_child_reaped'] is True
    assert receipt['termination_sent']==(failure in ('timeout','guard','kill_escalation'))
    assert child.poll() is not None
    if failure=='kill_escalation':assert ('kill',) in calls
    assert json.loads((tmp_path/'worker_started.json').read_text())['start_ticks']==4321
    assert not (tmp_path/'functional').exists()  # Fake child never runs a model.
