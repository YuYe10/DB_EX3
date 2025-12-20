#!/usr/bin/env python3
"""
学生学期限制选课功能 - 验证脚本
检查实现的各个方面是否正确
"""

import os
import sys
import re

def check_file_exists(path, description):
    """检查文件是否存在"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (未找到)")
        return False

def check_file_contains(path, pattern, description):
    """检查文件是否包含特定模式"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description}")
                return False
    except Exception as e:
        print(f"❌ {description} (错误: {str(e)})")
        return False

def main():
    """运行检查"""
    print("=" * 60)
    print("学生学期限制选课功能 - 实现检查")
    print("=" * 60)
    print()
    
    results = []
    
    # 检查核心文件修改
    print("📋 检查核心文件修改...")
    print("-" * 60)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 数据库
    results.append(check_file_contains(
        os.path.join(base_path, 'backend/app_core/db.py'),
        r'current_semester.*INT.*DEFAULT\s*1',
        "数据库: students 表包含 current_semester 字段"
    ))
    
    # 学生服务
    results.append(check_file_contains(
        os.path.join(base_path, 'backend/app_core/services/student_service.py'),
        r"SELECT.*current_semester.*FROM students",
        "学生服务: get_student_info() 返回 current_semester"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_path, 'backend/app_core/services/student_service.py'),
        r"plan_course\['semester'\]\s*!=\s*student\['current_semester'\]",
        "学生服务: enroll_course() 包含学期验证"
    ))
    
    # 学生界面
    results.append(check_file_contains(
        os.path.join(base_path, 'frontend/vue/src/components/StudentView.vue'),
        r'semester-badge',
        "前端UI: 包含 semester-badge 样式"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_path, 'frontend/vue/src/components/StudentView.vue'),
        r"c\.semester\s*!==\s*studentInfo\.current_semester",
        "前端UI: 包含学期检查逻辑"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_path, 'frontend/vue/src/components/StudentView.vue'),
        r'studentInfo\s*=\s*ref',
        "前端UI: 包含 studentInfo 响应式变量"
    ))
    
    # 脚本更新
    results.append(check_file_contains(
        os.path.join(base_path, 'backend/app_core/scripts/generate_sample_excel.py'),
        r'current_semester',
        "脚本: generate_sample_excel.py 支持 current_semester"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_path, 'backend/app_core/scripts/generate_teacher_roster.py'),
        r'current_semester',
        "脚本: generate_teacher_roster.py 支持 current_semester"
    ))
    
    print()
    
    # 检查新增文件
    print("📦 检查新增文件...")
    print("-" * 60)
    
    results.append(check_file_exists(
        os.path.join(base_path, 'backend/app_core/seeds/add_semester_to_students.sql'),
        "迁移脚本: SQL 迁移文件"
    ))
    
    results.append(check_file_exists(
        os.path.join(base_path, 'backend/app_core/scripts/migrate_add_semester.py'),
        "迁移工具: Python 迁移脚本"
    ))
    
    results.append(check_file_exists(
        os.path.join(base_path, 'SEMESTER_FEATURE_IMPLEMENTATION.md'),
        "文档: 实现总结文档"
    ))
    
    results.append(check_file_exists(
        os.path.join(base_path, 'DEPLOYMENT_GUIDE_CN.md'),
        "文档: 部署指南"
    ))
    
    results.append(check_file_exists(
        os.path.join(base_path, 'IMPLEMENTATION_CHECKLIST.md'),
        "文档: 实现检查清单"
    ))
    
    print()
    
    # 检查 README 更新
    print("📖 检查 README 更新...")
    print("-" * 60)
    
    results.append(check_file_contains(
        os.path.join(base_path, 'README.md'),
        r'当前学期限制选课',
        "README: 包含学期限制功能说明"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_path, 'README.md'),
        r'migrate_add_semester',
        "README: 包含迁移脚本运行说明"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_path, 'README.md'),
        r'current_semester',
        "README: Excel 格式规范包含 current_semester"
    ))
    
    print()
    
    # 统计结果
    print("=" * 60)
    print("📊 检查结果总结")
    print("-" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    print(f"📈 完成度: {percentage:.1f}%")
    
    print()
    if percentage == 100:
        print("🎉 所有检查均已通过！")
        print("✨ 实现完成，可以进行部署测试。")
        return 0
    else:
        print("⚠️  有些项目未通过检查，请查看上面的详细信息。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
