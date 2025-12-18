-- ====================================================
-- Professional Development Plans Sample Data
-- 专业培养计划示例数据
-- ====================================================

-- 1. 创建计算机科学专业培养计划
INSERT INTO major_plans (major_name, description) VALUES 
  ('计算机科学', '计算机科学与技术专业的核心课程与修习要求'),
  ('软件工程', '软件工程专业的专业培养计划'),
  ('信息学', '信息学专业的课程安排与学习要求'),
  ('数学与应用数学', '数学与应用数学专业的核心课程计划')
ON CONFLICT DO NOTHING;

-- 获取计划ID (这些是示例值，实际运行时需要根据插入后的真实ID替换)
-- 在PostgreSQL中，可以使用下面的方式获取刚插入的ID

-- 2. 为计算机科学专业添加课程
DO $$
DECLARE
  cs_plan_id INT;
  se_plan_id INT;
  info_plan_id INT;
  math_plan_id INT;
  course_ids INT[];
BEGIN
  -- 获取各个专业计划的ID
  SELECT id INTO cs_plan_id FROM major_plans WHERE major_name = '计算机科学' LIMIT 1;
  SELECT id INTO se_plan_id FROM major_plans WHERE major_name = '软件工程' LIMIT 1;
  SELECT id INTO info_plan_id FROM major_plans WHERE major_name = '信息学' LIMIT 1;
  SELECT id INTO math_plan_id FROM major_plans WHERE major_name = '数学与应用数学' LIMIT 1;

  -- ========== 计算机科学课程 (第1-8学期) ==========
  IF cs_plan_id IS NOT NULL THEN
    -- 第1学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 1, true FROM courses WHERE name IN ('高等数学', '大学英语', '计算机导论') ON CONFLICT DO NOTHING;
    
    -- 第2学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 2, true FROM courses WHERE name IN ('线性代数', '离散数学', 'C语言程序设计') ON CONFLICT DO NOTHING;
    
    -- 第3学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 3, true FROM courses WHERE name IN ('数据结构', '数据库原理', '操作系统基础') ON CONFLICT DO NOTHING;
    
    -- 第4学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 4, true FROM courses WHERE name IN ('计算机组成原理', '数据库实验', '算法设计') ON CONFLICT DO NOTHING;
    
    -- 第5学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 5, true FROM courses WHERE name IN ('操作系统', '计算机网络', '编译原理') ON CONFLICT DO NOTHING;
    
    -- 第6学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 6, true FROM courses WHERE name IN ('数据库系统实现', '高等数学实验', '计算机网络实验') ON CONFLICT DO NOTHING;
    
    -- 第7学期 (选修课程为主)
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 7, false FROM courses WHERE name IN ('人工智能基础', '机器学习导论', '图形学基础') ON CONFLICT DO NOTHING;
    
    -- 第8学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT cs_plan_id, id, 8, false FROM courses WHERE name IN ('大数据技术', '云计算基础', '区块链技术') ON CONFLICT DO NOTHING;
  END IF;

  -- ========== 软件工程课程 (第1-8学期) ==========
  IF se_plan_id IS NOT NULL THEN
    -- 第1学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 1, true FROM courses WHERE name IN ('高等数学', '大学英语', '计算机导论') ON CONFLICT DO NOTHING;
    
    -- 第2学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 2, true FROM courses WHERE name IN ('线性代数', '离散数学', 'C语言程序设计') ON CONFLICT DO NOTHING;
    
    -- 第3学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 3, true FROM courses WHERE name IN ('数据结构', '数据库原理', '操作系统基础') ON CONFLICT DO NOTHING;
    
    -- 第4学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 4, true FROM courses WHERE name IN ('软件工程', '设计模式', 'Java程序设计') ON CONFLICT DO NOTHING;
    
    -- 第5学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 5, true FROM courses WHERE name IN ('软件测试', '需求分析', '项目管理') ON CONFLICT DO NOTHING;
    
    -- 第6学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 6, true FROM courses WHERE name IN ('系统设计', '数据库系统实现', '软件文档编写') ON CONFLICT DO NOTHING;
    
    -- 第7学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 7, false FROM courses WHERE name IN ('Web框架', '移动开发基础', '微服务架构') ON CONFLICT DO NOTHING;
    
    -- 第8学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT se_plan_id, id, 8, false FROM courses WHERE name IN ('云原生开发', 'DevOps技术', '团队协作工具') ON CONFLICT DO NOTHING;
  END IF;

  -- ========== 信息学课程 (第1-8学期) ==========
  IF info_plan_id IS NOT NULL THEN
    -- 第1学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 1, true FROM courses WHERE name IN ('高等数学', '大学英语', '计算机导论') ON CONFLICT DO NOTHING;
    
    -- 第2学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 2, true FROM courses WHERE name IN ('线性代数', '离散数学', 'C语言程序设计') ON CONFLICT DO NOTHING;
    
    -- 第3学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 3, true FROM courses WHERE name IN ('数据结构', '概率论与数理统计', 'Web开发基础') ON CONFLICT DO NOTHING;
    
    -- 第4学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 4, true FROM courses WHERE name IN ('计算机组成原理', '数据库原理', 'Python程序设计') ON CONFLICT DO NOTHING;
    
    -- 第5学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 5, true FROM courses WHERE name IN ('计算机网络', '信息安全基础', '大数据处理基础') ON CONFLICT DO NOTHING;
    
    -- 第6学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 6, true FROM courses WHERE name IN ('数据库系统实现', '网络安全', '信息检索') ON CONFLICT DO NOTHING;
    
    -- 第7学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 7, false FROM courses WHERE name IN ('知识图谱', '自然语言处理', '数据可视化') ON CONFLICT DO NOTHING;
    
    -- 第8学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT info_plan_id, id, 8, false FROM courses WHERE name IN ('信息伦理与法律', '前沿信息技术', '信息管理实践') ON CONFLICT DO NOTHING;
  END IF;

  -- ========== 数学与应用数学课程 (第1-8学期) ==========
  IF math_plan_id IS NOT NULL THEN
    -- 第1学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 1, true FROM courses WHERE name IN ('高等数学', '大学英语', '计算机导论') ON CONFLICT DO NOTHING;
    
    -- 第2学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 2, true FROM courses WHERE name IN ('线性代数', '离散数学', '解析几何') ON CONFLICT DO NOTHING;
    
    -- 第3学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 3, true FROM courses WHERE name IN ('数据结构', '概率论与数理统计', '高等数学实验') ON CONFLICT DO NOTHING;
    
    -- 第4学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 4, true FROM courses WHERE name IN ('复变函数', '数学分析', 'C语言程序设计') ON CONFLICT DO NOTHING;
    
    -- 第5学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 5, true FROM courses WHERE name IN ('常微分方程', '偏微分方程', '数值分析') ON CONFLICT DO NOTHING;
    
    -- 第6学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 6, true FROM courses WHERE name IN ('数据库原理', 'Python程序设计', '计算机网络') ON CONFLICT DO NOTHING;
    
    -- 第7学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 7, false FROM courses WHERE name IN ('优化理论', '图论', '组合数学') ON CONFLICT DO NOTHING;
    
    -- 第8学期
    INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
    SELECT math_plan_id, id, 8, false FROM courses WHERE name IN ('泛函分析', '拓扑学', '抽象代数') ON CONFLICT DO NOTHING;
  END IF;

END $$;

-- ====================================================
-- 结果验证查询
-- ====================================================
-- 查看所有专业计划
SELECT id, major_name, description, created_at FROM major_plans ORDER BY id;

-- 查看每个专业的课程数量（按学期分组）
SELECT 
  mp.major_name,
  mpc.semester,
  COUNT(*) as course_count,
  SUM(CASE WHEN mpc.is_required THEN 1 ELSE 0 END) as required_count,
  SUM(CASE WHEN NOT mpc.is_required THEN 1 ELSE 0 END) as elective_count
FROM major_plans mp
LEFT JOIN major_plan_courses mpc ON mp.id = mpc.plan_id
GROUP BY mp.major_name, mpc.semester
ORDER BY mp.major_name, mpc.semester;

-- 查看所有培养计划详情
SELECT 
  mp.major_name,
  c.name as course_name,
  mpc.semester,
  CASE WHEN mpc.is_required THEN '必修' ELSE '选修' END as course_type
FROM major_plans mp
LEFT JOIN major_plan_courses mpc ON mp.id = mpc.plan_id
LEFT JOIN courses c ON mpc.course_id = c.id
ORDER BY mp.major_name, mpc.semester, c.name;
