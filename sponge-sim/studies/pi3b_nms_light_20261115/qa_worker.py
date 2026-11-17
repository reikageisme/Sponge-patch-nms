"""One native process/thread resource API pair, no operator/wall-time bracket."""
from pathlib import Path
import argparse
import gc
import hashlib
import json
import os
import platform
import threading
import traceback

import bracket

HERE=Path(__file__).resolve().parent


def context():
    return dict(governor=Path('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor').read_text(),
        swaps=Path('/proc/swaps').read_text(),affinity=sorted(os.sched_getaffinity(0)),gc_enabled=gc.isenabled())


def main(tag,commit):
    out=HERE/'qa_result_01.json'
    if out.exists():raise FileExistsError('exclusive result already exists')
    cfg=json.loads((HERE/'qa_config.json').read_text());manifest=json.loads((HERE/'qa_manifest.json').read_text())
    assert tag==cfg['tag']==manifest['tag'] and commit==manifest['commit']
    assert hashlib.sha256((HERE/'qa_config.json').read_bytes()).hexdigest()==manifest['config_sha256']
    for name,digest in cfg['source_sha256'].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest
    result=dict(tag=tag,commit=commit,source_sha256=cfg['source_sha256'],config_sha256=manifest['config_sha256'],
        before_context=context(),real_wall_bracket_exercised=False,observer_overhead_measured=False,
        model_or_nms_executed=False,rss_endpoint_recorded=False,scientific_timing_qualified=False)
    try:
        assert platform.system()=='Linux' and platform.machine()=='aarch64'
        assert platform.python_version()==cfg['python_version']
        assert result['before_context']['affinity']==[0,1,2,3]
        available=next(int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
        assert available>=400000 and int(Path('/sys/class/thermal/thermal_zone0/temp').read_text())<75000
        result['before']=bracket.sample();result['after']=bracket.sample()
        result['increments']=bracket.increments(result['before'],result['after'])
        for s in (result['before'],result['after']):
            assert s['pid']==os.getpid() and s['calling_tid']==threading.get_native_id()
            assert set(s['process'])==set(s['calling_thread'])==set(bracket.FIELDS)
            assert 'ru_maxrss' not in s['process'] and 'ru_maxrss' not in s['calling_thread']
        assert result['increments']['observer_work_included'] and not result['increments']['unique_wait_cause_identified']
        result['after_context']=context();assert result['after_context']==result['before_context']
        result['status']='PASS_LIGHT_RESOURCE_API_ONLY'
    except BaseException as exc:
        result.update(status='FAIL_STOP_NO_RETRY',error=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        result['after_context']=context()
    with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    return 0 if result['status']=='PASS_LIGHT_RESOURCE_API_ONLY' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--commit',required=True)
    args=p.parse_args();raise SystemExit(main(args.tag,args.commit))
