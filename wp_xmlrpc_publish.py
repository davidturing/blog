import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.methods.posts import NewPost

def main():
    creds = {}
    with open('/Users/zhaoqinhuang/david_project/.credentials/wordpress.env', 'r') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k.strip()] = v.strip().strip("'\"")

    url = 'https://dvspace5.wordpress.com/xmlrpc.php'
    username = creds.get('WORDPRESS_USERNAME')
    password = creds.get('WORDPRESS_APP_PASSWORD')

    print("Connecting to WordPress via XML-RPC...")
    client = Client(url, username, password)

    image_path = '/Users/zhaoqinhuang/david_project/baoyu_cover_light.png'
    print(f"Uploading image {image_path}...")
    
    with open(image_path, 'rb') as img_f:
        data = {
            'name': 'baoyu_cover_light.png',
            'type': 'image/png',
            'bits': xmlrpc_client.Binary(img_f.read()),
            'overwrite': True
        }
        res = client.call(UploadFile(data))
        
    attachment_id = res['id']
    image_url = res['url']
    print(f"Image uploaded successfully! Attachment ID: {attachment_id}")
    print(f"Image URL: {image_url}")

    print("Reading blog content...")
    with open('/Users/zhaoqinhuang/david_project/2026_Python_Data_Analyst_Stack.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Prepend image to the content so it displays at the top, and also set as featured image
    html_content = f'<img src="{image_url}" alt="2026 Python Data Analyst Cover" style="max-width:100%; height:auto;" />\n\n' + content

    post = WordPressPost()
    post.title = "2026 Python 数据分析师/科学家标准配置（企业级+开源双栈）"
    post.content = html_content
    post.post_status = "publish"
    # Set featured image
    post.thumbnail = attachment_id
    
    # Categories/Tags
    post.terms_names = {
        'post_tag': ['Python', 'Data Analyst', '2026', 'Polars'],
        'category': ['Technology', 'AI']
    }

    print("Publishing post...")
    post_id = client.call(NewPost(post))
    print(f"Post published successfully!")
    print(f"Post ID: {post_id}")
    print(f"URL: https://dvspace5.wordpress.com/?p={post_id}")

if __name__ == "__main__":
    main()