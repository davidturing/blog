#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress REST API 发布脚本
用于 WordPress.com 站点（XML-RPC 被禁用的情况）
"""

import requests
import json
import base64
from pathlib import Path

# WordPress 凭据
WP_SITE = "dvspace5.wordpress.com"
WP_USERNAME = "davidturing"
WP_APP_PASSWORD = "your_app_password_here"

# 从环境变量加载凭据
import os
WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD', WP_APP_PASSWORD)

# REST API 端点
REST_API_BASE = f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}"

def upload_media(file_path, title):
    """上传媒体文件到 WordPress"""
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Base64 编码
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'media': [{
            'name': f"{title}.png",
            'type': 'image/png',
            'bits': encoded_content,
            'overwrite': True
        }]
    }
    
    response = requests.post(
        f"{REST_API_BASE}/media/new",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        return result[0] if result else None
    else:
        print(f"上传失败: {response.status_code} - {response.text}")
        return None

def create_post(title, content, featured_image_id=None):
    """创建 WordPress 文章"""
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'title': title,
        'content': content,
        'status': 'publish',
        'categories': ['tech', 'python', 'data-science'],
        'tags': ['python', 'polars', 'duckdb', '2026', 'data-analysis']
    }
    
    if featured_image_id:
        data['featured_image'] = featured_image_id
    
    response = requests.post(
        f"{REST_API_BASE}/posts/new",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"发布失败: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # 加载文章内容
    with open('article_content.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = "2026年Python数据分析师首选技术栈选型"
    
    # 上传封面图
    cover_image = upload_media('Cover_Image.png', 'cover')
    featured_image_id = cover_image['ID'] if cover_image else None
    
    # 创建文章
    post = create_post(title, content, featured_image_id)
    
    if post:
        post_url = f"https://{WP_SITE}/?p={post['ID']}"
        print(f"发布成功!")
        print(f"文章ID: {post['ID']}")
        print(f"文章URL: {post_url}")
    else:
        print("发布失败")