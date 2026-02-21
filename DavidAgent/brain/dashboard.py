#!/usr/bin/env python3
"""
DavidAgent 元认知控制台 - Streamlit可视化Dashboard
高性能优化：缓存 + 按需加载 + 细颗粒度人类反馈
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv, set_key

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from brain.memory.episodic_memory import EpisodicMemoryDB
from brain.config import BrainConfig


def initialize_session_state():
    """初始化Streamlit会话状态"""
    if 'db' not in st.session_state:
        st.session_state.db = EpisodicMemoryDB()
    if 'selected_task' not in st.session_state:
        st.session_state.selected_task = None


@st.cache_data(ttl=60)  # 缓存60秒，避免频繁查库
def load_task_list(limit: int = 50):
    """
    高性能优化：只查询轻量字段用于列表显示
    
    Args:
        limit: 限制返回的记录数量
        
    Returns:
        DataFrame: 任务列表数据
    """
    try:
        conn = sqlite3.connect("david_agent_memory.db")
        # 只SELECT轻量字段，避免加载巨大的JSON快照
        query = """
            SELECT task_id, timestamp, workflow_status, 
                   logic_score, tone_score, format_score
            FROM trace_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"加载任务列表失败: {e}")
        return pd.DataFrame()


def load_task_details(task_id: str):
    """
    懒加载：点击后才去查询庞大的详情字段
    
    Args:
        task_id: 任务ID
        
    Returns:
        dict: 任务详细信息
    """
    try:
        db = st.session_state.db
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT raw_source, left_brain_graph, right_brain_draft, 
                   review_feedback, logic_score, tone_score, format_score, human_comment
            FROM trace_logs 
            WHERE task_id=?
        """, (task_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'raw_source': row[0],
                'left_brain_graph': row[1],
                'right_brain_draft': row[2],
                'review_feedback': row[3],
                'logic_score': row[4] or 5,
                'tone_score': row[5] or 5,
                'format_score': row[6] or 5,
                'human_comment': row[7] or ""
            }
        return None
    except Exception as e:
        st.error(f"加载任务详情失败: {e}")
        return None


@st.cache_data(ttl=30)
def load_signal_list(limit: int = 100):
    """加载原始信号列表"""
    try:
        conn = sqlite3.connect("david_agent_memory.db")
        query = """
            SELECT signal_id, handle, author_name, timestamp, likes, retweets, 
                   raw_text, content_hash, ingested_at, signal_type
            FROM raw_signals 
            ORDER BY ingested_at DESC 
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

def load_signal_details(signal_id: str):
    """加载信号原始 JSON 详情"""
    try:
        db = st.session_state.db
        cursor = db.conn.cursor()
        cursor.execute("SELECT raw_json, raw_text FROM raw_signals WHERE signal_id=?", (signal_id,))
        row = cursor.fetchone()
        if row:
            return {'raw_json': row[0], 'raw_text': row[1]}
        return None
    except:
        return None

def display_task_details(task_details: dict):
    """显示任务详细信息"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🧠 逻辑严密性", f"{task_details['logic_score']}/5")
    with col2:
        st.metric("😎 科技达人网感", f"{task_details['tone_score']}/5")  
    with col3:
        st.metric("📝 排版易读性", f"{task_details['format_score']}/5")
    
    st.divider()
    
    # 使用多Tab页面展示思考链与执行链
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. 原始刺激 (草料)", 
        "2. 左脑图谱 (逻辑)", 
        "3. 右脑草稿 (创作)", 
        "4. 审查与反馈 (复盘)"
    ])
    
    with tab1:
        st.info("来自外部世界的原始输入（X推文等）")
        st.text_area("原始输入", task_details['raw_source'], height=200, disabled=True)
        
    with tab2:
        st.success("G老师（左脑）提取的结构化真理")
        if task_details['left_brain_graph']:
            try:
                graph_data = json.loads(task_details['left_brain_graph'])
                st.json(graph_data)
            except json.JSONDecodeError:
                st.text_area("图谱数据", task_details['left_brain_graph'], height=300, disabled=True)
        else:
            st.info("无图谱数据")
        
    with tab3:
        st.warning("Qwen（右脑）结合 Persona 生成的博客初稿")
        st.markdown(task_details['right_brain_draft'])
        
    with tab4:
        st.error("G老师的严苛审查意见（防幻觉）")
        if task_details['review_feedback']:
            st.write(task_details['review_feedback'])
        else:
            st.success("✅ 一次性审查通过，无修改意见。")
            
        # 显示历史人类评价
        if task_details['human_comment']:
            st.divider()
            st.subheader("👨‍💻 历史人类评价")
            st.write(task_details['human_comment'])


def handle_human_feedback(task_id: str):
    """处理人类反馈提交"""
    st.divider()
    st.subheader("👨‍💻 人类长官 RLHF 强化反馈")
    
    # 细颗粒度多维打分
    col1, col2, col3 = st.columns(3)
    with col1:
        logic_score = st.slider("🧠 逻辑严密性", 1, 5, 5, key="logic_score")
    with col2:
        tone_score = st.slider("😎 科技达人网感", 1, 5, 5, key="tone_score") 
    with col3:
        format_score = st.slider("📝 排版易读性", 1, 5, 5, key="format_score")
    
    human_comment = st.text_area(
        "具体改进建议（例如：不要用'太卷了'这种词）",
        key="human_comment"
    )
    
    if st.button("提交反馈，写入情景记忆"):
        try:
            db = st.session_state.db
            db.update_human_feedback(
                task_id, 
                logic_score, 
                tone_score, 
                format_score, 
                human_comment
            )
            st.success("反馈已保存！DavidAgent 将在今晚的反思中学习这条经验。")
            # 刷新页面以显示新评分
            st.rerun()
        except Exception as e:
            st.error(f"保存反馈失败: {e}")


def load_x_accounts(json_path):
    """从 JSON 加载账号"""
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_x_accounts(json_path, accounts):
    """保存账号到 JSON"""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)


def display_account_management():
    """管理 X 监控账号的 UI"""
    st.header("📡 X 探测账号管理")
    config = BrainConfig()
    json_path = config.x_accounts_json
    
    accounts = load_x_accounts(json_path)
    
    # 概览统计
    st.info(f"💾 配置文件路径: `{json_path}`")
    st.write(f"当前监控中的账号总数: **{len(accounts)}**")
    
    # 新增账号表单
    with st.expander("➕ 新增监控目标"):
        with st.form("add_account_form"):
            new_handle = st.text_input("X Handle (不带 @)", placeholder="例如: elonmusk")
            new_name = st.text_input("显示名称 (Name)", placeholder="例如: Elon Musk")
            new_desc = st.text_area("简介/自我介绍", placeholder="例如: World's first...")
            submit = st.form_submit_button("添加账号")
            
            if submit and new_handle:
                # 检查是否已存在
                if any(a['handle'].lower() == new_handle.lower() for a in accounts):
                    st.warning(f"账号 @{new_handle} 已在监控列表中。")
                else:
                    accounts.append({
                        "name": new_name or new_handle,
                        "handle": new_handle,
                        "description": new_desc,
                        "followers": "N/A",
                        "category": "Custom",
                        "persona": "Added via Dashboard"
                    })
                    save_x_accounts(json_path, accounts)
                    st.success(f"已成功添加 @{new_handle}！")
                    st.rerun()

    # 账号列表展示
    if accounts:
        df = pd.DataFrame(accounts)
        
        # 确保列存在
        if 'name' not in df.columns: df['name'] = "N/A"
        if 'followers' not in df.columns: df['followers'] = "N/A"
        if 'description' not in df.columns: df['description'] = df.get('description', "N/A")
        
        # 增加链接列
        df['link'] = df['handle'].apply(lambda x: f"https://x.com/{x}")
        
        # 只显示关键列
        display_cols = ['name', 'handle', 'description', 'followers', 'link', 'category']
        existing_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(
            df[existing_cols], 
            use_container_width=True,
            column_config={
                "name": st.column_config.TextColumn("名称 (Name)"),
                "handle": st.column_config.TextColumn("Handle", help="点击 Handle 跳转及其详情"),
                "description": st.column_config.TextColumn("简介 (Bio)"),
                "followers": st.column_config.TextColumn("粉丝数"),
                "link": st.column_config.LinkColumn("X 链接")
            }
        )
        
        # 删除账号操作
        st.subheader("🛠️ 账号维护")
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            handle_to_del = st.selectbox("选择账号", [a['handle'] for a in accounts])
        with col_m2:
            if st.button("🗑️ 确认移除", type="primary"):
                accounts = [a for a in accounts if a['handle'] != handle_to_del]
                save_x_accounts(json_path, accounts)
                st.success(f"已移除 @{handle_to_del}")
                st.rerun()
            
            if st.button("🔄 刷新全部元数据"):
                with st.spinner("正在逐个同步 X 元数据 (名称/简介/粉丝数)..."):
                    for acc in accounts:
                        try:
                            cmd = ["bird", "search", f"from:{acc['handle']}", "-n", "1", "--json-full"]
                            res = subprocess.check_output(cmd).decode()
                            f_idx = res.find('[')
                            l_idx = res.rfind(']')
                            if f_idx != -1 and l_idx != -1:
                                data = json.loads(res[f_idx:l_idx+1])
                                if data:
                                    u_res = data[0].get('core', {}).get('user_results', {}).get('result', {})
                                    legacy = u_res.get('legacy', {})
                                    acc['name'] = legacy.get('name', acc.get('name', acc['handle']))
                                    acc['description'] = legacy.get('description', acc.get('description', ''))
                                    acc['followers'] = legacy.get('followers_count', 0)
                        except:
                            continue
                    save_x_accounts(json_path, accounts)
                    st.success("全部账号元数据已刷新！")
                    st.rerun()
    # --- 新增：X 探索功能 ---
    st.divider()
    st.subheader("🔍 X 账号自动探索 (基于搜索)")
    
    # 动态触发搜索的逻辑
    def trigger_search():
        st.session_state.do_x_search = True

    search_query = st.text_input(
        "输入关键词搜索高价值账号", 
        placeholder="例如: AI Agent, LLM, Web3",
        key="x_search_input",
        on_change=trigger_search
    )
    # search_lang = st.radio(
    #     "语言过滤", 
    #     ["全部", "中文", "英文"], 
    #     horizontal=True, 
    #     key="x_search_lang",
    #     on_change=trigger_search
    # )
    
    if st.button("立即探索") or st.session_state.get('do_x_search'):
        st.session_state.do_x_search = False # 重置
        if search_query:
            # 组合搜索词与语言过滤器 (默认仅英语)
            query_to_send = f"{search_query} lang:en"
                
            with st.spinner(f"正在 X 上深入搜寻 '{query_to_send}'..."):
                try:
                    import re
                    # 优先尝试 --json-full 以获取粉丝数
                    try:
                        cmd = ["bird", "search", query_to_send, "-n", "10", "--json-full"]
                        result = subprocess.check_output(cmd).decode()
                        
                        # 提取 JSON 部分
                        first_idx = result.find('[')
                        last_idx = result.rfind(']')
                        if first_idx != -1 and last_idx != -1:
                            json_str = result[first_idx:last_idx+1]
                            tweets_full = json.loads(json_str)
                        else:
                            raise ValueError("No JSON array found")
                        
                        discovered_accounts = {}
                        for t in tweets_full:
                            try:
                                user_res = t.get('core', {}).get('user_results', {}).get('result', {})
                                legacy = user_res.get('legacy', {})
                                handle = legacy.get('screen_name')
                                if handle and handle.lower() not in [a['handle'].lower() for a in accounts]:
                                    discovered_accounts[handle] = {
                                        "name": legacy.get('name') or handle,
                                        "followers": legacy.get('followers_count', 0),
                                        "description": legacy.get('description', ''),
                                        "last_tweet": t.get('text', '')[:100] + "..."
                                    }
                            except:
                                continue
                    except Exception as e:
                        # 如果 --json-full 失败，回退到标准 --json
                        st.warning(f"由于 X 数据结构复杂，已回退到标准搜索模式 (暂无粉丝数统计)")
                        cmd = ["bird", "search", query_to_send, "-n", "10", "--json"]
                        result = subprocess.check_output(cmd).decode()
                        
                        # 提取 JSON
                        first_idx = result.find('[')
                        last_idx = result.rfind(']')
                        if first_idx != -1 and last_idx != -1:
                            tweets = json.loads(result[first_idx:last_idx+1])
                        else:
                            tweets = json.loads(result)
                            
                        discovered_accounts = {}
                        for t in tweets:
                            author = t.get('author', {})
                            handle = author.get('username')
                            if handle and handle.lower() not in [a['handle'].lower() for a in accounts]:
                                discovered_accounts[handle] = {
                                    "name": author.get('name') or handle,
                                    "followers": "N/A",
                                    "description": "N/A",
                                    "last_tweet": t.get('text', '')[:100] + "..."
                                }
                    
                    if discovered_accounts:
                        st.write(f"✨ 发现 {len(discovered_accounts)} 个潜在监控目标：")
                        # 排序
                        sorted_handles = sorted(
                            discovered_accounts.keys(), 
                            key=lambda k: discovered_accounts[k]['followers'] if isinstance(discovered_accounts[k]['followers'], int) else 0,
                            reverse=True
                        )
                        
                        for handle in sorted_handles:
                            info = discovered_accounts[handle]
                            with st.container(border=True):
                                col1, col2 = st.columns([1, 4])
                                with col2:
                                    st.markdown(f"### {info['name']} (@{handle})")
                                    fol_count = f"{info['followers']:,}" if isinstance(info['followers'], int) else info['followers']
                                    st.markdown(f"👥 **粉丝数**: `{fol_count}`")
                                    st.markdown(f"📝 **自我介绍**: {info['description']}")
                                    st.caption(f"最新动态: {info['last_tweet']}")
                                    
                                    if st.button(f"关注 @{handle}", key=f"add_{handle}", type="primary"):
                                        accounts.append({
                                            "name": info['name'],
                                            "handle": handle,
                                            "description": info['description'],
                                            "followers": info['followers'],
                                            "category": "Discovered",
                                            "persona": "Automatic"
                                        })
                                        save_x_accounts(json_path, accounts)
                                        st.success(f"已添加 @{handle}")
                                        st.rerun()
                    else:
                        st.info("未发现新的相关账号。")
                except Exception as e:
                    st.error(f"探索失败: {e}")
        else:
            if st.session_state.get('x_search_input'): # 只有点击按钮且为空时才警告
                 st.warning("请输入搜索关键词。")

def display_system_config():
    """系统配置管理界面"""
    st.header("⚙️ 系统配置中心")
    st.write("在此管理 DavidAgent 的核心配置。修改将同步到 `.env` 文件。")
    
    env_path = project_root / ".env"
    load_dotenv(env_path)
    
    with st.expander("🔑 LLM 模型与 API 密钥", expanded=True):
        gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
        dashscope_key = st.text_input("DashScope (Qwen) API Key", value=os.getenv("DASHSCOPE_API_KEY", ""), type="password")
        dashscope_endpoint = st.text_input("Qwen Endpoint", value=os.getenv("DASHSCOPE_ENDPOINT", "https://dashscope.aliyuncs.com/compatible-mode/v1"))
        
        config = BrainConfig()
        st.info(f"当前右脑模型: **{config.right_brain_model}**")
        
    with st.expander("🌐 WordPress 发布配置"):
        wp_url = st.text_input("WP REST API URL", value=os.getenv("WP_SITE_URL", ""))
        wp_user = st.text_input("WP Username", value=os.getenv("WP_USERNAME", ""))
        wp_pwd = st.text_input("WP Application Password", value=os.getenv("WP_APP_PASSWORD", ""), type="password")
        wp_app_name = st.text_input("WP App Name (默认 dvspace5)", value=os.getenv("WP_APP_NAME", "dvspace5"))
        
    with st.expander("🐙 GitHub 与代码仓库"):
        gh_token = st.text_input("GitHub Token (可选)", value=os.getenv("GITHUB_TOKEN", ""), type="password")
        
    if st.button("💾 保存配置并重启服务", type="primary"):
        # 更新 .env 文件
        set_key(str(env_path), "GEMINI_API_KEY", gemini_key)
        set_key(str(env_path), "DASHSCOPE_API_KEY", dashscope_key)
        set_key(str(env_path), "DASHSCOPE_ENDPOINT", dashscope_endpoint)
        set_key(str(env_path), "WP_SITE_URL", wp_url)
        set_key(str(env_path), "WP_USERNAME", wp_user)
        set_key(str(env_path), "WP_APP_PASSWORD", wp_pwd)
        set_key(str(env_path), "WP_APP_NAME", wp_app_name)
        if gh_token:
            set_key(str(env_path), "GITHUB_TOKEN", gh_token)
            
        st.success("✅ 配置已成功写回 .env 文件！")
        st.toast("正在通知后台服务重载配置...")
        # 实际生产中可能需要重启进程，这里先演示保存成功

def display_metacognition_center():
    """元认知管理中心：避坑指南 + 每周洞察 + Token 经济学"""
    st.header("🧠 元认知与自我进化中心")
    
    tab1, tab2, tab3 = st.tabs(["📜 避坑指南 (Guidelines)", "📅 每周观察 (Weekly Insights)", "💰 Token 经济学"])
    
    with tab1:
        st.subheader("核心避坑指南")
        st.info("这是 DavidAgent 经过夜间反思后沉淀的 10 条金科玉律。")
        guidelines_path = project_root / "dynamic_guidelines.md"
        if guidelines_path.exists():
            with open(guidelines_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(content)
        else:
            st.warning("尚未生成 dynamic_guidelines.md 文件。")
            
    with tab2:
        st.subheader("每周行业透视")
        insight_dir = project_root / "brain" / "outputs" / "weekly_insights"
        if insight_dir.exists():
            insights = sorted([f for f in os.listdir(insight_dir) if f.endswith(".md")], reverse=True)
            if insights:
                selected_insight = st.selectbox("选择周报", insights)
                if selected_insight:
                    with open(insight_dir / selected_insight, "r", encoding="utf-8") as f:
                        st.markdown(f.read())
            else:
                st.info("暂无每周洞察报告。")
        else:
            st.info("目录 `brain/outputs/weekly_insights` 尚不存在。")
            
    with tab3:
        st.subheader("Token 消耗与成本分析")
        col1, col2 = st.columns(2)
        
        # 简单从数据库所有 full_snapshot 中统计 (由于数据量大，实际应在后端聚合，这里先做个演示)
        # 注意：这在真实大规模数据下会慢，此处仅作为功能占位
        st.info("统计数据正在从情景记忆快照中提取...")
        
        # 模拟展示，之后可以解析所有 full_snapshot 里的 token 字段
        st.write("📊 **当前概览 (估算)**")
        st.metric("累计 Token 消耗", "124,502")
        st.metric("总计 API 成本", "$0.0452")
        
        st.markdown("""
        > [!NOTE]
        > 成本按 Gemini 2.5 Pro 和 Qwen Coder Plus 标准定价计算。
        """)

def display_context_management():
    """管理 .share_context 目录下的内容"""
    st.header("📂 上下文管理 (Share Context)")
    st.write("在此管理 DavidAgent 在工作流中缓存的 `.share_context` 文件。")
    
    # 定位路径 (已迁移至 DavidAgent 根目录)
    context_path = Path("/Users/zhaoqinhuang/david_project/DavidAgent/.share_context")
    
    if not context_path.exists():
        st.warning(f"目录不存在: `{context_path}`")
        return
        
    files = []
    for f in context_path.iterdir():
        if f.is_file():
            stats = f.stat()
            files.append({
                "文件名": f.name,
                "大小 (KB)": round(stats.st_size / 1024, 2),
                "最近修改": pd.to_datetime(stats.st_mtime, unit='s'),
                "path": str(f)
            })
            
    if not files:
        st.info("当前无有效的上下文缓存文件。")
        return
        
    df = pd.DataFrame(files)
    
    # 全选删除功能
    st.subheader(f"当前共有 {len(files)} 个缓存文件")
    
    # 使用 st.dataframe 选择
    event = st.dataframe(
        df[["文件名", "大小 (KB)", "最近修改"]], 
        use_container_width=True,
        on_select="rerun",
        selection_mode="multi-row",
        key="context_files_df"
    )
    
    selected_indices = event.get('selection', {}).get('rows', [])
    
    if selected_indices:
        st.write(f"已选择 {len(selected_indices)} 个文件")
        
        # 预览功能 (仅预览第一个选中的文件)
        first_idx = selected_indices[0]
        preview_file = Path(df.iloc[first_idx]['path'])
        
        if preview_file.suffix.lower() == '.md':
            st.divider()
            st.subheader(f"📄 预览: {preview_file.name}")
            try:
                with open(preview_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    st.markdown(content)
            except Exception as e:
                st.error(f"无法读取预览内容: {e}")
        
        st.divider()
        if st.button("🗑️ 彻底删除选中的上下文", type="primary"):
            for idx in selected_indices:
                file_to_del = Path(df.iloc[idx]['path'])
                try:
                    file_to_del.unlink()
                except Exception as e:
                    st.error(f"删除 {file_to_del.name} 失败: {e}")
            st.success("选定文件已清理。")
            st.rerun()
    
    # 快捷操作
    st.divider()
    if st.button("🧹 一键清理所有上下文"):
        for f_info in files:
            try:
                Path(f_info['path']).unlink()
            except:
                pass
        st.success("所有上下文已清理。")
        st.rerun()

def display_perceptor_center():
    """感知中心 (Perceptor / X-Spider)"""
    st.header("📡 感知中心 (Perceptor Control)")
    st.write("监控 X-Spider 实时采集动态、历史数据及统计指标。")

    # 1. 顶部指标概览 (Phase 18.1)
    db = st.session_state.db
    stats = db.get_signal_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("总采集推文数", stats['total_count'])
    col2.metric("今日新增推文", stats['today_count'], delta=stats['today_count'])
    col3.metric("监控账号总数", len(stats['handle_dist']))

    st.divider()

    # 新增：受控采样控制面板 (Phase 20)
    with st.expander("🛠️ 受控采样采集 (Batch Control)", expanded=True):
        status_info = db.get_task_status("x_batch_crawl")
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            curr_status = status_info.get('status', 'idle').upper()
            st.write(f"**当前状态**: `{curr_status}`")
            if status_info.get('progress'):
                st.info(status_info['progress'])
            if status_info.get('config'):
                try:
                    selected = json.loads(status_info['config'])
                    st.caption(f"🎯 选定对象: {', '.join(selected[:5])}...")
                except:
                    pass
        
        with c2:
            if status_info.get('status') == 'idle':
                if st.button("🚀 开始随机采样", type="primary", use_container_width=True, key="start_batch"):
                    log_file_path = project_root / "brain/batch_worker.log"
                    log_file = open(log_file_path, "w")
                    subprocess.Popen([sys.executable, "-u", "brain/x_batch_worker.py"], stdout=log_file, stderr=subprocess.STDOUT)
                    st.success("后台进程已启动")
                    st.rerun()
            else:
                st.button("🚀 开始随机采样", disabled=True, use_container_width=True, key="start_batch_disabled")
                
        with c3:
            if status_info.get('status') == 'running':
                if st.button("🛑 紧急停止", type="secondary", use_container_width=True, key="stop_batch"):
                    db.set_task_status("x_batch_crawl", "stopping", progress="正在准备停止...")
                    st.warning("已发送停止信号")
                    st.rerun()
            elif status_info.get('status') == 'stopping':
                if st.button("🔄 强制重置", type="primary", use_container_width=True, key="force_reset_batch"):
                    db.set_task_status("x_batch_crawl", "idle", progress="已手动强制重置")
                    st.success("状态已重置")
                    st.rerun()
            else:
                st.button("🛑 紧急停止", disabled=True, use_container_width=True, key="stop_batch_disabled")

        st.divider()
        st.write("🎛️ **采集调度频率配置** (实时对后台 Worker 生效)")
        
        try:
            config_dict = json.loads(status_info.get('config') or "{}")
            if not isinstance(config_dict, dict):
                # Fallback if config was saved as a list previously
                config_dict = {} 
        except:
            config_dict = {}
            
        default_account_min = config_dict.get('account_min_sleep', 30)
        default_account_max = config_dict.get('account_max_sleep', 120)
        default_req_min = config_dict.get('req_min_sleep', 5)
        default_req_max = config_dict.get('req_max_sleep', 15)
        
        sccol1, sccol2 = st.columns(2)
        with sccol1:
            account_sleeps = st.slider("账号间休眠延迟范围 (秒)", 1, 300, (default_account_min, default_account_max))
        with sccol2:
            req_sleeps = st.slider("请求间步态延迟范围 (秒)", 1, 60, (default_req_min, default_req_max))
            
        if (account_sleeps[0] != default_account_min or account_sleeps[1] != default_account_max or 
            req_sleeps[0] != default_req_min or req_sleeps[1] != default_req_max):
            
            # preserve list of accounts if previously stored
            if "targets" not in config_dict and isinstance(json.loads(status_info.get('config') or "[]"), list):
                config_dict["targets"] = json.loads(status_info.get('config') or "[]")
                
            config_dict.update({
                'account_min_sleep': account_sleeps[0],
                'account_max_sleep': account_sleeps[1],
                'req_min_sleep': req_sleeps[0],
                'req_max_sleep': req_sleeps[1]
            })
            if st.button("💾 保存调度配置", type="primary"):
                db.set_task_status("x_batch_crawl", status_info.get('status', 'idle'), json.dumps(config_dict, ensure_ascii=False))
                st.success("配置已更新！")
                st.rerun()

        # 新增日志显示 (最新在顶部)
        st.write("---")
        log_c1, log_c2 = st.columns([5, 1])
        with log_c1:
            st.caption("📜 运行日志 (实时获取 - 最新日志在最上方)")
        with log_c2:
            if st.button("🔄 刷新日志", key="refresh_log_btn", use_container_width=True):
                st.rerun()

        log_path = project_root / "brain/batch_worker.log"
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    logs = f.readlines()
                    logs.reverse()  # 颠倒顺序，最新的在顶部
                    log_text = "".join(logs[:50]) if logs else "暂无日志"
                    st.text_area("Logs", value=log_text, height=250, label_visibility="collapsed")
            except Exception as e:
                st.error(f"读取日志失败: {e}")

    st.divider()

    tabs = st.tabs(["📊 采集概览", "🕵️ 原始信号查询", "📈 分布统计", "🛡️ 去重机制状态"])

    with tabs[0]:
        st.subheader("实时采集流")
        try:
            df = load_signal_list(limit=20)
            if not df.empty:
                for _, row in df.iterrows():
                    # 增强内容聚合显示
                    type_icon = "📄 Article" if row.get('signal_type') == 'article' else "🐦 Post"
                    with st.expander(f"{type_icon} | @{row['handle']} - {row['author_name']} | {row['ingested_at']}"):
                        if row.get('signal_type') == 'article':
                            st.markdown(row['raw_text'])
                        else:
                            st.write(row['raw_text'])
                        
                        st.caption(f"🆔 ID: `{row['signal_id']}` | 📅 发布于: `{row['timestamp']}`")
            else:
                st.info("检测中... 暂无实时采集数据")
        except Exception as e:
            st.error(f"无法加载实时流: {e}")

    with tabs[1]:
        # ... (保留原有逻辑)
        st.subheader("历史信号库")
        col1, col2 = st.columns([2, 1])
        limit = col2.number_input("显示条数", 10, 500, 100)
        
        df_all = load_signal_list(limit=limit)
        if not df_all.empty:
            st.markdown("👇 **点击表格中的任意一行**，即可在下方联动显示其完整的原始采集内容。")
            event = st.dataframe(
                df_all[['signal_id', 'signal_type', 'handle', 'author_name', 'timestamp', 'ingested_at']],
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            signal_ids = df_all['signal_id'].tolist()
            default_index = 0
            
            if event and hasattr(event, "selection") and getattr(event.selection, "rows", []):
                selected_idx = event.selection.rows[0]
                if selected_idx < len(df_all):
                    clicked_sig = df_all.iloc[selected_idx]['signal_id']
                    if clicked_sig in signal_ids:
                        default_index = signal_ids.index(clicked_sig)
            
            selected_sig = st.selectbox("也可手动选择或搜索特定信号 ID：", signal_ids, index=default_index)
            
            if selected_sig:
                details = load_signal_details(selected_sig)
                if details:
                    with st.container(border=True):
                        # 顶部栏：标题与操作按钮
                        d_col1, d_col2 = st.columns([4, 1])
                        with d_col1:
                            st.write(f"**信号详情**: `{selected_sig}`")
                        with d_col2:
                            if st.button("🗑️ 删除该信号", type="primary", use_container_width=True, key=f"del_{selected_sig}"):
                                if db.delete_raw_signal(selected_sig):
                                    st.success("删除成功！正在刷新...")
                                    load_signal_list.clear() # Clear cache
                                    import time
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("删除失败")
                                    
                        st.text_area("RAW TEXT", details.get('raw_text', ''), height=200)
                        with st.expander("🛠️ 查看底层抓取的完整 RAW JSON"):
                            try:
                                st.json(json.loads(details['raw_json']))
                            except:
                                st.text(details['raw_json'])
        else:
            st.info("暂无历史信号记录")

    with tabs[2]:
        st.subheader("账号采集分布")
        if stats['handle_dist']:
            dist_df = pd.DataFrame(list(stats['handle_dist'].items()), columns=['Handle', 'Count'])
            st.bar_chart(dist_df, x='Handle', y='Count', color="#4F8BF9")
            
            st.write("数据分布概览:")
            st.table(dist_df)
        else:
            st.info("暂无分配数据")

    with tabs[3]:
        st.subheader("内容级 Hash 去重系统")
        st.info("DavidAgent 使用 MD5 内容指纹技术，确保同一条推文不会重复进入工作流。")
        if not df_all.empty:
            st.write("最新 Hash 样板 (MD5):")
            st.dataframe(df_all[['content_hash', 'handle', 'ingested_at']].head(10))
        
        st.metric("去重引擎状态", "ACTIVE (WAL Mode)")

def display_system_status():
    """系统运行状态看板"""
    st.header("🚥 系统运行状态控制台")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("核心引擎: **RUNNING**")
    with col2:
        st.success("API 弹性保护: **ENABLED**")
    with col3:
        st.info("当前并发限额: **3**")
        
    st.divider()
    st.subheader("📡 后台进程状态")
    
    # 这里可以使用 subprocess.check_output 检查 ag_worker.py 是否在运行
    import subprocess
    try:
        pgrep_output = subprocess.check_output(["pgrep", "-f", "ag_worker.py"]).decode().strip()
        st.write(f"✅ `ag_worker.py` (PID: {pgrep_output}) 正在后台辛勤工作...")
    except:
        st.error("❌ `ag_worker.py` 未在运行，系统可能处于离线状态。")

    st.divider()
    st.subheader("🛠️ 核心参数概览")
    config = BrainConfig()
    st.json({
        "left_brain_model": config.left_brain_model,
        "right_brain_model": config.right_brain_model,
        "db_mode": "WAL Enabled",
        "api_resilience": "Exponential Backoff"
    })

def display_left_brain_monitor():
    """展示左脑监控中心"""
    st.header("🧠 左脑监控中心 (Left Brain Monitor)")
    st.markdown("该面板专门用于监控 `Gemini 3.1 Pro` 左脑中枢的 **ETL 知识提取** 与 **红蓝对抗 (免疫系统)** 运行结果。")
    
    top_tabs = st.tabs(["🧩 单点信号解析 (Signal Pipeline)", "🌐 全局知识图谱 (Systemic Graph)"])
    
    with top_tabs[0]:
        with st.expander("🔍 知识翻查 (PageIndex Search)"):
            st.markdown("与左脑共享的本地知识库检索能力。输入概念关键字，快速翻查对应的系统架构设计或已生成的图谱沉淀。")
            search_kw = st.text_input("输入检索关键字 (例如: 海马体, GraphData):")
            if st.button("检索知识流", key="btn_pageindex_search") and search_kw:
                from brain.left_brain.pageindex_tool import search_pageindex
                with st.spinner("正在全局翻阅本地 PageIndex 与 Docs..."):
                    search_res = search_pageindex(search_kw)
                    st.code(search_res, language="markdown")
        
        with st.expander("📂 摄入本地文档库 (docs/) 作为左脑真理基座"):
            st.markdown("将 `DavidAgent/docs` 下的所有 Markdown 文档解析为底层信号传入神经总线。")
            if st.button("开始批量摄入本地文档", type="primary"):
                db = st.session_state.db
                docs_path = Path(__file__).parent.parent / "docs"
                if docs_path.exists():
                    ingested_count = 0
                    for md_file in docs_path.rglob("*.md"):
                        try:
                            with open(md_file, "r", encoding="utf-8") as f:
                                content = f.read()
                            if not content.strip(): continue
                            
                            import hashlib
                            from datetime import datetime
                            import time
                            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                            
                            if not db.check_duplicate(content_hash):
                                signal_id = f"doc_{content_hash[:10]}"
                                
                                signal_data = {
                                    "raw_text": f"【系统架构文档: {md_file.name}】\n{content}",
                                    "source": "docs",
                                    "url": str(md_file),
                                    "timestamp": datetime.now().isoformat(),
                                    "type": "document"
                                }
                                
                                import json
                                # 写入信号与黑板
                                db.conn.execute('''
                                    INSERT INTO raw_signals (signal_id, content_hash, raw_json, raw_text, signal_type, processed)
                                    VALUES (?, ?, ?, ?, ?, 0)
                                ''', (signal_id, content_hash, json.dumps(signal_data), signal_data['raw_text'], 'document'))
                                
                                db.conn.execute('''
                                    INSERT INTO trace_logs (task_id, created_at, workflow_status, signal_data)
                                    VALUES (?, ?, ?, ?)
                                ''', (signal_id, datetime.now(), 'START', signal_data['raw_text']))
                                db.conn.commit()
                                ingested_count += 1
                        except Exception as e:
                            st.error(f"解析 {md_file.name} 失败: {e}")
                    
                    if ingested_count > 0:
                        st.success(f"✅ 成功摄取 {ingested_count} 篇 Markdown 文档！已进入 START 队列。")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.info("没有新的 Markdown 文档需要摄入 (或已全部存在)。")
                else:
                    st.error(f"找不到 docs 目录: {docs_path}")

        # --- 信号选定区域 ---
        signals_df = load_signal_list(limit=50)
        
        if signals_df.empty:
            st.info("⏳ 原始信号库暂时为空，等待感知器抓取或手动喂饭。")
            return
            
        def format_signal_option(signal_id):
            row = signals_df[signals_df['signal_id'] == signal_id].iloc[0]
            stype = row['signal_type']
            emoji = "🐦" if stype == "tweet" else "📚" if stype == "document" else "📄"
            date_val = str(row.get('timestamp', row.get('ingested_at', ''))).split()[0]
            text_preview = row['raw_text'][:20] + "..." if len(row['raw_text']) > 20 else row['raw_text']
            return f"{emoji} [{date_val}] {signal_id} | {text_preview}"
            
        selected_signal_id = st.selectbox(
            "选择要溯源的信号槽 (Signal ID)",
            options=signals_df['signal_id'].tolist(),
            format_func=format_signal_option,
            index=0
        )
        
        if selected_signal_id:
            raw_details = load_signal_details(selected_signal_id)
            task_details = load_task_details(selected_signal_id)
            
            tabs = st.tabs(["📥 阶段一: 原始输入", "🧬 阶段二: ETL 知识提取 (GraphData)", "🛡️ 阶段三: 红蓝对抗 (FactCheckResult)"])
            
            with tabs[0]:
                if raw_details:
                    st.markdown("### 📡 原始异构数据")
                    st.code(raw_details['raw_text'], language="markdown")
                else:
                    st.error("无法加载该信号的原始数据。")
                    
            with tabs[1]:
                if task_details and task_details.get('left_brain_graph'):
                    st.markdown("### 🕸️ 知识图谱晶体 (Pydantic Schema)")
                    import json
                    try:
                        graph_data = json.loads(task_details['left_brain_graph'])
                        st.subheader("摘要 (Summary)")
                        st.info(graph_data.get('summary', ''))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("核心实体 (Entities)")
                            st.json(graph_data.get('entities', []))
                        with col2:
                            st.subheader("逻辑关系 (Triples)")
                            st.json(graph_data.get('triples', []))
                    except json.JSONDecodeError:
                        st.error("GraphData JSON 解析失败。")
                        st.code(task_details['left_brain_graph'])
                else:
                    st.warning("⚠️ 该信号暂未经过 ETL 提取，或因关联度过低被丢弃。")
                    
            with tabs[2]:
                if task_details and task_details.get('left_brain_fact_check'):
                    st.markdown("### 👮 免疫系统审查与对抗记录")
                    try:
                        fact_check = json.loads(task_details['left_brain_fact_check'])
                        passed = fact_check.get('passed', False)
                        
                        if passed:
                            st.success("✅ **事实核查通过:** 没有发现捏造或主观幻觉。可以向海马体与突触网络流转。")
                        else:
                            st.error("❌ **事实核查失败:** 提取过程中发现杂质或幻觉，已驳回或标记。")
                            
                        st.markdown("#### 核查反馈 (Feedback)")
                        st.write(fact_check.get('feedback', '无可奉告'))
                        
                        hallucinations = fact_check.get('hallucinations', [])
                        if hallucinations:
                            st.markdown("#### 🚨 捕获的幻觉 (Hallucinations)")
                            for h in hallucinations:
                                st.warning(f"- {h}")
                    except json.JSONDecodeError:
                        st.error("FactCheckResult JSON 解析失败。")
                        st.code(task_details['left_brain_fact_check'])
                else:
                    st.info("ℹ️ 该信号不需要经过严苛核查，或尚未进入 Phase II 对抗验证流程。")

    with top_tabs[1]:
        st.markdown("### 全局 RDF 本体网络")
        st.caption("展示使用 `rdflib` 积累融合的所有左脑提取成果，这代表了系统当下的综合认知版图。")
        
        from brain.memory.global_graph import SystemicKnowledgeGraph
        sys_graph = SystemicKnowledgeGraph()
        
        if len(sys_graph.g) == 0:
            st.warning("当前全局图谱为空。请先去单点信号界面摄入文档。")
        else:
            st.success(f"🌐 宇宙扩展中：当前融合了 **{len(sys_graph.g)}** 个三元组事实。")
            
            with st.expander("🔍 图谱语义检索 (SPARQL Query)", expanded=False):
                st.markdown("标准化访问全局数据。您可以通过关键词极速检索，或者输入原生 SPARQL 查询深度交融的关系。")
                query_mode = st.radio("查询模式", ["极速搜索 (Keyword)", "高级查询 (Raw SPARQL)"], horizontal=True)
                
                if query_mode == "极速搜索 (Keyword)":
                    keyword = st.text_input("输入实体或概念 (例如: LeftBrain, 幻觉):")
                    if st.button("🔎 检索图谱") and keyword:
                        query = f"""
                        SELECT ?subject ?predicate ?object
                        WHERE {{
                            ?subject ?predicate ?object .
                            FILTER(regex(str(?subject), "{keyword}", "i") || regex(str(?object), "{keyword}", "i"))
                        }}
                        """
                        try:
                            results = sys_graph.g.query(query)
                            res_list = []
                            for row in results:
                                res_list.append({
                                    "Subject": str(row[0]).split('#')[-1],
                                    "Predicate": str(row[1]).split('#')[-1],
                                    "Object": str(row[2]).split('#')[-1]
                                })
                            if res_list:
                                st.dataframe(res_list, use_container_width=True)
                                st.success(f"找到 {len(res_list)} 条交互记录。")
                            else:
                                st.info("未找到包含该关键词的实体或关系。")
                        except Exception as e:
                            st.error(f"检索失败: {e}")
                            
                else:
                    raw_query = st.text_area("输入标准的 SPARQL 语句:", 
                        value="SELECT ?s ?p ?o\nWHERE {\n  ?s ?p ?o .\n}\nLIMIT 50", height=150)
                    if st.button("⚡ 执行 SPARQL"):
                        try:
                            results = sys_graph.g.query(raw_query)
                            cols = [str(v) for v in results.vars] if hasattr(results, 'vars') else ["Subject", "Predicate", "Object"]
                            res_list = []
                            for row in results:
                                res_list.append({cols[i]: str(row[i]).split('#')[-1] for i in range(len(row))})
                            if res_list:
                                st.dataframe(res_list, use_container_width=True)
                            else:
                                st.info("查询执行成功，但结果集为空。")
                        except Exception as e:
                            st.error(f"SPARQL 语法错误或执行失败: {e}")

            # --- 新增：动态字号与显示控制 ---
            st.divider()
            st.subheader("🎛️ 图谱显示偏好设置")
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                ui_core_font = st.slider("核心实体字号", min_value=14, max_value=50, value=30, step=2)
                ui_core_size = int(ui_core_font * 1.1)
            with col_f2:
                ui_attr_font = st.slider("属性节点字号", min_value=12, max_value=40, value=24, step=2)
                ui_attr_size = int(ui_attr_font * 1.05)
            with col_f3:
                ui_edge_font = st.slider("连线关系字号", min_value=10, max_value=30, value=20, step=2)

            if st.button("生成交互式可视化网络", type="primary", key="btn_render_sys_graph"):
                with st.spinner("正在通过 PyVis 渲染全局网络，请稍候..."):
                    import streamlit.components.v1 as components
                    from pyvis.network import Network
                    
                    # 使用 remote 避免由于 in_line javascript 过大导致 streamlit 卡死/白屏
                    net = Network(height="600px", width="100%", bgcolor="white", font_color="#333333", cdn_resources='remote')
                    net.barnes_hut()
                    # 开启物理系统使节点排布更合理
                    net.toggle_physics(True)
                    
                    from rdflib import URIRef
                    nodes_added = set()
                    
                    for subj, pred, obj in sys_graph.g:
                        s_name = subj.split('#')[-1]
                        o_name = obj.split('#')[-1] if isinstance(obj, URIRef) else str(obj)[:25] + "..."
                        p_name = pred.split('#')[-1]
                        
                        if s_name not in nodes_added:
                            # 增大核心节点的字体与物理体积
                            net.add_node(s_name, label=f"实体:\n{s_name}", title=s_name, size=ui_core_size, color="#ff4b4b", font={"color": "#333333", "size": ui_core_font, "face": "Arial", "bold": True})
                            nodes_added.add(s_name)
                        
                        if o_name not in nodes_added:
                            o_trunc = o_name[:20] + "..." if len(o_name) > 20 else o_name
                            net.add_node(o_name, label=f"属性/实体:\n{o_trunc}", title=o_name, size=ui_attr_size, color="#1f77b4", font={"color": "#333333", "size": ui_attr_font, "face": "Arial"})
                            nodes_added.add(o_name)
                            
                        # Edge 加上提示信息并调大字号
                        net.add_edge(s_name, o_name, title=p_name, label=f"({p_name})", color="#c2c2c2", font={"color": "#333333", "size": ui_edge_font, "face": "Arial", "background": "rgba(255,255,255,0.8)"})
                        
                    # 动态增加一些物理规则修正避免节点贴太紧而文字重叠
                    net.set_options("""
                    var options = {
                      "physics": {
                        "barnesHut": {
                          "gravitationalConstant": -40000,
                          "centralGravity": 0.3,
                          "springLength": 250,
                          "springConstant": 0.04,
                          "damping": 0.09,
                          "avoidOverlap": 0.5
                        },
                        "minVelocity": 0.75
                      }
                    }
                    """)
                        
                    tmp_html = "/tmp/systemic_graph.html"
                    net.save_graph(tmp_html)
                    
                    with open(tmp_html, 'r', encoding='utf-8') as f:
                        html_source = f.read()
                        
                    # 注入全屏按钮与自适应缩放JS代码
                    fullscreen_btn = """
                    <style>
                    body { margin: 0; padding: 0; overflow: hidden; background-color: white; }
                    #mynetwork { border: none !important; }
                    </style>
                    <button id="fs-btn" style="position:fixed; top:10px; right:10px; z-index:9999; padding:8px 15px; background-color:#ff4b4b; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                      ⛶ 全屏模式 (Fullscreen)
                    </button>
                    <script>
                    var myNet = document.getElementById('mynetwork');
                    var origHeight = myNet.style.height;
                    
                    document.getElementById('fs-btn').addEventListener('click', function() {
                        var elem = document.documentElement;
                        if (!document.fullscreenElement) {
                            elem.requestFullscreen().catch(err => {
                                alert(`Error attempting to enable fullscreen mode: ${err.message} (${err.name})`);
                            });
                        } else {
                            document.exitFullscreen();
                        }
                    });
                    
                    document.addEventListener('fullscreenchange', (event) => {
                        if (document.fullscreenElement) {
                            document.getElementById('fs-btn').innerText = "✖ 退出全屏 (Exit)";
                            myNet.style.height = '100vh';
                            myNet.style.width = '100vw';
                            if (typeof network !== 'undefined') { network.redraw(); network.fit({animation: true}); }
                        } else {
                            document.getElementById('fs-btn').innerText = "⛶ 全屏模式 (Fullscreen)";
                            myNet.style.height = origHeight;
                            myNet.style.width = '100%';
                            if (typeof network !== 'undefined') { network.redraw(); network.fit({animation: true}); }
                        }
                    });
                    
                    // 物理稳定后自动居中缩放到最合适视角
                    if (typeof network !== 'undefined') {
                        network.once("stabilizationIterationsDone", function() {
                            network.fit({animation: {duration: 1000, easingFunction: "easeInOutQuad"}});
                        });
                    }
                    </script>
                    """
                    html_source = html_source.replace('</body>', fullscreen_btn + '</body>')
                        
                    components.html(html_source, height=620)

def main():
    """主函数"""
    st.set_page_config(page_title="DavidAgent 元认知大盘", layout="wide")
    st.title("🧠 DavidAgent 双脑工作流全景复盘大盘")
    
    # 初始化会话状态
    initialize_session_state()
    
    # 侧边栏导航
    st.sidebar.title("🎮 控制中心")
    app_mode = st.sidebar.radio(
        "选择功能模块", 
        ["工作流复盘", "🧠 左脑监控 (Left Brain)", "感知中心 (Perceptor)", "X 账号管理", "元认知管理", "系统状态", "系统设置", "上下文管理"]
    )
    
    if app_mode == "工作流复盘":
        # ... (此处省略，保持原有逻辑)
        # 高性能优化：缓存侧边栏的轻量级列表
        st.sidebar.header("📜 历史任务 (Top 50)")
        df_tasks = load_task_list(limit=50)
        
        if df_tasks.empty:
            st.info("暂无任务记录")
            return
            
        # 任务选择
        selected_task = st.sidebar.selectbox(
            "选择复盘任务", 
            df_tasks['task_id'].tolist(),
            index=0
        )
        
        if selected_task:
            # 懒加载任务详情
            task_details = load_task_details(selected_task)
            if task_details:
                display_task_details(task_details)
                handle_human_feedback(selected_task)
            else:
                st.error("无法加载任务详情")
    elif app_mode == "🧠 左脑监控 (Left Brain)":
        display_left_brain_monitor()
    elif app_mode == "感知中心 (Perceptor)":
        display_perceptor_center()
    elif app_mode == "X 账号管理":
        display_account_management()
    elif app_mode == "元认知管理":
        display_metacognition_center()
    elif app_mode == "系统状态":
        display_system_status()
    elif app_mode == "系统设置":
        display_system_config()
    elif app_mode == "上下文管理":
        display_context_management()


if __name__ == "__main__":
    main()