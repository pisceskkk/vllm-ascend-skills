---
name: vllm-ascend-performance-regression
description: Compare baseline and candidate vLLM Ascend serving performance using controlled alternating runs.
---

# Vllm Ascend Performance Regression

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Hold all non-code settings identical across baseline and candidate.
2. Alternate run order, exclude warmup and record repeated measurements.
3. Compare throughput, TTFT, TPOT, ITL or other requested metrics with variance and outlier context.
4. Declare regression only for the metric and threshold established before measurement.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)
