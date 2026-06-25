# 📖 学生选课与成绩管理系统 — 使用与部署指南

> 本文档提供从环境搭建、日常使用到生产部署的完整操作指南。

---

## 目录

1. [系统概述](#1-系统概述)
2. [架构详解](#2-架构详解)
3. [环境搭建](#3-环境搭建)
4. [日常使用指南](#4-日常使用指南)
   - [管理员](#41-管理员)
   - [教师](#42-教师)
   - [学生](#43-学生)
5. [Excel 导入导出](#5-excel-导入导出)
6. [数据库管理](#6-数据库管理)
7. [部署指南](#7-部署指南)
8. [运维管理](#8-运维管理)
9. [开发指南](#9-开发指南)
10. [故障排除](#10-故障排除)

---

## 1. 系统概述

### 1.1 功能全景

本系统是一个完整的学生选课与成绩管理平台，覆盖教务管理核心流程：

```text
┌──────────────────────────────────────────────────────┐
│                    教务管理系统                        │
├───────────────┬──────────────────┬───────────────────┤
│    学生端      │     教师端       │     管理员端       │
├───────────────┼──────────────────┼───────────────────┤
│ • 浏览可选课程  │ • 查看授课列表    │ • 学生/教师/课程CRUD │
│ • 按学期选课    │ • 成绩录入与管理  │ • 选课关系管理      │
│ • 查看已选课程  │ • 成绩权重设置    │ • 系统统计面板      │
│ • 查看成绩     │ • Excel花名册导入 │ • Excel批量导入导出  │
│ • 退课        │ • 成绩导出Excel   │ • 专业培养计划管理   │
│               │ • 成绩统计分析    │ • 管理员学期修改     │
└───────────────┴──────────────────┴───────────────────┘
```

### 1.2 核心数据流

```text
浏览器 (Vue 3)
    │  HTTP请求 (JSON / FormData)
    ▼
Flask API 层 (路由 + 认证)
    │  请求去重 (middleware)
    │  操作审计 (middleware)
    ▼
Service 层 (业务逻辑)
    │  学期校验
    │  权重计算
    │  权限验证
    ▼
Repository 层 (数据访问)
    │  SQL 查询
    ▼
MySQL 8.0 (连接池: DBUtils/PooledDB)
```

---

## 2. 架构详解

### 2.1 三层架构

项目采用 **API → Service → Repository** 分层设计，各层职责明确：

| 层级 | 位置 | 职责 | 依赖方向 |
| ------ | ------ | ------ | ---------- |
| **API** | `backend/app_core/api/` | 处理 HTTP 请求/响应，参数解析，调用 Service | → Service |
| **Service** | `backend/app_core/services/` | 业务逻辑、校验、权限控制 | → Repository |
| **Repository** | `backend/app_core/repository.py` | 数据库 CRUD 操作 | → Database |

Service 层不依赖 Flask 框架，可独立进行单元测试。

### 2.2 数据库连接池

`backend/app_core/db.py` 使用 DBUtils 的 `PooledDB`：

```text
PooledDB (max=10, mincached=1, maxcached=5)
    │
    ├── 连接1 ─── 请求A
    ├── 连接2 ─── 请求B
    ├── ...
    └── 连接N ─── 请求N
```

- 每个请求通过上下文管理器 `get_cursor()` 获取连接
- 自动提交（成功）或回滚（异常）
- 连接用完后自动归还池中

### 2.3 中间件

位于 `backend/app_core/middleware.py`，提供：

- **请求去重**：POST/PUT/DELETE 操作 5 秒内防重复提交，返回 429
- **操作审计**：记录用户操作类型、路径、方法到日志

### 2.4 日志系统

位于 `backend/app_core/logger/config.py`，双通道输出：

| 通道 | 格式 | 级别 | 用途 |
| ------ | ------ | ------ | ------ |
| 控制台 | 彩色 ANSI + Emoji | DEBUG | 开发调试 |
| `app_core/logs/app.log` | 纯文本 | INFO | 运行记录 |
| `app_core/logs/error.log` | 纯文本 | ERROR | 错误追踪 |

日志分类：HTTP 请求/响应、数据库操作、认证事件、数据校验、系统错误。

---

## 3. 环境搭建

### 3.1 前置要求

| 软件 | 最低版本 | 说明 |
| ------ | ---------- | ------ |
| Docker + Docker Compose | 20.10+ | MySQL 容器运行 |
| Python | 3.10+ | 后端运行 |
| Node.js | 18+ | 前端构建与开发 |
| npm | 9+ | 前端依赖管理 |

### 3.2 克隆项目

```bash
git clone <repository-url>
cd DB_EX3
```

### 3.3 配置环境变量

在项目根目录创建 `.env`：

```env
# MySQL 连接
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_DBNAME=student_db
MYSQL_USER=student_app
MYSQL_PASSWORD=your_secure_password_here
MYSQL_ROOT_PASSWORD=your_root_password_here

# Flask
SECRET_KEY=generate-a-random-string-here
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

> **安全提示**：生产环境务必修改 `SECRET_KEY` 和所有密码为强随机值。

### 3.4 启动 MySQL

```bash
# 启动 MySQL 容器（后台运行）
docker compose up -d

# 确认容器状态
docker compose ps

# 预期输出：
# NAME                STATUS              PORTS
# student_db_mysql    running (healthy)   0.0.0.0:3307->3306/tcp
```

### 3.5 安装并启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate    # Linux/macOS
# venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

启动成功将显示：

```text
============================================================
🚀 学生选课与成绩管理系统后端 - 启动中...
============================================================
ℹ️ Server Configuration:
   Host: 0.0.0.0
   Port: 5000
   Debug: True
   Database: 127.0.0.1:3307/student_db
────────────────────────────────────────────────────────────
✅ Application initialized successfully
```

Schema 自动初始化：首次启动时自动创建 7 张数据表、索引和约束，并创建默认管理员帐号。

### 3.6 安装并启动前端

```bash
cd frontend/vue

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 `http://localhost:5173` 进入登录页面。

### 3.7 验证安装

```bash
# 健康检查
curl http://localhost:5000/api/health

# 预期响应
# {"db": true, "status": "ok"}
```

---

## 4. 日常使用指南

### 4.1 管理员

管理员拥有系统全部权限，通常是最先登录的角色。

#### 登录

| 字段 | 值 |
| ------ | ----- |
| 账号 | `admin` |
| 密码 | `admin@123` |
| URL | `http://localhost:5173` |

#### 操作面板

登录后进入管理员面板，包含以下功能区域：

**① 统计面板（顶部）**
- 学生总数 / 教师总数 / 课程总数 / 选课记录数 / 选课率
- 后端连接状态指示器

**② 学生管理**
- **新增**：填写学号、姓名、专业 → 点击"添加学生"
- **查看**：折叠列表展示所有学生，支持按学号/姓名/专业搜索
- **修改学期**：在下拉框中选择学期（1-8）→ 点击"保存"
- **删除**：点击学生行右侧"删除"按钮

**③ 教师管理**
- **新增**：填写工号、姓名、院系 → 点击"添加教师"
- **查看/搜索/删除**：与学生管理类似

**④ 课程管理**
- **新增**：填写课程编号、名称、学分、容量，可选关联教师
- **查看/编辑/删除**：管理所有课程信息

**⑤ 选课管理**
- **新增**：选择学生和课程 → 创建选课关系
- **成绩录入**：设置平时成绩（0-100）、期末成绩（0-100），系统自动按权重计算最终成绩
- **删除**：移除选课记录

**⑥ 成绩权重设置**
- 选择课程 → 设置平时成绩权重和期末成绩权重（两项之和必须为 1.0）
- 保存后自动重算该课程所有学生的最终成绩

**⑦ 专业培养计划**
- **创建计划**：输入专业名称（如"计算机科学"）→ 创建培养计划
- **添加课程**：选择计划 → 选择学期（1-12）→ 选择课程 → 设置必修/选修
- **查看/删除**：管理计划中的课程编排

**⑧ Excel 批量导入**
- 上传包含 courses / students / enrollments 工作表的 Excel 文件
- 系统自动创建或跳过已存在的记录

**⑨ 成绩导出**
- 选择课程 → 下载 Excel 格式的成绩单（含课程信息、学生名单、成绩统计）

#### 权限说明

管理员可以执行任何操作，包括：
- 修改任意学生的学期
- 为任意选课记录录入成绩
- 管理所有专业培养计划
- 批量导入/导出数据

### 4.2 教师

#### 登录

| 字段 | 值 |
| ------ | ----- |
| 账号 | 工号（如 `T001`） |
| 密码 | `t` + 工号（如 `tT001`） |
| 创建方式 | 管理员在后台创建教师后自动生成账号 |

#### 操作面板

**① 我的课程**
- 查看所有由当前教师授课的课程及其选课人数

**② 成绩管理**
- 点击课程进入学生名单
- 为每位学生设置：
  - **平时成绩**（0-100）：如出勤、作业、实验等
  - **期末成绩**（0-100）：期末考试或大作业
  - 系统自动按课程权重计算 `final_grade`
- 支持逐个保存或批量录入

**③ 成绩权重**
- 设置课程的成绩权重（平时成绩占比 + 期末成绩占比 = 1.0）
- 修改后立即重算所有学生的最终成绩
- 默认值：平时 0.5 / 期末 0.5

**④ Excel 花名册导入**
- 上传包含 `course` 和 `students` 两个工作表的 Excel
- `course` 工作表（一行）：course_code, name, credit, capacity
- `students` 工作表：student_no, name, major, current_semester
- 系统自动：创建课程（如不存在）→ 创建学生（如不存在）→ 创建选课关系
- 可下载模板文件参考格式

**⑤ 成绩导出**
- 选择课程 → 下载 Excel 格式成绩单
- 包含：课程信息、教师信息、平均分、及格率、优秀率、学生详细成绩

**⑥ 成绩统计**
- 按课程查看：选课人数、平均分、及格率、优秀率

### 4.3 学生

#### 登录

| 字段 | 值 |
| ------ | ----- |
| 账号 | 学号（如 `S001`） |
| 密码 | `s` + 学号（如 `sS001`） |
| 创建方式 | 管理员创建学生后自动生成账号 |

#### 操作面板

**① 可选课程**
- 显示当前学期可用课程列表
- 课程按学生所属专业的培养计划自动过滤
- 每门课程显示：课程编号、名称、学分、已选人数/容量、授课教师
- 支持按学期筛选

**② 我的选课**
- 已选课程列表，显示课程信息和成绩
- 每门课程显示：最终成绩、平时成绩、期末成绩、状态
- 支持退课操作

**③ 选课规则**
- 学生只能选择**当前学期**匹配的课程（由培养计划定义）
- 学生只能选择**本专业**培养计划内的课程
- 同一课程不可重复选择
- 选课无需审核，即时生效

---

## 5. Excel 导入导出

### 5.1 管理员批量导入

#### 文件格式

Excel 工作簿（`.xlsx`），需包含以下工作表：

**courses（课程信息）**

| 列名 | 必填 | 说明 |
| ------ | :--: | ------ |
| course_code | ✅ | 课程编号，唯一标识 |
| name | ✅ | 课程名称 |
| credit | | 学分，默认 0 |
| capacity | | 容量，默认 50 |
| semester | | 开设学期 |
| teacher_no | | 教师工号（自动关联已有教师或创建新教师） |
| teacher_name | | 教师姓名（新建教师时使用） |
| teacher_department | | 教师院系（新建教师时使用） |

**students（学生信息）**

| 列名 | 必填 | 说明 |
| ------ | :--: | ------ |
| student_no | ✅ | 学号，唯一标识 |
| name | | 姓名，默认使用学号 |
| major | | 专业 |
| current_semester | | 当前学期，默认 1 |

**enrollments（选课关系）**

| 列名 | 必填 | 说明 |
| ------ | :--: | ------ |
| course_code | ✅ | 课程编号 |
| student_no | ✅ | 学号 |
| grade | | 成绩（0-100） |
| status | | 状态：enrolled / dropped / completed |

#### 操作步骤

1. 管理员登录后，在面板中找到"导入"区域
2. 选择 `.xlsx` 文件
3. 点击上传
4. 查看导入汇总（创建数 / 跳过数 / 错误信息）

### 5.2 教师花名册导入

#### 文件格式

**course（课程信息，仅一行）**

| 列名 | 必填 | 说明 |
| ------ | :--: | ------ |
| course_code | ✅ | 课程编号 |
| name | ✅ | 课程名称 |
| credit | | 学分，默认 0 |
| capacity | | 容量，默认 50 |

**students（学生名单）**

| 列名 | 必填 | 说明 |
| ------ | :--: | ------ |
| student_no | ✅ | 学号 |
| name | | 姓名 |
| major | | 专业 |
| current_semester | | 当前学期 |

#### 操作步骤

1. 教师登录后，点击"导入花名册"
2. 可先下载模板 Excel
3. 按模板填写后上传
4. 系统自动：创建/更新课程 → 创建学生 → 建立选课关系

### 5.3 生成示例文件

```bash
cd backend

# 生成管理员导入示例
python -c "from app_core.scripts.generate_sample_excel import main; main()"

# 生成教师花名册示例
python -c "from app_core.scripts.generate_teacher_roster import main; main()"
```

### 5.4 成绩导出

管理员和教师均可导出课程成绩 Excel，包含两个工作表：

| 工作表 | 内容 |
| -------- | ------ |
| 课程信息 | 课程编号、名称、学分、教师、选课人数、平均分、及格率、优秀率 |
| 成绩名单 | 学号、姓名、专业、最终成绩、选课状态 |

---

## 6. 数据库管理

### 6.1 数据表结构

系统使用 7 张数据表：

```text
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   students   │     │   teachers   │     │    courses    │
├─────────────┤     ├─────────────┤     ├──────────────┤
│ id (PK)     │     │ id (PK)     │     │ id (PK)      │
│ student_no  │     │ teacher_no  │     │ course_code  │
│ name        │     │ name        │     │ name         │
│ major       │     │ department  │     │ credit       │
│ cur_semester│     └──────┬──────┘     │ capacity     │
│ sem_updated │            │            │ teacher_id(FK)│
└──────┬──────┘            │            │ ord_weight   │
       │                   │            │ final_weight │
       │    ┌──────────────┴─────┐      │ pass_rate    │
       │    │    enrollments     │      │ excel_rate   │
       │    ├───────────────────┤      └──────┬───────┘
       └───→│ id (PK)           │←────────────┘
            │ student_id (FK)   │
            │ course_id (FK)    │
            │ status            │
            │ grade             │
            │ ordinary_score    │
            │ final_score       │
            │ final_grade       │
            └───────────────────┘

┌─────────────┐     ┌─────────────────────┐
│    users     │     │    major_plans       │
├─────────────┤     ├─────────────────────┤
│ id (PK)     │     │ id (PK)             │
│ username    │     │ major_name (UNIQUE) │
│ password    │     │ description         │
│ role        │     └──────────┬──────────┘
│ ref_id      │                │
└─────────────┘     ┌──────────┴──────────┐
                    │  major_plan_courses  │
                    ├─────────────────────┤
                    │ id (PK)             │
                    │ plan_id (FK)        │
                    │ course_id (FK)      │
                    │ semester (1-12)     │
                    │ is_required         │
                    └─────────────────────┘
```

### 6.2 连接 MySQL

```bash
# 通过 Docker 容器连接
docker exec -it student_db_mysql mysql -u student_app -p student_db

# 或通过宿主机连接（端口映射为 3307）
mysql -h 127.0.0.1 -P 3307 -u student_app -p student_db
```

### 6.3 常用查询

```sql
-- 查看所有表
SHOW TABLES;

-- 查看学生选课情况
SELECT s.name, s.student_no, c.name AS course_name, e.status, e.final_grade
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id
ORDER BY s.student_no;

-- 查看某课程成绩分布
SELECT
    CASE
        WHEN COALESCE(e.final_grade, e.grade) >= 90 THEN '优秀(90+)'
        WHEN COALESCE(e.final_grade, e.grade) >= 80 THEN '良好(80-89)'
        WHEN COALESCE(e.final_grade, e.grade) >= 70 THEN '中等(70-79)'
        WHEN COALESCE(e.final_grade, e.grade) >= 60 THEN '及格(60-69)'
        ELSE '不及格(<60)'
    END AS grade_range,
    COUNT(*) AS count
FROM enrollments e
WHERE e.course_id = 1
GROUP BY grade_range
ORDER BY MIN(COALESCE(e.final_grade, e.grade)) DESC;

-- 查看专业培养计划
SELECT mp.major_name, mpc.semester, c.name, c.credit,
       CASE WHEN mpc.is_required THEN '必修' ELSE '选修' END AS type
FROM major_plans mp
JOIN major_plan_courses mpc ON mp.id = mpc.plan_id
JOIN courses c ON mpc.course_id = c.id
ORDER BY mp.major_name, mpc.semester;
```

### 6.4 备份与恢复

```bash
# 备份
docker exec student_db_mysql mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" student_db > backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i student_db_mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" student_db < backup_20250101.sql
```

---

## 7. 部署指南

### 7.1 Docker Compose（开发/测试）

项目已包含完整 Docker Compose 配置：

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f mysql

# 停止服务
docker compose down
```

数据持久化：MySQL 数据存储在 Docker Volume `mysql_data` 中，`docker compose down` 不会丢失数据。如需彻底清除：

```bash
docker compose down -v
```

### 7.2 Gunicorn 生产部署（Linux）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动（4 worker 进程）
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用 systemd 管理（推荐）
```

创建 systemd 服务文件 `/etc/systemd/system/student-system.service`：

```ini
[Unit]
Description=Student Course Selection System
After=network.target docker.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/DB_EX3/backend
Environment=PATH=/opt/DB_EX3/backend/venv/bin
ExecStart=/opt/DB_EX3/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now student-system
sudo systemctl status student-system
```

### 7.3 Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /opt/DB_EX3/frontend/vue/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反代到后端
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7.4 前端生产构建

```bash
cd frontend/vue
npm run build

# 将 dist/ 目录部署到 Nginx 或 CDN
# 构建产物在 frontend/vue/dist/
```

### 7.5 环境变量（生产环境）

生产环境 `.env` 建议配置：

```env
# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DBNAME=student_db
MYSQL_USER=student_app
MYSQL_PASSWORD=<strong-random-password>
MYSQL_ROOT_PASSWORD=<strong-random-password>

# Flask
SECRET_KEY=<random-64-char-string>
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

---

## 8. 运维管理

### 8.1 自动学期推进

系统包含学期自动推进脚本，可在 cron 中定时执行：

```bash
# 手动执行一次
cd /opt/DB_EX3
python backend/app_core/scripts/advance_semester.py

# 输出：
# [2025-12-15 03:00:01] advanced semesters for 42 students
```

#### 配置 cron（Linux）

```bash
# 每天凌晨 3 点执行
crontab -e
```cron
0 3 * * * cd /opt/DB_EX3 && /opt/DB_EX3/backend/venv/bin/python backend/app_core/scripts/advance_semester.py >> /var/log/semester_advance.log 2>&1
```

#### 工作原理

1. 检查每个学生的 `semester_updated_at` 字段
2. 如距今超过 6 个月（可配置），且 `current_semester < 8`（最大学期）
3. 自动将 `current_semester` +1
4. 更新 `semester_updated_at` 为当前时间

#### 配置参数

通过环境变量调整（在 `.env` 中设置）：

```env
# 自定义配置
SEMESTER_INTERVAL_MONTHS=6   # 间隔月份，默认 6
MAX_SEMESTER=8               # 最大学期，默认 8
```

### 8.2 日志文件管理

```bash
# 查看实时日志
tail -f backend/app_core/logs/app.log

# 查看错误日志
tail -f backend/app_core/logs/error.log

# 日志轮转（建议配置 logrotate）
# /etc/logrotate.d/student-system
/opt/DB_EX3/backend/app_core/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### 8.3 密码管理

```bash
# 通过 API 修改密码
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Content-Type: application/json" \
  -c cookies.txt -b cookies.txt \
  -d '{"old_password": "old", "new_password": "new"}'

# 登录获取 session
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username": "admin", "password": "admin@123"}'
```

### 8.4 数据库迁移

当项目升级后需要执行 Schema 变更：

```bash
# 查看迁移脚本
ls backend/app_core/seeds/

# 执行迁移（MySQL）
docker exec -i student_db_mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" student_db \
  < backend/app_core/seeds/add_semester_to_students.sql
```

> 注意：系统启动时会自动检测并添加缺失的列和约束（通过 `init_schema()` 中的条件迁移逻辑）。大多数情况下无需手动执行迁移。

---

## 9. 开发指南

### 9.1 项目启动（开发模式）

```bash
# 终端 1：MySQL
docker compose up -d

# 终端 2：后端（热重载需手动重启）
cd backend
source venv/bin/activate
python main.py

# 终端 3：前端（热重载）
cd frontend/vue
npm run dev
```

### 9.2 添加新的 API 端点

1. **Service 层**：在 `backend/app_core/services/` 中添加业务方法
2. **API 层**：在 `backend/app_core/api/` 中注册路由
3. **装饰器**：使用 `@api_endpoint` 或 `@handle_service_result` 标准化响应
4. **前端 API**：在 `frontend/vue/src/api/services.js` 中添加调用方法
5. **前端组件**：在 `frontend/vue/src/components/` 中添加 UI

### 9.3 运行测试

```bash
cd backend

# 运行所有测试
python -m unittest discover app_core/tests/

# 运行单个测试文件
python -m unittest app_core/tests/test_decoupling.py

# 运行单个测试方法
python -m unittest app_core/tests.test_decoupling.TestStudentRepository.test_create_student
```

### 9.4 代码结构约定

```text
backend/app_core/
├── api/           # Flask Blueprint 路由（每个角色一个文件）
├── services/      # 业务逻辑（每个角色一个 Service 类）
├── repository.py  # 数据访问抽象
├── db.py          # 数据库连接池与 Schema
├── config.py      # 应用配置
├── middleware.py   # 请求去重与审计
├── decorators.py  # API 端点装饰器
├── utils/         # 工具函数
├── logger/        # 日志系统
├── seeds/         # SQL 迁移脚本
├── scripts/       # 独立脚本
└── tests/         # 单元测试
```

### 9.5 关键约定

- **错误处理**：Service 层返回 `(data, error_message)` 元组或抛出 `ValueError`
- **密码哈希**：使用 SHA-256（`utils/helpers.py` 中的 `hash_password`）
- **Session 管理**：使用 Flask-Session，存储在文件系统
- **CORS**：默认允许 `localhost:5173` 和 `localhost:5174`
- **数据库字符集**：`utf8mb4` + `utf8mb4_unicode_ci` 排序规则

---

## 10. 故障排除

### 10.1 后端无法启动

| 现象 | 可能原因 | 解决方案 |
| ------ | ---------- | ---------- |
| `ModuleNotFoundError: flask` | 虚拟环境未激活 | `source venv/bin/activate && pip install -r requirements.txt` |
| `MYSQL_USER and MYSQL_PASSWORD not set` | `.env` 不存在或路径错误 | 确认 `.env` 在项目根目录 |
| `Can't connect to MySQL` | MySQL 容器未启动 | `docker compose up -d && docker compose ps` |
| 端口 5000 被占用 | 其他进程占用 | `lsof -i :5000` 查看占用，或修改 `FLASK_PORT` |
| 表不存在报错 | Schema 未初始化 | 重启后端触发 `init_schema()` |

### 10.2 前端无法连接后端

| 现象 | 可能原因 | 解决方案 |
| ------ | ---------- | ---------- |
| CORS 错误 | 前端 URL 不在 CORS 白名单 | 检查 `config.py` 中 `CORS_ORIGINS` 配置 |
| 网络错误 | 后端未启动或地址错误 | 检查 `VITE_API_BASE` 环境变量 |
| 401 未授权 | Session 过期或未登录 | 重新登录 |

### 10.3 数据库问题

| 现象 | 可能原因 | 解决方案 |
| ------ | ---------- | ---------- |
| 连接被拒绝 | MySQL 未就绪 | 等待健康检查通过：`docker compose ps` |
| 认证失败 | 密码错误 | 检查 `.env` 中密码是否与容器初始化一致 |
| 外键约束失败 | 数据依赖不完整 | 先创建关联记录（如先创建教师再创建课程） |
| 学期修改无效 | 超出范围 1-8 | 后端会静默忽略无效学期值 |

### 10.4 Excel 导入问题

| 现象 | 可能原因 | 解决方案 |
| ------ | ---------- | ---------- |
| "无法读取Excel文件" | 文件格式错误 | 确保为 `.xlsx` 格式 |
| "需包含 courses 工作表" | 工作表名称错误 | 检查工作表命名（区分大小写） |
| "course_code 与 name 为必填" | 必填列为空 | 补充必填字段 |
| 记录被跳过 | 数据已存在或格式错误 | 查看导入汇总中的 `errors` 列表 |

### 10.5 登录问题

| 现象 | 可能原因 | 解决方案 |
| ------ | ---------- | ---------- |
| 管理员不存在 | 初始化未执行 | 重启后端，确认日志输出 `✅ Application initialized` |
| 学生/教师无账号 | 创建时间早于系统上线 | 重启后端，`initialize_default_accounts` 会补充创建 |
| 密码错误 | 使用了错误的密码规则 | 学生：`s`+学号，教师：`t`+工号 |

### 10.6 日志位置

```bash
# 后端日志
backend/app_core/logs/app.log      # 全部 INFO+ 日志
backend/app_core/logs/error.log    # ERROR 级别日志

# Docker 日志
docker compose logs mysql

# 前端日志（浏览器开发者工具）
# F12 → Console / Network 面板
```
