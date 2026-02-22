# GitHub Sensor Skill

## 概述
为OpenClaw框架开发的GitHub感知器技能，作为DavidAgent仿生双脑架构感知层（Sensors）的核心组件。该技能能够从GitHub官方API获取最前沿的硬核技术趋势和深度项目解析，并将其标准化后投递给系统的黑板（Blackboard）。

## 架构定位
- **数据源类型**: GitHub官方API（Search API + Repository API + GraphQL API）
- **感知器角色**: 定向雷达，专门嗅探硬核技术真理和底层演进趋势
- **数据信噪比**: 极高（相比社交媒体高出几个数量级）
- **集成方式**: 异步技能组件，支持定时任务和事件触发

## 核心功能
1. **技术趋势获取**: 使用GitHub Search API获取过去24/48小时内创建且Star数最高的开源项目
2. **深度内容解卷**: 自动获取并解析高Star仓库的README.md内容
3. **实时脉搏监控**: 通过Events API监控特定用户或仓库的动态
4. **讨论区挖掘**: 使用GraphQL API抓取Discussions中的深度技术探讨

## 技术栈
- **异步框架**: Python asyncio
- **HTTP客户端**: httpx (支持异步和HTTP/2)
- **数据处理**: 标准化Markdown解析和文本清理
- **错误处理**: 指数退避重试 + 并发锁防爆盾

## 配置要求
- **环境变量**: `GITHUB_TOKEN` (用于提升API速率限制至5000次/小时)
- **依赖包**: httpx, aiofiles, python-dotenv

## 输出契约
所有输出必须符合统一数据契约格式：
```python
{
    "source_type": "github_trending|github_discussion|github_event",
    "source_id": "repo_12345678", 
    "author": "owner_username",
    "timestamp": "2026-02-21T10:00:00Z",
    "core_text": "【项目名称】: xxx\n【简介】: xxx\n【核心README】: ...",
    "original_url": "https://github.com/owner/repo"
}
```

## 使用场景
- **定时任务**: 每周一早上自动生成《本周GitHub值得关注的10个硬核开源项目》
- **事件触发**: 当行业大佬Star新项目时，自动触发深度解析
- **知识库更新**: 将高质量技术讨论存入PageIndex知识图谱
- **右脑内容生成**: 为Gemini提供高质量的Markdown格式输入

## 性能优势
- **二段式抓取**: 先搜索仓库，再并发获取README，I/O效率提升10倍
- **API防爆盾**: 完美应对GitHub速率限制，保证系统稳定性
- **左脑友好**: 原生Markdown格式，Gemini处理准确率接近100%