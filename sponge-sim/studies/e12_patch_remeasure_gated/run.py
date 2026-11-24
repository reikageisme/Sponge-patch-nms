"""E12 (BẢN NHÁP, chưa đăng ký trước, chưa chạy trên dữ liệu thật): đo lại bảng patch của E11 với cổng trôi theo khối.

Vì sao: E11 đã sửa lỗi bấm giờ của E6 (bước chèn patch nằm ngoài vùng đo) nhưng cả phiên bị loại vì 11/11 điểm tham chiếu
bị cờ trôi, nên cột end-to-end của bảng patch trong bài chỉ là số dự đoán. Ở đây:
  - phép đo của từng ảnh GIỐNG HỆT E11 (dùng lại ARMS, CONFIG, build_input, pipeline_fn của studies/e11_patch_remeasure/run.py);
  - mỗi khối 10 ảnh được đo trọn rồi mới ghi; điểm tham chiếu đo trước và sau khối (timing.DriftGate);
  - khối bị trôi quá 3% được đo lại, tối đa GATE['max_retries'] lần, chờ GATE['cooldown_s'] giây; hết lượt thì dừng phiên;
  - mọi lần thử, kể cả lần bị bỏ, được ghi vào raw (kind='block_attempt'); dòng đo của lần bị bỏ KHÔNG được ghi;
  - trên Linux, phiên chỉ bắt đầu khi hw_linux.lock_status(cpu)['ready'] là True (bỏ qua bằng --no-lock-check, có ghi vào manifest).
Trước khi đo thật: viết prereg/PREREG_E12.md từ prereg/DRAFT_PREREG_E12_patch_remeasure_gated.md, commit và gắn tag.

    python studies/e12_patch_remeasure_gated/run.py --run-dir results/e12/<id> --e7-dir results/e7_gpu/final/runs/e7 [--smoke]

Phần vòng khối (run_blocks) được kiểm bằng dữ liệu giả trong tests/test_review_fixes.py; phần đo cần ultralytics, ảnh và patch
nên CHƯA được chạy thử.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import random
import sys
import time
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))
sys.path.insert(0, str(SIM / 'studies' / 'e5_protocol'))

GATE = dict(flag=0.03, max_retries=3, cooldown_s=60.0)


def load_e11():
    spec = importlib.util.spec_from_file_location('e11run', SIM / 'studies' / 'e11_patch_remeasure' / 'run.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_blocks(blocks, measure_block, gate, writer):
    """blocks: list (chỉ số khối, danh sách ảnh). measure_block(bi, ids) -> list dòng raw (chưa ghi).
    Ghi các dòng của lần đo được nhận, theo thứ tự khối. SessionAbort (trôi kéo dài) được ghi rồi ném tiếp."""
    from sponge_sim import timing
    gate.start()
    done = 0
    try:
        for bi, ids in blocks:
            for row in gate.run_block(bi, lambda: measure_block(bi, ids)):
                writer.write(row)
            done += 1
    except timing.SessionAbort as e:
        writer.write(dict(kind='abort', reason=str(e), blocks_done=done, wall_utc=time.time()))
        raise
    finally:
        writer.write(dict(kind='gate_summary', **gate.summary(), blocks_done=done, wall_utc=time.time()))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', required=True)
    ap.add_argument('--profile', default='P1_cpu2')
    ap.add_argument('--e7-dir', required=True)
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--no-lock-check', action='store_true', help='bỏ kiểm khoá tần số (Linux); được ghi vào manifest')
    a = ap.parse_args()
    e11 = load_e11()
    ARMS, CLEAN, PATCHED, FINAL_Q = e11.ARMS, e11.CLEAN, e11.PATCHED, e11.FINAL_Q
    cfg = dict(e11.CONFIG, experiment='E12', smoke=a.smoke, profile=a.profile, gate=GATE)
    if a.smoke:
        cfg.update(n_images=2, seeds=[0], micro_repeats=2, pipeline_repeats=1, images_per_block=1)
    run_dir = Path(a.run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)

    linux = platform.system() == 'Linux'
    if linux:
        from sponge_sim import hw_linux as hw
    else:
        from sponge_sim import hw
    cpus = hw.profiles(hw.cpu_topology() if not linux else None)[a.profile]
    lock = hw.lock_status(cpus[0]) if linux else dict(ready=None, note='không phải Linux: không kiểm được khoá tần số')
    if linux and not lock['ready'] and not a.no_lock_check:
        raise SystemExit('môi trường chưa khoá: ' + '; '.join(lock['problems']))
    readback = hw.pin(cpus)
    import numpy as np
    import torch
    torch.set_num_interop_threads(1)
    verify = hw.verify_pin(cpus, min_effective=cfg['min_effective'])
    torch.set_num_threads(len(cpus))
    from ultralytics import YOLO
    from sponge_sim import attacks_provenance as ap_, cohorts, manifest, provenance as pv, timing
    from sponge_sim.backends import BACKENDS
    from run import IMAGE_IDS  # cùng 100 ảnh với E5/E6/E11 (studies/e5_protocol/run.py)
    repo = cohorts.REPO
    if not verify['passed']:
        raise SystemExit('verify ghim FAIL -> dừng')

    want = {}
    for r in json.loads((Path(a.e7_dir) / 'patches_index.json').read_text(encoding='utf-8')):
        if r['queries'] == FINAL_Q:
            want[(Path(r['path']).parts[0], int(r['seed']))] = r['patch_sha256']
    patches, patch_sha = {}, {}
    for arm in PATCHED:
        name, canvas, _, _ = ARMS[arm]
        for s in cfg['seeds']:
            path = Path(a.e7_dir) / name / f'seed{s}' / (f'patch_q{FINAL_Q}' + (f'_c{canvas}' if canvas != 320 else '') + '.npy')
            arr = np.load(path)
            got = e11.sha256_array(arr)
            if want.get((name, s)) != got:
                raise SystemExit(f'SHA256 patch không khớp bản ghi GPU: {arm} seed {s}')
            patches[(arm, s)] = torch.from_numpy(arr)
            patch_sha[f'{arm}|{s}'] = dict(path=str(path), sha256=got)

    manifest.write(run_dir / 'manifest.json', manifest.build(dict(cfg, arms=list(ARMS), patch_sha=patch_sha, lock_status=lock,
                                                                 lock_check_skipped=bool(a.no_lock_check))))
    data = repo / 'outputs/datasets/coco_val2017_extended'
    names = {im['id']: im['file_name'] for im in json.loads((data / 'instances_subset.json').read_text(encoding='utf-8'))['images']}
    model = YOLO(str(repo / 'yolov8n.pt')).model.eval().float()
    clean_hist = cohorts.records(cohorts.read_case('X1-500', 'clean', 0, 0))
    w = timing.JsonlWriter(run_dir / f'raw_{a.profile}.jsonl')
    w.write(dict(kind='pin', profile=a.profile, allowed=cpus, readback=readback, verify=verify, torch_threads=torch.get_num_threads(), lock_status=lock))

    orders = timing.latin_blocks(cfg['backends'], 40000, cfg['latin_seed'])
    porders = timing.latin_blocks(cfg['pipeline_backends'], 40000, cfg['latin_seed'] + 1)
    ids_all = IMAGE_IDS[:cfg['n_images']]
    k = cfg['images_per_block']
    blocks = [(bi, ids_all[bi * k:(bi + 1) * k]) for bi in range((len(ids_all) + k - 1) // k)]
    units_per_image = len(CLEAN) + len(PATCHED) * len(cfg['seeds'])

    def measure_block(bi, ids):
        """Đo một khối. Thứ tự đơn vị và thứ tự backend là hàm tất định của (ảnh, vị trí), nên lần đo lại dùng đúng thứ tự cũ."""
        rows = []
        for pos, image_id in enumerate(ids):
            gi = bi * k + pos
            bases = {c: ap_.load_image_canvas(data / 'images' / names[image_id], c) for c in (320, 640)}
            units = [(arm, None) for arm in CLEAN] + [(arm, s) for arm in PATCHED for s in cfg['seeds']]
            random.Random(cfg['order_seed'] * 100003 + image_id).shuffle(units)
            for ui, (arm, seed) in enumerate(units):
                order_k = gi * units_per_image + ui
                _, canvas, location, size = ARMS[arm]
                base = bases[canvas]
                loc = None
                if seed is not None:
                    loc = ap_.find_locations([base], size, location, (seed if location != 'saliency' else 0) + image_id, canvas=canvas)[0]
                img = e11.build_input(arm, base, patches.get((arm, seed)), loc, ap_.insert)       # NGOÀI vùng đo, như E11
                with torch.no_grad():
                    raw = model(img)
                raw = raw[0] if isinstance(raw, (tuple, list)) else raw
                decoded = pv.decode(raw[0])
                n_by_tau = {t: int((decoded[:, 4] > t).sum()) for t in cfg['tau_list']}
                if arm in ('clean_a', 'clean_b') and image_id in clean_hist and n_by_tau[0.01] != clean_hist[image_id]['active_candidates']:
                    raise SystemExit(f'lệch N so với bản ghi X1-500 đã khoá: ảnh {image_id} {arm} (fail-closed như E11)')
                base_row = dict(profile=a.profile, image_id=image_id, arm=arm, seed=seed, canvas=canvas, location=loc, block=bi,
                                n_by_tau={str(t): n for t, n in n_by_tau.items()})
                for tau in cfg['tau_list']:
                    active, _ = pv.tau_filter(decoded, tau, None)
                    boxes, scores, classes = active[:, :4].contiguous(), active[:, 4].contiguous(), active[:, 5].contiguous()
                    for rep in range(-cfg['micro_warmup'], cfg['micro_repeats']):
                        for name in orders[order_k]:
                            b = BACKENDS[name]
                            tt = timing.timed(pv.tau_filter, setup=lambda: (decoded, tau, None))[0]
                            tn = timing.timed(b.run, setup=lambda: (b.prepare(boxes, scores, classes), cfg['iou']))[0]
                            if rep >= 0:
                                rows.append(dict(kind='micro', **base_row, tau=tau, rep=rep, backend=name, nms_input=len(scores),
                                                 kept=len(tn['result']), tau_ns=tt['ns'], nms_ns=tn['ns'], wall_utc=tn['wall_utc']))
                for rep in range(-cfg['pipeline_warmup'], cfg['pipeline_repeats']):
                    for name in porders[order_k]:
                        r = timing.timed(e11.pipeline_fn(model, img, BACKENDS[name], cfg['iou'], pv, torch))[0]
                        if rep >= 0:
                            rows.append(dict(kind='pipeline', **base_row, rep=rep, backend=name, total_ns=r['ns'], wall_utc=r['wall_utc']))
        return rows

    gate = timing.DriftGate(writer=w, **GATE)
    try:
        run_blocks(blocks, measure_block, gate, w)
    finally:
        w.close()
    print('[E12] DONE', gate.summary(), flush=True)


if __name__ == '__main__':
    main()
