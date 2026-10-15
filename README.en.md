# vllm-ascend-skills

[中文](README.md) | English

A collection of **17 coding-agent skills** for vLLM, vllm-ascend and Ascend NPU development, covering serving, correctness validation, debugging, Triton operator development, benchmarking, profiling analysis and multistream optimization.

Each package describes its scope and workflow in `SKILL.md`, with supporting references, acceptance contracts or reusable scripts to help an agent complete tasks with traceable evidence.

## Quick start

```bash
git clone https://github.com/pisceskkk/vllm-ascend-skills.git
cd vllm-ascend-skills
```

Choose a skill from the catalog below and ask your coding agent to read `skills/<name>/SKILL.md`, followed by the references needed for the task. Supply the target source paths and revisions, model, devices, runtime environment and acceptance criteria.

For clients that discover skills under a project's `.agents/skills/` directory, run the following from this repository root on Linux/macOS. Replace `project_dir` with your project's absolute path. If an entry already exists, `ln -s` reports an error; inspect it before resolving the conflict.

```bash
skill_repo="$(pwd)"
project_dir="/absolute/path/to/your/project"
mkdir -p "$project_dir/.agents/skills"
for skill_dir in "$skill_repo"/skills/*; do
  ln -s "$skill_dir" "$project_dir/.agents/skills/$(basename "$skill_dir")"
done
```

You can also use your client's supported skill-directory configuration or explicit file references. Discovery depends on the client and its starting directory; verify which skills it actually loads. Keep the repository layout intact because the Triton stage skills use relative links to sibling packages.

## Skill catalog

The `vllm-ascend-` prefix identifies workflows tied to vLLM Ascend serving or its codebase. The `ascend-` prefix identifies methods applicable to broader Ascend operator and analysis tasks.

| Skill | Purpose |
|---|---|
| [vllm-ascend-serving](skills/vllm-ascend-serving/SKILL.md) | Source pairing, device selection, launch, health checks and cleanup for colocated serving |
| [vllm-ascend-pd-serving](skills/vllm-ascend-pd-serving/SKILL.md) | Prefill/decode roles, connectors, startup order and KV transfer validation |
| [vllm-ascend-change-validation](skills/vllm-ascend-change-validation/SKILL.md) | Map code changes to correctness, build and performance evidence |
| [vllm-ascend-correctness-validation](skills/vllm-ascend-correctness-validation/SKILL.md) | Deterministic correctness comparisons across revisions, execution modes and APIs |
| [vllm-ascend-graph-debug](skills/vllm-ascend-graph-debug/SKILL.md) | Localize graph capture, replay and eager/graph divergence |
| [vllm-ascend-distributed-debug](skills/vllm-ascend-distributed-debug/SKILL.md) | Diagnose startup, collectives, endpoints and hangs using topology and per-rank evidence |
| [ascend-operator-debug](skills/ascend-operator-debug/SKILL.md) | Reduce model symptoms to one operator and check dtype, shape, layout and execution modes |
| [ascend-triton-workflow](skills/ascend-triton-workflow/SKILL.md) | Coordinate Triton operator development, correctness validation and optimization |
| [ascend-triton-operator-development](skills/ascend-triton-operator-development/SKILL.md) | Develop the first correct kernel from a PyTorch reference or GPU Triton implementation |
| [ascend-triton-kernel-validation](skills/ascend-triton-kernel-validation/SKILL.md) | Validate a declared correctness matrix and check execution and fallback behavior |
| [ascend-triton-kernel-optimization](skills/ascend-triton-kernel-optimization/SKILL.md) | Optimize a validated kernel using per-shape measurements and profiler evidence |
| [vllm-ascend-benchmark](skills/vllm-ascend-benchmark/SKILL.md) | Measure one serving code state with warmup, repeated runs and normalized metrics |
| [vllm-ascend-performance-regression](skills/vllm-ascend-performance-regression/SKILL.md) | Compare baseline and candidate serving performance with alternating runs |
| [vllm-ascend-profiling-collection](skills/vllm-ascend-profiling-collection/SKILL.md) | Collect a verified torch-profiler workload window with complete rank outputs |
| [ascend-profiling-analysis](skills/ascend-profiling-analysis/SKILL.md) | Analyze ranks, steps, layers, blocks, operators and cross-rank behavior |
| [vllm-ascend-memory-profiling](skills/vllm-ascend-memory-profiling/SKILL.md) | Attribute HBM use to weights, KV cache, HCCL, activations and runtime components |
| [ascend-model-multistream-overlap-skill](skills/ascend-model-multistream-overlap-skill/SKILL.md) | Design multistream overlap using source mapping, resource-aware DAGs and paired validation |

## Usage examples

Once your client has loaded the relevant skill, describe a task as follows. If skill discovery is unavailable, provide the `SKILL.md` path explicitly.

- **Change validation**: Use `vllm-ascend-change-validation` to inspect the given baseline/candidate diff, plan and execute validation for an attention-path change, and report passed checks and coverage gaps.
- **Performance regression**: Use `vllm-ascend-performance-regression` to alternate two revisions with the same model, devices, serving arguments and request set, then report throughput, latency and measurement variation.
- **Profiling analysis**: Use `ascend-profiling-analysis` to analyze the specified profiler output directory and report hotspots by rank, step and layer with evidence paths.
- **Triton operator**: Use `ascend-triton-workflow` to port the supplied PyTorch reference to Ascend Triton, validate correctness over a shape/dtype matrix, and then optimize performance.

## Triton operator workflow

```text
ascend-triton-workflow
  -> ascend-triton-operator-development
  -> ascend-triton-kernel-validation
  -> ascend-triton-kernel-optimization
```

The [Ascend Triton operator playbook](skills/ascend-triton-workflow/references/ascend-triton-operator-playbook.md) describes stage routing, transitions and linked evidence. Development establishes semantics and produces a candidate; validation checks execution and the correctness matrix; optimization measures and iterates on a validated candidate. Each stage skill defines its detailed acceptance contract.

## Environment and dependencies

- Reading skills and references requires a Markdown-capable tool. Each reusable script defines its own inputs and dependencies.
- Python 3.10+ is recommended for local tests. The profiling tests use `pytest` and `PyYAML`.
- NPU inference, Triton compilation, device timing and collection require a target Ascend environment with compatible vLLM, vllm-ascend, PyTorch, `torch_npu`, CANN and profiler versions. Triton tasks also require a suitable `triton-ascend` installation.
- Install [AISBench](https://github.com/AISBench/benchmark) and [aisbench_auto_tools](https://github.com/rayn-zzz/aisbench_auto_tools_prefix) separately when needed, and supply their actual paths to the relevant workflow.

This repository provides domain workflows and reusable tools. The target project supplies machine provisioning, remote execution, source synchronization, model weights and the serving runtime. Record source revisions, runtime arguments and artifact paths for reproducibility and comparison.

## Repository layout

```text
vllm-ascend-skills/
├── README.md
├── README.en.md
├── LICENSE
├── skills/<name>/
│   ├── SKILL.md
│   ├── agents/          # Optional client metadata
│   ├── references/      # Methods and acceptance contracts
│   ├── scripts/         # Reusable tools, where provided
│   ├── assets/          # Templates and examples, where provided
│   └── tests/           # Portable tests, where provided
├── lib/run_manifest.py
└── schemas/run-manifest-v1.schema.json
```

[Run Manifest v1](schemas/run-manifest-v1.schema.json) and its [helper library](lib/run_manifest.py) provide an optional run-record contract. The helper uses only the Python standard library.

The domain workflows were extracted from `vllm-ascend-workspace/.agents/skills/`. In that workspace, `.agents/skills/<name>` uses relative symlinks to this repository. Domain instructions and reusable implementations are maintained here; the workspace manages machines and sessions.

## Local validation

Run from the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pytest PyYAML
python3 -m unittest discover -s skills/ascend-model-multistream-overlap-skill/tests
python3 -m pytest skills/ascend-profiling-analysis/tests -q
```

These two suites use synthetic inputs to cover multistream tools and profiling analysis. They require no NPU and do not run model inference. Hardware-dependent workflows still need validation in a matching Ascend environment.

## Maintenance and contributions

When changing a skill, review its `SKILL.md`, references, scripts, templates and related tests together. Update documentation when commands or paths change, and keep both READMEs aligned in content and examples. Include the skill name, code revision, environment, reproduction steps and relevant logs when reporting an issue.

## License

This repository is licensed under the [MIT License](LICENSE).
