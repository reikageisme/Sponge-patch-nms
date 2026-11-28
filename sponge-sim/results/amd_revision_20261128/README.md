# AMD re-measurement after review (28/11/2026)

Raw records and analyses of E9-R, E10-R and E10-RM, measured on the same frequency-locked AMD Ryzen 5 5500 as the
24/11 replication (`../amd_20261124`). These numbers are a separate set and are not pooled with 24/11.

## Preregistration

- Plan: `sponge-sim/prereg/PREREG_AMD_REVISION_20261128.md`, tag `prereg-amd-revision-20261128` (f7c9140).
  Every run used f7c9140 (`*/prereg_commit.txt`).
- Deviations: `sponge-sim/prereg/DEVIATIONS_AMD_REVISION_20261128.md` (written on the machine before smoke and
  appended before the E10-RM rerun and before the analyses; entries are never edited).

## Machine and lock

Xubuntu 24.04.5 live USB, `amd-pstate-epp`, governor `performance`, min = max = 3.6 GHz, boost off, process pinned to
CPU 2 with its SMT sibling (CPU 8) offline, no swap. The runner (`sponge-sim/studies/linux_profile/run_revision.sh`)
checks the clock with `turbostat` before and after each experiment (`*/xung_truoc.log`, `*/xung_sau.log`).
All six completed experiment runs (three in `smoke`, E9-R and E10-R in `full-01`, E10-RM in `full-02`) passed
both checks (3574-3575 MHz, 100% busy). The failed `full-01/e10rm` attempt passed its pre-run check and has no
post-run check.

## Layout

| Folder | Content |
|---|---|
| `smoke` | smoke run of all three experiments (exit 0). Not used for results. |
| `full-01/e9r` | E9-R, finer N grid in the full pipeline. Complete. |
| `full-01/e10r` | E10-R, reference attacks, 50 images, 3 + 20 repetitions, NMS timed inside the full call. Complete. |
| `full-01/e10rm` | **Failed** E10-RM attempt: the USB overlay ran out of space at 06:08:19Z when Ubuntu's `apt-daily-upgrade` wrote its package cache (DEVIATIONS 6). No `DONE`, no post-run clock check, last line cut. Kept as recorded; not analysed. |
| `full-02/e10rm` | E10-RM rerun (exploratory: `--malloc-fixed --n-images 10`), same tag and runner (DEVIATIONS 8). Complete. |
| `analysis` | outputs of the preregistered analyses, their logs, and the two post-run helper scripts (DEVIATIONS 9-10) |

Each experiment folder has `environment.txt`, `prereg_commit.txt`, `run.log`, `run/manifest.json` and
`run/raw_P1_cpu2.jsonl` (one JSON record per measurement). `full-01/e10r/run/e10r_new_endpoints.json` and
`full-02/e10rm/run/e10r_new_endpoints.json` are written by `analyze_new.py` next to the raw file.

## Analyses (run on the measurement machine after unlocking the clock)

```bash
AA=sponge-sim/results/aa_linux_20261124/x/sponge-aa-20261124/full-01
E1=sponge-sim/results/amd_20261124/full-01/e1/run
R=sponge-sim/results/amd_revision_20261128
python -X utf8 sponge-sim/studies/e9_pipeline/analyze.py --part a --run-dir $R/full-01/e9r/run \
  --aa320 $AA/aa_320/summary.json --aa640 $AA/aa_640/summary.json --out $R/analysis/e9r_summary_part_a.json
python -X utf8 sponge-sim/studies/e10_reference/analyze.py $R/full-01/e10r/run $E1/summary.json $E1/raw_P1_cpu2.jsonl $R/analysis/e10r_summary.json
python -X utf8 sponge-sim/studies/e10_reference/analyze.py $R/full-02/e10rm/run $E1/summary.json $E1/raw_P1_cpu2.jsonl $R/analysis/e10rm_summary.json
python -X utf8 sponge-sim/studies/e10r_reference_rerun/analyze_new.py $R/full-01/e10r/run
python -X utf8 $R/analysis/analyze_new_safe_spearman.py sponge-sim/studies/e10r_reference_rerun/analyze_new.py $R/full-02/e10rm/run
python -X utf8 $R/analysis/n_harm_e9r.py sponge-sim/studies/review_20261127/diag_posthoc.py $R/full-01/e9r/run/raw_P1_cpu2.jsonl $R/analysis/e9r_n_harm.json
```

On the machine the inputs from 24/11 were read from a RAM copy (DEVIATIONS 11), so the logs show `/dev/shm` paths.

## Checksums

Written on the measurement machine before transfer; paths are relative to this folder.

```bash
cd sponge-sim/results/amd_revision_20261128
sha256sum -c results.sha256 results_full02.sha256 derived.sha256
```

- `results.sha256`: `full-01` and `smoke` as they stood after the main session (before any analysis output).
- `results_full02.sha256`: `full-02`.
- `derived.sha256`: `analysis/` and the two `e10r_new_endpoints.json` files.
