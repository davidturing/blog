#!/bin/bash

# 科技达人世界感知自主演进 - 定时执行脚本
# 应该通过 crontab 在每天凌晨 01:00 执行

set -e

echo "🤖 科技达人世界感知自主演进启动..."

# 检查是否在正确的目录
if [ ! -f "sensors/tech_blogger_watcher.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 创建必要的目录
mkdir -p logs data memory config

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如果需要）
if [ ! -f "venv/.installed" ]; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# 运行科技达人演进
echo "🚀 执行世界感知演进..."
python -m sensors.tech_blogger_watcher

echo "✅ 科技达人演进完成！"