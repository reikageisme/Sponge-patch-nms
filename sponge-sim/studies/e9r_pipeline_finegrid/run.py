"""E9-R — tiêm ứng viên vào toàn pipeline với lưới N mịn hơn ở đầu thấp (góp ý của thầy 27/11/2026: N* rơi vào mức thấp nhất).

Dùng LẠI nguyên worker của `sponge-sim/studies/e9_pipeline/run.py` (sha256 8dc07b9fc2fb73a4db67660aa4bfa903c31d08e2e91743cae718eddc57f68e46),
không chép, không sửa file đó: nạp module rồi gọi `worker(run_dir, cfg)` với cấu hình dưới đây. Khác biệt duy nhất so với E9:
  - lưới N: 320 px {0, 10, 30, 50, 100, 300, 1000, 2100}; 640 px {0, 10, 30, 50, 100, 300, 1000, 3000, 8400};
  - tên thí nghiệm E9R và seed thứ tự mới (9202/9203). Cùng 20 ảnh, cùng hình học, cap, số lần lặp, seed tập tiêm (theo N).
Xem prereg/DRAFT_PREREG_AMD_REVISION_20261127.md.
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import time
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))
_spec = importlib.util.spec_from_file_location('e9run', SIM / 'studies' / 'e9_pipeline' / 'run.py')
e9 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e9)

CONFIG = {**e9.CONFIG, 'experiment': 'E9R', 'cell_order_seed': 9202, 'latin_seed': 9203,
          'canvases': [dict(canvas=320, anchors=2100, n=[0, 10, 30, 50, 100, 300, 1000, 2100], warmup=1, repeats=5),
                       dict(canvas=640, anchors=8400, n=[0, 10, 30, 50, 100, 300, 1000, 3000, 8400], warmup=1, repeats=3)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', required=True)
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--worker', action='store_true')
    a = ap.parse_args()
    run_dir = Path(a.run_dir)
    cfg = {**CONFIG, **(e9.SMOKE if a.smoke else {}), 'smoke': a.smoke}
    if a.worker:
        e9.worker(run_dir, cfg)
        return
    run_dir.mkdir(parents=True, exist_ok=False)
    from sponge_sim import manifest
    n_cells = {c['canvas']: len(e9.cells(cfg, c)) for c in cfg['canvases']}
    manifest.write(run_dir / 'manifest.json', manifest.build({**cfg, 'cells_per_image': n_cells},
                                                             extra_files=[SIM / 'studies' / 'e9_pipeline' / 'run.py']))
    t0 = time.time()
    subprocess.run([sys.executable, '-X', 'utf8', __file__, '--run-dir', str(run_dir), '--worker'] + (['--smoke'] if a.smoke else []), check=True)
    print(f'[E9R] xong sau {time.time() - t0:.1f}s', flush=True)
    print('[E9R] DONE', flush=True)


if __name__ == '__main__':
    main()
