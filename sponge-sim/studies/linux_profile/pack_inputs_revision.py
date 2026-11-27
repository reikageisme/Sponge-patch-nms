"""Đóng gói đầu vào cho đợt đo lại 28/11/2026 (E9-R, E10-R) để mang sang Xubuntu live.

Chạy trên Windows, từ thư mục repo GỐC (nơi có outputs/, yolov8n.pt), CHỈ ĐỌC dữ liệu nguồn:
    python -X utf8 <đường-dẫn>/pack_inputs_revision.py D:/Sponge-patch-study D:/Sponge-patch-study/transfer/inputs_revision_20261128.tar

Tar chứa đúng các file runner cần, giữ đường dẫn tương đối so với gốc repo, kèm INPUTS_SHA256.txt (sha256sum -c được).
Trên máy live: giải nén vào gốc bản clone git rồi `sha256sum -c INPUTS_SHA256.txt`.
Các runner tự kiểm SHA-256 của trọng số YOLOv5s và từng nhiễu loạn (fail-closed); file này chỉ để kiểm việc chép.
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path

METHODS = ('overload', 'phantom_sponges')
SEEDS = range(5)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def files(root: Path) -> list[Path]:
    out = [root / 'yolov8n.pt', root / 'outputs/weights/reference/yolov5s.pt',
           root / 'outputs/extended_q1_20261002/reference/manifest.json']
    for d in ('outputs/vendor_underload', 'outputs/runtime/reference', 'outputs/datasets/coco_val2017_extended'):
        out += sorted(p for p in (root / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    ref = root / 'outputs/extended_q1_20261002/reference'
    for m in METHODS:
        for s in SEEDS:
            rec_path = ref / f'{m}_seed{s}.json'
            rec = json.loads(rec_path.read_text(encoding='utf-8'))
            out.append(rec_path)
            pert = root / rec['perturbation_file'].replace('\\', '/')
            out += sorted(p for p in pert.parent.rglob('*') if p.is_file())
    return out


def main():
    root, dest = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise SystemExit(f'{dest} đã có, không ghi đè')
    fs = files(root)
    missing = [str(p) for p in fs if not p.is_file()]
    if missing:
        raise SystemExit('thiếu file: ' + ', '.join(missing))
    lines = []
    with tarfile.open(dest, 'w', format=tarfile.PAX_FORMAT) as tar:
        for p in fs:
            rel = p.relative_to(root).as_posix()
            tar.add(p, arcname=rel)
            lines.append(f'{sha256(p)}  {rel}')
        # thư mục cấu hình rỗng mà yolov5_ref trỏ YOLOV5_CONFIG_DIR tới
        info = tarfile.TarInfo('outputs/runtime/reference_config')
        info.type = tarfile.DIRTYPE
        info.mode = 0o755
        tar.addfile(info)
        data = ('\n'.join(lines) + '\n').encode()
        info = tarfile.TarInfo('INPUTS_SHA256.txt')
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    print(f'{len(fs)} files, {dest.stat().st_size / 1e6:.1f} MB -> {dest}')
    print(f'sha256 of tar: {sha256(dest)}')


if __name__ == '__main__':
    main()
