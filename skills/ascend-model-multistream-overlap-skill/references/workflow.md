# 工作流与调度设计

## 实验边界与窗口

基线/候选使用相同模型、硬件、runtime、输入、负载生成和采样配置。记录 commit、dirty diff、native 算子版本。先明确目标是 TTFT、ITL、step latency、吞吐还是 SLO goodput；约束指标可以不同。固定请求率与饱和并发分别解释，客户端并发不等于设备实际 batch。

采集前确认真实请求可完成。预热后开启有界窗口，使用单调时钟 deadline、独立停止控制和异常清理；start/stop 都应有超时。stop 失败时检查实际状态，用环境支持的方式结束本次采集并报告实际时长，不能默认为已停止。清理范围限于本次拥有的服务/进程。

分别观察 prefill 的输入/token 总量与 chunk 边界、decode 的 batch/KV/图档位、mixed 的比例和动态调度。启动/冷编译仅在它们是目标时单独测量。多个短窗口可优于一个全流程大 trace。

保存窗口内实际形状、padding、step 类别和 rank 角色。缺少 step 标记时结合调用链、图实例和形状确认，仍不确定则标 unknown。检查请求成功率、预期 rank 数、device kernel 输出、时钟域和时间覆盖。缺失 rank 不能外推为全拓扑成功。

## 从模块到资源 DAG

展开关键路径中的 Cast、Contiguous/布局转换、量化、归约、cache 发布和 collective。使用实际 task type、计数器和调用链标注 AIC/AIV/mixed/CPU/communication/unknown；名称不保证跨芯片/版本/tiling 的资源类型一致。

先依据 [源码映射](code-mapping.md) 绑定节点，再建基线与候选 DAG。边类别：

| 类型 | 含义 | 调整时需要证明 |
|---|---|---|
| data | tensor producer → consumer | 生产完成且消费者可见 |
| stream | 同流提交顺序 | 是否存在真实数据依赖 |
| event | 跨流 record/wait | 所有分支记录/等待正确 |
| alias | in-place 与共享 view | 无读写/写写冲突 |
| cache | KV/state 发布与消费 | slot、版本、可见性一致 |
| collective | 进程组操作序列 | 全 rank 顺序/参与集合一致 |
| lifetime | 异步使用与复用/释放 | 分配器与 graph buffer 安全 |

时间相邻不建立依赖。记录删除/新增边及理由，未证明可移除的边保留。模型语义图与含 event/wait 的执行图分开标识。

## 通用调度示例

**向量与矩阵配对：** 独立的向量处理与投影可尝试并发，但投影内部可能先执行向量布局转换。将转换纳入 DAG；考虑先完成前置阶段，再并发目标阶段，或用更早的独立矩阵计算掩盖前置阶段。不要通过改变必要 dtype 语义来消除转换。

**通信掩盖：** 启动异步通信后推进不依赖其输出的计算，仅在真实消费者前等待。确认通信是否占用 AIV、copy engine、网络/HBM，以及进程组顺序。等待后移不保证总延迟下降。

**短 kernel：** stream/event/host launch 开销可能超过可隐藏时间；减少同步、融合或保持串行可作为候选。图回放收益不能直接外推 eager。

**流水化：** 跨块/层/微批重排需要记录依赖距离、在途 tensor、缓存槽复用、尾块和 rank 分支。不要仅复制一段 Python 调用到另一流。

每个方案记录关键路径下界、预计收益来源、新增瓶颈、正确性不变量、验证矩阵与拒绝条件。下界只用于筛选，实际执行决定保留与否。
