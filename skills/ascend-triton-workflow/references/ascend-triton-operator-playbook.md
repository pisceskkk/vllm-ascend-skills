# Ascend Triton 算子工程 Playbook

> 这是 `vllm-ascend-skills` 中 Ascend Triton Skill 组的总览，由
> `ascend-triton-workflow` 维护。阶段行为、验收规则和硬件技巧以各 Skill 的
> `SKILL.md`、`references/` 和随包提供的参考代码为准；执行工具由目标环境提供。

## 内容导航

- [目标与边界](#1-目标与边界)
- [路由规则](#2-路由规则)
- [统一状态机](#3-统一状态机)
- [阶段契约](#4-阶段契约)
- [证据与可恢复性](#5-证据与可恢复性)
- [使用顺序示例](#6-使用顺序示例)
- [来源与维护原则](#7-来源与维护原则)

## 1. 目标与边界

这组 Skill 由一个编排 Skill 和三个阶段 Skill 组成，可独立调用、组合和恢复：

| Skill | 适用场景 | 核心输出 |
|---|---|---|
| [ascend-triton-workflow](../SKILL.md) | 从需求到可发布 kernel 的端到端任务 | 父 Run Manifest、阶段链接、最终结论 |
| [ascend-triton-operator-development](../../ascend-triton-operator-development/SKILL.md) | 从 PyTorch 或 GPU Triton 语义得到第一版 Ascend Triton kernel | 任务契约、语义审计、设计草图、候选 kernel |
| [ascend-triton-kernel-validation](../../ascend-triton-kernel-validation/SKILL.md) | 判断候选是否真的由 Triton 执行并在显式矩阵上正确 | AST gate、逐 case 结果、correctness manifest |
| [ascend-triton-kernel-optimization](../../ascend-triton-kernel-optimization/SKILL.md) | 在正确性锚点上做 profiler 驱动的性能迭代 | 基线、优化轮次、keep/discard 记录、最佳候选 |

Playbook 负责组内路由、阶段衔接和共同证据要求。各阶段 Skill 负责本阶段的详细契约与
验收；本集合保留了工作区版本的领域方法和可复用代码，机器配置、代码同步、会话管理和
服务运行由使用方环境提供。维护阶段细节时，应修改对应 Skill，并检查本总览的摘要和链接。

本流程以 Vector 类 kernel 为主要适用对象。涉及 `tl.dot`、Cube/Vector 混合、
跨核通信、原子规约、数据依赖的离散访问或复杂控制流时，仍可使用编排与证据框架，
但必须扩展硬件模型和验证矩阵，不能直接套用 Vector 优化结论。

## 2. 路由规则

- 用户要求“迁移、实现、生成第一版”时，使用 `ascend-triton-operator-development`。
- 用户要求“验证、对齐精度、排除 PyTorch fallback”时，使用 `ascend-triton-kernel-validation`。
- 用户要求“profile、提速、优化到目标”时，使用 `ascend-triton-kernel-optimization`。
- 请求横跨两个以上阶段，或要求完整闭环时，先使用 `ascend-triton-workflow`，再调用阶段 Skill。
- 已经缩小为单个 `torch_npu`、ACLNN 或自定义算子故障，而非 Triton kernel 工程问题时，
  转交 [ascend-operator-debug](../../ascend-operator-debug/SKILL.md)。
- 模型级 graph/eager 分歧尚未归因到单 kernel 时，先使用
  [vllm-ascend-graph-debug](../../vllm-ascend-graph-debug/SKILL.md)。

本集合提供领域流程与证据契约；依赖 `torch`、`torch_npu`、Triton 编译、设备计时或
profiler 的执行必须在目标 Ascend 环境完成。执行工具、隔离方式、代码同步和知识查询
遵循目标项目的规则；这些运行时能力由使用方提供。

## 3. 统一状态机

```text
DISCOVER
   |
   v
DEVELOP  -- task contract + semantic audit + sketch + candidate
   |
   v
VALIDATE -- AST gate + compile/run + explicit case matrix
   |                         |
   | correctness passed      | mismatch / compile / runtime failure
   v                         v
OPTIMIZE <--------------- DEVELOP or VALIDATE diagnosis
   |
   | plan -> edit -> validate -> profile -> KEEP/DISCARD/NOISE/FAIL
   v
FINALIZE -- publish best correctness-passing candidate and evidence links
```

状态转换遵循以下硬约束：

1. 没有成功的正确性 manifest，不得开始性能比较。
2. 一轮优化只验证一个主要假设，只保留一个可归因的主要改动。
3. 候选必须得到 `KEEP`、`DISCARD`、`NOISE` 或 `FAIL`，不得覆盖唯一的 best kernel。
4. 环境、参考实现、编译、运行、数值和性能失败分别分类。
5. 同类故障重复前先查询目标项目的已验证知识；连续失败则进入诊断，不原样重试。
6. 最终产物只能指向全量正确性通过的候选；声明性能提升时还须有有效性能证据。

## 4. 阶段契约

### 4.1 开发：冻结语义，再写 kernel

开发阶段首先固定：

- 输入输出的 shape、dtype、layout、stride 和动态范围；
- in-place、alias、atomic、随机数、NaN/Inf 等副作用或边界语义；
- 参考实现与逐 dtype 容差；
- 功能用例和性能用例；
- 目标 SoC、CANN、`torch_npu`、`triton-ascend` 版本与能力快照。

然后审计每个 load/store mask、索引表达式、grid 映射、归约 identity 和累加 dtype。
第一版 kernel 以最小正确为目标：host wrapper 只负责参数整理、分配和 launch，核心计算
必须位于 `@triton.jit` 内。

详细规则见：

- [语义审计](../../ascend-triton-operator-development/references/semantic-review.md)
- [架构与代码生成](../../ascend-triton-operator-development/references/architecture-and-codegen.md)

### 4.2 验证：先排除退化，再证明正确

验证阶段的顺序固定为：

1. AST gate：确认存在 `@triton.jit` kernel、目标 `forward` 可达路径真的 launch kernel，
   且核心计算未回退到 PyTorch。
2. 编译：覆盖会触发不同 specialization 的 case。
3. 运行：逐 case 独立记录 compilation/runtime/unsupported 状态。
4. 数值：检查 shape、dtype、stride、NaN/Inf，并使用任务声明的容差。
5. 守卫：在可行时检查越界写和非预期 in-place 修改。

只有 `passed_cases == total_cases > 0` 才可生成成功的 correctness manifest。
`unsupported` 或缺失 case 是 `inconclusive`，不能伪装成通过。

详细规则见：

- [用例设计](../../ascend-triton-kernel-validation/references/case-design.md)
- [验证验收](../../ascend-triton-kernel-validation/references/acceptance.md)

### 4.3 优化：基于证据验证单一假设

优化阶段先记录可复现基线，再按以下循环工作：

```text
profile -> classify bottleneck -> one hypothesis -> one main change
        -> full validation -> repeated benchmark -> KEEP/DISCARD/NOISE/FAIL
```

性能证据必须保证：

- baseline 和 candidate 使用相同环境、case、计时口径和同步方式；
- 排除首次编译和 warmup；
- 分 case 保留重复样本和稳健统计量，而非只给一个平均值；
- 同时观察 wrapper latency 与 device kernel time；
- 正确性失败的候选不进入性能排名；
- 提升小于噪声阈值时标记 `NOISE`，不强行 `KEEP`。

详细的 Ascend 优化知识位于：

- [Profiling 决策树](../../ascend-triton-kernel-optimization/references/profiling-decision-tree.md)
- [Ascend 优化技巧](../../ascend-triton-kernel-optimization/references/ascend-techniques.md)

其中包括 UB live-set 预算、grid 与物理核映射、MTE/Vector/Scalar 流水、dtype、mask、
地址计算、multibuffer、尾块和小 shape 策略。所有核数、存储容量、编译选项和 API 支持
都视为环境事实：先探测并记录，缺失时标记 `unknown`，不得把单一 910B 环境的经验写成
跨芯片常量。

## 5. 证据与可恢复性

四个 Skill 的证据契约使用 Run Manifest v1。本集合提供可选的标准库辅助实现
[lib/run_manifest.py](../../../lib/run_manifest.py) 和
[schema](../../../schemas/run-manifest-v1.schema.json)，供目标环境的执行工具集成：

| 阶段 | Run Manifest 类型 | 关键链接 |
|---|---|---|
| workflow | `change-validation` | development、correctness、performance 子 manifest |
| development | `debug` | task contract、语义报告、草图、候选 kernel、correctness manifest |
| validation | `correctness` | kernel hash、静态检查、case 矩阵、结果汇总 |
| optimization | `performance` | 起始 correctness、baseline、每轮 candidate correctness 和测量 |

运行状态写入目标项目明确指定、未跟踪的产物目录；使用原工作区执行工具时为
`.vaws-local/`。集成执行脚本时，进度写 `stderr`，最终机器可读 JSON 写 `stdout`。
manifest 和 artifact 记录绝对路径、hash、环境与父子关系，使流程可以在中断后恢复，
也能区分“未运行”“证据缺失”“已失败”和“已通过”。

## 6. 使用顺序示例

以从 GPU Triton 迁移并优化一个算子为例，使用目标环境的工具完成以下步骤：

1. 由 workflow 固定需求和必需阶段，建立父 manifest；配置与链接要求见
   [编排行为契约](behavior.md)。
2. 由 development 完成任务契约、语义审计、设计草图和候选 kernel，记录 `debug` 证据。
3. 由 validation 先运行静态 gate，再在目标 Ascend 环境执行完整 case 矩阵，记录
   `correctness` 证据。随包提供的静态 gate 见
   [validate_triton_impl.py](../../ascend-triton-kernel-validation/scripts/validate_triton_impl.py)。
4. 全量正确性通过后，由 optimization 建立 NPU 基线，逐轮修改、重新验证、测量并作出
   `KEEP` / `DISCARD` / `NOISE` / `FAIL` 决策，记录 `performance` 证据。
5. 将终态子 manifest 链接回 workflow，按[编排验收](acceptance.md)交付候选和报告。

本集合的执行入口以各包实际提供的 `scripts/` 为准。阶段契约中的 `plan`、`record`、
`analyze`、`link` 和 `finalize` 表示执行工具需要实现的操作；原工作区的控制脚本及
`command-recipes.md` 由原工作区维护。

## 7. 来源与维护原则

本 Skill 组综合了以下材料的互补部分：

- [`simple-vector-triton-gpu-to-npu`](https://gitcode.com/Ascend/agent-skills/blob/master/community/Op/simple-vector-triton-gpu-to-npu/SKILL.md)：语义审计、最小迁移、mask 职责与错误分流。
- [`vector-triton-ascend-ops-optimizer`](https://gitcode.com/Ascend/agent-skills/blob/master/community/Op/vector-triton-ascend-ops-optimizer/SKILL.md)：UB、分核、流水、访存与 dtype 优化假设。
- [`AscendOpGenAgent`](https://github.com/Just-it/AscendOpGenAgent)：阶段编排、AST fallback gate、全 shape 验证和 keep/discard 状态机。

材料快照日期为 2026-08-03。外部项目中的固定阈值、设备常量和命令没有直接提升为本仓库
的永久事实；快变能力应进入目标项目的知识库，经目标环境验证后再使用。修改任一 Skill
时，应同步检查其 `SKILL.md`、`references/` 以及实际提供的 `scripts/`、`tests/` 和
`agents/`。本总览随 `ascend-triton-workflow` 管理，共同规则应与三个阶段的契约保持一致。
