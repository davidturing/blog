import autogen
from api_config import API_KEYS

def get_reviewer_agent():
    # 使用 Gemini 作为架构审查官
    gemini_config = {
        "config_list": [{"model": "gemini-1.5-pro", "api_key": API_KEYS.get("gemini_api_key", "")}],
        "temperature": 0.0,
        "max_tokens": 2048
    }

    REVIEWER_SYSTEM_PROMPT = """
    你是 AutoGen 架构级的资深审查专家 (AutoGen_Arch_Review_Agent)。
    你的**唯一职责**是审查 AutoGen 多智能体代码中的执行时序、异步通信逻辑与状态机同步风险。

    【你的审查边界】
    你**必须无视**任何业务逻辑（如金融计算、机器学习算法）、普通语法错误、拼写或代码格式问题。
    你只专注于寻找会导致“死锁”、“流程提前中断”、“状态机乱序”或“未处理的异步挂起”等【致命架构 BUG】。

    【必查清单 (Checklist)】
    1. 同步与异步混用风险：检查是否在 `async def` 中错误使用了同步的 `initiate_chat` 而非 `a_initiate_chat`。
    2. 状态机非阻塞读取：检查是否存在刚发起对话任务（无论同步或 `asyncio.create_task`）后，主线程立刻执行 `get_state()` 的时序错误（必须使用 `wait_for_state` 或相应的 Event 阻塞机制）。
    3. 状态流转断链：检查 DAG (有向无环图) 流程中，上游 Agent 的执行结果是否能够可靠地触发状态机的变更以唤醒下游 Agent。
    4. 异步死锁陷阱：检查是否有未 `await` 的协程对象，或者使用了 `time.sleep()` 阻塞了整个异步事件循环 (Event Loop)。
    5. 左右脑执行顺序：审查多智能体之间是否存在抢占式写入 Blackboard 导致数据脏读、写冲突的架构漏洞。

    【输出格式要求】
    如果发现上述风险，你必须以严格的格式输出：
    🚨 **【致命架构 BUG】**：<简述问题核心>
    - **触发原因**：<解释为何会导致死锁/断流>
    - **修复方案**：<给出正确的 AutoGen 或 asyncio 语法/代码修正>

    如果代码在架构与时序上完全安全，请输出：
    ✅ **【架构安全审查通过】**：未发现时序、异步调度或状态机流转风险。
    """

    autogen_arch_reviewer = autogen.AssistantAgent(
        name="AutoGen_Arch_Review_Agent",
        system_message=REVIEWER_SYSTEM_PROMPT,
        llm_config=gemini_config
    )
    return autogen_arch_reviewer

def run_arch_review(files_to_review=None):
    if not files_to_review:
        files_to_review = ["dml_pipeline.py", "blackboard.py", "autogen_agents.py"]
    
    reviewer = get_reviewer_agent()
    proxy_trigger = autogen.UserProxyAgent(
        name="Review_Trigger",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config={"use_docker": False}
    )

    print("\n" + "="*50)
    print("🔍 [系统拦截] 正在启动 AutoGen 底层架构 BUG 自动审查...")
    print("="*50)

    for file_path in files_to_review:
        print(f"\n=> 正在审查: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            
            prompt = f"请严格审查以下 AutoGen 系统的代码文件 `{file_path}`，寻找异步时序与状态机 BUG：\n\n```python\n{code_content}\n```"
            
            # 使用 initiate_chat 触发审查
            proxy_trigger.initiate_chat(
                reviewer,
                message=prompt,
                clear_history=True,
                silent=True # 控制台输出由我们自行控制
            )
            
            # 提取 Reviewer 的回复
            last_msg = proxy_trigger.last_message(reviewer)
            if last_msg and last_msg.get("content"):
                reply = last_msg["content"]
                if "🚨" in reply or "致命架构 BUG" in reply:
                    print(f"❌ 警告: 在 {file_path} 中发现潜在架构风险！")
                    print(reply)
                else:
                    print(f"✅ {file_path}: 架构安全审查通过。")
            else:
                print(f"⚠️ {file_path}: 审查未能返回结果。")
                
        except Exception as e:
            print(f"审查文件 {file_path} 时发生异常: {e}")

if __name__ == "__main__":
    run_arch_review()
