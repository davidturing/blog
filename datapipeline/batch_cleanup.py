
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
Your task is to rewrite the provided WordPress content.

**Requirements:**
1.  **Language**: Translate everything into **Simplified Chinese (简体中文)**.
2.  **Style**: Use a friendly, encouraging, and easy-to-understand tone (beginner-friendly). Expand on difficult concepts to make them clearer.
3.  **Formatting**:
    -   **CRITICAL**: You MUST preserve all HTML tags for images (`<img>`), videos (`<video>`, `<iframe>`), and links (`<a>`). EXACTLY as they are. Do not translate the URLs.
    -   **CRITICAL**: Translate the **Anchor Text** of links (`<a ...>Translate This</a>`), but NOT the `href`.
    -   Translate the headers (h1, h2, etc.) and paragraph text.
4.  **Content**:
    -   If the content is very short, expand it intelligently based on the context.
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

def process_item(server, item_id, item_type='post'):
    print(f"Processing {item_type.upper()} ID {item_id}...")
    
    try:
        if item_type == 'post':
            p = server.wp.getPost(0, WP_USER, WP_APP_PASS, item_id)
            title = p['post_title']
            content = p['post_content']
        else:
            p = server.wp.getPage(0, WP_USER, WP_APP_PASS, item_id)
            title = p['page_title'] # Often 'title' but getPage returns struct
            if not title: title = p.get('title', 'Untitled')
            content = p.get('description', '') # 'description' field usually holds body for pages
            
        print(f"  -> Title: {title}")
        
        # Rewrite
        new_content = rewrite_content(title, content)
        if not new_content:
            print("  -> Failed to generate.")
            return

        # Translate Title
        try:
            title_resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Translate: {title}. Return ONLY Chinese title."
            )
            new_title = title_resp.text.strip().replace('"', '').replace('title:', '')
        except:
            new_title = title
            
        print(f"  -> New Title: {new_title}")
        
        # Update
        update_data = {
            'post_title' if item_type == 'post' else 'page_title': new_title,
            'post_content' if item_type == 'post' else 'page_description': new_content
        }
        
        # XML-RPC keys vary. editPost uses post_content. editPage usually structurally similar but let's check.
        # wp.editPage(blog_id, username, password, page_id, content_struct, publish)
        
        if item_type == 'post':
            server.wp.editPost(0, WP_USER, WP_APP_PASS, item_id, update_data)
        else:
            # For pages, fields might be different.
            # Usually struct with 'title', 'description', etc.
            page_data = {
                'title': new_title,
                'description': new_content
            }
            server.wp.editPage(0, WP_USER, WP_APP_PASS, item_id, page_data)
            
        print("  -> Success!")
        
    except Exception as e:
        print(f"  -> Error: {e}")

def main():
    server = get_server()
    
    # 1. Failed Posts
    failed_posts = [8, 14, 20, 32, 40, 42]
    # failed_posts = [42] # Test single if needed, but let's do all
    
    for pid in failed_posts:
        process_item(server, pid, 'post')
        time.sleep(5) # Slow down
        
    # 2. Page 192 (About/Introduction)
    process_item(server, 192, 'page')

if __name__ == "__main__":
    main()
