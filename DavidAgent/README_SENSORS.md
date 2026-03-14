# DavidAgent 感知收割机系统

**专为 Mac mini M4 优化的五大感知通道框架**

## 🎯 系统概述

DavidAgent 感知收割机是一个自动化的技术感知系统，通过五大通道实时捕获外部世界的技术演进：

1. **GitHub 技术演进探测器** - 发现高价值开源项目
2. **RSS/ArXiv 理论采集器** - 追踪学术论文和技术博客
3. **X/Twitter 趋势嗅探器** - 捕捉社交媒体热点
4. **官方文档本体重构器** - 爬取技术文档
5. **StackOverflow 异常补丁采集器** - 挖掘实战解决方案

## 🏗️ 系统架构

```
DavidAgent/
├── brain/
│   ├── sensors/                    # 五大感知通道
│   │   ├── __init__.py
│   │   ├── github_watcher.py       # GitHub 探测器
│   │   ├── rss_gatherer.py         # RSS 采集器
│   │   ├── social_sniffer.py       # 社交嗅探器
│   │   ├── doc_spider.py           # 文档爬虫
│   │   ├── qa_miner.py             # QA 采集器
│   │   ├── cognitive_filter.py     # 认知熵过滤
│   │   ├── run_discovery.py        # 总调度入口
│   │   └── config.json             # 感知配置
│   └── reasoning_bank.jsonl        # 推理规则库
├── hippocampus/
│   └── episodic/                   # 情景记忆
│       ├── github_seen_repos.parquet
│       └── discovery_*.json
├── logs/
│   └── discovery.log               # 系统日志
└── reports/
    └── daily_report_*.md           # 每日报告
```

## ⚙️ Mac mini M4 优化特性

- **内存友好**: ≤2GB 内存占用，使用 Polars + Parquet 高效存储
- **带宽控制**: ≤100MB/日流量，异步+限流设计
- **ANE 加速**: 向量化计算利用 Apple Neural Engine
- **后台运行**: 仅在凌晨 01:00-06:00 执行，不抢占前台资源
- **缓存优先**: 历史数据去重，避免重复抓取

## 🚀 快速开始

### 1. 安装依赖

```bash
cd DavidAgent
pip install -r requirements_sensors.txt
```

### 2. 配置 API 凭据

编辑 `.credentials/api_keys.env`：

```bash
GITHUB_TOKEN=your_github_token
X_API_BEARER_TOKEN=your_x_token
SERPAPI_KEY=your_serpapi_key
```

### 3. 配置感知参数

编辑 `brain/sensors/config.json`：

```json
{
  "github_topics": ["polars", "autogen", "llm"],
  "rss_feeds": ["https://arxiv.org/rss/cs.AI"],
  "cognitive_threshold": 0.65,
  "max_fetch_per_cycle": 5
}
```

### 4. 运行系统

```bash
cd brain/sensors

# 正常运行
python run_discovery.py

# 模拟运行（不保存数据）
python run_discovery.py --dry-run

# 强制抓取（忽略缓存）
python run_discovery.py --force_fetch
```

### 5. 查看结果

- **每日报告**: `DavidAgent/reports/daily_report_YYYYMMDD.md`
- **系统日志**: `DavidAgent/logs/discovery.log`
- **记忆数据**: `DavidAgent/hippocampus/episodic/`
- **推理规则**: `DavidAgent/brain/reasoning_bank.jsonl`

## 📊 认知熵过滤算法

系统使用 **KL 散度** 计算信息增益，只保留高价值内容：

```
Information Gain = KL(P_new || P_existing)

过滤规则:
- 信息增益 > 0.65 → 保留并蒸馏
- 信息增益 ≤ 0.65 → 丢弃（冗余或低价值）
```

这确保了：
- ✅ 避免重复学习
- ✅ 只关注真正的新知识
- ✅ 最小化 Token 消耗

## 🔧 高级配置

### 自定义感知主题

编辑 `config.json` 中的 `github_topics` 和 `social_keywords`：

```json
{
  "github_topics": ["your-topic-1", "your-topic-2"],
  "social_keywords": ["Keyword1", "Keyword2"]
}
```

### 调整执行窗口

修改 `execution_window` 参数：

```json
{
  "execution_window": {
    "start_hour": 1,  // 凌晨1点开始
    "end_hour": 6     // 早上6点结束
  }
}
```

### 资源限制

```json
{
  "memory_limit_mb": 2048,    // 内存上限
  "bandwidth_limit_mb": 100,  // 每日流量上限
  "max_fetch_per_cycle": 5    // 每轮抓取上限
}
```

## 📈 每日报告示例

```markdown
# DavidAgent 每日数字战利品报告
**生成时间**: 2026-03-15 01:05:23

## 📊 感知统计
- GitHub 仓库: 3 项
- RSS 文章: 5 项
- 社交趋势: 2 项
- 技术文档: 2 项
- QA 补丁: 3 项
- **总计**: 15 项

## 🔍 认知熵过滤
- 过滤前: 15 项
- 过滤后: 8 项
- 信息增益阈值: 0.65

## 💎 高价值发现
### 1. GitHub: openclaw/openclaw
- 来源: github
- 信息增益: 0.850
- 内容摘要: Next-generation AI agent framework with MCP protocol...
```

## 🔄 定时执行

使用 crontab 设置每日自动执行：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨1点执行）
0 1 * * * cd /path/to/DavidAgent/brain/sensors && python run_discovery.py >> /path/to/DavidAgent/logs/cron.log 2>&1
```

## 🛡️ 安全设计

- ✅ **零信任凭据**: 所有 API 凭据从环境变量加载
- ✅ **无硬编码**: 代码中不包含任何密钥
- ✅ **缓存隔离**: 历史数据使用 Parquet 独立存储
- ✅ **资源限制**: 内存、带宽、执行时间全面限制

## 🔗 集成接口

### 接入左脑/右脑蒸馏

过滤后的洞察可通过以下接口传递给左脑/右脑模块：

```python
# 获取过滤后的洞察
filtered_insights = orchestrator.apply_cognitive_filter(all_insights)

# 传递给左脑（技术结构提取）
left_brain_result = left_brain.extract_structure(filtered_insights)

# 传递给右脑（概念洞察提取）
right_brain_result = right_brain.extract_insights(filtered_insights)
```

### 接入 ReasoningBank

系统自动将高价值洞察追加到 `reasoning_bank.jsonl`：

```json
{"source": "github", "title": "...", "content": "...", "timestamp": "..."}
{"source": "rss", "title": "...", "content": "...", "timestamp": "..."}
```

### 接入 Tailscale + OpenClaw

系统已兼容 Tailscale 和 OpenClaw 网关：

- 通过 Tailscale 访问内网资源
- 通过 OpenClaw 调用远程工具
- 所有网络请求支持代理配置

## 🐛 故障排除

### 依赖问题

```bash
# 如果遇到依赖冲突，建议使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements_sensors.txt
```

### 内存不足

调整 `config.json` 中的 `max_fetch_per_cycle` 参数，减少单轮抓取数量。

### API 限流

检查 `.credentials/api_keys.env` 中的 API 凭据是否有效，或等待 API 限流窗口重置。

## 📝 开发者备注

- 所有模块支持异步执行，提升并发性能
- 认知熵过滤算法可独立扩展（`cognitive_filter.py`）
- 各感知通道模块化设计，易于添加新通道
- 完整的日志记录，便于调试和审计

---

**DavidAgent 感知收割机 - 让 AI 真正看见世界** 🌍