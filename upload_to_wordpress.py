#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from wordpress_xmlrpc import Client, WordPressPost, WordPressMedia
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import sys

# WordPress配置
WP_URL = "https://datagov1.wordpress.com"
WP_USERNAME = "davidturing"  # 替换为实际用户名
WP_APP_PASSWORD = "your-app-password-here"  # 替换为实际应用密码

def upload_pdf_to_wordpress(pdf_path):
    """上传PDF到WordPress并返回直接下载链接"""
    try:
        # 创建WordPress客户端
        client = Client(f"{WP_URL}/xmlrpc.php", WP_USERNAME, WP_APP_PASSWORD)
        
        # 准备媒体文件
        with open(pdf_path, 'rb') as pdf_file:
            data = {
                'name': 'dama_handbook_final_v2.pdf',
                'type': 'application/pdf',
            }
            data['bits'] = xmlrpc_client.Binary(pdf_file.read())
            
            # 上传媒体文件
            response = client.call(media.UploadFile(data))
            attachment_id = response['id']
            attachment_url = response['link']
            
            print(f"PDF uploaded successfully!")
            print(f"Attachment ID: {attachment_id}")
            print(f"Direct download URL: {attachment_url}")
            
            return attachment_url
            
    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return None

if __name__ == "__main__":
    pdf_path = "/Users/zhaoqinhuang/david_project/damabook/dama_handbook_final_v2.pdf"
    if os.path.exists(pdf_path):
        print("Uploading PDF to WordPress...")
        download_url = upload_pdf_to_wordpress(pdf_path)
        if download_url:
            print(f"\n✅ Success! Direct download link: {download_url}")
        else:
            print("\n❌ Failed to upload PDF")
    else:
        print(f"PDF file not found: {pdf_path}")