# DavidAgent：仿生双脑多智能体系统详细设计方案（四重增强版）

## 一、 架构系统总览
系统深度模拟人类大脑的认知与进化机制，采用 **“仿生双脑（左脑逻辑/右脑创意）+ 四重增强架构”** 的核心设计。基于 Python 异步生态构建，是一个具备自主感知、深度思考与自我批判能力的响应式“数字生命体”。

**核心目标**：实现对 X 网站等高价值信息流的自动化研读、知识图谱内化、升维创作与自动化分身布道。

## 二、 核心五大器官 (The Five Organs)

### 1. 感知器 (Sensors)
- **物理实现**：基于 Playwright/AsyncIO 的异步爬虫。
- **职责**：从 X (Twitter)、RSS 等外部渠道抓取原始数据的“干草料”。

### 2. 左脑中枢 (Left Brain - The Logic)
- **物理基座**：**Gemini 2.5 Pro**。
- **职责**：
  - **知识解构**：利用 Pydantic 结构化输出，将非结构化文本提炼为 JSON 图谱（实体+三元组）。
  - **事实核查 (Fact-Checking)**：扮演免疫系统的职责，对右脑草稿进行红蓝对抗式的逻辑审查。

### 3. 右脑中枢 (Right Brain - The Creative)
- **物理基座**：**Qwen-Coder-Plus**。
- **职责**：
  - **Persona 演绎**：赋予系统以“科技达人”的灵魂与幽默感。
  - **升维创作**：将左脑的干瘪数据骨架，转化为引人入胜的技术博客。

### 4. 虚拟胼胝体 (Corpus Callosum - The Bus)
- **设计模式**：**黑板模式 (Blackboard Pattern)**。
- **技术实现**：`brain.memory.blackboard.BrainBlackboard`。
- **价值**：作为全局状态总线，实现左右脑的绝对解耦。通过事件驱动（Event-Driven）机制，实现 IDLE -> INGESTING -> DRAFTING -> REVIEWING -> READY -> PUBLISHED 的状态自动流转。

### 5. 海马体 (Hippocampus - The Memory)
四重增强的仿生存储矩阵，确保认知连续性：

#### **⚡ SkillRL（本能技能层）- 最高优先级**
- **功能**: 高频问题的即时响应，实现"本能反应"
- **触发条件**: 同一问题被问≥3次自动提炼为技能
- **响应速度**: < 10ms
- **特点**: 跳过所有复杂处理，直接返回答案

#### **💡 ReasoningBank（推理避坑层）- 第二优先级**
- **功能**: 提供历史教训和防坑建议
- **数据源**: 成功经验库 + 失败教训库
- **特点**: 主动预警潜在错误，避免重复踩坑

#### **🧠 Memory Alpha（智能记忆层）- 第三优先级**
- **架构**: 三级记忆（感知缓存 → 工作记忆 → 长期存储）
- **功能**: 管理短期记忆和上下文
- **特点**: 智能筛选重要信息，自动遗忘低价值内容

#### **📊 LanceDB 7层混合检索（精确检索层）- 底层保障**
- **Pipeline**: 向量检索 → BM25 → MMR去重 → 元数据过滤 → 时间衰减 → 偏好加权 → 重排序
- **功能**: 精准的历史记忆召回
- **特点**: 7层处理确保最高相关性

## 三、 认知自进化回路 (The Self-Evolution Loop)

1. **夜间反思 (Nightly Reflection)**：
   - 系统在低峰期自动扫描 SQLite 中的失败案例。
   - 使用 Gemini 2.5 Pro 进行元认知分析，提炼根因。
2. **规则演进 (Rule Consolidation)**：
   - 提取的规则经由剪枝与合并，动态写入 `dynamic_guidelines.md`。
   - 绝不盲目追加 Prompt，始终保持右脑创作指令的轻量与高效。
3. **技能进化 (Skill Evolution)**：
   - 高频成功案例自动提炼为本能技能
   - 失败教训自动转化为防坑策略

## 四、 高可用基座设计 (Resilience)

- **防爆熔断**：全局信号量 `asyncio.Semaphore(3)` 限制 LLM 并发，保护 API 余额与系统句柄。
- **弹性重试**：封装 `@with_resilience` 装饰器，实现指数退避与死信队列管控。
- ** Token 监控**：实时记录并可视化每一步的 API 消耗，确保“数字经济学”透明可控。
- **SDK 升级**：已从 `google.generativeai` 升级到 `google.genai`，确保长期兼容性

## 五、 技术栈清单 (Stack)

- **核心运行时**：Python 3.10+, AsyncIO, Pydantic v2
- **智能体引擎**：google-genai, DashScope Python SDK
- **存储引擎**：SQLite (WAL), ChromaDB, LanceDB
- **观测平台**：Streamlit Web 控制台

---
*最后更新: 2026-02-28*
*记录人: Steven (AI Assistant)*

这套设计将千问的广度与表达力同 Gemini 的深度与解析力完美结合，同时利用四重增强架构构建了坚不可摧的智能记忆底座。