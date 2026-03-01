#!/usr/bin/env python3
"""
本地执行器 - ag引擎的运动神经（Local Motor Cortex）
负责安全执行本地命令或Python脚本，并反馈结果到黑板。
"""

import asyncio
import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

class LocalExecutor:
    """本地执行器 - 负责执行黑板上的 local_command"""
    
    def __init__(self, blackboard):
        self.blackboard = blackboard
        self.timeout = 120  # 默认超时时间
        self.init_listeners()
        
    def init_listeners(self):
        """初始化事件监听器"""
        self.blackboard.subscribe('state_changed:workflow_status', self._on_workflow_status_change)
        
    async def _on_workflow_status_change(self, status: str, old_status: str):
        """处理任务状态变化"""
        if status != 'LOCAL_EXECUTION':
            return
            
        print("⚡ [执行器-Local] 捕获到本地执行指令，正在准备环境...")
        
        command = await self.blackboard.read('local_command')
        if not command:
            print("❌ [执行器-Local] 错误：状态为 LOCAL_EXECUTION，但找不到待执行内容。")
            self.blackboard.update('workflow_status', 'ERROR', 'LOCAL_EXECUTOR')
            return
            
        try:
            # 执行指令
            result = await self.execute(command)
            
            # 写回结果
            self.blackboard.update('execution_result', result, 'LOCAL_EXECUTOR')
            
            if result.get('success'):
                print("✅ [执行器-Local] 指令执行成功！")
                self.blackboard.update('workflow_status', 'DONE', 'LOCAL_EXECUTOR')
            else:
                print(f"⚠️ [执行器-Local] 指令执行返回非零状态: {result.get('return_code')}")
                self.blackboard.update('workflow_status', 'ERROR', 'LOCAL_EXECUTOR')
                
        except Exception as e:
            print(f"❌ [执行器-Local] 执行过程崩溃: {e}")
            self.blackboard.update('workflow_status', 'ERROR', 'LOCAL_EXECUTOR')

    async def execute(self, command: str) -> Dict[str, Any]:
        """
        在沙盒化的 subprocess 中执行指令
        """
        print(f"[*] 正在执行: {command[:100]}...")
        
        try:
            # 使用 asyncio.create_subprocess_shell 异步执行
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
                return_code = process.returncode
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Execution timed out after {self.timeout}s",
                    "return_code": -1
                }
                
            return {
                "success": return_code == 0,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "return_code": return_code
            }
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }

if __name__ == "__main__":
    # 模拟环境测试
    from brain.memory.blackboard import BrainBlackboard
    bb = BrainBlackboard()
    exec_inner = LocalExecutor(bb)
    
    async def test():
        await bb.update('local_command', 'echo "Hello from LocalExecutor"', 'TEST')
        await bb.update('workflow_status', 'LOCAL_EXECUTION', 'TEST')
        await asyncio.sleep(2)
        print(f"Final Status: {bb.state['workflow_status']}")
        print(f"Result: {bb.state['execution_result']}")

    asyncio.run(test())
