# imessage.py
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def send_to_iphone(content):
    """
    调用 macOS 的 Messages 应用发送 iMessage
    """
    phone_number = os.getenv("MY_PHONE_NUMBER")
    
    if not phone_number:
        print("❌ 错误: 未在 .env 中找到 MY_PHONE_NUMBER")
        return False

    # 处理内容中的双引号，防止破坏 AppleScript 语法
    safe_content = content.replace('"', '\\"').replace("'", "\\'")

    # AppleScript 脚本
    # 逻辑：告诉 Messages 应用，找到对应号码的 buddy，并发消息
    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone_number}" of targetService
        send "{safe_content}" to targetBuddy
    end tell
    '''

    try:
        # 执行 AppleScript
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"📱 iMessage 已推送到: {phone_number}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ iMessage 发送失败. 请检查号码是否正确，或是否给予了终端权限。")
        print(f"错误信息: {e}")
        return False