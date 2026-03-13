"""
Meta Prefrontal Cortex - DavidAgent's Advanced Self-Reflection Module

This module acts as the meta-cognitive layer that monitors all task outcomes,
performs automatic quality assessment, and makes decisions about memory
consolidation or deprecation based on execution quality.

Key Features:
1. Listens to all final task outputs
2. Automatically triggers self-reflection after task completion (60s delay)
3. Right brain: Quality scoring (0-1 scale)
4. Left brain: ReasoningBank error detection
5. Decision logic for memory distillation vs. deprecation
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaPrefrontalCortex:
    """Meta cognitive controller for DavidAgent's self-reflection system."""
    
    def __init__(self, workspace_path: str = "/Users/zhaoqinhuang/david_project"):
        self.workspace_path = Path(workspace_path)
        self.memory_path = self.workspace_path / "memory"
        self.reasoning_bank_path = self.workspace_path / "reasoning_bank"
        self.deprecated_rules_path = self.memory_path / "deprecated_rules.json"
        self.quality_threshold_high = 0.8
        self.quality_threshold_low = 0.4
        self.reflection_delay = 60  # seconds
        
        # Ensure required directories exist
        self.memory_path.mkdir(exist_ok=True)
        self.reasoning_bank_path.mkdir(exist_ok=True)
        
        # Load existing deprecated rules
        self.deprecated_rules = self._load_deprecated_rules()
    
    def _load_deprecated_rules(self) -> Dict[str, Any]:
        """Load existing deprecated rules from file."""
        if self.deprecated_rules_path.exists():
            try:
                with open(self.deprecated_rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load deprecated rules: {e}")
                return {}
        return {}
    
    def _save_deprecated_rules(self):
        """Save deprecated rules to file."""
        try:
            with open(self.deprecated_rules_path, 'w', encoding='utf-8') as f:
                json.dump(self.deprecated_rules, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save deprecated rules: {e}")
    
    async def monitor_task_output(self, task_result: Dict[str, Any], task_context: Dict[str, Any]):
        """
        Monitor final task output and schedule automatic reflection.
        
        Args:
            task_result: Final output of the completed task
            task_context: Context information about the task execution
        """
        logger.info("Task completed. Scheduling automatic reflection in 60 seconds...")
        
        # Schedule reflection after delay
        await asyncio.sleep(self.reflection_delay)
        await self._perform_self_reflection(task_result, task_context)
    
    async def _perform_self_reflection(self, task_result: Dict[str, Any], task_context: Dict[str, Any]):
        """
        Perform automatic self-reflection on task execution.
        
        Args:
            task_result: Final output of the completed task
            task_context: Context information about the task execution
        """
        logger.info("Starting automatic self-reflection...")
        
        # Right brain: Quality assessment (0-1 scale)
        quality_score = await self._assess_quality(task_result, task_context)
        logger.info(f"Right brain quality assessment: {quality_score:.3f}")
        
        # Left brain: Check for ReasoningBank errors
        has_reasoning_errors = await self._check_reasoning_bank_errors(task_context)
        logger.info(f"Left brain ReasoningBank error check: {'Errors found' if has_reasoning_errors else 'No errors'}")
        
        # Make decision based on quality score and error status
        await self._make_reflection_decision(
            quality_score=quality_score,
            has_reasoning_errors=has_reasoning_errors,
            task_result=task_result,
            task_context=task_context
        )
    
    async def _assess_quality(self, task_result: Dict[str, Any], task_context: Dict[str, Any]) -> float:
        """
        Right brain function: Assess execution quality on 0-1 scale.
        
        Quality factors:
        - Task completion success
        - Output relevance and accuracy
        - Efficiency of execution path
        - User satisfaction indicators
        - Novelty of the execution path
        
        Returns:
            float: Quality score between 0.0 and 1.0
        """
        # This would typically use an LLM to assess quality
        # For now, implement basic heuristic assessment
        
        score = 0.0
        max_score = 0.0
        
        # Check if task was successful (basic indicator)
        if task_result.get('success', False):
            score += 0.3
        max_score += 0.3
        
        # Check if output contains expected elements
        if 'output' in task_result:
            score += 0.2
        max_score += 0.2
        
        # Check execution efficiency (time, steps, etc.)
        execution_time = task_context.get('execution_time', 0)
        if execution_time > 0 and execution_time < 300:  # Less than 5 minutes
            score += 0.2
        max_score += 0.2
        
        # Check if this is a novel execution path
        is_novel_path = task_context.get('is_novel_path', False)
        if is_novel_path:
            score += 0.3
        max_score += 0.3
        
        # Normalize score
        quality_score = score / max_score if max_score > 0 else 0.0
        return min(1.0, max(0.0, quality_score))
    
    async def _check_reasoning_bank_errors(self, task_context: Dict[str, Any]) -> bool:
        """
        Left brain function: Check if task execution triggered ReasoningBank errors.
        
        Returns:
            bool: True if ReasoningBank errors were detected, False otherwise
        """
        # Check if there are any error logs in the reasoning bank for this task
        task_id = task_context.get('task_id')
        if not task_id:
            return False
        
        # Look for error files in reasoning bank
        error_files = list(self.reasoning_bank_path.glob(f"{task_id}_errors_*.json"))
        return len(error_files) > 0
    
    async def _make_reflection_decision(
        self,
        quality_score: float,
        has_reasoning_errors: bool,
        task_result: Dict[str, Any],
        task_context: Dict[str, Any]
    ):
        """
        Make decision based on reflection results.
        
        Decision Logic:
        - If quality_score > 0.8 AND is new path → Trigger memory distillation
        - If quality_score < 0.4 → Mark as DEPRECATED, write to deprecated rules
        """
        task_id = task_context.get('task_id', 'unknown_task')
        execution_path = task_context.get('execution_path', 'unknown_path')
        is_novel_path = task_context.get('is_novel_path', False)
        
        logger.info(f"Making reflection decision for task {task_id}")
        logger.info(f"Quality: {quality_score:.3f}, Errors: {has_reasoning_errors}, Novel: {is_novel_path}")
        
        if quality_score > self.quality_threshold_high and is_novel_path:
            # High quality + novel path → Memory distillation
            logger.info("Triggering memory distillation for high-quality novel execution path")
            await self._trigger_memory_distillation(task_result, task_context)
            
        elif quality_score < self.quality_threshold_low:
            # Low quality → Mark as deprecated
            logger.info("Marking execution path as DEPRECATED due to low quality")
            await self._mark_as_deprecated(
                task_id=task_id,
                execution_path=execution_path,
                quality_score=quality_score,
                has_reasoning_errors=has_reasoning_errors,
                task_context=task_context
            )
        else:
            logger.info("Reflection complete. No action required.")
    
    async def _trigger_memory_distillation(self, task_result: Dict[str, Any], task_context: Dict[str, Any]):
        """
        Trigger memory distillation process for high-quality novel execution paths.
        """
        # This would integrate with the existing memory distillation system
        # For now, log the event and create a distilled memory record
        
        distilled_memory = {
            'timestamp': time.time(),
            'task_id': task_context.get('task_id'),
            'execution_path': task_context.get('execution_path'),
            'quality_score': await self._assess_quality(task_result, task_context),
            'key_insights': task_result.get('key_insights', []),
            'successful_patterns': task_context.get('successful_patterns', []),
            'distilled_knowledge': task_result.get('output', '')[:500]  # First 500 chars
        }
        
        # Save distilled memory
        distilled_path = self.memory_path / f"distilled_{task_context.get('task_id', 'unknown')}.json"
        try:
            with open(distilled_path, 'w', encoding='utf-8') as f:
                json.dump(distilled_memory, f, indent=2, ensure_ascii=False)
            logger.info(f"Memory distillation completed: {distilled_path}")
        except Exception as e:
            logger.error(f"Failed to save distilled memory: {e}")
    
    async def _mark_as_deprecated(
        self,
        task_id: str,
        execution_path: str,
        quality_score: float,
        has_reasoning_errors: bool,
        task_context: Dict[str, Any]
    ):
        """
        Mark execution path as deprecated and add to避坑 rules.
        """
        deprecation_record = {
            'timestamp': time.time(),
            'task_id': task_id,
            'execution_path': execution_path,
            'quality_score': quality_score,
            'has_reasoning_errors': has_reasoning_errors,
            'failure_reasons': task_context.get('error_logs', []),
            'avoidance_rule': f"Avoid execution path '{execution_path}' for task type '{task_context.get('task_type', 'unknown')}'"
        }
        
        # Add to deprecated rules
        rule_key = f"{task_id}_{execution_path}"
        self.deprecated_rules[rule_key] = deprecation_record
        self._save_deprecated_rules()
        
        logger.info(f"Added deprecation rule: {rule_key}")
    
    def get_deprecated_rules(self) -> Dict[str, Any]:
        """Get current deprecated rules."""
        return self.deprecated_rules.copy()


# Global instance for easy access
_meta_prefrontal_cortex_instance = None

def get_meta_prefrontal_cortex() -> MetaPrefrontalCortex:
    """Get singleton instance of MetaPrefrontalCortex."""
    global _meta_prefrontal_cortex_instance
    if _meta_prefrontal_cortex_instance is None:
        _meta_prefrontal_cortex_instance = MetaPrefrontalCortex()
    return _meta_prefrontal_cortex_instance


# Integration function for controller.py
async def integrate_with_controller(task_result: Dict[str, Any], task_context: Dict[str, Any]):
    """
    Integration point for controller.py to trigger meta prefrontal cortex monitoring.
    
    Usage in controller.py:
    await integrate_with_controller(final_result, execution_context)
    """
    cortex = get_meta_prefrontal_cortex()
    await cortex.monitor_task_output(task_result, task_context)


if __name__ == "__main__":
    # Example usage
    async def example():
        cortex = MetaPrefrontalCortex()
        
        # Simulate a task result
        task_result = {
            'success': True,
            'output': 'Task completed successfully with high quality output',
            'key_insights': ['Insight 1', 'Insight 2']
        }
        
        task_context = {
            'task_id': 'example_task_001',
            'execution_path': 'novel_path_v1',
            'is_novel_path': True,
            'execution_time': 120,
            'task_type': 'data_analysis'
        }
        
        await cortex.monitor_task_output(task_result, task_context)
    
    # Run example (uncomment for testing)
    # asyncio.run(example())