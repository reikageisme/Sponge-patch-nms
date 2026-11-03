"""Chuẩn bị gói Zenodo (KHÔNG tải lên): python -X utf8 paper_vi/zenodo/make_bundle.py

Tạo zenodo_bundle/ ở gốc kho: bản sao tệp đăng ký trước, DEVIATIONS, script phân tích và sinh bảng, các tệp tóm tắt mà bảng đọc,
và MANIFEST.json ghi SHA-256 + kích thước của mọi tệp đã chép VÀ của mọi bản ghi thô (raw_*.jsonl) mà các tóm tắt dựa vào
(bản ghi thô lớn không chép; người dùng quyết định có tải kèm không). Không xoá hay sửa gì trong sponge-sim/results.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIM = ROOT / 'sponge-sim'
OUT = ROOT / 'zenodo_bundle'
COPY = ['sponge-sim/prereg', 'sponge-sim/DEVIATIONS.md', 'sponge-sim/src/sponge_sim', 'sponge-sim/tests',
        'sponge-sim/studies', 'paper_vi/tables', 'paper_vi/main_vi.tex', 'paper_vi/supplement_vi.tex']
RUNS = ['e1/E1_P1cpu2_20261101', 'e5/AA_P1cpu2_20261101', 'e5/AA640_P1cpu2_20261102', 'e5/AA640_P1cpu2_20261102b', 'e9/E9_P1cpu2_20261102',
        'e10/E10_P1cpu2_20261102', 'e6/E6_P1cpu2_20261102', 'e6/E6A1_P1cpu2_20261102b', 'e6/E6_pooled_baselines_100img', 'amdahl', 'diag_insert']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    files = []
    for rel in COPY:
        src = ROOT / rel
        dst = OUT / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    runs = list(RUNS) + [str(p.parent.relative_to(SIM / 'results')).replace('\\', '/') for p in (SIM / 'results/e11').glob('E11_*/summary.json')]
    raw = []
    for r in runs:
        d = SIM / 'results' / r
        for p in sorted(d.glob('*.json')):
            dst = OUT / 'sponge-sim/results' / r / p.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
        for p in sorted(d.glob('raw_*.jsonl')):
            raw.append(dict(path=str(p.relative_to(ROOT)).replace('\\', '/'), bytes=p.stat().st_size, sha256=sha(p), copied=False))
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name != 'MANIFEST.json':
            files.append(dict(path=str(p.relative_to(OUT)).replace('\\', '/'), bytes=p.stat().st_size, sha256=sha(p)))
    git = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    tags = subprocess.run(['git', '-C', str(ROOT), 'tag', '-l', 'prereg-*', '--format=%(refname:short) %(objectname:short)'], capture_output=True, text=True).stdout.split('\n')
    (OUT / 'MANIFEST.json').write_text(json.dumps(dict(git_head=git, prereg_tags=[t for t in tags if t], files=files, raw_not_copied=raw), indent=1), encoding='utf-8')
    shutil.copy2(Path(__file__).with_name('README_ZENODO.md'), OUT / 'README.md')
    print('files', len(files), 'raw (not copied)', len(raw), '->', OUT)


if __name__ == '__main__':
    main()
