---
name: vllm-ascend-memory-profiling
description: Attribute Ascend HBM use during vLLM serving to weights, KV cache, HCCL, activations and runtime components.
---

# vLLM Ascend Memory Profiling

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Capture device HBM, process information, vLLM logs and msprof component data for the same run.
2. Estimate fixed overhead, weights, KV cache, HCCL and runtime with explicit evidence for each value.
3. Cross-check totals and report residual or overlapping accounting rather than silently forcing a sum.
4. State which components could not be measured and why.

## Detailed references

- [msprof_fields.md](references/msprof_fields.md)

## Reference code

The scripts in `scripts/` contain domain analysis or validation logic. Use them with inputs that match their documented contracts; runtime-specific tools remain external.

Read [core logic](references/core-logic.md) when planning or reviewing the implementation.
