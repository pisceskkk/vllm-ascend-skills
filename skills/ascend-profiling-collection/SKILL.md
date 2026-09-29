---
name: ascend-profiling-collection
description: Collect one useful Ascend torch-profiler case with a verified workload window and complete rank outputs.
---

# Ascend Profiling Collection

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Configure the profiler and confirm the service is ready before opening the window.
2. Start profiling, drive a representative request wave and clean follow-up request, then stop profiling.
3. Require workload success and the expected number of rank output directories.
4. After analysis, require kernel_details.csv and trace_view.json in each expected output.

## Reference code

The scripts in `scripts/` contain domain analysis or validation logic. Use them with inputs that match their documented contracts; runtime-specific tools remain external.

Read [core logic](references/core-logic.md) when planning or reviewing the implementation.
