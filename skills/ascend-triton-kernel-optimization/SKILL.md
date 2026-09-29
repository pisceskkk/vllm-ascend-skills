---
name: ascend-triton-kernel-optimization
description: Optimize a correctness-passed Ascend Triton kernel with per-shape measurements and profiler evidence.
---

# Ascend Triton Kernel Optimization

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Begin from a passed validation result for the exact kernel hash.
2. Identify the active MTE, Vector, Scalar or occupancy bottleneck and state one hypothesis per round.
3. Revalidate each candidate across the full case matrix before comparing performance.
4. Keep or discard based on repeated per-shape measurements, noise and regressions.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [ascend-techniques.md](references/ascend-techniques.md)
- [behavior.md](references/behavior.md)
- [profiling-decision-tree.md](references/profiling-decision-tree.md)

Treat missing model capability, compatibility or validation facts as unknown. Use verified knowledge from the target project when available.
