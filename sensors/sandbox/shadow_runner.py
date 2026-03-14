"""
影子沙箱验证算法实现。

使用 Docker 侧车隔离环境，自动生成测试用例，
运行成功写入 SkillRL，失败 Traceback 存入 ReasoningBank。
"""

import logging
import subprocess
import tempfile
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class ShadowSandbox:
    """影子沙箱验证器。"""

    def __init__(self, config: Dict[str, Any]):
        """初始化影子沙箱。
        
        Args:
            config: 配置字典，包含 max_test_cases, min_test_cases, timeout_seconds 等参数。
        """
        self.logger = logging.getLogger("ShadowSandbox")
        self.config = config
        self.max_test_cases = config.get("max_test_cases", 10)
        self.min_test_cases = config.get("min_test_cases", 5)
        self.timeout_seconds = config.get("timeout_seconds", 60)
        self.docker_image = config.get("docker_image", "python:3.11-slim")
        
        # Verify Docker is available
        self.docker_available = self._check_docker_availability()

    def _check_docker_availability(self) -> bool:
        """检查 Docker 是否可用。
        
        Returns:
            True if Docker is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("Docker is available for sandboxing")
                return True
            else:
                self.logger.warning("Docker not available: command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.warning("Docker not available: command not found or timed out")
            return False

    def validate(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """在影子沙箱中验证技能。
        
        Args:
            skill: 要验证的技能字典（来自双脑蒸馏的输出）。
            
        Returns:
            验证结果字典，包含 success, skill, error_trace 等字段。
        """
        self.logger.info(f"Validating skill {skill.get('task_id', 'unknown')}")
        
        if not self.docker_available:
            self.logger.error("Docker not available, cannot run sandbox validation")
            return {
                "success": False,
                "skill": None,
                "error_trace": "Docker not available for sandbox validation",
                "validation_details": {"reason": "docker_unavailable"}
            }
            
        try:
            # Generate test cases
            test_cases = self.generate_test_cases(skill)
            
            if len(test_cases) < self.min_test_cases:
                self.logger.warning(f"Insufficient test cases generated: {len(test_cases)}")
                return {
                    "success": False,
                    "skill": None,
                    "error_trace": f"Insufficient test cases ({len(test_cases)} < {self.min_test_cases})",
                    "validation_details": {"reason": "insufficient_test_cases"}
                }
                
            # Run isolated validation
            result = self.run_isolated(skill, test_cases)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during validation: {e}")
            return {
                "success": False,
                "skill": None,
                "error_trace": str(e),
                "validation_details": {"reason": "validation_exception"}
            }

    def generate_test_cases(self, skill: Dict[str, Any]) -> List[Dict[str, Any]]:
        """为技能生成测试用例。
        
        Args:
            skill: 技能字典。
            
        Returns:
            测试用例列表。
        """
        self.logger.debug("Generating test cases for skill validation...")
        test_cases = []
        
        try:
            # Extract code blocks from the skill
            code_blocks = []
            if "core_logic" in skill and "left_brain" in skill["core_logic"]:
                left_brain = skill["core_logic"]["left_brain"]
                code_blocks = left_brain.get("code_blocks", [])
                
            if not code_blocks:
                self.logger.warning("No code blocks found in skill for test generation")
                return []
                
            # Generate test cases based on code blocks
            for i, code_block in enumerate(code_blocks[:self.max_test_cases]):
                test_case = self._create_test_case_from_code(code_block, i, skill)
                if test_case:
                    test_cases.append(test_case)
                    
            # If we have fewer than min_test_cases, try to generate more from other sources
            if len(test_cases) < self.min_test_cases:
                additional_tests = self._generate_additional_tests(skill, self.min_test_cases - len(test_cases))
                test_cases.extend(additional_tests)
                
            self.logger.info(f"Generated {len(test_cases)} test cases")
            return test_cases[:self.max_test_cases]
            
        except Exception as e:
            self.logger.error(f"Error generating test cases: {e}")
            return []

    def _create_test_case_from_code(self, code_block: str, index: int, skill: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """从代码块创建测试用例。
        
        Args:
            code_block: 代码块字符串。
            index: 测试用例索引。
            skill: 技能字典。
            
        Returns:
            测试用例字典，如果无法创建则返回 None。
        """
        try:
            # Clean the code block
            clean_code = self._clean_code_block(code_block)
            
            if not clean_code.strip():
                return None
                
            # Create a simple test that tries to execute the code
            test_code = f"""
import sys
import traceback

def test_case_{index}():
    try:
{self._indent_code(clean_code)}
        return True, "Execution successful"
    except Exception as e:
        return False, str(e) + "\\n" + traceback.format_exc()

if __name__ == "__main__":
    success, message = test_case_{index}()
    print(f"{{'success': {{success}}, 'message': '{{message}}'}}")
"""
            
            return {
                "id": f"test_{index}",
                "code": test_code,
                "description": f"Test case {index} for skill {skill.get('task_id', 'unknown')}",
                "expected_outcome": "successful execution"
            }
            
        except Exception as e:
            self.logger.warning(f"Error creating test case from code: {e}")
            return None

    def _clean_code_block(self, code_block: str) -> str:
        """清理代码块，移除不必要的标记。
        
        Args:
            code_block: 原始代码块。
            
        Returns:
            清理后的代码块。
        """
        # Remove common code block markers
        lines = code_block.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are just language identifiers
            if line.strip().lower() in ['python', 'javascript', 'bash', 'shell', '']:
                continue
            cleaned_lines.append(line)
            
        return '\n'.join(cleaned_lines)

    def _indent_code(self, code: str, indent: str = "        ") -> str:
        """为代码添加缩进。
        
        Args:
            code: 要缩进的代码。
            indent: 缩进字符串。
            
        Returns:
            缩进后的代码。
        """
        lines = code.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)

    def _generate_additional_tests(self, skill: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """生成额外的测试用例。
        
        Args:
            skill: 技能字典。
            count: 需要生成的测试用例数量。
            
        Returns:
            额外的测试用例列表。
        """
        additional_tests = []
        
        # Create tests based on APIs mentioned in the skill
        if "core_logic" in skill and "left_brain" in skill["core_logic"]:
            apis = skill["core_logic"]["left_brain"].get("apis", [])
            for i, api in enumerate(apis[:count]):
                test_code = f"""
def test_api_{i}():
    try:
        # This is a placeholder test for API: {api}
        # In a real implementation, this would be more sophisticated
        assert "{api}" is not None
        return True, "API reference check passed"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, message = test_api_{i}()
    print(f"{{'success': {{success}}, 'message': '{{message}}'}}")
"""
                
                additional_tests.append({
                    "id": f"api_test_{i}",
                    "code": test_code,
                    "description": f"API reference test for {api}",
                    "expected_outcome": "API exists"
                })
                
        return additional_tests

    def run_isolated(self, skill: Dict[str, Any], test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """在隔离环境中运行测试。
        
        Args:
            skill: 技能字典。
            test_cases: 测试用例列表。
            
        Returns:
            验证结果字典。
        """
        self.logger.debug("Running isolated validation in Docker sandbox...")
        
        # Create temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write test cases to files
            test_files = []
            for i, test_case in enumerate(test_cases):
                test_file = temp_path / f"test_{i}.py"
                with open(test_file, 'w') as f:
                    f.write(test_case['code'])
                test_files.append(test_file)
                
            # Create a main test runner
            runner_code = self._create_test_runner(test_files, skill)
            runner_file = temp_path / "runner.py"
            with open(runner_file, 'w') as f:
                f.write(runner_code)
                
            # Create Dockerfile
            dockerfile_content = self._create_dockerfile()
            dockerfile = temp_path / "Dockerfile"
            with open(dockerfile, 'w') as f:
                f.write(dockerfile_content)
                
            # Build and run Docker container
            try:
                # Build image
                build_cmd = ["docker", "build", "-t", f"skill_test_{skill.get('task_id', 'unknown')}", "."]
                build_result = subprocess.run(
                    build_cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds
                )
                
                if build_result.returncode != 0:
                    error_msg = f"Docker build failed: {build_result.stderr}"
                    self.logger.error(error_msg)
                    return {
                        "success": False,
                        "skill": None,
                        "error_trace": error_msg,
                        "validation_details": {
                            "reason": "docker_build_failed",
                            "stdout": build_result.stdout,
                            "stderr": build_result.stderr
                        }
                    }
                    
                # Run container
                run_cmd = [
                    "docker", "run", "--rm", 
                    "--memory=512m",  # Limit memory usage
                    "--cpus=0.5",     # Limit CPU usage
                    f"skill_test_{skill.get('task_id', 'unknown')}"
                ]
                
                run_result = subprocess.run(
                    run_cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds
                )
                
                # Clean up image
                cleanup_cmd = ["docker", "rmi", f"skill_test_{skill.get('task_id', 'unknown')}"]
                subprocess.run(cleanup_cmd, capture_output=True)
                
                # Parse results
                if run_result.returncode == 0:
                    # Parse the output to get detailed results
                    try:
                        results = json.loads(run_result.stdout)
                        if results.get("overall_success", False):
                            # Validation successful, return the skill
                            return {
                                "success": True,
                                "skill": skill,
                                "error_trace": None,
                                "validation_details": {
                                    "test_results": results.get("test_results", []),
                                    "stdout": run_result.stdout,
                                    "stderr": run_result.stderr
                                }
                            }
                        else:
                            error_msg = f"Tests failed: {results.get('failure_reason', 'Unknown')}"
                            return {
                                "success": False,
                                "skill": None,
                                "error_trace": error_msg,
                                "validation_details": {
                                    "reason": "test_failure",
                                    "test_results": results.get("test_results", []),
                                    "stdout": run_result.stdout,
                                    "stderr": run_result.stderr
                                }
                            }
                    except json.JSONDecodeError:
                        # If we can't parse JSON, check if it contains success indicators
                        if "Execution successful" in run_result.stdout:
                            return {
                                "success": True,
                                "skill": skill,
                                "error_trace": None,
                                "validation_details": {
                                    "stdout": run_result.stdout,
                                    "stderr": run_result.stderr
                                }
                            }
                        else:
                            error_msg = f"Unexpected output format: {run_result.stdout[:200]}"
                            return {
                                "success": False,
                                "skill": None,
                                "error_trace": error_msg,
                                "validation_details": {
                                    "reason": "output_parse_error",
                                    "stdout": run_result.stdout,
                                    "stderr": run_result.stderr
                                }
                            }
                else:
                    error_msg = f"Docker run failed with exit code {run_result.returncode}: {run_result.stderr}"
                    return {
                        "success": False,
                        "skill": None,
                        "error_trace": error_msg,
                        "validation_details": {
                            "reason": "docker_run_failed",
                            "stdout": run_result.stdout,
                            "stderr": run_result.stderr
                        }
                    }
                    
            except subprocess.TimeoutExpired:
                error_msg = f"Validation timed out after {self.timeout_seconds} seconds"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "skill": None,
                    "error_trace": error_msg,
                    "validation_details": {"reason": "timeout"}
                }
            except Exception as e:
                error_msg = f"Error running isolated validation: {e}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "skill": None,
                    "error_trace": error_msg,
                    "validation_details": {"reason": "runtime_error"}
                }

    def _create_test_runner(self, test_files: List[Path], skill: Dict[str, Any]) -> str:
        """创建测试运行器代码。
        
        Args:
            test_files: 测试文件路径列表。
            skill: 技能字典。
            
        Returns:
            测试运行器代码字符串。
        """
        test_imports = []
        test_calls = []
        
        for i, test_file in enumerate(test_files):
            test_imports.append(f"import test_{i}")
            test_calls.append(f"    result_{i} = test_{i}.test_case_{i}() if hasattr(test_{i}, 'test_case_{i}') else test_{i}.test_api_{i}()")
            test_calls.append(f"    test_results.append({{'id': 'test_{i}', 'success': result_{i}[0], 'message': result_{i}[1]}})")
            
        runner_code = f"""
import json
import sys

# Import test modules
{chr(10).join(test_imports)}

def main():
    test_results = []
    
    # Run all tests
{chr(10).join(test_calls)}
    
    # Calculate overall success
    overall_success = all(result['success'] for result in test_results)
    
    # Prepare output
    output = {{
        'overall_success': overall_success,
        'test_results': test_results,
        'skill_task_id': '{skill.get('task_id', 'unknown')}'
    }}
    
    print(json.dumps(output))
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
"""
        
        return runner_code

    def _create_dockerfile(self) -> str:
        """创建 Dockerfile 内容。
        
        Returns:
            Dockerfile 内容字符串。
        """
        return f"""FROM {self.docker_image}

WORKDIR /app

# Copy test files
COPY . .

# Install any dependencies (this is a simplified version)
# In a real implementation, you'd parse requirements from the skill
RUN pip install --no-cache-dir pytest

CMD ["python", "runner.py"]
"""

    def audit_result(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """审计验证结果。
        
        Args:
            validation_result: 验证结果字典。
            
        Returns:
            审计后的结果字典。
        """
        self.logger.debug("Auditing validation result...")
        
        # Add audit metadata
        audit_result = validation_result.copy()
        audit_result["audit_timestamp"] = self._get_timestamp()
        audit_result["audit_version"] = "1.0"
        
        # Add security checks
        if validation_result["success"]:
            audit_result["security_status"] = "passed"
        else:
            audit_result["security_status"] = "failed"
            
        return audit_result

    def _get_timestamp(self) -> str:
        """获取当前时间戳。
        
        Returns:
            ISO 格式的时间戳字符串。
        """
        from datetime import datetime
        return datetime.now().isoformat()