"""Chạy nguyên studies/e10r_reference_rerun/analyze_new.py; chỉ thay diag.spearman để trả None (không xác định) khi một
biến là hằng số (mẫu số 0). Viết SAU phiên đo (28/11/2026) vì E10-RM có minflt = 0 ở mọi lần đo sạch (DEVIATIONS mục 9).
Dùng: analyze_new_safe_spearman.py <analyze_new.py> <run_dir>"""
import importlib.util
import json
import sys
from pathlib import Path

script, run_dir = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location('an', script)
an = importlib.util.module_from_spec(spec)
spec.loader.exec_module(an)
orig = an.diag.spearman


def safe(a, b):
    ra, rb = an.diag.ranks(a), an.diag.ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    if sum((x - ma) ** 2 for x in ra) == 0 or sum((y - mb) ** 2 for y in rb) == 0:
        return None
    return orig(a, b)


an.diag.spearman = safe
sys.argv = [script, run_dir]
try:
    an.main()
except TypeError:  # dòng in cuối của analyze_new dùng '%.2f' với rho; JSON đã ghi trước dòng in đó
    res = json.loads((Path(run_dir) / 'e10r_new_endpoints.json').read_text(encoding='utf-8'))
    for k, v in res['clean'].items():
        print('clean', k, 'MDE %.3f%%' % v['in_session_mde_pct'], 'bimodal', v['bimodal_flag'],
              'rho(minflt,total)', v['spearman_minflt_total'])
