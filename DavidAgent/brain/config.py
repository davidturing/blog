"""
仿生双脑架构配置文件
"""
import os
from pathlib import Path

class BrainConfig:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
        # 模型配置
        self.right_brain_model = "qwen3-max-2026-01-23"
        self.left_brain_model = "gemini"
        
        # 路径配置  
        self.chromadb_path = self.project_root / "chroma_data"
        self.pageindex_path = self.project_root / "skills" / "self-learning-agent" / "pageindex" / "knowledge"
        self.blog_output_path = self.project_root / "blog"
        
        # API密钥（从环境变量加载）
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        self.dashscope_endpoint = os.getenv("DASHSCOPE_ENDPOINT", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # WordPress配置
        self.wp_site_url = os.getenv("WP_SITE_URL")
        self.wp_username = os.getenv("WP_USERNAME")
        self.wp_app_password = os.getenv("WP_APP_PASSWORD")
        self.wp_app_name = os.getenv("WP_APP_NAME", "dvspace5")

        # X认证
        self.x_auth_token = os.getenv("X_AUTH_TOKEN") 
        self.x_ct0 = os.getenv("X_CT0")
        
        # X 感知目标配置
        self.x_target_accounts = ["DeepSeek_AI", "OpenAI", "AnthropicAI", "GoogleDeepMind"]
        self.x_accounts_json = self.project_root.parent / "skills" / "self-learning-agent" / "data" / "raw" / "x_accounts.json"