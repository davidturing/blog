#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
升级 Google Generative AI SDK 到新的 google-genai 包
替换所有 google.generativeai 导入为 google.genai
"""

import os
import re
import shutil
from pathlib import Path

def upgrade_file(file_path):
    """升级单个文件的导入语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含旧的导入
        if 'google.generativeai' not in content:
            return False
        
        # 创建备份
        backup_path = str(file_path) + '.backup'
        shutil.copy2(file_path, backup_path)
        
        # 替换导入语句
        # 基本导入替换
        content = re.sub(r'import google\.generativeai as genai', 'import google.genai as genai', content)
        content = re.sub(r'from google\.generativeai import', 'from google.genai import', content)
        
        # 特殊情况处理
        content = re.sub(r'google\.generativeai\.GenerativeModel', 'google.genai.GenerativeModel', content)
        content = re.sub(r'google\.generativeai\.types', 'google.genai.types', content)
        content = re.sub(r'google\.generativeai\.embed_content', 'google.genai.embed_content', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 升级完成: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 升级失败 {file_path}: {e}")
        return False

def find_and_upgrade_files(project_root):
    """查找并升级所有相关文件"""
    project_path = Path(project_root)
    upgraded_files = []
    
    # 查找 Python 文件
    for py_file in project_path.rglob("*.py"):
        if upgrade_file(py_file):
            upgraded_files.append(str(py_file))
    
    return upgraded_files

if __name__ == "__main__":
    project_root = "/Users/zhaoqinhuang/david_project"
    print("🚀 开始升级 Google Generative AI SDK...")
    print(f"项目根目录: {project_root}")
    
    upgraded_files = find_and_upgrade_files(project_root)
    
    if upgraded_files:
        print(f"\n🎉 升级完成！共升级 {len(upgraded_files)} 个文件:")
        for file in upgraded_files:
            print(f"  - {file}")
    else:
        print("\nℹ️  未找到需要升级的文件")
    
    print("\n✅ 升级脚本执行完成！")