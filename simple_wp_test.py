#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost

# 测试 dvspace5
print("Testing dvspace5.wordpress.com...")
try:
    client = Client('https://dvspace5.wordpress.com/xmlrpc.php', 'davidturing', '2oen cgw4 gh5k z3tn')
    posts = client.call(GetPosts({'number': 1}))
    print(f"✅ dvspace5 connection successful! Found {len(posts)} recent posts.")
except Exception as e:
    print(f"❌ dvspace5 connection failed: {e}")

# 测试 datagov1  
print("\nTesting datagov1.wordpress.com...")
try:
    # 使用相同的密码（假设两个站点使用相同的应用密码）
    client = Client('https://datagov1.wordpress.com/xmlrpc.php', 'davidturing', '2oen cgw4 gh5k z3tn')
    posts = client.call(GetPosts({'number': 1}))
    print(f"✅ datagov1 connection successful! Found {len(posts)} recent posts.")
except Exception as e:
    print(f"❌ datagov1 connection failed: {e}")