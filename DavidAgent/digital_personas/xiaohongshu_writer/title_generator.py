#!/usr/bin/env python3
"""
小红书爆款标题自动生成器
SDD文档: docs/specs/xiaohongshu_writer_title_generator_v1.md
"""

import re
from typing import List, Dict


class XiaohongshuTitleGenerator:
    """小红书爆款标题生成器"""
    
    def __init__(self):
        # 标题模板
        self.templates = {
            "pain_solution": "🔥{pain}：{solution}！",
            "number_effect": "🎯{number}{action}，{effect}",
            "insider_reveal": "💡内部揭秘：{reveal}？",
            "efficiency_boost": "🚀{before} → {after}，{secret}",
            "mind_blowing": "✨意外发现：{discovery}！"
        }
        
        # 关键词库
        self.pain_words = ["崩溃", "踩坑", "浪费", "低效", "复杂", "头疼"]
        self.number_words = ["3步", "5分钟", "10倍", "99%", "一键", "秒级"]
        self.effect_words = ["爆款", "涨粉", "效率翻倍", "省时省力", "惊艳"]
        self.authority_words = ["米其林", "大厂", "专家", "秘籍", "内部", "独家"]
        
        # 领域关键词映射
        self.domain_keywords = {
            "AI": ["AI", "大模型", "智能体", "MCP协议", "架构教练"],
            "架构": ["架构", "系统设计", "微服务", "分布式", "标准化"],
            "程序员效率": ["效率", "工具链", "自动化", "DevOps", "开发"],
            "工具技巧": ["技巧", "秘籍", "最佳实践", "避坑", "优化"]
        }
        
    def generate_titles(self, topic: str) -> List[str]:
        """
        生成5个爆款标题
        
        Args:
            topic: 内容主题关键词
            
        Returns:
            List[str]: 5个不同风格的标题
        """
        # 提取领域关键词
        keywords = self._extract_domain_keywords(topic)
        
        # 生成关键词映射
        keyword_mapping = self._create_keyword_mapping(topic, keywords)
        
        # 应用模板生成标题
        titles = []
        for template_name, template in self.templates.items():
            try:
                title = template.format(**keyword_mapping)
                # 确保标题长度符合规范
                if len(title) <= 30:
                    titles.append(title)
                else:
                    # 截断并添加省略号
                    titles.append(title[:27] + "...")
            except KeyError as e:
                # 模板参数缺失，使用默认值
                titles.append(f"🔥{topic}爆款标题！")
                
        return titles[:5]  # 确保最多5个标题
        
    def _extract_domain_keywords(self, topic: str) -> List[str]:
        """提取领域关键词"""
        keywords = []
        topic_lower = topic.lower()
        
        for domain, words in self.domain_keywords.items():
            for word in words:
                if word.lower() in topic_lower:
                    keywords.append(word)
                    break
                    
        return keywords if keywords else ["AI", "效率"]
        
    def _create_keyword_mapping(self, topic: str, domain_keywords: List[str]) -> Dict[str, str]:
        """创建关键词映射"""
        # 基础关键词
        base_keywords = {
            "pain": f"程序员{self.pain_words[0]}",
            "solution": f"{topic}让效率提升10倍",
            "number": self.number_words[0],
            "action": f"搞定{topic}",
            "effect": f"{self.effect_words[0]}方案",
            "reveal": f"为什么顶级系统都采用{topic}",
            "before": "重复造轮子",
            "after": "标准化开发", 
            "secret": f"{topic}的秘密",
            "discovery": f"{topic}竟能解决99%问题"
        }
        
        # 根据领域调整关键词
        if "AI" in domain_keywords or "智能体" in domain_keywords:
            base_keywords.update({
                "pain": "AI开发者崩溃",
                "effect": "大厂AI团队都在用",
                "reveal": f"AI架构师的{topic}秘籍"
            })
        elif "架构" in domain_keywords:
            base_keywords.update({
                "pain": "架构师头疼",
                "effect": "系统稳定性提升10倍",
                "secret": f"架构标准化的{topic}"
            })
        elif "效率" in domain_keywords:
            base_keywords.update({
                "pain": "开发效率低效",
                "effect": "工作效率翻倍",
                "discovery": f"{topic}让编码速度提升99%"
            })
            
        return base_keywords
        
    def validate_sdd_compliance(self) -> bool:
        """验证SDD合规性"""
        # 检查模板数量
        if len(self.templates) != 5:
            return False
            
        # 检查关键词库完整性
        required_keys = ["pain_words", "number_words", "effect_words", "authority_words"]
        for key in required_keys:
            if not hasattr(self, key) or len(getattr(self, key)) == 0:
                return False
                
        return True


def main():
    """主函数 - 命令行测试"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python title_generator.py <topic>")
        return
        
    topic = sys.argv[1]
    generator = XiaohongshuTitleGenerator()
    
    # 验证SDD合规性
    if not generator.validate_sdd_compliance():
        print("❌ SDD合规性验证失败")
        return
        
    titles = generator.generate_titles(topic)
    
    print(f"📝 小红书爆款标题生成器")
    print(f"🎯 主题: {topic}")
    print(f"✨ 生成结果:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")


if __name__ == "__main__":
    main()