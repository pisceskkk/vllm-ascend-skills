---
name: ascend-operator-debug
description: Reduce an Ascend model symptom to one operator call and validate its dtype, shape, layout and execution modes.
---

# Ascend Operator Debug

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Capture operator arguments, input metadata, layout, stream and execution mode. For an operator error in a container, retain relevant plog from `~/ascend/log/debug/` with its rank/device and time window.
2. Define a trusted reference and tolerances before running comparisons.
3. Vary one axis at a time across a declared case matrix.
4. Classify unsupported combinations, crashes and numerical mismatches; retain a regression case.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)
