# World Grounding & Proactive Exploration System

**从孤岛智能 → 全球感知智能**  
彻底解决认知近亲繁殖问题，实现 DavidAgent 的自主世界感知能力。

## 🎯 核心目标

1. **5大外部资讯自主获取通道** - 24小时静默世界感知
2. **认知熵驱动探索** - 只补认知缺口，不重复学习  
3. **双脑知识蒸馏** - 左脑分析技术结构，右脑合成概念洞察
4. **影子沙箱安全验证** - 100%外部知识隔离验证
5. **CPEP跨分身经验对齐** - 单点学习 → 全系统红利

## 🏗️ 系统架构

```
World Grounding System
├── sensors/                    # 感知模块
│   ├── external_watcher.py     # 主入口协调器 (5大通道)
│   ├── embedding/              # ANE向量化
│   │   └── ane_encoder.py      # Apple Neural Engine加速
│   ├── distiller/              # 双脑蒸馏
│   │   └── brain_balance.py    # 左脑分析 + 右脑合成
│   ├── sandbox/                # 影子沙箱
│   │   └── shadow_runner.py    # Docker隔离验证
│   └── cpep/                   # 跨分身同步
│       └── align_broadcast.py  # CPEP协议实现
├── config/                     # 配置文件
│   └── world_grounding.toml    # 系统配置与限流
├── data/                       # 数据存储
│   ├── lancedb/                # 向量数据库 (磁盘存储)
│   ├── reasoning_bank.jsonl    # 避坑规则库
│   └── skill_rl.jsonl          # 技能强化学习库
├── memory/                     # 每日学习报告
├── logs/                       # 系统日志
├── requirements.txt            # 依赖清单
├── run_world_grounding.sh      # 一键启动脚本
└── README.md                   # 本文件
```

## ⚙️ Mac mini M4 优化特性

- **ANE加速**: 利用Apple Neural Engine进行高效向量化
- **内存优化**: ≤2GB内存占用，LanceDB磁盘索引
- **流量控制**: ≤100MB/日带宽限制，带熔断机制  
- **后台运行**: 仅在凌晨02:00-06:00低峰期运行
- **资源隔离**: 不抢占前台应用资源

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd world-grounding-system
```

### 2. 一键启动
```bash
./run_world_grounding.sh
```

### 3. 查看结果
- **每日报告**: `memory/YYYY-MM-DD.md`
- **系统日志**: `logs/world_grounding.log`
- **验证技能**: `data/skill_rl.jsonl`
- **避坑规则**: `data/reasoning_bank.jsonl`

## 🔧 配置说明

所有配置都在 `config/world_grounding.toml` 中：

- **系统约束**: 内存、带宽、运行时间窗口
- **数据源**: GitHub、RSS、社交平台、文档、Q&A
- **算法参数**: 认知熵阈值、置信度要求、测试用例数量
- **分身类型**: 支持的数字分身列表

## 📊 验收标准

✅ **功能完整**: 5大通道可用、认知熵过滤、双脑蒸馏、沙箱验证、CPEP同步  
✅ **性能达标**: 内存≤2GB、日流量≤100MB、ANE加速、静默后台  
✅ **安全保障**: 100%沙箱验证、来源追踪、错误经验留存  
✅ **无缝融合**: 接入SkillRL+ReasoningBank、无幻觉、自动汇报  
✅ **体验优秀**: 新技能自动可用、分身能力同步、稳定无故障

## 📅 自动化流程

1. **02:00**: 自动启动世界感知周期
2. **02:00-06:00**: 并行抓取5大资讯源
3. **实时**: 认知熵过滤 + 双脑蒸馏
4. **实时**: 影子沙箱验证
5. **实时**: CPEP跨分身广播
6. **08:00**: 生成每日学习报告

## 🤖 数字分身适配

新技能验证通过后，自动为不同分身生成适配版本：

- **科技达人**: 科普文章风格，强调技术影响
- **首席数据官**: 治理视角，关注风险和合规  
- **Vibe Coding老师**: 代码示例，实操指导
- **Agent自进化老师**: 反思性学习，哲学洞察
- **多智能体老师**: 系统思维，协调模式

## 🛡️ 安全设计

- **零信任原则**: 所有外部知识必须经过沙箱验证
- **资源隔离**: Docker容器隔离，网络禁用，内存限制
- **熔断机制**: 带宽超限自动停止，防止API滥用
- **审计追踪**: 完整的来源、时间戳、置信度记录

## 📈 扩展性

- **新增数据源**: 实现新的poll方法并更新配置
- **新分身类型**: 在CPEP模板中添加新persona配置
- **算法优化**: 替换ANE编码器或蒸馏逻辑
- **存储扩展**: 集成更多向量数据库选项

---

**DavidAgent World Grounding System** - 让AI真正理解这个世界 🌍