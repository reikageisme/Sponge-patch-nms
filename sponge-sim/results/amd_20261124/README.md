# AMD frequency-locked replication (24/11/2026)

Raw records and analyses of the CPU timing experiments repeated on a frequency-locked
AMD Ryzen 5 5500 (Zen 3). The manuscript (`paper_en/main.tex`) reports these numbers as
its primary results; laptop numbers are kept in their own folders and are not pooled with these.

## Machine and lock

- Xubuntu 24.04.5 live session, kernel 7.0.0-31-generic, `amd-pstate-epp` driver.
- Governor `performance`, scaling min = max = 3.6 GHz, boost off.
- Process pinned to logical CPU 2; its SMT sibling (CPU 8) offline; one Torch thread.
- `turbostat` gate before and after every experiment (`*/xung_truoc.log`, `*/xung_sau.log`;
  "xung" = clock): every busy-MHz sample within ±1% of target and at least 95% busy.
  All 10 checks of the five full runs passed (every sample at 3575 MHz, 100% busy).

## Preregistration

- Plan: `sponge-sim/prereg/PREREG_AMD_REPLICATION_20261124.md`.
  Deviations: `sponge-sim/prereg/DEVIATIONS_AMD_20261124.md`.
- Tags: `prereg-amd-replication-20261124` (9db1369), `-r1` (0963be0), `-r2` (e979b63).
  All full runs used e979b63 (`*/prereg_commit.txt`). The supervisor log
  (`full-01/supervisor.log`) shows the first full run starting at 04:41 UTC, after the
  last tag commit at 04:32 UTC.

## Layout

| Folder | Experiment |
|---|---|
| `full-01/e1` | E1 dose response (injected candidate count N) |
| `full-01/e1nc1l` | E1 one-class grid |
| `full-01/e9` | E9 injection into the full pipeline (part A) |
| `full-01/e10` | E10 reference attacks |
| `full-01/e12` | E12 patch re-measurement with the per-block drift gate |
| `full-01/analysis` | post-run analyses and the post hoc analyses used by the manuscript |
| `smoke_runs` | smoke runs, kept as they were: `smoke` (exit 127, runner path bug), `smoke-02` (exit 1, missing packages), `smoke-03` (exit 0). Smoke runs were not used for the results. |

Each experiment folder has `environment.txt` (package versions), `prereg_commit.txt`,
`run.log`, `run/manifest.json` (configuration, file hashes, CPU and lock state) and
`run/raw_P1_cpu2.jsonl` (one JSON record per measurement), plus the summaries.

`full-01/e12/run/raw_P1_cpu2.jsonl` is stored compressed as `raw_P1_cpu2.jsonl.gz`
(`gzip -n -9`) because GitHub rejects files above 100 MB (the file is 122 MB).
`gzip -dk full-01/e12/run/raw_P1_cpu2.jsonl.gz` restores the original byte for byte.
Decompress it before running `sponge-sim/studies/figures/make_figs_amd.py`,
`sponge-sim/studies/amd_replication/posthoc_amd.py` or the E12 analyzer, which read the
`.jsonl` file. The decompressed file is listed in `.gitignore`.

## Checksums

The SHA-256 lists were written on the measurement machine before transfer.

- `full01.remote.sha256`: raw run files (paths relative to this folder).
- `full01_derived.remote.sha256`: summaries and analyses (paths relative to this folder).
- `full01_analysis.remote.sha256`: an earlier listing of the analysis outputs (paths relative to `full-01`).

```bash
cd sponge-sim/results/amd_20261124
gzip -dk full-01/e12/run/raw_P1_cpu2.jsonl.gz
sha256sum -c full01.remote.sha256 full01_derived.remote.sha256
(cd full-01 && sha256sum -c ../full01_analysis.remote.sha256)
```

## Rebuilding the manuscript numbers

`paper_en/tables_q3/make_tables_en.py` reads the summaries in `full-01` and the Linux A/A
summaries in `../aa_linux_20261124`. `paper_en/tables_q3/check_numbers_en.py` compares a
fresh build with the saved tables and the source registry `numbers_en.json`.
The AMD figures are drawn by `sponge-sim/studies/figures/make_figs_amd.py`.
