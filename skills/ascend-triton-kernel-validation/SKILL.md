---
name: ascend-triton-kernel-validation
description: Validate an Ascend Triton candidate against a trusted reference with a declared case matrix and fallback gate.
---

# Ascend Triton Kernel Validation

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Freeze candidate hash, reference, tolerances and shape/dtype/layout/stride cases.
2. Reject a missing Triton launch or reachable PyTorch computation fallback.
3. Compare shape and dtype, then NaN/Inf behavior and numerical values for every case.
4. Only an all-passed, nonempty case matrix supports a correctness claim.

## Detailed references

- [Operator playbook](../ascend-triton-workflow/references/ascend-triton-operator-playbook.md): read when handing correctness evidence to development or optimization.
- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)
- [case-design.md](references/case-design.md)

## Reference code

The scripts in `scripts/` contain domain analysis or validation logic. Use them with inputs that match their documented contracts; runtime-specific tools remain external.

Treat missing model capability, compatibility or validation facts as unknown. Use verified knowledge from the target project when available.
