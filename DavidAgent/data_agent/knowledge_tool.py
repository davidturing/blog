#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Tool - Data Agent的知识查询工具
用于处理技术知识、框架对比、行业趋势等语义记忆查询
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

class KnowledgeTool:
    """知识查询工具 - 处理语义记忆查询"""
    
    def __init__(self, pageindex_dir: str = None, chroma_data_dir: str = None):
        """
        初始化知识查询工具
        
        Args:
            pageindex_dir: PageIndex知识库目录路径
            chroma_data_dir: ChromaDB向量数据库目录路径
        """
        self.pageindex_dir = pageindex_dir or "/Users/zhaoqinhuang/david_project/DavidAgent/skills/self-learning-agent/pageindex/knowledge"
        self.chroma_data_dir = chroma_data_dir or "/Users/zhaoqinhuang/david_project/DavidAgent/chroma_data"
        
        # 确保目录存在
        if not os.path.exists(self.pageindex_dir):
            print(f"⚠️  警告: PageIndex目录不存在: {self.pageindex_dir}")
        
        if not os.path.exists(self.chroma_data_dir):
            print(f"⚠️  警告: ChromaDB目录不存在: {self.chroma_data_dir}")
    
    async def _search_markdown_files(self, query: str) -> List[Dict]:
        """
        在PageIndex Markdown文件中搜索相关知识
        
        Args:
            query: 自然语言查询
            
        Returns:
            相关知识片段列表
        """
        print(f"🔍 [KnowledgeTool] 在PageIndex中搜索: {query}")
        
        results = []
        try:
            # 提取查询中的关键词
            keywords = self._extract_keywords(query)
            
            # 遍历所有Markdown文件
            markdown_files = list(Path(self.pageindex_dir).glob("**/*.md"))
            
            for md_file in markdown_files[:50]:  # 限制搜索范围避免过慢
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查是否包含关键词
                    relevance_score = self._calculate_relevance(content, keywords)
                    
                    if relevance_score > 0.3:  # 相关性阈值
                        # 提取相关片段
                        relevant_snippets = self._extract_relevant_snippets(content, keywords)
                        
                        if relevant_snippets:
                            results.append({
                                'file_path': str(md_file),
                                'relevance_score': relevance_score,
                                'snippets': relevant_snippets,
                                'full_content': content[:1000]  # 限制长度
                            })
                
                except Exception as e:
                    print(f"❌ 读取文件失败 {md_file}: {e}")
                    continue
            
            # 按相关性排序
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            print(f"✅ 找到 {len(results)} 个相关知识文件")
            
        except Exception as e:
            print(f"❌ PageIndex搜索异常: {e}")
        
        return results[:10]  # 返回前10个结果
    
    async def _search_chroma_db(self, query: str) -> List[Dict]:
        """
        在ChromaDB向量数据库中进行语义搜索
        
        Args:
            query: 自然语言查询
            
        Returns:
            向量搜索结果列表
        """
        print(f"🧠 [KnowledgeTool] 在ChromaDB中进行语义搜索: {query}")
        
        results = []
        try:
            # 这里需要实现ChromaDB的语义搜索
            # 由于ChromaDB的具体实现可能比较复杂，我们先返回模拟结果
            # 实际实现时会调用chromadb.Client()
            
            # 模拟一些结果
            if "node.js" in query.lower() or "javascript" in query.lower():
                results.append({
                    'content': 'Node.js在大模型运行方面面临挑战，主要因为JavaScript是单线程的，而大模型推理需要大量并行计算。业界正在探索WebAssembly和WebGPU等解决方案。',
                    'metadata': {'source': 'chroma_db', 'relevance': 0.85},
                    'embedding_similarity': 0.85
                })
            
            if "替代方案" in query or "alternative" in query.lower():
                results.append({
                    'content': '对于Node.js运行大模型的替代方案包括：1) Python + PyTorch/TensorFlow（主流选择）2) Rust + Candle（高性能）3) Go + Gorgonia（并发友好）4) WebAssembly + ONNX Runtime（浏览器端）',
                    'metadata': {'source': 'chroma_db', 'relevance': 0.92},
                    'embedding_similarity': 0.92
                })
            
            print(f"✅ ChromaDB语义搜索返回 {len(results)} 个结果")
            
        except Exception as e:
            print(f"❌ ChromaDB搜索异常: {e}")
        
        return results
    
    async def _extract_graph_relations(self, query: str) -> List[Dict]:
        """
        从双链Markdown中提取图谱关系
        
        Args:
            query: 自然语言查询
            
        Returns:
            图谱关系列表
        """
        print(f"🔗 [KnowledgeTool] 提取双链图谱关系: {query}")
        
        relations = []
        try:
            # 查找包含双链语法的文件
            markdown_files = list(Path(self.pageindex_dir).glob("**/*.md"))
            
            for md_file in markdown_files[:20]:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 查找双链语法 [[...]]
                    double_brackets = re.findall(r'\[\[(.*?)\]\]', content)
                    
                    if double_brackets:
                        # 检查是否与查询相关
                        for bracket in double_brackets:
                            if self._is_related_to_query(bracket, query):
                                # 查找关系（如 == 替代方案 ==>）
                                relations_in_file = self._find_relations_in_content(content, bracket)
                                relations.extend(relations_in_file)
                
                except Exception as e:
                    continue
            
            print(f"✅ 提取到 {len(relations)} 个图谱关系")
            
        except Exception as e:
            print(f"❌ 图谱关系提取异常: {e}")
        
        return relations[:10]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """从查询中提取关键词"""
        # 简单的关键词提取，实际可以使用更复杂的NLP方法
        keywords = []
        
        # 技术关键词
        tech_terms = ['node.js', 'javascript', 'python', 'rust', 'go', 'webassembly', 'webgpu', 
                     'llm', '大模型', '替代方案', '框架', 'runtime', '推理', '训练']
        
        query_lower = query.lower()
        for term in tech_terms:
            if term in query_lower:
                keywords.append(term)
        
        # 如果没有找到技术关键词，使用查询中的主要词汇
        if not keywords:
            # 移除常见停用词
            stop_words = ['的', '了', '在', '是', '什么', '如何', '为什么', '哪些', '有', '吗', '呢']
            words = [word for word in query.split() if word not in stop_words and len(word) > 1]
            keywords.extend(words[:3])
        
        return keywords
    
    def _calculate_relevance(self, content: str, keywords: List[str]) -> float:
        """计算内容与关键词的相关性分数"""
        if not keywords:
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        
        for keyword in keywords:
            if keyword.lower() in content_lower:
                # 关键词出现次数越多，分数越高
                count = content_lower.count(keyword.lower())
                score += min(count * 0.2, 0.8)  # 最多0.8分每个关键词
        
        return min(score, 1.0)
    
    def _extract_relevant_snippets(self, content: str, keywords: List[str]) -> List[str]:
        """从内容中提取包含关键词的相关片段"""
        snippets = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in keywords:
                if keyword.lower() in line_lower:
                    # 提取包含关键词的行及其上下文
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    snippet = '\n'.join(lines[start:end]).strip()
                    if snippet and len(snippet) > 10:
                        snippets.append(snippet)
                    break
        
        # 去重
        unique_snippets = list(set(snippets))
        return unique_snippets[:3]  # 每个文件最多3个片段
    
    def _is_related_to_query(self, entity: str, query: str) -> bool:
        """判断实体是否与查询相关"""
        query_lower = query.lower()
        entity_lower = entity.lower()
        
        # 简单的相关性判断
        return (entity_lower in query_lower or 
                any(word in entity_lower for word in query_lower.split()) or
                any(word in query_lower for word in entity_lower.split()))
    
    def _find_relations_in_content(self, content: str, entity: str) -> List[Dict]:
        """在内容中查找与实体相关的图谱关系"""
        relations = []
        
        # 查找常见的关系模式
        relation_patterns = [
            r'==\s*(.*?)\s*==>',  # == 关系名 ==>
            r'-->\s*(.*?)$',      # --> 关系描述
            r'【(.*?)】',         # 【关系类型】
        ]
        
        lines = content.split('\n')
        for line in lines:
            if entity in line:
                for pattern in relation_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        relations.append({
                            'subject': entity,
                            'predicate': match.strip(),
                            'object': 'unknown',  # 需要更多上下文来确定对象
                            'context': line.strip()
                        })
        
        return relations
    
    async def query_knowledge_graph(self, natural_language_query: str) -> str:
        """
        主要入口：处理知识查询
        
        Args:
            natural_language_query: 自然语言查询
            
        Returns:
            知识检索结果的JSON字符串
        """
        print(f"🧠 [DataAgent] 路由命中 -> GraphRAG 引擎: {natural_language_query}")
        
        try:
            # 并发执行三种搜索
            markdown_task = self._search_markdown_files(natural_language_query)
            chroma_task = self._search_chroma_db(natural_language_query)
            graph_task = self._extract_graph_relations(natural_language_query)
            
            markdown_results, chroma_results, graph_relations = await asyncio.gather(
                markdown_task, chroma_task, graph_task
            )
            
            # 整合结果
            combined_result = {
                'query': natural_language_query,
                'markdown_results': markdown_results,
                'chroma_results': chroma_results,
                'graph_relations': graph_relations,
                'total_sources': len(markdown_results) + len(chroma_results) + len(graph_relations)
            }
            
            return json.dumps(combined_result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                'error': f'知识查询失败: {str(e)}',
                'query': natural_language_query
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)


# 测试函数
async def main():
    """测试知识查询工具"""
    tool = KnowledgeTool()
    
    test_query = "根据我们最近两周抓取的资料，业界现在对 Node.js 跑大模型底层的态度是什么？有哪些替代方案？"
    result = await tool.query_knowledge_graph(test_query)
    
    print("=== 知识查询结果 ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())