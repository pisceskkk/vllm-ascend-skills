---
name: vllm-ascend-correctness-validation
description: Design and compare deterministic vLLM Ascend correctness cases across code states, execution modes and API paths.
---

# Vllm Ascend Correctness Validation

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Define the affected case matrix: baseline/candidate, eager/graph, offline/online and task metrics as needed.
2. Fix prompts, tokenizer, model weights, seed, temperature, topology and feature flags across comparisons.
3. Normalize outputs and metrics before comparison; repeat suspected nondeterministic cases.
4. Classify the first divergence and preserve raw responses, logs and case configuration.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)

## Reference code

The scripts in `scripts/` contain domain analysis or validation logic. Use them with inputs that match their documented contracts; runtime-specific tools remain external.

AISBench and `aisbench_auto_tools` are external tools. Supply their installation or source location from the target environment.
