import re

with open('MEMORY.md', 'r', encoding='utf-8') as f:
    content = f.read()

new_list = """## 数字分身列表
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

### WordPress 账户信息"""

pattern = r"## 数字分身列表.*?### WordPress 账户信息"
new_content = re.sub(pattern, new_list, content, flags=re.DOTALL)

with open('MEMORY.md', 'w', encoding='utf-8') as f:
    f.write(new_content)
