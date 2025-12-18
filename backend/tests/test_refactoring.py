"""
重构代码验证脚本 - 不需要数据库连接
"""

print("=" * 60)
print("后端代码重构验证")
print("=" * 60)

# 1. 测试配置模块
print("\n[1/6] 测试配置模块...")
try:
    from config import Config
    print(f"✅ Config导入成功")
    print(f"   - SECRET_KEY: {Config.SECRET_KEY[:20]}...")
    print(f"   - DEBUG: {Config.DEBUG}")
    print(f"   - CORS_ORIGINS: {len(Config.CORS_ORIGINS)} 个")
except Exception as e:
    print(f"❌ Config导入失败: {e}")

# 2. 测试工具模块
print("\n[2/6] 测试工具模块...")
try:
    from utils import hash_password, json_response, error_response, validate_fields
    
    # 测试密码哈希
    hashed = hash_password("test123")
    print(f"✅ hash_password() 工作正常")
    print(f"   - 哈希长度: {len(hashed)}")
    
    # 测试字段验证
    try:
        validate_fields({'name': 'test'}, ['name', 'age'])
    except ValueError as e:
        print(f"✅ validate_fields() 工作正常 (检测到缺失字段)")
    
    print(f"✅ 工具函数导入成功")
except Exception as e:
    print(f"❌ 工具模块导入失败: {e}")

# 3. 测试Services模块结构
print("\n[3/6] 测试Services模块...")
try:
    import services
    print(f"✅ Services包导入成功")
    print(f"   - UserService: {'UserService' in dir(services)}")
    print(f"   - StudentService: {'StudentService' in dir(services)}")
    print(f"   - TeacherService: {'TeacherService' in dir(services)}")
    print(f"   - AdminService: {'AdminService' in dir(services)}")
except Exception as e:
    print(f"❌ Services模块导入失败: {e}")

# 4. 测试API蓝图模块
print("\n[4/6] 测试API蓝图模块...")
try:
    from api import auth_bp, student_bp, teacher_bp, admin_bp
    print(f"✅ API蓝图导入成功")
    print(f"   - auth_bp: {auth_bp.name} ({len(list(auth_bp.deferred_functions))} 个路由)")
    print(f"   - student_bp: {student_bp.name}")
    print(f"   - teacher_bp: {teacher_bp.name}")
    print(f"   - admin_bp: {admin_bp.name}")
except Exception as e:
    print(f"❌ API蓝图导入失败: {e}")

# 5. 测试应用创建（不启动）
print("\n[5/6] 测试Flask应用创建...")
try:
    import sys
    import os
    
    # Mock db module to avoid database connection
    class MockDB:
        def fetch_one(self, *args, **kwargs):
            return None
        def fetch_all(self, *args, **kwargs):
            return []
        def execute(self, *args, **kwargs):
            pass
        def execute_returning(self, *args, **kwargs):
            return 1
    
    # 替换db模块
    sys.modules['db'] = type('MockModule', (), {'db': MockDB()})()
    
    from app import create_app
    test_app = create_app()
    
    print(f"✅ Flask应用创建成功")
    print(f"   - 应用名称: {test_app.name}")
    print(f"   - 注册的蓝图数: {len(test_app.blueprints)}")
    print(f"   - 蓝图列表: {list(test_app.blueprints.keys())}")
    
    # 列出所有路由
    print(f"\n   注册的路由:")
    routes = []
    for rule in test_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append(f"     {rule.methods} {rule.rule}")
    
    # 按路径排序并去重
    routes = sorted(set(routes))
    for route in routes[:10]:  # 只显示前10个
        print(route)
    if len(routes) > 10:
        print(f"     ... 还有 {len(routes) - 10} 个路由")
    
except Exception as e:
    print(f"❌ Flask应用创建失败: {e}")
    import traceback
    traceback.print_exc()

# 6. 检查文件结构
print("\n[6/6] 检查文件结构...")
try:
    import os
    backend_path = os.path.dirname(__file__)
    
    required_files = [
        'app.py',
        'config.py',
        'utils.py',
        'main.py',
        'services/__init__.py',
        'services/user_service.py',
        'services/student_service.py',
        'services/teacher_service.py',
        'services/admin_service.py',
        'api/__init__.py',
        'api/auth.py',
        'api/student.py',
        'api/teacher.py',
        'api/admin.py',
    ]
    
    all_exist = True
    for file in required_files:
        path = os.path.join(backend_path, file)
        exists = os.path.exists(path)
        if not exists:
            print(f"   ❌ 缺失: {file}")
            all_exist = False
    
    if all_exist:
        print(f"✅ 所有必需文件都存在 ({len(required_files)} 个)")
    
    # 统计代码行数
    total_lines = 0
    for file in required_files:
        if file.endswith('.py'):
            path = os.path.join(backend_path, file)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
    
    print(f"   总代码行数: {total_lines} 行")
    print(f"   旧版 app.py: 606 行")
    print(f"   模块化优势: 代码分散到 {len(required_files)} 个文件")
    
except Exception as e:
    print(f"❌ 文件结构检查失败: {e}")

print("\n" + "=" * 60)
print("验证完成！")
print("=" * 60)
print("\n如果所有测试都通过，说明重构成功！")
print("下一步: 安装依赖后启动服务器进行集成测试")
print("命令: cd backend && python app.py")
