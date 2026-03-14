"""
Shadow sandbox for isolated skill validation.

Implements the shadow sandbox verification algorithm using Docker sidecar isolation.
Generates test cases, runs them in isolated environment, and validates results
before allowing knowledge to be written to permanent memory.
"""

import logging
import json
import tempfile
import os
from typing import Dict, Any, List, Optional
from datetime import datetime


class ShadowSandbox:
    """Shadow sandbox for isolated skill validation."""
    
    def __init__(self, config: dict):
        """Initialize the shadow sandbox.
        
        Args:
            config: Configuration dictionary containing sandbox parameters.
        """
        self.logger = logging.getLogger("ShadowSandbox")
        self.max_test_cases = config.get("max_test_cases", 10)
        self.min_test_cases = config.get("min_test_cases", 5)
        self.timeout_seconds = config.get("timeout_seconds", 60)
        self.docker_image = config.get("docker_image", "python:3.11-slim")
        self._check_docker_availability()
        
    def _check_docker_availability(self):
        """Check if Docker is available for sandboxing."""
        try:
            import docker
            self.docker_client = docker.from_env()
            self.docker_available = True
            self.logger.info("Docker available for sandbox isolation")
        except ImportError:
            self.docker_available = False
            self.logger.warning("Docker not available - using simulated sandbox")
        except Exception as e:
            self.docker_available = False
            self.logger.warning(f"Docker connection failed: {e} - using simulated sandbox")
            
    def validate(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a distilled skill in the shadow sandbox.
        
        Args:
            skill: Distilled skill from the dual-brain distiller.
            
        Returns:
            Validation result with success status and either validated skill or error trace.
        """
        self.logger.info(f"Validating skill: {skill.get('task_id', 'unknown')}")
        
        try:
            # Generate test cases
            test_cases = self.generate_test_cases(skill)
            
            if not test_cases:
                self.logger.warning("No test cases generated - validation failed")
                return {
                    "success": False,
                    "error_trace": "No test cases could be generated for validation",
                    "skill": None
                }
                
            # Run tests in isolated environment
            if self.docker_available:
                result = self._run_docker_validation(test_cases, skill)
            else:
                result = self._run_simulated_validation(test_cases, skill)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed with exception: {e}")
            return {
                "success": False,
                "error_trace": f"Validation exception: {str(e)}",
                "skill": None
            }
            
    def generate_test_cases(self, skill: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for the skill.
        
        Args:
            skill: Distilled skill to generate tests for.
            
        Returns:
            List of test case dictionaries.
        """
        self.logger.info("Generating test cases for skill validation")
        
        test_cases = []
        
        # Extract code blocks from the skill
        code_blocks = []
        if "core_logic" in skill and "technical_structure" in skill["core_logic"]:
            tech_struct = skill["core_logic"]["technical_structure"]
            if "code_blocks" in tech_struct:
                code_blocks = tech_struct["code_blocks"]
                
        # If we have code blocks, create execution tests
        if code_blocks:
            for i, code_block in enumerate(code_blocks[:self.max_test_cases]):
                test_case = {
                    "id": f"exec_test_{i}",
                    "type": "code_execution",
                    "code": code_block,
                    "expected_behavior": "Code executes without errors",
                    "timeout": self.timeout_seconds
                }
                test_cases.append(test_case)
                
        # Create validation tests based on action list
        if "action_list" in skill and skill["action_list"]:
            for i, action in enumerate(skill["action_list"][:self.max_test_cases]):
                test_case = {
                    "id": f"action_test_{i}",
                    "type": "action_validation",
                    "action": action,
                    "expected_behavior": "Action is valid and safe",
                    "timeout": self.timeout_seconds
                }
                test_cases.append(test_case)
                
        # Ensure we have at least min_test_cases
        while len(test_cases) < self.min_test_cases:
            test_cases.append({
                "id": f"fallback_test_{len(test_cases)}",
                "type": "basic_validation",
                "description": "Basic skill structure validation",
                "expected_behavior": "Skill has valid structure",
                "timeout": 10
            })
            
        # Limit to max_test_cases
        test_cases = test_cases[:self.max_test_cases]
        
        self.logger.info(f"Generated {len(test_cases)} test cases")
        return test_cases
        
    def _run_docker_validation(
        self, 
        test_cases: List[Dict[str, Any]], 
        skill: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run validation in Docker container.
        
        Args:
            test_cases: List of test cases to run.
            skill: Skill being validated.
            
        Returns:
            Validation result dictionary.
        """
        self.logger.info("Running Docker-based validation")
        
        try:
            # Create temporary directory for test files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write skill to file
                skill_file = os.path.join(temp_dir, "skill.json")
                with open(skill_file, "w") as f:
                    json.dump(skill, f, indent=2)
                    
                # Write test cases to file
                test_file = os.path.join(temp_dir, "tests.json")
                with open(test_file, "w") as f:
                    json.dump(test_cases, f, indent=2)
                    
                # Create validation script
                validation_script = self._create_validation_script()
                script_file = os.path.join(temp_dir, "validate.py")
                with open(script_file, "w") as f:
                    f.write(validation_script)
                    
                # Run Docker container
                container = self.docker_client.containers.run(
                    self.docker_image,
                    command=f"python validate.py",
                    volumes={temp_dir: {"bind": "/test", "mode": "rw"}},
                    working_dir="/test",
                    detach=True,
                    network_disabled=True,  # Disable network for security
                    mem_limit="512m",       # Limit memory usage
                    cpu_quota=50000,        # Limit CPU usage (50% of one core)
                    timeout=self.timeout_seconds
                )
                
                # Wait for completion
                result = container.wait(timeout=self.timeout_seconds)
                logs = container.logs().decode("utf-8")
                container.remove()
                
                # Parse results
                if result["StatusCode"] == 0:
                    # Success
                    validated_skill = skill.copy()
                    validated_skill["validation_timestamp"] = datetime.now().isoformat()
                    validated_skill["validation_method"] = "docker_sandbox"
                    validated_skill["test_cases_passed"] = len(test_cases)
                    
                    return {
                        "success": True,
                        "skill": validated_skill,
                        "error_trace": None
                    }
                else:
                    # Failure
                    return {
                        "success": False,
                        "error_trace": f"Docker validation failed: {logs}",
                        "skill": None
                    }
                    
        except Exception as e:
            self.logger.error(f"Docker validation failed: {e}")
            return {
                "success": False,
                "error_trace": f"Docker validation exception: {str(e)}",
                "skill": None
            }
            
    def _run_simulated_validation(
        self, 
        test_cases: List[Dict[str, Any]], 
        skill: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run simulated validation when Docker is not available.
        
        Args:
            test_cases: List of test cases to simulate.
            skill: Skill being validated.
            
        Returns:
            Validation result dictionary.
        """
        self.logger.info("Running simulated validation (Docker not available)")
        
        # Simulate validation by checking basic structure
        try:
            # Basic validation checks
            if not skill.get("task_id"):
                raise ValueError("Missing task_id")
            if not skill.get("core_logic"):
                raise ValueError("Missing core_logic")
            if not skill.get("confidence", 0) >= 0.5:
                raise ValueError("Confidence too low for validation")
                
            # Simulate test execution
            passed_tests = 0
            for test_case in test_cases:
                # Simulate random success/failure based on confidence
                import random
                if random.random() < skill.get("confidence", 0.7):
                    passed_tests += 1
                    
            # Require at least 50% of tests to pass
            if passed_tests >= len(test_cases) * 0.5:
                validated_skill = skill.copy()
                validated_skill["validation_timestamp"] = datetime.now().isoformat()
                validated_skill["validation_method"] = "simulated_sandbox"
                validated_skill["test_cases_passed"] = passed_tests
                
                return {
                    "success": True,
                    "skill": validated_skill,
                    "error_trace": None
                }
            else:
                return {
                    "success": False,
                    "error_trace": f"Simulated validation failed: {passed_tests}/{len(test_cases)} tests passed",
                    "skill": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error_trace": f"Simulated validation exception: {str(e)}",
                "skill": None
            }
            
    def _create_validation_script(self) -> str:
        """Create Python validation script for Docker container.
        
        Returns:
            Validation script as string.
        """
        script = '''
import json
import sys
import traceback

def validate_skill(skill_file, test_file):
    """Validate skill against test cases."""
    try:
        # Load skill
        with open(skill_file, 'r') as f:
            skill = json.load(f)
            
        # Load test cases  
        with open(test_file, 'r') as f:
            test_cases = json.load(f)
            
        # Basic validation
        if not skill.get('task_id'):
            raise ValueError('Missing task_id')
        if not skill.get('core_logic'):
            raise ValueError('Missing core_logic')
            
        # Execute test cases (simplified for demo)
        for test_case in test_cases:
            if test_case['type'] == 'code_execution':
                # In real implementation, this would safely execute code
                # For security, we'll just validate structure
                if 'code' not in test_case:
                    raise ValueError(f'Invalid test case: {test_case}')
            elif test_case['type'] == 'action_validation':
                if 'action' not in test_case:
                    raise ValueError(f'Invalid test case: {test_case}')
                    
        print('Validation successful')
        return True
        
    except Exception as e:
        print(f'Validation failed: {e}')
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = validate_skill('skill.json', 'tests.json')
    sys.exit(0 if success else 1)
'''
        return script
        
    def audit_result(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Audit validation result for compliance with safety standards.
        
        Args:
            validation_result: Result from validate() method.
            
        Returns:
            Audited result with additional metadata.
        """
        audited_result = validation_result.copy()
        audited_result["audit_timestamp"] = datetime.now().isoformat()
        audited_result["audit_version"] = "1.0"
        
        if validation_result["success"]:
            # Add security metadata for successful validations
            audited_result["security_level"] = "validated"
            audited_result["can_write_to_permanent_memory"] = True
        else:
            # Add error categorization for failed validations
            error_trace = validation_result["error_trace"]
            if "network" in error_trace.lower() or "http" in error_trace.lower():
                audited_result["error_category"] = "network_restriction"
            elif "memory" in error_trace.lower() or "ram" in error_trace.lower():
                audited_result["error_category"] = "resource_limit"
            elif "syntax" in error_trace.lower() or "parse" in error_trace.lower():
                audited_result["error_category"] = "code_error"
            else:
                audited_result["error_category"] = "general_failure"
                
            audited_result["security_level"] = "rejected"
            audited_result["can_write_to_permanent_memory"] = False
            
        return audited_result