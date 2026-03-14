"""
DavidAgent 感知收割机系统测试脚本

验证所有模块是否可以正常导入和运行。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "DavidAgent" / "brain" / "sensors"))


def test_imports():
    """测试所有模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        from cognitive_filter import CognitiveEntropyFilter
        print("✅ cognitive_filter 导入成功")
    except ImportError as e:
        print(f"❌ cognitive_filter 导入失败: {e}")
        return False
        
    try:
        from github_watcher import GitHubWatcher
        print("✅ github_watcher 导入成功")
    except ImportError as e:
        print(f"❌ github_watcher 导入失败: {e}")
        return False
        
    try:
        from rss_gatherer import RSSGatherer
        print("✅ rss_gatherer 导入成功")
    except ImportError as e:
        print(f"❌ rss_gatherer 导入失败: {e}")
        return False
        
    try:
        from social_sniffer import SocialSniffer
        print("✅ social_sniffer 导入成功")
    except ImportError as e:
        print(f"❌ social_sniffer 导入失败: {e}")
        return False
        
    try:
        from doc_spider import DocSpider
        print("✅ doc_spider 导入成功")
    except ImportError as e:
        print(f"❌ doc_spider 导入失败: {e}")
        return False
        
    try:
        from qa_miner import QAMiner
        print("✅ qa_miner 导入成功")
    except ImportError as e:
        print(f"❌ qa_miner 导入失败: {e}")
        return False
        
    try:
        from run_discovery import DiscoveryOrchestrator
        print("✅ run_discovery 导入成功")
    except ImportError as e:
        print(f"❌ run_discovery 导入失败: {e}")
        return False
        
    return True


def test_config_loading():
    """测试配置文件加载"""
    print("\n🧪 测试配置文件加载...")
    
    config_path = project_root / "DavidAgent" / "brain" / "sensors" / "config.json"
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return False
        
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        print("✅ 配置文件加载成功")
        print(f"  - GitHub topics: {config.get('github_topics', [])}")
        print(f"  - RSS feeds: {len(config.get('rss_feeds', []))} 个源")
        print(f"  - 认知阈值: {config.get('cognitive_threshold', 0.65)}")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False


def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        from cognitive_filter import CognitiveEntropyFilter
        
        # 测试认知熵过滤
        config = {"cognitive_threshold": 0.65, "max_fetch_per_cycle": 5}
        filter = CognitiveEntropyFilter(config)
        
        # 测试内容过滤
        test_content = [
            {"content": "This is a novel breakthrough in AI architecture with innovative framework design and efficient optimization algorithms."},
            {"content": "Test content with scalability improvements and performance benchmarks."},
            {"content": "Short text."}
        ]
        
        filtered = filter.filter_content_batch(test_content)
        print(f"✅ 认知熵过滤测试通过: {len(test_content)} → {len(filtered)} 项")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("🚀 DavidAgent 感知收割机系统测试\n")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config_loading,
        test_basic_functionality
    ]
    
    results = []
    for test in tests:
        results.append(test())
        
    print("\n" + "=" * 60)
    
    if all(results):
        print("🎉 所有测试通过！系统已就绪。")
        print("\n使用方法:")
        print("  cd DavidAgent/brain/sensors")
        print("  python run_discovery.py           # 正常运行")
        print("  python run_discovery.py --dry-run # 模拟运行")
        print("  python run_discovery.py --force_fetch # 强制抓取")
        return 0
    else:
        print("💥 部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())