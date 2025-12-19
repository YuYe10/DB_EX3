# 快速开始指南

## 📋 目录
1. [功能预览](#功能预览)
2. [系统要求](#系统要求)
3. [安装步骤](#安装步骤)
4. [使用说明](#使用说明)
5. [常见问题](#常见问题)
6. [技术细节](#技术细节)

---

## 🎯 功能预览

教师现在可以：
- ✅ 查看学生成绩（优先显示最终成绩）
- ✅ 编辑学生的平时成绩和期末成绩
- ✅ 自定义平时占比和期末占比
- ✅ 实时预览最终成绩
- ✅ 自动验证占比和（必须等于1）
- ✅ 导出包含最终成绩的 Excel

---

## 🔧 系统要求

### 后端
- Python 3.8+
- Flask 2.0+
- PostgreSQL 12+
- pandas, openpyxl

### 前端
- Node.js 16+
- npm 8+
- Vue 3.0+
- Vite 3.0+

### 浏览器
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 📦 安装步骤

### 1. 准备数据库
确保数据库已包含以下字段：
```sql
-- enrollments 表应包含:
- ordinary_score (NUMERIC)
- final_score (NUMERIC)
- ordinary_weight (NUMERIC)
- final_weight (NUMERIC)
- final_grade (NUMERIC)
```

### 2. 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖（如需要）
pip install -r requirements.txt

# 启动服务
python main.py

# 服务启动在 http://localhost:5000
```

### 3. 启动前端

```bash
# 进入前端目录
cd frontend/vue

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

### 4. 测试功能

```bash
# 1. 使用教师账号登录
# 2. 进入"我的授课"
# 3. 选择一门课程
# 4. 点击学生的"编辑成绩"按钮
# 5. 输入平时成绩、期末成绩
# 6. 调整占比（会自动验证）
# 7. 点击保存
```

---

## 📖 使用说明

### 编辑成绩的完整流程

#### 步骤 1: 进入课程
```
教师界面 → 我的授课 → 选择课程 → 查看学生列表
```

#### 步骤 2: 开始编辑
```
点击学生行的"编辑成绩"按钮 → 编辑器展开
```

#### 步骤 3: 输入数据
```
输入平时成绩 (0-100)
输入期末成绩 (0-100)
输入平时占比 (0-1)
期末占比会自动计算
```

#### 步骤 4: 验证
```
查看"占比和"是否为 1.00
查看"预计最终成绩"的计算结果
确认无误后点击保存
```

#### 步骤 5: 保存
```
点击"✓ 保存"按钮
系统提示成功后编辑器自动关闭
学生列表刷新显示新成绩
```

### 导出成绩

```
选择课程 → 点击"导出成绩Excel" → 下载文件
```

生成的 Excel 包含：
- 课程基本信息（课程号、名称、学分、容量、教师）
- 学生成绩表（学号、姓名、专业、**最终成绩**、状态）

---

## ❓ 常见问题

### Q1: 为什么修改占比后另一个占比会变？
**A**: 系统要求两个占比的和必须等于 1.0。修改一个占比时，系统自动调整另一个以保持和为 1.0。

```
示例：
- 修改平时占比为 0.4
- 期末占比自动变为 0.6（0.4 + 0.6 = 1.0）
```

### Q2: 如果占比和不等于 1 会怎样？
**A**: 保存时系统会检查，如果占比和不是 1.0（允许误差 ±0.01），会显示错误提示。

```
错误信息示例：
"占比和必须等于 1，当前为: 0.95"
```

### Q3: 最终成绩是怎样计算的？
**A**: 使用加权平均公式：

$$\text{最终成绩} = \text{平时成绩} \times \text{平时占比} + \text{期末成绩} \times \text{期末占比}$$

```
示例：
平时成绩: 80, 平时占比: 0.4
期末成绩: 85, 期末占比: 0.6
最终成绩 = 80 × 0.4 + 85 × 0.6 = 32 + 51 = 83.0
```

### Q4: 如果我不小心修改了怎么办？
**A**: 在编辑器关闭之前，可以点击"取消"按钮放弃所有更改。

```
编辑中 → 点击"取消" → 编辑器关闭，数据不保存
```

### Q5: 导出的 Excel 中会显示什么成绩？
**A**: 导出时会显示最终成绩。如果没有期末成绩，则显示平时成绩（向后兼容）。

```
显示优先级：
1. 最终成绩（final_grade）- 如果存在
2. 历史成绩（grade）- 备选
3. 空值 - 未评分
```

### Q6: 我可以看到其他教师的成绩吗？
**A**: 不可以。系统在权限层验证，确保教师只能看到和编辑其所教课程的数据。

### Q7: 平时和期末成绩有什么限制吗？
**A**: 是的，两个成绩都必须在 0-100 范围内，且支持小数点后一位精度。

```
有效范围：
- 成绩: 0.0 到 100.0
- 占比: 0.00 到 1.00
```

### Q8: 批量编辑成绩支持吗？
**A**: 当前版本需要逐个编辑。如果要批量操作，可以通过导入 Excel 功能实现。

---

## 🔍 技术细节

### 前端技术栈
```
Vue 3 (框架)
  ├── Composition API (组件逻辑)
  ├── ref() (响应式状态)
  └── Fetch API (网络请求)

Vite (构建工具)
  ├── 热模块更新
  └── 优化打包

CSS Grid (布局)
  ├── 响应式设计
  └── Flexbox (辅助)
```

### 后端技术栈
```
Flask (框架)
  ├── 路由处理
  ├── 认证中间件
  └── 错误处理

Python (语言)
  ├── 业务逻辑
  ├── 数据验证
  └── 权限检查

PostgreSQL (数据库)
  ├── 数据存储
  ├── SQL 查询
  └── 事务处理
```

### API 端点

#### 获取课程列表
```http
GET /api/teacher/courses
Authorization: Bearer <token>
```

**响应**:
```json
[
  {
    "id": 1,
    "name": "数据库原理",
    "course_code": "CS101",
    "enrolled_count": 50
  }
]
```

#### 获取学生列表
```http
GET /api/teacher/courses/{course_id}/students
Authorization: Bearer <token>
```

**响应**:
```json
[
  {
    "id": 1,
    "student_no": "2020001",
    "student_name": "张三",
    "major": "计算机科学",
    "ordinary_score": 80,
    "final_score": 85,
    "ordinary_weight": 0.4,
    "final_weight": 0.6,
    "final_grade": 83.0,
    "grade": null
  }
]
```

#### 更新成绩
```http
PUT /api/teacher/enrollments/{enrollment_id}/grades
Authorization: Bearer <token>
Content-Type: application/json

{
  "ordinary_score": 80,
  "final_score": 85,
  "ordinary_weight": 0.4,
  "final_weight": 0.6
}
```

**响应** (成功):
```json
{
  "message": "Student grades updated successfully"
}
```

**响应** (错误):
```json
{
  "message": "占比和必须为1，当前为0.95"
}
```

#### 导出成绩
```http
GET /api/teacher/courses/{course_id}/grades/export
Authorization: Bearer <token>
```

**响应**: Excel 文件

---

## 🚀 性能优化

### 前端优化
- ✅ 组件懒加载
- ✅ 事件去抖
- ✅ 状态缓存
- ✅ CSS 优化

### 后端优化
- ✅ 数据库索引
- ✅ 查询优化
- ✅ 连接池
- ✅ 缓存策略

### 推荐配置
```bash
# 环境变量
export VITE_API_BASE=http://localhost:5000/api
export FLASK_ENV=production
export DATABASE_POOL_SIZE=20
```

---

## 📚 相关文件

| 文件 | 说明 |
|------|------|
| IMPLEMENTATION_SUMMARY.md | 实现细节 |
| TEACHER_GRADES_GUIDE.md | 完整使用指南 |
| PROJECT_STATUS.md | 项目状态 |
| CHANGES_SUMMARY.md | 代码变更 |
| COMPLETION_CHECKLIST.md | 完成清单 |

---

## 🆘 故障排查

### 问题 1: 后端无法启动
```bash
# 检查 Python 版本
python --version

# 检查依赖
pip list | grep Flask

# 检查数据库连接
psql -h localhost -U user -d student_db -c "SELECT 1"

# 查看详细错误
python main.py --debug
```

### 问题 2: 前端页面空白
```bash
# 清除浏览器缓存
# Ctrl + Shift + Delete

# 重启开发服务器
npm run dev

# 检查 API 连接
curl http://localhost:5000/api/health
```

### 问题 3: 成绩编辑不成功
```bash
# 查看浏览器控制台错误
# F12 → Console

# 查看网络请求
# F12 → Network → 查看 PUT 请求

# 检查权限
# 确认登录的是正确的教师账户
```

### 问题 4: Excel 导出失败
```bash
# 检查 pandas 和 openpyxl
pip list | grep -E "pandas|openpyxl"

# 检查文件权限
ls -la /tmp

# 重启后端
python main.py
```

---

## 💡 最佳实践

1. **定期保存**: 编辑完成后立即保存，避免数据丢失
2. **验证占比**: 保存前确认"占比和"为 1.00
3. **检查预览**: 保存前查看"预计最终成绩"是否合理
4. **定期导出**: 定期导出成绩作为备份
5. **批量检查**: 定期检查学生的成绩是否有异常

---

## 📞 获取帮助

- 📖 查看详细文档：[TEACHER_GRADES_GUIDE.md](TEACHER_GRADES_GUIDE.md)
- 🔍 了解技术细节：[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- 📊 查看项目状态：[PROJECT_STATUS.md](PROJECT_STATUS.md)
- 📋 查看完成清单：[COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md)

---

**祝您使用愉快！** 🎉
