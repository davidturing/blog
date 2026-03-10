#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataAgent NL2SQL 转换演示
展示自然语言如何转换为SQL查询
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_agent import DataAgent

def demo_nl2sql_conversion():
    """演示NL2SQL转换过程"""
    
    # 创建DataAgent实例（使用模拟模式）
    agent = DataAgent()
    
    print("🔍 DataAgent NL2SQL 转换演示")
    print("=" * 60)
    
    # 测试用例1: Token消耗查询
    query1 = "过去一周，我们抓取 GitHub Trending 耗费了多少 Token？"
    print(f"\n📝 自然语言查询 1: {query1}")
    
    # 模拟生成SQL
    sql1 = agent._simulate_sql_generation(query1)
    print(f"⚙️  生成的SQL:")
    print(sql1.strip())
    
    # 测试用例2: 错误统计查询  
    query2 = "最近系统报错最多的是哪一天？"
    print(f"\n📝 自然语言查询 2: {query2}")
    
    sql2 = agent._simulate_sql_generation(query2)
    print(f"⚙️  生成的SQL:")
    print(sql2.strip())
    
    # 测试用例3: 抓取统计查询
    query3 = "最近一周都抓取了哪些类型的数据？"
    print(f"\n📝 自然语言查询 3: {query3}")
    
    sql3 = agent._simulate_sql_generation(query3)
    print(f"⚙️  生成的SQL:")
    print(sql3.strip())
    
    print("\n" + "=" * 60)
    print("✅ NL2SQL转换演示完成！")
    
    # 展示安全防护机制
    print("\n🛡️  安全防护演示:")
    unsafe_sql = "DROP TABLE raw_signals; -- 恶意SQL注入"
    is_safe = agent._is_safe_sql(unsafe_sql)
    print(f"恶意SQL: {unsafe_sql}")
    print(f"安全性检查结果: {'✅ 安全' if is_safe else '❌ 不安全 - 已拒绝'}")

if __name__ == "__main__":
    demo_nl2sql_conversion()