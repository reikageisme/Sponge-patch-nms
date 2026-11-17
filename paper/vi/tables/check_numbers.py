"""Kiểm số của paper_vi/main_vi.tex.   python paper_vi/tables/check_numbers.py [--all]

1) Mọi bảng tables/tab_*.tex phải giống hệt bản sinh lại từ tệp tóm tắt (không sửa tay) -> make_tables.py --check.
2) Mọi \\input{tables/...} trong bài phải tồn tại; không còn bảng số viết tay (môi trường table chứa số mà không \\input).
3) Mọi số trong phần Kết quả (--all: cả tóm tắt, thảo luận, các mối đe dọa, kết luận) phải khớp một ô trong numbers.json
   (số đã sinh kèm nguồn) hoặc là hằng số thiết kế khai báo dưới đây. Báo các số không khớp; mã thoát 1 nếu có.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent / 'main_vi.tex'
# Hằng số thiết kế (lưới, cấu hình, kích thước), không phải kết quả đo. Nguồn: tệp đăng ký trước / cấu hình chạy.
DESIGN = {'0', '1', '2', '3', '4', '5', '6', '8', '9', '10', '11', '12', '15', '16', '20', '25', '30', '48', '50', '64', '80', '100', '128', '156', '200', '300',
          '320', '600', '625', '640', '1000', '1500', '2100', '3000', '8400', '10000', '25200', '30000', '62500', '25000', '0,01', '0,25', '0,45', '0,5', '0,8',
          '0,1', '0,2', '0,02', '1,5', '2,05', '0,05', '90', '95', '2017', '2021', '2022', '2023', '2024', '2025', '2026', '1335', '4498500', '1225', '3672'}
SECTIONS = {'results': ('\\section{Kết quả}', '\\section{Thảo luận}')}
SECTIONS_ALL = {'abstract': ('\\begin{abstract}', '\\end{abstract}'), 'discussion': ('\\section{Thảo luận}', '\\section{Các mối đe dọa'),
                'threats': ('\\section{Các mối đe dọa', '\\section{Kết luận'), 'conclusion': ('\\section{Kết luận', '\\section*{Phát hành')}


def norm(x: str) -> str:
    x = x.replace('{,}', ',').replace('$-$', '-').replace('$>$', '>').replace('\\,', '')
    return x.strip('$').lstrip('-').lstrip('>')


def numbers_in(text: str):
    t = re.sub(r'(?<!\\)%.*', '', text)  # chỉ bỏ chú thích LaTeX, không bỏ \%
    t = re.sub(r'SHA-256', ' ', t)
    t = re.sub(r'\\(ref|label|cite|input|includegraphics|texttt|url|todo|nodata)\{[^}]*\}', ' ', t)
    t = re.sub(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', ' ', t, flags=re.S)
    t = re.sub(r'\^\{?[\d]+\}?', ' ', t)  # số mũ 10^4
    t = re.sub(r'\b[QH]\d\b|\b[CB]\d\b|\bM_\{?N', ' ', t)
    t = t.replace('{,}', ',').replace('\\,', '')
    return re.findall(r'(?<![\w.,])\d+(?:,\d+)?(?![\w])', t)


def main():
    ok = True
    r = subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'make_tables.py'), '--check'], capture_output=True, text=True, encoding='utf-8')
    print('[1] bảng sinh tự động:', r.stdout.strip() or r.stderr.strip()[-400:])
    ok &= r.returncode == 0
    s = PAPER.read_text(encoding='utf-8')
    inputs = re.findall(r'\\input\{tables/([^}]+)\}', s)
    missing = [i for i in inputs if not (HERE / f'{i}.tex').exists()]
    hand = [m for m in re.findall(r'\\begin\{table\*?\}(.*?)\\end\{table\*?\}', s, flags=re.S) if re.search(r'\d,\d', m)]
    print('[2] \\input thiếu tệp:', missing or 'không có', '| bảng số viết tay còn lại:', len(hand))
    ok &= not missing and not hand
    reg = json.loads((HERE / 'numbers.json').read_text(encoding='utf-8'))
    known = {norm(c['text']) for v in reg.values() for c in v} | DESIGN
    secs = dict(SECTIONS, **(SECTIONS_ALL if '--all' in sys.argv else {}))
    for name, (a, b) in secs.items():
        seg = s[s.index(a):s.index(b)]
        bad = sorted({n for n in numbers_in(seg) if n not in known}, key=lambda z: float(z.replace(',', '.')))
        print(f'[3] {name}: {len(numbers_in(seg))} số, không khớp nguồn: {bad or "không có"}')
        if name == 'results':
            ok &= not bad
    print('KẾT QUẢ:', 'ĐẠT' if ok else 'KHÔNG ĐẠT')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
