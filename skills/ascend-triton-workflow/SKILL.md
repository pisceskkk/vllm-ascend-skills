---
name: ascend-triton-workflow
description: Coordinate complete Ascend Triton operator development, correctness validation and optimization with linked evidence.
---

# Ascend Triton Workflow

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Freeze source, reference semantics, target SoC, software versions and case set.
2. Plan development, correctness and optimization as separate stages.
3. Require a passed correctness result for the exact candidate before optimization.
4. Link stage artifacts and report incomplete or failed coverage.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)

Treat missing model capability, compatibility or validation facts as unknown. Use verified knowledge from the target project when available.
