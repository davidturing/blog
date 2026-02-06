
import requests
import re
import os
import json
from bs4 import BeautifulSoup
from pathlib import Path
import hashlib

# Config
SOURCE_FILE = "/Users/david/david_project/microblocks_about.md"
DOWNLOAD_DIR = Path("/Users/david/david_project/知识库/microblock/download")
METADATA_FILE = DOWNLOAD_DIR / "metadata.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def extract_urls(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Regex to find links: [Title](URL) or just URLs
    # The file has lines like "1. Title：URL"
    urls = []
    
    # Pattern for plain URLs in text
    # Looking for http/https, stopping at whitespace or newline
    # Also handle the "Title：URL" format specifically from the file
    lines = content.split('\n')
    for line in lines:
        # Match standard markdown links: [text](url)
        md_match = re.search(r'\[.*?\]\((https?://\S+)\)', line)
        if md_match:
            urls.append(md_match.group(1))
            continue
            
        # Match raw links: https://...
        raw_match = re.search(r'(https?://\S+)', line)
        if raw_match:
            # Clean up trailing content if any (like closing parenthesis if inside text)
            url = raw_match.group(1).rstrip(').,')
            urls.append(url)
            
    return sorted(list(set(urls)))

def fetch_url(url):
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text, response.status_code
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, 0

def save_content(url, html_content):
    if not html_content:
        return None

    # Create a safe filename hash
    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
    
    # Try to get a readable title from HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.title.string.strip() if soup.title else "No Title"
    clean_title = re.sub(r'[^\w\s-]', '', title)[:50].strip().replace(' ', '_')
    
    filename_base = f"{url_hash}_{clean_title}"
    
    # Save Raw HTML
    html_path = DOWNLOAD_DIR / f"{filename_base}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    # Extract and Save Text (Main content)
    # Remove scripts, styles
    for script in soup(["script", "style", "nav", "footer"]):
        script.extract()
        
    text_content = soup.get_text(separator='\n\n')
    # Clean up excessive newlines
    text_content = re.sub(r'\n{3,}', '\n\n', text_content).strip()
    
    text_path = DOWNLOAD_DIR / f"{filename_base}.txt"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(f"URL: {url}\nTitle: {title}\n\n{text_content}")
        
    return {
        "url": url,
        "title": title,
        "html_path": str(html_path),
        "text_path": str(text_path),
        "filename_base": filename_base
    }

def main():
    if not DOWNLOAD_DIR.exists():
        DOWNLOAD_DIR.mkdir(parents=True)
        
    urls = extract_urls(SOURCE_FILE)
    print(f"Found {len(urls)} distinct URLs.")
    
    metadata = []
    
    for i, url in enumerate(urls):
        print(f"Processing {i+1}/{len(urls)}: {url}")
        html, status = fetch_url(url)
        if html:
            entry = save_content(url, html)
            if entry:
                metadata.append(entry)
        else:
            print(f"Skipping {url} due to download failure.")
            
    # Save metadata
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    print(f"Completed. Saved {len(metadata)} pages to {DOWNLOAD_DIR}")

if __name__ == "__main__":
    main()
