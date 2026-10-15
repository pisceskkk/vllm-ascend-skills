---
name: ascend-triton-operator-development
description: Develop the first correct Ascend Triton kernel from a PyTorch reference or a GPU Triton implementation.
---

# Ascend Triton Operator Development

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Audit loads, stores, masks, indexing, reductions, atomics, aliases and side effects against the reference.
2. Design grid, tile sizes, UB live set, padding and specialization for the target SoC.
3. Keep the host wrapper limited to allocation, metadata and launch.
4. Hand the candidate and complete semantic contract to correctness validation.

## Detailed references

- [Operator playbook](../ascend-triton-workflow/references/ascend-triton-operator-playbook.md): read when this development task needs coordination with validation or optimization.
- [acceptance.md](references/acceptance.md)
- [architecture-and-codegen.md](references/architecture-and-codegen.md)
- [behavior.md](references/behavior.md)
- [semantic-review.md](references/semantic-review.md)

Treat missing model capability, compatibility or validation facts as unknown. Use verified knowledge from the target project when available.
