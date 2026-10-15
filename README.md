# vllm-ascend-skills

中文 | [English](README.en.md)

面向 vLLM、vllm-ascend 与 Ascend NPU 开发的 **17 个 AI 编程助手技能包**，覆盖服务部署、正确性验证、故障定位、Triton 算子开发、性能评测、Profiling 分析和多流优化。

每个技能包以 `SKILL.md` 描述适用场景与执行流程，并提供相应的参考资料、验收要求或可复用脚本，帮助编程助手将任务推进到有证据支撑的结论。

## 快速开始

```bash
git clone https://github.com/pisceskkk/vllm-ascend-skills.git
cd vllm-ascend-skills
```

从下方目录选择技能，让编程助手读取对应的 `skills/<name>/SKILL.md`，再按需读取其中引用的资料。使用前提供目标代码路径与版本、模型、设备和运行环境，以及本次任务的验收目标。

如果客户端支持从项目的 `.agents/skills/` 发现技能，可以在 Linux/macOS 上从本仓库根目录执行以下命令。将 `project_dir` 替换为目标项目的绝对路径；已有同名条目时，`ln -s` 会报错，请检查后处理。

```bash
skill_repo="$(pwd)"
project_dir="/absolute/path/to/your/project"
mkdir -p "$project_dir/.agents/skills"
for skill_dir in "$skill_repo"/skills/*; do
  ln -s "$skill_dir" "$project_dir/.agents/skills/$(basename "$skill_dir")"
done
```

也可以通过客户端支持的技能目录配置或显式文件引用接入。加载方式取决于客户端及其启动目录，接入后检查实际发现的技能。建议保留整个仓库的目录结构，Triton 阶段技能之间存在相对路径引用。

## 技能目录

`vllm-ascend-` 前缀表示依赖 vLLM Ascend 服务或代码库的流程；`ascend-` 前缀表示可用于更广泛 Ascend 算子与分析任务的方法。

| Skill | 用途 |
|---|---|
| [vllm-ascend-serving](skills/vllm-ascend-serving/SKILL.md) | 共置服务的版本配对、设备选择、启动、健康检查与清理 |
| [vllm-ascend-pd-serving](skills/vllm-ascend-pd-serving/SKILL.md) | Prefill/Decode 分离部署、连接器配置与 KV 传输验证 |
| [vllm-ascend-change-validation](skills/vllm-ascend-change-validation/SKILL.md) | 根据代码变更确定正确性、构建与性能验证范围 |
| [vllm-ascend-correctness-validation](skills/vllm-ascend-correctness-validation/SKILL.md) | 跨代码版本、执行模式和 API 路径的确定性正确性比较 |
| [vllm-ascend-graph-debug](skills/vllm-ascend-graph-debug/SKILL.md) | 定位图捕获、重放和 eager/graph 结果分歧 |
| [vllm-ascend-distributed-debug](skills/vllm-ascend-distributed-debug/SKILL.md) | 基于拓扑与逐 rank 证据诊断启动、通信与卡死问题 |
| [ascend-operator-debug](skills/ascend-operator-debug/SKILL.md) | 将模型异常缩小到单算子，检查 dtype、shape、layout 和执行模式 |
| [ascend-triton-workflow](skills/ascend-triton-workflow/SKILL.md) | 串联 Triton 算子开发、正确性验证与性能优化 |
| [ascend-triton-operator-development](skills/ascend-triton-operator-development/SKILL.md) | 从 PyTorch 参考或 GPU Triton 实现开发首个正确版本 |
| [ascend-triton-kernel-validation](skills/ascend-triton-kernel-validation/SKILL.md) | 按显式用例矩阵验证精度，并检查执行与 fallback |
| [ascend-triton-kernel-optimization](skills/ascend-triton-kernel-optimization/SKILL.md) | 在正确性通过后，结合逐 shape 测量与 profiler 优化 |
| [vllm-ascend-benchmark](skills/vllm-ascend-benchmark/SKILL.md) | 对单个代码状态进行预热、重复测量与指标归一化 |
| [vllm-ascend-performance-regression](skills/vllm-ascend-performance-regression/SKILL.md) | 以交替运行方式比较 baseline 与 candidate 的服务性能 |
| [vllm-ascend-profiling-collection](skills/vllm-ascend-profiling-collection/SKILL.md) | 采集指定负载窗口的 torch-profiler 数据并检查 rank 完整性 |
| [ascend-profiling-analysis](skills/ascend-profiling-analysis/SKILL.md) | 分析 rank、step、layer、block、算子与跨 rank 行为 |
| [vllm-ascend-memory-profiling](skills/vllm-ascend-memory-profiling/SKILL.md) | 将 HBM 占用归因到权重、KV cache、HCCL、激活与运行时 |
| [ascend-model-multistream-overlap-skill](skills/ascend-model-multistream-overlap-skill/SKILL.md) | 基于源码映射、资源约束 DAG 和配对实验设计多流重叠 |

## 使用示例

在客户端已经加载相应技能后，可以按以下方式描述任务；未启用技能发现时，直接给出 `SKILL.md` 路径。

- **变更验证**：使用 `vllm-ascend-change-validation`，检查给定 baseline 与 candidate 的差异，为 attention 路径变更制定并执行验证，列出通过项与覆盖缺口。
- **性能回归**：使用 `vllm-ascend-performance-regression`，在相同模型、设备、服务参数和请求集下交替运行两个版本，报告吞吐、延迟和测量波动。
- **Profiling 分析**：使用 `ascend-profiling-analysis`，分析指定 profiler 输出目录，给出逐 rank、step 和 layer 的热点及证据路径。
- **Triton 算子**：使用 `ascend-triton-workflow`，将给定 PyTorch 参考实现迁移到 Ascend Triton，先按 shape/dtype 矩阵验证正确性，再进行性能优化。

## Triton 算子流程

```text
ascend-triton-workflow
  -> ascend-triton-operator-development
  -> ascend-triton-kernel-validation
  -> ascend-triton-kernel-optimization
```

[Ascend Triton 算子 Playbook](skills/ascend-triton-workflow/references/ascend-triton-operator-playbook.md) 说明阶段路由、状态转换和证据衔接。开发阶段确定语义并形成候选实现，验证阶段检查执行路径和正确性矩阵，优化阶段基于通过验证的候选开展测量与迭代。详细验收以各阶段技能的契约为准。

## 环境与依赖

- 阅读技能与参考资料只需支持 Markdown 的工具；可复用脚本的输入和依赖以对应文件为准。
- 本地测试建议使用 Python 3.10+；Profiling 测试使用 `pytest` 和 `PyYAML`。
- NPU 推理、Triton 编译、设备计时和采集任务需要目标 Ascend 环境，以及相互兼容的 vLLM、vllm-ascend、PyTorch、`torch_npu`、CANN 和相应 profiler；Triton 任务还需要适配的 `triton-ascend`。
- [AISBench](https://github.com/AISBench/benchmark) 与 [aisbench_auto_tools](https://github.com/rayn-zzz/aisbench_auto_tools_prefix) 按需单独安装，并向相关流程提供实际路径。

本仓库提供领域流程和可复用工具。机器配置、远程执行、源码同步、模型权重与服务运行由目标项目提供。执行时记录源码版本、运行参数和产物路径，以便复现与比较。

## 仓库结构

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

[Run Manifest v1](schemas/run-manifest-v1.schema.json) 与 [辅助库](lib/run_manifest.py) 提供可选的运行记录契约，辅助库仅使用 Python 标准库。

这些技能的领域流程提取自 `vllm-ascend-workspace/.agents/skills/`。在该工作区中，`.agents/skills/<name>` 通过相对符号链接指向本仓库；领域说明和可复用实现维护在这里，机器与会话管理由工作区负责。

## 本地验证

在仓库根目录运行：

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pytest PyYAML
python3 -m unittest discover -s skills/ascend-model-multistream-overlap-skill/tests
python3 -m pytest skills/ascend-profiling-analysis/tests -q
```

这两组测试使用合成输入，覆盖多流分析工具与 Profiling 分析逻辑，不需要 NPU，也不执行模型推理。硬件相关流程仍需在匹配的 Ascend 环境验证。

## 维护与贡献

修改技能时同步检查 `SKILL.md`、引用资料、脚本、模板与相关测试。命令和路径发生变化时更新对应文档，并保持中英文 README 的内容与示例一致。报告问题时附上技能名称、代码版本、环境、复现步骤和相关日志。

## 许可证

本仓库采用 [MIT License](LICENSE)。
