
import xmlrpc.client
import ssl
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Config
WP_USER = "davidturing"
WP_APP_PASS = "5hyx wocr tyom lwef"
WP_DOMAIN = "microblocks0.wordpress.com"
WP_XMLRPC_URL = f"https://{WP_DOMAIN}/xmlrpc.php"

load_dotenv("/Users/david/david_project/.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

REWRITE_PROMPT = """
You are an expert technical writer and translator, acting as "Doubao" (a helpful AI assistant).
Your task is to rewrite the provided WordPress Page content.

**Requirements:**
1.  **Language**: Translate everything into **Simplified Chinese (简体中文)**.
2.  **Style**: Use a friendly, encouraging, and easy-to-understand tone.
3.  **Formatting**:
    -   **CRITICAL**: You MUST preserve all HTML tags EXACTLY.
    -   **CRITICAL: LINK LISTS**: This page likely contains a list of links to other posts. You MUST translate the **Anchor Text** (the clickable text) of these links to Chinese, ensuring they match the context of the linked articles. DO NOT change the structure or `href` of the links.
    -   Translate headers and descriptions.

**Input Content:**
"""

def get_server():
    context = ssl._create_unverified_context()
    return xmlrpc.client.ServerProxy(WP_XMLRPC_URL, context=context)

def main():
    server = get_server()
    PAGE_ID = 192
    
    print(f"Fetching Page {PAGE_ID}...")
    try:
        # wp.getPage(blog_id, page_id, username, password)
        # Note: Some implementations put username/password first. WordPress XML-RPC usually:
        # wp.getPage(blog_id, page_id, username, password) OR
        # wp.getPage(blog_id, page_id, username, password)
        # Let's try standard signature: blog_id, page_id, username, password
        page = server.wp.getPage(0, PAGE_ID, WP_USER, WP_APP_PASS)
        
        title = page.get('title', 'Untitled') # it's 'page_title' or 'title' depending on endpoint
        content = page.get('description', '') # Content usually in 'description' or 'text_more'
        
        print(f"Original Title: {title}")
        print(f"Original Content Length: {len(content)}")
        
        # Rewrite
        print("Sending to AI...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_text(text=REWRITE_PROMPT),
                types.Part.from_text(text=f"Title: {title}\n\nContent:\n{content}")
            ]
        )
        new_content = response.text
        
        # Translate Title
        title_resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Translate: {title}. Return ONLY Chinese title."
        )
        new_title = title_resp.text.strip().replace('"', '').replace('title:', '')
        
        print(f"New Title: {new_title}")
        
        # Update
        # wp.editPage(blog_id, page_id, username, password, content_struct, publish)
        # content_struct keys: title, description, mt_text_more, ...
        content_struct = {
            'title': new_title,
            'description': new_content,
            'mt_allow_comments': 1,  # Sometimes required
            'mt_allow_pings': 1
        }
        
        print("Updating page...")
        server.wp.editPage(0, PAGE_ID, WP_USER, WP_APP_PASS, content_struct, True)
        print("Success!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
