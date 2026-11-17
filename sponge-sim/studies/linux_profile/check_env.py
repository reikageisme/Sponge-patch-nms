"""Kiểm môi trường đo đã khoá chưa (Linux, chỉ đọc). Dùng trước mỗi phiên; kết quả ghi vào manifest của phiên.

    python studies/linux_profile/check_env.py <cpu sẽ ghim> [file json]

Mã thoát 0 khi `ready` là true. Khoá bằng `sudo bash studies/linux_profile/lock_env.sh lock <cpu> <kHz>` (đổi cấu hình nguồn, đọc trước khi chạy).
"""
import json
import platform
import sys
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SIM / 'src'))

if __name__ == '__main__':
    if platform.system() != 'Linux':
        r = dict(ready=False, platform=platform.platform(), problems=['không phải Linux: không kiểm và không khoá được tần số theo cách này'])
    else:
        from sponge_sim import hw_linux
        r = dict(hw_linux.lock_status(int(sys.argv[1]) if len(sys.argv) > 1 else 2), kernel=platform.release(),
                 power=hw_linux.power_snapshot(), thermal=hw_linux.read_thermal())
    print(json.dumps(r, indent=1, ensure_ascii=False, default=str))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str), encoding='utf-8')
    sys.exit(0 if r['ready'] else 1)
