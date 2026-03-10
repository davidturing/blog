#!/usr/bin/env python3
"""
WordPress XML-RPC 工具模块
包含 SSL 证书绕过和二进制传输处理
"""

import ssl
import xmlrpc.client
from typing import Dict, Any, Tuple

class WordPressTool:
    """WordPress XML-RPC 客户端工具"""
    
    def __init__(self, endpoint: str, username: str, password: str):
        """
        初始化 WordPress 客户端
        
        Args:
            endpoint: WordPress XML-RPC 端点地址
            username: 用户名
            password: 应用程序密码
        """
        # ⚠️ SSL 证书绕过 (macOS/Linux 环境必需)
        ssl._create_default_https_context = ssl._create_unverified_context
        
        self.endpoint = endpoint
        self.client = xmlrpc.client.ServerProxy(endpoint)
        self.username = username
        self.password = password
    
    def upload_file(self, file_path: str, file_name: str, content_type: str = "image/png") -> Dict[str, Any]:
        """
        上传文件到 WordPress 媒体库
        
        Args:
            file_path: 本地文件路径
            file_name: 文件名
            content_type: MIME 类型
            
        Returns:
            上传结果字典，包含 attachment_id 和 url
        """
        with open(file_path, 'rb') as f:
            # ⚠️ 必须使用 xmlrpc.client.Binary 封装二进制内容
            binary_data = xmlrpc.client.Binary(f.read())
        
        data = {
            'name': file_name,
            'type': content_type,
            'bits': binary_data,
            'overwrite': True
        }
        
        result = self.client.wp.uploadFile(
            0,  # blog_id (通常为0)
            self.username,
            self.password,
            data
        )
        
        return result
    
    def create_post(self, title: str, content: str, thumbnail_id: int = None) -> int:
        """
        创建并发布文章
        
        Args:
            title: 文章标题
            content: HTML 内容
            thumbnail_id: 特色图像 ID
            
        Returns:
            文章 ID
        """
        post_data = {
            'post_title': title,
            'post_content': content,
            'post_status': 'publish',
            'post_type': 'post'
        }
        
        if thumbnail_id:
            post_data['thumbnail'] = thumbnail_id
        
        post_id = self.client.wp.newPost(
            0,  # blog_id
            self.username,
            self.password,
            post_data
        )
        
        return post_id

def test_wordpress_connection(endpoint: str) -> bool:
    """测试 WordPress XML-RPC 连接"""
    try:
        client = xmlrpc.client.ServerProxy(endpoint)
        methods = client.system.listMethods()
        return 'wp.newPost' in methods and 'wp.uploadFile' in methods
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False