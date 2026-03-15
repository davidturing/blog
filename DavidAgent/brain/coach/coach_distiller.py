#!/usr/bin/env python3
"""
真·架构蒸馏引擎 - 稳定模型重建
只做真实可运行代码，无任何模拟或美化
"""

import asyncio
import json
import os
import time
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 真实的 API 客户端（需要安装相应库）
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    
try:
    import zhipuai
except ImportError:
    zhipuai = None


class TrueCoachDistiller:
    """真·架构蒸馏引擎"""
    
    def __init__(self, tech_repo_path: str = "/Users/zhaoqinhuang/github/tech"):
        self.tech_repo_path = Path(tech_repo_path)
        self.coach_dir = self.tech_repo_path / "architecture-coach"
        self.reasoning_bank_dir = self.coach_dir / "reasoning-bank"
        self.reasoning_bank_dir.mkdir(parents=True, exist_ok=True)
        
        # 从环境变量读取 API keys
        self.api_keys = self._load_api_keys()
        
        # 初始化真实 API 客户端
        self.gemini_client = self._init_gemini_client()
        self.qwen_client = self._init_qwen_client() 
        self.glm_client = self._init_glm_client()
        
        # 知识库路径
        self.knowledge_bases = {
            "L1_Skills": self.reasoning_bank_dir / "l1_skills",
            "L2_Reasoning": self.reasoning_bank_dir / "l2_reasoning",
            "Pitfalls": self.reasoning_bank_dir / "pitfalls", 
            "M4_Optimization": self.reasoning_bank_dir / "m4_optimization"
        }
        
        for kb_dir in self.knowledge_bases.values():
            kb_dir.mkdir(exist_ok=True)
            
    def _load_api_keys(self) -> Dict[str, str]:
        """从环境变量安全读取 API keys"""
        api_keys = {}
        
        # Gemini API Key
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            api_keys["gemini"] = gemini_key
        else:
            print("⚠️  GEMINI_API_KEY 环境变量未设置")
            
        # Qwen API Key (通过 DashScope)
        qwen_key = os.getenv("DASHSCOPE_API_KEY") 
        if qwen_key:
            api_keys["qwen"] = qwen_key
        else:
            print("⚠️  DASHSCOPE_API_KEY 环境变量未设置")
            
        # GLM API Key
        glm_key = os.getenv("ZHIPUAI_API_KEY")
        if glm_key:
            api_keys["glm"] = glm_key
        else:
            print("⚠️  ZHIPUAI_API_KEY 环境变量未设置")
            
        return api_keys
        
    def _init_gemini_client(self):
        """初始化 Gemini 客户端"""
        if not genai or "gemini" not in self.api_keys:
            return None
            
        try:
            genai.configure(api_key=self.api_keys["gemini"])
            return genai
        except Exception as e:
            print(f"❌ Gemini 客户端初始化失败: {e}")
            return None
            
    def _init_qwen_client(self):
        """初始化 Qwen 客户端"""
        if not OpenAI or "qwen" not in self.api_keys:
            return None
            
        try:
            client = OpenAI(
                api_key=self.api_keys["qwen"],
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            return client
        except Exception as e:
            print(f"❌ Qwen 客户端初始化失败: {e}")
            return None
            
    def _init_glm_client(self):
        """初始化 GLM 客户端"""
        if not zhipuai or "glm" not in self.api_keys:
            return None
            
        try:
            zhipuai.api_key = self.api_keys["glm"]
            return zhipuai
        except Exception as e:
            print(f"❌ GLM 客户端初始化失败: {e}")
            return None
            
    async def distill_architecture_knowledge(self, topic: str, context: str) -> Dict[str, Any]:
        """真实蒸馏架构知识"""
        print(f"🧠 启动真·架构蒸馏: {topic}")
        
        distillation_result = {
            "topic": topic,
            "distillation_id": f"true_distill_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "model_outputs": {},
            "raw_responses": {},
            "consensus_score": 0.0,
            "knowledge_extracted": {},
            "status": "pending",
            "errors": []
        }
        
        # 并行调用三大真实模型
        tasks = []
        if self.gemini_client:
            tasks.append(self._call_gemini_real(topic, context))
        else:
            distillation_result["errors"].append("Gemini 客户端不可用")
            
        if self.qwen_client:
            tasks.append(self._call_qwen_real(topic, context))
        else:
            distillation_result["errors"].append("Qwen 客户端不可用")
            
        if self.glm_client:
            tasks.append(self._call_glm_real(topic, context))
        else:
            distillation_result["errors"].append("GLM 客户端不可用")
            
        if not tasks:
            distillation_result["status"] = "failed"
            distillation_result["errors"].append("所有模型客户端都不可用")
            return distillation_result
            
        try:
            # 执行真实模型调用（带超时）
            results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=60)
            
            # 处理结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_msg = f"模型调用异常: {str(result)}"
                    print(f"❌ {error_msg}")
                    distillation_result["errors"].append(error_msg)
                    continue
                    
                model_name, output, raw_response = result
                distillation_result["model_outputs"][model_name] = output
                distillation_result["raw_responses"][model_name] = raw_response
                
        except asyncio.TimeoutError:
            error_msg = "模型调用超时 (60秒)"
            print(f"❌ {error_msg}")
            distillation_result["errors"].append(error_msg)
            distillation_result["status"] = "timeout"
            return distillation_result
            
        except Exception as e:
            error_msg = f"蒸馏过程异常: {str(e)}"
            print(f"❌ {error_msg}")
            distillation_result["errors"].append(error_msg)
            distillation_result["status"] = "error"
            return distillation_result
            
        # 提取结构化知识（仅从成功调用的模型）
        if distillation_result["model_outputs"]:
            extracted_knowledge = await self._extract_structured_knowledge_real(
                distillation_result["model_outputs"]
            )
            distillation_result["knowledge_extracted"] = extracted_knowledge
            
            # 计算真实共识得分
            consensus_score = await self._calculate_real_consensus_score(extracted_knowledge)
            distillation_result["consensus_score"] = consensus_score
            
            # 保存原始响应（可审计）
            await self._save_raw_responses(distillation_result)
            
            # 知识固化
            if consensus_score > 0:
                distillation_result["status"] = "completed"
                await self._consolidate_knowledge_real(extracted_knowledge, distillation_result["distillation_id"])
            else:
                distillation_result["status"] = "no_consensus"
                
        else:
            distillation_result["status"] = "no_model_outputs"
            
        return distillation_result
        
    async def _call_gemini_real(self, topic: str, context: str):
        """真实调用 Gemini 3.1 Pro"""
        print("🔍 调用 Gemini 3.1 Pro...")
        
        prompt = f"""
        你是一个架构师，需要为以下架构课题提供全局架构推理：

        课题: {topic}
        上下文: {context}

        请严格按照以下JSON格式输出：
        {{
            "L2_Reasoning": [
                {{
                    "reasoning_path": "详细的推理路径",
                    "sop_steps": ["步骤1", "步骤2", "步骤3"],
                    "tradeoffs": ["权衡点1", "权衡点2"], 
                    "long_term_vision": "长期架构愿景",
                    "confidence": 0.0-1.0
                }}
            ]
        }}
        """
        
        try:
            model = self.gemini_client.GenerativeModel('gemini-3.1-pro')
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            if hasattr(response, 'text'):
                output_text = response.text
            else:
                output_text = str(response)
                
            # 解析 JSON
            try:
                output_json = json.loads(output_text)
            except json.JSONDecodeError:
                # 如果不是有效JSON，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
                if json_match:
                    output_json = json.loads(json_match.group())
                else:
                    raise ValueError(f"无法解析 Gemini 响应为 JSON: {output_text[:200]}...")
                    
            return "gemini", output_json, output_text
            
        except Exception as e:
            error_msg = f"Gemini 调用失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    async def _call_qwen_real(self, topic: str, context: str):
        """真实调用 Qwen 2.5 Coder"""
        print("🔍 调用 Qwen 2.5 Coder...")
        
        prompt = f"""
        你是一个代码专家，需要为以下架构课题提供原子代码技能：

        课题: {topic}
        上下文: {context}

        请严格按照以下JSON格式输出：
        {{
            "L1_Skills": [
                {{
                    "skill_name": "技能名称",
                    "code_snippet": "完整的可运行代码",
                    "api_practices": ["最佳实践1", "最佳实践2"],
                    "confidence": 0.0-1.0
                }}
            ]
        }}
        """
        
        try:
            response = await asyncio.to_thread(
                self.qwen_client.chat.completions.create,
                model="qwen-2.5-coder",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            output_text = response.choices[0].message.content
            
            # 解析 JSON
            try:
                output_json = json.loads(output_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
                if json_match:
                    output_json = json.loads(json_match.group())
                else:
                    raise ValueError(f"无法解析 Qwen 响应为 JSON: {output_text[:200]}...")
                    
            return "qwen", output_json, output_text
            
        except Exception as e:
            error_msg = f"Qwen 调用失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    async def _call_glm_real(self, topic: str, context: str):
        """真实调用 GLM 5"""
        print("🔍 调用 GLM 5...")
        
        prompt = f"""
        你是一个严谨的系统工程师，需要为以下架构课题提供避坑指南和M4优化建议：

        课题: {topic}
        上下文: {context}

        请严格按照以下JSON格式输出：
        {{
            "Pitfalls": [
                {{
                    "pitfall_description": "详细的陷阱描述",
                    "boundary_conditions": ["边界条件1", "边界条件2"],
                    "mitigation_strategy": "缓解策略",
                    "confidence": 0.0-1.0
                }}
            ],
            "M4_Optimization": [
                {{
                    "optimization_target": "优化目标",
                    "m4_specific_technique": "Apple Silicon 专用技术",
                    "performance_gain": "性能提升描述",
                    "memory_savings": "内存节省描述",
                    "confidence": 0.0-1.0
                }}
            ]
        }}
        """
        
        try:
            response = await asyncio.to_thread(
                self.glm_client.model_api.invoke,
                model="glm-5",
                prompt=prompt,
                temperature=0.1,
                max_tokens=1000
            )
            
            if 'data' in response and 'choices' in response['data']:
                output_text = response['data']['choices'][0]['content']
            else:
                output_text = str(response)
                
            # 解析 JSON
            try:
                output_json = json.loads(output_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
                if json_match:
                    output_json = json.loads(json_match.group())
                else:
                    raise ValueError(f"无法解析 GLM 响应为 JSON: {output_text[:200]}...")
                    
            return "glm", output_json, output_text
            
        except Exception as e:
            error_msg = f"GLM 调用失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    async def _extract_structured_knowledge_real(self, model_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """从真实模型输出提取结构化知识"""
        knowledge = {
            "L1_Skills": [],
            "L2_Reasoning": [], 
            "Pitfalls": [],
            "M4_Optimization": []
        }
        
        for model_name, output in model_outputs.items():
            if model_name == "qwen" and "L1_Skills" in output:
                knowledge["L1_Skills"].extend(output["L1_Skills"])
            elif model_name == "gemini" and "L2_Reasoning" in output:
                knowledge["L2_Reasoning"].extend(output["L2_Reasoning"])
            elif model_name == "glm":
                if "Pitfalls" in output:
                    knowledge["Pitfalls"].extend(output["Pitfalls"])
                if "M4_Optimization" in output:
                    knowledge["M4_Optimization"].extend(output["M4_Optimization"])
                    
        return knowledge
        
    async def _calculate_real_consensus_score(self, knowledge: Dict[str, Any]) -> float:
        """计算真实共识得分"""
        # 只有当所有4个知识类别都有内容时才计算共识
        complete_categories = sum(1 for cat in ["L1_Skills", "L2_Reasoning", "Pitfalls", "M4_Optimization"] 
                                if len(knowledge.get(cat, [])) > 0)
        
        if complete_categories == 4:
            # 计算平均置信度
            all_confidences = []
            for category in knowledge.values():
                for item in category:
                    if isinstance(item, dict) and "confidence" in item:
                        all_confidences.append(item["confidence"])
                        
            if all_confidences:
                avg_confidence = sum(all_confidences) / len(all_confidences)
                return round(avg_confidence, 3)
                
        return 0.0
        
    async def _save_raw_responses(self, distillation_result: Dict[str, Any]):
        """保存原始响应用于审计"""
        raw_dir = self.reasoning_bank_dir / "raw_responses"
        raw_dir.mkdir(exist_ok=True)
        
        raw_file = raw_dir / f"{distillation_result['distillation_id']}_raw.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(distillation_result["raw_responses"], f, indent=2, ensure_ascii=False)
            
    async def _consolidate_knowledge_real(self, knowledge: Dict[str, Any], distillation_id: str):
        """真实固化知识"""
        # 保存 JSON
        json_path = self.reasoning_bank_dir / f"{distillation_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
            
        # 保存 Markdown
        md_path = self.reasoning_bank_dir / f"{distillation_id}.md"
        md_content = self._generate_real_markdown(knowledge, distillation_id)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
    def _generate_real_markdown(self, knowledge: Dict[str, Any], distillation_id: str) -> str:
        """生成真实 Markdown 摘要"""
        md = f"# 真·架构知识蒸馏摘要\n\n"
        md += f"**蒸馏ID**: {distillation_id}\n"
        md += f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for category, items in knowledge.items():
            if items:
                md += f"## {category}\n\n"
                for item in items:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key != "confidence":
                                if isinstance(value, list):
                                    md += f"- **{key}**:\n"
                                    for v in value:
                                        md += f"  - {v}\n"
                                else:
                                    md += f"- **{key}**: {value}\n"
                        md += "\n"
                        
        return md


async def main():
    """主函数 - 可直接运行"""
    print("🚀 启动真·架构蒸馏引擎...")
    
    # 创建蒸馏引擎
    distiller = TrueCoachDistiller()
    
    # MCP 架构自愈课题
    topic = "MCP架构自愈"
    context = """
    MCP (Model Context Protocol) 标准化中枢需要实现自动错误检测和修复能力。
    关键要求包括：只读模式安全、内存熔断保护、查询验证、分身权限控制。
    需要在 Mac mini M4 环境下运行，内存限制 < 100MB。
    架构教练需要能够自动校验和修复 MCP 组件的问题。
    """
    
    # 执行真实蒸馏
    result = await distiller.distill_architecture_knowledge(topic, context)
    
    # 输出真实结果
    print("\n" + "="*60)
    print("📊 真·架构蒸馏结果")
    print("="*60)
    print(f"状态: {result['status']}")
    print(f"共识得分: {result['consensus_score']}")
    print(f"蒸馏ID: {result['distillation_id']}")
    print(f"错误数: {len(result['errors'])}")
    
    if result['errors']:
        print("\n❌ 错误详情:")
        for error in result['errors']:
            print(f"  - {error}")
            
    if result['knowledge_extracted']:
        print(f"\n✅ 提取知识类别: {list(result['knowledge_extracted'].keys())}")
        
    print(f"\n📁 ReasoningBank 路径: {distiller.reasoning_bank_dir}")
    
    return result


if __name__ == "__main__":
    # 检查必要的依赖
    missing_deps = []
    try:
        import google.generativeai
    except ImportError:
        missing_deps.append("google-generativeai")
        
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
        
    try:
        import zhipuai
    except ImportError:
        missing_deps.append("zhipuai")
        
    if missing_deps:
        print(f"❌ 缺少必要依赖: {', '.join(missing_deps)}")
        print("请运行: pip install " + " ".join(missing_deps))
        exit(1)
        
    # 检查环境变量
    required_envs = ["GEMINI_API_KEY", "DASHSCOPE_API_KEY", "ZHIPUAI_API_KEY"]
    missing_envs = [env for env in required_envs if not os.getenv(env)]
    
    if missing_envs:
        print(f"⚠️  缺少环境变量: {', '.join(missing_envs)}")
        print("请设置相应的 API keys")
        
    # 运行主函数
    asyncio.run(main())