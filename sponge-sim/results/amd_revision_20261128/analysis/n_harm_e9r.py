"""N_harm cho E9-R: gọi nguyên diag_posthoc.b3_e9 (đã đăng ký trong PREREG), chỉ đổi đường dẫn raw E9 sang E9-R."""
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('dp', sys.argv[1]); dp = importlib.util.module_from_spec(spec); spec.loader.exec_module(dp)
dp.SRC['e9'] = str(Path(sys.argv[2]).resolve())
res = dict(analysis='N_harm on E9-R raw via diag_posthoc.b3_e9 (preregistered 28/11)', source=dp.SRC['e9'],
           bootstrap_seed=dp.SEED, n_boot=dp.N_BOOT, harm_thresholds_ms=dp.HARM, B3_e9r_n_harm=dp.b3_e9())
Path(sys.argv[3]).write_text(json.dumps(res, indent=1, default=str), encoding='utf-8', newline='\n')
for k, v in res['B3_e9r_n_harm'].items():
    print(k, v['n_harm'])
