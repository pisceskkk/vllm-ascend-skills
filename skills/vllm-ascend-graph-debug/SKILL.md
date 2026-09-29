---
name: vllm-ascend-graph-debug
description: Localize Ascend graph capture, replay or eager/graph divergence with controlled experiments and intermediate snapshots.
---

# Vllm Ascend Graph Debug

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Establish an eager passing baseline and a minimal graph failure.
2. Change one variable per experiment and record hypothesis, expected outcome and observation.
3. Align eager and graph intermediate snapshots to find the first divergent boundary.
4. Rerun the minimal and original case after a fix and remove instrumentation.

## Detailed references

- [acceptance.md](references/acceptance.md)

Read [core logic](references/core-logic.md) when planning or reviewing the implementation.
