"""Đo thời gian CPU theo quy ước skill: perf_counter_ns, gc tắt trong vùng đo, warm-up bỏ,
timestamp từng phép đo, benchmark tham chiếu để bắt trôi xung nhịp, khối Latin square.
"""
from __future__ import annotations

import gc
import json
import random
import time
from pathlib import Path

import torch

DRIFT_FLAG = 0.03  # >3% so với tham chiếu đầu phiên -> gắn cờ


def timed(fn, setup=None, repeats: int = 1, warmup: int = 0, sync=None) -> list[dict]:
    """Mỗi lần lặp: args = setup() (NGOÀI vùng đo), rồi đo fn(*args). Trả về list dict.
    gc tắt trong suốt vòng đo, bật lại sau.
    sync: hàm gọi NGAY TRƯỚC t0 và NGAY TRƯỚC t1 để chặn đồng hồ cho tới khi công việc xong
    (vd torch.cuda.synchronize cho đo GPU, vì kernel CUDA bất đồng bộ). Mặc định None = không đổi hành vi CPU."""
    setup = setup or (lambda: ())
    for _ in range(warmup):
        fn(*setup())
    out = []
    was = gc.isenabled()
    gc.disable()
    try:
        for r in range(repeats):
            args = setup()
            if sync is not None:
                sync()
            t0 = time.perf_counter_ns()
            result = fn(*args)
            if sync is not None:
                sync()
            t1 = time.perf_counter_ns()
            out.append(dict(rep=r, ns=t1 - t0, t_start_ns=t0, wall_utc=time.time(), result=result))
    finally:
        if was:
            gc.enable()
    return out


_REF_A = None


def reference_ms(repeats: int = 15) -> float:
    """Benchmark tham chiếu cố định (matmul 256×256, 20 lần) – trung vị ms. Dùng số thread hiện hành."""
    global _REF_A
    if _REF_A is None:
        g = torch.Generator().manual_seed(0)
        _REF_A = torch.randn(256, 256, generator=g)
    def work():
        a = _REF_A
        for _ in range(20):
            a = torch.tanh(a @ _REF_A)
        return None
    samples = sorted(x['ns'] for x in timed(work, repeats=repeats, warmup=3))
    return samples[len(samples) // 2] / 1e6


def drift(ref_now: float, ref_start: float) -> dict:
    d = ref_now / ref_start - 1
    return dict(ref_ms=ref_now, ref_start_ms=ref_start, rel_change=d, flagged=abs(d) > DRIFT_FLAG)


def latin_blocks(conditions: list, n_blocks: int, seed: int) -> list[list]:
    """Hình vuông Latin vòng (mỗi điều kiện xuất hiện ở mỗi vị trí như nhau qua k khối),
    thứ tự hàng và nhãn điều kiện được hoán vị ngẫu nhiên theo seed."""
    rng = random.Random(seed)
    k = len(conditions)
    labels = conditions[:]
    rng.shuffle(labels)
    rows = [[labels[(i + j) % k] for j in range(k)] for i in range(k)]
    blocks = []
    while len(blocks) < n_blocks:
        batch = rows[:]
        rng.shuffle(batch)
        blocks += batch
    return blocks[:n_blocks]


class JsonlWriter:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = self.path.open('a', encoding='utf-8')

    def write(self, row: dict):
        self.fh.write(json.dumps(row, ensure_ascii=False, default=str) + '\n')
        self.fh.flush()

    def close(self):
        self.fh.close()


# ----------------------------------------------------------------------------------------------------------------------
# Bổ sung sau phản biện 16/11/2026: cổng trôi theo khối (E11 bị loại vì 11/11 điểm tham chiếu bị cờ).

class SessionAbort(RuntimeError):
    pass


class DriftGate:
    """Đo điểm tham chiếu TRƯỚC và SAU mỗi khối; khối chỉ được nhận khi cả hai điểm lệch ref đầu phiên không quá `flag`
    và lệch nhau không quá `flag`. Khối bị trôi được đo lại (tối đa `max_retries` lần, chờ `cooldown_s` giữa các lần);
    hết lượt thì dừng phiên sớm bằng SessionAbort. Mọi lần thử, kể cả lần bị bỏ, được ghi với kind='block_attempt'
    để báo cáo đầy đủ. Quy tắc (flag, max_retries, cooldown_s) phải nằm trong file đăng ký trước của phiên đo."""

    def __init__(self, reference_fn=None, writer=None, flag: float = DRIFT_FLAG, max_retries: int = 3,
                 cooldown_s: float = 60.0, sleep=time.sleep):
        self.ref = reference_fn or reference_ms
        self.w, self.flag, self.max_retries, self.cooldown, self.sleep = writer, flag, max_retries, cooldown_s, sleep
        self.ref0 = None
        self.attempts = []

    def _log(self, **row):
        row.setdefault('wall_utc', time.time())
        self.attempts.append(row)
        if self.w is not None:
            self.w.write(dict(kind='block_attempt', **row))

    def start(self) -> float:
        self.ref0 = self.ref()
        self._log(block='start', ref_ms=self.ref0, accepted=True)
        return self.ref0

    def run_block(self, block, measure):
        """measure() -> list các dòng raw của khối (CHƯA ghi file). Trả về các dòng của lần đo được nhận."""
        if self.ref0 is None:
            self.start()
        for attempt in range(self.max_retries + 1):
            before = self.ref()
            rows = measure()
            after = self.ref()
            d_b, d_a, d_in = before / self.ref0 - 1, after / self.ref0 - 1, after / before - 1
            ok = max(abs(d_b), abs(d_a), abs(d_in)) <= self.flag
            self._log(block=block, attempt=attempt, ref_before_ms=before, ref_after_ms=after, rel_before=d_b, rel_after=d_a,
                      rel_within=d_in, accepted=ok, n_rows=len(rows))
            if ok:
                return rows
            if attempt < self.max_retries:
                self.sleep(self.cooldown)
        raise SessionAbort(f'khối {block}: tham chiếu trôi quá {self.flag:.0%} sau {self.max_retries + 1} lần đo; dừng phiên')

    def summary(self) -> dict:
        blocks = [a for a in self.attempts if a.get('block') != 'start']
        acc = [a for a in blocks if a['accepted']]
        return dict(attempts=len(blocks), accepted=len(acc), rejected=len(blocks) - len(acc),
                    max_abs_accepted=max([max(abs(a['rel_before']), abs(a['rel_after'])) for a in acc] or [0.0]))
