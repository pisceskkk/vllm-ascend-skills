# vLLM Ascend skill references

A standalone collection of 17 Skill packages for vLLM and vllm-ascend development, validation, debugging and performance analysis. These packages preserve domain workflows and reusable analysis code. They do not provide machine provisioning, source synchronization, session orchestration or a serving runtime.

## Layout

- `skills/<name>/SKILL.md`: activation description and core workflow.
- `skills/<name>/references/`: domain contracts and methods selected from the source packages.
- `skills/<name>/scripts/`: reusable code that does not import the workspace control layer.
- `lib/run_manifest.py` and `schemas/run-manifest-v1.schema.json`: optional Run Manifest v1 contract, using only the Python standard library.

For Codex, install or point skill discovery at individual `skills/<name>` directories. The scripts are reference implementations; each file's input contract and external runtime needs still apply. NPU execution requires an Ascend environment with the relevant vLLM, vllm-ascend, torch_npu, CANN and profiler versions.

AISBench and `aisbench_auto_tools` are external tools. Obtain [AISBench](https://github.com/AISBench/benchmark) and [aisbench_auto_tools](https://github.com/rayn-zzz/aisbench_auto_tools_prefix) separately and supply their paths from the target environment; neither is vendored or a Git submodule here.

## Scope

The repository carries the two serving Skills, change and correctness validation, graph/distributed/operator debugging, four Triton Skills, Benchmark and performance regression, profiling collection and analysis, HBM attribution, and multistream overlap. It contains domain reference material and does not assume the original workspace's machine inventory or remote execution state.
