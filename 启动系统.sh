#!/usr/bin/env zsh
# 学生选课与成绩管理系统 - 启动脚本 (zsh)

print -P "%F{cyan}========================================%f"
print -P "%F{yellow}  学生选课与成绩管理系统%f"
print -P "%F{cyan}========================================%f"
print ""

# 获取脚本所在目录
SCRIPT_DIR="${0:a:h}"
cd "$SCRIPT_DIR" || {
  print -P "%F{red}无法进入脚本目录：$SCRIPT_DIR%f"
  exit 1
}

# 启动后端服务
print -P "%F{green}[1/2] 正在启动后端服务...%f"
BACKEND_PATH="$SCRIPT_DIR/backend"
if [[ ! -d "$BACKEND_PATH" ]]; then
  print -P "%F{red}后端目录不存在：$BACKEND_PATH%f"
  exit 1
fi

# 在新终端窗口或后台启动后端（按环境可调整）
# 这里默认后台运行并输出到日志文件
(
  cd "$BACKEND_PATH" &&
  print -P "%F{cyan}后端服务器%f" &&
  python app.py > "$SCRIPT_DIR/backend_server.log" 2>&1
) &
print -P "%F{gray}后端服务已启动: http://localhost:5000%f"
print ""

# 等待3秒
sleep 3

# 启动前端服务
print -P "%F{green}[2/2] 正在启动前端服务...%f"
FRONTEND_PATH="$SCRIPT_DIR/frontend/vue"
if [[ ! -d "$FRONTEND_PATH" ]]; then
  print -P "%F{red}前端目录不存在：$FRONTEND_PATH%f"
  exit 1
fi

(
  cd "$FRONTEND_PATH" &&
  print -P "%F{cyan}前端开发服务器%f" &&
  npm run dev > "$SCRIPT_DIR/frontend_server.log" 2>&1
) &
print -P "%F{gray}前端服务正在启动...%f"
print ""

print -P "%F{cyan}========================================%f"
print -P "%F{green}系统启动完成！%f"
print ""
print -P "%F{yellow}管理员登录:%f"
print "  账号: admin"
print "  密码: admin@123"
print ""
print -P "%F{gray}查看完整说明: 启动指南.md%f"
print -P "%F{cyan}========================================%f"
print ""

# 交互式停留（可选）：提示用户关闭或查看日志
print -n "按 Enter 键退出，或 Ctrl+C 停止服务并退出："
read -r _

# 提示后台进程信息
print -P "%F{gray}后端日志: $SCRIPT_DIR/backend_server.log%f"
print -P "%F{gray}前端日志: $SCRIPT_DIR/frontend_server.log%f"
