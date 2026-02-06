
import xmlrpc.client
import re
import os
import sys

# Try to import markdown, if not found, we will use a simple fallback or just raw text
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False
    print("Markdown library not found. Will attempt simple formatting.")

# Config
WP_USER = "davidturing"
WP_APP_PASS = "5hyx wocr tyom lwef"
WP_DOMAIN = "microblocks0.wordpress.com"
WP_XMLRPC_URL = f"https://{WP_DOMAIN}/xmlrpc.php"

CONTENT_FILE = "/Users/david/david_project/microblocks_about.md"

def preprocess_content(text):
    # Convert "Title：URL" lines to markdown links if they aren't already
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        match = re.search(r'^(\d+\.\s*.+?)[：:]\s*(https?://\S+)', line)
        if match:
            title_part = match.group(1)
            url = match.group(2)
            new_line = f"{title_part}: [{url}]({url})"
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

def convert_to_html(text):
    if HAS_MARKDOWN:
        return markdown.markdown(text)
    else:
        # Simple fallback conversion
        html = ""
        lines = text.split('\n')
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                html += "<br>\n"
                continue
                
            if line.startswith("# "):
                html += f"<h1>{line[2:]}</h1>\n"
            elif line.startswith("## "):
                html += f"<h2>{line[3:]}</h2>\n"
            elif line.startswith("### "):
                html += f"<h3>{line[4:]}</h3>\n"
            elif re.match(r'^\d+\.', line):
                if not in_list:
                    html += "<ul>\n" 
                    in_list = True
                
                # Linkify
                link_match = re.search(r'\[(.+?)\]\((.+?)\)', line)
                if link_match:
                    display = link_match.group(1)
                    url = link_match.group(2)
                    line_content = line.replace(f"[{display}]({url})", f'<a href="{url}">{display}</a>')
                else:
                    line_content = line
                
                html += f"<li>{line_content}</li>\n"
            else:
                html += f"<p>{line}</p>\n"
                
        if in_list:
            html += "</ul>\n"
            
        return html

import ssl

def publish_page_xmlrpc(title, content):
    print(f"Connecting to XML-RPC at {WP_XMLRPC_URL}...")
    
    # Bypass SSL verification
    context = ssl._create_unverified_context()
    server = xmlrpc.client.ServerProxy(WP_XMLRPC_URL, context=context)
    
    post_content = {
        'post_type': 'page',
        'post_title': title,
        'post_content': content,
        'post_status': 'publish'
    }
    
    try:
        # wp.newPost(blog_id, username, password, content)
        post_id = server.wp.newPost(0, WP_USER, WP_APP_PASS, post_content)
        print(f"Successfully published page! ID: {post_id}")
        return True
    except xmlrpc.client.Fault as err:
        print(f"A fault occurred")
        print(f"Fault code: {err.faultCode}")
        print(f"Fault string: {err.faultString}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    if not os.path.exists(CONTENT_FILE):
        print(f"Content file not found: {CONTENT_FILE}")
        return

    with open(CONTENT_FILE, 'r') as f:
        raw_text = f.read()
        
    processed_text = preprocess_content(raw_text)
    html_content = convert_to_html(processed_text)
    
    publish_page_xmlrpc("MicroBlocks 介绍", html_content)

if __name__ == "__main__":
    main()
