"""E10-R — đo lại E10 (Overload / Phantom Sponges, YOLOv5s, 640 px) theo góp ý của thầy 27/11/2026.

Nguồn: chép từ `sponge-sim/studies/e10_reference/run.py` (sha256 7e4cf7137ad31e4d23387933c28feaa2edaab7f97a50e32f2159563af5a1dbec,
toàn file, dòng 1-139). File gốc KHÔNG sửa. Khác biệt so với bản gốc (mọi thứ khác giữ nguyên):
  1. Lặp nhiều hơn: micro và pipeline 3 lần khởi động + 20 lần đo (gốc 1 + 3). Seed thứ tự mới (10202/10203).
  2. Mốc thời gian LỒNG trong chính lần gọi toàn trình: sau forward, sau decode, sau lọc tau, sau NMS
     (fwd_ns, dec_ns, flt_ns, nms_in_ns), để so trực tiếp NMS-trong-pipeline với NMS vi mô (mâu thuẫn Bảng 10).
  3. Đếm page fault (ru_minflt, ru_majflt của getrusage) quanh mỗi lần gọi có bấm giờ, ngoài đồng hồ, để kiểm giả thuyết
     "hai mức thời gian do cấp phát bộ nhớ" (chẩn đoán post hoc 27/11, results/review_20261127).
  4. Tuỳ chọn --malloc-fixed (phiên thăm dò riêng): cố định ngưỡng mmap/trim của glibc qua biến môi trường của worker.
  5. Tuỳ chọn --n-images để chạy phiên thăm dò nhỏ hơn.
Xem prereg/PREREG_AMD_REVISION_20261128.md.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import resource
import subprocess
import sys
import time
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))

CONFIG = dict(experiment='E10R', profile='P1_cpu2', min_effective=0.5, n_images=50, seeds=[0, 1, 2, 3, 4],
              methods=['overload', 'phantom_sponges'], tau_list=[.01, .25], tau_nms=.25, iou=.45, nc=80,
              micro_backends=['torch_pure', 'tv_nms', 'tv_batched', 'ultra_native'], micro_warmup=3, micro_repeats=20,
              pipeline_backends=['tv_nms', 'tv_batched', 'ultra_native'], pipeline_warmup=3, pipeline_repeats=20,
              order_seed=10202, latin_seed=10203, images_per_block=5, malloc_fixed=False)
SMOKE = dict(n_images=2, micro_repeats=2, pipeline_repeats=2)
# glibc: đặt bất kỳ biến nào dưới đây sẽ tắt việc tự điều chỉnh ngưỡng; 32 MiB là trần của M_MMAP_THRESHOLD trên 64 bit.
MALLOC_ENV = {'MALLOC_MMAP_THRESHOLD_': str(32 * 1024 * 1024), 'MALLOC_TRIM_THRESHOLD_': str(64 * 1024 ** 3)}


def image_ids(n):
    spec = importlib.util.spec_from_file_location('e5run', SIM / 'studies' / 'e5_protocol' / 'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.IMAGE_IDS[:n]


def faults():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_minflt, r.ru_majflt


def worker(run_dir, cfg):
    from sponge_sim import hw
    cpus = hw.profiles(hw.cpu_topology())[cfg['profile']]
    readback = hw.pin(cpus)
    import numpy as np
    import torch
    torch.set_num_interop_threads(1)
    verify = hw.verify_pin(cpus, min_effective=cfg['min_effective'])
    torch.set_num_threads(len(cpus))
    from sponge_sim import provenance as pv, timing, yolov5_ref
    from sponge_sim.backends import BACKENDS
    from sponge_sim.cohorts import REPO
    w = timing.JsonlWriter(run_dir / f'raw_{cfg["profile"]}.jsonl')
    w.write(dict(kind='pin', profile=cfg['profile'], allowed=cpus, readback=readback, verify=verify, torch_threads=torch.get_num_threads(),
                 malloc_env={k: os.environ.get(k) for k in MALLOC_ENV}))
    if not verify['passed']:
        w.close()
        raise SystemExit('verify ghim FAIL -> dừng (PREREG E10-R)')
    model, LoadImages = yolov5_ref.load()  # kiểm SHA-256 trọng số YOLOv5s, fail-closed
    pert = {}
    ref = REPO / 'outputs/extended_q1_20261002/reference'
    for m in cfg['methods']:
        for s in cfg['seeds']:
            rec = json.loads((ref / f'{m}_seed{s}.json').read_text(encoding='utf-8'))
            path = REPO / rec['perturbation_file'].replace('\\', '/')
            if yolov5_ref.sha256(path) != rec['trained_float_perturbation_sha256']:
                raise SystemExit(f'SHA256 nhiễu loạn lệch bản ghi: {m} seed {s}')
            pert[(m, s)] = torch.from_numpy(np.load(path))
    w.write(dict(kind='perturbations', items={f'{m}|{s}': yolov5_ref.sha256(REPO / json.loads((ref / f'{m}_seed{s}.json').read_text(encoding='utf-8'))['perturbation_file'].replace('\\', '/'))
                                              for m, s in pert}))
    data = REPO / 'outputs/datasets/coco_val2017_extended'
    names = {im['id']: im['file_name'] for im in json.loads((data / 'instances_subset.json').read_text(encoding='utf-8'))['images']}
    ids = image_ids(cfg['n_images'])
    arms = [('clean_a', None, None), ('clean_b', None, None)] + [(m, m, s) for m in cfg['methods'] for s in cfg['seeds']]
    rng = random.Random(cfg['order_seed'])
    orders = timing.latin_blocks(cfg['micro_backends'], len(ids) * len(arms), cfg['latin_seed'])
    porders = timing.latin_blocks(cfg['pipeline_backends'], len(ids) * len(arms), cfg['latin_seed'] + 1)
    k = 0
    ref0 = timing.reference_ms()
    for ii, image_id in enumerate(ids):
        if ii % cfg['images_per_block'] == 0:
            w.write(dict(kind='reference', block=ii // cfg['images_per_block'], **timing.drift(timing.reference_ms(), ref0), wall_utc=time.time()))
        loader = LoadImages(str(data / 'images' / names[image_id]), img_size=640, stride=32, auto=False)
        _, im, _, _, _ = next(iter(loader))
        clean = torch.from_numpy(im).float()[None] / 255
        units = arms[:]
        rng.shuffle(units)
        for name, m, s in units:
            image = clean if m is None else (clean + pert[(m, s)][None]).clamp(0, 1)
            with torch.no_grad():
                raw = model(image)[0][0]
            decoded = yolov5_ref.decode(raw)
            n_by_tau = {str(t): int((decoded[:, 4] > t).sum()) for t in cfg['tau_list']}
            active, _ = pv.tau_filter(decoded, cfg['tau_nms'], None)
            boxes, scores, classes = active[:, :4].contiguous(), active[:, 4].contiguous(), active[:, 5].contiguous()
            base = dict(profile=cfg['profile'], image_id=image_id, arm=name, method=m, seed=s, block=ii // cfg['images_per_block'], n_by_tau=n_by_tau)
            for rep in range(-cfg['micro_warmup'], cfg['micro_repeats']):
                for be in orders[k]:
                    b = BACKENDS[be]
                    f0 = faults()
                    tn = timing.timed(b.run, setup=lambda: (b.prepare(boxes, scores, classes, cfg['nc']), cfg['iou']))[0]
                    f1 = faults()
                    if rep >= 0:
                        w.write(dict(kind='micro', **base, rep=rep, backend=be, nms_input=len(scores), kept=len(tn['result']), nms_ns=tn['ns'],
                                     minflt=f1[0] - f0[0], majflt=f1[1] - f0[1], wall_utc=tn['wall_utc']))
            for rep in range(-cfg['pipeline_warmup'], cfg['pipeline_repeats']):
                for be in porders[k]:
                    b = BACKENDS[be]
                    marks = []

                    def full():
                        with torch.no_grad():
                            r = model(image)[0][0]
                        marks.append(time.perf_counter_ns())
                        d = yolov5_ref.decode(r)
                        marks.append(time.perf_counter_ns())
                        a, _n = pv.tau_filter(d, cfg['tau_nms'], None)
                        marks.append(time.perf_counter_ns())
                        out = b.run(b.prepare(a[:, :4], a[:, 4], a[:, 5], cfg['nc']), cfg['iou'])
                        marks.append(time.perf_counter_ns())
                        return out
                    f0 = faults()
                    tt = timing.timed(full)[0]
                    f1 = faults()
                    if rep >= 0:
                        t0 = tt['t_start_ns']
                        w.write(dict(kind='pipeline', **base, rep=rep, backend=be, total_ns=tt['ns'],
                                     fwd_ns=marks[0] - t0, dec_ns=marks[1] - marks[0], flt_ns=marks[2] - marks[1], nms_in_ns=marks[3] - marks[2],
                                     minflt=f1[0] - f0[0], majflt=f1[1] - f0[1], wall_utc=tt['wall_utc']))
            k += 1
    w.write(dict(kind='reference', block='end', **timing.drift(timing.reference_ms(), ref0), wall_utc=time.time()))
    w.write(dict(kind='pin_end', verify=hw.verify_pin(cpus, min_effective=cfg['min_effective'])))
    w.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', required=True)
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--worker', action='store_true')
    ap.add_argument('--malloc-fixed', action='store_true', help='phiên thăm dò: cố định ngưỡng mmap/trim của glibc')
    ap.add_argument('--n-images', type=int, default=None, help='phiên thăm dò: số ảnh (mặc định theo CONFIG)')
    a = ap.parse_args()
    run_dir = Path(a.run_dir)
    cfg = {**CONFIG, **(SMOKE if a.smoke else {}), 'smoke': a.smoke, 'malloc_fixed': a.malloc_fixed}
    if a.n_images is not None and not a.smoke:  # smoke luôn 2 ảnh
        cfg['n_images'] = a.n_images
    if a.worker:
        worker(run_dir, cfg)
        return
    run_dir.mkdir(parents=True, exist_ok=False)
    from sponge_sim import manifest
    manifest.write(run_dir / 'manifest.json', manifest.build({**cfg, 'malloc_env': MALLOC_ENV if a.malloc_fixed else None},
                                                             extra_files=[SIM / 'src' / 'sponge_sim' / 'yolov5_ref.py']))
    env = {**os.environ, **(MALLOC_ENV if a.malloc_fixed else {})}
    args = ['--run-dir', str(run_dir), '--worker'] + (['--smoke'] if a.smoke else []) + (['--malloc-fixed'] if a.malloc_fixed else [])
    args += ['--n-images', str(cfg['n_images'])]
    t0 = time.time()
    subprocess.run([sys.executable, '-X', 'utf8', '-B', __file__] + args, check=True, env=env)
    print(f'[E10R] xong sau {time.time() - t0:.1f}s', flush=True)
    print('[E10R] DONE', flush=True)


if __name__ == '__main__':
    main()
