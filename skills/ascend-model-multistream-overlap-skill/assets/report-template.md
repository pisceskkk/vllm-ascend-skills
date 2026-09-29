# Model multistream overlap experiment

## Outcome and scope

Record keep/revise/reject/unresolved, target cases, measured benefit and limits.

## Reproduction

Record baseline/candidate code and dirty diff hashes, code-map snapshots, model/input/config identity, hardware/runtime, topology, launch and analysis commands. Reference each artifact by path and SHA256.

## Workload and interaction coverage

Reference workload, feature-interaction and resource matrices. Record actual device shapes and phase/rank coverage, selected combinations, omitted combinations and reasons.

## Operator-to-code evidence

| Evidence ID | Operator instance/group | Python site and source hash | Expanded call chain | Tensor reads/writes/aliases | Runtime correlation | Mapping status |
|---|---|---|---|---|---|---|

## Baseline and candidate DAG

Include DAGs, changed edges, source mapping checks, dependency rationale, expected waits and precedence lower bound. Explain hidden preprocessing and lifecycle requirements.

## Correctness

Record comparison inputs, criteria/tolerances, repetitions, boundary cases, mismatches and infrastructure failures separately.

## Observed scheduling

| Case/rank/phase | Semantic pair | Raw file/record range | Core resources | Overlap/coverage | Launch skew | Kernel inflation | Wait/step impact |
|---|---|---|---|---|---|---|---|

Distinguish resource-sharing risk from demonstrated contention; distinguish time intersection from effective overlap. Note incomplete/truncated instances and uncertainty.

## Profiler-free performance

Reference every paired measurement, configuration fingerprint, objective/guardrail metrics, variability and regression budgets. Retain per-case results before any justified business weighting.

## Iteration decision

Record all three validation gates, unresolved evidence, next hypothesis or stop reason, final code identity and authorized delivery location.
