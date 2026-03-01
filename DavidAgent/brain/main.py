"""
仿生双脑多智能体系统主入口
"""
from .config import BrainConfig
from .workflow.x_ingestion import XIngestionWorkflow

def main():
    """启动仿生双脑系统"""
    config = BrainConfig()
    workflow = XIngestionWorkflow()
    
    print("🚀 仿生双脑多智能体系统启动")
    print(f"   右脑模型: {config.right_brain_model}")
    print(f"   左脑模型: {config.left_brain_model}")
    print("   系统状态: 就绪，等待外部刺激...")
    
    return workflow

if __name__ == "__main__":
    main()