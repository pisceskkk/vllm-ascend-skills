# Correctness validation acceptance

## Reproducibility

- [ ] Baseline and candidate use the same case document.
- [ ] Workspace snapshots, environment, model, weights, tokenizer, topology, and feature flags are recorded.
- [ ] Exact-comparison cases use `temperature=0` and an explicit seed.
- [ ] Commands or equivalent executor configurations are recorded.

## Execution

- [ ] Code parity was established immediately before each remote execution.
- [ ] Offline or online executor produced a normalized result file.
- [ ] Offline execution and its Python subprocesses resolve the materialized packages rather than the outer `vllm/` repository namespace.
- [ ] Service health was confirmed before online cases.
- [ ] Repeated outputs are stable or the case is classified flaky.
- [ ] Infrastructure and unsupported failures are not counted as product regressions.

## Comparison

- [ ] Every planned case has baseline and candidate evidence.
- [ ] Token or text comparison is used where exactness is meaningful.
- [ ] Numeric tolerances are explicit and justified.
- [ ] Task metric direction and regression thresholds are explicit.
- [ ] Eager/graph divergence routes to graph debug.

## Delivery

- [ ] `manifest.json`, `cases.json`, `comparison.json`, `report.md`, raw outputs, and `reproduction.sh` exist.
- [ ] Run Manifest v1 validates and links every delivered artifact.
- [ ] The report lists unsupported and untested combinations.
- [ ] A passed run contains only exact or within-tolerance cases.

## One-click AISBench accuracy

- [ ] Service startup, readiness, warmup, measured rounds, cleanup, and parity are orchestrated by the managed wrappers.
- [ ] Accuracy concurrency is at least 16 unless low concurrency was explicitly acknowledged.
- [ ] Template provenance and the effective output length, temperature, top-p, seed, concurrency, and prompt count are frozen.
- [ ] The warmup is separate from all measured work directories.
- [ ] All measured summaries normalize successfully and aggregate across the requested run count.
- [ ] Raw AISBench outputs are pulled with SHA-256 verification; failure paths make a best-effort pull.
- [ ] Run Manifest v1 records resolved config, artifact manifest, and summary.
