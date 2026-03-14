# World Grounding & Proactive Exploration System

![Mac mini M4 Optimized](https://img.shields.io/badge/Optimized-Mac%20mini%20M4-333333?logo=apple)
![ANE Accelerated](https://img.shields.io/badge/ANE-Accelerated-FF9500?logo=apple)
![Low Memory](https://img.shields.io/badge/Memory-%3C2GB-4A90E2)

**从孤岛智能→全球感知智能，彻底解决认知近亲繁殖问题**

## 🎯 核心目标

1. **5大外部资讯自主获取通道** - 24小时静默世界感知
2. **认知熵驱动探索** - 只补认知缺口，不重复学习  
3. **双脑知识蒸馏** - 左脑分析结构，右脑合成洞察
4. **影子沙箱安全验证** - 100%外部知识隔离验证
5. **CPEP跨分身经验对齐** - 单点学习→全系统红利

## 🏗️ 系统架构

```
World Grounding System
├── sensors/
│   ├── external_watcher.py          # 主入口协调器
│   ├── embedding/
│   │   └── ane_encoder.py           # ANE向量化编码器
│   ├── distiller/
│   │   └── brain_balance.py         # 双脑知识蒸馏
│   ├── sandbox/
│   │   └── shadow_runner.py         # 影子沙箱验证
│   └── cpep/
│       └── align_broadcast.py       # 跨分身对齐协议
├── config/
│   └── world_grounding.toml         # 系统配置文件
├── data/                           # 持久化存储
│   ├── lancedb/                    # LanceDB向量数据库
│   ├── reasoning_bank.jsonl        # ReasoningBank避坑规则
│   └── skill_rl.jsonl              # SkillRL技能库
├── memory/                         # 每日学习报告
├── requirements.txt                # 依赖清单
├── start_world_grounding.sh        # 一键启动脚本
└── README.md                       # 本说明文档
```

## 🚀 快速开始

### 1. 系统要求

- **硬件**: Mac mini M4 (推荐) 或其他 Apple Silicon Mac
- **软件**: macOS, Docker Desktop for Mac, Python 3.9+
- **网络**: 稳定互联网连接 (每日流量限制 ≤100MB)

### 2. 安装部署

```bash
# 克隆项目（如果尚未存在）
git clone <your-repo-url>
cd world-grounding-system

# 赋予启动脚本执行权限
chmod +x start_world_grounding.sh

# 启动系统（自动创建虚拟环境并安装依赖）
./start_world_grounding.sh
```

### 3. 自动化运行

系统设计为**完全自动化**运行：

- **02:00-06:00**: 执行世界感知周期（低峰期，不抢占前台资源）
- **08:00**: 生成每日学习报告到 `memory/` 目录
- **后台静默**: 内存占用 ≤2GB，支持 ANE 加速

## 🔧 配置说明

所有配置都在 `config/world_grounding.toml` 中：

### 系统约束
```toml
[system]
max_memory_mb = 2048                    # 最大内存限制 (2GB)
daily_bandwidth_limit_mb = 100          # 每日带宽限制 (100MB)
ane_enabled = true                      # 启用 ANE 加速
background_only = true                  # 仅后台运行
run_window_start = "02:00"              # 运行窗口开始时间
run_window_end = "06:00"                # 运行窗口结束时间
```

### 资讯源配置
```toml
[sources.github]
enabled = true
rate_limit_per_hour = 30

[sources.rss]
enabled = true
feeds = [
    "https://arxiv.org/rss/cs.AI",
    "https://arxiv.org/rss/cs.LG",
    # ... 更多订阅源
]

[sources.social]
enabled = true
platforms = ["hackernews", "reddit"]
```

### 算法参数
```toml
[curiosity_engine]
similarity_threshold = 0.6              # 认知熵相似度阈值
min_popularity_score = 10               # 最小热度分数

[shadow_sandbox]
max_test_cases = 10                     # 最大测试用例数
timeout_seconds = 60                    # 沙箱超时时间
```

## 📊 验收标准

✅ **功能完整**: 5大通道可用、认知熵过滤有效、蒸馏输出标准、沙箱安全、CPEP同步、全自动运行

✅ **性能达标**: 内存≤2GB、日流量≤100MB、ANE加速、静默后台、LanceDB磁盘存储

✅ **安全保障**: 所有外部知识100%沙箱验证、带来源/时间戳/置信度、错误经验留存、无API滥用

✅ **无缝融合**: 无缝接入SkillRL+ReasoningBank、无幻觉、无过时知识、每日自动汇报

✅ **体验优秀**: 新技能自动可用、分身能力自动同步、稳定无故障

## 🤖 数字分身支持

系统支持以下数字分身的自动内容转译：

- **科技达人** → 科普博客文章
- **首席数据官** → 数据治理洞察  
- **Vibe Coding 老师** → 编程教学课程
- **Agent 自进化老师** → 强化学习课程
- **多智能体老师** → 协同规划方案
- **大数据专家** → 大数据解决方案
- **推荐系统老师** → 推荐算法课程
- **芯片数据专家** → 半导体分析报告
- **家庭助理** → 家庭自动化方案
- **Agentic AI 老师** → Agentic AI 课程
- **Python 数据分析师** → 数据分析代码
- **摄影师（GLM）** → 摄影技术指南
- **数字化转型专家（GLM）** → 数字化转型策略

## 📈 输出示例

每日 08:00 自动生成的学习报告：

```
David，我已完成昨晚的世界探索：
发现新技术：3 | 验证技能：2 | 存入 SkillBank：2 条 | 存入 ReasoningBank：1 条避坑规则 | 已同步所有分身 | 流量使用：45.2MB | 认知熵降低：15.3%
```

## 🛠️ 开发与调试

### 手动运行单次周期
```bash
source venv/bin/activate
python3 -m sensors.external_watcher
```

### 查看日志
系统使用标准 Python logging，日志输出到 stdout/stderr。

### 测试组件
各模块都包含完整的类型注解和异常处理，支持单元测试。

## 📜 许可证

本系统遵循 DavidAgent 的内部使用协议，专为 Mac mini M4 环境优化。

---

**🚀 从孤岛智能到全球感知，让 AI 拥有真正的世界视野！**