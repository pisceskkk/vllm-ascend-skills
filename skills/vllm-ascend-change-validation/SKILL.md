---
name: vllm-ascend-change-validation
description: Map a vLLM or vllm-ascend diff to sufficient correctness, build and performance evidence and summarize coverage.
---

# Vllm Ascend Change Validation

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Collect the exact baseline/candidate diff, including relevant untracked changes.
2. Classify affected components and choose required checks using validation rules; flag unknown mappings for review.
3. Link each executed check to its plan item and Run Manifest evidence.
4. Report passed, failed, missing and untested combinations separately.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)
- [validation-rules.md](references/validation-rules.md)

Treat missing model capability, compatibility or validation facts as unknown. Use verified knowledge from the target project when available.
