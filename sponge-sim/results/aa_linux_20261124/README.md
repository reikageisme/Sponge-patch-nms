# Linux frequency-locked clean A/A calibration (24/11/2026)

Clean-image A/A calibration on the same frequency-locked AMD Ryzen 5 5500 as
`../amd_20261124`, at 320 px and 640 px. `REPORT.md` (Vietnamese) gives the results
and the reproduction checks.

- Preregistration: `sponge-sim/prereg/PREREG_AA_LINUX_20261124.md`, tag
  `prereg-aa-linux-20261124` (6de50aa). The same commit is in
  `x/sponge-aa-20261124/aa_prereg_source.bundle`.
- Raw records and summaries: `x/sponge-aa-20261124/full-01/aa_{320,640}/`.
  The smoke run is in `x/sponge-aa-20261124/smoke-01/`.
- Checksums written on the measurement machine: `x/sponge-aa-20261124/results.sha256`
  (`cd x/sponge-aa-20261124 && sha256sum -c results.sha256`).

The folder keeps the path of the measurement workspace (`x/sponge-aa-20261124`) because
`paper_en/tables_q3/make_tables_en.py` reads the summaries from there. The workspace's own
git directory, dataset copy and source snapshot are not included; the source is the tagged commit.
