# 🎓 学生选课与成绩管理系统

一个功能完整的学生选课与成绩管理系统，支持学生/教师/管理员三角色，包含课程浏览与选课、成绩管理、专业培养计划、Excel 批量导入导出、日志审计与可测试的服务层架构。

**亮点**
- 三角色权限、会话认证与跨域支持
- 学期限制选课：学生仅能选择“当前学期”的课程
- 成绩管理：平时/期末成绩与权重占比，自动计算最终成绩
- 专业培养计划：按专业与学期组织课程体系
- 批量导入导出：支持多种 Excel 模板
- 自动学期推进：每过半年自动将学生学期 +1（可配置），管理员可查看/修改

---

## 🧱 技术架构
- 后端：Flask、psycopg2、Flask-Session、Flask-CORS
- 数据库：PostgreSQL 或 openGauss（支持 SSH 隧道）
- 前端：Vue 3（Vite）
- 架构：API → Service → Repository（松耦合、可测试）
- 日志：彩色分级日志与操作审计（后端）

---

## 📁 项目结构（简要）

```
backend/
  app.py                 # Flask 应用入口（工厂模式，导出 app）
  app_core/
    config.py            # 配置（读取 .env、CORS、Session 等）
    db.py                # 数据库连接与 schema 初始化（含条件迁移 DO 块）
    api/                 # 路由：auth / student / teacher / admin
    services/            # 业务服务层（含学期验证与管理员更新）
    seeds/               # SQL 种子与迁移（semester 字段等）
    scripts/             # 实用脚本（示例 Excel、教师名册、自动学期推进）

frontend/vue/
  src/
    components/          # Login / AdminView / StudentView / TeacherView
    api/                 # client.js 与 services.js
    composables/         # 复用逻辑
```

---

## 🚀 快速开始（Windows / Linux / macOS）

### 1) 数据库与环境变量
在仓库根目录创建 .env（被后端自动加载），示例：

```env
# PostgreSQL / openGauss 连接
OG_HOST=127.0.0.1
OG_PORT=5432             # openGauss 常为 26000；按实际调整
OG_DBNAME=student_db
OG_USER=appuser
OG_PASSWORD=your_password

# 可选：SSH 隧道（如需）
OG_SSH_TUNNEL=false
OG_SSH_HOST=your_ssh_host
OG_SSH_PORT=22
OG_SSH_USER=your_ssh_user
OG_SSH_PASSWORD=your_ssh_password
OG_SSH_PKEY=path/to/id_rsa
```

### 2) 后端启动

```powershell
# Windows PowerShell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt

# 初始化 schema（可选；启动时也会触发）
python -c "from app_core.db import db; db.init_schema()"

# 启动后端（默认 http://localhost:5000）
python app.py
```

```bash
# Linux/macOS
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from app_core.db import db; db.init_schema()"
python app.py
```

### 3) 学期字段迁移（已有数据的数据库建议执行）
若运行时报错“students.current_semester/semester_updated_at 不存在”，请直接在数据库执行以下 SQL 或使用种子文件：

```sql
-- 为 students 添加学期字段（如缺失）
ALTER TABLE students ADD COLUMN IF NOT EXISTS current_semester INT DEFAULT 1;
ALTER TABLE students ADD COLUMN IF NOT EXISTS semester_updated_at TIMESTAMP DEFAULT NOW();
UPDATE students SET current_semester = COALESCE(current_semester, 1);
UPDATE students SET semester_updated_at = COALESCE(semester_updated_at, NOW());
```

也可使用种子文件：
- [backend/app_core/seeds/add_semester_to_students.sql](backend/app_core/seeds/add_semester_to_students.sql)
- [backend/app_core/seeds/add_semester_timestamp.sql](backend/app_core/seeds/add_semester_timestamp.sql)

PostgreSQL 示例：

```bash
psql -h $OG_HOST -p $OG_PORT -U $OG_USER -d $OG_DBNAME -f backend/app_core/seeds/add_semester_to_students.sql
psql -h $OG_HOST -p $OG_PORT -U $OG_USER -d $OG_DBNAME -f backend/app_core/seeds/add_semester_timestamp.sql
```

openGauss 环境可使用 `gsql`，或直接在客户端执行上述 SQL。

### 4) 前端启动

```bash
cd frontend/vue
npm install
npm run dev    # 默认 http://localhost:5173
```

如后端不在同机，在仓库根目录创建 .env.development：

```env
VITE_API_BASE=http://<后端IP或域名>:5000/api
```

### 5) 一键启动脚本
- Linux/macOS：运行 [启动系统.sh](启动系统.sh)
- Windows：运行 [启动系统.ps1](启动系统.ps1)

---

## 📅 自动学期推进（半年 +1）

脚本： [backend/app_core/scripts/advance_semester.py](backend/app_core/scripts/advance_semester.py)

功能：当 `semester_updated_at` 距今超过设定月份（默认 6），且 `current_semester < 最大学期（默认 8）`，则将该学生的 `current_semester` +1，并刷新 `semester_updated_at`。

Windows 任务计划程序示例（每日运行一次）：

```powershell
# 以系统计划任务执行（示意命令）
PowerShell -File "I:\Codes\DB\EX3\backend\venv\Scripts\Activate.ps1"; \
  python "I:\Codes\DB\EX3\backend\app_core\scripts\advance_semester.py" --months 6 --max-semester 8
```

管理员界面支持查看与手动修改学期（后端验证范围 1–8 并更新时间戳）。

---

## 📦 Excel 批量导入规范（摘要）

管理员导入：

| 工作表 | 必需列 | 可选列 | 说明 |
|--------|--------|--------|------|
| courses | course_code, name, credit, capacity, semester | teacher_no, teacher_name, teacher_department | 课程基础信息与学期归属 |
| students | student_no, name, major | current_semester | 学生基础信息与当前学期 |
| enrollments | course_code, student_no | grade, status | 选课关系与成绩状态 |

教师导入：

| 工作表 | 必需列 | 说明 |
|--------|--------|------|
| course | course_code, name, credit, capacity, semester | 课程信息（仅一行） |
| students | student_no, name, major, current_semester | 学生名单 |

详细模板与示例请见 docs 目录或管理员/教师界面内的模板下载。

---

## 🔐 默认账号与角色

| 角色 | 用户名 | 密码 | 说明 |
|-----|--------|------|------|
| 管理员 | admin | admin@123 | 初始管理员，后端启动时自动创建 |
| 学生 | 学号 | s+学号 | 例如：S001 → sS001（管理员创建学生时自动生成账号） |
| 教师 | 工号 | t+工号 | 例如：T001 → tT001（管理员创建教师时自动生成账号） |

---

## 📚 API 概览（摘要）

- 认证：`POST /api/auth/login`、`POST /api/auth/logout`、`POST /api/auth/change-password`
- 学生：`GET /api/student/courses`、`GET /api/student/enrollments`、`POST /api/enrollments`、`DELETE /api/student/enrollments/{id}`
- 教师：`GET /api/teacher/courses`、`GET /api/teacher/courses/{id}/students`、`PUT /api/teacher/enrollments/{id}/grade`
- 管理员：`GET/POST/PUT/DELETE /api/students | /api/teachers | /api/courses`、选课与统计接口

详细 API 请查看后端源码与 docs 文档。

---

## 🛠️ 部署（简要）

Gunicorn + Nginx（Linux）：

```bash
pip install gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Docker（后端示例 Dockerfile）：

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

## ❓ 常见问题
- 认证失败/SASL：检查数据库加密与 `pg_hba.conf`；重置 `appuser` 密码
- 权限拒绝：确认已授予表/模式权限
- SSH 隧道失败：检查 `AllowTcpForwarding` 等 sshd_config 配置
- 前端 404：确认 `VITE_API_BASE` 指向后端 API 根路径
- 500 报错（缺列）：执行上文“学期字段迁移” SQL 后重启后端

---

## 📑 测试

```bash
cd backend
python -m pytest tests/
```

---

## 📄 许可证
MIT License

---

## 📝 更新日志（摘录）

v2.0.0（2025-12-15）
- 完成后端数据验证层与操作审计
- 登录界面 UX 升级与删除确认对话框
- 学生课程发现与管理员仪表盘增强
- 选课与成绩的端到端流程优化
- 完整文档与部署指南
