# vllm-ascend-skills

[中文](README.md) | English

**17 coding-agent skills** for vLLM, vllm-ascend and Ascend NPU development, covering serving, change validation, debugging, Triton operators and performance analysis.

Load a skill into your coding agent to work through a domain-specific workflow and assess results against explicit acceptance criteria. Each skill starts with `SKILL.md` and supporting references; some also include analysis scripts, templates and local tests.

## Quick start

### Get the skills

```bash
git clone https://github.com/pisceskkk/vllm-ascend-skills.git
cd vllm-ascend-skills
```

Ask your coding agent to read the relevant `skills/<name>/SKILL.md` to get started. Choose a task from the [skill catalog](#skill-catalog) below. Keep the repository layout intact: Triton skills use relative links to sibling packages.

### Add skills to a project

For clients that discover project skills under `.agents/skills/`, run the following from this repository root on Linux/macOS. Replace `project_dir` with your project's absolute path:

```bash
skill_repo="$(pwd)"
project_dir="/absolute/path/to/your/project"
mkdir -p "$project_dir/.agents/skills"
for skill_dir in "$skill_repo"/skills/*; do
  ln -s "$skill_dir" "$project_dir/.agents/skills/$(basename "$skill_dir")"
done
```

Inspect any existing entries with the same names first; this command does not overwrite them. Other clients can use their skill-directory configuration or explicit `SKILL.md` references. Confirm that the client recognizes the skills after setup.

## Usage

Give your agent a skill name or file path, along with the source revisions, input data and target environment for the task. For example, to validate an attention-path change:

> Read `skills/vllm-ascend-change-validation/SKILL.md`. In `/path/to/vllm-ascend`, compare the attention-path changes between `<baseline-ref>` and `<candidate-ref>`. Using `/path/to/model` and the specified Ascend devices, select and run the required correctness, build and performance checks. Report validation results, evidence paths and coverage gaps.

Replace the example paths, revisions and devices with your actual configuration. The target project's execution tools handle serving and device operations; each `SKILL.md` defines its required inputs and acceptance criteria.

## Skill catalog

Skills prefixed with `vllm-ascend-` target vLLM Ascend serving or its codebase. Skills prefixed with `ascend-` cover general Ascend operator development and analysis.

### Serving and distributed deployment

| Skill | Purpose |
|---|---|
| [vllm-ascend-serving](skills/vllm-ascend-serving/SKILL.md) | Source pairing, device selection, launch, health checks and cleanup for colocated serving |
| [vllm-ascend-pd-serving](skills/vllm-ascend-pd-serving/SKILL.md) | Prefill/decode roles, connectors, startup order and KV transfer validation |
| [vllm-ascend-distributed-debug](skills/vllm-ascend-distributed-debug/SKILL.md) | Diagnose startup, collectives, endpoints and hangs using topology and per-rank evidence |

### Validation and debugging

| Skill | Purpose |
|---|---|
| [vllm-ascend-change-validation](skills/vllm-ascend-change-validation/SKILL.md) | Map code changes to correctness, build and performance evidence |
| [vllm-ascend-correctness-validation](skills/vllm-ascend-correctness-validation/SKILL.md) | Deterministic correctness comparisons across revisions, execution modes and APIs |
| [vllm-ascend-graph-debug](skills/vllm-ascend-graph-debug/SKILL.md) | Localize graph capture, replay and eager/graph divergence |
| [ascend-operator-debug](skills/ascend-operator-debug/SKILL.md) | Reduce model symptoms to one operator and check dtype, shape, layout and execution modes |

### Triton operator development

| Skill | Purpose |
|---|---|
| [ascend-triton-workflow](skills/ascend-triton-workflow/SKILL.md) | Coordinate Triton operator development, correctness validation and optimization |
| [ascend-triton-operator-development](skills/ascend-triton-operator-development/SKILL.md) | Develop the first correct kernel from a PyTorch reference or GPU Triton implementation |
| [ascend-triton-kernel-validation](skills/ascend-triton-kernel-validation/SKILL.md) | Validate a declared correctness matrix and check execution and fallback behavior |
| [ascend-triton-kernel-optimization](skills/ascend-triton-kernel-optimization/SKILL.md) | Optimize a validated kernel using per-shape measurements and profiler evidence |

For tasks spanning stages, start with `ascend-triton-workflow` and follow development → correctness validation → performance optimization. See the [Triton operator playbook](skills/ascend-triton-workflow/references/ascend-triton-operator-playbook.md) for stage transitions and acceptance requirements.

### Benchmarking and performance analysis

| Skill | Purpose |
|---|---|
| [vllm-ascend-benchmark](skills/vllm-ascend-benchmark/SKILL.md) | Measure one serving code state with warmup, repeated runs and normalized metrics |
| [vllm-ascend-performance-regression](skills/vllm-ascend-performance-regression/SKILL.md) | Compare baseline and candidate serving performance with alternating runs |
| [vllm-ascend-profiling-collection](skills/vllm-ascend-profiling-collection/SKILL.md) | Collect a verified torch-profiler workload window with complete rank outputs |
| [ascend-profiling-analysis](skills/ascend-profiling-analysis/SKILL.md) | Analyze ranks, steps, layers, blocks, operators and cross-rank behavior |
| [vllm-ascend-memory-profiling](skills/vllm-ascend-memory-profiling/SKILL.md) | Attribute HBM use to weights, KV cache, HCCL, activations and runtime components |
| [ascend-model-multistream-overlap-skill](skills/ascend-model-multistream-overlap-skill/SKILL.md) | Design multistream overlap using source mapping, resource-aware DAGs and paired validation |

## Requirements

Prepare the environment for the task you plan to run:

- **Local analysis and tests**: Python 3.10+ is recommended. The tests below use `pytest` and `PyYAML` with synthetic inputs and require no NPU.
- **NPU inference and profiling**: Ascend hardware and compatible vLLM, vllm-ascend, PyTorch, `torch_npu`, CANN and profiler versions. Triton tasks also require `triton-ascend`.
- **Evaluation tools**: Install [AISBench](https://github.com/AISBench/benchmark) and [aisbench_auto_tools](https://github.com/rayn-zzz/aisbench_auto_tools_prefix) separately when needed, and supply their actual paths.

Consult the selected skill and script for exact dependencies and input formats. Supply your own model weights and runtime environment.

## Development and contributing

Report problems through [Issues](https://github.com/pisceskkk/vllm-ascend-skills/issues) or submit a pull request. Include the skill name, source revision, runtime environment and reproduction steps in issue reports.

When changing a skill, review its `SKILL.md`, references, scripts and related tests together, and keep both READMEs aligned. For recording run status and artifacts, see the [Run Manifest schema](schemas/run-manifest-v1.schema.json) and its [standard-library helper](lib/run_manifest.py).

Run local tests from the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pytest PyYAML
python3 -m unittest discover -s skills/ascend-model-multistream-overlap-skill/tests
python3 -m pytest skills/ascend-profiling-analysis/tests -q
```

These tests cover multistream tools and profiling analysis. Changes involving NPU inference, compilation or device performance also need validation in a matching Ascend environment.

## License

[MIT License](LICENSE)
