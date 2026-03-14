#!/bin/bash
# DavidAgent 感知收割机一键启动脚本

set -e  # 遇错立即退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 DavidAgent 感知收割机启动中..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python 3.9+"
    exit 1
fi

# 检查凭据文件
if [ ! -f "../.credentials/api_keys.env" ]; then
    echo "⚠️  警告: 凭据文件不存在，将使用受限模式运行"
    echo "💡 提示: 请编辑 ../.credentials/api_keys.env 配置 API Token"
else
    echo "✅ 凭据文件已找到"
fi

# 检查依赖
echo "🔍 检查依赖..."
python3 -c "import polars, requests, feedparser, aiohttp, bs4" 2>/dev/null || {
    echo "❌ 依赖缺失，请先安装依赖:"
    echo "   pip3 install -r requirements.txt --break-system-packages"
    exit 1
}

# 创建必要目录
mkdir -p hippocampus/episodic logs reports

# 运行感知收割机
echo "🎯 启动五大感知通道..."
cd brain/sensors
python3 run_discovery.py "$@"

echo "✅ DavidAgent 感知收割机执行完成！"
echo "📊 查看报告: ../../reports/daily_report_*.md"
echo "📝 查看日志: ../../logs/discovery.log"