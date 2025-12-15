# 日志系统配置说明

## 概述

新的日志系统提供了彩色输出、分级别提示和高级格式化，完全符合zsh终端高亮显示。

## 主要特性

### 1. 彩色日志输出
- 根据日志级别自动着色（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- 不同操作类型使用不同的Emoji图标
- HTTP方法（GET、POST、PUT、DELETE）自动着色
- HTTP状态码着色（2xx绿色、3xx蓝色、4xx黄色、5xx红色）

### 2. 日志级别与图标

| 级别 | 图标 | 颜色 | 说明 |
|------|------|------|------|
| DEBUG | 🔍 | 灰色 | 调试信息 |
| INFO | ℹ️ | 蓝色 | 普通信息 |
| SUCCESS | ✅ | 绿色 | 成功操作 |
| WARNING | ⚠️ | 黄色 | 警告信息 |
| ERROR | ❌ | 红色 | 错误信息 |
| CRITICAL | 🔴 | 加粗红 | 严重错误 |

### 3. 特殊日志类型

#### REQUEST (请求)
- 图标: `→`
- 颜色: 蓝色
- 格式: `REQUEST: {METHOD} {PATH}`
- 示例: `ℹ️ REQUEST: → GET /api/students`

#### RESPONSE (响应)
- 图标: `←`
- 颜色: 根据状态码
- 格式: `RESPONSE: {STATUS} {METHOD} {PATH} ({ELAPSED}ms)`
- 示例: `ℹ️ RESPONSE: ← 200 GET /api/students (45.23ms)`

#### DATABASE (数据库)
- 图标: `💾`
- 颜色: 洋红色
- 格式: `DATABASE: {OPERATION} on {TABLE}`
- 示例: `ℹ️ DATABASE: 💾 INSERT on students`

#### AUTH (认证)
- 图标: `🔐`
- 颜色: 蓝绿色
- 格式: `AUTH: {ACTION} ({USER})`
- 示例: `ℹ️ AUTH: 🔐 Login (user123)`

### 4. 文件输出

所有日志同时写入文件：

- **logs/app.log** - 所有日志（包括DEBUG）
- **logs/error.log** - 仅ERROR及以上级别
- **logs/operation.log** - 操作审计日志（如有）

## 使用示例

### 在Python代码中

```python
import logging
from logger_config import log_request, log_response, log_database, log_auth, log_error

logger = logging.getLogger(__name__)

# 记录普通信息
logger.info("应用已初始化")
logger.warning("⚠️ 警告信息")
logger.error("❌ 发生错误")

# 记录特殊操作
log_request("GET", "/api/students")
log_response(200, "GET", "/api/students", elapsed=45.23)
log_database("INSERT", "students", name="张三", student_no="S001")
log_auth("Login", user="admin")
log_error("数据库连接失败", connection_error, host="192.168.0.61")
```

### 在API端点中

```python
from flask import Blueprint
from logger_config import log_database, log_error

bp = Blueprint('student', __name__)

@bp.route('/api/students', methods=['POST'])
def create_student():
    try:
        # 你的逻辑代码
        log_database("INSERT", "students", student_no=request.json.get('student_no'))
        return {"success": True}
    except Exception as e:
        log_error("Failed to create student", e)
        raise
```

## 日志输出示例

```
21:58:52 ℹ️ INFO     [werkzeug] REQUEST: → GET /api/students
21:58:52 ℹ️ INFO     [response] RESPONSE: ← 200 GET /api/students (12.34ms)
21:58:53 ℹ️ INFO     [database] DATABASE: 💾 INSERT on students
21:58:54 🔐 INFO     [auth] AUTH: 🔐 Login (admin)
21:58:55 ❌ ERROR    [error] ERROR: Database connection failed - Connection timeout
21:58:56 ⚠️ WARNING  [audit] Duplicate request blocked: /api/students (user123)
21:58:57 ✅ SUCCESS  [database] Operation completed successfully
```

## 自定义颜色

可以在 `logger_config.py` 中修改 `Colors` 类来自定义颜色：

```python
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    # ... 更多颜色
```

## 性能考虑

- 日志系统使用异步处理，不会显著影响应用性能
- 文件日志和控制台日志分离配置
- 自动日志轮转（可在生产环境配置）

## 故障排除

### 日志未显示颜色
- 检查终端是否支持ANSI颜色（zsh、bash现代版本都支持）
- 在某些IDE的终端中可能需要启用"允许ANSI颜色"选项

### 日志级别过多/过少
- 修改 `logger_config.py` 中 `setup_logging()` 的 `console_level` 参数
- 或在 `main.py` 中调整：`setup_logging(console_level=logging.INFO)`

### 文件日志损坏
- 删除 `logs/` 目录中的文件，系统会自动重建
- 确保 `logs/` 目录有写入权限

## 下一步改进

- [ ] 集成Sentry用于错误追踪
- [ ] 添加日志轮转（按大小和时间）
- [ ] 支持结构化日志（JSON格式）
- [ ] 实时日志查看界面
- [ ] 性能指标自动采集
