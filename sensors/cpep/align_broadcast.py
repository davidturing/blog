"""
CPEP (Cross-Persona Experience Protocol) 跨分身经验对齐协议实现。

新技能验证通过后自动全分身广播，按类型转译：
科技达人（科普）、技术专家（代码）、架构师（设计思想）。
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class CPEPAlign:
    """CPEP 跨分身对齐器。"""

    def __init__(self, config: Dict[str, Any]):
        """初始化 CPEP 对齐器。
        
        Args:
            config: 配置字典，包含 avatar_types 等参数。
        """
        self.logger = logging.getLogger("CPEPAlign")
        self.config = config
        self.avatar_types = config.get("avatar_types", [])
        self.broadcast_delay_seconds = config.get("broadcast_delay_seconds", 5)
        
        # Define translation templates for each avatar type
        self.translation_templates = {
            "tech_blogger": self._translate_for_tech_blogger,
            "chief_data_officer": self._translate_for_chief_data_officer,
            "vibe_coding_teacher": self._translate_for_vibe_coding_teacher,
            "agent_self_improvement_teacher": self._translate_for_agent_self_improvement_teacher,
            "multi_agent_teacher": self._translate_for_multi_agent_teacher,
            "big_data_expert": self._translate_for_big_data_expert,
            "recommendation_system_teacher": self._translate_for_recommendation_system_teacher,
            "chip_data_expert": self._translate_for_chip_data_expert,
            "home_assistant": self._translate_for_home_assistant,
            "agentic_ai_teacher": self._translate_for_agentic_ai_teacher,
            "python_data_analyst": self._translate_for_python_data_analyst,
            "photographer_glm": self._translate_for_photographer_glm,
            "digital_transformation_expert_glm": self._translate_for_digital_transformation_expert_glm
        }

    def broadcast(self, distilled_knowledge: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """广播经验到所有分身。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            广播结果字典。
        """
        self.logger.info(f"Broadcasting experience for task {distilled_knowledge.get('task_id', 'unknown')}")
        
        broadcast_results = {}
        
        # Determine if the knowledge is valid for broadcasting
        is_valid = validation_result.get("success", False)
        
        for avatar_type in self.avatar_types:
            try:
                if is_valid:
                    # Translate for valid knowledge
                    translated_content = self.translate_for_avatar(
                        avatar_type, 
                        distilled_knowledge, 
                        validation_result
                    )
                    
                    # Store the translated content (in real implementation, this would be sent to the avatar)
                    broadcast_results[avatar_type] = {
                        "status": "success",
                        "content": translated_content,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.logger.debug(f"Successfully translated for {avatar_type}")
                    
                else:
                    # For invalid knowledge, send error information
                    error_content = self._create_error_notification(
                        avatar_type, 
                        distilled_knowledge, 
                        validation_result
                    )
                    
                    broadcast_results[avatar_type] = {
                        "status": "error_notification",
                        "content": error_content,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.logger.debug(f"Sent error notification to {avatar_type}")
                    
            except Exception as e:
                self.logger.error(f"Error broadcasting to {avatar_type}: {e}")
                broadcast_results[avatar_type] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                
        return {
            "broadcast_id": self._generate_broadcast_id(distilled_knowledge),
            "task_id": distilled_knowledge.get("task_id", "unknown"),
            "total_avatars": len(self.avatar_types),
            "successful_broadcasts": sum(1 for r in broadcast_results.values() if r["status"] == "success"),
            "error_notifications": sum(1 for r in broadcast_results.values() if r["status"] == "error_notification"),
            "failed_broadcasts": sum(1 for r in broadcast_results.values() if r["status"] == "failed"),
            "details": broadcast_results
        }

    def _generate_broadcast_id(self, distilled_knowledge: Dict[str, Any]) -> str:
        """生成广播 ID。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            广播 ID 字符串。
        """
        import hashlib
        task_id = distilled_knowledge.get("task_id", "unknown")
        timestamp = datetime.now().isoformat()
        broadcast_string = f"{task_id}:{timestamp}"
        return hashlib.md5(broadcast_string.encode()).hexdigest()

    def translate_for_avatar(self, avatar_type: str, distilled_knowledge: Dict[str, Any], 
                           validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为特定分身类型翻译知识。
        
        Args:
            avatar_type: 分身类型。
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            翻译后的内容字典。
        """
        if avatar_type not in self.translation_templates:
            self.logger.warning(f"No translation template for avatar type: {avatar_type}")
            # Use default translation
            return self._translate_default(avatar_type, distilled_knowledge, validation_result)
            
        translation_func = self.translation_templates[avatar_type]
        return translation_func(distilled_knowledge, validation_result)

    def _translate_for_tech_blogger(self, distilled_knowledge: Dict[str, Any], 
                                   validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为科技达人分身翻译（科普风格）。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            翻译后的内容字典。
        """
        core_logic = distilled_knowledge.get("core_logic", {})
        right_brain = core_logic.get("right_brain", {})
        
        return {
            "persona": "tech_blogger",
            "content_type": "blog_post",
            "title": f"【技术洞察】{distilled_knowledge.get('title', 'New Technology Insight')}",
            "summary": self._extract_summary(right_brain),
            "main_content": self._create_blog_content(distilled_knowledge, right_brain),
            "key_takeaways": self._extract_key_takeaways(right_brain),
            "technical_depth": "intermediate",
            "audience": "tech_enthusiasts",
            "publish_ready": True,
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _extract_summary(self, right_brain: Dict[str, Any]) -> str:
        """从右脑分析中提取摘要。
        
        Args:
            right_brain: 右脑分析结果。
            
        Returns:
            摘要字符串。
        """
        key_insights = right_brain.get("key_insights", [])
        if key_insights:
            return key_insights[0][:200] + "..." if len(key_insights[0]) > 200 else key_insights[0]
            
        pain_points = right_brain.get("core_pain_points", [])
        if pain_points:
            return f"解决 {pain_points[0][:100]}..." if len(pain_points[0]) > 100 else pain_points[0]
            
        return "新技术洞察摘要"

    def _create_blog_content(self, distilled_knowledge: Dict[str, Any], 
                            right_brain: Dict[str, Any]) -> str:
        """创建博客主要内容。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            right_brain: 右脑分析结果。
            
        Returns:
            博客内容字符串。
        """
        content = []
        
        # Introduction
        content.append(f"## 技术背景\n\n{distilled_knowledge.get('title', '新技术介绍')}")
        
        # Pain points
        pain_points = right_brain.get("core_pain_points", [])
        if pain_points:
            content.append("\n## 核心痛点\n")
            for point in pain_points[:3]:
                content.append(f"- {point}")
                
        # Applicable scenarios
        scenarios = right_brain.get("applicable_scenarios", [])
        if scenarios:
            content.append("\n## 适用场景\n")
            for scenario in scenarios[:3]:
                content.append(f"- {scenario}")
                
        # Capability boundaries
        boundaries = right_brain.get("capability_boundaries", [])
        if boundaries:
            content.append("\n## 能力边界\n")
            for boundary in boundaries[:3]:
                content.append(f"- {boundary}")
                
        # Key insights
        insights = right_brain.get("key_insights", [])
        if insights:
            content.append("\n## 关键洞察\n")
            for insight in insights:
                content.append(f"- {insight}")
                
        return "\n".join(content)

    def _extract_key_takeaways(self, right_brain: Dict[str, Any]) -> List[str]:
        """提取关键要点。
        
        Args:
            right_brain: 右脑分析结果。
            
        Returns:
            要点列表。
        """
        takeaways = []
        
        # Add pain points
        pain_points = right_brain.get("core_pain_points", [])
        takeaways.extend([f"痛点: {p[:50]}..." if len(p) > 50 else f"痛点: {p}" for p in pain_points[:2]])
        
        # Add scenarios
        scenarios = right_brain.get("applicable_scenarios", [])
        takeaways.extend([f"场景: {s[:50]}..." if len(s) > 50 else f"场景: {s}" for s in scenarios[:2]])
        
        # Add boundaries
        boundaries = right_brain.get("capability_boundaries", [])
        takeaways.extend([f"边界: {b[:50]}..." if len(b) > 50 else f"边界: {b}" for b in boundaries[:2]])
        
        return takeaways[:5]  # Limit to 5 takeaways

    def _translate_for_chief_data_officer(self, distilled_knowledge: Dict[str, Any], 
                                         validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为首席数据官分身翻译（数据治理风格）。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            翻译后的内容字典。
        """
        core_logic = distilled_knowledge.get("core_logic", {})
        left_brain = core_logic.get("left_brain", {})
        right_brain = core_logic.get("right_brain", {})
        
        return {
            "persona": "chief_data_officer",
            "content_type": "data_governance_note",
            "title": f"数据治理洞察: {distilled_knowledge.get('title', 'New Data Insight')}",
            "data_quality_impact": self._assess_data_quality_impact(right_brain),
            "governance_considerations": self._extract_governance_considerations(right_brain),
            "implementation_risks": self._extract_implementation_risks(right_brain),
            "compliance_notes": self._generate_compliance_notes(),
            "technical_specifications": left_brain.get("structure", {}),
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _assess_data_quality_impact(self, right_brain: Dict[str, Any]) -> str:
        """评估对数据质量的影响。
        
        Args:
            right_brain: 右脑分析结果。
            
        Returns:
            影响描述字符串。
        """
        pain_points = right_brain.get("core_pain_points", [])
        if pain_points:
            return f"可能改善数据质量问题: {pain_points[0][:100]}..."
            
        return "需要进一步评估数据质量影响"

    def _extract_governance_considerations(self, right_brain: Dict[str, Any]) -> List[str]:
        """提取治理考虑因素。
        
        Args:
            right_brain: 右脑分析结果。
            
        Returns:
            治理考虑因素列表。
        """
        boundaries = right_brain.get("capability_boundaries", [])
        scenarios = right_brain.get("applicable_scenarios", [])
        
        considerations = []
        considerations.extend([f"边界限制: {b[:80]}..." if len(b) > 80 else f"边界限制: {b}" for b in boundaries[:2]])
        considerations.extend([f"适用场景: {s[:80]}..." if len(s) > 80 else f"适用场景: {s}" for s in scenarios[:2]])
        
        return considerations

    def _extract_implementation_risks(self, right_brain: Dict[str, Any]) -> List[str]:
        """提取实施风险。
        
        Args:
            right_brain: 右脑分析结果。
            
        Returns:
            风险列表。
        """
        pain_points = right_brain.get("core_pain_points", [])
        boundaries = right_brain.get("capability_boundaries", [])
        
        risks = []
        risks.extend([f"痛点风险: {p[:80]}..." if len(p) > 80 else f"痛点风险: {p}" for p in pain_points[:2]])
        risks.extend([f"能力限制风险: {b[:80]}..." if len(b) > 80 else f"能力限制风险: {b}" for b in boundaries[:2]])
        
        return risks

    def _generate_compliance_notes(self) -> str:
        """生成合规性说明。
        
        Returns:
            合规性说明字符串。
        """
        return "需评估 GDPR、CCPA 等数据隐私法规合规性。建议进行数据保护影响评估(DPIA)。"

    def _translate_for_vibe_coding_teacher(self, distilled_knowledge: Dict[str, Any], 
                                          validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为 Vibe Coding 老师分身翻译（教学风格）。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            翻译后的内容字典。
        """
        core_logic = distilled_knowledge.get("core_logic", {})
        left_brain = core_logic.get("left_brain", {})
        right_brain = core_logic.get("right_brain", {})
        
        return {
            "persona": "vibe_coding_teacher",
            "content_type": "coding_lesson",
            "title": f"Vibe Coding 课程: {distilled_knowledge.get('title', 'New Coding Concept')}",
            "learning_objectives": self._extract_learning_objectives(right_brain),
            "code_examples": left_brain.get("code_blocks", [])[:3],
            "step_by_step_guide": left_brain.get("execution_steps", []),
            "common_pitfalls": right_brain.get("core_pain_points", []),
            "best_practices": self._extract_best_practices(right_brain),
            "exercise_suggestions": self._generate_exercise_suggestions(left_brain, right_brain),
            "difficulty_level": "intermediate",
            "estimated_time": "30-45 minutes",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _extract_learning_objectives(self, right_brain: Dict[str, Any]) -> List[str]:
        """提取学习目标。
        
        Args:
            right_brain: 右脑分析结果。
            
        Returns:
            学习目标列表。
        """
        insights = right_brain.get("key_insights", [])
        scenarios = right_brain.get("applicable_scenarios", [])
        
        objectives = []
        objectives.extend([f"理解: {i[:60]}..." if len(i) > 60 else f"理解: {i}" for i in insights[:2]])
        objectives.extend([f"掌握: {s[:60]}..." if len(s) > 60 else f"掌握: {s}" for s in scenarios[:2]])
        
        return objectives

    def _extract_best_practices(self, right_brain: Dict[str, Any]) -> List[str]:
        """提取最佳实践。
        
        Args:
            right_brain: 右脑分析结果。
            
        Returns:
            最佳实践列表。
        """
        boundaries = right_brain.get("capability_boundaries", [])
        insights = right_brain.get("key_insights", [])
        
        practices = []
        practices.extend([f"注意边界: {b[:70]}..." if len(b) > 70 else f"注意边界: {b}" for b in boundaries[:2]])
        practices.extend([f"关键洞察: {i[:70]}..." if len(i) > 70 else f"关键洞察: {i}" for i in insights[:2]])
        
        return practices

    def _generate_exercise_suggestions(self, left_brain: Dict[str, Any], 
                                      right_brain: Dict[str, Any]) -> List[str]:
        """生成练习建议。
        
        Args:
            left_brain: 左脑分析结果。
            right_brain: 右脑分析结果。
            
        Returns:
            练习建议列表。
        """
        code_blocks = left_brain.get("code_blocks", [])
        pain_points = right_brain.get("core_pain_points", [])
        
        exercises = []
        if code_blocks:
            exercises.append("修改提供的代码示例以解决特定问题")
        if pain_points:
            exercises.append(f"针对 '{pain_points[0][:50]}...' 设计解决方案")
        exercises.append("实现一个完整的端到端示例")
        exercises.append("编写单元测试验证功能正确性")
        
        return exercises[:3]

    def _translate_for_agent_self_improvement_teacher(self, distilled_knowledge: Dict[str, Any], 
                                                     validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为 Agent 自进化老师分身翻译（强化学习风格）。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            翻译后的内容字典。
        """
        return {
            "persona": "agent_self_improvement_teacher",
            "content_type": "rl_curriculum",
            "title": f"Agent 自进化课程: {distilled_knowledge.get('title', 'New RL Concept')}",
            "reward_function_design": self._design_reward_function(distilled_knowledge),
            "exploration_strategy": self._suggest_exploration_strategy(distilled_knowledge),
            "policy_improvement": self._suggest_policy_improvement(distilled_knowledge),
            "meta_learning_opportunities": self._identify_meta_learning_opportunities(distilled_knowledge),
            "failure_analysis": validation_result.get("error_trace", "") if not validation_result.get("success", False) else "",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified" if validation_result.get("success", False) else "needs_improvement"
        }

    def _design_reward_function(self, distilled_knowledge: Dict[str, Any]) -> str:
        """设计奖励函数。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            奖励函数描述字符串。
        """
        right_brain = distilled_knowledge.get("core_logic", {}).get("right_brain", {})
        pain_points = right_brain.get("core_pain_points", [])
        
        if pain_points:
            return f"奖励函数应鼓励解决: {pain_points[0][:100]}..."
            
        return "需要基于具体应用场景设计奖励函数"

    def _suggest_exploration_strategy(self, distilled_knowledge: Dict[str, Any]) -> str:
        """建议探索策略。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            探索策略描述字符串。
        """
        boundaries = distilled_knowledge.get("core_logic", {}).get("right_brain", {}).get("capability_boundaries", [])
        
        if boundaries:
            return f"探索策略应避免: {boundaries[0][:100]}..."
            
        return "建议使用好奇心驱动的探索策略"

    def _suggest_policy_improvement(self, distilled_knowledge: Dict[str, Any]) -> str:
        """建议策略改进。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            策略改进建议字符串。
        """
        insights = distilled_knowledge.get("core_logic", {}).get("right_brain", {}).get("key_insights", [])
        
        if insights:
            return f"策略改进应基于: {insights[0][:100]}..."
            
        return "需要分析成功案例以改进策略"

    def _identify_meta_learning_opportunities(self, distilled_knowledge: Dict[str, Any]) -> List[str]:
        """识别元学习机会。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            元学习机会列表。
        """
        return [
            "跨领域知识迁移",
            "失败模式学习",
            "探索效率优化",
            "奖励函数自适应"
        ]

    def _translate_for_multi_agent_teacher(self, distilled_knowledge: Dict[str, Any], 
                                          validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为多智能体老师分身翻译（协同规划风格）。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            翻译后的内容字典。
        """
        return {
            "persona": "multi_agent_teacher",
            "content_type": "multi_agent_coordination",
            "title": f"多智能体协同: {distilled_knowledge.get('title', 'New Coordination Pattern')}",
            "coordination_protocol": self._design_coordination_protocol(distilled_knowledge),
            "role_assignment": self._suggest_role_assignment(distilled_knowledge),
            "communication_patterns": self._identify_communication_patterns(distilled_knowledge),
            "conflict_resolution": self._suggest_conflict_resolution(distilled_knowledge),
            "scalability_considerations": self._assess_scalability(distilled_knowledge),
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _design_coordination_protocol(self, distilled_knowledge: Dict[str, Any]) -> str:
        """设计协调协议。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            协调协议描述字符串。
        """
        return "基于任务分解和角色专业化设计协调协议"

    def _suggest_role_assignment(self, distilled_knowledge: Dict[str, Any]) -> str:
        """建议角色分配。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            角色分配建议字符串。
        """
        left_brain = distilled_knowledge.get("core_logic", {}).get("left_brain", {})
        code_blocks = left_brain.get("code_blocks", [])
        
        if code_blocks:
            return "根据代码模块功能分配角色"
            
        return "基于能力互补原则分配角色"

    def _identify_communication_patterns(self, distilled_knowledge: Dict[str, Any]) -> List[str]:
        """识别通信模式。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            通信模式列表。
        """
        return [
            "发布-订阅模式",
            "请求-响应模式",
            "广播模式",
            "点对点模式"
        ]

    def _suggest_conflict_resolution(self, distilled_knowledge: Dict[str, Any]) -> str:
        """建议冲突解决。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            冲突解决建议字符串。
        """
        pain_points = distilled_knowledge.get("core_logic", {}).get("right_brain", {}).get("core_pain_points", [])
        
        if pain_points:
            return f"冲突解决应关注: {pain_points[0][:100]}..."
            
        return "建议使用优先级仲裁机制"

    def _assess_scalability(self, distilled_knowledge: Dict[str, Any]) -> str:
        """评估可扩展性。
        
        Args:
            distilled_knowledge: 蒸馏后的知识。
            
        Returns:
            可扩展性评估字符串。
        """
        boundaries = distilled_knowledge.get("core_logic", {}).get("right_brain", {}).get("capability_boundaries", [])
        
        if boundaries:
            return f"可扩展性受限于: {boundaries[0][:100]}..."
            
        return "需要压力测试验证可扩展性"

    # Additional translation methods for other avatar types
    def _translate_for_big_data_expert(self, distilled_knowledge: Dict[str, Any], 
                                      validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为大数据专家分身翻译。"""
        return {
            "persona": "big_data_expert",
            "content_type": "big_data_solution",
            "title": f"大数据解决方案: {distilled_knowledge.get('title', 'New Big Data Insight')}",
            "data_pipeline_design": "基于蒸馏知识设计数据管道",
            "processing_framework": "选择合适的处理框架",
            "storage_optimization": "存储优化建议",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_for_recommendation_system_teacher(self, distilled_knowledge: Dict[str, Any], 
                                                    validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为推荐系统老师分身翻译。"""
        return {
            "persona": "recommendation_system_teacher",
            "content_type": "recsys_lesson",
            "title": f"推荐系统课程: {distilled_knowledge.get('title', 'New RecSys Concept')}",
            "algorithm_adaptation": "算法适配建议",
            "evaluation_metrics": "评估指标建议",
            "cold_start_solution": "冷启动解决方案",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_for_chip_data_expert(self, distilled_knowledge: Dict[str, Any], 
                                       validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为芯片数据专家分身翻译。"""
        return {
            "persona": "chip_data_expert",
            "content_type": "semiconductor_analysis",
            "title": f"半导体数据分析: {distilled_knowledge.get('title', 'New Semiconductor Insight')}",
            "yield_analysis": "良率分析建议",
            "process_optimization": "工艺优化建议",
            "defect_classification": "缺陷分类方法",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_for_home_assistant(self, distilled_knowledge: Dict[str, Any], 
                                     validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为家庭助理分身翻译。"""
        return {
            "persona": "home_assistant",
            "content_type": "home_automation",
            "title": f"家庭自动化: {distilled_knowledge.get('title', 'New Home Automation Feature')}",
            "practical_application": "实际应用场景",
            "setup_instructions": "设置说明",
            "integration_tips": "集成提示",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_for_agentic_ai_teacher(self, distilled_knowledge: Dict[str, Any], 
                                         validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为 Agentic AI 老师分身翻译。"""
        return {
            "persona": "agentic_ai_teacher",
            "content_type": "agentic_ai_lesson",
            "title": f"Agentic AI 课程: {distilled_knowledge.get('title', 'New Agentic AI Concept')}",
            "reflection_mechanism": "反思机制设计",
            "tool_use_strategy": "工具使用策略",
            "planning_approach": "规划方法",
            "multi_agent_coordination": "多智能体协调",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_for_python_data_analyst(self, distilled_knowledge: Dict[str, Any], 
                                          validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为 Python 数据分析师分身翻译。"""
        core_logic = distilled_knowledge.get("core_logic", {})
        left_brain = core_logic.get("left_brain", {})
        
        return {
            "persona": "python_data_analyst",
            "content_type": "data_analysis_code",
            "title": f"Python 数据分析: {distilled_knowledge.get('title', 'New Data Analysis Technique')}",
            "code_examples": left_brain.get("code_blocks", [])[:3],
            "data_processing_steps": left_brain.get("execution_steps", []),
            "visualization_suggestions": "可视化建议",
            "statistical_methods": "统计方法建议",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_for_photographer_glm(self, distilled_knowledge: Dict[str, Any], 
                                       validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为摄影师（GLM）分身翻译。"""
        return {
            "persona": "photographer_glm",
            "content_type": "photography_technique",
            "title": f"摄影技术: {distilled_knowledge.get('title', 'New Photography Technique')}",
            "visual_composition": "视觉构图建议",
            "lighting_setup": "灯光设置建议",
            "post_processing": "后期处理技巧",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_for_digital_transformation_expert_glm(self, distilled_knowledge: Dict[str, Any], 
                                                        validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为数字化转型专家（GLM）分身翻译。"""
        return {
            "persona": "digital_transformation_expert_glm",
            "content_type": "digital_transformation_strategy",
            "title": f"数字化转型: {distilled_knowledge.get('title', 'New Digital Transformation Insight')}",
            "business_impact": "业务影响分析",
            "implementation_roadmap": "实施路线图",
            "change_management": "变革管理建议",
            "roi_analysis": "投资回报分析",
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified"
        }

    def _translate_default(self, avatar_type: str, distilled_knowledge: Dict[str, Any], 
                          validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """默认翻译方法。
        
        Args:
            avatar_type: 分身类型。
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            默认翻译内容字典。
        """
        return {
            "persona": avatar_type,
            "content_type": "generic_knowledge",
            "title": f"{avatar_type}: {distilled_knowledge.get('title', 'New Knowledge')}",
            "raw_knowledge": distilled_knowledge,
            "validation_result": validation_result,
            "source_url": distilled_knowledge.get("url", ""),
            "confidence": distilled_knowledge.get("confidence", 0.0),
            "validation_status": "verified" if validation_result.get("success", False) else "unverified"
        }

    def _create_error_notification(self, avatar_type: str, distilled_knowledge: Dict[str, Any], 
                                  validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """为无效知识创建错误通知。
        
        Args:
            avatar_type: 分身类型。
            distilled_knowledge: 蒸馏后的知识。
            validation_result: 验证结果。
            
        Returns:
            错误通知字典。
        """
        return {
            "persona": avatar_type,
            "content_type": "error_notification",
            "title": f"知识验证失败: {distilled_knowledge.get('title', 'Unknown')}",
            "task_id": distilled_knowledge.get("task_id", "unknown"),
            "error_details": validation_result.get("error_trace", "Unknown error"),
            "validation_details": validation_result.get("validation_details", {}),
            "recommendation": "此知识未通过沙箱验证，请谨慎使用或等待修正版本",
            "timestamp": datetime.now().isoformat()
        }