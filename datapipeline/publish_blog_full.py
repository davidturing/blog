
import xmlrpc.client
import ssl
import os
import mimetypes
from bs4 import BeautifulSoup
from pathlib import Path

# Config
WP_USER = "davidturing"
WP_APP_PASS = "5hyx wocr tyom lwef"
WP_DOMAIN = "microblocks0.wordpress.com"
WP_XMLRPC_URL = f"https://{WP_DOMAIN}/xmlrpc.php"

HTML_FILE = Path("/Users/david/david_project/microblocks_guide.html")
PROJECT_ROOT = Path("/Users/david/david_project")

def get_server():
    # Bypass SSL verification
    context = ssl._create_unverified_context()
    return xmlrpc.client.ServerProxy(WP_XMLRPC_URL, context=context)

def upload_image(server, image_path):
    print(f"Uploading image: {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return None
        
    filename = os.path.basename(image_path)
    mime_type, _ = mimetypes.guess_type(image_path)
    
    with open(image_path, 'rb') as f:
        data = f.read()
        
    image_data = {
        'name': filename,
        'type': mime_type or 'image/png',
        'bits': xmlrpc.client.Binary(data),
        'overwrite': False
    }
    
    try:
        response = server.wp.uploadFile(0, WP_USER, WP_APP_PASS, image_data)
        url = response.get('url')
        print(f"  -> Uploaded to: {url}")
        return url
    except Exception as e:
        print(f"  -> Upload failed: {e}")
        return None

def process_html_and_publish():
    server = get_server()
    
    if not HTML_FILE.exists():
        print("HTML file not found.")
        return
        
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
    # 1. Extract Details
    title = str(soup.title.string) if soup.title and soup.title.string else "MicroBlocks Guide"
    
    # 2. Handle Images
    images = soup.find_all('img')
    for img in images:
        src = img.get('src')
        if src and not src.startswith(('http://', 'https://')):
            # Resolve local path
            # The src in HTML is like 'images/foo.png'
            # The FILE is in PROJECT_ROOT.
            # So local path is PROJECT_ROOT / src
            local_path = PROJECT_ROOT / src
            
            new_url = upload_image(server, str(local_path))
            if new_url:
                img['src'] = new_url
                # Remove srcset if it exists to avoid confusion
                if img.has_attr('srcset'):
                    del img['srcset']
            
    # 3. Prepare Content
    # We want to keep the <style> and the <body> content.
    # WordPress might strip <style> tags in the body, but it's worth a try.
    # Alternatively, we convert styles to inline, but that's complex.
    # For now, let's concatenate style + body content.
    
    content_parts = []
    
    # Add Styles
    styles = soup.find_all('style')
    for style in styles:
        content_parts.append(str(style))
        
    # Add Body Content (excluding scripts if any)
    if soup.body:
        # We process the body children
        for child in soup.body.children:
            if child.name != 'script':
                content_parts.append(str(child))
    else:
        # Fallback if no body tag
        content_parts.append(str(soup))
        
    final_content = "\n".join(content_parts)
    
    # 4. Publish
    post_content = {
        'post_type': 'post', # Publishing as a blog POST, not a page
        'post_title': title,
        'post_content': final_content,
        'post_status': 'publish'
    }
    
    print(f"Publishing post: '{title}'...")
    try:
        post_id = server.wp.newPost(0, WP_USER, WP_APP_PASS, post_content)
        print(f"Successfully published! Post ID: {post_id}")
    except Exception as e:
        print(f"Publish failed: {e}")

if __name__ == "__main__":
    process_html_and_publish()
