import os
import json
import base64
import requests

def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("tenant_access_token")
    return None

def upload_file(token, file_path):
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    
    with open(file_path, "rb") as f:
        files = {
            "file": (file_name, f, "text/markdown"),
            "file_type": (None, "stream"),
            "file_name": (None, file_name)
        }
        from requests_toolbelt import MultipartEncoder
        m = MultipartEncoder(
            fields={'file_type': 'stream', 'file_name': file_name, 'file': (file_name, open(file_path, 'rb'), 'text/markdown')}
        )
        headers['Content-Type'] = m.content_type
        response = requests.post(url, headers=headers, data=m)
        
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data["data"]["file_key"]
        else:
            print("Upload Error:", data)
    else:
        print("Upload HTTP Error:", response.text)
    return None

def send_file_message(token, chat_id, file_key):
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "receive_id": chat_id,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    app_id = "cli_a9f6b35832799bdf"
    app_secret = "vEinjEwHXN34K0pGeOYMNciWc2bRJAks"
    chat_id = "ou_e06f1450d233b1d7b88e827607add690" # open_id from context
    file_path = "/Users/zhaoqinhuang/david_project/sign_change_benchmark/report.md"
    
    print("1. 获取 Token...")
    token = get_tenant_access_token(app_id, app_secret)
    if not token:
        print("获取 Token 失败")
        exit(1)
        
    print("2. 上传文件...")
    file_key = upload_file(token, file_path)
    if not file_key:
        print("上传文件失败")
        exit(1)
        
    print(f"文件上传成功，file_key: {file_key}")
    
    print("3. 发送消息...")
    res = send_file_message(token, chat_id, file_key)
    print(f"发送结果: {json.dumps(res, ensure_ascii=False)}")
