#!/bin/bash

# Django服务器启动脚本
# 自动进入项目目录，激活虚拟环境，启动服务器

echo "正在启动Django服务器..."

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 进入项目目录
cd "$SCRIPT_DIR"
echo "当前目录: $(pwd)"

# 检查虚拟环境是否存在
if [ -d ".venv" ]; then
    echo "激活虚拟环境..."
    source .venv/bin/activate
    echo "虚拟环境已激活"
else
    echo "警告: 未找到虚拟环境目录 .venv"
    echo "请先创建虚拟环境: python -m venv .venv"
    exit 1
fi

# 检查manage.py是否存在
if [ ! -f "manage.py" ]; then
    echo "错误: 未找到manage.py文件"
    exit 1
fi

# 启动Django开发服务器
echo "启动Django服务器 (0.0.0.0:8000)..."
python manage.py runserver 0.0.0.0:8000