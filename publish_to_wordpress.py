#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publish blog post to WordPress with image
"""

import os
import requests
from base64 import b64encode

# Load WordPress credentials
wordpress_env = {}
with open('.credentials/wordpress.env', 'r') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            wordpress_env[key] = value

WP_URL = "https://dvspace5.wordpress.com/wp-json/wp/v2"
USERNAME = "davidturing"
PASSWORD = wordpress_env.get('WORDPRESS_APP_PASSWORD')

def upload_image(image_path, title):
    """Upload image to WordPress"""
    with open(image_path, 'rb') as img:
        image_data = img.read()
    
    headers = {
        'Content-Type': 'image/png',
        'Authorization': 'Basic ' + b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    }
    
    files = {'file': (os.path.basename(image_path), image_data, 'image/png')}
    data = {'title': title}
    
    response = requests.post(
        f"{WP_URL}/media",
        headers=headers,
        files=files,
        data=data
    )
    
    if response.status_code == 201:
        return response.json()['id'], response.json()['source_url']
    else:
        print(f"Image upload failed: {response.status_code} - {response.text}")
        return None, None

def publish_post(title, content, image_id=None):
    """Publish post to WordPress"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    }
    
    # Add featured image if provided
    post_data = {
        'title': title,
        'content': content,
        'status': 'publish'
    }
    
    if image_id:
        post_data['featured_media'] = image_id
    
    response = requests.post(
        f"{WP_URL}/posts",
        headers=headers,
        json=post_data
    )
    
    if response.status_code == 201:
        return response.json()['link']
    else:
        print(f"Post publish failed: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # Read blog content
    with open('blog_content_with_image.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Upload image
    image_id, image_url = upload_image('tech_architecture_diagram.png', '2026 Python Data Analyst Tech Stack')
    
    if image_id:
        # Update content to include image
        html_content = f'<img src="{image_url}" alt="2026 Python Data Analyst Technology Architecture" style="width:100%; max-width:800px; height:auto; margin:20px 0;">\n\n' + content.replace('\n', '<br>\n')
    else:
        html_content = content.replace('\n', '<br>\n')
    
    # Publish post
    post_url = publish_post(
        '🚀 2026 Python数据分析师生存指南：从"Hello World"到企业级AI战士的终极装备清单！',
        html_content,
        image_id
    )
    
    if post_url:
        print(f"Blog post published successfully: {post_url}")
    else:
        print("Failed to publish blog post")