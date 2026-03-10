#!/usr/bin/env python3
"""
Simple Share Tweet to WordPress - Bypass moderation for testing
"""

import os
import sys
import json
import requests
import time
from dotenv import load_dotenv
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.compat import xmlrpc_client

# Load env
load_dotenv(override=True)

# WordPress Config
WP_USER = os.getenv("WORDPRESS_USERNAME") or "davidturing" 
WP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD") 
WP_URL = os.getenv("WORDPRESS_URL", "https://dvspace5.wordpress.com")
XMLRPC_ENDPOINT = f"{WP_URL.rstrip('/')}/xmlrpc.php"

def fetch_tweet_content(tweet_url):
    """Fetch tweet content using api.fxtwitter.com (JSON)."""
    print(f"Fetching tweet: {tweet_url}...")
    
    try:
        parts = tweet_url.split('/')
        if 'status' in parts:
            status_idx = parts.index('status')
            tweet_id = parts[status_idx + 1].split('?')[0]
            username = parts[status_idx - 1]
            
            api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"
            print(f"Querying API: {api_url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = requests.get(api_url, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == 200 and 'tweet' in data:
                    tweet = data['tweet']
                    text = tweet.get('text', '')
                    author = tweet.get('author', {}).get('name', 'Unknown')
                    author_id = tweet.get('author', {}).get('screen_name', username)
                    
                    images = []
                    if 'media' in tweet and 'photos' in tweet['media']:
                        for p in tweet['media']['photos']:
                            images.append(p['url'])
                            
                    print(f"✅ Fetched Standard Tweet: {text[:50]}...")
                    return {
                        "type": "tweet",
                        "text": text,
                        "author": author,
                        "username": author_id,
                        "images": images,
                        "url": tweet_url
                    }
    except Exception as e:
        print(f"⚠️ FxTwitter API fetch failed: {e}")
    return None

def upload_image_xmlrpc(client, image_url):
    """Upload image via XML-RPC."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(image_url, headers=headers, timeout=30)
        resp.raise_for_status()
        img_data = resp.content
        
        base_name = os.path.basename(image_url.split('?')[0])
        filename = f"tw_{int(time.time())}_{base_name}"
        if not filename.endswith(('.jpg', '.png', '.jpeg', '.gif', '.webp')):
            filename += ".jpg"
        
        data = {
            'name': filename,
            'type': resp.headers.get('Content-Type', 'image/jpeg'),
            'bits': xmlrpc_client.Binary(img_data),
            'overwrite': False,
        }
        response = client.call(media.UploadFile(data))
        return response.get('url')
    except Exception as e:
        print(f"Image Upload Failed: {e} | URL: {image_url}")
        return None

def run(tweet_url):
    # 1. Fetch
    tweet_data = fetch_tweet_content(tweet_url)
    if not tweet_data:
        print("❌ Failed to fetch tweet content.")
        return
    
    # 2. Connect to WordPress
    print("Connecting to WordPress...")
    try:
        client = Client(XMLRPC_ENDPOINT, WP_USER, WP_PASSWORD)
    except Exception as e:
        print(f"WP Connection Failed: {e}")
        return

    # 3. Upload Images
    uploaded_map = {}
    images_to_process = list(set(tweet_data["images"]))
    
    if images_to_process:
        print(f"Found {len(images_to_process)} images. Uploading...")
        for img_url in images_to_process:
            wp_img = upload_image_xmlrpc(client, img_url)
            if wp_img:
                print(f"  -> Uploaded: {wp_img}")
                uploaded_map[img_url] = wp_img
            else:
                print(f"  -> Failed to upload: {img_url}")

    # 4. Construct Content
    username = tweet_data.get('username', 'Unknown')
    post_title = "斯坦福大学 Vibe Coding 课程分享"
    
    content_html = f"<h3>来自 @{username} 的分享</h3>"
    content_html += f"<blockquote>{tweet_data['text'].replace(chr(10), '<br>')}</blockquote>"
    
    # Add images
    if uploaded_map:
        content_html += "<div style='margin-top:15px;'>"
        for orig_url, wp_url in uploaded_map.items():
            content_html += f"<img src='{wp_url}' style='max-width:100%; margin-bottom:10px; display:block; border-radius:4px;' />"
        content_html += "</div>"
    
    content_html += f"<p>原文链接: <a href='{tweet_url}'>{tweet_url}</a></p>"

    # 5. Publish
    post = WordPressPost()
    post.title = post_title
    post.content = content_html
    post.post_status = 'publish'
    
    try:
        print(f"Publishing to WordPress: {post_title}...")
        post_id = client.call(posts.NewPost(post))
        print(f"SUCCESS: Post published! Link: {WP_URL}/?p={post_id}")
        return True
    except Exception as e:
        print(f"Publish Failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 share_tweet_simple.py <tweet_url>")
    else:
        run(sys.argv[1])