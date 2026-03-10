#!/usr/bin/env python3
import xmlrpc.client
import os

# Load credentials
with open('.credentials/wordpress.env', 'r') as f:
    creds = {}
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            creds[key] = value

username = creds.get('WORDPRESS_USERNAME', '')
password = creds.get('WORDPRESS_PASSWORD', '')

# WordPress XML-RPC endpoint
wp_url = "https://dvspace5.wordpress.com/xmlrpc.php"

try:
    # Create client
    client = xmlrpc.client.ServerProxy(wp_url)
    
    # Test basic method
    methods = client.mw.getRecentPosts('', username, password, 1)
    print("✅ XML-RPC connection successful!")
    print(f"Recent posts count: {len(methods)}")
    
except Exception as e:
    print(f"❌ XML-RPC connection failed: {e}")
    print(f"Error type: {type(e).__name__}")