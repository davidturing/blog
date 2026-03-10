# 长期记忆 (Long-term Memory)

## 用户偏好 (User Preferences)
- **语言**: 中文 (Chinese)
- **沟通风格**: 尽量使用 session memory，注意控制上下文大小，避免过长。

## 系统环境 (System Environment)
- **操作系统**: macOS (Mac OS)
- **Python命令**: 使用 `python3` 而不是 `python`
- **pip命令**: 使用 `pip3` 而不是 `pip`
- **虚拟环境**: 项目使用 `venv` 虚拟环境，位于 `/Users/zhaoqinhuang/david_project/venv/`
- **Python路径**: 虚拟环境中的Python路径为 `/Users/zhaoqinhuang/david_project/venv/bin/python3.14`

## 技术问题 (Technical Issues)
- **2026-02-17**: 用户报告 `spawn EBADF` 错误。昨晚重装 OpenClaw。目前正在验证修复情况。

## 数字分身列表
数字分身通过不同方式验证其工作状态：

### 博客发布型数字分身
1. **科技达人**角色的目标网站：`dvspace5.wordpress.com`
2. **首席数据官**角色的目标网站：`datagov1.wordpress.com`

### 教学型数字分身  
3. **推荐系统老师**：负责推荐系统课程教学，包含完整的5课时课程体系、学生管理（Mike/John）、作业批改和成绩评估

### 专业领域型数字分身
4. **芯片数据专家**：专注半导体良率分析、Exensio平台、PDF Solutions技术栈
5. **家庭助理**：专注家庭生活场景协助
6. **大数据专家**：全行业通用大数据技术，包含华为云MRS和GaussDB(DWS)全栈技术
7. **Python 数据分析师**：面向数据架构师的 AI 数字分身 + 现代化 Python 开发专家

### AI教育体系型数字分身
8. **Vibe Coding 老师**：斯坦福 CS146S The Modern Software Developer 课程，专注Vibe Coding、自然语言驱动开发、AI IDE、MCP协议、Agent架构
9. **Agent 自进化老师**：斯坦福 CS329A Self-Improving AI Agents 课程，专注Agent自进化、反思机制、强化学习、工具调用、检索增强
10. **多智能体老师**：斯坦福 CS372 AGI for Reasoning & Planning 课程，专注多Agent协同、长链规划、MACI框架、时序推理、全局调度  
11. **Agentic AI 老师**：吴恩达 Agentic AI（四大模式实战课），专注Reflection、Tool Use、Planning、Multi-agent 四大模式

### 全链路视觉创作数字分身
12. **摄影师（GLM）**
- **身份**：摄影师
- **模型**：GLM 大模型
- **核心能力**：
  - 佳能 / 索尼 / 尼康 单反、微单、镜头体系
  - 华为、苹果手机专业摄影、创作
  - 大疆无人机航拍、运镜、构图
  - 望远镜观测与拍摄
  - 照片/视频后期（LR、PS、PR、剪映、达芬奇）
  - AI 照片创作、AI 视频生成、AI 修图扩图
- **定位**：全链路视觉创作专家（拍摄 + 后期 + AI 创作）

### 企业架构与咨询数字分身
13. **数字化转型专家（GLM）**
- **身份**：数字化转型专家
- **模型**：GLM 大模型
- **核心能力**：
  - 企业数字化转型整体规划与落地
  - 企业战略规划、业务架构、IT 架构
  - IT 治理、数据治理、合规与风险管控
  - 企业 IT 运维、云平台、自动化运维
- **定位**：企业级数字化顶层设计与落地专家

### WordPress 账户信息
- 两个网站使用同一个 WordPress 账户：`davidturing`
- 两个网站的 WordPress 应用密码相同
- 凭据存储在 `.credentials/wordpress.env` 文件中

## 知识库
**科技达人**和**首席数据官**两个角色的**知识总结**都应存放于 GitHub 仓库: `https://github.com/davidturing/tech`

## DAMA-DMBOK2 教程图像标准（2026-02-25）

### 蓝图风格 sRGB 背景颜色标准
所有 DAMA-DMBOK2 教程 PPT 图片必须使用统一的深蓝色背景，参考以下 sRGB 值：

- **标准深蓝色**: srgb(9,53,114) 到 srgb(16,61,120)
- **具体章节参考**:
  - Chapter 05: srgb(9,53,114)
  - Chapter 06: srgb(16,61,120) 
  - Chapter 03 (修正后): srgb(13,52,107)

### 图像生成规范
- **风格**: Professional blueprint aesthetic with technical precision
- **背景**: Dark blue gradient (#093572 to #103D78)
- **文字**: High contrast white/light blue text for readability
- **布局**: Clean, organized grid with DAMA three-step methodology (Plan-Develop-Control-Operate)
- **分辨率**: 2K quality, 16:9 aspect ratio
- **模型**: gemini-3-pro-image-preview (formerly "banana")

### 文件命名约定
- **格式**: chapter_XX_blueprint.png (XX = 两位章节数字)
- **位置**: github.com/davidturing/tech/damabook/
- **数字分身**: 首席数据官 (Chief Data Officer)

## 凭据管理架构（2026-02-24）
为解决 WordPress 凭据发现问题，已实施**统一凭据管理中心**：

### 架构设计
- **凭据中心**: `.credentials/` 目录
- **自动发现**: 支持多位置凭据扫描（DavidAssistant/.env, .credentials/, etc.）
- **数字分身**: 通过 `digital_personas.json` 配置不同角色的凭据
- **智能注入**: 根据任务上下文自动选择正确的凭据集

### 凭据文件
- `.credentials/wordpress.env`: WordPress 凭据
- `.credentials/api_keys.env`: API 密钥  
- `.credentials/digital_personas.json`: 数字分身配置
- `.credentials/credential_manager.py`: 凭据管理器

### 安全特性
- 环境变量优先传递敏感凭据
- 文件权限控制（仅用户可读写）
- 凭据验证与缓存机制
- 最小权限原则

此架构确保了自动化任务的可靠执行，避免了凭据缺失导致的工作流中断。

## 模型使用策略（2026-03-02）
**重要**: David 明确表示暂时不会使用 OpenAI 的模型。任何新大模型的引入到 DavidAgent 都必须获得 David 的明确同意。

### 授权模型优先级
1. **首选**: Google Gemini (已授权)
2. **备选**: 千问（Qwen）模型，简称 Q老师 (DashScope 通义万象，已授权)  
   - **当前默认模型**: bailian/qwen3-max-2026-01-23
3. **禁止**: OpenAI 系列模型 (未经用户同意)

### 执行原则
- 绝不自动尝试未授权的 API 密钥或模型
- 在技能调用前必须检查模型授权状态
- 所有自动化流程必须遵循此模型使用策略
- 当前会话使用模型: bailian/qwen3-max-2026-01-23
## 飞书原生附件发送方案（2026-03-09）
当 `feishu_doc` 等原生工具因权限受限无法发送实际文件附件时，采用以下通过 OpenAPI `requests` + `requests-toolbelt` 封装的标准方案：
1. **获取 Tenant Token**: 调用 `/auth/v3/tenant_access_token/internal`。
2. **多部分表单上传**: 使用 `requests_toolbelt.MultipartEncoder` 封装流式数据，向 `/im/v1/files` 提交获取 `file_key`。
3. **消息发送**: 调用 `/im/v1/messages?receive_id_type=open_id` 将 `file_key` 组装在 `msg_type="file"` 中发送。
此方案已验证成功且稳定，用于向 David 的飞书客户端直接推送报告、数据文件。
