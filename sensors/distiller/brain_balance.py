"""
Dual-brain knowledge distillation module.

Implements the dual-brain logic distillation algorithm with:
- Left brain (Analyzer): Extracts code blocks, APIs, execution steps, structure
- Right brain (Synthesizer): Extracts core pain points,适用场景, capability boundaries

Outputs standardized JSON reasoning paths for SkillRL integration.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class DualBrainDistiller:
    """Dual-brain knowledge distiller for external content."""
    
    def __init__(self, config: dict):
        """Initialize the dual-brain distiller.
        
        Args:
            config: Configuration dictionary containing distillation parameters.
        """
        self.logger = logging.getLogger("DualBrainDistiller")
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.min_content_length = config.get("min_content_length", 100)
        
    def distill(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Distill raw external data into structured knowledge.
        
        Args:
            raw_data: Raw data from external sources with required fields:
                - source: Source type (github, rss, etc.)
                - title: Content title
                - raw_content: Raw text content
                - url: Source URL
                - timestamp: ISO format timestamp
                
        Returns:
            Structured reasoning path with standardized format.
        """
        if not self._validate_input(raw_data):
            raise ValueError("Invalid input data for distillation")
            
        # Generate task ID
        task_id = self._generate_task_id(raw_data)
        
        # Left brain analysis
        left_analysis = self.left_analyze(raw_data)
        
        # Right brain synthesis  
        right_synthesis = self.right_synthesize(raw_data)
        
        # Combine into reasoning path
        reasoning_path = self.to_reasoning_path(
            task_id=task_id,
            left_analysis=left_analysis,
            right_synthesis=right_synthesis,
            raw_data=raw_data
        )
        
        return reasoning_path
        
    def _validate_input(self, raw_data: Dict[str, Any]) -> bool:
        """Validate input data structure.
        
        Args:
            raw_data: Raw data dictionary to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        required_fields = ["source", "title", "raw_content", "url", "timestamp"]
        return all(field in raw_data for field in required_fields)
        
    def _generate_task_id(self, raw_data: Dict[str, Any]) -> str:
        """Generate unique task ID for the distilled knowledge.
        
        Args:
            raw_data: Raw data dictionary.
            
        Returns:
            Unique task ID string.
        """
        import hashlib
        source_str = f"{raw_data['source']}_{raw_data['url']}_{raw_data['timestamp']}"
        return hashlib.md5(source_str.encode()).hexdigest()[:16]
        
    def left_analyze(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Left brain analysis - extract structural and technical elements.
        
        Args:
            raw_data: Raw data dictionary.
            
        Returns:
            Dictionary containing technical analysis results.
        """
        self.logger.info(f"Left brain analyzing: {raw_data['title']}")
        
        content = raw_data["raw_content"]
        source = raw_data["source"]
        
        analysis = {
            "code_blocks": [],
            "apis": [],
            "execution_steps": [],
            "structure": {},
            "confidence": 0.0
        }
        
        try:
            if source == "github":
                analysis = self._analyze_github_content(content)
            elif source == "stackoverflow":
                analysis = self._analyze_qa_content(content)
            elif source == "readthedocs":
                analysis = self._analyze_docs_content(content)
            else:
                analysis = self._analyze_generic_content(content)
                
            # Calculate confidence based on content quality and completeness
            analysis["confidence"] = self._calculate_confidence(analysis, content)
            
        except Exception as e:
            self.logger.error(f"Error in left brain analysis: {e}")
            analysis["confidence"] = 0.0
            
        return analysis
        
    def _analyze_github_content(self, content: str) -> Dict[str, Any]:
        """Analyze GitHub repository content.
        
        Args:
            content: Repository description or README content.
            
        Returns:
            Analysis results specific to GitHub content.
        """
        # Extract potential code patterns, language mentions, and structure
        lines = content.split('\n')
        code_blocks = []
        apis = []
        execution_steps = []
        
        # Simple pattern matching for demonstration
        # In real implementation, this would use more sophisticated NLP
        for line in lines:
            if '```' in line:
                # Found code block marker
                code_blocks.append(line)
            elif 'API' in line or '.api' in line or 'endpoint' in line.lower():
                apis.append(line.strip())
            elif any(keyword in line.lower() for keyword in ['step', 'install', 'run', 'execute']):
                execution_steps.append(line.strip())
                
        return {
            "code_blocks": code_blocks,
            "apis": apis,
            "execution_steps": execution_steps,
            "structure": {"type": "repository", "language_hints": self._extract_language_hints(content)}
        }
        
    def _analyze_qa_content(self, content: str) -> Dict[str, Any]:
        """Analyze Q&A platform content.
        
        Args:
            content: Question and answer content.
            
        Returns:
            Analysis results specific to Q&A content.
        """
        # Extract code solutions, error handling, and implementation details
        lines = content.split('\n')
        code_blocks = []
        apis = []
        execution_steps = []
        
        for line in lines:
            if '```' in line or line.startswith('    ') or line.startswith('\t'):
                # Code formatting indicators
                code_blocks.append(line)
            elif 'error' in line.lower() or 'exception' in line.lower():
                execution_steps.append(f"Error handling: {line.strip()}")
            elif 'solution' in line.lower() or 'answer' in line.lower():
                execution_steps.append(f"Solution step: {line.strip()}")
                
        return {
            "code_blocks": code_blocks,
            "apis": apis,
            "execution_steps": execution_steps,
            "structure": {"type": "q&a", "problem_solution_pairs": 1}
        }
        
    def _analyze_docs_content(self, content: str) -> Dict[str, Any]:
        """Analyze documentation content.
        
        Args:
            content: Documentation text.
            
        Returns:
            Analysis results specific to documentation.
        """
        # Extract API references, usage patterns, and conceptual structure
        lines = content.split('\n')
        code_blocks = []
        apis = []
        execution_steps = []
        
        for line in lines:
            if '```' in line:
                code_blocks.append(line)
            elif any(indicator in line for indicator in ['def ', 'function ', 'class ', 'interface ']):
                apis.append(line.strip())
            elif 'example:' in line.lower() or 'usage:' in line.lower():
                execution_steps.append(line.strip())
                
        return {
            "code_blocks": code_blocks,
            "apis": apis,
            "execution_steps": execution_steps,
            "structure": {"type": "documentation", "sections": len([l for l in lines if l.startswith('#')])}
        }
        
    def _analyze_generic_content(self, content: str) -> Dict[str, Any]:
        """Analyze generic content when source type is unknown.
        
        Args:
            content: Generic text content.
            
        Returns:
            Basic analysis results.
        """
        # Basic content analysis
        sentences = content.split('.')
        code_indicators = sum(1 for s in sentences if any(c in s for c in ['=', '(', ')', '{', '}', '[', ']']))
        
        return {
            "code_blocks": [],
            "apis": [],
            "execution_steps": [],
            "structure": {"type": "generic", "code_likelihood": min(code_indicators / len(sentences), 1.0)}
        }
        
    def _extract_language_hints(self, content: str) -> List[str]:
        """Extract programming language hints from content.
        
        Args:
            content: Text content to analyze.
            
        Returns:
            List of detected programming languages.
        """
        languages = []
        content_lower = content.lower()
        
        language_keywords = {
            "python": ["python", "import ", "def ", "class ", ".py"],
            "javascript": ["javascript", "js", "function ", "const ", "let ", ".js"],
            "typescript": ["typescript", "ts", "interface ", "type ", ".ts"],
            "java": ["java", "public class", "private ", "protected ", ".java"],
            "go": ["golang", "go", "func ", "package ", ".go"],
            "rust": ["rust", "fn ", "impl ", "trait ", ".rs"]
        }
        
        for lang, keywords in language_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                languages.append(lang)
                
        return languages
        
    def _calculate_confidence(self, analysis: Dict[str, Any], content: str) -> float:
        """Calculate confidence score for the analysis.
        
        Args:
            analysis: Analysis results dictionary.
            content: Original content text.
            
        Returns:
            Confidence score between 0 and 1.
        """
        # Base confidence on content length
        base_confidence = min(len(content) / self.min_content_length, 1.0)
        
        # Boost confidence based on detected elements
        element_boost = 0.0
        if analysis["code_blocks"]:
            element_boost += 0.2
        if analysis["apis"]:
            element_boost += 0.15
        if analysis["execution_steps"]:
            element_boost += 0.15
            
        confidence = min(base_confidence + element_boost, 1.0)
        return max(confidence, 0.1)  # Minimum confidence of 0.1
        
    def right_synthesize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Right brain synthesis - extract conceptual and contextual insights.
        
        Args:
            raw_data: Raw data dictionary.
            
        Returns:
            Dictionary containing conceptual synthesis results.
        """
        self.logger.info(f"Right brain synthesizing: {raw_data['title']}")
        
        content = raw_data["raw_content"]
        source = raw_data["source"]
        
        synthesis = {
            "core_pain_points": [],
            "applicable_scenarios": [],
            "capability_boundaries": [],
            "key_insights": [],
            "confidence": 0.0
        }
        
        try:
            if source == "hackernews":
                synthesis = self._synthesize_social_content(content)
            elif source == "arxiv":
                synthesis = self._synthesize_research_content(content)
            elif source == "rss":
                synthesis = self._synthesize_blog_content(content)
            else:
                synthesis = self._synthesize_generic_content(content)
                
            # Calculate confidence
            synthesis["confidence"] = self._calculate_synthesis_confidence(synthesis, content)
            
        except Exception as e:
            self.logger.error(f"Error in right brain synthesis: {e}")
            synthesis["confidence"] = 0.0
            
        return synthesis
        
    def _synthesize_social_content(self, content: str) -> Dict[str, Any]:
        """Synthesize insights from social media content.
        
        Args:
            content: Social media post content.
            
        Returns:
            Synthesis results for social content.
        """
        # Extract trends, opinions, and community sentiment
        pain_points = []
        scenarios = []
        boundaries = []
        insights = []
        
        # Simple keyword-based extraction for demonstration
        content_lower = content.lower()
        
        if 'problem' in content_lower or 'issue' in content_lower or 'challenge' in content_lower:
            pain_points.append("Community identified challenges in current approaches")
        if 'solution' in content_lower or 'alternative' in content_lower:
            scenarios.append("Alternative approaches being discussed")
        if 'limitation' in content_lower or 'constraint' in content_lower:
            boundaries.append("Recognized limitations in existing solutions")
        if 'trend' in content_lower or 'future' in content_lower:
            insights.append("Emerging trends and future directions")
            
        return {
            "core_pain_points": pain_points,
            "applicable_scenarios": scenarios,
            "capability_boundaries": boundaries,
            "key_insights": insights
        }
        
    def _synthesize_research_content(self, content: str) -> Dict[str, Any]:
        """Synthesize insights from research papers.
        
        Args:
            content: Research paper abstract or content.
            
        Returns:
            Synthesis results for research content.
        """
        # Extract novel contributions, methodology, and implications
        pain_points = []
        scenarios = []
        boundaries = []
        insights = []
        
        content_lower = content.lower()
        
        if 'novel' in content_lower or 'new' in content_lower:
            insights.append("Novel approach or methodology introduced")
        if 'problem' in content_lower or 'gap' in content_lower:
            pain_points.append("Identified research gap or problem")
        if 'application' in content_lower or 'use case' in content_lower:
            scenarios.append("Potential applications and use cases")
        if 'limitation' in content_lower or 'future work' in content_lower:
            boundaries.append("Acknowledged limitations and future work")
            
        return {
            "core_pain_points": pain_points,
            "applicable_scenarios": scenarios,
            "capability_boundaries": boundaries,
            "key_insights": insights
        }
        
    def _synthesize_blog_content(self, content: str) -> Dict[str, Any]:
        """Synthesize insights from technical blog posts.
        
        Args:
            content: Blog post content.
            
        Returns:
            Synthesis results for blog content.
        """
        # Extract practical insights, lessons learned, and recommendations
        pain_points = []
        scenarios = []
        boundaries = []
        insights = []
        
        content_lower = content.lower()
        
        if 'lesson' in content_lower or 'learned' in content_lower:
            insights.append("Practical lessons learned from real-world experience")
        if 'mistake' in content_lower or 'error' in content_lower:
            pain_points.append("Common mistakes and pitfalls to avoid")
        if 'best practice' in content_lower or 'recommendation' in content_lower:
            scenarios.append("Best practices and recommended approaches")
        if 'not suitable' in content_lower or 'avoid' in content_lower:
            boundaries.append("Situations where the approach is not suitable")
            
        return {
            "core_pain_points": pain_points,
            "applicable_scenarios": scenarios,
            "capability_boundaries": boundaries,
            "key_insights": insights
        }
        
    def _synthesize_generic_content(self, content: str) -> Dict[str, Any]:
        """Synthesize insights from generic content.
        
        Args:
            content: Generic text content.
            
        Returns:
            Basic synthesis results.
        """
        return {
            "core_pain_points": [],
            "applicable_scenarios": [],
            "capability_boundaries": [],
            "key_insights": ["Generic content analysis - limited contextual insights"]
        }
        
    def _calculate_synthesis_confidence(self, synthesis: Dict[str, Any], content: str) -> float:
        """Calculate confidence score for the synthesis.
        
        Args:
            synthesis: Synthesis results dictionary.
            content: Original content text.
            
        Returns:
            Confidence score between 0 and 1.
        """
        # Base confidence on content length
        base_confidence = min(len(content) / self.min_content_length, 1.0)
        
        # Boost confidence based on detected insights
        insight_boost = 0.0
        total_insights = (
            len(synthesis["core_pain_points"]) +
            len(synthesis["applicable_scenarios"]) +
            len(synthesis["capability_boundaries"]) +
            len(synthesis["key_insights"])
        )
        insight_boost = min(total_insights * 0.1, 0.4)
        
        confidence = min(base_confidence + insight_boost, 1.0)
        return max(confidence, 0.1)  # Minimum confidence of 0.1
        
    def to_reasoning_path(
        self,
        task_id: str,
        left_analysis: Dict[str, Any],
        right_synthesis: Dict[str, Any],
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert dual-brain analysis into standardized reasoning path.
        
        Args:
            task_id: Unique task identifier.
            left_analysis: Left brain analysis results.
            right_synthesis: Right brain synthesis results.
            raw_data: Original raw data.
            
        Returns:
            Standardized reasoning path dictionary.
        """
        # Determine overall confidence as average of both brains
        overall_confidence = (left_analysis["confidence"] + right_synthesis["confidence"]) / 2
        
        # Extract core logic from both analyses
        core_logic = {
            "technical_structure": left_analysis["structure"],
            "conceptual_insights": {
                "pain_points": right_synthesis["core_pain_points"],
                "scenarios": right_synthesis["applicable_scenarios"],
                "boundaries": right_synthesis["capability_boundaries"]
            }
        }
        
        # Create action list from execution steps and applicable scenarios
        action_list = []
        action_list.extend(left_analysis["execution_steps"])
        action_list.extend(right_synthesis["applicable_scenarios"])
        
        # Critical checks from pain points and boundaries
        critical_check = []
        critical_check.extend(right_synthesis["core_pain_points"])
        critical_check.extend(right_synthesis["capability_boundaries"])
        
        reasoning_path = {
            "task_id": task_id,
            "core_logic": core_logic,
            "action_list": action_list,
            "critical_check": critical_check,
            "source": raw_data["source"],
            "url": raw_data["url"],
            "title": raw_data["title"],
            "timestamp": raw_data["timestamp"],
            "confidence": overall_confidence,
            "distillation_timestamp": datetime.now().isoformat()
        }
        
        return reasoning_path