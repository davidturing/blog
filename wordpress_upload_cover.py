#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 图像上传脚本 - 封面图
"""
import xmlrpc.client
import base64
from pathlib import Path

# WordPress 配置
WP_URL = "https://dvspace5.wordpress.com/xmlrpc.php"
WP_USERNAME = "davidturing"
WP_PASSWORD = "your_app_password_here"  # 将从凭据文件加载

def upload_image(image_path, title, description=""):
    """上传单张图像到 WordPress"""
    try:
        # 读取图像文件
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
        
        # 准备上传数据
        data = {
            'name': Path(image_path).name,
            'type': 'image/png',
            'bits': xmlrpc.client.Binary(img_data),
            'overwrite': True
        }
        
        if title:
            data['title'] = title
        if description:
            data['caption'] = description
        
        # 创建 XML-RPC 客户端
        client = xmlrpc.client.ServerProxy(WP_URL)
        
        # 上传文件
        result = client.wp.uploadFile(0, WP_USERNAME, WP_PASSWORD, data)
        print(f"✅ 图像上传成功: {result['url']}")
        print(f"   ID: {result['id']}")
        return result
        
    except Exception as e:
        print(f"❌ 图像上传失败: {str(e)}")
        return None

if __name__ == "__main__":
    # 上传封面图
    cover_result = upload_image(
        "Cover_Image.png", 
        "2026 Python 数据分析师技术栈封面",
        "现代化 Python 数据分析技术栈概览"
    )