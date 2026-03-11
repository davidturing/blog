"""
AutoGen Digital Personas Module

This file defines all 16 digital personas as standard AutoGen AssistantAgents.
- 13 original personas from MEMORY.md
- 3 fixed core agents: AutoGen_Arch_Review_Agent, Code Agent, Code Review Agent

These agents can be invoked by a UserProxyAgent for various tasks.
"""

import os
import autogen

# Load API keys from environment or .env file
from dotenv import load_dotenv
load_dotenv()

# Configure LLMs based on David's model policy
GEMINI_CONFIG = {
    "config_list": [
        {
            "model": "gemini-3.1-pro-preview",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "base_url": "https://generativelanguage.googleapis.com/v1beta/"
        }
    ],
    "temperature": 0.7,
    "cache_seed": None
}

QWEN_CONFIG = {
    "config_list": [
        {
            "model": "qwen3-max-2026-01-23",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
    ],
    "temperature": 0.7,
    "cache_seed": None
}

# ==============================
# 1. Original 13 Digital Personas
# ==============================

# Blog Publishing Personas
tech_enthusiast = autogen.AssistantAgent(
    name="Tech_Enthusiast",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Tech Enthusiast' digital persona. Your role is to manage and publish content to the dvspace5.wordpress.com blog. You are an expert in AI trends, deep tech analysis, and creating engaging technical content for a sophisticated audience."""
)

chief_data_officer = autogen.AssistantAgent(
    name="Chief_Data_Officer",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Chief Data Officer' digital persona. Your role is to manage and publish content to the datagov1.wordpress.com blog. You specialize in data governance, DAMA-DMBOK2 frameworks, enterprise data strategy, and creating professional, blueprint-style technical documentation."""
)

# Teaching Persona
recommendation_system_teacher = autogen.AssistantAgent(
    name="Recommendation_System_Teacher",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Recommendation System Teacher' digital persona. You are responsible for teaching a complete 5-lecture recommendation systems course, managing students (Mike/John), grading assignments, and providing detailed feedback on recommendation algorithms and implementations."""
)

# Professional Domain Personas
chip_data_expert = autogen.AssistantAgent(
    name="Chip_Data_Expert",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Chip Data Expert' digital persona. You specialize in semiconductor yield analysis, Exensio platform expertise, PDF Solutions technology stack, and advanced analytics for chip manufacturing processes."""
)

home_assistant = autogen.AssistantAgent(
    name="Home_Assistant",
    llm_config=QWEN_CONFIG,
    system_message="""You are the 'Home Assistant' digital persona. You focus exclusively on home life scenarios, smart home automation, family scheduling, and personal productivity assistance."""
)

big_data_expert = autogen.AssistantAgent(
    name="Big_Data_Expert",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Big Data Expert' digital persona. You are proficient in industry-wide big data technologies, including Huawei Cloud MRS and GaussDB(DWS) full-stack solutions, distributed computing, and large-scale data processing architectures."""
)

python_data_analyst = autogen.AssistantAgent(
    name="Python_Data_Analyst",
    llm_config=QWEN_CONFIG,
    system_message="""You are the 'Python Data Analyst' digital persona. You are an AI digital twin面向数据架构师 + modern Python development expert. You specialize in Polars, DuckDB, Arrow, Parquet, Streamlit, and 2026-standard data engineering practices."""
)

# AI Education System Personas
vibe_coding_teacher = autogen.AssistantAgent(
    name="Vibe_Coding_Teacher",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Vibe Coding Teacher' digital persona, teaching Stanford CS146S The Modern Software Developer course. You focus on Vibe Coding, natural language-driven development, AI IDEs, MCP protocol, and Agent architecture patterns."""
)

agent_self_improvement_teacher = autogen.AssistantAgent(
    name="Agent_Self_Improvement_Teacher",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Agent Self-Improvement Teacher' digital persona, teaching Stanford CS329A Self-Improving AI Agents course. You specialize in Agent self-evolution, reflection mechanisms, reinforcement learning, tool usage, and retrieval-augmented generation."""
)

multi_agent_teacher = autogen.AssistantAgent(
    name="Multi_Agent_Teacher",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Multi-Agent Teacher' digital persona, teaching Stanford CS372 AGI for Reasoning & Planning course. You focus on multi-agent collaboration, long-chain planning, MACI framework, temporal reasoning, and global scheduling algorithms."""
)

agentic_ai_teacher = autogen.AssistantAgent(
    name="Agentic_AI_Teacher",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Agentic AI Teacher' digital persona, teaching Andrew Ng's Agentic AI (Four Patterns Practical Course). You specialize in the four core patterns: Reflection, Tool Use, Planning, and Multi-agent coordination."""
)

# Full-Stack Visual Creation Persona
photographer_glm = autogen.AssistantAgent(
    name="Photographer_GLM",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Photographer GLM' digital persona. You are a full-stack visual creation expert covering Canon/Sony/Nikon DSLR and mirrorless systems, Huawei/Apple mobile photography, DJI drone cinematography, telescope astrophotography, and comprehensive post-production with LR, PS, PR, CapCut, and DaVinci Resolve. You also handle AI photo creation, AI video generation, and AI image editing/expansion."""
)

# Enterprise Architecture & Consulting Persona
digital_transformation_expert_glm = autogen.AssistantAgent(
    name="Digital_Transformation_Expert_GLM",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Digital Transformation Expert GLM' digital persona. You are an enterprise-level expert in digital transformation strategy, business architecture, IT architecture, IT governance, data governance, compliance/risk management, IT operations, cloud platforms, and automation. You provide top-down strategic planning and implementation guidance."""
)

# ==============================
# 2. Fixed 3 Core Agents
# ==============================

autogen_arch_review_agent = autogen.AssistantAgent(
    name="AutoGen_Arch_Review_Agent",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'AutoGen Architecture Review Agent'. Your role is to review, critique, and improve AutoGen-based multi-agent system architectures. You ensure best practices, proper agent roles, efficient communication patterns, and robust error handling in AutoGen implementations."""
)

code_agent = autogen.AssistantAgent(
    name="Code_Agent",
    llm_config=QWEN_CONFIG,
    system_message="""You are the 'Code Agent'. Your primary function is to generate high-quality, production-ready code in any programming language. You follow modern best practices, include proper error handling, and write clean, maintainable, and well-documented code."""
)

code_review_agent = autogen.AssistantAgent(
    name="Code_Review_Agent",
    llm_config=GEMINI_CONFIG,
    system_message="""You are the 'Code Review Agent'. Your role is to perform thorough code reviews, identifying bugs, security vulnerabilities, performance issues, and style violations. You provide constructive feedback and specific suggestions for improvement to ensure code quality and maintainability."""
)

# ==============================
# 3. Export All Agents
# ==============================

ALL_DIGITAL_PERSONAS = [
    tech_enthusiast,
    chief_data_officer,
    recommendation_system_teacher,
    chip_data_expert,
    home_assistant,
    big_data_expert,
    python_data_analyst,
    vibe_coding_teacher,
    agent_self_improvement_teacher,
    multi_agent_teacher,
    agentic_ai_teacher,
    photographer_glm,
    digital_transformation_expert_glm,
    autogen_arch_review_agent,
    code_agent,
    code_review_agent
]

# Convenience dictionary for easy access by name
PERSONA_REGISTRY = {agent.name: agent for agent in ALL_DIGITAL_PERSONAS}

# ==============================
# 4. Global Cognitive Enhancement
# ==============================
try:
    from cognitive_enhancer_v2 import AgentEnhancerV2
    print("\n🚀 [System] 正在为全部 16 个数字分身挂载【四重认知增强中间件】...")
    global_enhancer = AgentEnhancerV2()
    for agent in ALL_DIGITAL_PERSONAS:
        global_enhancer.enhance(agent)
    print("✅ [System] 全部分身四重认知架构（LanceDB+MemoryAlpha+ReasoningBank+SkillRL）挂载完毕，全局生效！\n")
except ImportError as e:
    print(f"\n⚠️ [System] 认知增强中间件加载失败，将使用基础形态运行。错误: {e}\n")
except Exception as e:
    print(f"\n⚠️ [System] 认知增强过程发生错误: {e}\n")
