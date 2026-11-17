"""ONE engineering service invocation: inventory + fixed functional pool creation.

No model, NMS, mask, ru_maxrss, operator timer or performance endpoint.
This does not qualify simultaneous utilization or overhead of a future tracer.
"""
from pathlib import Path
import argparse
import gc
import hashlib
import json
import os
import platform
import traceback

import inventory

HERE = Path(__file__).resolve().parent


def context():
    return dict(governor=Path('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor').read_text(),
        swaps=Path('/proc/swaps').read_text(), affinity=sorted(os.sched_getaffinity(0)))


def main(tag, commit):
    path = HERE/'qa_result_01.json'
    if path.exists(): raise FileExistsError('exclusive QA result already exists')
    reg = json.loads((HERE/'qa_config.json').read_text())
    manifest = json.loads((HERE/'qa_manifest.json').read_text())
    for name, digest in reg['source_sha256'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest
    assert tag == reg['tag'] and len(commit) == 40
    assert manifest['tag'] == tag and manifest['commit'] == commit
    assert manifest['config_sha256'] == hashlib.sha256((HERE/'qa_config.json').read_bytes()).hexdigest()
    result = dict(tag=tag, commit=commit, scope='Engineering thread/cgroup API + one functional matmul only',
        source_sha256=reg['source_sha256'], config_sha256=hashlib.sha256((HERE/'qa_config.json').read_bytes()).hexdigest(),
        before_context=context(), nms_endpoint_recorded=False, performance_endpoint_recorded=False,
        simultaneous_execution_qualified=False, observer_sham_qualified=False)
    try:
        assert platform.system() == 'Linux' and platform.machine() == 'aarch64'
        assert result['before_context']['affinity'] == [0, 1, 2, 3]
        assert Path('/sys/fs/cgroup/cgroup.controllers').exists()
        memory = dict((x.split(':', 1)[0], x.split(':', 1)[1].strip()) for x in Path('/proc/meminfo').read_text().splitlines())
        assert int(memory['MemAvailable'].split()[0]) >= 400000
        assert int(Path('/sys/class/thermal/thermal_zone0/temp').read_text()) < 75000
        result['pre_import_inventory'] = inventory.snapshot()
        assert result['pre_import_inventory']['cgroup_path'] == reg['expected_cgroup']
        import torch
        assert torch.__version__ == reg['torch_version']
        torch.set_num_threads(4); torch.set_num_interop_threads(1)
        result['torch_configuration'] = dict(version=torch.__version__, threads=torch.get_num_threads(),
            interop=torch.get_num_interop_threads(), parallel_info=torch.__config__.parallel_info(),
            environment={k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS')})
        x = torch.ones((512, 512), dtype=torch.float32)
        y = torch.mm(x, x)
        assert bool((y == 512).all()) and y.device.type == 'cpu'
        result['functional_check'] = dict(shape=[512, 512], operations=1, all_entries_equal=512, exact_pass=True)
        del x, y
        gc.collect()
        result['pool_before'] = inventory.snapshot()
        result['pool_after'] = inventory.snapshot()
        result['pool_delta'] = inventory.increments(result['pool_before'], result['pool_after'])
        for s in (result['pre_import_inventory'], result['pool_before'], result['pool_after']):
            assert s['complete_stable_set'] and s['cgroup_path'] == reg['expected_cgroup']
            assert all(t['affinity'] == [0, 1, 2, 3] for t in s['threads'].values())
        assert len(result['pool_after']['threads']) >= 4
        result['after_context'] = context()
        assert result['after_context'] == result['before_context']
        result['status'] = 'PASS_SERVICE_POOL_INVENTORY_API_ONLY'
    except BaseException as exc:
        result.update(status='FAIL_STOP_NO_RETRY', error=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
        result['after_context'] = context()
    with path.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, allow_nan=False)
    print(json.dumps(dict(status=result['status'], result_sha256=hashlib.sha256(path.read_bytes()).hexdigest())))
    return 0 if result['status'] == 'PASS_SERVICE_POOL_INVENTORY_API_ONLY' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--tag', required=True); p.add_argument('--commit', required=True)
    args = p.parse_args(); raise SystemExit(main(args.tag, args.commit))
