# 学生选课与成绩管理系统 - 启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  学生选课与成绩管理系统" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 启动后端服务
Write-Host "[1/2] 正在启动后端服务..." -ForegroundColor Green
$backendPath = Join-Path $scriptPath "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '后端服务器' -ForegroundColor Cyan; python app.py"
Write-Host "后端服务已启动: http://localhost:5000" -ForegroundColor Gray
Write-Host ""

# 等待3秒
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "[2/2] 正在启动前端服务..." -ForegroundColor Green
$frontendPath = Join-Path $scriptPath "frontend\vue"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host '前端开发服务器' -ForegroundColor Cyan; npm run dev"
Write-Host "前端服务正在启动..." -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "系统启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "管理员登录:" -ForegroundColor Yellow
Write-Host "  账号: admin" -ForegroundColor White
Write-Host "  密码: admin@123" -ForegroundColor White
Write-Host ""
Write-Host "查看完整说明: 启动指南.md" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "按 Enter 键关闭此窗口"
