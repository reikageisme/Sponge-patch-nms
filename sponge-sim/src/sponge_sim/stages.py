"""Tách phần tăng ngoài NMS (32-50% mức tăng end-to-end ở E10 chưa giải thích được).

Đo riêng từng chặng cho CÙNG một ảnh sạch và ảnh bị tấn công: forward, decode, lọc tau, NMS, rồi kiểm hai giả thuyết của bài:
  H_a  forward chậm đi vì số subnormal (denormal) trong activation: đếm subnormal ở đầu vào và ở đầu ra từng lớp,
       và đo forward lần nữa với torch.set_flush_denormal(True). Nếu forward chậm biến mất khi flush thì H_a đúng.
  H_b  bước lọc điểm / dựng tensor tỉ lệ với số ứng viên: thời gian decode + lọc tau theo N.
Mỗi chặng được bấm giờ riêng, xen kẽ sạch / tấn công trong cùng khối (ABBA), gc tắt, warm-up bỏ, như sponge_sim.timing.

Dùng trên dữ liệu thật (trong repo, cần ultralytics + ảnh nhiễu đã lưu của E10):
    from sponge_sim.stages import stage_times, subnormal_report
    rep = stage_times(model, x_clean, x_attacked, decode=pv.decode, tau_filter=pv.tau_filter, nms=lambda a: backend.run(backend.prepare(a[:, :4], a[:, 4], a[:, 5]), .45))
Tự kiểm (không cần ultralytics):
    python -m sponge_sim.stages --selftest   (hoặc tests/test_review_fixes.py)
"""
import gc
import sys
import time

import numpy as np
import torch

TINY = float(np.finfo(np.float32).tiny)


def count_subnormal(t):
    t = t.detach().float().abs()
    return int(((t > 0) & (t < TINY)).sum())


def subnormal_report(model, x):
    """Số subnormal ở đầu vào và ở đầu ra từng module lá (Conv, BatchNorm, hàm kích hoạt...)."""
    rows, hooks = [], []
    for name, m in model.named_modules():
        if len(list(m.children())) == 0:
            def hook(mod, inp, out, name=name):
                if isinstance(out, torch.Tensor):
                    rows.append(dict(layer=name, kind=type(mod).__name__, numel=out.numel(), subnormal=count_subnormal(out)))
            hooks.append(m.register_forward_hook(hook))
    try:
        with torch.no_grad():
            model(x)
    finally:
        for h in hooks:
            h.remove()
    tot = sum(r['subnormal'] for r in rows); n = sum(r['numel'] for r in rows)
    return dict(input_subnormal=count_subnormal(x), activations_subnormal=tot, activations_total=n, share=tot / max(n, 1),
                worst_layers=sorted(rows, key=lambda r: -r['subnormal'])[:5])


def _time(fn, repeats, warmup):
    for _ in range(warmup):
        fn()
    out = []
    was = gc.isenabled(); gc.disable()
    try:
        for _ in range(repeats):
            t0 = time.perf_counter_ns(); fn(); out.append((time.perf_counter_ns() - t0) / 1e6)
    finally:
        if was:
            gc.enable()
    return out


def stage_times(model, x_clean, x_att, decode=None, tau_filter=None, nms=None, tau=0.25, repeats=20, warmup=3):
    """Trả trung vị ms từng chặng cho sạch / tấn công và hiệu, cộng forward với flush denormal bật."""
    def fwd(x):
        with torch.no_grad():
            r = model(x)
        return r[0] if isinstance(r, (tuple, list)) else r
    res = {}
    raw = {k: fwd(x) for k, x in (('clean', x_clean), ('attacked', x_att))}
    order = ['clean', 'attacked', 'attacked', 'clean']       # ABBA
    xs = dict(clean=x_clean, attacked=x_att)

    def run(name, make):
        t = {'clean': [], 'attacked': []}
        for k in order:
            t[k] += _time(make(k), repeats // 2, warmup)
        c, a = float(np.median(t['clean'])), float(np.median(t['attacked']))
        res[name] = dict(clean_ms=c, attacked_ms=a, delta_ms=a - c, ratio=a / c if c else None)

    run('forward', lambda k: (lambda: fwd(xs[k])))
    prev = torch.set_flush_denormal(True)
    try:
        run('forward_flush_denormal', lambda k: (lambda: fwd(xs[k])))
    finally:
        torch.set_flush_denormal(False)
    res['flush_denormal_supported'] = bool(prev)
    if decode is not None:
        dec = {k: decode(raw[k][0]) for k in raw}
        run('decode', lambda k: (lambda: decode(raw[k][0])))
        if tau_filter is not None:
            act = {k: tau_filter(dec[k], tau, None)[0] for k in dec}
            run('tau_filter', lambda k: (lambda: tau_filter(dec[k], tau, None)))
            res['n_candidates'] = {k: int(len(act[k])) for k in act}
            if nms is not None:
                run('nms', lambda k: (lambda: nms(act[k])))
    parts = [res[s]['delta_ms'] for s in ('forward', 'decode', 'tau_filter', 'nms') if s in res]
    res['sum_of_stage_deltas_ms'] = float(sum(parts))
    res['forward_delta_removed_by_flush_ms'] = res['forward']['delta_ms'] - res['forward_flush_denormal']['delta_ms']
    return res


def selftest():
    torch.manual_seed(0); torch.set_num_threads(1)
    model = torch.nn.Sequential(torch.nn.Conv2d(3, 32, 3, padding=1), torch.nn.SiLU(), torch.nn.Conv2d(32, 32, 3, padding=1), torch.nn.SiLU(),
                                torch.nn.Conv2d(32, 8, 1)).eval()
    x_clean = torch.rand(1, 3, 160, 160)
    x_sub = torch.full((1, 3, 160, 160), 1e-39)             # đầu vào toàn subnormal
    assert count_subnormal(x_sub) == x_sub.numel() and count_subnormal(x_clean) == 0
    a, b = subnormal_report(model, x_clean), subnormal_report(model, x_sub)
    assert b['input_subnormal'] > 0 and a['input_subnormal'] == 0
    dec = lambda r: r.reshape(8, -1).T.contiguous()
    tf = lambda d, tau, cap: (d[d[:, 4] > tau], 0)
    r = stage_times(model, x_clean, x_sub, decode=dec, tau_filter=tf, nms=lambda act: act[:, 4].argsort(), tau=0.0, repeats=10, warmup=1)
    for k in ('forward', 'forward_flush_denormal', 'decode', 'tau_filter', 'nms'):
        assert r[k]['clean_ms'] > 0
    print('selftest OK')
    print(' subnormal trong activation: sạch %d, đầu vào subnormal %d' % (a['activations_subnormal'], b['activations_subnormal']))
    print(' forward: sạch %.2f ms, subnormal %.2f ms (tỉ số %.2f); bật flush: tỉ số %.2f; flush hỗ trợ: %s'
          % (r['forward']['clean_ms'], r['forward']['attacked_ms'], r['forward']['ratio'], r['forward_flush_denormal']['ratio'], r['flush_denormal_supported']))


if __name__ == '__main__':
    selftest() if '--selftest' in sys.argv else print(__doc__)
