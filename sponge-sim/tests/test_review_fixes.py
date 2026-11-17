"""Test cho phần bổ sung sau phản biện 16/11/2026 (REVIEW_FIXES_20261116.md).
Chạy bằng pytest, hoặc không cần pytest:  python tests/test_review_fixes.py
Không cần ultralytics; test dùng torchvision tự bỏ qua khi thiếu.
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
REPO = ROOT.parent
NB = 2000   # bootstrap ngắn cho test


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _R(seed=0, mean=1.03, sd=.02, shape=(50, 5)):
    return np.exp(np.log(mean) + np.random.default_rng(seed).normal(0, sd, shape))


# ---------------------------------------------------------------- stats
def test_null_model_passes_rule_when_ratio_near_one():
    from sponge_sim import stats
    R = _R()
    good = stats.skill_vs_null(R, np.full_like(R, 1.03), 1, NB)
    bad = stats.skill_vs_null(R, np.full_like(R, 1.10), 1, NB)
    assert good['null_passes'] and good['model_passes']          # luật 0,05 không phân biệt được hai mô hình
    assert good['skill'] > 0 and good['model_better_than_null']
    assert bad['skill'] < 0 and not bad['model_better_than_null'] and bad['signed_log_bias'] > 0


def test_tost_margins():
    from sponge_sim import stats
    R = _R()
    assert stats.tost_ratio(R, .05, 1, NB)['equivalent']
    t = stats.tost_ratio(R, .01, 1, NB)
    assert not t['equivalent'] and t['above_margin']
    assert abs(stats.tost_ratio(R, .05, 1, NB)['mean_ratio'] - 1.03) < .005


def test_ratio_summaries_mean_pulled_by_small_clean_counts():
    from sponge_sim import stats
    Nc = np.concatenate([np.full(40, 50.), np.full(10, 2.)])
    r = stats.ratio_summaries(np.full((50, 5), 5000.), Nc, 1, NB)
    assert r['ratio_of_medians'] == 100 and r['median_of_ratios'] == 100
    assert r['mean_of_ratios'] > 3 * r['ratio_of_medians'] and abs(r['share_clean_below_10'] - .2) < 1e-9


def test_tail_summary():
    from sponge_sim import stats
    t = stats.tail_summary(np.concatenate([np.full(95, 30.), np.full(5, 120.)]))
    assert t['median'] == 30 and abs(t['share_over_100ms'] - .05) < 1e-9 and t['p99'] == 120


def test_old_stats_unchanged():
    from sponge_sim import stats
    x = np.array([.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0])
    assert stats.sign_flip_p(x) == 2 / 1024 and abs(stats.dz(x) - x.mean() / x.std(ddof=1)) < 1e-12
    assert stats.holm([.01, .04, .03]) == [.03, .06, .06]


# ---------------------------------------------------------------- drift gate
def _gate(seq, **kw):
    from sponge_sim import timing
    it = iter(seq)
    return timing.DriftGate(lambda: next(it), cooldown_s=0, sleep=lambda s: None, **kw)


def test_drift_gate_remeasures_then_aborts():
    from sponge_sim import timing
    calls = []
    g = _gate([1.00, 1.00, 1.01, 1.00, 1.08, 1.01, 1.02, 1.2, 1.21, 1.2, 1.22, 1.19, 1.21], max_retries=2)
    assert g.run_block(0, lambda: calls.append(0) or ['a']) == ['a']
    assert g.run_block(1, lambda: calls.append(1) or ['b']) == ['b'] and calls.count(1) == 2
    try:
        g.run_block(2, lambda: ['c'])
        raise AssertionError('phải dừng phiên')
    except timing.SessionAbort:
        pass
    s = g.summary()
    assert s == dict(attempts=6, accepted=2, rejected=4, max_abs_accepted=s['max_abs_accepted']) and s['max_abs_accepted'] <= .03


def test_drift_gate_logs_every_attempt_and_e12_writes_only_accepted_rows():
    from sponge_sim import timing
    e12 = _load('studies/e12_patch_remeasure_gated/run.py', 'e12run')

    class W:
        def __init__(self):
            self.rows = []

        def write(self, r):
            self.rows.append(r)
    w = W()
    it = iter([1.0, 1.0, 1.0, 1.0, 1.1, 1.0, 1.0])       # khối 0 ổn; khối 1 lần đầu trôi, lần hai ổn
    gate = timing.DriftGate(lambda: next(it), writer=w, cooldown_s=0, sleep=lambda s: None)
    n = {'k': 0}

    def measure(bi, ids):
        n['k'] += 1
        return [dict(kind='pipeline', block=bi, image_id=i, attempt_tag=n['k']) for i in ids]
    done = e12.run_blocks([(0, [1, 2]), (1, [3, 4])], measure, gate, w)
    kinds = [r['kind'] for r in w.rows]
    assert done == 2 and kinds.count('pipeline') == 4 and kinds.count('block_attempt') == 4 and kinds[-1] == 'gate_summary'
    assert {r['attempt_tag'] for r in w.rows if r['kind'] == 'pipeline' and r['block'] == 1} == {3}     # chỉ dòng của lần được nhận
    assert w.rows[-1]['rejected'] == 1 and w.rows[-1]['blocks_done'] == 2


def test_e12_reuses_e11_measurement_and_gate_config():
    e12 = _load('studies/e12_patch_remeasure_gated/run.py', 'e12run2')
    src = (ROOT / 'studies/e12_patch_remeasure_gated/run.py').read_text(encoding='utf-8')
    assert e12.GATE == dict(flag=0.03, max_retries=3, cooldown_s=60.0)
    assert 'e11.build_input(' in src and 'e11.pipeline_fn(' in src and 'ap_.insert' in src
    timed = src[src.index('def measure_block'):]
    assert 'timing.timed(e11.pipeline_fn' in timed and 'insert(' not in timed.split('timing.timed(e11.pipeline_fn')[1][:200]


# ---------------------------------------------------------------- hw_linux.lock_status
def _fake_sys(root, gov='performance', fmin='2400000', fmax='2400000', no_turbo='1', sib='2,10', sib_online='0', iso='2'):
    c = root / 'devices/system/cpu'
    for p, v in ((c / 'cpu2/cpufreq/scaling_governor', gov), (c / 'cpu2/cpufreq/scaling_min_freq', fmin), (c / 'cpu2/cpufreq/scaling_max_freq', fmax),
                 (c / 'intel_pstate/no_turbo', no_turbo), (c / 'cpu2/topology/thread_siblings_list', sib), (c / 'cpu10/online', sib_online), (c / 'isolated', iso)):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(v)


def test_lock_status_ready_and_problems():
    from sponge_sim import hw_linux
    with tempfile.TemporaryDirectory() as d:
        _fake_sys(Path(d))
        ok = hw_linux.lock_status(2, d)
        assert ok['ready'] and ok['smt_siblings'] == [10] and ok['problems'] == []
    with tempfile.TemporaryDirectory() as d:
        _fake_sys(Path(d), gov='powersave', fmin='800000', no_turbo='0', sib_online='1', iso='3')
        bad = hw_linux.lock_status(2, d)
        assert not bad['ready'] and len(bad['problems']) == 5


# ---------------------------------------------------------------- stages, optimizers
def test_subnormal_count_and_stage_times():
    import torch
    from sponge_sim import stages
    torch.manual_seed(0)
    model = torch.nn.Sequential(torch.nn.Conv2d(3, 8, 3, padding=1), torch.nn.SiLU(), torch.nn.Conv2d(8, 6, 1)).eval()
    x, xs = torch.rand(1, 3, 32, 32), torch.full((1, 3, 32, 32), 1e-39)
    assert stages.count_subnormal(xs) == xs.numel() and stages.count_subnormal(x) == 0
    assert stages.subnormal_report(model, xs)['input_subnormal'] == xs.numel()
    r = stages.stage_times(model, x, xs, decode=lambda t: t.reshape(6, -1).T.contiguous(), tau_filter=lambda d, tau, cap: (d[d[:, 4] > tau], 0),
                           nms=lambda a: a[:, 4].argsort(), tau=-1e9, repeats=4, warmup=1)
    for k in ('forward', 'forward_flush_denormal', 'decode', 'tau_filter', 'nms'):
        assert r[k]['clean_ms'] > 0 and r[k]['attacked_ms'] > 0
    assert r['n_candidates']['clean'] == 32 * 32


def test_optimizers_use_equal_budget_and_are_monotone():
    import torch
    from sponge_sim import optimizers
    target = torch.rand(3, 16, 16)
    calls = [0]

    def fitness(batch):
        calls[0] += len(batch)
        return -((batch - target) ** 2).mean(dim=(1, 2, 3))
    res = optimizers.sweep(fitness, (3, 16, 16), budgets=[100, 400], seeds=range(2))
    assert calls[0] == 400 * 2 * len(optimizers.METHODS)
    for n in optimizers.METHODS:
        m = res['curves'][n]['mean']
        assert m[0] <= m[1] + 1e-12
        assert set(res['summary'][n]) >= {'final_mean', 'plateau'}


# ---------------------------------------------------------------- inject: một lớp, và lưới E1 mới
def test_inject_single_class_and_e1_large_grid():
    from sponge_sim import inject
    t, meta = inject.make(1000, 'disjoint', 7, anchors=8400, nc=1)
    assert set(t[:, 5].tolist()) == {0.0} and meta['nc'] == 1 and int((t[:, 4] > .01).sum()) == 1000
    e1 = _load('studies/e1_dose/run.py', 'e1run')
    base = e1.groups(e1.CONFIG)
    big = e1.groups({**e1.CONFIG, **e1.NC1_LARGE})
    assert not any(g['nc'] == 1 and g['anchors'] > 2100 for g in base)                  # lưới mặc định không đổi
    assert len(base) == 123
    assert {(g['anchors'], g['nc']) for g in big} == {(8400, 1), (8400, 80), (10000, 1), (10000, 80)}
    assert all(g['cap'] is None and g['n'] >= 1000 for g in big)


def test_batched_nms_single_class_is_not_cheaper_on_large_sets():
    try:
        import torchvision  # noqa: F401
    except ImportError:
        return                                                                           # bỏ qua khi thiếu torchvision
    import time
    import torch
    from sponge_sim import inject
    out = {}
    for nc in (80, 1):
        t, _ = inject.make(8000, 'disjoint', 3, anchors=8400, nc=nc)
        a = t[t[:, 4] > .01]
        b, s, c = a[:, :4].contiguous(), a[:, 4].contiguous(), a[:, 5].long()
        ts = []
        for _ in range(3):
            t0 = time.perf_counter()
            keep = torchvision.ops.batched_nms(b, s, c, .45)
            ts.append(time.perf_counter() - t0)
        out[nc] = (min(ts), len(keep))
    assert out[1][1] == out[80][1] == 8000                                               # hộp rời nhau: giữ hết ở cả hai
    assert out[1][0] > out[80][0]                                                        # một lớp chậm hơn 80 lớp (không ghim, chỉ kiểm hướng)


# ---------------------------------------------------------------- phân tích bổ sung E10 trên raw giả
def _fake_e10(run, e1_summary, n_img=12, seeds=(0, 1)):
    rng = np.random.default_rng(0)
    curves = {}
    for be in ('tv_nms',):
        for A, ns in (('2100', (10, 30)), ('10000', (100, 1000, 10000))):
            for n in ns:
                curves[f'P1_cpu2|{A}|{be}|mixed|80|None|{n}'] = dict(median_ms=0.001 * n)
    Path(e1_summary).write_text(json.dumps(dict(curves=curves)), encoding='utf-8')
    rows = []
    for i in range(n_img):
        t0 = 300 + rng.normal(0, 1)
        for arm, seed, n, extra in [('clean_a', None, 40, 0), ('clean_b', None, 40, 0)] + [('overload', s, 5000, 9.0) for s in seeds]:
            rows.append(dict(kind='micro', image_id=i, arm=arm, seed=seed, backend='tv_nms', nms_ns=(0.05 + 0.001 * n) * 1e6,
                             n_by_tau={'0.01': n * 2, '0.25': n}, nms_input=n, kept=min(n, 300)))
            for rep in range(3):
                rows.append(dict(kind='pipeline', image_id=i, arm=arm, seed=seed, backend='tv_nms', total_ns=(t0 + extra + rng.normal(0, .5)) * 1e6))
    Path(run).mkdir(parents=True, exist_ok=True)
    (Path(run) / 'raw_P1_cpu2.jsonl').write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')


def test_e10_addon_on_synthetic_raw():
    addon = _load('studies/e10_reference/analyze_addon.py', 'e10addon')
    with tempfile.TemporaryDirectory() as d:
        run, e1s = Path(d) / 'run', Path(d) / 'e1.json'
        _fake_e10(run, e1s)
        r = addon.analyse(run, e1s, n_boot=500)
    m = r['model']['overload|tv_nms']
    assert m['null_passes'] and 0.02 < m['null_median_abs_log_err'] < 0.04                # tăng khoảng 3%: mô hình rỗng vẫn qua luật 0,05
    assert r['n_ratio']['overload|tau0.25']['ratio_of_medians'] == 125.0
    c = r['criterion']['overload|tv_nms']
    assert 8 < c['d_total_ms'] < 10 and 4 < c['d_nms_ms'] < 6 and 0.3 < c['share_outside_nms'] < 0.6
    assert r['tost']['overload|tv_nms']['0.05']['equivalent'] and not r['tost']['overload|tv_nms']['0.01']['equivalent']
    assert r['tails']['overload|tv_nms']['share_over_100ms'] == 1.0


# ---------------------------------------------------------------- kiểm tóm tắt trên kết quả đã commit
def test_summary_checks_on_committed_results():
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        for s in ('criterion_null_model.py', 'single_class_check.py'):
            subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'studies/review_20261116' / s), str(REPO), d], check=True, capture_output=True)
        a = json.loads((Path(d) / 'a1_criterion_null_model.json').read_text(encoding='utf-8'))
        b = json.loads((Path(d) / 'a2_single_class_check.json').read_text(encoding='utf-8'))
    assert a['criterion']['counterexamples_to_only_if'] == 2 and a['criterion']['delta_total_exceeds_threshold_in'] == '6/6'
    assert a['null_model']['model_passes'] == 3 and a['null_model']['null_point_below_0_05'] == 6
    assert [round(x['ratio_of_medians']) for x in a['n_tau'] if 'tau0.25' in x['cell']] == [124, 107]
    assert b['large_grids'] == [8400, 10000] and b['large_grids_without_nc1'] == [8400, 10000]


if __name__ == '__main__':
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith('test_') and callable(v)):
        try:
            fn()
            print('PASS', name)
        except Exception as e:  # noqa: BLE001
            fails += 1
            print('FAIL', name, '|', type(e).__name__, str(e)[:300])
    print(f'{fails} lỗi')
    sys.exit(1 if fails else 0)
