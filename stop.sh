#!/bin/bash
# AI小商 - 停止服务脚本
# 用法: ./stop.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[停止] 正在停止AI小商服务...${NC}"

# 停止前端
if lsof -ti:5173 > /dev/null 2>&1; then
    kill $(lsof -ti:5173) 2>/dev/null
    echo -e "${GREEN}  ✓ 前端服务已停止${NC}"
else
    echo -e "${YELLOW}  - 前端服务未运行${NC}"
fi

# 停止后端
if lsof -ti:8000 > /dev/null 2>&1; then
    kill $(lsof -ti:8000) 2>/dev/null
    echo -e "${GREEN}  ✓ 后端服务已停止${NC}"
else
    echo -e "${YELLOW}  - 后端服务未运行${NC}"
fi

echo -e "${GREEN}所有服务已停止！${NC}"
