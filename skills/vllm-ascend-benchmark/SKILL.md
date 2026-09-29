---
name: vllm-ascend-benchmark
description: Measure one vLLM Ascend online-serving code state with warmup, repeated runs and normalized metrics.
---

# Vllm Ascend Benchmark

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Fix model, topology, workload, concurrency, request rate and serving arguments.
2. Start one service, warm it, then run repeated measured rounds against that same service.
3. Exclude warmup from aggregated throughput and latency statistics; retain raw outputs.
4. Record service failure and cleanup separately from workload failure.

AISBench and `aisbench_auto_tools` are external tools. Supply their installation or source location from the target environment.

Read [core logic](references/core-logic.md) when planning or reviewing the implementation.
