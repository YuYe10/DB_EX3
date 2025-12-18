"""
Teacher service for teacher-related operations.
"""
from typing import List, Dict, Any, Optional
from typing import Tuple
from io import BytesIO
from datetime import datetime
from app_core.db import db
from app_core.services.admin_service import AdminService


class TeacherService:
    """Service for teacher-related operations."""
    
    @staticmethod
    def get_courses(teacher_id: int) -> List[Dict[str, Any]]:
        """Get courses taught by the teacher."""
        return db.fetch_all(
            '''
            SELECT c.*,
                   (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) AS enrolled_count
            FROM courses c
            WHERE c.teacher_id = %s
            ORDER BY c.id DESC
            ''',
            [teacher_id]
        )
    
    @staticmethod
    def get_course_students(teacher_id: int, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get student list for a course (only if teacher teaches it).
        
        Returns:
            List of students if teacher teaches the course, None otherwise
        """
        # Verify teacher teaches this course
        course = db.fetch_one("SELECT * FROM courses WHERE id=%s", [course_id])
        if not course or course['teacher_id'] != teacher_id:
            return None
        
        return db.fetch_all(
            '''
            SELECT e.*, s.name AS student_name, s.student_no, s.major
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            WHERE e.course_id = %s
            ORDER BY s.student_no
            ''',
            [course_id]
        )
    
    @staticmethod
    def set_grade(teacher_id: int, enrollment_id: int, grade: float) -> bool:
        """
        Set grade for a student (only if teacher teaches the course).
        
        Returns:
            True if successful, False if enrollment not found or access denied
        """
        # Verify teacher teaches this course
        enrollment = db.fetch_one(
            '''
            SELECT e.*, c.teacher_id
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.id = %s
            ''',
            [enrollment_id]
        )
        
        if not enrollment or enrollment['teacher_id'] != teacher_id:
            return False
        
        db.execute('UPDATE enrollments SET grade=%s WHERE id=%s', [grade, enrollment_id])
        return True

    # ===== Export ===== #
    @staticmethod
    def export_course_grades(teacher_id: int, course_id: int) -> Tuple[Any, Any]:
        """Export grades for a course taught by the teacher."""
        course = db.fetch_one('SELECT id, teacher_id FROM courses WHERE id=%s', [course_id])
        if not course or course['teacher_id'] != teacher_id:
            return None, None
        return AdminService.export_course_grades(course_id)

    @staticmethod
    def sample_course_roster() -> Tuple[Any, str]:
        """Generate an in-memory sample roster Excel for teachers."""
        import pandas as pd

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            course_df = pd.DataFrame([
                {
                    'course_code': 'C900',
                    'name': '算法设计',
                    'credit': 3,
                    'capacity': 80,
                }
            ])
            students_df = pd.DataFrame([
                {'student_no': 'S1001', 'name': '张同学', 'major': '计算机'},
                {'student_no': 'S1002', 'name': '李同学', 'major': '软件工程'},
                {'student_no': 'S1003', 'name': '王同学', 'major': '人工智能'},
            ])
            course_df.to_excel(writer, sheet_name='course', index=False)
            students_df.to_excel(writer, sheet_name='students', index=False)
        buffer.seek(0)
        filename = f"课程名单示例-{datetime.now().strftime('%Y%m%d-%H%M%S')}.xlsx"
        return buffer, filename

    # ===== Import roster (teacher) ===== #
    @staticmethod
    def import_course_roster(teacher_id: int, file_stream) -> Dict[str, Any]:
        """Teacher imports a course roster Excel and binds it to themselves."""
        import pandas as pd  # local import to avoid heavy module at import time
        try:
            workbook = pd.ExcelFile(file_stream)
        except Exception as exc:
            raise ValueError(f"无法读取Excel文件: {exc}")

        if 'course' not in workbook.sheet_names:
            raise ValueError("Excel需包含名称为 'course' 的工作表，提供课程信息")
        if 'students' not in workbook.sheet_names:
            raise ValueError("Excel需包含名称为 'students' 的工作表，提供学生名单")

        summary = {
            'course_created': 0,
            'course_updated': 0,
            'students_created': 0,
            'students_skipped': 0,
            'enrollments_created': 0,
            'enrollments_skipped': 0,
            'errors': []
        }

        course_df = workbook.parse('course').fillna('')
        if course_df.empty:
            raise ValueError("'course' 工作表为空，至少需要一行课程信息")
        course_row = course_df.iloc[0]
        course_code = str(course_row.get('course_code', '')).strip()
        course_name = str(course_row.get('name', '')).strip()
        credit = course_row.get('credit', 0)
        capacity = course_row.get('capacity', 50)

        def _num(value, default):
            try:
                if pd.isna(value):
                    return default
            except Exception:
                pass
            try:
                return int(value)
            except Exception:
                try:
                    return float(value)
                except Exception:
                    return default

        credit = _num(credit, 0)
        capacity = _num(capacity, 50)

        if not course_code or not course_name:
            raise ValueError("course_code 与 name 为必填")

        existing = db.fetch_one('SELECT id, teacher_id FROM courses WHERE course_code=%s', [course_code])
        if existing and existing['teacher_id'] and existing['teacher_id'] != teacher_id:
            raise ValueError("该课程号已绑定其他教师，无法导入")

        if existing:
            course_id = existing['id']
            db.execute(
                'UPDATE courses SET name=%s, credit=%s, capacity=%s, teacher_id=%s WHERE id=%s',
                [course_name, credit, capacity, teacher_id, course_id]
            )
            summary['course_updated'] += 1
        else:
            course_id = AdminService.create_course(course_code, course_name, credit, capacity, teacher_id)
            summary['course_created'] += 1

        # cache students
        student_map = {row['student_no']: row['id'] for row in db.fetch_all('SELECT id, student_no FROM students')}

        students_df = workbook.parse('students').fillna('')
        for _, row in students_df.iterrows():
            student_no = str(row.get('student_no', '')).strip()
            if not student_no:
                summary['errors'].append('学生行缺少 student_no，已跳过')
                continue
            if student_no in student_map:
                student_id = student_map[student_no]
                summary['students_skipped'] += 1
            else:
                name = str(row.get('name', '')).strip() or student_no
                major = str(row.get('major', '')).strip()
                student_id = AdminService.create_student(student_no, name, major)
                student_map[student_no] = student_id
                summary['students_created'] += 1

            exists = db.fetch_one(
                'SELECT id FROM enrollments WHERE student_id=%s AND course_id=%s',
                [student_id, course_id]
            )
            if exists:
                summary['enrollments_skipped'] += 1
                continue
            db.execute(
                'INSERT INTO enrollments (student_id, course_id, status) VALUES (%s, %s, %s)',
                [student_id, course_id, 'enrolled']
            )
            summary['enrollments_created'] += 1

        summary['course_id'] = course_id
        summary['course_code'] = course_code
        summary['course_name'] = course_name
        return summary
