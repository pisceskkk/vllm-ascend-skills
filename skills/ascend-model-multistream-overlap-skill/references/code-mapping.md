# 算子与实际源码关联

## 重排前的映射链

为每个受影响的语义操作建立：

`trace event/graph instance → runtime operator/correlation → wrapper/native 调用链 → Python 调用站点 → tensor producer/consumer → DAG 节点`。

保存代码版本、文件路径、qualified function、起止行、文件 hash 与片段 hash。站点记录输入/输出的 shape、dtype、layout、alias、读写集合、cache/collective 副作用，以及对应 workload/rank/branch。代码锚点只证明引用了哪份源代码，不能证明 kernel 身份。

## 如何核实

1. 静态展开目标调用：模块 → wrapper/quantization method → ATen/custom op → runtime kernel。检查隐含转换、同步、通信和输出处理。
2. 使用 profiler 的 scope、stack、correlation/flow、图实例或已核实的提交序列核对。优先复用现有标记；缺失时可用受控的诊断标记获取映射，记录其开销与图捕获兼容性，并在最终性能测试前移除或保持双方相同。
3. 核对输入/输出形状、dtype、tensor 数据流、层/分支/rank。相同名称和权重形状不保证是同一个投影。
4. 支持一对多（一个 Python 调用展开多个 kernel）和多对一（融合、编译/图优化）。不要为了画图强行映射为一对一。
5. 给映射标记 verified 或 hypothesis。verified 需要静态链证据和 runtime 证据；源码站点哈希检查通过不足以自动提升状态。

## 脚本与变更纪律

`verify_code_map.py snapshot` 消费计划文件，将相对路径解析到指定 source root，校验 qualified function 和行区间，保存源码及片段 SHA256。只解析 AST，不 import/执行源码。

`check` 检测文件、函数位置或片段变化；失败意味着映射需要更新，不代表代码一定错误。基线和候选分别保存快照；不要覆盖基线映射以掩盖变化。修改后审查调用展开和 tensor 契约，再为候选生成新快照。

`validate_dag.py --code-map ...` 要求每个节点的 code_sites 存在，并由 verified binding 覆盖。绑定还必须带 static_evidence 与 runtime_evidence；节点与 binding 的 operator_id 精确一致。这个结构性检查不能代替人工核对证据内容。

在部署前确认执行源与候选快照一致。再次运行、capture 或采集时，如果源码、wrapper、native 算子、编译策略或运行时发生变化，重新核查对应映射。

## 通用反例

一个 `project(x)` 调用可能产生 `layout_convert → matmul → output_cast`。若只把 matmul 画进 DAG，把整个调用移到辅助流可能造成两个向量转换并发，或者扩大等待区间。正确方案应明确移动的是整个调用还是内部阶段，并重新验证 buffer 生命周期与输出 dtype。

不同分支都调用同形状的 projection 时，依赖 correlation、scope 或调用顺序和数据流共同区分。最近时间戳配对只能作为待调查线索。
