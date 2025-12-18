"""修复 major_plans 表的列名问题"""
from db import db
import sys

def main():
    print("=" * 60)
    print("修复 major_plans 表结构")
    print("=" * 60)
    
    try:
        # 1. 首先检查当前表结构
        print("\n1. 检查当前表结构...")
        columns = db.fetch_all("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'major_plans' 
            ORDER BY ordinal_position
        """)
        
        if columns:
            print("   当前列：")
            column_names = []
            for col in columns:
                column_names.append(col['column_name'])
                print(f"   - {col['column_name']}: {col['data_type']}")
        else:
            print("   ⚠️  major_plans 表不存在或为空")
            print("\n2. 创建 major_plans 表...")
            db.execute("""
                CREATE TABLE IF NOT EXISTS major_plans (
                    id SERIAL PRIMARY KEY,
                    major_name VARCHAR(128) NOT NULL,
                    description TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(major_name)
                )
            """)
            print("   ✅ 表已创建")
            return
        
        # 2. 检查是否需要重命名列
        print("\n2. 检查列名...")
        if 'name' in column_names and 'major_name' not in column_names:
            print("   发现问题：表使用的是 'name' 列而不是 'major_name'")
            print("   正在重命名列...")
            db.execute("ALTER TABLE major_plans RENAME COLUMN name TO major_name")
            print("   ✅ 已将 'name' 重命名为 'major_name'")
        elif 'major' in column_names and 'major_name' not in column_names:
            print("   发现问题：表使用的是 'major' 列而不是 'major_name'")
            print("   正在重命名列...")
            db.execute("ALTER TABLE major_plans RENAME COLUMN major TO major_name")
            print("   ✅ 已将 'major' 重命名为 'major_name'")
        elif 'major_name' in column_names:
            print("   ✅ 'major_name' 列已存在")
        else:
            print("   ⚠️  未找到专业名称列，添加 'major_name' 列...")
            db.execute("""
                ALTER TABLE major_plans 
                ADD COLUMN major_name VARCHAR(128) NOT NULL DEFAULT ''
            """)
            print("   ✅ 已添加 'major_name' 列")
        
        # 3. 确保 updated_at 列存在
        print("\n3. 检查 'updated_at' 列...")
        if 'updated_at' not in column_names:
            print("   添加 'updated_at' 列...")
            db.execute("""
                ALTER TABLE major_plans 
                ADD COLUMN updated_at TIMESTAMP DEFAULT NOW()
            """)
            print("   ✅ 已添加 'updated_at' 列")
        else:
            print("   ✅ 'updated_at' 列已存在")
        
        # 4. 确保 UNIQUE 约束存在
        print("\n4. 检查 UNIQUE 约束...")
        constraints = db.fetch_all("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'major_plans' 
            AND constraint_type = 'UNIQUE'
        """)
        
        has_unique = any('major_name' in c['constraint_name'].lower() 
                        for c in constraints)
        
        if not has_unique:
            print("   添加 major_name 的 UNIQUE 约束...")
            try:
                db.execute("""
                    ALTER TABLE major_plans 
                    ADD CONSTRAINT major_plans_major_name_key UNIQUE (major_name)
                """)
                print("   ✅ 已添加 UNIQUE 约束")
            except Exception as e:
                if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                    print("   ℹ️  UNIQUE 约束已存在")
                else:
                    raise
        else:
            print("   ✅ UNIQUE 约束已存在")
        
        # 5. 显示最终表结构
        print("\n5. 最终表结构：")
        final_columns = db.fetch_all("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'major_plans' 
            ORDER BY ordinal_position
        """)
        
        for col in final_columns:
            nullable = '可空' if col['is_nullable'] == 'YES' else '非空'
            default = f" (默认: {col['column_default']})" if col['column_default'] else ""
            print(f"   - {col['column_name']}: {col['data_type']} ({nullable}){default}")
        
        # 6. 检查 major_plan_courses 表
        print("\n6. 检查 major_plan_courses 表...")
        mpc_exists = db.fetch_one("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'major_plan_courses'
            ) as exists
        """)
        
        if mpc_exists and mpc_exists['exists']:
            print("   ✅ major_plan_courses 表已存在")
        else:
            print("   创建 major_plan_courses 表...")
            db.execute("""
                CREATE TABLE IF NOT EXISTS major_plan_courses (
                    id SERIAL PRIMARY KEY,
                    plan_id INT REFERENCES major_plans(id) ON DELETE CASCADE,
                    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
                    semester INT NOT NULL,
                    is_required BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(plan_id, course_id, semester)
                )
            """)
            print("   ✅ 表已创建")
        
        print("\n" + "=" * 60)
        print("✅ 所有修复完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
