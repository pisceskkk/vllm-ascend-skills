---
name: ascend-profiling-analysis
description: Analyze Ascend profiler roots into rank, step, layer, block, operator and cross-rank findings with traceable evidence.
---

# Ascend Profiling Analysis

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Normalize kernel, communication and trace records while preserving links to source rows.
2. Segment steps and layers, classify blocks, and group equivalent shapes.
3. Align ranks and attribute compute, communication and idle intervals.
4. Emit only findings with evidence IDs, limitations and links to raw rows.

## Detailed references


## Reference code

The scripts in `scripts/` contain domain analysis or validation logic. Use them with inputs that match their documented contracts; runtime-specific tools remain external.

Read [core logic](references/core-logic.md) when planning or reviewing the implementation.
