import os
import time
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts

# WordPress 配置
WP_SITE_URL = 'https://dvspace5.wordpress.com/xmlrpc.php'
WP_USERNAME = 'davidturing'
WP_APP_PASSWORD = '2oen cgw4 gh5k z3tn'

def read_article_content():
    """读取文章内容"""
    with open('davidagent_v1_article.md', 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def publish_blog():
    try:
        print("Connecting to WordPress...")
        client = Client(WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD)
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    title = "DavidAgent v1.0 发布：你的第一个仿生数字分身"
    
    # 读取文章内容
    content = read_article_content()
    
    # 转换为 HTML（简单的 Markdown 到 HTML 转换）
    content_html = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
    content_html = f"<p>{content_html}</p>"

    post = WordPressPost()
    post.title = title
    post.content = content_html
    post.post_status = 'publish'
    post.terms_names = {
        'category': ['AI', 'Agent', 'Technology'],
        'post_tag': ['DavidAgent', 'Digital Twin', 'AI Agent', 'Gemini', 'Qwen']
    }

    try:
        print(f"Publishing blog: {title}...")
        post_id = client.call(posts.NewPost(post))
        print(f"SUCCESS: Blog published! Link: https://dvspace5.wordpress.com/?p={post_id}")
        return post_id
    except Exception as e:
        print(f"Publish Failed: {e}")
        return None

if __name__ == "__main__":
    publish_blog()