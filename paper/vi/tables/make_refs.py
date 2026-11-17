"""Sinh danh mục tài liệu tham khảo theo APA 7 (tables/refs_apa.tex) và tệp .bib lọc tương ứng (references_apa.bib).

    python paper_vi/tables/make_refs.py

Chỉ giữ: tạp chí Q1/Q2 (SJR) và hội nghị hạng A*/A/B (CORE). Bỏ (03/11/2026, theo yêu cầu): bản arXiv, workshop, phần mềm.
Thông tin (tác giả, năm, trang, DOI) đối chiếu với trang venue gốc / CVF Open Access / MLAnthology / DOI (REPORT_Q3.md mục d).
Trích dẫn trong bài dùng natbib authoryear: \\citep{key} -> (Tác giả et al., năm).
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CVPR = 'Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)'
ICCV = 'Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)'
WACV = 'Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)'

# (key, [(họ, tên viết tắt)], năm, tiêu đề (sentence case), kiểu, nơi đăng, chi tiết, doi, hạng)
REFS = [
    ('shumailov2021sponge', [('Shumailov', 'I.'), ('Zhao', 'Y.'), ('Bates', 'D.'), ('Papernot', 'N.'), ('Mullins', 'R.'), ('Anderson', 'R.')], 2021,
     'Sponge examples: Energy-latency attacks on neural networks', 'proc', '2021 IEEE European Symposium on Security and Privacy (EuroS\\&P)', 'pp. 212--231', '10.1109/EuroSP51992.2021.00024', 'CORE A'),
    ('nicgslowdown2022', [('Chen', 'S.'), ('Song', 'Z.'), ('Haque', 'M.'), ('Liu', 'C.'), ('Yang', 'W.')], 2022,
     'NICGSlowDown: Evaluating the efficiency robustness of neural image caption generation models', 'proc', CVPR, 'pp. 15365--15374', None, 'CORE A*'),
    ('phantom2023', [('Shapira', 'A.'), ('Zolfi', 'A.'), ('Demetrio', 'L.'), ('Biggio', 'B.'), ('Shabtai', 'A.')], 2023,
     'Phantom sponges: Exploiting non-maximum suppression to attack deep object detectors', 'proc', WACV, 'pp. 4571--4580', None, 'CORE A'),
    ('overload2024', [('Chen', 'E.-C.'), ('Chen', 'P.-Y.'), ('Chung', 'I.-H.'), ('Lee', 'C.-R.')], 2024,
     'Overload: Latency attacks on object detection for edge devices', 'proc', CVPR, 'pp. 24716--24725', None, 'CORE A*'),
    ('slowtrack2024', [('Ma', 'C.'), ('Wang', 'N.'), ('Chen', 'Q. A.'), ('Shen', 'C.')], 2024,
     'SlowTrack: Increasing the latency of camera-based perception in autonomous driving using adversarial examples', 'serial',
     'Proceedings of the AAAI Conference on Artificial Intelligence', '38(5), 4062--4070', '10.1609/aaai.v38i5.28200', 'CORE A*'),
    ('underload2025', [('Wang', 'T.'), ('Wang', 'Z.'), ('Wang', 'C.'), ('Shu', 'Y.'), ('Deng', 'R.'), ('Cheng', 'P.'), ('Chen', 'J.')], 2025,
     'Can\'t slow me down: Learning robust and hardware-adaptive object detectors against latency attacks for edge devices', 'proc', CVPR, 'pp. 19230--19240', None, 'CORE A*'),
    ('evade2025', [('Monteuuis', 'J.-P.'), ('Chen', 'C.'), ('Petit', 'J.')], 2025,
     'Latency NMS attacks: Is it real life or is it just fantasy?', 'serial', 'Advances in Neural Information Processing Systems', '38', None, 'CORE A*'),
    ('bitflip2025', [('Sistla', 'M.'), ('Wen', 'Y.'), ('Shah', 'A. B.'), ('Huang', 'C.'), ('Wang', 'L.'), ('Wu', 'X.'), ('Chen', 'J.'), ('Pan', 'M.'), ('Fu', 'X.')], 2025,
     'Bit-flip induced latency attacks in object detection', 'proc', WACV, 'pp. 6709--6718', None, 'CORE A'),
    ('athalye2018eot', [('Athalye', 'A.'), ('Engstrom', 'L.'), ('Ilyas', 'A.'), ('Kwok', 'K.')], 2018,
     'Synthesizing robust adversarial examples', 'serial', 'Proceedings of Machine Learning Research (ICML 2018)', '80, 284--293', None, 'CORE A*'),
    ('ilyas2018blackbox', [('Ilyas', 'A.'), ('Engstrom', 'L.'), ('Athalye', 'A.'), ('Lin', 'J.')], 2018,
     'Black-box adversarial attacks with limited queries and information', 'serial', 'Proceedings of Machine Learning Research (ICML 2018)', '80, 2137--2146', None, 'CORE A*'),
    ('neubeck2006nms', [('Neubeck', 'A.'), ('Van Gool', 'L.')], 2006,
     'Efficient non-maximum suppression', 'proc', '18th International Conference on Pattern Recognition (ICPR\'06)', 'Vol. 3, pp. 850--855', '10.1109/ICPR.2006.479', 'CORE B', 'IEEE'),
    ('redmon2016yolo', [('Redmon', 'J.'), ('Divvala', 'S.'), ('Girshick', 'R.'), ('Farhadi', 'A.')], 2016,
     'You only look once: Unified, real-time object detection', 'proc', 'Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)', 'pp. 779--788', '10.1109/CVPR.2016.91', 'CORE A*'),
    ('carion2020detr', [('Carion', 'N.'), ('Massa', 'F.'), ('Synnaeve', 'G.'), ('Usunier', 'N.'), ('Kirillov', 'A.'), ('Zagoruyko', 'S.')], 2020,
     'End-to-end object detection with transformers', 'proc', 'Computer Vision -- ECCV 2020', 'pp. 213--229', '10.1007/978-3-030-58452-8_13', 'CORE A*', 'Springer'),
    ('lin2014coco', [('Lin', 'T.-Y.'), ('Maire', 'M.'), ('Belongie', 'S.'), ('Hays', 'J.'), ('Perona', 'P.'), ('Ramanan', 'D.'), ('Doll{\\\'a}r', 'P.'), ('Zitnick', 'C. L.')], 2014,
     'Microsoft COCO: Common objects in context', 'proc', 'Computer Vision -- ECCV 2014', 'pp. 740--755', '10.1007/978-3-319-10602-1_48', 'CORE A*', 'Springer'),
    ('paszke2019pytorch', [('Paszke', 'A.'), ('Gross', 'S.'), ('Massa', 'F.'), ('Lerer', 'A.'), ('Bradbury', 'J.'), ('Chanan', 'G.'), ('Killeen', 'T.'), ('Lin', 'Z.'),
                           ('Gimelshein', 'N.'), ('Antiga', 'L.'), ('Desmaison', 'A.'), ('K{\\"o}pf', 'A.'), ('Yang', 'E.'), ('DeVito', 'Z.'), ('Raison', 'M.'), ('Tejani', 'A.'),
                           ('Chilamkurthy', 'S.'), ('Steiner', 'B.'), ('Fang', 'L.'), ('Bai', 'J.'), ('Chintala', 'S.')], 2019,
     'PyTorch: An imperative style, high-performance deep learning library', 'serial', 'Advances in Neural Information Processing Systems', '32, 8026--8037', None, 'CORE A*'),
    ('efron1979bootstrap', [('Efron', 'B.')], 1979, 'Bootstrap methods: Another look at the jackknife', 'serial', 'The Annals of Statistics', '7(1), 1--26', '10.1214/aos/1176344552', 'SJR Q1'),
    ('cameron2008cluster', [('Cameron', 'A. C.'), ('Gelbach', 'J. B.'), ('Miller', 'D. L.')], 2008,
     'Bootstrap-based improvements for inference with clustered errors', 'serial', 'The Review of Economics and Statistics', '90(3), 414--427', '10.1162/rest.90.3.414', 'SJR Q1'),
    ('holm1979', [('Holm', 'S.')], 1979, 'A simple sequentially rejective multiple test procedure', 'serial', 'Scandinavian Journal of Statistics', '6(2), 65--70', None, 'SJR Q1'),
    ('apde2025', [('Zheng', 'J.'), ('Sun', 'J.'), ('Lin', 'C.'), ('Zhao', 'Z.'), ('Ma', 'C.'), ('Zhang', 'C.'), ('Wang', 'C.'), ('Wang', 'Q.'), ('Shen', 'C.')], 2025,
     'Revisiting adversarial patch defenses on object detectors: Unified evaluation, large-scale dataset, and new insights', 'proc', ICCV, 'pp. 23476--23486', None, 'CORE A*'),
    ('pbcat2025', [('Li', 'X.'), ('Zhu', 'Y.'), ('Huang', 'Y.'), ('Zhang', 'W.'), ('He', 'Y.'), ('Shi', 'J.'), ('Hu', 'X.')], 2025,
     'PBCAT: Patch-based composite adversarial training against physically realizable attacks on object detection', 'proc', ICCV, 'pp. 24456--24466', None, 'CORE A*'),
    ('oddr2025', [('Chattopadhyay', 'N.'), ('Guesmi', 'A.'), ('Hanif', 'M. A.'), ('Ouni', 'B.'), ('Shafique', 'M.')], 2025,
     'ODDR: Outlier detection \\& dimension reduction based defense against adversarial patches', 'proc', ICCV, 'pp. 22999--23008', None, 'CORE A*'),
    ('diffpad2025', [('Fu', 'J.'), ('Zhang', 'X.'), ('Pashami', 'S.'), ('Rahimian', 'F.'), ('Holst', 'A.')], 2025,
     'DiffPAD: Denoising diffusion-based adversarial patch decontamination', 'proc', WACV, 'pp. 6602--6611', None, 'CORE A'),
    ('unifiedpatchdet2025', [('Kumar', 'V.'), ('Agarwal', 'A.')], 2025, 'A unified, resilient, and explainable adversarial patch detector', 'proc', CVPR, 'pp. 30387--30397', '10.1109/CVPR52734.2025.02829', 'CORE A*'),
    ('antistyler2026', [('Yankelev', 'I.'), ('Grolman', 'E.'), ('Yerushalmi Levi', 'Y.'), ('Giloni', 'A.'), ('Hofman', 'O.'), ('Shimizu', 'T.'), ('Elovici', 'Y.'), ('Shabtai', 'A.')], 2026,
     'AntiStyler: Defending object detection models against adversarial patch attacks using style removal', 'proc', CVPR, 'pp. 27936--27945', None, 'CORE A*'),
    ('trace2026', [('Lee', 'W.'), ('Lee', 'J.'), ('Na', 'H.'), ('Park', 'S.'), ('Choi', 'D.')], 2026,
     'TRACE: Confounder-free adversarial fine-tuning for robust object detection', 'proc', WACV, 'pp. 6705--6714', None, 'CORE A'),
    ('iap2025', [('Dutta', 'S. K.'), ('Zhang', 'X.')], 2025,
     'IAP: Invisible adversarial patch attack through perceptibility-aware localization and perturbation optimization', 'proc', ICCV, 'pp. 14766--14775', '10.1109/ICCV51701.2025.01370', 'CORE A*'),
    ('grac2025', [('Liang', 'J.'), ('Liang', 'S.'), ('Lou', 'T.'), ('Zhang', 'M.'), ('Li', 'W.'), ('Fan', 'D.'), ('Cao', 'X.')], 2025,
     'Gradient-reweighted adversarial camouflage for physical object detection evasion', 'proc', ICCV, 'pp. 13880--13889', None, 'CORE A*'),
    ('gs3dcamo2025', [('Lou', 'T.'), ('Jia', 'X.'), ('Liang', 'S.'), ('Liang', 'J.'), ('Zhang', 'M.'), ('Xiao', 'Y.'), ('Cao', 'X.')], 2025,
     '3D Gaussian splatting driven multi-view robust physical adversarial camouflage generation', 'proc', ICCV, 'pp. 28752--28762', '10.1109/ICCV51701.2025.02670', 'CORE A*'),
    ('afog2025', [('Yahn', 'Z.'), ('Tekin', 'S. F.'), ('Ilhan', 'F.'), ('Hu', 'S.'), ('Huang', 'T.'), ('Xu', 'Y.'), ('Loper', 'M.'), ('Liu', 'L.')], 2025,
     'Adversarial attention perturbations for large object detection transformers', 'proc', ICCV, 'pp. 3184--3193', None, 'CORE A*'),
    ('rgbt2026', [('Zhu', 'X.'), ('Zeng', 'G.'), ('Hu', 'Z.'), ('Zhu', 'J.'), ('Hu', 'X.')], 2026,
     'Physical adversarial clothing evades visible-thermal detectors via non-overlapping RGB-T pattern', 'proc', CVPR, 'pp. 13356--13365', None, 'CORE A*'),
    ('thermal2026', [('Long', 'J.'), ('Jiang', 'T.'), ('Liu', 'H.'), ('Ma', 'C.'), ('Zhou', 'W.'), ('Yang', 'Y.'), ('Yao', 'W.')], 2026,
     'Thermally activated dual-modal adversarial clothing against AI surveillance systems', 'proc', CVPR, 'pp. 34929--34939', None, 'CORE A*'),
]
REMOVED = ['brown2017patch', 'thys2019fooling', 'jocher2023ultralytics', 'badpatch2025', 'remotepatch2025', 'trackflood2026', 'eventburst2026', 'yolov12', 'yolov13']


def authors_apa(a):
    names = [f'{s}, {g}' for s, g in a]
    if len(names) == 1:
        return names[0]
    if len(names) <= 20:
        return ', '.join(names[:-1]) + ', \\& ' + names[-1]
    return ', '.join(names[:19]) + ', \\ldots{} ' + names[-1]  # APA 7: 19 tác giả đầu, dấu ba chấm, tác giả cuối


def label(a, y):
    if len(a) == 1:
        return f'{a[0][0]}({y})'
    if len(a) == 2:
        return f'{a[0][0]} \\& {a[1][0]}({y})'
    return f'{a[0][0]} et~al.({y})'


def apa_text(r):
    key, a, y, title, kind, venue, det, doi, rank = r[:9]
    pub = r[9] if len(r) > 9 else None
    if kind == 'proc':
        s = f'{authors_apa(a)} ({y}). {title}. In \\textit{{{venue}}} ({det}).' + (f' {pub}.' if pub else '')
    else:
        m = re.match(r'(\d+)(\(\d+\))?(?:, (.*))?', det)
        vol, iss, pages = m.group(1), m.group(2) or '', m.group(3)
        s = f'{authors_apa(a)} ({y}). {title}. \\textit{{{venue}}}, \\textit{{{vol}}}{iss}' + (f', {pages}' if pages else '') + '.'
    if doi:
        s += f' \\url{{https://doi.org/{doi}}}'
    return s


def sortkey(r):
    return ([x[0].lower().replace('{\\', '').replace('}', '') for x in r[1]], r[2])


def protect(title):
    """Giữ nguyên chữ hoa của tên riêng/viết tắt khi biblatex-apa đổi tiêu đề sang sentence case."""
    out = []
    for i, w in enumerate(title.split(' ')):
        first = i == 0 or out[-1].endswith(':')
        inner_caps = bool(re.search(r'.[A-Z]', w.strip(':,')))  # viết tắt/tên riêng kiểu NMS, PyTorch, 3D: luôn bảo vệ
        out.append('{' + w + '}' if inner_caps or (not first and re.search(r'[A-Z]', w)) else w)
    return ' '.join(out)


def bib_entry(r):
    key, a, y, title, kind, venue, det, doi, rank = r[:9]
    pub = r[9] if len(r) > 9 else None
    f = [('author', ' and '.join(f'{s}, {g}' for s, g in a)), ('year', str(y)), ('title', protect(title))]
    if kind == 'proc':
        typ = 'inproceedings'
        f.append(('booktitle', venue))
        m = re.search(r'Vol\. (\d+)', det)
        if m:
            f.append(('volume', m.group(1)))
        f.append(('pages', re.search(r'pp\. ([\d-]+)', det).group(1)))
        if pub:
            f.append(('publisher', pub))
    else:
        typ = 'article'
        m = re.match(r'(\d+)(?:\((\d+)\))?(?:, (.*))?', det)
        f.append(('journaltitle', venue))
        f.append(('volume', m.group(1)))
        if m.group(2):
            f.append(('number', m.group(2)))
        if m.group(3):
            f.append(('pages', m.group(3)))
    if doi:
        f.append(('doi', doi))
    f.append(('keywords', rank.replace(' ', '-')))
    f.append(('apa', apa_text(r)))
    f.append(('sortkey', ' '.join(re.sub(r'[^a-z ]', '', x[0].lower()) for x in a) + f' {y}'))
    return f'@{typ}{{{key},\n' + ',\n'.join(f'  {k} = {{{v}}}' for k, v in f) + '\n}'


def main():
    # Từ 03/11/2026: paper_vi/references_apa.bib là tệp BibTeX chuẩn viết tay (dạng Google Scholar) và apa7num.bst tự định dạng APA 7.
    # Script này không còn ghi đè tệp đó; chỉ giữ dữ liệu REFS (hạng nơi đăng, nguồn kiểm) để tra cứu.
    print('make_refs: không ghi gì (references_apa.bib là tệp chuẩn viết tay).')
    return
    refs = sorted(REFS, key=sortkey)
    hdr = ('% SINH TỰ ĐỘNG bởi paper_vi/tables/make_refs.py — KHÔNG SỬA TAY.\n'
           '% Dùng với BibTeX + apa7num.bst: danh mục đánh số [n], xếp theo vần tác giả; trường apa là chuỗi APA 7 đã chuẩn hoá.\n'
           '% keywords = hạng của nơi đăng (CORE cho hội nghị, SJR cho tạp chí).\n\n')
    (HERE.parent / 'references_apa.bib').write_text(hdr + '\n\n'.join(bib_entry(r) for r in refs) + '\n', encoding='utf-8')
    print('refs', len(refs))


if __name__ == '__main__':
    main()
