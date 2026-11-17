"""Build the Overleaf bundle: one folder, only the files the two manuscripts actually use.

    python -X utf8 paper_en/make_bundle.py

Writes paper_en/sponge_paper/ and paper_en/sponge_paper.zip (upload the zip to Overleaf, compiler pdfLaTeX,
recompile twice). Source: the session script used on 16-17/11/2026, with repository-relative paths.
"""
import os
import re
import shutil
import zipfile
from pathlib import Path

R = Path(__file__).resolve().parent
root = R / 'sponge_paper'
(root / 'figures').mkdir(parents=True, exist_ok=True)
(root / 'tables_q3').mkdir(parents=True, exist_ok=True)
files = ['main.tex', 'mainvi.tex', 'references.bib', 'apa7num.bst', 'cas-dc.cls', 'cas-common.sty']
used = set()
for doc in ('main.tex', 'mainvi.tex'):
    body = (R / doc).read_text(encoding='utf-8').split(chr(92) + 'begin{document}')[1]
    used |= {m + '.tex' for m in re.findall(r'\\input\{([^}]+)\}', body)}
    used |= {'figures/' + m for m in re.findall(r'\\includegraphics\[[^\]]*\]\{([^}]+)\}', body)}
for f in files + sorted(used):
    assert (R / f).exists(), f
    (root / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(R / f, root / f)
(root / 'COMPILE.txt').write_text(
    'Overleaf: upload this folder as-is (New Project > Upload Project, choose sponge_paper.zip).\n'
    'Compiler: pdfLaTeX (Menu > Compiler). Recompile twice.\n'
    '  main.tex   = English manuscript (official)\n'
    '  mainvi.tex = Vietnamese reading copy (set it as main document to build it)\n'
    'figures/ and tables_q3/ hold only the files the manuscripts use.\n', encoding='utf-8', newline='\n')
keep = {f.replace('/', os.sep) for f in files + sorted(used)} | {'COMPILE.txt'}
z = R / 'sponge_paper.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for rel in sorted(keep):
        zf.write(root / rel, ('sponge_paper/' + rel).replace(os.sep, '/'))
print('files:', len(keep), '| zip bytes:', z.stat().st_size)
