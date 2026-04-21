#!/bin/bash
# AI小商 - 重启服务脚本
# 用法: ./restart.sh

echo "正在重启服务..."
./stop.sh
sleep 2
./start.sh
