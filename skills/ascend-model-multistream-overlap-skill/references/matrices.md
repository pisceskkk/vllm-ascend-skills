# 三类叠加矩阵

矩阵模板中的 candidate/unmeasured 表示待选择、未验证。根据改动影响填写选择理由和不适用证据；不默认执行完整笛卡尔积。

## Workload

使用 `assets/workload-matrix.csv`：phase、输入/输出/KV 长度、请求率/并发、实际设备 batch、token/padding、chunking、cache 状态、稳态/边界/压力点。按业务分布选择典型点，并保留低占用、长上下文、图档位边界等受影响场景。

不同 workload 单独统计，不混合不同形状的 kernel 时长。业务权重未知时不输出任意加权总收益。

## 功能交互

使用 `assets/feature-interaction-matrix.csv`。从图模式、TP/DP/PP/CP/EP、dtype/量化/布局、投机执行、异步调度、chunking、prefix cache、既有 overlap 中选择真实支持且受影响的组合。先单功能，再有风险的两两组合，最后实际部署的高阶组合；两两覆盖不能证明全部高阶组合。

覆盖 source/consumer、局部/global tensor、空本地输入、尾块、有效 token/padding 和静态 buffer 重放。不能把不支持或未测试当通过。

## 资源叠加

使用 `assets/resource-overlap-matrix.csv`，按硬件实测调整：

- AIC × AIV：常见候选，但可能共享带宽或存在混合实现。
- AIV × AIV、AIC × AIC：存在共享执行资源风险；低占用或空洞可能仍允许收益。
- mixed × AIC/AIV：分解真实资源需求，不能只看主核标签。
- compute × communication：检查 AIV、网络、HBM 与进程组顺序。
- compute × memory movement：检查 copy 实现、带宽和 tensor 生命周期。
- unknown：补充证据后再判断。

同形状 kernel 变慢是竞争线索。比较时保持 dtype、布局、tiling、图模式和负载条件；tiling 改变应单独归因。
