"""Fixed stage-by-stage pool metadata; no model/NMS/RSS/latency endpoint."""
from pathlib import Path
import argparse
import contextlib
import gc
import hashlib
import io
import json
import os
import platform
import traceback

import inventory
import metadata

HERE = Path(__file__).resolve().parent


def context():
    return dict(governor=Path('/sys/devices/system/cpu/cpufreq/policy0/scaling_governor').read_text(),
                swaps=Path('/proc/swaps').read_text(), affinity=sorted(os.sched_getaffinity(0)))


def main(tag, commit):
    out = HERE/'qa_result_01.json'
    if out.exists(): raise FileExistsError('exclusive result exists')
    cfg = json.loads((HERE/'qa_config.json').read_text())
    manifest = json.loads((HERE/'qa_manifest.json').read_text())
    for name, digest in cfg['source_sha256'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest
    assert tag == cfg['tag'] == manifest['tag'] and commit == manifest['commit']
    assert manifest['config_sha256'] == hashlib.sha256((HERE/'qa_config.json').read_bytes()).hexdigest()
    result = dict(tag=tag, commit=commit, source_sha256=cfg['source_sha256'],
        config_sha256=manifest['config_sha256'], before_context=context(), snapshots=[],
        performance_endpoint_recorded=False, nms_endpoint_recorded=False,
        library_ownership_identified=False, simultaneous_execution_qualified=False)
    try:
        assert platform.system() == 'Linux' and platform.machine() == 'aarch64'
        result['python_version'] = platform.python_version()
        assert result['python_version'] == cfg['python_version']
        assert result['before_context']['affinity'] == [0, 1, 2, 3]
        available = next(int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
        assert available >= 400000 and int(Path('/sys/class/thermal/thermal_zone0/temp').read_text()) < 75000
        result['kernel_metadata'] = metadata.kernel_metadata()
        def capture(label):
            x = metadata.stage(label)
            result['snapshots'].append(x)
            assert x['complete'] and x['inventory']['cgroup_path'] == cfg['expected_cgroup']
            assert all(t['affinity'] == [0, 1, 2, 3] for t in x['inventory']['threads'].values())
        capture('baseline')
        import numpy as np
        assert np.__version__ == cfg['numpy_version']
        capture('numpy_import')
        a = np.ones((512, 512), dtype=np.float32); b = a @ a
        assert bool(np.all(b == 512))
        del a, b
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): np.show_config()
        result['numpy_configuration'] = dict(version=np.__version__, show_config=buf.getvalue())
        result['numpy_functional_check'] = dict(mm_invocations=1, shape=[512, 512], exact_value=512, passed=True)
        capture('numpy_mm_and_diagnostics')
        import torch
        assert torch.__version__ == cfg['torch_version']
        capture('torch_import')
        torch.set_num_threads(4)
        capture('torch_set_intraop')
        torch.set_num_interop_threads(1)
        capture('torch_set_interop')
        x = torch.ones((512, 512), dtype=torch.float32)
        capture('torch_ones')
        y = torch.mm(x, x)
        capture('torch_mm')
        assert bool((y == 512).all()) and y.device.type == 'cpu'
        result['torch_functional_check'] = dict(mm_invocations=1, shape=[512, 512], exact_value=512, passed=True)
        del x, y
        gc.collect()
        capture('torch_validation_and_gc')
        result['torch_configuration'] = dict(version=torch.__version__, threads=torch.get_num_threads(),
            interop=torch.get_num_interop_threads(), parallel_info=torch.__config__.parallel_info(),
            environment={k:os.environ.get(k) for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS')})
        capture('torch_diagnostics')
        capture('final_adjacent')
        assert [s['label'] for s in result['snapshots']] == cfg['stages']
        assert len(result['snapshots'][-1]['inventory']['threads']) >= 4
        result['final_delta'] = inventory.increments(result['snapshots'][-2]['inventory'], result['snapshots'][-1]['inventory'])
        result['transitions'] = metadata.transitions(result['snapshots'])
        result['after_context'] = context()
        assert result['after_context'] == result['before_context']
        result['status'] = 'PASS_STAGED_POOL_METADATA_ONLY'
    except BaseException as exc:
        result.update(status='FAIL_STOP_NO_RETRY', error=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
        result['after_context'] = context()
    with out.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, allow_nan=False)
    return 0 if result['status'] == 'PASS_STAGED_POOL_METADATA_ONLY' else 1


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--commit',required=True)
    args=p.parse_args();raise SystemExit(main(args.tag,args.commit))
