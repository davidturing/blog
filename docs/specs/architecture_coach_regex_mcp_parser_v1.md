# Architecture Coach Regex MCP Parser - SDD v1.0

## 1. 目标锚定 (Why & CPEP 认知红利)
- **Why**: 解决动态/混淆 HTML 结构解析问题，特别是 GitHub 文档结构变更导致的 ParseError
- **Cognitive Profit**: 提高网页抓取工具的鲁棒性，减少因网站结构变更导致的失败
- **Expected Outcome**: 在 ≤200MB 内存限制下，实现 ≥95% 的 HTML 结构解析成功率

## 2. 契约定义 (I/O、类型、范围、熔断阈值、状态机)
- **Input**: 
  - html_content (string): 要解析的 HTML 内容
  - max_memory_mb (number, default: 200): 最大内存使用限制
  - min_content_length (integer, default: 50): 最小提取内容长度
  - fallback_to_beautifulsoup (boolean, default: true): 是否回退到 BeautifulSoup
- **Output**: 
  - parsed_content (string): 提取的纯文本内容
  - content_length (integer): 内容长度
  - method_used (string): 使用的解析方法 ("regex" 或 "beautifulsoup")
  - memory_used_mb (number): 实际内存使用量
- **Types**: 严格类型定义，符合 JSON Schema 标准
- **Range**: 
  - 内存限制: 1-1000 MB (默认 200MB)
  - 内容长度: 1-100000 字符
- **熔断阈值**: 
  - 内存超限 → 立即熔断
  - 内容长度不足 → 返回失败
  - 连续 5 次失败 → 启动自省模式
- **状态机**: 
  - IDLE → VALIDATE_INPUT → PARSE_WITH_REGEX → SUCCESS/FAILURE → FALLBACK_BS → FINAL_RESULT → IDLE

## 3. 数据本体 (Data Ontology、存储 Schema、生命周期)
- **Data Ontology**:
  - HTMLContent: {raw_html, size_bytes, source_url}
  - ParsedResult: {content_text, extraction_method, confidence_score}
  - PerformanceMetrics: {memory_used_mb, execution_time_ms, success_rate}
- **存储 Schema**: 
  - 输入数据: 瞬时处理，不持久化
  - 输出结果: 返回给调用方，可选缓存 (1h TTL)
  - 性能指标: 内存中聚合，定期清理
- **生命周期**: 
  - 输入数据: 瞬时 (immediate processing, no storage)
  - 输出结果: 海马体 (1 hour retention for debugging)
  - 性能指标: 瞬时 (real-time only, no persistence)

## 4. 容错与演进 (防御假设、自愈策略、架构教练干预规则)
- **防御假设**:
  - HTML 结构可能随时变化
  - 内存资源可能受限
  - 网络内容可能包含恶意代码
- **自愈策略**:
  - 多重解析策略 (regex + BeautifulSoup fallback)
  - 内存使用监控和限制
  - 自动性能退化检测
- **架构教练干预规则**:
  - 任何内存使用超过 200MB 的修改必须重新评估
  - 解析成功率低于 90% 触发自动优化
  - 新增依赖必须通过安全审计

---
**Created by**: Architecture Coach (Self-Evolving Agent V2.0)
**Compliance**: OpenSpec v1.0 Four Pillars ✅
**GitHub Sync**: Required before production deployment
**Status**: Ready for GitHub synchronization