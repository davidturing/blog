"""
双脑逻辑蒸馏算法实现。

左脑 Analyzer：提取代码块、API、执行步骤、结构；
右脑 Synthesizer：提取核心痛点、适用场景、能力边界；
输出标准化 JSON 推理路径。
"""

import logging
from typing import Dict, Any, List, Optional
import re
from datetime import datetime


class DualBrainDistiller:
    """双脑知识蒸馏器。"""

    def __init__(self, config: Dict[str, Any]):
        """初始化双脑蒸馏器。
        
        Args:
            config: 配置字典，包含 confidence_threshold 等参数。
        """
        self.logger = logging.getLogger("DualBrainDistiller")
        self.config = config
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.min_content_length = config.get("min_content_length", 100)

    def distill(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """对原始数据进行双脑蒸馏。
        
        Args:
            raw_data: 原始数据字典，包含 source, title, description, raw_content 等字段。
            
        Returns:
            蒸馏后的标准化推理路径。
        """
        self.logger.info(f"Distilling content from {raw_data.get('source', 'unknown')}")
        
        # Validate input
        if not self._validate_input(raw_data):
            raise ValueError("Invalid input data for distillation")
            
        # Generate task ID
        task_id = self._generate_task_id(raw_data)
        
        # Left brain analysis
        left_result = self.left_analyze(raw_data)
        
        # Right brain synthesis
        right_result = self.right_synthesize(raw_data)
        
        # Combine results and calculate confidence
        combined_result = self._combine_results(task_id, left_result, right_result, raw_data)
        
        # Validate confidence
        if combined_result["confidence"] < self.confidence_threshold:
            self.logger.warning(f"Low confidence ({combined_result['confidence']}) for distilled knowledge")
            
        return combined_result

    def _validate_input(self, raw_data: Dict[str, Any]) -> bool:
        """验证输入数据的有效性。
        
        Args:
            raw_data: 原始数据字典。
            
        Returns:
            True if valid, False otherwise.
        """
        required_fields = ["source", "title", "raw_content"]
        for field in required_fields:
            if field not in raw_data or not raw_data[field]:
                self.logger.error(f"Missing required field: {field}")
                return False
                
        if len(str(raw_data["raw_content"])) < self.min_content_length:
            self.logger.warning("Content too short for meaningful distillation")
            return False
            
        return True

    def _generate_task_id(self, raw_data: Dict[str, Any]) -> str:
        """生成任务 ID。
        
        Args:
            raw_data: 原始数据字典。
            
        Returns:
            任务 ID 字符串。
        """
        import hashlib
        source = raw_data.get("source", "unknown")
        title = raw_data.get("title", "no_title")
        timestamp = raw_data.get("timestamp", datetime.now().isoformat())
        
        # Create a unique hash
        task_string = f"{source}:{title}:{timestamp}"
        return hashlib.md5(task_string.encode()).hexdigest()

    def left_analyze(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """左脑分析：提取代码块、API、执行步骤、结构。
        
        Args:
            raw_data: 原始数据字典。
            
        Returns:
            左脑分析结果。
        """
        self.logger.debug("Performing left brain analysis...")
        content = str(raw_data["raw_content"])
        source = raw_data.get("source", "unknown")
        
        analysis = {
            "code_blocks": [],
            "apis": [],
            "execution_steps": [],
            "structure": {}
        }
        
        try:
            # Extract code blocks based on source type
            if source == "github":
                analysis["code_blocks"] = self._extract_github_code_blocks(content)
            elif source == "stackoverflow":
                analysis["code_blocks"] = self._extract_stackoverflow_code_blocks(content)
            elif source == "readthedocs":
                analysis["code_blocks"] = self._extract_docs_code_blocks(content)
            else:
                analysis["code_blocks"] = self._extract_generic_code_blocks(content)
                
            # Extract APIs (this is a simplified version)
            analysis["apis"] = self._extract_apis(content)
            
            # Extract execution steps
            analysis["execution_steps"] = self._extract_execution_steps(content)
            
            # Analyze structure
            analysis["structure"] = self._analyze_structure(content)
            
        except Exception as e:
            self.logger.error(f"Error in left brain analysis: {e}")
            
        return analysis

    def _extract_github_code_blocks(self, content: str) -> List[str]:
        """从 GitHub 内容中提取代码块。
        
        Args:
            content: GitHub 内容字符串。
            
        Returns:
            代码块列表。
        """
        # GitHub README files often use triple backticks for code blocks
        code_blocks = re.findall(r'```(?:\w+)?\s*(.*?)```', content, re.DOTALL)
        return [block.strip() for block in code_blocks if block.strip()]

    def _extract_stackoverflow_code_blocks(self, content: str) -> List[str]:
        """从 StackOverflow 内容中提取代码块。
        
        Args:
            content: StackOverflow 内容字符串。
            
        Returns:
            代码块列表。
        """
        # StackOverflow uses both triple backticks and indented code blocks
        backtick_blocks = re.findall(r'```(?:\w+)?\s*(.*?)```', content, re.DOTALL)
        indented_blocks = re.findall(r'((?: {4}.*?\n)+)', content)
        
        all_blocks = [block.strip() for block in backtick_blocks if block.strip()]
        all_blocks.extend([block.strip() for block in indented_blocks if block.strip()])
        
        return all_blocks

    def _extract_docs_code_blocks(self, content: str) -> List[str]:
        """从文档内容中提取代码块。
        
        Args:
            content: 文档内容字符串。
            
        Returns:
            代码块列表。
        """
        # Documentation often uses various code block formats
        code_blocks = []
        
        # Triple backticks
        code_blocks.extend(re.findall(r'```(?:\w+)?\s*(.*?)```', content, re.DOTALL))
        
        # Sphinx-style code blocks
        code_blocks.extend(re.findall(r'::\s*\n\n((?: {4}.*?\n)+)', content))
        
        # HTML pre/code blocks (for web-scraped content)
        code_blocks.extend(re.findall(r'<pre><code.*?>(.*?)</code></pre>', content, re.DOTALL))
        
        return [block.strip() for block in code_blocks if block.strip()]

    def _extract_generic_code_blocks(self, content: str) -> List[str]:
        """从通用内容中提取代码块。
        
        Args:
            content: 通用内容字符串。
            
        Returns:
            代码块列表。
        """
        # Try multiple patterns
        patterns = [
            r'```(?:\w+)?\s*(.*?)```',
            r'::\s*\n\n((?: {4}.*?\n)+)',
            r'<pre><code.*?>(.*?)</code></pre>'
        ]
        
        code_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            code_blocks.extend([match.strip() for match in matches if match.strip()])
            
        return code_blocks

    def _extract_apis(self, content: str) -> List[str]:
        """提取 API 信息。
        
        Args:
            content: 内容字符串。
            
        Returns:
            API 列表。
        """
        # This is a simplified implementation
        # In a real system, you'd have more sophisticated API detection
        
        # Look for common API patterns
        api_patterns = [
            r'\b\w+\.\w+\(.*?\)',  # method calls like obj.method()
            r'\b\w+\(.*?\)',       # function calls like func()
            r'GET /[\w/]+',         # REST endpoints
            r'POST /[\w/]+',
            r'PUT /[\w/]+',
            r'DELETE /[\w/]+'
        ]
        
        apis = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            apis.update(matches)
            
        return list(apis)[:10]  # Limit to top 10

    def _extract_execution_steps(self, content: str) -> List[str]:
        """提取执行步骤。
        
        Args:
            content: 内容字符串。
            
        Returns:
            执行步骤列表。
        """
        # Look for numbered lists or step patterns
        step_patterns = [
            r'\d+\.\s+(.+?)(?=\n\d+\.|\Z)',
            r'Step \d+:\s+(.+?)(?=\nStep \d+:|\Z)',
            r'(?:^|\n)(?:-|\*|\•)\s+(.+?)(?=\n(?:-|\*|\•)|\Z)'
        ]
        
        steps = []
        for pattern in step_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            steps.extend([match.strip() for match in matches if match.strip()])
            
        return steps[:10]  # Limit to top 10

    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """分析内容结构。
        
        Args:
            content: 内容字符串。
            
        Returns:
            结构分析结果。
        """
        # Basic structural analysis
        lines = content.split('\n')
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        structure = {
            "line_count": len(lines),
            "paragraph_count": len(paragraphs),
            "avg_paragraph_length": sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            "has_code": bool(re.search(r'```|<code>| {4}\w', content)),
            "has_lists": bool(re.search(r'\n\s*[-*]\s|\n\s*\d+\.', content)),
            "has_headings": bool(re.search(r'\n#+\s', content))
        }
        
        return structure

    def right_synthesize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """右脑合成：提取核心痛点、适用场景、能力边界。
        
        Args:
            raw_data: 原始数据字典。
            
        Returns:
            右脑合成结果。
        """
        self.logger.debug("Performing right brain synthesis...")
        content = str(raw_data["raw_content"])
        title = raw_data.get("title", "")
        source = raw_data.get("source", "unknown")
        
        synthesis = {
            "core_pain_points": [],
            "applicable_scenarios": [],
            "capability_boundaries": [],
            "key_insights": []
        }
        
        try:
            # Extract core pain points
            synthesis["core_pain_points"] = self._extract_pain_points(content, title)
            
            # Extract applicable scenarios
            synthesis["applicable_scenarios"] = self._extract_scenarios(content, title)
            
            # Extract capability boundaries
            synthesis["capability_boundaries"] = self._extract_boundaries(content, title)
            
            # Extract key insights
            synthesis["key_insights"] = self._extract_insights(content, title)
            
        except Exception as e:
            self.logger.error(f"Error in right brain synthesis: {e}")
            
        return synthesis

    def _extract_pain_points(self, content: str, title: str) -> List[str]:
        """提取核心痛点。
        
        Args:
            content: 内容字符串。
            title: 标题字符串。
            
        Returns:
            痛点列表。
        """
        # Look for problem statements and pain point indicators
        pain_indicators = [
            r'problem with',
            r'issue with',
            r'challenge of',
            r'difficulty in',
            r'limitation of',
            r'frustrating',
            r'annoying',
            r'troublesome',
            r'pain point',
            r'bottleneck'
        ]
        
        pain_points = []
        combined_text = f"{title}. {content}"
        
        for indicator in pain_indicators:
            matches = re.finditer(indicator, combined_text, re.IGNORECASE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 50)
                end = min(len(combined_text), match.end() + 100)
                context = combined_text[start:end].strip()
                if context and context not in pain_points:
                    pain_points.append(context)
                    
        return pain_points[:5]  # Limit to top 5

    def _extract_scenarios(self, content: str, title: str) -> List[str]:
        """提取适用场景。
        
        Args:
            content: 内容字符串。
            title: 标题字符串。
            
        Returns:
            场景列表。
        """
        # Look for scenario indicators
        scenario_indicators = [
            r'use case',
            r'scenario',
            r'when to use',
            r'applicable for',
            r'suitable for',
            r'ideal for',
            r'best used when',
            r'works well for'
        ]
        
        scenarios = []
        combined_text = f"{title}. {content}"
        
        for indicator in scenario_indicators:
            matches = re.finditer(indicator, combined_text, re.IGNORECASE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 30)
                end = min(len(combined_text), match.end() + 80)
                context = combined_text[start:end].strip()
                if context and context not in scenarios:
                    scenarios.append(context)
                    
        return scenarios[:5]  # Limit to top 5

    def _extract_boundaries(self, content: str, title: str) -> List[str]:
        """提取能力边界。
        
        Args:
            content: 内容字符串。
            title: 标题字符串。
            
        Returns:
            边界列表。
        """
        # Look for limitation and boundary indicators
        boundary_indicators = [
            r'limitation',
            r'boundary',
            r'constraint',
            r'cannot',
            r'does not',
            r'not suitable for',
            r'only works for',
            r'requires',
            r'depends on',
            r'assumes'
        ]
        
        boundaries = []
        combined_text = f"{title}. {content}"
        
        for indicator in boundary_indicators:
            matches = re.finditer(indicator, combined_text, re.IGNORECASE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 30)
                end = min(len(combined_text), match.end() + 80)
                context = combined_text[start:end].strip()
                if context and context not in boundaries:
                    boundaries.append(context)
                    
        return boundaries[:5]  # Limit to top 5

    def _extract_insights(self, content: str, title: str) -> List[str]:
        """提取关键洞察。
        
        Args:
            content: 内容字符串。
            title: 标题字符串。
            
        Returns:
            洞察列表。
        """
        # Look for insight indicators
        insight_indicators = [
            r'key insight',
            r'main takeaway',
            r'important point',
            r'crucial',
            r'essential',
            r'fundamental',
            r'core concept',
            r'major finding'
        ]
        
        insights = []
        combined_text = f"{title}. {content}"
        
        for indicator in insight_indicators:
            matches = re.finditer(indicator, combined_text, re.IGNORECASE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 30)
                end = min(len(combined_text), match.end() + 80)
                context = combined_text[start:end].strip()
                if context and context not in insights:
                    insights.append(context)
                    
        # If no explicit insights found, extract key sentences
        if not insights:
            sentences = re.split(r'[.!?]+', combined_text)
            # Get sentences that contain technical terms or are longer than average
            tech_terms = ['api', 'model', 'algorithm', 'framework', 'system', 'architecture']
            for sentence in sentences:
                if len(sentence) > 50 and any(term in sentence.lower() for term in tech_terms):
                    insights.append(sentence.strip() + '.')
                    if len(insights) >= 3:
                        break
                        
        return insights[:3]  # Limit to top 3

    def _combine_results(self, task_id: str, left_result: Dict[str, Any], 
                        right_result: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """合并左右脑结果。
        
        Args:
            task_id: 任务 ID。
            left_result: 左脑分析结果。
            right_result: 右脑合成结果。
            raw_data: 原始数据。
            
        Returns:
            合并后的标准化推理路径。
        """
        # Calculate confidence based on content quality and completeness
        confidence = self._calculate_confidence(left_result, right_result, raw_data)
        
        # Build the standardized reasoning path
        reasoning_path = {
            "task_id": task_id,
            "core_logic": {
                "left_brain": left_result,
                "right_brain": right_result
            },
            "action_list": self._generate_action_list(left_result, right_result),
            "critical_check": self._generate_critical_checks(left_result, right_result),
            "source": raw_data.get("source", "unknown"),
            "url": raw_data.get("url", ""),
            "title": raw_data.get("title", ""),
            "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
            "confidence": confidence
        }
        
        return reasoning_path

    def _calculate_confidence(self, left_result: Dict[str, Any], 
                             right_result: Dict[str, Any], raw_data: Dict[str, Any]) -> float:
        """计算置信度。
        
        Args:
            left_result: 左脑分析结果。
            right_result: 右脑合成结果。
            raw_data: 原始数据。
            
        Returns:
            置信度分数（0.0 到 1.0）。
        """
        score = 0.0
        max_score = 0.0
        
        # Left brain confidence factors
        if left_result.get("code_blocks"):
            score += 0.2
            max_score += 0.2
        if left_result.get("apis"):
            score += 0.15
            max_score += 0.15
        if left_result.get("execution_steps"):
            score += 0.15
            max_score += 0.15
            
        # Right brain confidence factors
        if right_result.get("core_pain_points"):
            score += 0.15
            max_score += 0.15
        if right_result.get("applicable_scenarios"):
            score += 0.15
            max_score += 0.15
        if right_result.get("capability_boundaries"):
            score += 0.1
            max_score += 0.1
        if right_result.get("key_insights"):
            score += 0.1
            max_score += 0.1
            
        # Content length factor
        content_length = len(str(raw_data.get("raw_content", "")))
        if content_length > 500:
            score += 0.1
            max_score += 0.1
        elif content_length > 200:
            score += 0.05
            max_score += 0.1
            
        # Avoid division by zero
        if max_score == 0:
            return 0.0
            
        return min(score / max_score, 1.0)

    def _generate_action_list(self, left_result: Dict[str, Any], 
                             right_result: Dict[str, Any]) -> List[str]:
        """生成行动列表。
        
        Args:
            left_result: 左脑分析结果。
            right_result: 右脑合成结果。
            
        Returns:
            行动列表。
        """
        actions = []
        
        # Based on left brain analysis
        if left_result.get("code_blocks"):
            actions.append("Extract and validate code examples")
        if left_result.get("apis"):
            actions.append("Document API usage patterns")
        if left_result.get("execution_steps"):
            actions.append("Create step-by-step implementation guide")
            
        # Based on right brain synthesis
        if right_result.get("core_pain_points"):
            actions.append("Address identified pain points")
        if right_result.get("applicable_scenarios"):
            actions.append("Define clear use cases")
        if right_result.get("capability_boundaries"):
            actions.append("Establish clear limitations")
            
        return actions

    def _generate_critical_checks(self, left_result: Dict[str, Any], 
                                 right_result: Dict[str, Any]) -> List[str]:
        """生成关键检查点。
        
        Args:
            left_result: 左脑分析结果。
            right_result: 右脑合成结果。
            
        Returns:
            关键检查点列表。
        """
        checks = []
        
        # Validation checks
        if left_result.get("code_blocks"):
            checks.append("Verify code blocks execute correctly")
        if left_result.get("apis"):
            checks.append("Validate API compatibility and availability")
            
        # Boundary checks
        if right_result.get("capability_boundaries"):
            checks.append("Test edge cases beyond stated boundaries")
            
        # Consistency checks
        checks.append("Ensure left and right brain insights are consistent")
        checks.append("Validate against existing knowledge base")
        
        return checks