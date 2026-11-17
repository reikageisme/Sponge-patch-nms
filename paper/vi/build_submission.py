import re
import shutil
from pathlib import Path

R = Path('D:/Sponge-patch-study')
OUT = R / 'paper' / 'submission_Q3_v5'  # v5 (03/11/2026): bảng patch dùng toàn trình dự đoán; v4 giữ nguyên
OUT.mkdir(exist_ok=True)
(OUT / 'figures').mkdir(exist_ok=True)
old = (R / 'paper' / 'submission_Q1' / 'BaoCaoKhoaHocAdversarialAttacks_Q1_VI.tex').read_text(encoding='utf-8')
TAB = R / 'paper' / 'vi' / 'tables'


def inline_tables(tex):
    """Chèn nội dung tables/tab_*.tex (sinh tự động) vào chỗ \\input, để gói nộp là một tệp .tex."""
    return re.sub(r'\\input\{tables/([^}]+)\}', lambda m: (TAB / f'{m.group(1)}.tex').read_text(encoding='utf-8').split('\n', 1)[1].rstrip('\n'), tex)


vi = inline_tables((R / 'paper' / 'vi' / 'main_vi.tex').read_text(encoding='utf-8'))

# ---- tiền tố: giữ preamble CAS tiếng Việt đã biên dịch được của gói cũ
pre = old[:old.index('\\begin{document}')]
pre = pre.replace('\\usepackage[numbers]{natbib}', '\\usepackage[numbers,sort&compress]{natbib}')  # đánh số [n]; danh mục APA 7 qua apa7num.bst (BibTeX, nhanh)
pre = pre.replace('\\graphicspath{{media/}{./}}', '\\graphicspath{{figures/}{./}}')
pre += ('% Lệnh riêng của bản thảo này\n'
        '\\newcommand{\\nodata}[1]{\\textcolor{red}{[CHƯA CÓ SỐ: #1]}}\n'
        '\\newcommand{\\todo}[1]{\\textcolor{red}{[TODO: #1]}}\n'
        '\\newcommand{\\Ntau}{N_{\\tau}}\n'
        '% Giữ hình/bảng gần chỗ được nhắc: chặn trôi qua ranh giới mục và nới các tham số đặt float\n'
        '\\usepackage{placeins}\n'
        '\\usepackage{adjustbox}\n'
        '\\usepackage{float}\n'
        '\\usepackage{capt-of}\n'
        '\\renewcommand{\\topfraction}{0.9}\\renewcommand{\\bottomfraction}{0.8}\\renewcommand{\\textfraction}{0.07}\n'
        '\\renewcommand{\\floatpagefraction}{0.6}\\renewcommand{\\dbltopfraction}{0.9}\\renewcommand{\\dblfloatpagefraction}{0.6}\n'
        '\\setcounter{topnumber}{4}\\setcounter{bottomnumber}{2}\\setcounter{totalnumber}{8}\\setcounter{dbltopnumber}{4}\n\n')

title = re.search(r'\\title\{(.*?)\}\n', vi).group(1)
abstract = vi[vi.index('\\begin{abstract}') + len('\\begin{abstract}'):vi.index('\\end{abstract}')].strip()
kw = re.search(r'\\noindent\\textbf\{Từ khóa:\} (.*)\n', vi).group(1)
kws = ' \\sep '.join(x.strip() for x in kw.split(';'))

front = ('\\begin{document}\n\\let\\WriteBookmarks\\relax\n\\def\\floatpagepagefraction{1}\n\\def\\textpagefraction{.001}\n'
         f'\\hypersetup{{pdftitle={{{title}}}}}\n'
         '\\shorttitle{Tấn công cạn kiệt tài nguyên qua NMS}\n\\shortauthors{Phạm Tuấn Anh và Mai Quốc Bảo}\n'
         f'\\title[mode=title]{{{title}}}\n'
         '\\author[1]{Phạm Tuấn Anh}\n\\ead{anh25807700004@hutech.edu.vn}\n'
         '\\author[1]{Mai Quốc Bảo}\n\\ead{bao2580770008@hutech.edu.vn}\n'
         '\\cortext[cor1]{Tác giả liên hệ: Đinh Phương Nam. Email: dp.nam@hutech.edu.vn.}\n'
         '\\nonumnote{Giảng viên hướng dẫn: Đinh Phương Nam, Trường Đại học Công nghệ Thành phố Hồ Chí Minh (HUTECH). Email: dp.nam@hutech.edu.vn.}\n'
         '\\affiliation[1]{organization={Trường Đại học Công nghệ Thành phố Hồ Chí Minh (HUTECH)},\ncity={Thành phố Hồ Chí Minh},country={Việt Nam}}\n\n'
         f'\\begin{{abstract}}\n{abstract}\n\\end{{abstract}}\n\n'
         f'\\begin{{keywords}}[Từ khóa]\n{kws}\n\\end{{keywords}}\n\\maketitle\n\n')

body = vi[vi.index('\\section{Giới thiệu}'):vi.rindex('\\bibliographystyle{apa7num}')]
# hai cột: bảng hẹp (<= 4 cột, không tabularx) giữ một cột, đặt [!htbp]; bảng rộng dùng table* [!t]
def colspec(block):
    """Chuỗi đặc tả cột của tabular đầu tiên, lấy theo cặp ngoặc khớp (đặc tả có thể chứa @{} và p{...})."""
    k = block.find('\\begin{tabular}{')
    if k < 0:
        return None
    i = k + len('\\begin{tabular}{')
    depth, j = 1, i
    while depth:
        depth += {'{': 1, '}': -1}.get(block[j], 0)
        j += 1
    return block[i:j - 1]


def ncols(spec):
    spec = re.sub(r'[@!]\{[^{}]*\}', '', spec)          # bỏ @{...}
    spec = re.sub(r'[pmb]\{[^{}]*\}', 'p', spec)         # p{..} -> một cột
    return len(re.findall(r'[lcrpX]', spec))


def boxed(block, width):
    """Thu nhỏ tabular (không phải tabularx) cho vừa chiều rộng; không phóng to bảng nhỏ."""
    block = block.replace('\\begin{tabular}{', '\\begin{adjustbox}{max width=' + width + '}\n\\begin{tabular}{', 1)
    k = block.rfind('\\end{tabular}')
    return block[:k] + '\\end{tabular}\n\\end{adjustbox}' + block[k + len('\\end{tabular}'):] if k >= 0 else block


def place(m):
    block = m.group(0)
    spec = colspec(block)
    long_p = spec is not None and any(float(w) >= 7 for w in re.findall(r'p\{([\d.]+)cm\}', spec))  # cột p{} dài hơn một cột trang
    wide = 'tabularx' in block or spec is None or ncols(spec) >= 5 or long_p
    inner = block[len('\\begin{table}[t]'):-len('\\end{table}')]
    if wide:
        if 'tabularx' not in inner:
            inner = boxed(inner, '\\textwidth')
        return '\\begin{table*}[!t]' + inner + '\\end{table*}'
    return '\\begin{table}[H]' + boxed(inner, '\\columnwidth') + '\\end{table}'  # một cột: đặt đúng chỗ, không tạo trang chỉ có float


body = re.sub(r'\\begin\{table\}\[t\].*?\\end\{table\}', place, body, flags=re.S)
# table* đã có trong nguồn: cũng thu cho vừa trang nếu là tabular thường
body = re.sub(r'\\begin\{table\*\}\[t\].*?\\end\{table\*\}',
              lambda m: m.group(0).replace('\\begin{table*}[t]', '\\begin{table*}[!t]', 1) if 'tabularx' in m.group(0)
              else boxed(m.group(0).replace('\\begin{table*}[t]', '\\begin{table*}[!t]', 1), '\\textwidth'), body, flags=re.S)
body = body.replace('\\begin{figure*}[t]', '\\begin{figure*}[!t]').replace('\\begin{figure}[t]', '\\begin{figure}[H]').replace('\\begin{figure}[!t]', '\\begin{figure}[H]')
# hình rộng: 0,9 chiều rộng trang để không chiếm cả trang
body = body.replace('\\includegraphics[width=\\textwidth]', '\\includegraphics[width=0.9\\textwidth]')
# chỉ chặn float ở ranh giới MỤC (không chặn ở tiểu mục: tránh trang trống)
body = body.replace('\\section{', '\\FloatBarrier\n\\section{')
# Bản 3 (sau ảnh Overleaf 02/11): [H] và rào chắn ở mỗi mục để lại nhiều khoảng trắng. Để LaTeX tự xếp cho đầy trang:
# bảng/hình một cột [!htbp], toàn trang [!tp] (được phép đứng trên trang float), bỏ mọi rào chắn trừ một rào trước phần cuối bài.
body = body.replace('\\FloatBarrier\n', '')
body = body.replace('[H]', '[!htbp]').replace('\\begin{table*}[!t]', '\\begin{table*}[!tp]').replace('\\begin{figure*}[!t]', '\\begin{figure*}[!tp]')
body = body.replace('\\section*{', '\\FloatBarrier\n\\section*{', 1)
# Bản 4 (ảnh Overleaf lần 4: hình một cột kẹt lại và kéo mọi hình phía sau về cuối bài, vì LaTeX giữ thứ tự float cùng loại).
# Bảng/hình MỘT CỘT không còn là float: đặt thẳng vào dòng văn bản (center + \captionof), không thể kẹt hay đẩy hình khác;
# chỉ còn bảng/hình toàn trang là float [!tp].
def inline(m, kind):
    block = m.group(0)
    block = block.replace('\\begin{' + kind + '}[!htbp]', '\\par\\begin{center}', 1)
    block = block.replace('\\caption{', '\\captionof{' + kind + '}{', 1)
    k = block.rfind('\\end{' + kind + '}')
    return block[:k] + '\\end{center}\\par' + block[k + len('\\end{' + kind + '}'):]
for kind in ('table', 'figure'):
    body = re.sub(r'\\begin\{' + kind + r'\}\[!htbp\].*?\\end\{' + kind + r'\}', lambda m, k=kind: inline(m, k), body, flags=re.S)
tail = '\\bibliographystyle{apa7num}\n\\bibliography{references}\n\n\\end{document}\n'  # danh mục đọc từ references.bib (biber)
tex = pre + front + body + tail
(OUT / 'main_vi.tex').write_text(tex, encoding='utf-8')

# ---- tài liệu tham khảo: gộp
bib = (R / 'paper' / 'vi' / 'references_apa.bib').read_text(encoding='utf-8')  # chỉ 31 mục còn trích dẫn
(OUT / 'references.bib').write_text(bib, encoding='utf-8')
shutil.copy2(R / 'paper' / 'vi' / 'apa7num.bst', OUT / 'apa7num.bst')
for f in ('cas-dc.cls', 'cas-common.sty'):
    shutil.copy2(R / 'paper' / 'submission_Q1' / f, OUT / f)
shutil.copytree(R / 'paper' / 'submission_Q1' / 'thumbnails', OUT / 'thumbnails', dirs_exist_ok=True)
for f in (R / 'paper_en' / 'figures').glob('*.pdf'):
    shutil.copy2(f, OUT / 'figures' / f.name)
# tài liệu bổ sung: tệp riêng, bảng đã chèn
sup = inline_tables((R / 'paper' / 'vi' / 'supplement_vi.tex').read_text(encoding='utf-8')).replace('{../../paper_en/figures/}', '{figures/}')
(OUT / 'supplement_vi.tex').write_text(sup, encoding='utf-8')

# ---- kiểm cấu trúc
b = 0
for ch in tex:
    b += (ch == '{') - (ch == '}')
envs = {e: (tex.count('\\begin{' + e + '}'), tex.count('\\end{' + e + '}')) for e in sorted(set(re.findall(r'\\begin\{(\w+\*?)\}', tex)))}
keys = set(k.strip() for c in re.findall(r'\\cite\{([^}]*)\}', tex) for k in c.split(','))
missing = [k for k in keys if '{' + k + ',' not in bib]
labels = re.findall(r'\\label\{([^}]*)\}', tex)
undef = set(re.findall(r'\\ref\{([^}]*)\}', tex)) - set(labels)
dup = sorted({l for l in labels if labels.count(l) > 1})
figs = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}', tex)
print('brace', b, 'unbalanced envs', {e: v for e, v in envs.items() if v[0] != v[1]})
print('cites', len(keys), 'missing', missing, 'undef refs', undef, 'dup labels', dup)
print('figures', figs, [(OUT / 'figures' / f).exists() for f in figs])
print('nodata', tex.count('\\nodata{') - 1)
