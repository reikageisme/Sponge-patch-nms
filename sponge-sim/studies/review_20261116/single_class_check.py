"""Ứng viên tổng hợp một lớp so với 80 lớp ngẫu nhiên (điểm phản biện về lời khuyên "class-batched kernel").
Chỉ đọc summary của E1 trong repo.

    python studies/review_20261116/single_class_check.py <gốc repo> sponge-sim/results/review_20261116

In: thời gian NMS với nc = 1 so với nc = 80 ở các ô đã đo, và danh sách ô nc = 1 CHƯA đo (cần chạy bổ sung).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

repo = Path(sys.argv[1])
out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / 'ket_qua'
out_dir.mkdir(parents=True, exist_ok=True)
curves = json.loads((repo / 'sponge-sim/results/e1/E1_P1cpu2_20261101/summary.json').read_text(encoding='utf-8'))['curves']
cells = {}
for k, v in curves.items():
    prof, A, be, geom, nc, cap, n = k.split('|')
    cells[(int(A), be, geom, int(nc), cap, int(n))] = v['median_ms']
grid = defaultdict(set)
for (A, be, geom, nc, cap, n) in cells:
    grid[(A, nc)].add(n)
md = ['# A2. Một lớp so với 80 lớp ngẫu nhiên', '', '## Lưới đã đo', '', '| Số anchor | nc | Các giá trị N đã đo |', '|---|---|---|']
for (A, nc), ns in sorted(grid.items()):
    md.append(f"| {A} | {nc} | {', '.join(map(str, sorted(ns)))} |")
rows = []
md += ['', '## Ô có cả hai (không cap)', '', '| Anchor | NMS | Hình học | N | nc = 80 (ms) | nc = 1 (ms) | nc1 / nc80 |', '|---|---|---|---|---|---|---|']
for (A, be, geom, nc, cap, n), t in sorted(cells.items()):
    if nc == 80 and cap == 'None' and n >= 1000 and (A, be, geom, 1, cap, n) in cells:
        t1 = cells[(A, be, geom, 1, cap, n)]
        rows.append(dict(anchors=A, backend=be, geometry=geom, n=n, nc80_ms=t, nc1_ms=t1, ratio=t1 / t))
        md.append(f'| {A} | {be} | {geom} | {n} | {t:.3f} | {t1:.3f} | {t1 / t:.2f} |')
big = sorted({A for (A, nc) in grid if nc == 80 and max(grid[(A, 80)]) > 4000})
missing = [A for A in big if (A, 1) not in grid]
big80 = [dict(anchors=A, backend=be, geometry=geom, n=n, ms=t) for (A, be, geom, nc, cap, n), t in sorted(cells.items())
         if nc == 80 and cap == 'None' and n == max(grid[(A, 80)]) and A in big and be in ('tv_nms', 'tv_batched')]
md += ['', '## Ô lớn nhất với nc = 80 (chỗ lời khuyên "class-batched" dựa vào)', '', '| Anchor | NMS | Hình học | N | ms |', '|---|---|---|---|---|']
md += [f"| {r['anchors']} | {r['backend']} | {r['geometry']} | {r['n']} | {r['ms']:.2f} |" for r in big80]
md += ['', '## Kết luận', '',
       '- Ở lưới 2100 anchor, một lớp KHÔNG làm batched NMS đắt hơn; với hộp chồng nhau còn rẻ hơn (tỉ số dưới 1).',
       f"- Lợi thế lớn của `tv_batched` chỉ xuất hiện ở lưới lớn ({', '.join(map(str, big))} anchor), nơi torchvision chạy NMS riêng từng lớp khi có hơn 4000 hộp. Lưới này chưa có nc = 1: {', '.join(map(str, missing)) or 'không thiếu'}.",
       '- Cần đo bổ sung nc = 1 ở lưới lớn trước khi viết "class-batched kernel làm NMS không nhạy". Nếu một lớp xoá lợi thế đó thì lời khuyên phải ghi điều kiện "ứng viên trải trên nhiều lớp".', '',
       'Lệnh gợi ý (cùng giao thức E1, chỉ thêm nc = 1 ở hai lưới lớn; đăng ký trước rồi mới chạy):', '',
       '```bash', 'python sponge-sim/studies/e1_dose/run.py --run-dir sponge-sim/results/e1/E1_nc1_large --nc1-large', '```',
       '(cờ `--nc1-large` đã thêm vào `studies/e1_dose/run.py`: 36 nhóm, nc = 1 và nc = 80 ở 8400 và 10000 anchor, không cap.)']
(out_dir / 'a2_single_class_check.json').write_text(json.dumps(dict(pairs=rows, large_grids=big, large_grids_without_nc1=missing, largest_nc80=big80), indent=1), encoding='utf-8')
(out_dir / 'a2_single_class_check.md').write_text('\n'.join(md), encoding='utf-8')
print('\n'.join(md))
