#!/usr/bin/env python3
"""
WordPress执行器 - ag引擎的运动神经（Motor Cortex）
监听黑板上的READY_TO_PUBLISH状态，自动发布到WordPress
包含完整的重试机制和容错处理
"""

import os
import asyncio
import aiohttp
import base64
import json
from typing import Dict, Any, Optional
from pathlib import Path
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent


class WordPressExecutor:
    """WordPress执行器 - 负责物理输出动作，具备工业级可靠性"""
    
    def __init__(self, blackboard):
        """
        初始化WordPress执行器
        
        Args:
            blackboard: 全局状态黑板实例
        """
        self.blackboard = blackboard
        
        # WordPress XML-RPC API配置（从环境变量读取）
        base_url = os.getenv('WP_SITE_URL', 'https://dvspace5.wordpress.com')
        if base_url.endswith('xmlrpc.php'):
            self.wp_url = base_url
        else:
            self.wp_url = f"{base_url.rstrip('/')}/xmlrpc.php"
        self.wp_username = os.getenv('WP_USERNAME')
        self.wp_app_password = os.getenv('WP_APP_PASSWORD')  # WP应用密码，不是登录密码
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 2.0  # 初始重试延迟（秒）
        self.timeout = 30.0     # HTTP请求超时（秒）
        
        # 验证必要配置
        if not self.wp_username or not self.wp_app_password:
            raise ValueError("缺少WordPress认证配置：WP_USERNAME 和 WP_APP_PASSWORD 必须在环境变量中设置")
        
        # 启动神经元监听
        self.init_listeners()
        
    def init_listeners(self):
        """初始化事件监听器"""
        # 运动神经的唯一触发点：监听全局工作流状态
        self.blackboard.subscribe('state_changed:workflow_status', self._on_workflow_status_change)
        
    async def _on_workflow_status_change(self, status: str, old_status: str):
        """处理工作流状态变化"""
        # 只对"准备发布"状态做出反应
        if status != 'READY_TO_PUBLISH':
            return
            
        print("🚀 [执行器-Motor] 接收到左脑的绿色通行证，准备执行全网发布...")
        
        # 1. 从黑板获取最终通过审查的文章内容
        final_draft = await self.blackboard.read('draft_content')
        
        if not final_draft:
            print("❌ [执行器-Motor] 错误：状态为就绪，但黑板上找不到草稿内容！")
            self.blackboard.update('workflow_status', 'ERROR', 'EXECUTOR')
            return
            
        try:
            # 2. 解析标题和正文
            title, content = self._parse_markdown(final_draft)
            
            # 3. 执行物理动作：调用WordPress API（带重试机制）
            publish_result = await self._push_to_wordpress_with_retry(title, content)
            
            print(f"🎉 [执行器-Motor] 发布大成功！文章已上线。")
            print(f"🔗 [文章链接]: {publish_result.get('link', 'N/A')}")
            
            # 追踪：记录发布结果
            self.blackboard.append_trace('PUBLISH', f'WordPress 发布成功: {publish_result.get("link", "N/A")}', {
                'post_id': publish_result.get('id'),
                'link': publish_result.get('link', 'N/A')
            })
            
            # 4. 更新最终状态，ag引擎完成一个完整的生命周期
            self.blackboard.update('workflow_status', 'PUBLISHED', 'EXECUTOR')
            
            # 彻底清空黑板，进入待机状态，准备吃下一口草料
            # await self.blackboard.clear()
            
        except Exception as e:
            self.blackboard.append_trace('PUBLISH', f'WordPress 发布失败: {e}')
            print(f"❌ [执行器-Motor] 发布到WordPress失败: {e}")
            self.blackboard.update('workflow_status', 'ERROR', 'EXECUTOR')
            
    def _parse_markdown(self, markdown_text: str) -> tuple[str, str]:
        """
        从Markdown中剥离标题和正文
        
        Args:
            markdown_text: Markdown格式的文章内容
            
        Returns:
            tuple: (标题, 正文内容)
        """
        lines = markdown_text.split('\n')
        title = 'ag 引擎自动生成的科技博文'
        content_lines = []
        
        # 寻找第一个H1标题作为文章标题
        for line in lines:
            if line.startswith('# ') and title == 'ag 引擎自动生成的科技博文':
                title = line.replace('# ', '').strip()
            else:
                content_lines.append(line)
                
        return title, '\n'.join(content_lines)
        
    async def _push_to_wordpress_with_retry(self, title: str, content: str) -> Dict[str, Any]:
        """
        带重试机制的WordPress发布
        
        Args:
            title: 文章标题
            content: 文章内容（Markdown或HTML）
            
        Returns:
            dict: WordPress API响应
            
        Raises:
            Exception: 所有重试都失败后抛出异常
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await self._push_to_wordpress(title, content)
                return result
                
            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)  # 指数退避
                    print(f"⚠️ [执行器-Motor] WordPress API请求失败 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}")
                    print(f"   等待 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    print(f"❌ [执行器-Motor] 所有重试都失败了: {e}")
                    
            except asyncio.TimeoutError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    print(f"⚠️ [执行器-Motor] WordPress API请求超时 (尝试 {attempt + 1}/{self.max_retries + 1})")
                    print(f"   等待 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    print(f"❌ [执行器-Motor] 所有重试都超时了")
                    
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    print(f"⚠️ [执行器-Motor] WordPress发布遇到未知错误 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}")
                    print(f"   等待 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    print(f"❌ [执行器-Motor] 未知错误导致所有重试失败: {e}")
        
        # 如果所有重试都失败，抛出最后一个异常
        raise last_exception
        
    async def _push_to_wordpress(self, title: str, content: str) -> Dict[str, Any]:
        """
        发送XML-RPC请求发布到WordPress
        
        Args:
            title: 文章标题
            content: 文章内容（Markdown或HTML）
            
        Returns:
            dict: 成功时包含文章id和链接的字典
        """
        import xmlrpc.client
        
        def _sync_push():
            server = xmlrpc.client.ServerProxy(self.wp_url)
            
            post_data = {
                'post_type': 'post',
                'post_title': title,
                'post_content': content,
                'post_status': 'publish'
            }
            
            # wp.newPost(blog_id, username, password, content)
            post_id = server.wp.newPost(1, self.wp_username, self.wp_app_password, post_data)
            return {'id': post_id, 'link': f"{self.wp_url.replace('/xmlrpc.php', '')}/?p={post_id}"}
            
        try:
            return await asyncio.to_thread(_sync_push)
        except Exception as e:
            raise Exception(f"WordPress XML-RPC Error: {e}")


# 为了兼容性，也提供同步版本（如果需要的话）
class WordPressExecutorSync:
    """WordPress执行器同步版本（备用）"""
    
    def __init__(self, blackboard):
        self.blackboard = blackboard
        base_url = os.getenv('WP_SITE_URL', 'https://dvspace5.wordpress.com')
        if base_url.endswith('/posts'):
            self.wp_url = base_url
        else:
            self.wp_url = f"{base_url.rstrip('/')}/wp-json/wp/v2/posts"
        self.wp_username = os.getenv('WP_USERNAME')
        self.wp_app_password = os.getenv('WP_APP_PASSWORD')
        
        if not self.wp_username or not self.wp_app_password:
            raise ValueError("缺少WordPress认证配置")
            
        self.init_listeners()
        
    def init_listeners(self):
        """同步版本的监听器（需要配合事件循环）"""
        pass  # 实际使用中建议使用异步版本