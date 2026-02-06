
import xmlrpc.client
import ssl
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Config
WP_USER = "davidturing"
WP_APP_PASS = "5hyx wocr tyom lwef"
WP_DOMAIN = "microblocks0.wordpress.com"
WP_XMLRPC_URL = f"https://{WP_DOMAIN}/xmlrpc.php"

# Load Gemini
load_dotenv("/Users/david/david_project/.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

REWRITE_PROMPT = """
You are an expert technical writer and translator, acting as "Doubao" (a helpful AI assistant).
Your task is to rewrite the provided WordPress blog post content.

**Requirements:**
1.  **Language**: Translate everything into **Simplified Chinese (简体中文)**.
2.  **Style**: Use a friendly, encouraging, and easy-to-understand tone (beginner-friendly). Expand on difficult concepts to make them clearer.
3.  **Formatting**:
    -   **CRITICAL**: You MUST preserve all HTML tags for images (`<img>`), videos (`<video>`, `<iframe>`), and links (`<a>`). EXACTLY as they are. Do not translate the URLs.
    -   Translate the headers (h1, h2, etc.) and paragraph text.
4.  **Content**:
    -   If the content is very short, expand it intelligently based on the context (it is about MicroBlocks, physical computing, education).
    -   Do not output markdown code blocks. Output raw HTML content ready for WordPress.

**Input Content:**
"""

def get_server():
    context = ssl._create_unverified_context()
    return xmlrpc.client.ServerProxy(WP_XMLRPC_URL, context=context)

def rewrite_content(title, content):
    print(f"  -> Sending to AI...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_text(text=REWRITE_PROMPT),
                types.Part.from_text(text=f"Title: {title}\n\nContent:\n{content}")
            ]
        )
        return response.text
    except Exception as e:
        print(f"  -> AI Error: {e}")
        return None

import concurrent.futures
import re

def is_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def process_post(p):
    pid = p['post_id']
    title = p['post_title']
    content = p['post_content']
    
    # Skip if ID 200, 6 or already Chinese
    if str(pid) in ['200', '6']:
        print(f"Skipping ID {pid} (Protected)")
        return
        
    if is_chinese(title):
        print(f"Skipping ID {pid} (Already Chinese): {title}")
        return

    print(f"Processing ID {pid}: {title}...")
    
    # 1. Generate New Content
    new_content = rewrite_content(title, content)
    
    if not new_content:
        print(f"  -> [ID {pid}] Failed to generate content.")
        return
        
    # 2. Translate Title
    try:
        title_resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Translate this blog post title to Simplified Chinese: {title}. Return ONLY the title."
        )
        new_title = title_resp.text.strip().replace('"', '').replace('title:', '')
    except:
        new_title = title
        
    print(f"  -> [ID {pid}] New Title: {new_title}")
    
    # 3. Update Post
    # Create a new server instance for thread safety
    server = get_server()
    update_data = {
        'post_title': new_title,
        'post_content': new_content
    }
    
    try:
        server.wp.editPost(0, WP_USER, WP_APP_PASS, pid, update_data)
        print(f"  -> [ID {pid}] Update Success!")
    except Exception as e:
        print(f"  -> [ID {pid}] Update Failed: {e}")

def main():
    server = get_server()
    print("Fetching posts...")
    posts = server.wp.getPosts(0, WP_USER, WP_APP_PASS, {'number': 100})
    print(f"Found {len(posts)} posts. Starting parallel processing (max 5 threads)...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_post, posts)

if __name__ == "__main__":
    main()
