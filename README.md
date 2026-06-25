# 🎓 学生选课与成绩管理系统

一个功能完整的学生选课与成绩管理系统，支持学生/教师/管理员三角色，包含课程浏览与选课、成绩管理、专业培养计划、Excel 批量导入导出、日志审计与可测试的三层服务架构。

## ✨ 亮点

- 三角色权限体系（学生/教师/管理员），Session 会话认证与 CORS 跨域支持
- 学期限制选课：学生仅能选择当前学期且匹配专业培养计划的课程
- 成绩权重管理：平时成绩与期末成绩按权重自动计算最终成绩，支持按课程自定义权重
- 专业培养计划：按专业与学期组织课程体系，区分必修/选修
- Excel 批量导入导出：管理员多工作表导入，教师花名册导入，成绩导出
- 自动学期推进：每过半年自动将学生学期 +1（可配置），管理员可查看/手动修改
- 请求去重与操作审计：防止重复提交，记录关键操作日志
- 彩色分级日志系统：控制台彩色输出 + 文件持久化，按模块分类

---

## 🧱 技术架构

| 层级 | 技术栈 |
| ------ | -------- |
| 后端框架 | Flask 3.0、Flask-CORS、Flask-Session |
| 数据库 | MySQL 8.0（Docker 部署） |
| 数据库驱动 | PyMySQL + DBUtils（连接池） |
| 前端 | Vue 3（Composition API、`<script setup>`）+ Vite |
| 数据处理 | Pandas、openpyxl |
| 架构模式 | API → Service → Repository（三层解耦、可测试） |
| 日志 | 自定义彩色分级日志（控制台 + 文件） |

---

## 📁 项目结构

```text
DB_EX3/
├── backend/                          # Flask 后端
│   ├── app.py                        # Flask 应用工厂（create_app）
│   ├── main.py                       # 入口（含启动横幅）
│   ├── run.sh                        # 后端启动脚本
│   ├── requirements.txt              # Python 依赖
│   └── app_core/                     # 核心应用包
│       ├── config.py                 # 配置（读取 .env、CORS、Session）
│       ├── db.py                     # 数据库连接池与 Schema 初始化
│       ├── repository.py             # Repository 层（数据访问抽象）
│       ├── middleware.py             # 请求去重与操作审计
│       ├── decorators.py             # API 端点装饰器
│       ├── api/                      # 路由层（Flask Blueprint）
│       │   ├── auth.py               # 认证接口
│       │   ├── student.py            # 学生接口
│       │   ├── teacher.py            # 教师接口
│       │   └── admin.py              # 管理员接口
│       ├── services/                 # 业务服务层
│       │   ├── user_service.py       # 用户认证与密码管理
│       │   ├── student_service.py    # 选课业务（含学期校验）
│       │   ├── teacher_service.py    # 成绩管理与花名册导入
│       │   ├── admin_service.py      # CRUD、统计、Excel 导入导出
│       │   └── major_plan_service.py # 专业培养计划管理
│       ├── utils/                    # 工具函数
│       │   ├── helpers.py            # 密码哈希、JSON 响应、认证装饰器
│       │   └── validators.py         # 数据校验
│       ├── logger/                   # 日志系统
│       │   └── config.py             # 彩色格式化器与日志配置
│       ├── seeds/                    # SQL 迁移脚本
│       │   ├── add_semester_to_students.sql
│       │   ├── add_semester_timestamp.sql
│       │   ├── major_plans_seed.sql
│       │   └── fix_major_plans_table.sql
│       ├── scripts/                  # 实用脚本
│       │   ├── advance_semester.py   # 自动学期推进
│       │   ├── generate_sample_excel.py
│       │   └── generate_teacher_roster.py
│       └── tests/                    # 单元测试
│           ├── test_decoupling.py    # Repository/Service 解耦测试
│           ├── test_major_plans.py   # 专业培养计划集成测试
│           └── test_refactoring.py   # 模块导入与结构验证
├── frontend/vue/                     # Vue 3 前端
│   ├── index.html
│   ├── vite.config.js                # Vite 配置（端口 5173）
│   ├── package.json
│   └── src/
│       ├── main.js                   # Vue 应用入口
│       ├── App.vue                   # 根组件（基于角色的视图路由）
│       ├── style.css
│       ├── api/
│       │   ├── client.js             # HTTP 客户端封装
│       │   └── services.js           # AuthService / StudentService / TeacherService / AdminService
│       ├── components/
│       │   ├── Login.vue             # 登录页面
│       │   ├── StudentView.vue       # 学生面板
│       │   ├── TeacherView.vue       # 教师面板
│       │   └── AdminView.vue         # 管理员面板
│       └── composables/
│           └── index.js              # 组合式函数（useAuth、useAsync、useList 等）
├── docker-compose.yml                # MySQL 8.0 容器
├── .env.example                      # 环境变量模板
├── start.sh                          # 一键启动脚本（zsh）
├── start.ps1                         # 一键启动脚本（PowerShell）
└── README.md
```

---

## 🚀 快速开始

### 1) 环境准备

- 安装 [Docker](https://docs.docker.com/get-docker/) 与 Docker Compose
- 安装 Python 3.10+
- 安装 Node.js 18+

### 2) 配置环境变量

在项目根目录创建 `.env` 文件（可参考 `.env.example`）：

```env
# MySQL 连接（Docker）
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307            # 默认映射端口，可自定义
MYSQL_DBNAME=student_db
MYSQL_USER=student_app
MYSQL_PASSWORD=your_app_password
MYSQL_ROOT_PASSWORD=your_root_password

# Flask
SECRET_KEY=change-me-in-production
FLASK_ENV=development
```

### 3) 启动 MySQL 数据库

```bash
docker compose up -d
```

MySQL 8.0 将在 `localhost:3307`（或自定义端口）启动，数据持久化到 Docker Volume。

### 4) 启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端（默认 http://localhost:5000）
python main.py
```

数据库 Schema 将在首次启动时自动初始化（包括表结构与默认管理员账号）。

### 5) 启动前端

```bash
cd frontend/vue

npm install
npm run dev       # 默认 http://localhost:5173
```

如后端不在本机，在项目根目录创建 `.env.development`：

```env
VITE_API_BASE=http://<后端IP或域名>:5000/api
```

### 6) 一键启动

- **Linux / macOS（zsh）**：运行 `./start.sh`
- **Windows（PowerShell）**：运行 `.\start.ps1`

---

## 📅 自动学期推进（半年+1）

脚本：[backend/app_core/scripts/advance_semester.py](backend/app_core/scripts/advance_semester.py)

当 `semester_updated_at` 距今超过设定月份（默认 6），且 `current_semester < 最大学期（默认 8）`，则自动将学生 `current_semester` +1 并刷新时间戳。

```bash
# 手动运行
python backend/app_core/scripts/advance_semester.py --months 6 --max-semester 8

# 配合 cron 每日执行（Linux）
0 3 * * * cd /path/to/DB_EX3 && python backend/app_core/scripts/advance_semester.py --months 6 --max-semester 8
```

管理员界面支持查看与手动修改学期（后端验证范围 1–8 并更新时间戳）。

---

## 📊 成绩权重管理

每门课程支持自定义平时成绩权重与期末成绩权重（`ordinary_weight` + `final_weight` = 1.0）：

- 教师/管理员可在界面中调整权重
- 修改权重后自动重算该课程所有选课学生的 `final_grade`
- 成绩计算公式：`final_grade = ordinary_score × ordinary_weight + final_score × final_weight`

---

## 📚 专业培养计划

管理员可创建多个专业培养计划，每个计划按学期组织课程体系：

- 按专业（major）创建培养计划
- 每个计划下按学期（1-12）添加课程
- 区分必修（required）与选修（elective）
- 学生只能浏览和选择本专业当前学期培养计划内的课程

---

## 📦 Excel 批量导入规范

### 管理员导入模板

| 工作表 | 必需列 | 可选列 | 说明 |
| -------- | -------- | -------- | ------ |
| courses | course_code, name, credit, capacity, semester | teacher_no, teacher_name, teacher_department | 课程基础信息与学期归属 |
| students | student_no, name, major | current_semester | 学生基础信息与当前学期 |
| enrollments | course_code, student_no | grade, status | 选课关系与成绩状态 |

### 教师花名册导入模板

| 工作表 | 必需列 | 说明 |
| -------- | -------- | ------ |
| course | course_code, name, credit, capacity, semester | 课程信息（仅一行） |
| students | student_no, name, major, current_semester | 学生名单 |

示例文件可通过 `generate_sample_excel.py` 和 `generate_teacher_roster.py` 生成，也可在管理员/教师界面下载模板。

---

## 🔐 默认账号

| 角色 | 用户名 | 密码 | 说明 |
| ----- | -------- | ------ | ------ |
| 管理员 | admin | admin@123 | 后端启动时自动创建 |
| 学生 | 学号 | s+学号 | 例如：S001 → sS001（创建学生时自动生成） |
| 教师 | 工号 | t+工号 | 例如：T001 → tT001（创建教师时自动生成） |

---

## 📡 API 概览

### 认证（`/api/auth`）
| 方法 | 路径 | 说明 |
| ------ | ------ | ------ |
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/logout` | 登出 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| POST | `/api/auth/change-password` | 修改密码 |

### 学生（`/api/student`）
| 方法 | 路径 | 说明 |
| ------ | ------ | ------ |
| GET | `/api/student/info` | 学生个人信息（含当前学期） |
| GET | `/api/student/semesters` | 可选学期列表 |
| GET | `/api/student/courses/available` | 可选课程（按专业培养计划与学期过滤） |
| GET | `/api/student/enrollments` | 我的选课与成绩 |
| POST | `/api/student/enrollments` | 选课 |
| DELETE | `/api/student/enrollments/{id}` | 退课 |

### 教师（`/api/teacher`）
| 方法 | 路径 | 说明 |
| ------ | ------ | ------ |
| GET | `/api/teacher/courses` | 我教授的课程（含选课人数） |
| GET | `/api/teacher/courses/{id}/students` | 课程学生名单与成绩 |
| GET | `/api/teacher/courses/stats` | 成绩统计（平均分/及格率/优秀率） |
| PUT | `/api/teacher/enrollments/{id}/grade` | 设置单个成绩 |
| PUT | `/api/teacher/enrollments/{id}/grades` | 设置平时/期末成绩（自动权重计算） |
| PUT | `/api/teacher/courses/{id}/weights` | 更新成绩权重（触发全部重算） |
| GET | `/api/teacher/courses/{id}/grades/export` | 导出成绩 Excel |
| POST | `/api/teacher/courses/import` | 导入花名册 Excel |
| GET | `/api/teacher/courses/import/sample` | 下载花名册模板 |

### 管理员（`/api`）
| 方法 | 路径 | 说明 |
| ------ | ------ | ------ |
| GET/POST | `/api/students` | 学生列表 / 创建 |
| PUT/DELETE | `/api/students/{id}` | 更新 / 删除学生 |
| GET/POST | `/api/teachers` | 教师列表 / 创建 |
| PUT/DELETE | `/api/teachers/{id}` | 更新 / 删除教师 |
| GET/POST | `/api/courses` | 课程列表 / 创建 |
| PUT/DELETE | `/api/courses/{id}` | 更新 / 删除课程 |
| GET/POST | `/api/enrollments` | 选课列表 / 创建 |
| PUT/DELETE | `/api/enrollments/{id}` | 更新 / 删除选课记录 |
| PUT | `/api/enrollments/{id}/grade` | 设置单个成绩 |
| PUT | `/api/enrollments/{id}/grades` | 设置平时/期末成绩 |
| PUT | `/api/courses/{id}/weights` | 更新成绩权重 |
| POST | `/api/import/courses` | 批量 Excel 导入（courses/students/enrollments） |
| GET | `/api/courses/{id}/grades/export` | 导出成绩 Excel |
| GET | `/api/statistics/overview` | 系统统计概览（含课程筛选） |
| GET | `/api/health` | 健康检查 |
| GET/POST | `/api/major-plans` | 培养计划列表 / 创建 |
| GET/PUT/DELETE | `/api/major-plans/{id}` | 查看 / 更新 / 删除培养计划 |
| GET/POST | `/api/major-plans/{id}/courses` | 计划课程列表 / 添加课程 |
| DELETE | `/api/major-plans/courses/{id}` | 从计划中移除课程 |

---

## 🛠️ 部署

### Docker Compose（推荐）

项目已包含 `docker-compose.yml` 用于启动 MySQL：

```bash
docker compose up -d
```

### Gunicorn + Nginx（Linux 生产环境）

```bash
pip install gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

配合 Nginx 反向代理，前端构建后部署静态文件：

```bash
cd frontend/vue
npm run build
# 将 dist/ 部署到 Nginx 静态目录
```

---

## 🧪 测试

```bash
cd backend
python -m unittest discover app_core/tests/
```

测试覆盖：
- 模块导入与结构完整性（`test_refactoring.py`）
- Repository 与 Service 层解耦（`test_decoupling.py`）
- 专业培养计划功能（`test_major_plans.py`）

---

## ❓ 常见问题

| 问题 | 解决方案 |
| ------ | ---------- |
| MySQL 连接失败 | 确认 `docker compose up -d` 已执行且容器正常运行 |
| 认证失败 | 检查 `.env` 中 `MYSQL_PASSWORD` 是否正确 |
| 前端 404 / CORS 错误 | 确认 `VITE_API_BASE` 指向正确的后端地址 |
| 数据库缺列报错（500） | 执行 `seeds/` 目录下对应迁移 SQL |
| 端口冲突 | 修改 `docker-compose.yml` 端口映射或 `.env` 中 `FLASK_PORT` |
| Docker 未安装 | 需手动安装 MySQL 8.0 并配置 `.env` 连接参数 |

---

## 📝 更新日志（摘录）

**v2.1.0**（2025-12）
- 数据库从 PostgreSQL 迁移至 MySQL 8.0
- 新增 Docker Compose 支持，简化数据库部署
- 新增成绩权重管理功能（按课程自定义平时/期末权重）
- 新增专业培养计划模块
- 完善三层架构解耦（API → Service → Repository）
- 新增请求去重中间件与操作审计日志
- 升级彩色分级日志系统

**v2.0.0**（2025-12）
- 完成后端数据验证层与操作审计
- 登录界面 UX 升级与删除确认对话框
- 学生课程发现与管理员仪表盘增强
- 选课与成绩的端到端流程优化
- 完整文档与部署指南

---

## 📄 许可证

MIT License
