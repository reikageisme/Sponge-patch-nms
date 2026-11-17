"""So optimizer không đạo hàm ở cùng ngân sách truy vấn, có đường cong hội tụ (điểm phản biện: GA 625 lần đánh giá là quá yếu).

Mọi phương pháp tối ưu cùng một hàm `fitness(batch_patch[B, C, H, W]) -> điểm[B]` (càng lớn càng tốt), mỗi patch được chấm
tính là MỘT truy vấn, và dừng đúng ở cùng ngân sách. Ghi best-so-far tại các mốc ngân sách để vẽ hội tụ.
  random   : rút ngẫu nhiên đều (baseline B3 của bài)
  ga       : quần thể 20, elite 5, lai một điểm theo khối, đột biến Gauss (cùng cỡ quần thể với SpongeGA của repo)
  nes      : NES đối xứng (antithetic), ước lượng gradient bằng xếp hạng, bước Adam, tham số hoá trong không gian thấp chiều rồi nội suy lên
  es       : (1+lambda)-ES với bước tự thích nghi theo luật 1/5
Kết luận về "tìm kiếm không đạo hàm không làm tăng N_tau" chỉ nên viết khi đường cong đã phẳng ở ngân sách lớn nhất
và phương pháp mạnh nhất vẫn không vượt random; nếu chưa phẳng thì claim phải giới hạn ở ngân sách đã thử.

Nối với repo (ví dụ, YOLOv8n 320 px, cùng mục tiêu với attacks_provenance.objective):
    def fitness(batch):                                   # batch [B, 3, 64, 64] trong [0, 1]
        out = []
        for p in batch:
            x = transform(insert(train, p[None], locations))          # EOT + chèn, như optimize()
            pred = victim.model(x); pred = pred[0] if isinstance(pred, (tuple, list)) else pred
            out.append(float(objective(pred[:, 4:].max(dim=1).values.float()).mean()))
        return torch.tensor(out)
    res = sweep(fitness, shape=(3, 64, 64), budgets=[625, 2500, 10000, 40000], seeds=range(5))
Lưu ý ngân sách: trong repo một "truy vấn" = một ảnh x một lần EOT; ở đây một truy vấn = một patch được chấm trên cả tập.
Quy đổi cho đúng khi so với 62 500 của E7 và ghi rõ đơn vị trong bài.

    python -m sponge_sim.optimizers --selftest   (hoặc tests/test_review_fixes.py)
"""
import json
import sys

import numpy as np
import torch
import torch.nn.functional as F


class Counter:
    def __init__(self, fitness, budget):
        self.f, self.budget, self.used, self.best, self.best_x, self.trace = fitness, budget, 0, -float('inf'), None, []

    def left(self):
        return self.budget - self.used

    def __call__(self, batch):
        batch = batch[:self.left()]
        if len(batch) == 0:
            return torch.empty(0)
        s = self.f(batch.clamp(0, 1)).float(); self.used += len(batch)
        i = int(s.argmax())
        if float(s[i]) > self.best:
            self.best, self.best_x = float(s[i]), batch[i].clamp(0, 1).clone()
        self.trace.append((self.used, self.best))
        return s


def run_random(c, shape, g, batch=20):
    while c.left() > 0:
        c(torch.rand((batch,) + shape, generator=g))


def run_ga(c, shape, g, pop=20, elite=5, sigma=0.1, block=8):
    P = torch.rand((pop,) + shape, generator=g); s = c(P)
    while c.left() > 0 and len(s) == len(P):
        order = s.argsort(descending=True); E = P[order[:elite]]
        kids = []
        for _ in range(pop - elite):
            a, b = E[torch.randint(0, elite, (2,), generator=g)]
            mask = (torch.rand((1, shape[1] // block + 1, shape[2] // block + 1), generator=g) < .5).float()
            mask = F.interpolate(mask[None], size=shape[1:], mode='nearest')[0]
            kid = mask * a + (1 - mask) * b
            kids.append((kid + sigma * torch.randn(shape, generator=g) * (torch.rand(shape, generator=g) < .1)).clamp(0, 1))
        P = torch.cat([E, torch.stack(kids)]); s2 = c(P[elite:])
        if len(s2) < pop - elite:
            break
        s = torch.cat([s[order[:elite]], s2])


def run_nes(c, shape, g, pairs=10, sigma=0.1, lr=0.05, low=16):
    """Tìm trong lưới low x low rồi nội suy lên cỡ patch: giảm số chiều từ C*H*W xuống C*low*low."""
    lshape = (shape[0], min(low, shape[1]), min(low, shape[2]))
    up = lambda z: torch.sigmoid(F.interpolate(z, size=shape[1:], mode='bilinear', align_corners=False))
    th = torch.zeros(lshape); m = torch.zeros(lshape); v = torch.zeros(lshape); t = 0
    while c.left() >= 2:
        k = min(pairs, c.left() // 2)
        eps = torch.randn((k,) + lshape, generator=g)
        s = c(up(torch.cat([th + sigma * eps, th - sigma * eps])))
        if len(s) < 2 * k:
            break
        r = s.argsort().argsort().float(); r = (r - r.mean()) / (r.std() + 1e-12)       # định hình fitness theo hạng
        grad = ((r[:k] - r[k:]).view(-1, 1, 1, 1) * eps).mean(0) / sigma
        t += 1; m = .9 * m + .1 * grad; v = .999 * v + .001 * grad ** 2
        th = th + lr * (m / (1 - .9 ** t)) / ((v / (1 - .999 ** t)).sqrt() + 1e-8)


def run_es(c, shape, g, lam=10, sigma=0.2, low=16):
    lshape = (shape[0], min(low, shape[1]), min(low, shape[2]))
    up = lambda z: torch.sigmoid(F.interpolate(z, size=shape[1:], mode='bilinear', align_corners=False))
    x = torch.zeros(lshape); fx = float(c(up(x[None]))[0])
    while c.left() > 0:
        kids = x + sigma * torch.randn((lam,) + lshape, generator=g); s = c(up(kids))
        if len(s) == 0:
            break
        succ = float((s > fx).float().mean()); i = int(s.argmax())
        if float(s[i]) > fx:
            x, fx = kids[i], float(s[i])
        sigma *= 1.22 if succ > .2 else .82                                               # luật 1/5
        sigma = float(min(max(sigma, 1e-3), 2.0))


METHODS = dict(random=run_random, ga=run_ga, nes=run_nes, es=run_es)


def sweep(fitness, shape, budgets, seeds=range(5), methods=METHODS, marks=None):
    """Trả best-so-far tại từng mốc ngân sách, theo phương pháp và seed, cộng kiểm tra đã hội tụ hay chưa."""
    budgets = sorted(budgets); B = budgets[-1]; marks = sorted(set(marks or budgets))
    out = dict(shape=list(shape), budgets=budgets, seeds=list(seeds), curves={}, summary={})
    for name, fn in methods.items():
        C = []
        for sd in seeds:
            g = torch.Generator().manual_seed(1000 * sd + sum(map(ord, name))); c = Counter(fitness, B)
            fn(c, tuple(shape), g)
            tr = np.array(c.trace)
            C.append([float(tr[tr[:, 0] <= b][-1, 1]) if (tr[:, 0] <= b).any() else float('nan') for b in marks])
        C = np.array(C); out['curves'][name] = dict(marks=marks, best_by_seed=C.tolist(), mean=np.nanmean(C, 0).tolist())
    ref = np.array(out['curves']['random']['best_by_seed']) if 'random' in out['curves'] else None
    for name, cv in out['curves'].items():
        C = np.array(cv['best_by_seed']); last, prev = C[:, -1], C[:, -2] if C.shape[1] > 1 else C[:, -1]
        gain = last - prev
        s = dict(final_mean=float(last.mean()), final_sd=float(last.std(ddof=1)) if len(last) > 1 else 0.0,
                 gain_last_step_mean=float(gain.mean()), plateau=bool(abs(gain.mean()) <= 0.01 * max(abs(last.mean()), 1e-12)))
        if ref is not None and name != 'random':
            d = last - ref[:, -1]; s['minus_random_mean'] = float(d.mean()); s['seeds_above_random'] = f'{int((d > 0).sum())}/{len(d)}'
        out['summary'][name] = s
    return out


def selftest():
    torch.manual_seed(0); H = 32
    target = (torch.rand(3, H, H) > .5).float()
    target = F.interpolate(F.interpolate(target[None], size=(4, 4), mode='bilinear'), size=(H, H), mode='bilinear')[0]   # mục tiêu trơn
    calls = [0]

    def fitness(batch):
        calls[0] += len(batch)
        return -((batch - target) ** 2).mean(dim=(1, 2, 3))
    res = sweep(fitness, (3, H, H), budgets=[200, 800, 3200], seeds=range(3))
    assert calls[0] == 3200 * 3 * len(METHODS), calls[0]                        # mọi phương pháp dùng đúng cùng ngân sách
    S = res['summary']
    for n in METHODS:
        m = res['curves'][n]['mean']; assert m[0] <= m[1] + 1e-12 <= m[2] + 2e-12, (n, m)    # best-so-far không giảm
    assert S['nes']['final_mean'] > S['random']['final_mean'] and S['es']['final_mean'] > S['random']['final_mean']
    print('selftest OK (hàm thử: khớp một ảnh mục tiêu trơn; điểm = -MSE, càng gần 0 càng tốt)')
    for n in METHODS:
        print(' %-6s best tại 200 / 800 / 3200 truy vấn: %s | phẳng: %s | hơn random: %s'
              % (n, ' / '.join('%.4f' % x for x in res['curves'][n]['mean']), S[n]['plateau'], S[n].get('seeds_above_random', '-')))
    return res


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        r = selftest()
        if len(sys.argv) > 2:
            open(sys.argv[2], 'w', encoding='utf-8').write(json.dumps(r, indent=1))
    else:
        print(__doc__)
