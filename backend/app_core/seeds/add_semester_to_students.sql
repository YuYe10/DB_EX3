-- 为 students 表添加 current_semester 字段的迁移脚本
-- 如果字段已存在，会被忽略

-- 检查是否已有 current_semester 列，如果没有则添加
ALTER TABLE students
ADD COLUMN IF NOT EXISTS current_semester INT DEFAULT 1
CHECK (current_semester >= 1 AND current_semester <= 8);

-- 为现有学生分配默认学期（如果尚未分配）
UPDATE students
SET current_semester = 1
WHERE current_semester IS NULL OR current_semester = 0;

-- 可选：根据学生编号散列分配学期以获得多样性
-- 取消注释以下行以使用基于学生ID的伪随机分配
-- UPDATE students
-- SET current_semester = ((id - 1) % 4) + 1
-- WHERE current_semester = 1;
