# Moltbot 与 WordPress 集成指南

Moltbot 不仅能管理代码，还能成为你的内容发布助手。本文将介绍如何配置 Moltbot 连接到 WordPress 站点，实现自动发布文章。

## 1. 准备工作

在开始之前，你需要：
- 一个运行中的 **WordPress** 站点（建议版本 5.6+）。
- **Moltbot** 已安装并配置好基本环境。
- 具有发布权限的 WordPress 用户账号。

## 2. 配置 WordPress 认证

为了安全起见，建议使用 **应用程序密码 (Application Passwords)** 而不是直接使用登录密码。

1.  登录你的 WordPress 后台。
2.  进入 **用户 (Users)** -> **个人资料 (Profile)**。
3.  滚动到 **应用程序密码** 部分。
4.  输入名称（例如 `Moltbot`），点击 **添加新应用程序密码**。
5.  复制生成的密码（格式如 `xxxx xxxx xxxx xxxx`），保存好，稍后会用到。

> **注意**：如果你的站点禁用了 REST API 或使用了某些安全插件，可能需要额外配置白名单。

## 3. 配置 Moltbot

在你的 Moltbot 项目中，设置环境变量或更新 `config.yaml`。建议使用 `.env` 文件存储敏感信息。

### 环境变量方式

```bash
export WP_URL="https://your-site.com/wp-json/wp/v2"
export WP_USER="your_username"
export WP_PASSWORD="your-application-password"
```

## 4. 编写发布脚本

Moltbot 可以通过简单的 HTTP 请求与 WordPress 交互。以下是一个使用 Moltbot 发布文章的示例流程（假设你正在编写一个 Moltbot 技能或脚本）：

```python
# moltbot_wp.py 示例伪代码
import os
import requests
from requests.auth import HTTPBasicAuth

def post_to_wordpress(title, content, status='draft'):
    url = f"{os.getenv('WP_URL')}/posts"
    auth = HTTPBasicAuth(os.getenv('WP_USER'), os.getenv('WP_PASSWORD'))
    
    data = {
        'title': title,
        'content': content,
        'status': status  # 'publish' 为直接发布，'draft' 为草稿
    }
    
    response = requests.post(url, auth=auth, json=data)
    
    if response.status_code == 201:
        print(f"✅ 文章发布成功！ID: {response.json()['id']}")
        print(f"🔗 链接: {response.json()['link']}")
    else:
        print(f"❌ 发布失败: {response.text}")

# 让 Moltbot 执行
# post_to_wordpress("Moltbot 测试文章", "这是通过 Moltbot 自动发布的内容。")
```

## 5. 进阶用法

- **自动配图**：Moltbot 可以先上传图片到 WordPress 媒体库（`/media` 端点），获得 ID 后将其设置为文章特色图片。
- **定时发布**：结合 Moltbot 的定时任务功能，可以实现定时发布内容。
- **内容转换**：利用 Moltbot 的 AI 能力，将 Markdown 笔记自动转换为 HTML 格式并发布。

---

通过集成 WordPress，Moltbot 变成了你的全能内容管家。快去试试吧！
