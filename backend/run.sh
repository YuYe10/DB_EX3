#!/bin/bash
# 启动脚本：带有彩色日志的后端服务器

cd "$(dirname "$0")"

echo -e "\033[1;32m========================================\033[0m"
echo -e "\033[1;32m🚀 学生选课与成绩管理系统 - 后端启动\033[0m"
echo -e "\033[1;32m========================================\033[0m\n"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m❌ 错误: 未找到Python3\033[0m"
    exit 1
fi

echo -e "\033[0;36mℹ️  Python版本:\033[0m"
python3 --version

echo -e "\033[0;36mℹ️  启动目录:\033[0m"
pwd

# 检查依赖
echo -e "\n\033[0;36m📦 检查依赖...\033[0m"
if ! python3 -c "import flask" &> /dev/null; then
    echo -e "\033[0;33m⚠️  Flask未安装，正在安装...\033[0m"
    pip install -q flask flask-cors flask-session python-dotenv psycopg2-binary pandas openpyxl bcrypt
fi

echo -e "\033[0;36m✅ 依赖检查完成\033[0m\n"

# 启动应用
echo -e "\033[0;36m🔧 启动应用服务器...\033[0m\n"
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

python3 -m flask run --host 0.0.0.0 --port 5000
