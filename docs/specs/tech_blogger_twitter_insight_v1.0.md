# Tech Blogger Twitter Insight Tool - SDD v1.0

## 1. 目标锚定 (Why & CPEP 认知红利)
- **Why**: 自动化抓取 AI 领域最新 Twitter 动态，生成深度中文洞察博客
- **Cognitive Profit**: 减少人工监控时间，提高内容时效性和质量
- **Expected Outcome**: 每日自动发布高质量 AI 洞察文章到 dvspace5.wordpress.com

## 2. 契约定义 (I/O、类型、范围、熔断阈值、状态机)
- **Input**: Twitter API credentials, search keywords, time range (last 24h)
- **Output**: Formatted blog post in Markdown with Chinese translation and insights
- **Types**: 
  - Input: JSON config with API keys and parameters
  - Output: String (Markdown content)
- **Range**: 
  - Max tweets: 50 per execution
  - Time window: last 24 hours only
- **熔断阈值**: 
  - API rate limit: 300 requests/hour
  - Error tolerance: 3 consecutive failures → pause for 1 hour
- **状态机**: 
  - IDLE → FETCH_TWEETS → FILTER_AI → SUMMARIZE → TRANSLATE → PUBLISH → IDLE

## 3. 数据本体 (Data Ontology、存储 Schema、生命周期)
- **Data Ontology**:
  - Tweet: {id, text, author, timestamp, engagement}
  - Summary: {original_text, chinese_summary, insights, keywords}
  - BlogPost: {title, content, tags, publish_status}
- **存储 Schema**: 
  - Raw tweets: JSON format, temporary storage (24h TTL)
  - Summaries: SQLite database with daily rotation
  - Published posts: WordPress API direct publish
- **生命周期**: 
  - Raw data: 瞬时 (immediate processing, 1h TTL)
  - Summaries: 海马体 (24h retention for reference)

## 4. 容错与演进 (防御假设、自愈策略、架构教练干预规则)
- **防御假设**:
  - Twitter API may be rate limited or unavailable
  - Translation quality may vary
  - Network connectivity issues possible
- **自愈策略**:
  - Exponential backoff on API failures
  - Fallback to cached recent data if API down
  - Quality check on translation before publishing
- **架构教练干预规则**:
  - Any modification to core logic requires SDD update
  - New dependencies must pass security audit
  - Performance degradation > 20% triggers rollback

---
**Created by**: DavidAgent Self-Evolving Agent V2.0
**Compliance**: OpenSpec v1.0 Four Pillars ✅
**Status**: Ready for Architecture Coach Audit