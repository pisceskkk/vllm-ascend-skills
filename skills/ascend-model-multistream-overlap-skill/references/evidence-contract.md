# 输入与指标契约

## Kernel 归一化

输入 CSV 必需列：`Name,Start Time(us),Duration(us),Stream ID`。资源类型读取 `Accelerator Core`，缺失时读取 `Task Type`；未知值保留 unknown。可选形状、dtype、Model ID 字段用于归因。

时间以 Decimal 微秒解析，保留绝对时间及相对 origin，避免 epoch 浮点精度损失。source_row 是含 header 的 CSV 记录号；存在字段内换行时不是物理文本行号。source SHA256 固定源文件身份。

输出 events.csv 和 summary.json。累计 task duration 的占比不等于 wall-time 占比；按资源计算的区间并集是时间覆盖，不是核心数占用率或硬件利用率。不同名称/shape/dtype/core 分开汇总。

脚本不加载大 trace JSON。需要 flow、stack、event-wait 时使用环境的 trace 工具提取并关联。适配其他 exporter 时保留时钟域、单位、原始记录映射和 checksum。

## 显式配对

见 `assets/pairs-template.csv`：a 是目标，b 是伙伴；group_id 是核实过的同一逻辑操作实例；relation 为 intended_complementary 或 suspected_contention；evidence 包含代码/DAG/step/layer/branch/correlation 依据。事件必须同 case/rank/phase，跨 rank 时钟分析另行处理。

overlap = max(0, min(endA,endB)-max(startA,startB))；coverage_A = overlap/duration_A；launch_skew = startB-startA。零 duration 的 coverage 为 null。

同一目标对应多个伙伴时取重叠区间并集，目标 duration 只计一次，aggregate 按 relation 分开。共享资源标记仅代表风险，unknown 不得当作互补。采集边界截断的实例应排除或单列，不宣称完整掩盖。

## DAG

JSON 包含 context、nodes、edges。节点有唯一 id、label、非负 duration_us、resources、code_sites、evidence；边有 from、to、kind、evidence。kind 可为 data/stream/event/alias/cache/collective/lifetime。

校验器检查引用、重复边、环和非有限耗时，结合 code-map 核实映射结构，输出最早开始/结束、一个关键路径和 Mermaid。耗时来自同一代表性场景。下界不模拟资源竞争、host 开销或并发后的算子变慢。

## 性能 CSV

baseline/candidate 分开保存。必需列：`case_id,pair_id,metric,value,unit,profile_enabled,config_fingerprint,code_ref`。pair_id 对应交替实验的测量 block；同 case/pair 必须完整匹配且 unit/config 一致。fingerprint 固化模型、硬件、runtime、输入和参数，仅排除本次明确改变的因素；脚本只检查字符串，真实性由执行器保证。

value 为正值；profiler 必须关闭。按 case 对配对改善百分比做 bootstrap，默认至少 5 对。higher: 100*(candidate/baseline-1)；lower: 100*(1-candidate/baseline)。区间反映所测 block 的抽样不确定性，仍需检查漂移、独立性和多指标比较。

结果为 improved/regressed/within_regression_budget/inconclusive/insufficient_repeats。该结果不综合正确性和调度行为，不能独立批准交付。
