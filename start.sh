#!/usr/bin/env bash
# AI小商 - 一键启动脚本（可双击运行）

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=========================================="
echo "    AI小商 - 智慧校园AI伙伴"
echo "    一键启动脚本"
echo "=========================================="

# 检测 Node.js
if ! command -v node &>/dev/null; then
    echo "错误: 未找到 Node.js"
    echo ""
    echo "请先安装 Node.js："
    echo "  1) 官网下载: https://nodejs.org/"
    echo "  2) Homebrew: brew install node"
    echo "  3) nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    exit 1
fi

# 检测 Python3
if ! command -v python3 &>/dev/null; then
    echo "错误: 未找到 Python3"
    echo "请安装 Python3: https://www.python.org/downloads/"
    exit 1
fi

# 创建后端虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "[1/4] 创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
else
    echo "[1/4] 虚拟环境已存在"
fi

# 安装后端依赖
echo "[2/4] 安装后端依赖..."
cd backend
source venv/bin/activate
pip install -q -r requirements.txt
cd ..
echo "    后端依赖安装完成"

# 启动后端（后台）
echo "[3/4] 启动后端服务..."

# 检查端口是否被占用，如果被占用则自动终止旧进程
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "    端口 8000 已被占用，正在终止旧进程..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

cd backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "    后端 PID: $BACKEND_PID，日志: backend.log"

# 等待后端就绪
echo "    等待后端就绪..."
for i in $(seq 1 30); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q 200; then
        echo "    后端已就绪 (http://localhost:8000)"
        break
    fi
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "错误: 后端启动失败，请查看 backend.log"
        exit 1
    fi
    sleep 1
done

# 安装前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "[4/4] 安装前端依赖..."
    cd frontend
    npm install > /dev/null 2>&1
    cd ..
else
    echo "[4/4] 前端依赖已存在"
fi

# 退出时停止后端
cleanup() {
    echo ""
    echo "正在停止后端 (PID $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    echo "已退出。"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 启动前端（前台）
echo ""
echo "=========================================="
echo "    启动完成！"
echo "=========================================="
echo ""
echo "  🌐 前端地址: http://localhost:5173"
echo "  📚 后端API:  http://localhost:8000"
echo "  📖 API文档:  http://localhost:8000/docs"
echo ""
echo "  按 Ctrl+C 可同时停止前端与后端"
echo "=========================================="
echo ""

# 自动打开浏览器
sleep 2
open http://localhost:5173/login

cd frontend && npm run dev
