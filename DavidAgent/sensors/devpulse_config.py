"""
DevPulse-Sensor 配置文件
"""

# Hacker News 关键词过滤
HN_KEYWORDS = [
    "AI", "LLM", "Agent", "Cursor", "Copilot", "Code", "Python", "React",
    "LangChain", "Devin", "GitHub", "OpenAI", "Anthropic", "HuggingFace",
    "Machine Learning", "Deep Learning", "Neural", "Artificial Intelligence",
    "大模型", "AI编程", "代码生成", "智能编程"
]

# RSS 订阅源列表
RSS_SOURCES = [
    # 官方博客
    "https://huggingface.co/blog/feed.xml",
    "https://openai.com/blog/rss/",
    "https://blog.anthropic.com/rss",
    "https://github.blog/feed/",
    
    # 技术媒体
    "https://techcrunch.com/feed/",
    "https://arstechnica.com/feed/",
    "https://www.wired.com/feed/category/ai/rss",
    
    # 开发者博客（示例）
    "https://simonwillison.net/atom/everything/",
    "https://danluu.com/atom.xml",
    
    # 中文技术博客
    "https://coolshell.cn/feed",
    "https://www.ruanyifeng.com/blog/atom.xml"
]

# 抓取频率配置（秒）
HN_FETCH_INTERVAL = 3600  # 每小时抓取一次
RSS_FETCH_INTERVAL = 7200  # 每2小时抓取一次

# 去重缓存配置
DUPLICATE_CACHE_SIZE = 1000  # 内存缓存大小
DUPLICATE_CACHE_FILE = "devpulse_cache.json"  # 持久化缓存文件

# 网页内容提取配置
CONTENT_EXTRACT_TIMEOUT = 30  # 内容提取超时（秒）
MIN_CONTENT_LENGTH = 100  # 最小内容长度

# 日志级别
LOG_LEVEL = "INFO"