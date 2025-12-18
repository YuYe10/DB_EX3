"""检查 major_plans 表结构"""
from db import db

try:
    # 检查表结构
    result = db.fetch_all("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'major_plans' 
        ORDER BY ordinal_position
    """)
    
    if result:
        print('major_plans 表的列结构：')
        for row in result:
            nullable = '可空' if row['is_nullable'] == 'YES' else '非空'
            print(f"  - {row['column_name']}: {row['data_type']} ({nullable})")
    else:
        print('major_plans 表不存在')
        
    # 尝试查询表数据
    print('\n尝试查询表数据...')
    plans = db.fetch_all("SELECT * FROM major_plans LIMIT 1")
    if plans:
        print(f'表中有数据，列名: {list(plans[0].keys())}')
    else:
        print('表为空')
        
except Exception as e:
    print(f'错误: {type(e).__name__}: {e}')
