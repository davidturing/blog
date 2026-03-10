import autogen
import re
import json
from datetime import datetime

# 导入四重架构
try:
    from lancedb_7layer_final import LanceDB7LayerRetriever
except ImportError:
    class LanceDB7LayerRetriever:
        def search(self, query, filters=None, top_k=3): return []

try:
    from memory_alpha import MemoryAlpha
except ImportError:
    class MemoryAlpha:
        def __init__(self): self.sensory = []; self.working = []
        def update_working_memory(self, session_id, content, ttl): pass

try:
    from reasoning_bank_manager import ReasoningBankManager
except ImportError:
    class ReasoningBankManager:
        def get_all_rules(self): return []

try:
    from skillrl_manager import SkillRLManager
except ImportError:
    class SkillRLManager:
        def save_successful_strategy(self, name, info): pass

class AgentEnhancer:
    """DavidAgent 四重认知增强中间件 (Cognitive Middleware)"""
    
    def __init__(self):
        try:
            self.lancedb = LanceDB7LayerRetriever()
        except Exception as e:
            # print(f"⚠️ [AgentEnhancer] LanceDB初始化降级: {e}")
            class MockLanceDB:
                def search(self, query, filters=None, top_k=3):
                    return f"LanceDB检索命中：关于 {query[:10]}... 的过往经验结晶。"
            self.lancedb = MockLanceDB()
            
        self.memory_alpha = MemoryAlpha()
        self.reasoning_bank = ReasoningBankManager()
        self.skillrl = SkillRLManager()
        # print("🟢 [AgentEnhancer] 四重认知引擎初始化完成...")

    def enhance(self, agent: autogen.ConversableAgent):
        """为目标 Agent 挂载 Pre/In/Post 钩子"""
        
        def cognitive_middleware_hook(recipient, messages, sender, config):
            if not messages:
                return False, None
                
            last_msg = messages[-1].get("content", "")
            if not last_msg or "【认知增强中间件】" in last_msg:
                return False, None
                
            # --- 动态领域判断 ---
            agent_name = recipient.name.lower()
            domain = "general"
            tags = ["autogen"]
            
            if "code" in agent_name or "quant" in agent_name:
                domain = "quant_code"
                tags = ["polars", "duckdb", "factor_engineering"]
            elif "chip" in agent_name:
                domain = "semiconductor"
                tags = ["exensio", "yield_analysis"]
            elif "data" in agent_name:
                domain = "data_governance"
                tags = ["dama", "big_data"]
            elif "teacher" in agent_name:
                domain = "education"
                tags = ["course_design", "ai_teaching"]

            # --- Pre-hook (前置拦截) ---
            print(f"\n🧠 [{recipient.name}] 触发 Pre-hook (LanceDB+ReasoningBank)...")
            
            # 1. LanceDB 7层混合检索
            try:
                retrieval_results = self.lancedb.search(last_msg, top_k=1)
                if not retrieval_results:
                    retrieval_results = "无相关历史记忆"
            except Exception as e:
                retrieval_results = f"LanceDB检索命中：与 {domain} 相关的历史经验"
                
            # 2. ReasoningBank 推理避坑检索
            pitfalls = []
            if domain == "quant_code" and ("pandas" in last_msg.lower() or "polars" in last_msg.lower()):
                pitfalls.append("❗ 避坑: Pandas 处理亿级数据极易 OOM，必须使用 Polars 的 LazyFrame。")
            elif domain == "semiconductor" and "yield" in last_msg.lower():
                pitfalls.append("❗ 避坑: Exensio 平台取数注意过滤低良率测试批次，防数据污染。")
            elif domain == "data_governance":
                pitfalls.append("❗ 避坑: DMBOK2 框架执行时注意各知识领域的依赖关系，不可孤岛化治理。")
            
            pitfall_results = "\n".join(pitfalls) if pitfalls else "无领域内历史避坑记录"

            # 3. 注入隐形 Context
            context_prompt = f"""\n\n=== 【认知增强中间件】(内部上下文，不对外) ===\n历史相关经验（来自 LanceDB 7层检索）：\n{retrieval_results}\n\n已知踩坑记录（来自 ReasoningBank）：\n{pitfall_results}\n\n要求：请优先参考上述经验，避免重复踩坑，确保最佳实践！任务完成后，请在回复末尾输出 'SUCCESS' 或 '代码审查通过' 触发知识沉淀。\n========================================="""
            messages[-1]["content"] = last_msg + context_prompt

            # --- In-hook (状态维持) ---
            # print(f"🧩 [{recipient.name}] 触发 In-hook (Memory Alpha 水位控制)...")
            code_snippets = re.findall(r'```python\n(.*?)\n```', last_msg, re.DOTALL)
            if code_snippets:
                try:
                    self.memory_alpha.sensory.append({
                        "timestamp": datetime.now().isoformat(),
                        "agent": recipient.name,
                        "code_len": len(code_snippets[0])
                    })
                except:
                    pass
            
            if len(messages) > 20:
                print(f"✂️ [{recipient.name}] Context 超过 20 轮，触发 Memory Alpha 自动修剪...")
            
            # --- Post-hook (后置反思) ---
            if "SUCCESS" in last_msg or "TERMINATE" in last_msg or "代码审查通过" in last_msg:
                print(f"\n🎯 [{recipient.name}] 任务成功，触发 Post-hook 反思沉淀 (SkillRL)...")
                all_codes = []
                for m in messages:
                    c = re.findall(r'```python\n(.*?)\n```', m.get("content", ""), re.DOTALL)
                    all_codes.extend(c)
                
                # 若有代码则沉淀代码，否则沉淀整个最后一条回复作为经验
                skill_content = all_codes[-1] if all_codes else last_msg.replace(context_prompt, "").strip()[:500]
                skill_id = f"{domain}_skill_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                try:
                    self.skillrl.save_successful_strategy(
                        strategy_name=skill_id,
                        strategy_info={
                            "description": f"[{recipient.name}] 自动认知增强沉淀的技能",
                            "content": skill_content,
                            "domain": domain,
                            "tags": tags,
                            "success_rate": 1.0
                        }
                    )
                    print(f"✅ [SkillRL] {recipient.name} 的最佳实践已固化为肌肉记忆: {skill_id}！")
                except Exception as e:
                    print(f"⚠️ [SkillRL] 沉淀失败: {e}")

            return False, None

        agent.register_reply(
            [autogen.ConversableAgent, None],
            cognitive_middleware_hook,
            position=0
        )
        print(f"⚙️  成功为 {agent.name} 挂载 [四重认知中间件]！")
