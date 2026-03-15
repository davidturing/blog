# Daily Evolution Report Task - SDD v1.0

## 1. 目标锚定 (Why & CPEP 认知红利)
- **Why**: 每日自动生成 DavidAgent 自主进化状态报告，确保系统透明度和可追溯性
- **Cognitive Profit**: 自动化监控系统健康状态，及时发现潜在问题，减少人工检查成本
- **Expected Outcome**: 每日凌晨生成并推送当日进化报告到 GitHub，确保架构合规性

## 2. 契约定义 (I/O、类型、范围、熔断阈值、状态机)
- **Input**: 当前日期（自动获取）
- **Output**: Markdown 格式的每日进化报告文件
- **Types**: 
  - Input: datetime (auto-generated)
  - Output: string (Markdown content)
- **Range**: 
  - 报告内容长度: 500-2000 字符
  - 执行时间: ≤ 30 秒
- **熔断阈值**: 
  - GitHub 同步失败 → 自动重试 2 次后触发自愈
  - 文件写入失败 → 记录错误并继续
  - 连续 3 天失败 → 发送警报
- **状态机**: 
  - START → ARCHITECTURE_AUDIT → RUNNING → SUCCESS/FAILED → LOGGING → SELF_HEALING → ARCHIVED

## 3. 数据本体 (Data Ontology、存储 Schema、生命周期)
- **Data Ontology**:
  - EvolutionReport: {date, system_status, key_metrics, next_steps}
  - ExecutionLog: {task_name, start_time, end_time, success, errors}
- **存储 Schema**: 
  - 报告文件: davidagent_evolution/davidagent_evolution_YYYY-MM-DD.md
  - 执行日志: task_logs/daily_evolution_report_YYYYMMDD_HHMMSS.json
- **生命周期**: 
  - 报告文件: 永久存储（GitHub 归档）
  - 执行日志: 30 天 TTL（本地存储）

## 4. 容错与演进 (防御假设、自愈策略、架构教练干预规则)
- **防御假设**:
  - GitHub 可能暂时不可用
  - 文件系统可能写入失败
  - 网络连接可能中断
- **自愈策略**:
  - 自动重试机制（最多 2 次）
  - 递归自省分析失败根因
  - 自动修复权限/路径问题
- **架构教练干预规则**:
  - 任何绕过 SDD 的修改都被禁止
  - 未通过架构审计的任务不得执行
  - 失败率超过 10% 触发架构审查

---
**Created by**: Architecture Coach (DavidAgent V2.0)
**Compliance**: OpenSpec v1.0 Four Pillars ✅
**Enforcement**: Mandatory for all automated tasks