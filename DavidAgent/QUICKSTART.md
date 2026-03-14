# DavidAgent 感知收割机 - 快速启动指南

## 🚀 5分钟快速启动

### 第一步：配置 API 凭据（可选）

编辑 `.credentials/api_keys.env` 文件：

```bash
# 至少配置 GitHub Token 以启用 GitHub 感知
GITHUB_TOKEN=your_github_personal_access_token

# 其他 API 可选
X_API_BEARER_TOKEN=your_twitter_bearer_token
SERPAPI_KEY=your_serpapi_key
```

> 💡 没有 API Token？系统仍可运行，将使用模拟数据进行演示。

### 第二步：安装依赖

```bash
cd DavidAgent
pip3 install -r requirements_sensors.txt --break-system-packages
```

### 第三步：运行系统

```bash
cd brain/sensors

# 模拟运行（推荐首次使用）
python3 run_discovery.py --dry-run

# 正式运行
python3 run_discovery.py

# 强制抓取（忽略缓存）
python3 run_discovery.py --force_fetch
```

### 第四步：查看结果

```bash
# 查看每日报告
cat ../../reports/daily_report_*.md

# 查看系统日志
tail -f ../../logs/discovery.log

# 查看记忆数据
ls ../../hippocampus/episodic/
```

## 📊 预期输出示例

```
🚀 DavidAgent 感知收割机启动
============================================================
[INFO] 🚀 启动五大感知通道...
[INFO] 📊 感知完成: GitHub 3 | RSS 5 | Social 2 | Docs 2 | QA 3
[INFO] 🔍 开始认知熵过滤，共 15 项洞察...
[INFO] ✅ 认知熵过滤完成，保留 8 项高价值洞察
[INFO] 💾 洞察已保存到记忆
[INFO] 📚 已追加 8 条到 ReasoningBank
[INFO] 📄 每日报告已生成
============================================================
✅ 感知收割完成，耗时 12.34 秒
============================================================
```

## 🔧 常见问题

### Q1: 没有配置 API Token，能运行吗？

**A**: 可以！系统会使用模拟数据进行演示，所有功能均可测试。

### Q2: 如何获取 GitHub Token？

**A**: 访问 https://github.com/settings/tokens/new，创建 Personal Access Token，勾选 `public_repo` 权限即可。

### Q3: 内存占用多少？

**A**: 默认限制 2GB，实际运行通常 < 500MB（Polars 高效存储）。

### Q4: 每天什么时候运行？

**A**: 建议使用 crontab 设置为凌晨 01:00 自动运行：

```bash
crontab -e
# 添加以下行：
0 1 * * * cd /path/to/DavidAgent/brain/sensors && python3 run_discovery.py >> /path/to/logs/cron.log 2>&1
```

### Q5: 如何自定义感知主题？

**A**: 编辑 `brain/sensors/config.json`：

```json
{
  "github_topics": ["your-topic-1", "your-topic-2"],
  "social_keywords": ["Keyword1", "Keyword2"],
  "rss_feeds": ["https://your-rss-feed.com/rss.xml"]
}
```

## 📈 进阶使用

### 集成到左脑/右脑蒸馏

```python
from run_discovery import DiscoveryOrchestrator

# 创建调度器
orchestrator = DiscoveryOrchestrator()

# 运行感知
insights = await orchestrator.run_all_channels()

# 应用认知熵过滤
filtered = orchestrator.apply_cognitive_filter(insights)

# 传递给左脑/右脑
left_brain_result = left_brain.extract_structure(filtered)
right_brain_result = right_brain.extract_insights(filtered)
```

### 接入 ReasoningBank

```python
# ReasoningBank 位于：
DavidAgent/brain/reasoning_bank.jsonl

# 格式：每行一个 JSON 对象
{"source": "github", "title": "...", "content": "...", "timestamp": "..."}
```

## 🎯 下一步

1. **配置定时任务**: 设置 crontab 每日自动运行
2. **优化配置**: 根据需求调整 `config.json` 参数
3. **集成工作流**: 接入左脑/右脑蒸馏系统
4. **监控告警**: 配置日志监控和异常告警

---

**准备就绪！开始你的感知收割之旅** 🌍