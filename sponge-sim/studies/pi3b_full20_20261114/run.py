# Copied from sponge-sim/studies/pi3b_600mhz_swapguard_v2/run.py:1-424
# SHA256 028a11f97f726941950be4dc406c8138cd3695a42b246a526d5c7519127c611b; parent protocol remains CLOSED and immutable.
# Copied from sponge-sim/studies/pi3b_600mhz/run.py:1-362
# SHA256 9cc349be2c265fb4615d0016e9dae4a5aef53961df0d603abcb42d7a9fdbec8a; original is immutable.
"""PI3B-600MHZ worker: frozen PGD pair replay on a Raspberry Pi 3B clamped at 600 MHz.

Runs ON THE PI (Linux/aarch64). Needs only stdlib + torch/torchvision/ultralytics/numpy/psutil.
No attack optimization, no input selection, no network.

Provenance (rule: old code is copied, never edited):
- pipeline `full`, `pred_proto`, `suppress`, reference block and timing discipline follow
  sponge-sim/studies/laptop_seg/run.py:176-214 (SHA256 23efa8bd9ca8eb685a7d95a28c19ff0365dada31efaf57e3494ffbd0b2558260);
- `observed_suppression` follows sponge-sim/studies/laptop_seg/defense_replay.py:5-23
  (SHA256 of that file is bound in lock.json `derived_from`);
- output lifetime (release after both clock endpoints) follows
  sponge-sim/studies/laptop_seg/output_lifetime.py:11-21.
Windows-only parts of the laptop runner (powrprof, QoS, PDH) are NOT ported; the Pi
equivalents are cpufreq/vcgencmd readbacks recorded outside the timed region.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from guard import read_fast, violations, strict_temp

ARMS = ['clean_total_A', 'clean_total_B', 'adv_total', 'advcap_total', 'clean_forward', 'adv_forward']
STAGE_ARMS = ['nms_clean', 'nms_adv', 'mask_clean', 'mask_adv', 'nms_adv_B', 'mask_adv_B']
POLICY = Path('/sys/devices/system/cpu/cpufreq/policy0')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def arm_order(n_arms, image_index, rep, seed):
    """Seeded shuffle; depends only on (seed, image, rep), never on observed timing."""
    order = list(range(n_arms))
    random.Random(seed + 1000 * image_index + rep).shuffle(order)
    return order


def dose_levels(k_available, levels):
    """Registered K levels that the frozen detection set can supply (no padding, no resampling)."""
    return [k for k in levels if k <= k_available]


def vcgencmd(*a):
    try:
        return subprocess.run(['vcgencmd', *a], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception as e:  # recorded, never silently replaced by a guess
        return f'ERROR:{type(e).__name__}'


def meminfo():
    out = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        k, v = line.split(':', 1)
        if k in ('MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'):
            out[k] = int(v.split()[0])
    return out


def vmstat(keys=('pgmajfault', 'pswpin', 'pswpout', 'oom_kill')):
    out = {}
    for line in Path('/proc/vmstat').read_text().splitlines():
        k, v = line.split()
        if k in keys:
            out[k] = int(v)
    return out


def environment():
    """Read-only board state. Called OUTSIDE every timed region."""
    return dict(governor=(POLICY / 'scaling_governor').read_text().strip(),
                scaling_cur_khz=int((POLICY / 'scaling_cur_freq').read_text()),
                arm_clock_hz=vcgencmd('measure_clock', 'arm'),
                temp=vcgencmd('measure_temp'), throttled=vcgencmd('get_throttled'),
                mem_kb=meminfo(), vmstat=vmstat(), loadavg=os.getloadavg())


def usb_block_devices():
    return sorted(p.name for p in Path('/sys/block').iterdir() if p.name.startswith('sd'))


def load_lock(path, base):
    lock = json.loads(Path(path).read_text())
    for row in lock['files']:
        if sha(base / row['name']) != row['sha256']:
            raise RuntimeError(f'locked file changed: {row["name"]}')
    return lock


def worker(args):
    base = args.base
    lock = load_lock(args.lock, base)
    cfg = lock['smoke' if args.smoke else 'full']
    prof = lock['profiles'][args.profile]
    cpus = prof['cpus']
    if args.mode == 'stages' and args.profile != 'PI4':
        raise RuntimeError('stages mode is registered for PI4 only')
    os.sched_setaffinity(0, cpus)                # before torch imports / thread pools
    assert sorted(os.sched_getaffinity(0)) == cpus
    for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[k] = str(len(cpus))
    import psutil
    import torch
    torch.manual_seed(lock['seed'])
    torch.set_num_threads(len(cpus))
    torch.set_num_interop_threads(1)
    import torchvision                           # fixed compiled NMS, before Ultralytics
    import ultralytics
    from ultralytics import YOLO
    from ultralytics.utils import nms, ops
    import numpy as np
    versions = dict(torch=torch.__version__, torchvision=torchvision.__version__,
                    ultralytics=ultralytics.__version__, numpy=np.__version__,
                    python=sys.version.split()[0])
    if versions != lock['versions']:
        raise RuntimeError(f'runtime version changed: {versions}')
    if sha(nms.__file__) != lock['nms_source_sha256'] or sha(ops.__file__) != lock['ops_source_sha256']:
        raise RuntimeError('runtime nms/ops source changed')
    assert 'torchvision.ops.nms' in Path(nms.__file__).read_text(encoding='utf-8')
    if usb_block_devices():
        raise RuntimeError('external USB storage attached; registered condition is none')
    env0 = environment()
    initial_fast = read_fast()
    errors = violations(initial_fast, lock, cpus)
    if errors:
        raise RuntimeError(f'initial guard: {errors}')
    if env0['governor'] != lock['governor']:
        raise RuntimeError(f'governor is {env0["governor"]}, registered {lock["governor"]}')
    if env0['mem_kb']['SwapTotal'] != 0:
        raise RuntimeError('swap must be off for the registered condition')
    proc = psutil.Process()
    manifest = dict(experiment='PI3B-FULL20-POST-PILOT', mode=args.mode, smoke=args.smoke, profile=args.profile,
                    cpu_set=cpus, config=cfg, lock_sha256=sha(args.lock), runner_sha256=sha(__file__),
                    tag=args.tag, prereg_commit=args.commit, versions=versions,
                    model=Path('/proc/device-tree/model').read_text().strip('\x00'),
                    kernel=os.uname().release, machine=os.uname().machine,
                    torch_threads=torch.get_num_threads(), interop_threads=torch.get_num_interop_threads(),
                    parallel_info=torch.__config__.parallel_info(), environment_start=env0,
                    firmware=vcgencmd('version'), usb_block_devices=usb_block_devices(),
                    backend='torchvision.ops.nms inside locked Ultralytics wrapper',
                    weights_sha256=sha(base / lock['weights']), argv=sys.argv,
                    initial_fast=initial_fast, guard_policy='pre_post_every_clocked_call_v2')
    (args.run_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    fh = (args.run_dir / 'raw.jsonl').open('x', encoding='utf-8')
    pending = []
    guard_sequence = 0

    def write(**row):
        pending.append(dict(wall_utc=time.time(), **row))

    def flush():
        for row in pending:
            fh.write(json.dumps(row, allow_nan=False) + '\n')
        fh.flush()
        os.fsync(fh.fileno())
        pending.clear()

    def timed(fn):
        nonlocal guard_sequence
        guard_sequence += 1
        gid = guard_sequence
        fast = read_fast()
        problems = violations(fast, lock, cpus, initial_fast['vmstat'])
        write(kind='guard', guard_id=gid, phase='pre', fast=fast, violations=problems)
        if problems:
            raise RuntimeError(f'pre-clock guard: {problems}')
        enabled = gc.isenabled()
        gc.disable()
        try:
            c0 = time.process_time_ns()
            t0 = time.perf_counter_ns()
            result = fn()
            ns = time.perf_counter_ns() - t0
            cpu_ns = time.process_time_ns() - c0
            del result                             # released AFTER both clock endpoints
        finally:
            if enabled:
                gc.enable()
        try:
            fast = read_fast()
            problems = violations(fast, lock, cpus, initial_fast['vmstat'])
        except Exception as e:
            write(kind='guard', guard_id=gid, phase='post', fast=None,
                  violations=['read_failed'],error=str(e),ns=ns,t_start_ns=t0,process_cpu_ns=cpu_ns)
            raise
        write(kind='guard', guard_id=gid, phase='post', fast=fast, violations=problems,
              ns=ns, t_start_ns=t0, process_cpu_ns=cpu_ns)
        if problems:
            raise RuntimeError(f'post-clock guard: {problems}; completed duration retained in guard row')
        return ns, t0, cpu_ns, gid

    def verify_pin(label):
        before = psutil.cpu_times(percpu=True)
        x = torch.randn(256, 256)
        end = time.perf_counter() + cfg['pin_seconds']
        while time.perf_counter() < end:
            x @ x
        after = psutil.cpu_times(percpu=True)
        busy = []
        for b, a in zip(before, after):
            total = sum(a) - sum(b)
            busy.append(0.0 if total <= 0 else 1 - ((a.idle + a.iowait) - (b.idle + b.iowait)) / total)
        inside = sum(busy[c] for c in cpus)
        outside = sum(v for c, v in enumerate(busy) if c not in cpus)
        need = .5 if len(cpus) == 1 else .7 * len(cpus)
        passed = inside >= need and (len(cpus) == len(busy) or outside < .5)
        write(kind=label, busy=busy, inside=inside, outside=outside, need=need, passed=passed,
              affinity=sorted(os.sched_getaffinity(0)))
        flush()
        if not passed:
            raise RuntimeError('pin load gate failed')

    net = YOLO(str(base / lock['weights'])).model.eval().float().cpu()
    for p in net.parameters():
        p.requires_grad_(False)

    def tensors(raw):
        if torch.is_tensor(raw):
            yield raw
        elif isinstance(raw, (tuple, list)):
            for x in raw:
                yield from tensors(x)
        elif isinstance(raw, dict):
            for x in raw.values():
                yield from tensors(x)

    def pred_proto(raw):
        ts = list(tensors(raw))
        pred = next(t for t in ts if t.ndim == 3 and t.shape[1] == 116)
        proto = next(t for t in ts if t.ndim == 4 and t.shape[1] == 32)
        return pred, proto[0]

    def suppress(pred, max_det=300, max_nms=30000):
        return nms.non_max_suppression(pred, conf_thres=.25, iou_thres=.45,
                                       nc=80, max_det=max_det, max_nms=max_nms)[0]

    def full(image, max_det=300, max_nms=30000):
        pred, proto = pred_proto(net(image))
        det = suppress(pred, max_det=max_det, max_nms=max_nms)
        if not len(det):
            return None
        return ops.process_mask_native(proto, det[:, 6:], det[:, :4], (640, 640))

    def observed_suppression(pred, setting):
        original = torchvision.ops.nms
        calls = []

        def recorded(boxes, scores, iou_threshold):
            calls.append(len(scores))
            return original(boxes, scores, iou_threshold)

        torchvision.ops.nms = recorded
        try:
            det = suppress(pred.clone(), **setting)
        finally:
            torchvision.ops.nms = original
        if len(calls) > 1:
            raise RuntimeError('unexpected multiple NMS kernel invocations')
        return det, 0 if not calls else calls[0]

    def load_pair(name):
        pair = torch.load(base / name, map_location='cpu', weights_only=True)
        clean, adv = pair['clean'].contiguous(), pair['attacked'].contiguous()
        for t in (clean, adv):
            assert t.shape == (1, 3, 640, 640) and t.dtype == torch.float32 and torch.isfinite(t).all()
        if adv.min() < 0 or adv.max() > 1 or (adv - clean).abs().max() > 16 / 255 + 1e-6:
            raise RuntimeError('frozen input budget/range check failed')
        return clean, adv

    names = lock['inputs'][:cfg['n_images']]
    cap = lock['defense']
    ref_image = load_pair(names[0])[0]
    reference0 = None

    def reference(block):
        nonlocal reference0
        for _ in range(cfg['reference_warmup']):
            net(ref_image)
        samples = [timed(lambda: net(ref_image))[0] for _ in range(cfg['reference_samples'])]
        median = float(np.median(samples))
        reference0 = median if reference0 is None else reference0
        write(kind='reference', block=block, samples_ns=samples, ratio=median / reference0,
              flagged=abs(median / reference0 - 1) > lock['gates']['reference_drift'])

    def guard(block):
        env = environment()
        write(kind='environment', block=block, **env)
        if sorted(os.sched_getaffinity(0)) != cpus:
            raise RuntimeError('affinity changed')
        fast = read_fast()
        problems = violations(fast, lock, cpus, initial_fast['vmstat'])
        write(kind='condition', block=block, fast=fast, violations=problems)
        if problems:
            raise RuntimeError(f'condition guard: {problems}')
        if env['governor'] != lock['governor'] or env['mem_kb']['SwapTotal'] != 0:
            raise RuntimeError('swap/governor condition changed')
        hz = int(env['arm_clock_hz'].split('=')[1])
        if not lock['gates']['clock_hz'][0] <= hz <= lock['gates']['clock_hz'][1]:
            raise RuntimeError('actual arm clock outside registered band')
        temp = strict_temp(env['temp'])
        if not temp < lock['gates']['abort_temp_c']:
            raise RuntimeError(f'temperature stop: {env["temp"]}')
        if env['mem_kb']['MemAvailable'] < lock['gates']['abort_mem_available_kb']:
            raise RuntimeError('memory stop')

    try:
        with torch.inference_mode():
            verify_pin('pin_start')
            for _ in range(cfg['global_warmup']):
                full(ref_image)
            reference('start')
            for ix, name in enumerate(names):
                stem = name.split('_')[0]
                guard(ix)
                clean, adv = load_pair(name)        # one pair in memory, loaded outside every clock
                reference(ix)
                counts = {}
                preds = {}
                for arm, im in (('clean', clean), ('adv', adv)):
                    pred, proto = pred_proto(net(im))
                    det, kernel_n = observed_suppression(pred, dict(max_det=300, max_nms=30000))
                    n_tau = int((pred[:, 4:84].amax(1) > .25).sum())
                    counts[arm] = dict(n_tau=n_tau, kernel_n=kernel_n, k=len(det),
                                       prediction_sha256=hashlib.sha256(pred.numpy().tobytes()).hexdigest())
                    preds[arm] = (pred, proto, det)
                det_cap, kernel_cap = observed_suppression(preds['adv'][0], cap)
                counts['advcap'] = dict(n_tau=counts['adv']['n_tau'], kernel_n=kernel_cap, k=len(det_cap), options=cap)
                if kernel_cap != min(counts['adv']['n_tau'], cap['max_nms']) or len(det_cap) > cap['max_det']:
                    raise RuntimeError('defense boundary/count contract failed')
                write(kind='counts', image=stem, block=ix, counts=counts, proto_shape=list(preds['clean'][1].shape))
                if args.mode == 'pipeline':
                    del preds
                    work = [('clean_total_A', lambda: full(clean), lambda: ()),
                            ('clean_total_B', lambda: full(clean), lambda: ()),
                            ('adv_total', lambda: full(adv), lambda: ()),
                            ('advcap_total', lambda: full(adv, **cap), lambda: ()),
                            ('clean_forward', lambda: net(clean), lambda: ()),
                            ('adv_forward', lambda: net(adv), lambda: ())]
                    assert [w[0] for w in work] == ARMS
                else:
                    def mask_job(proto, det):
                        return lambda: None if not len(det) else ops.process_mask_native(
                            proto, det[:, 6:], det[:, :4], (640, 640))
                    pc, prc, dc = preds['clean']
                    pa, pra, da = preds['adv']
                    work = [('nms_clean', lambda p: suppress(p), lambda: (pc.clone(),)),
                            ('nms_adv', lambda p: suppress(p), lambda: (pa.clone(),)),
                            ('mask_clean', mask_job(prc, dc), lambda: ()),
                            ('mask_adv', mask_job(pra, da), lambda: ()),
                            ('nms_adv_B', lambda p: suppress(p), lambda: (pa.clone(),)),
                            ('mask_adv_B', mask_job(pra, da), lambda: ())]
                    assert [w[0] for w in work] == STAGE_ARMS
                    if ix < cfg['dose_images']:
                        for k in dose_levels(len(da), lock['dose_levels']):
                            work.append((f'maskdose_{k}', mask_job(pra, da[:k]), lambda: ()))
                for _, fn, setup in work:
                    for _ in range(cfg['warmup_per_image']):
                        fn(*setup())
                for rep in range(cfg['repeats'][f'{args.mode}_{args.profile}']):
                    for pos, j in enumerate(arm_order(len(work), ix, rep, lock['seed'])):
                        arm, fn, setup = work[j]
                        arguments = setup()          # clones made outside the clock
                        ns, start, cpu_ns, gid = timed(lambda f=fn, a=arguments: f(*a))
                        write(kind='timing', image=stem, block=ix, arm=arm, rep=rep, position=pos,
                              ns=ns, t_start_ns=start, process_cpu_ns=cpu_ns, guard_id=gid)
                write(kind='memory', image=stem, info=proc.memory_info()._asdict())
                flush()
                del work, clean, adv
                gc.collect()
            reference('end')
            guard('end')
            verify_pin('pin_end')
        write(kind='done', affinity=sorted(os.sched_getaffinity(0)), environment_end=environment())
    except BaseException as e:
        write(kind='aborted', error=type(e).__name__, message=str(e))
        raise
    finally:
        flush()
        fh.close()


def main(args):
    """Preserve preparation failures, including failures before Torch/manifest/raw."""
    if args.smoke:
        raise ValueError('No repeat smoke: retain the failed v2 pilot')
    args.run_dir.mkdir(parents=True, exist_ok=False)
    preparation = dict(wall_utc=time.time(), argv=sys.argv, runner_sha256=sha(__file__),
                       status='PREPARING', profile=args.profile, mode=args.mode)
    (args.run_dir / 'preparation.json').write_text(json.dumps(preparation, indent=2), encoding='utf-8')
    try:
        worker(args)
    except BaseException as e:
        terminal = dict(status='FAILED', error=type(e).__name__, message=str(e), wall_utc=time.time())
        if not (args.run_dir / 'raw.jsonl').exists():
            with (args.run_dir / 'raw.jsonl').open('x', encoding='utf-8') as f:
                f.write(json.dumps(dict(kind='preparation_failed', **terminal)) + '\n')
        raise
    else:
        terminal = dict(status='COMPLETED', wall_utc=time.time())
    finally:
        # Uncatchable termination may leave this absent; the systemd supervisor owns cleanup.
        if 'terminal' in locals():
            with (args.run_dir / 'terminal.json').open('x', encoding='utf-8') as f:
                json.dump(terminal, f, indent=2)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--lock', type=Path, required=True)
    ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--run-dir', type=Path, required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--commit', required=True)
    ap.add_argument('--profile', choices=['PI4', 'PI1'], required=True)
    ap.add_argument('--mode', choices=['pipeline', 'stages'], required=True)
    ap.add_argument('--smoke', action='store_true')
    main(ap.parse_args())
