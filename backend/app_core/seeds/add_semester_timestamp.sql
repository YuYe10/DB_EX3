-- Add semester_updated_at column to students if missing
ALTER TABLE students
ADD COLUMN IF NOT EXISTS semester_updated_at TIMESTAMP DEFAULT NOW();

-- Backfill nulls
UPDATE students
SET semester_updated_at = NOW()
WHERE semester_updated_at IS NULL;
