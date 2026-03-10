import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.methods.posts import NewPost

def main():
    creds = {}
    with open('/Users/zhaoqinhuang/david_project/.credentials/wordpress.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                creds[k.strip()] = v.strip().strip("'\"")

    url = 'https://dvspace5.wordpress.com/xmlrpc.php'
    username = creds.get('WORDPRESS_USERNAME')
    password = creds.get('WORDPRESS_APP_PASSWORD')

    print("Connecting to WordPress via XML-RPC...")
    client = Client(url, username, password)

    # Create a simple placeholder image since Gemini API is expired
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (1200, 630), color=(245, 245, 245))  # Light background
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 60)
    except:
        font = ImageFont.load_default()
    d.text((50, 200), '2026 Python Data Analyst\nStandard Configuration', fill=(30, 30, 30), font=font)
    img.save('baoyu_cover_light.png')
    
    image_path = 'baoyu_cover_light.png'
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

    # Blog content
    content = """
# 🚀 2026 Python数据分析师生存指南：从"Hello World"到企业级AI战士的终极装备清单！

> **警告：本文可能会让你的旧笔记本电脑哭泣，让你的IT部门瑟瑟发抖！**

## 💥 开场暴击：你的Pandas还在用apply()？

如果你还在用`df.apply(lambda x: x*2)`处理百万行数据，那你可能还在用算盘做数据分析！2026年了，兄弟！**无GIL时代已经来临**，Python 3.14让你的多核CPU终于可以全力输出，而不是在GIL锁前排队等死！

## 🛠️ 核心装备：现代数据科学家的"瑞士军刀"

### 🔧 环境管理：告别"在我机器上能跑"
- **Python 3.14**：自由线程支持，多核利用率提升50%+！再也不用看着8核CPU只用1核干瞪眼
- **uv包管理器**：Rust写的超级快！30分钟的环境搭建？现在2分钟搞定！
- **VS Code + Python插件**：类型提示、调试、Jupyter集成，一应俱全

### 🚀 数据处理三剑客：Polars + DuckDB + Pandas 3.0

| 工具 | 定位 | 杀手锏 | 适用场景 |
|------|------|--------|----------|
| **Polars 1.8+** | 高性能DataFrame | Rust+Arrow内核，内存省70%！ | 10GB+大数据、ETL、良率分析 |
| **DuckDB 1.4.4+** | 嵌入式分析引擎 | 无服务SQL，直接读Parquet | 复杂聚合、本地OLAP |
| **Pandas 3.0** | 经典DataFrame | 生态成熟，兼容老代码 | 小数据探索、教学 |

### 📋 快速安装清单（复制即用）

```bash
# 安装uv（超快包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 初始化项目
uv init data-project && cd data-project

# 安装核心包（分析师版）
uv add polars duckdb numpy scipy pandas scikit-learn matplotlib seaborn plotly jupyterlab
```

## 💡 总结：2026年的数据分析师应该这样玩！

**数据处理核心**：Polars + DuckDB，性能碾压传统方案  
**AI集成标配**：LLM + RAG + Agent，智能分析新时代  
**工程化保障**：MLOps + 容器化，从实验到生产无缝衔接  
"""

    html_content = f'<img src="{image_url}" alt="2026 Python Data Analyst Cover" style="max-width:100%; height:auto; margin-bottom: 20px;" />\n\n' + content

    post = WordPressPost()
    post.title = "2026 Python 数据分析师/科学家标准配置（企业级+开源双栈）"
    post.content = html_content
    post.post_status = "publish"  # Ensure it's published
    post.post_type = "post"
    post.thumbnail = attachment_id
    
    post.terms_names = {
        'post_tag': ['Python', 'Data Analyst', '2026', 'Polars'],
        'category': ['Technology']
    }

    print("Publishing post...")
    post_id = client.call(NewPost(post))
    print(f"✅ Post published successfully!")
    print(f"Post ID: {post_id}")
    print(f"URL: https://dvspace5.wordpress.com/?p={post_id}")

if __name__ == "__main__":
    main()