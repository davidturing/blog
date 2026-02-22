"""
Data Agent Dashboard Integration
将Data Agent集成到Streamlit监控大盘中
"""
import streamlit as st
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from data_agent.data_agent import DataAgent

class DataAgentDashboard:
    """Data Agent Dashboard集成类"""
    
    def __init__(self):
        self.data_agent = None
        self._initialize_data_agent()
    
    def _initialize_data_agent(self):
        """初始化Data Agent"""
        try:
            # 检查环境变量
            if not os.getenv('GEMINI_API_KEY'):
                st.warning("⚠️ 未设置GEMINI_API_KEY环境变量，部分功能可能受限")
            
            # 初始化Data Agent
            self.data_agent = DataAgent(
                db_path="david_agent_memory.db",
                pageindex_dir="skills/self-learning-agent/pageindex/knowledge"
            )
            st.success("✅ Data Agent初始化成功！")
            
        except Exception as e:
            st.error(f"❌ Data Agent初始化失败: {e}")
            self.data_agent = None
    
    async def process_query(self, query: str) -> str:
        """处理用户查询"""
        if self.data_agent is None:
            return "Data Agent未初始化，请检查配置。"
        
        try:
            result = await self.data_agent.process_human_query(query)
            return result
        except Exception as e:
            return f"查询处理失败: {e}"
    
    def render_dashboard(self):
        """渲染Dashboard界面"""
        st.title("🧠 Data Agent - 私人交互式智库")
        st.markdown("""
        ### 向你的数字分身提问
        Data Agent是DavidAgent的"前额叶皮层"，可以帮你：
        - 📊 查询系统运行状态、Token消耗、抓取日志等运维指标
        - 🧠 查询技术概念、框架对比、行业趋势等技术知识
        - 🔍 基于你个人数字分身的私有世界观生成洞察
        """)
        
        # 用户输入
        user_query = st.text_input(
            "对话框：向海马体提问...",
            placeholder="例如：'过去一周GitHub Trending耗费了多少Token？' 或 'Node.js跑大模型的替代方案有哪些？'"
        )
        
        if user_query:
            with st.spinner("🤔 Data Agent正在思考..."):
                # 异步处理查询
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.process_query(user_query))
                    st.markdown("### 💡 回答:")
                    st.write(result)
                except Exception as e:
                    st.error(f"处理查询时出错: {e}")
                finally:
                    loop.close()
        
        # 示例查询
        st.markdown("### 💡 示例查询:")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**运维指标查询:**")
            st.code("过去一周GitHub Trending耗费了多少Token？")
            st.code("哪天的死信任务最多？")
            st.code("X Spider的平均处理时间是多少？")
        
        with col2:
            st.markdown("**知识洞察查询:**")
            st.code("Node.js跑大模型的替代方案有哪些？")
            st.code("GitHub上最新的AI框架趋势是什么？")
            st.code("Gemini 3.1 Pro相比之前的版本有什么改进？")
        
        # 系统状态
        st.markdown("---")
        st.markdown("### 📊 系统状态")
        if self.data_agent:
            st.success("✅ Data Agent: 运行中")
            st.info(f"📊 SQLite数据库: {self.data_agent.db_path}")
            st.info(f"🧠 知识库目录: {self.data_agent.pageindex_dir}")
        else:
            st.error("❌ Data Agent: 未初始化")

# 全局实例
dashboard_instance = DataAgentDashboard()

def main():
    """主函数"""
    dashboard_instance.render_dashboard()

if __name__ == "__main__":
    main()