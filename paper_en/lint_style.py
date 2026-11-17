"""Soát hình thức bản thảo LaTeX: dấu gạch, DOI trong bib, độ dài caption / abstract / kết luận, tên câu hỏi nghiên cứu.

    python paper_en/lint_style.py paper_en [thư mục ghi kết quả]

Không sửa file nào. Lưu ý: bản trong repo (paper_en) có thể cũ hơn bản PDF đang nộp; chạy lại trên bản mới nhất.
"""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / 'ket_qua'
out_dir.mkdir(parents=True, exist_ok=True)
tex_files = [p for p in sorted(src.rglob('*.tex')) if 'segmentation_extension' not in p.parts]
md = ['# A3. Soát hình thức bản thảo', '', f'Thư mục: `{src}` ({len(tex_files)} file .tex).', '']

# 1. dấu gạch
hits = []
for p in tex_files:
    for i, line in enumerate(p.read_text(encoding='utf-8', errors='replace').split('\n'), 1):
        code = line.split('%')[0] if not line.lstrip().startswith('%') else ''
        if re.search(r'\)\s*--\s*[(+]|\\(draw|path)\b', code):   # TikZ: (a)--(b) là cú pháp vẽ, không phải dấu gạch
            continue
        for m in re.finditer(r'[\u2013\u2014]|(?<!-)--(?!-)|---', code):
            hits.append((p.relative_to(src).as_posix(), i, m.group(0), code[max(0, m.start() - 25):m.end() + 25].strip()))
md += [f'## 1. Dấu gạch (en dash, em dash, `--`, `---`): {len(hits)} chỗ', '']
by = {}
for f, i, g, ctx in hits:
    by.setdefault(f, []).append((i, g, ctx))
for f, xs in by.items():
    md.append(f'- `{f}`: {len(xs)} chỗ. Ví dụ dòng {xs[0][0]}: `{xs[0][2]}`')
md += ['', 'Sửa: đổi mọi `--` trong khoảng số và từ ghép thành `-`; trong bib, `pages = {284--293}` do kiểu bst in ra en dash, đổi thành `284-293` hoặc sửa bst.', '']

# 2. bib
bib = src / 'references.bib'
if bib.exists():
    entries = re.split(r'\n(?=@)', bib.read_text(encoding='utf-8', errors='replace'))
    no_id, pages_dash = [], 0
    for e in entries:
        m = re.match(r'@(\w+)\{([^,]+),', e)
        if not m or m.group(1).lower() in ('comment', 'string'):
            continue
        pages_dash += bool(re.search(r'pages\s*=\s*[{"][^}"]*--', e))
        if not re.search(r'\b(doi|eprint|url)\s*=', e, re.I):
            no_id.append((m.group(2), m.group(1)))
    n = sum(1 for e in entries if re.match(r'@(?!comment|string)\w+\{', e, re.I))
    md += [f'## 2. Tài liệu tham khảo: {n} mục, {len(no_id)} mục không có doi / eprint / url', '']
    md += [f'- `{k}` ({t})' for k, t in no_id]
    md += ['', f'- {pages_dash} mục có khoảng trang viết bằng `--`.', '']

# 3. độ dài
main = (src / 'main.tex').read_text(encoding='utf-8', errors='replace') if (src / 'main.tex').exists() else ''
words = lambda s: len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.-]*", re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?|[{}$]', ' ', s)))
md += ['## 3. Độ dài', '']
m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', main, re.S)
if m:
    md.append(f'- Abstract: khoảng {words(m.group(1))} từ (hướng dẫn: 200 đến 260).')
m = re.search(r'\\section\{Conclusions?\}(.*?)(\\section|\\appendix|\\bibliography|\\printcredits|\\end\{document\})', main, re.S)
if m:
    md.append(f'- Kết luận: khoảng {words(m.group(1))} từ (hướng dẫn: 150 đến 200).')
caps = []
for p in tex_files:
    t = p.read_text(encoding='utf-8', errors='replace')
    for mm in re.finditer(r'\\caption\{', t):
        depth, j = 1, mm.end()
        while depth and j < len(t):
            depth += (t[j] == '{') - (t[j] == '}'); j += 1
        caps.append((words(t[mm.end():j - 1]), p.relative_to(src).as_posix(), t[mm.end():mm.end() + 60].replace('\n', ' ')))
long = sorted([c for c in caps if c[0] > 60], reverse=True)
md.append(f'- Caption: {len(caps)} cái, {len(long)} cái dài hơn 60 từ.')
md += [f'  - {w} từ, `{f}`: {s}...' for w, f, s in long[:12]]

# 4. cấu trúc
md += ['', '## 4. Cấu trúc theo hướng dẫn viết', '']
rq = len(re.findall(r'\bRQ\d', main)); q = len(re.findall(r'\bQ[1-4]\b', main))
md.append(f'- Nhắc "RQn": {rq} lần; nhắc "Q1..Q4": {q} lần. Nếu câu hỏi nghiên cứu đang đặt tên Q1 đến Q4 thì đổi thành RQ1 đến RQ4 để khỏi lẫn với hạng tạp chí.')
md.append(f"- Ô \"Answer to RQ\": {len(re.findall(r'Answer to RQ', main))}. Danh sách đóng góp C1..Cn: {'có' if re.search(r'C1[,:) ]', main) else 'chưa thấy'}.")
md.append(f"- Trích định luật Amdahl: {'có' if re.search(r'cite[^}]*amdahl', main, re.I) else 'chưa thấy lệnh cite nào có khoá chứa amdahl'}.")
(out_dir / 'a3_manuscript_lint.md').write_text('\n'.join(md), encoding='utf-8')
print('\n'.join(md))
