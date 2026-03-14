"""
官方文档本体重构器 - 技术文档爬取与分析
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup


class DocSpider:
    """官方文档本体重构器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化文档爬虫
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger("DocSpider")
        self.config = config
        self.doc_targets = config.get("docs_targets", [])
        
    async def fetch_doc_page(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """获取单个文档页面
        
        Args:
            session: aiohttp 会话
            url: 文档 URL
            
        Returns:
            页面内容或 None
        """
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"文档页面 {url} 返回状态码: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"获取文档页面失败 {url}: {e}")
            return None
            
    def extract_main_content(self, html_content: str) -> str:
        """从 HTML 中提取主要内容
        
        Args:
            html_content: HTML 内容
            
        Returns:
            提取的纯文本内容
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
                
            # 尝试找到主要内容区域
            main_content = None
            candidates = [
                soup.find('main'),
                soup.find('article'), 
                soup.find('div', class_='content'),
                soup.find('div', id='content'),
                soup.find('div', class_='main'),
                soup.find('div', id='main')
            ]
            
            for candidate in candidates:
                if candidate:
                    main_content = candidate
                    break
                    
            if not main_content:
                main_content = soup
                
            # 提取文本并清理
            text = main_content.get_text(separator=' ', strip=True)
            # 清理多余空白
            text = ' '.join(text.split())
            
            return text[:2000]  # 限制长度
            
        except Exception as e:
            self.logger.error(f"提取主要内容失败: {e}")
            return ""
            
    async def crawl_all_docs(self) -> List[Dict[str, Any]]:
        """并发爬取所有目标文档
        
        Returns:
            文档内容列表
        """
        self.logger.info(f"开始爬取 {len(self.doc_targets)} 个文档目标...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_doc_page(session, url) for url in self.doc_targets]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        # 处理结果
        docs = []
        for i, result in enumerate(results):
            if isinstance(result, str):
                content = self.extract_main_content(result)
                if content:
                    docs.append({
                        "url": self.doc_targets[i],
                        "content": content,
                        "source": self._identify_doc_source(self.doc_targets[i])
                    })
            elif isinstance(result, Exception):
                self.logger.error(f"文档爬取异常: {result}")
                
        self.logger.info(f"文档爬取完成，获得 {len(docs)} 份文档")
        return docs
        
    def _identify_doc_source(self, url: str) -> str:
        """识别文档源
        
        Args:
            url: 文档 URL
            
        Returns:
            源标识
        """
        if "polars.rs" in url:
            return "polars"
        elif "openclaw.ai" in url:
            return "openclaw"
        else:
            return "unknown"
            
    def extract_insights(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从文档中提取洞察
        
        Args:
            docs: 文档列表
            
        Returns:
            提取的洞察列表
        """
        insights = []
        
        for doc in docs:
            insight = {
                "source": "docs",
                "title": f"Documentation: {doc['source'].title()}",
                "content": doc["content"],
                "metadata": {
                    "doc_source": doc["source"],
                    "url": doc["url"]
                },
                "timestamp": datetime.now().isoformat()
            }
            insights.append(insight)
            
        return insights
        
    async def run_discovery(self) -> List[Dict[str, Any]]:
        """运行完整的文档爬取流程
        
        Returns:
            提取的洞察列表
        """
        try:
            # 爬取文档
            docs = await self.crawl_all_docs()
            
            if not docs:
                self.logger.info("未获取到任何文档内容")
                return []
                
            # 提取洞察
            insights = self.extract_insights(docs)
            
            # 限制数量
            max_fetch = self.config.get("max_fetch_per_cycle", 5)
            insights = insights[:max_fetch]
            
            self.logger.info(f"文档爬取完成，获得 {len(insights)} 项洞察")
            return insights
            
        except Exception as e:
            self.logger.error(f"文档爬取失败: {e}")
            return []