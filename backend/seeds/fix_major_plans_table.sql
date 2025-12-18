-- 修复 major_plans 表的列名问题
-- 如果表使用的是 'name' 列而不是 'major_name'，则重命名该列

-- 方案1：重命名列（如果存在 name 列）
DO $$ 
BEGIN
    -- 检查是否有 name 列
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'major_plans' 
        AND column_name = 'name'
    ) THEN
        -- 重命名 name 为 major_name
        ALTER TABLE major_plans RENAME COLUMN name TO major_name;
        RAISE NOTICE '已将 major_plans.name 重命名为 major_plans.major_name';
    END IF;
    
    -- 检查是否缺少 major_name 列
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'major_plans' 
        AND column_name = 'major_name'
    ) THEN
        -- 如果没有 major_name 列，添加它
        ALTER TABLE major_plans ADD COLUMN major_name VARCHAR(128) NOT NULL DEFAULT '';
        RAISE NOTICE '已添加 major_plans.major_name 列';
        
        -- 如果有 major 列，从它复制数据
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'major_plans' 
            AND column_name = 'major'
        ) THEN
            UPDATE major_plans SET major_name = major;
            ALTER TABLE major_plans DROP COLUMN major;
            RAISE NOTICE '已从 major_plans.major 迁移数据';
        END IF;
    END IF;
    
    -- 确保 updated_at 列存在
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'major_plans' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE major_plans ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
        RAISE NOTICE '已添加 major_plans.updated_at 列';
    END IF;
    
    -- 确保 unique 约束存在
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'major_plans_major_name_key'
    ) THEN
        ALTER TABLE major_plans ADD CONSTRAINT major_plans_major_name_key UNIQUE (major_name);
        RAISE NOTICE '已添加 major_name 的 UNIQUE 约束';
    END IF;
    
END $$;

-- 显示最终的表结构
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'major_plans' 
ORDER BY ordinal_position;
