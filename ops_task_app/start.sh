#!/bin/bash
# 运营任务地图 - 一键启动脚本

echo "=============================="
echo "  运营任务地图 启动中..."
echo "=============================="

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装：sudo apt install python3 python3-pip"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip3 install -r requirements.txt -q

# 创建数据目录
mkdir -p data

# 启动服务
echo ""
echo "✅ 启动成功！"
echo "👉 在浏览器打开：http://你的服务器IP:8000"
echo "   （局域网内其他人也可以通过同样地址访问）"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=============================="

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
