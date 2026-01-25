#!/bin/bash

# 1. 获取文件名参数，如果没有提供，则默认使用 test.md
FILE_NAME=${1:-"test.md"}

# 2. 检查文件是否存在
if [ ! -f "$FILE_NAME" ]; then
    echo "错误: 文件 $FILE_NAME 不存在，请检查文件名或路径。"
    exit 1
fi

# 3. 确保在仓库目录下
cd "$(dirname "$0")"

# 4. 执行 Git 操作
echo "正在处理文件: $FILE_NAME ..."
git add "$FILE_NAME"
git commit -m "Auto-update: AI generated $FILE_NAME on $(date '+%Y-%m-%d %H:%M:%S')"

# 5. 推送到 GitHub
# 确保你已配置 SSH 或 Credential Helper 以免除密码确认
git push origin main

echo "成功：$FILE_NAME 已推送到 GitHub 仓库！"
