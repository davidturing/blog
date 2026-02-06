<!-- Sync Impact Report
- Version change: 1.1.1 -> 1.1.2
- List of modified principles: Added Principle VI (Documentation Standards)
- Added sections: VI. Documentation Standards
- Templates requiring updates: ✅ None
-->

# 数据治理知识库项目章程 (Data Governance Knowledge Base Constitution)

## 核心原则 (Core Principles)

### 一、结构化与模块化 (I. Structured & Modular)
知识库必须严格遵循层级化的目录结构。
- 每个核心主题独立为一个章节目录（如 `01.数据治理核心概念`）。
- 每个章节目录必须包含一个 `index.md` 作为导航入口。
- 所有引用资源应放置在同级或下级的 `images/` 或 `resources/` 目录中，保持自包含性。

### 二、图文并茂与易读性 (II. Visual & Accessible)
内容必须追求高可读性，避免晦涩的学术堆砌。
- **强制要求**：核心概念必须配有图表（流程图、架构图、思维导图）进行可视化解释。
- 语言风格应专业且通俗，优先使用“主-谓-宾”短句。
- 关键术语首次出现时应提供中英文对照。

### 三、markdown 优先 (III. Markdown First)
所有文档必须使用标准 Markdown 格式。
- 严禁使用特定平台的专有语法。
- 代码块必须指定语言标记（如 ````json`）。
- 链接必须使用相对路径，确保在不同环境下（本地/GitHub/Web）均可跳转。

### 四、循证与前瞻 (IV. Evidence-Based & Forward-Looking)
内容建设应兼顾理论沉淀与前沿趋势。
- 理论阐述应引用权威标准（如 DAMA, DCMM）。
- 必须包含 `2026_insights.md` 等前瞻性分析，捕捉大模型（LLM）时代的数据治理新挑战。
- 案例分析应基于真实或高仿真场景。

### 五、目录层级控制 (V. Directory Depth Control)
严格限制目录嵌套深度，保持扁平化。
- **最大层级限制**：知识库章节结构最多支持 3 层。
- **目录策略**：仅第 1 层章节必须创建独立目录（如 `01.数据治理核心概念/`）。
- **文件策略**：第 2 层和第 3 层内容直接以 Markdown 文件形式存在于第 1 层目录下，**严禁创建第 2 层或第 3 层子目录**。

### 六、文档格式规范 (VI. Documentation Standards)
所有文档撰写必须严格遵循 `/Users/david/david_project/智能体/spec/doc-spec.md` 定义的视觉与语义标准。
- **字体强制**：正文使用微软雅黑 (Microsoft YaHei)，标题使用宋体 (SimSun)。
- **语义样式**：核心术语首次出现必须 **加粗**，提示/警告信息必须 _斜体_。
- **列表缩进**：嵌套列表严格使用 4 空格缩进。

## 非功能性约束 (Constraints)

- **文件名规范**：使用英文或拼音命名文件（如 `data_quality.md`），避免在 URL 中出现中文编码问题（章节目录名除外）。
- **代码存放规范**：所有自动化脚本（如 Python 脚本）必须存放在 `/Users/david/david_project/datapipeline/` 目录下，严禁直接放置在项目根目录。
- **版本控制**：所有变更必须通过 Git 提交，且 Commit Message 需清晰描述变更内容。

## 治理机制 (Governance)

本章程是项目协作的最高准则。
- **变更流程**：对本章程的任何修改需经核心维护者批准，并更新版本号。
- **合规审查**：新加入的章节必须在合并前通过“章程符合性检查”（尤其是图表完整性）。

**Version**: 1.1.2 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
