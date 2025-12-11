# 学生选课与成绩管理系统（Flask + Vue + openGauss）

## 环境准备

- Python 3.10+
- Node.js 18+
- openGauss 数据库（本项目示例：服务器内网 192.168.0.61:26000，经 SSH 公网 1.92.114.171:22 访问）

## 1) 配置后端

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r ..\requirements.txt

copy ..\.env.example ..\.env   # 根据实际修改
#
```

`.env` 关键项（直连或 SSH 隧道二选一）：

```bash
# 直连示例
OG_SSH_TUNNEL=false
OG_HOST=192.168.0.61
OG_PORT=26000
OG_DBNAME=student_db
OG_USER=appuser
OG_PASSWORD=your_db_password

# 如需 SSH 隧道
OG_SSH_TUNNEL=true
OG_SSH_HOST=1.92.114.171
OG_SSH_PORT=22
OG_SSH_USER=your_ssh_user
OG_SSH_PASSWORD=your_ssh_password
OG_HOST=192.168.0.61   # 隧道目标 DB 地址
OG_PORT=26000
```

## 2) 数据库权限（需在服务器 gsql 用管理员执行）

```sql
GRANT CONNECT ON DATABASE student_db TO appuser;
GRANT USAGE, CREATE ON SCHEMA public TO appuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO appuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO appuser;
```
（后端启动会自动建表：students/teachers/courses/enrollments）

## 3) 运行后端

```bash
cd backend
.\.venv\Scripts\activate
python app.py
```
默认监听 `http://0.0.0.0:5000`。

## 4) 前端

已用 Vite 初始化在 `frontend/vue`。

```bash
cd frontend/vue
npm install
npm run dev
```
如后端不在同机，可在根目录创建 `.env.development` 设置：

```bash
VITE_API_BASE=http://<后端IP或域名>:5000/api
```

## 5) 身份验证与角色系统

系统已实现基于会话的身份验证，包含三种角色：

### 默认登录账号

| 角色 | 用户名 | 密码 | 说明 |
|-----|--------|------|------|
| 管理员 | `admin` | `admin@123` | 完整权限，可管理所有数据 |
| 学生 | `学号` | `s+学号` | 如 S001 的密码为 sS001 |
| 教师 | `工号` | `t+工号` | 如 T001 的密码为 tT001 |

**注意**：学生和教师账号在管理员创建对应记录时自动生成。

### 角色功能

- **学生界面**：浏览可选课程、选课、退课、查看成绩、修改密码
- **教师界面**：查看所教课程、查看选课学生名单、录入/修改学生成绩、修改密码
- **管理员界面**：完整的CRUD功能（学生、教师、课程、选课记录管理）、统计数据查看

## 6) 主要接口

### 认证接口

- `POST /api/auth/login` - 登录（返回用户信息及会话）
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/change-password` - 修改密码

### 学生接口（需学生角色）

- `GET /api/student/courses/available` - 获取可选课程列表
- `GET /api/student/enrollments` - 获取我的选课记录
- `POST /api/student/enrollments` - 选课
- `DELETE /api/student/enrollments/{id}` - 退课

### 教师接口（需教师角色）

- `GET /api/teacher/courses` - 获取我教授的课程
- `GET /api/teacher/courses/{id}/students` - 获取某课程的学生名单
- `PUT /api/teacher/enrollments/{id}/grade` - 修改学生成绩

### 管理员接口（需管理员角色）

- `GET/POST/PUT/DELETE /api/students` - 学生管理
- `GET/POST/PUT/DELETE /api/teachers` - 教师管理
- `GET/POST/PUT/DELETE /api/courses` - 课程管理
- `GET/POST /api/enrollments`，`PUT /api/enrollments/{id}/grade`，`DELETE /api/enrollments/{id}` - 选课管理
- `GET /api/statistics/overview` - 统计数据

### 公共接口

- `GET /api/health` - 健康检查

## 7) 常见问题

- **认证失败/SASL**：确保 `password_encryption_type=0` 且 `pg_hba.conf` 使用 `md5`；用管理员重置 `appuser` 密码。
- **权限拒绝**：确认已执行 schema/table 授权命令。
- **SSH 隧道被拒**：确认 `sshd_config` 中 `AllowTcpForwarding yes`、`GatewayPorts yes`、`PermitOpen any` 并已 `systemctl restart sshd`。
- **前端 404**：确认 `VITE_API_BASE` 指向后端 API 根路径。
- **登录失败**：确保后端已启动并初始化数据库（会自动创建 admin 账号）。
- **学生/教师无法登录**：管理员需要先创建对应的学生/教师记录，系统会自动生成登录账号。

## 8) 快速启动

双击根目录的 `启动系统.bat`（Windows）即可自动启动后端和前端服务。

或手动启动：

```bash
# 终端1 - 后端
cd backend
python app.py

# 终端2 - 前端
cd frontend/vue
npm run dev
```

更多详情请参考 [启动指南.md](启动指南.md)。
