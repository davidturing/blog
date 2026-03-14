"""
CPEP (Cross-Persona Experience Protocol) for avatar alignment.

Implements the CPEP cross-persona alignment protocol that automatically
broadcasts validated skills to all digital personas, translating them
according to each persona's specialization:
- Tech Blogger: Popular science translation
- Technical Expert: Code-focused translation  
- Architect: Design philosophy translation
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class CPEPAlign:
    """CPEP (Cross-Persona Experience Protocol) broadcaster."""
    
    def __init__(self, config: dict):
        """Initialize the CPEP aligner.
        
        Args:
            config: Configuration dictionary containing CPEP parameters.
        """
        self.logger = logging.getLogger("CPEPAlign")
        self.avatar_types = config.get("avatar_types", [])
        self.broadcast_delay_seconds = config.get("broadcast_delay_seconds", 5)
        self._load_persona_templates()
        
    def _load_persona_templates(self):
        """Load translation templates for each persona type."""
        # In a real implementation, these would be loaded from files
        # For now, we'll define them inline
        self.persona_templates = {
            "tech_blogger": {
                "style": "popular_science",
                "focus": ["key_insights", "applicable_scenarios"],
                "avoid": ["technical_details", "code_blocks"],
                "tone": "accessible_and_engaging"
            },
            "chief_data_officer": {
                "style": "data_governance",
                "focus": ["capability_boundaries", "critical_check"],
                "avoid": ["marketing_fluff"],
                "tone": "professional_and_precise"
            },
            "vibe_coding_teacher": {
                "style": "educational_coding",
                "focus": ["code_blocks", "execution_steps", "action_list"],
                "avoid": ["high_level_concepts"],
                "tone": "instructional_and_practical"
            },
            "agent_self_improvement_teacher": {
                "style": "reflective_learning",
                "focus": ["core_logic", "capability_boundaries", "key_insights"],
                "avoid": ["implementation_details"],
                "tone": "philosophical_and_insightful"
            },
            "multi_agent_teacher": {
                "style": "systems_thinking",
                "focus": ["core_logic", "applicable_scenarios", "capability_boundaries"],
                "avoid": ["single_agent_focus"],
                "tone": "architectural_and_coordinated"
            }
        }
        
    def broadcast(self, skill: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast validated skill to all personas via CPEP.
        
        Args:
            skill: Original validated skill.
            validation_result: Result from shadow sandbox validation.
            
        Returns:
            Broadcast result with translation status for each persona.
        """
        self.logger.info(f"Broadcasting skill {skill.get('task_id', 'unknown')} via CPEP")
        
        broadcast_result = {
            "original_skill_id": skill.get("task_id", "unknown"),
            "broadcast_timestamp": datetime.now().isoformat(),
            "persona_translations": {},
            "broadcast_status": "completed"
        }
        
        try:
            # Only broadcast if validation was successful
            if not validation_result.get("success", False):
                self.logger.warning("Skipping broadcast - validation failed")
                broadcast_result["broadcast_status"] = "skipped_validation_failed"
                return broadcast_result
                
            # Translate for each persona type
            for avatar_type in self.avatar_types:
                try:
                    translation = self.translate_for_avatar(skill, avatar_type)
                    broadcast_result["persona_translations"][avatar_type] = translation
                    
                    # In real implementation, this would send to the actual persona
                    # For now, we'll just log the translation
                    self.logger.info(f"Translated for {avatar_type}: {translation.get('title', 'No title')}")
                    
                except Exception as e:
                    self.logger.error(f"Translation failed for {avatar_type}: {e}")
                    broadcast_result["persona_translations"][avatar_type] = {
                        "error": str(e),
                        "status": "translation_failed"
                    }
                    
            # Add delay if configured (simulated)
            if self.broadcast_delay_seconds > 0:
                import time
                time.sleep(min(self.broadcast_delay_seconds, 1))  # Cap at 1 second for demo
                
        except Exception as e:
            self.logger.error(f"Broadcast failed: {e}")
            broadcast_result["broadcast_status"] = f"broadcast_failed: {str(e)}"
            
        return broadcast_result
        
    def translate_for_avatar(self, skill: Dict[str, Any], avatar_type: str) -> Dict[str, Any]:
        """Translate skill for specific avatar type.
        
        Args:
            skill: Original validated skill.
            avatar_type: Target persona type.
            
        Returns:
            Translated skill adapted for the persona.
        """
        if avatar_type not in self.persona_templates:
            raise ValueError(f"Unknown avatar type: {avatar_type}")
            
        template = self.persona_templates[avatar_type]
        translation = {
            "original_task_id": skill.get("task_id"),
            "avatar_type": avatar_type,
            "translation_timestamp": datetime.now().isoformat(),
            "status": "translated"
        }
        
        try:
            # Apply persona-specific translation logic
            if avatar_type == "tech_blogger":
                translation.update(self._translate_for_tech_blogger(skill))
            elif avatar_type == "chief_data_officer":
                translation.update(self._translate_for_chief_data_officer(skill))
            elif avatar_type == "vibe_coding_teacher":
                translation.update(self._translate_for_vibe_coding_teacher(skill))
            elif avatar_type == "agent_self_improvement_teacher":
                translation.update(self._translate_for_agent_self_improvement_teacher(skill))
            elif avatar_type == "multi_agent_teacher":
                translation.update(self._translate_for_multi_agent_teacher(skill))
            else:
                # Generic translation fallback
                translation.update(self._translate_generic(skill, template))
                
        except Exception as e:
            self.logger.error(f"Translation error for {avatar_type}: {e}")
            translation["status"] = "translation_error"
            translation["error"] = str(e)
            
        return translation
        
    def _translate_for_tech_blogger(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Translate for tech blogger persona (popular science style)."""
        core_logic = skill.get("core_logic", {})
        key_insights = []
        
        # Extract key insights from both technical and conceptual parts
        if "conceptual_insights" in core_logic:
            insights = core_logic["conceptual_insights"]
            key_insights.extend(insights.get("key_insights", []))
            key_insights.extend(insights.get("applicable_scenarios", []))
            
        # Create engaging title and summary
        original_title = skill.get("title", "New Technology Discovery")
        translated_title = f"🚀 {original_title}: What This Means for AI Development"
        
        summary = " ".join(key_insights[:3]) if key_insights else "This discovery represents an important advancement in AI technology."
        
        return {
            "title": translated_title,
            "summary": summary,
            "content_type": "blog_post",
            "audience": "tech_enthusiasts",
            "key_points": key_insights,
            "call_to_action": "Learn more about how this impacts the future of AI agents"
        }
        
    def _translate_for_chief_data_officer(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Translate for chief data officer persona (governance focused)."""
        critical_checks = skill.get("critical_check", [])
        capability_boundaries = []
        
        # Extract governance-relevant information
        if "core_logic" in skill and "conceptual_insights" in skill["core_logic"]:
            insights = skill["core_logic"]["conceptual_insights"]
            capability_boundaries.extend(insights.get("capability_boundaries", []))
            
        return {
            "title": f"Data Governance Assessment: {skill.get('title', 'Unknown Skill')}",
            "risk_assessment": critical_checks,
            "compliance_considerations": capability_boundaries,
            "data_impact": "Requires evaluation of data handling implications",
            "governance_recommendation": "Review before implementation in production systems"
        }
        
    def _translate_for_vibe_coding_teacher(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Translate for vibe coding teacher persona (code-focused)."""
        action_list = skill.get("action_list", [])
        code_blocks = []
        
        # Extract code-related information
        if "core_logic" in skill and "technical_structure" in skill["core_logic"]:
            tech_struct = skill["core_logic"]["technical_structure"]
            code_blocks.extend(tech_struct.get("code_blocks", []))
            
        # Create practical coding examples
        examples = []
        for i, action in enumerate(action_list[:3]):
            examples.append({
                "example_id": f"ex_{i}",
                "description": action,
                "code_snippet": code_blocks[i] if i < len(code_blocks) else "# Implementation example"
            })
            
        return {
            "title": f"Coding Workshop: {skill.get('title', 'New Technique')}",
            "learning_objectives": action_list[:5],
            "code_examples": examples,
            "implementation_steps": action_list,
            "common_pitfalls": skill.get("critical_check", [])[:3]
        }
        
    def _translate_for_agent_self_improvement_teacher(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Translate for agent self-improvement teacher persona (reflective)."""
        core_logic = skill.get("core_logic", {})
        key_insights = []
        
        if "conceptual_insights" in core_logic:
            insights = core_logic["conceptual_insights"]
            key_insights.extend(insights.get("key_insights", []))
            key_insights.extend(insights.get("capability_boundaries", []))
            
        return {
            "title": f"Agent Reflection: {skill.get('title', 'Learning Opportunity')}",
            "philosophical_insights": key_insights,
            "growth_opportunities": skill.get("action_list", [])[:3],
            "limitations_awareness": skill.get("critical_check", []),
            "meta_learning": "How this knowledge contributes to agent evolution"
        }
        
    def _translate_for_multi_agent_teacher(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Translate for multi-agent teacher persona (systems thinking)."""
        core_logic = skill.get("core_logic", {})
        scenarios = []
        boundaries = []
        
        if "conceptual_insights" in core_logic:
            insights = core_logic["conceptual_insights"]
            scenarios.extend(insights.get("applicable_scenarios", []))
            boundaries.extend(insights.get("capability_boundaries", []))
            
        return {
            "title": f"Multi-Agent Coordination: {skill.get('title', 'System Capability')}",
            "coordination_patterns": scenarios,
            "system_boundaries": boundaries,
            "agent_roles": "Define how different agent types can leverage this capability",
            "orchestration_strategy": "Integration approach for multi-agent systems"
        }
        
    def _translate_generic(self, skill: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Generic translation fallback."""
        return {
            "title": f"{template.get('style', 'generic')}: {skill.get('title', 'Unknown')}",
            "translation_template": template,
            "original_skill_summary": {
                "confidence": skill.get("confidence"),
                "source": skill.get("source"),
                "timestamp": skill.get("timestamp")
            }
        }