# vllm-ascend-skills

中文 | [English](README.en.md)

面向 vLLM、vllm-ascend 与 Ascend NPU 开发的 **17 个 AI 编程助手技能包**，覆盖服务部署、变更验证、故障定位、Triton 算子开发和性能分析。

将技能加载到编程助手后，可以让它按领域流程完成任务，并依据明确的验收要求整理结果。每个技能以 `SKILL.md` 为入口，配有参考资料；部分技能还提供分析脚本、模板和本地测试。

## 快速开始

### 获取技能

```bash
git clone https://github.com/pisceskkk/vllm-ascend-skills.git
cd vllm-ascend-skills
```

让编程助手读取所需的 `skills/<name>/SKILL.md` 即可开始使用，具体选择见下方[技能目录](#技能目录)。保留完整仓库目录结构，Triton 技能之间使用了相对路径引用。

### 接入项目

如果客户端支持从 `.agents/skills/` 发现项目技能，在 Linux/macOS 上从本仓库根目录执行以下命令，将 `project_dir` 替换为目标项目的绝对路径：

```bash
skill_repo="$(pwd)"
project_dir="/absolute/path/to/your/project"
mkdir -p "$project_dir/.agents/skills"
for skill_dir in "$skill_repo"/skills/*; do
  ln -s "$skill_dir" "$project_dir/.agents/skills/$(basename "$skill_dir")"
done
```

已有同名条目时请先检查；此命令不会覆盖它们。其他客户端可使用其技能目录配置或直接引用 `SKILL.md`，加载后确认所需技能已被识别。

## 如何使用

向助手提供技能名称或文件路径，以及任务涉及的源码版本、输入数据和目标环境。例如，验证一次 attention 路径变更：

> 读取 `skills/vllm-ascend-change-validation/SKILL.md`。目标仓库为 `/path/to/vllm-ascend`，比较 `<baseline-ref>` 与 `<candidate-ref>` 的 attention 路径变更。使用 `/path/to/model` 和指定的 Ascend 设备，确定并执行必要的正确性、构建和性能检查，输出验证结果、证据路径与覆盖缺口。

将示例中的路径、版本和设备替换为实际配置。服务与设备操作由目标项目的执行工具完成；各技能的 `SKILL.md` 说明所需输入和验收要求。

## 技能目录

`vllm-ascend-` 技能面向 vLLM Ascend 服务或代码库；`ascend-` 技能覆盖通用 Ascend 算子开发与分析。

### 服务与分布式部署

| Skill | 用途 |
|---|---|
| [vllm-ascend-serving](skills/vllm-ascend-serving/SKILL.md) | 共置服务的版本配对、设备选择、启动、健康检查与清理 |
| [vllm-ascend-pd-serving](skills/vllm-ascend-pd-serving/SKILL.md) | Prefill/Decode 分离部署、连接器配置与 KV 传输验证 |
| [vllm-ascend-distributed-debug](skills/vllm-ascend-distributed-debug/SKILL.md) | 基于拓扑与逐 rank 证据诊断启动、通信与卡死问题 |

### 验证与故障定位

| Skill | 用途 |
|---|---|
| [vllm-ascend-change-validation](skills/vllm-ascend-change-validation/SKILL.md) | 根据代码变更确定正确性、构建与性能验证范围 |
| [vllm-ascend-correctness-validation](skills/vllm-ascend-correctness-validation/SKILL.md) | 跨代码版本、执行模式和 API 路径的确定性正确性比较 |
| [vllm-ascend-graph-debug](skills/vllm-ascend-graph-debug/SKILL.md) | 定位图捕获、重放和 eager/graph 结果分歧 |
| [ascend-operator-debug](skills/ascend-operator-debug/SKILL.md) | 将模型异常缩小到单算子，检查 dtype、shape、layout 和执行模式 |

### Triton 算子开发

| Skill | 用途 |
|---|---|
| [ascend-triton-workflow](skills/ascend-triton-workflow/SKILL.md) | 串联 Triton 算子开发、正确性验证与性能优化 |
| [ascend-triton-operator-development](skills/ascend-triton-operator-development/SKILL.md) | 从 PyTorch 参考或 GPU Triton 实现开发首个正确版本 |
| [ascend-triton-kernel-validation](skills/ascend-triton-kernel-validation/SKILL.md) | 按显式用例矩阵验证精度，并检查执行与 fallback |
| [ascend-triton-kernel-optimization](skills/ascend-triton-kernel-optimization/SKILL.md) | 在正确性通过后，结合逐 shape 测量与 profiler 优化 |

跨阶段任务从 `ascend-triton-workflow` 开始，按“开发 → 正确性验证 → 性能优化”推进。阶段衔接与验收要求见 [Triton 算子 Playbook](skills/ascend-triton-workflow/references/ascend-triton-operator-playbook.md)。

### 性能评测与分析

| Skill | 用途 |
|---|---|
| [vllm-ascend-benchmark](skills/vllm-ascend-benchmark/SKILL.md) | 对单个代码状态进行预热、重复测量与指标归一化 |
| [vllm-ascend-performance-regression](skills/vllm-ascend-performance-regression/SKILL.md) | 以交替运行方式比较 baseline 与 candidate 的服务性能 |
| [vllm-ascend-profiling-collection](skills/vllm-ascend-profiling-collection/SKILL.md) | 采集指定负载窗口的 torch-profiler 数据并检查 rank 完整性 |
| [ascend-profiling-analysis](skills/ascend-profiling-analysis/SKILL.md) | 分析 rank、step、layer、block、算子与跨 rank 行为 |
| [vllm-ascend-memory-profiling](skills/vllm-ascend-memory-profiling/SKILL.md) | 将 HBM 占用归因到权重、KV cache、HCCL、激活与运行时 |
| [ascend-model-multistream-overlap-skill](skills/ascend-model-multistream-overlap-skill/SKILL.md) | 基于源码映射、资源约束 DAG 和配对实验设计多流重叠 |

## 环境要求

按任务准备运行环境：

- **本地分析与测试**：建议 Python 3.10+。下方测试使用 `pytest` 和 `PyYAML`，以合成输入运行，无需 NPU。
- **NPU 推理与采集**：需要 Ascend 设备及相互兼容的 vLLM、vllm-ascend、PyTorch、`torch_npu`、CANN 和相应 profiler。Triton 任务还需要 `triton-ascend`。
- **评测工具**：需要时单独安装 [AISBench](https://github.com/AISBench/benchmark) 和 [aisbench_auto_tools](https://github.com/rayn-zzz/aisbench_auto_tools_prefix)，并提供实际路径。

具体依赖与输入格式以所用技能和脚本为准，模型权重与运行环境由使用方准备。

## 开发与贡献

欢迎通过 [Issues](https://github.com/pisceskkk/vllm-ascend-skills/issues) 报告问题或提交 Pull Request。报告问题时请附上技能名称、代码版本、运行环境和复现步骤。

修改技能时同步检查 `SKILL.md`、引用资料、脚本及相关测试，并保持中英文 README 一致。需要记录运行状态与产物时，可参考 [Run Manifest schema](schemas/run-manifest-v1.schema.json) 和仅依赖 Python 标准库的[辅助库](lib/run_manifest.py)。

在仓库根目录运行本地测试：

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pytest PyYAML
python3 -m unittest discover -s skills/ascend-model-multistream-overlap-skill/tests
python3 -m pytest skills/ascend-profiling-analysis/tests -q
```

测试覆盖多流工具与 Profiling 分析逻辑。涉及 NPU 推理、编译和设备性能的改动，还需在匹配的 Ascend 环境验证。

## 许可证

[MIT License](LICENSE)
