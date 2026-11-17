# Sponge Patch: when does inflating NMS become an availability problem?

[Tiếng Việt](README.vi.md) · [Measurement harness](sponge-sim/README.md) · [Progress log](sponge-sim/PROGRESS.md) · [Deviations](sponge-sim/DEVIATIONS.md) · [Internal review](docs/REVIEW/04_q1_gap_analysis.md)

Research code for the HUTECH project *"Sponge Patch adversarial attacks: exploiting resource exhaustion with spatial
optimisation"*. The project began as an attack paper. Its current, evidence-driven question is narrower and, we think,
more useful:

> **A.** Is the number of candidates entering NMS (N<sub>τ</sub>) a reliable proxy for latency and service degradation?
> Where does the proxy hold, and where does it mislead?
>
> **C.** Under which conditions (NMS backend × class-aware/agnostic × top-k cap × τ × allowed CPU cores × frame period)
> does an NMS-targeted attack actually turn into a missed deadline?

Every number below is traceable to a raw record (`file:selector`). Experiments are pre-registered and git-tagged
before measurement, and negative results are reported as they are.

---

## What the evidence says so far

### 1. The optimised patch barely moves N<sub>τ</sub>, and saliency placement does not help

The primary contrast is SG-GA (saliency-guided GA) minus GA at the image centre, using the mean per-image candidate ratio
(patch / clean, denominator `max(clean, 1)`). The analysis is paired over 10 patch seeds.

| Cohort | Images | Mean difference | 95% CI | Exact sign-flip p | d<sub>z</sub> | Source |
|---|---:|---:|---|---:|---:|---|
| OLD128 | 128 | −0.00513 | [−0.01118; 0.00071] | 0.1504 | −0.498 | `outputs/extended_q1_20261002/analysis.json:primary` |
| X1-500 | 500 | −0.02934 | [−0.03833; −0.02160] | 0.001953 | −2.05 | `outputs/x1_500img_20261018/analysis.json:596-653` |

- In X1-500, p = 0.001953 is the smallest value attainable with 10 seeds: **all 10 seeds have the same (negative) sign.**
  On this cohort SG-GA is worse than centre placement. It is also worse than GA with random placement: −0.04386
  [−0.05451; −0.03385], Holm p = 0.0293. Against plain random search the difference is 0.00174 [−0.00270; 0.00641],
  Holm p = 1.0, which detects no difference but does not establish equivalence
  (`outputs/x1_500img_20261018/analysis.json:secondary_holm_family`).
- X1-500 is an **expansion** run after OLD128 returned p = 0.1504 (the 128 images are a subset of the 500). It is not an
  independent replication.
- CIs are computed over seeds and are conditional on the fixed image set. A two-level (image × seed) bootstrap is planned.
- Both rows are recomputed from raw records by `sponge-sim/tests/test_regression_x1.py` (matches to 1e-12).

### 2. N<sub>τ</sub> ranks NMS cost across images, but patch-induced changes drown in noise

Exploratory re-analysis of the historical X1-500 timings: unpinned CPU, one NMS sample per record, pure-PyTorch NMS
(`sponge-sim/results/e2a/20261021T145544/summary.json`).

| Comparison | Spearman ρ [95% CI, image-cluster bootstrap] | Selector |
|---|---|---|
| Between images (clean): N vs NMS latency | 0.9379 [0.9215; 0.9499] | `between_image_clean` |
| Within image: ΔN from SG-GA patch vs Δ NMS latency | 0.1214 [0.103; 0.1396] | `within_image.sg_ga` |

Mean ΔN caused by the patches is small, from −2.5836 to +1.636 (`within_image.*.mean_dN`). On clean images, repeated
measurements with identical N differ by a median of 0.27 ms, but the 90th percentile is 13.57 ms
(`noise_vs_effect.clean_clean_abs_diff_ms`). A post-hoc A/A control (`posthoc_aa.json`, declared in DEVIATIONS) overlaps
every attack condition. **The historical data cannot separate attack-induced latency from measurement noise.** That is
why we built a new harness.

### 3. A measurement protocol that can see sub-1% effects

`sponge-sim` pins the process to cores read from the OS topology and verifies the pinning under real load. It times each
stage separately and sizes measurement noise with an A/A design: 100 images × 20 runs per profile
(`sponge-sim/results/e5/20261021T151412/summary.json:profiles.<profile>.stages.<stage>.mde_ratio_pct`).

| Profile (Intel i5-1335U) | MDE forward | MDE end-to-end | MDE NMS (pure PyTorch) |
|---|---:|---:|---:|
| P1: 1 performance core | 0.58% | 0.59% | 1.07% |
| E1: 1 efficiency core | 1.94% | 1.27% | 2.97% |

The 4-efficiency-core profile is excluded from core-count conclusions: its threads did not run in parallel during the
session (see `sponge-sim/DEVIATIONS.md`).

### 4. Controlled positive control and dose-response (E1): pre-registration under review

E1 injects N synthetic candidates (0 to 2100, the anchor count of the 320×320 head) directly at the decoded → NMS
boundary. It varies backend, box geometry, class count and top-k cap, and measures NMS separately from the forward pass.
`[NO NUMBERS YET: not measured]`.

---

## Scope (read before citing)

- **Testbed:** resource-constrained simulation on a laptop CPU with pinned cores. One machine, one detector (YOLOv8n),
  prepared tensors (direct 320×320 resize).
- Patches are inserted digitally. EOT is a software transform. No camera capture and no embedded or ARM hardware
  have been measured.
- Candidate-count ratios and latency ratios are different quantities and are never mixed in one column. Cohorts
  (OLD128 / X1-500 / X2) are never pooled.
- "No significant difference" is never reported as "equivalent". Null results come with an MDE.

## Repository map

| Path | Content |
|---|---|
| `sponge-sim/` | New measurement harness: pinning, 4 NMS backends, synthetic injection, statistics, pre-registrations, results |
| `outputs/extended_q1_20261002`, `outputs/x1_500img_20261018` | Raw evaluation records of cohorts OLD128 and X1-500 (read-only) |
| `core/`, `attack/`, `experiments/` | Original attack and evaluation code (frozen; reused only through copies with source headers) |
| `docs/REVIEW/` | Internal audit: paper vs repository, gap analysis |
| `paper_en/main.tex` | Official manuscript (English); older Vietnamese versions under `paper/` |
| `docs/CLAUDE_CODE_SETUP.md` | Tooling notes for the research assistant setup |

## Reproduce the checks

```bash
cd sponge-sim
python -X utf8 -m pytest tests -q -p no:cacheprovider
python -X utf8 studies/e2_proxy/e2a_historical.py
```

Timing experiments must run on an idle machine with a fixed power plan. Measurements so far used Windows "Balanced"
(`381b4222-f694-41f0-9685-ff5bb260df2e`), and the checklist is printed by `python -m sponge_sim.hw`.

## Responsible release

We publish the measurement harness, schemas, manifests, synthetic fixtures and raw timing data. Positive controls use
**synthetic candidate injection** on a local testbed and do not require an optimised patch. No attack service or
packaged patch is distributed.

## Team

Phạm Tuấn Anh, Mai Quốc Bảo. Supervisor and corresponding author: Đinh Phương Nam (HUTECH).
