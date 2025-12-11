# 后端代码重构说明

## 📁 新的项目结构

```
backend/
├── app.py                  # 应用入口（使用工厂模式）
├── main.py                # 服务启动脚本
├── config.py              # 配置管理
├── utils.py               # 通用工具函数
├── db.py                  # 数据库连接（保持不变）
├── services/              # 业务逻辑层
│   ├── __init__.py
│   ├── user_service.py    # 用户认证服务
│   ├── student_service.py # 学生业务逻辑
│   ├── teacher_service.py # 教师业务逻辑
│   └── admin_service.py   # 管理员业务逻辑
└── api/                   # 路由层（蓝图）
    ├── __init__.py
    ├── auth.py           # 认证路由
    ├── student.py        # 学生路由
    ├── teacher.py        # 教师路由
    └── admin.py          # 管理员路由
```

## 🎯 重构目标

### 1. **关注点分离**
- **配置管理** (`config.py`): 所有配置集中管理
- **工具函数** (`utils.py`): 通用功能复用
- **业务逻辑** (`services/`): 独立于路由的业务处理
- **路由控制** (`api/`): 只负责HTTP请求处理

### 2. **代码复用性**
- 统一的响应格式 (`json_response`, `error_response`)
- 统一的字段验证 (`validate_fields`)
- 统一的认证装饰器 (`require_auth`)

### 3. **可测试性**
- Services层可独立测试（不依赖Flask上下文）
- 清晰的函数签名和返回值
- 业务逻辑与HTTP层解耦

### 4. **可维护性**
- 单一职责原则：每个模块只做一件事
- 代码组织清晰，易于定位问题
- 便于团队协作开发

## 📝 核心模块说明

### config.py
集中管理所有配置项：
- Flask配置（密钥、调试模式等）
- Session配置
- CORS配置
- 数据库配置

### utils.py
提供通用工具函数：
- `hash_password()`: 密码加密
- `json_response()`: 标准JSON响应
- `error_response()`: 错误响应
- `validate_fields()`: 字段验证
- `require_auth()`: 认证装饰器

### services/
业务逻辑层，每个服务类负责特定领域：

**UserService**: 用户管理
- 用户认证
- 密码修改
- 用户账号初始化

**StudentService**: 学生功能
- 获取可选课程
- 查看选课记录
- 选课/退课

**TeacherService**: 教师功能
- 获取教授课程
- 查看学生名单
- 录入成绩

**AdminService**: 管理员功能
- CRUD操作（学生、教师、课程、选课）
- 数据统计

### api/
路由层，使用Flask蓝图组织：

**auth_bp**: 认证相关路由
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/change-password

**student_bp**: 学生路由
- GET /api/student/courses/available
- GET/POST /api/student/enrollments
- DELETE /api/student/enrollments/:id

**teacher_bp**: 教师路由
- GET /api/teacher/courses
- GET /api/teacher/courses/:id/students
- PUT /api/teacher/enrollments/:id/grade

**admin_bp**: 管理员路由
- GET/POST /api/students
- PUT/DELETE /api/students/:id
- GET/POST /api/teachers
- PUT/DELETE /api/teachers/:id
- GET/POST /api/courses
- PUT/DELETE /api/courses/:id
- GET/POST /api/enrollments
- PUT /api/enrollments/:id/grade
- DELETE /api/enrollments/:id
- GET /api/statistics/overview
- GET /api/health

## 🔄 与旧代码的兼容性

所有API端点保持不变，前端无需修改。重构只改变了代码组织方式，不改变功能。

## 🚀 启动方式

与之前完全相同：

```bash
cd backend
python app.py
# 或
python main.py
```

## 📌 优势对比

### 重构前 (app.py 600+行)
```python
# 所有代码在一个文件
- 配置、工具、业务、路由混在一起
- 难以测试
- 难以维护
- 代码重复多
```

### 重构后 (模块化)
```python
# 清晰的分层架构
✅ 配置独立 (config.py)
✅ 工具复用 (utils.py)
✅ 业务逻辑独立 (services/)
✅ 路由清晰 (api/)
✅ 易于测试
✅ 易于扩展
✅ 代码复用
```

## 🔧 后续扩展建议

1. **添加日志系统**: 使用Python logging模块
2. **添加单元测试**: 针对services层编写测试
3. **添加API文档**: 使用Flask-RESTX或Swagger
4. **添加数据验证**: 使用marshmallow或pydantic
5. **添加缓存层**: 使用Redis缓存常用查询
6. **添加异常处理中间件**: 统一处理未捕获的异常

## 📖 开发规范

### 添加新功能
1. 在对应的service中添加业务逻辑
2. 在对应的api蓝图中添加路由
3. 确保使用统一的响应格式
4. 添加必要的权限验证

### 示例：添加新的学生功能
```python
# 1. 在 services/student_service.py 中添加方法
@staticmethod
def get_grades(student_id: int):
    return db.fetch_all(
        "SELECT * FROM enrollments WHERE student_id=%s",
        [student_id]
    )

# 2. 在 api/student.py 中添加路由
@student_bp.route('/grades', methods=['GET'])
@require_auth(['student'])
def get_grades():
    grades = StudentService.get_grades(session['ref_id'])
    return json_response(grades)
```

## 🎉 重构完成

后端代码已经成功重构为模块化、分层架构，具有更好的可维护性和可扩展性！
