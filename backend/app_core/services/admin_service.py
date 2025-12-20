"""
Admin service for administrative operations.
"""
from typing import List, Dict, Any, Optional
from io import BytesIO
from datetime import datetime
import pandas as pd

from app_core.db import db
from app_core.services.user_service import UserService


class AdminService:
    """Service for admin-related operations."""

    # ===== Excel Import / Export ===== #

    @staticmethod
    def import_courses_excel(file_stream) -> Dict[str, Any]:
        """Import courses, students, and enrollments from an Excel workbook."""
        try:
            workbook = pd.ExcelFile(file_stream)
        except Exception as exc:  # pragma: no cover - defensive parsing
            raise ValueError(f"无法读取Excel文件: {exc}")

        if 'courses' not in workbook.sheet_names:
            raise ValueError("Excel需包含名称为 'courses' 的工作表")

        summary = {
            'courses_created': 0,
            'courses_skipped': 0,
            'students_created': 0,
            'students_skipped': 0,
            'teachers_created': 0,
            'enrollments_created': 0,
            'enrollments_skipped': 0,
            'errors': []
        }

        # Cache existing IDs
        student_map = {row['student_no']: row['id'] for row in db.fetch_all('SELECT id, student_no FROM students')}
        teacher_map = {row['teacher_no']: row['id'] for row in db.fetch_all('SELECT id, teacher_no FROM teachers')}
        course_map = {row['course_code']: row['id'] for row in db.fetch_all('SELECT id, course_code FROM courses')}

        # Optional helper to coerce numeric values with default fallback
        def _num(value, default):
            if pd.isna(value):
                return default
            try:
                return int(value)
            except Exception:
                try:
                    return float(value)
                except Exception:
                    return default

        # Students sheet (optional)
        if 'students' in workbook.sheet_names:
            students_df = workbook.parse('students').fillna('')
            for _, row in students_df.iterrows():
                student_no = str(row.get('student_no', '')).strip()
                if not student_no:
                    summary['errors'].append('学生行缺少 student_no，已跳过')
                    continue
                if student_no in student_map:
                    summary['students_skipped'] += 1
                    continue
                name = str(row.get('name', '')).strip() or student_no
                major = str(row.get('major', '')).strip()
                student_id = AdminService.create_student(student_no, name, major)
                student_map[student_no] = student_id
                summary['students_created'] += 1

        # Courses sheet (required)
        courses_df = workbook.parse('courses').fillna('')
        for _, row in courses_df.iterrows():
            course_code = str(row.get('course_code', '')).strip()
            name = str(row.get('name', '')).strip()
            if not course_code or not name:
                summary['errors'].append('课程行缺少 course_code 或 name，已跳过')
                continue

            teacher_no = str(row.get('teacher_no', '')).strip()
            teacher_name = str(row.get('teacher_name', '')).strip()
            # 支持从导入名单中提取教师院系，优先使用 teacher_department，其次 department
            teacher_department = str(row.get('teacher_department', '')).strip() or str(row.get('department', '')).strip()
            teacher_id = None
            if teacher_no:
                if teacher_no in teacher_map:
                    teacher_id = teacher_map[teacher_no]
                    # 如果已有教师记录但未填写院系，且本次导入提供了院系，则进行补全
                    if teacher_department:
                        db.execute(
                            """
                            UPDATE teachers
                            SET department=%s
                            WHERE id=%s AND (department IS NULL OR department='')
                            """,
                            [teacher_department, teacher_id]
                        )
                else:
                    t_name = teacher_name or teacher_no
                    teacher_id = AdminService.create_teacher(teacher_no, t_name, teacher_department)
                    teacher_map[teacher_no] = teacher_id
                    summary['teachers_created'] += 1

            credit = _num(row.get('credit', 0), 0)
            capacity = _num(row.get('capacity', 50), 50)

            if course_code in course_map:
                summary['courses_skipped'] += 1
                course_id = course_map[course_code]
            else:
                course_id = AdminService.create_course(course_code, name, credit, capacity, teacher_id)
                course_map[course_code] = course_id
                summary['courses_created'] += 1

        # Enrollments sheet (optional)
        if 'enrollments' in workbook.sheet_names:
            enroll_df = workbook.parse('enrollments').fillna('')
            for _, row in enroll_df.iterrows():
                course_code = str(row.get('course_code', '')).strip()
                student_no = str(row.get('student_no', '')).strip()
                if not course_code or not student_no:
                    summary['errors'].append('选课行缺少 course_code 或 student_no，已跳过')
                    continue
                if course_code not in course_map:
                    summary['errors'].append(f'课程 {course_code} 未找到，选课跳过')
                    continue
                if student_no not in student_map:
                    # Create missing student on the fly
                    student_name = str(row.get('student_name', '')).strip() or student_no
                    major = str(row.get('major', '')).strip()
                    student_id = AdminService.create_student(student_no, student_name, major)
                    student_map[student_no] = student_id
                    summary['students_created'] += 1
                course_id = course_map[course_code]
                student_id = student_map[student_no]

                exists = db.fetch_one(
                    'SELECT id FROM enrollments WHERE student_id=%s AND course_id=%s',
                    [student_id, course_id]
                )
                if exists:
                    summary['enrollments_skipped'] += 1
                    continue

                grade_val = row.get('grade', None)
                grade = None if pd.isna(grade_val) else grade_val
                status = str(row.get('status', 'enrolled')).strip() or 'enrolled'

                db.execute(
                    'INSERT INTO enrollments (student_id, course_id, status, grade) VALUES (%s, %s, %s, %s)',
                    [student_id, course_id, status, grade]
                )
                summary['enrollments_created'] += 1

        return summary

    @staticmethod
    def export_course_grades(course_id: int):
        """Export a course's roster and grades to an Excel workbook."""
        course = db.fetch_one(
            '''
            SELECT c.*, t.name AS teacher_name, t.teacher_no
            FROM courses c
            LEFT JOIN teachers t ON c.teacher_id = t.id
            WHERE c.id = %s
            ''',
            [course_id]
        )
        if not course:
            return None, None

        # Aggregate stats for the course
        course_stats = db.fetch_one(
            '''
            SELECT 
                COUNT(e.id) AS enrolled_count,
                ROUND(AVG(COALESCE(e.final_grade, e.grade))::numeric, 2) AS avg_grade,
                ROUND(
                    (SUM(CASE WHEN COALESCE(e.final_grade, e.grade) >= 60 THEN 1 ELSE 0 END)::numeric
                        / NULLIF(COUNT(e.id), 0)) * 100, 2
                ) AS pass_rate,
                ROUND(
                    (SUM(CASE WHEN COALESCE(e.final_grade, e.grade) >= 90 THEN 1 ELSE 0 END)::numeric
                        / NULLIF(COUNT(e.id), 0)) * 100, 2
                ) AS excellent_rate
            FROM enrollments e
            WHERE e.course_id = %s
            ''',
            [course_id]
        ) or {}

        enrollments = db.fetch_all(
            '''
            SELECT 
                s.student_no, 
                s.name AS student_name, 
                s.major, 
                COALESCE(e.final_grade, e.grade) AS grade, 
                e.status
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            WHERE e.course_id = %s
            ORDER BY s.student_no
            ''',
            [course_id]
        )

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Course info with Chinese headers
            course_df = pd.DataFrame([{
                '课程号': course.get('course_code'),
                '课程名': course.get('name'),
                '学分': course.get('credit'),
                '容量': course.get('capacity'),
                '授课教师': course.get('teacher_name'),
                '教师工号': course.get('teacher_no'),
                '选课人数': course_stats.get('enrolled_count', 0),
                '平均成绩': course_stats.get('avg_grade'),
                '及格率(%)': course_stats.get('pass_rate'),
                '优秀率(%)': course_stats.get('excellent_rate'),
            }])
            course_df.to_excel(writer, sheet_name='课程信息', index=False)

            # Enrollment/grade data with Chinese headers
            grades_df = pd.DataFrame(enrollments)
            if not grades_df.empty:
                grades_df = grades_df.rename(columns={
                    'student_no': '学号',
                    'student_name': '姓名',
                    'major': '专业',
                    'grade': '成绩',
                    'status': '状态'
                })
            else:  # ensure headers exist even when empty
                grades_df = pd.DataFrame(columns=['学号', '姓名', '专业', '成绩', '状态'])
            grades_df.to_excel(writer, sheet_name='成绩名单', index=False)
        buffer.seek(0)

        teacher_part = course.get('teacher_name') or '未指定教师'
        course_part = course.get('name') or f'课程{course_id}'
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        safe_course = course_part.replace('/', '-')
        safe_teacher = teacher_part.replace('/', '-')
        filename = f"{safe_course}-{safe_teacher}-{timestamp}.xlsx"
        return buffer, filename
    
    # ========== Students ========== #
    
    @staticmethod
    def get_students(major: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all students with optional filtering."""
        sql = 'SELECT * FROM students WHERE 1=1'
        params = []
        
        if major:
            sql += ' AND major ILIKE %s'
            params.append(f'%{major}%')
        if keyword:
            sql += ' AND (name ILIKE %s OR student_no ILIKE %s)'
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        sql += ' ORDER BY id DESC'
        return db.fetch_all(sql, params)
    
    @staticmethod
    def create_student(student_no: str, name: str, major: str = '') -> int:
        """Create a new student and associated user account."""
        student_id = db.execute_returning(
            'INSERT INTO students (student_no, name, major) VALUES (%s, %s, %s) RETURNING id',
            [student_no, name, major]
        )
        
        # Create user account
        UserService.create_user(student_no, f"s{student_no}", 'student', student_id)
        
        return student_id
    
    @staticmethod
    def update_student(student_id: int, data: Dict[str, Any]) -> bool:
        """Update student information including current_semester."""
        fields = ['student_no', 'name', 'major', 'current_semester']
        updates = []
        params = []

        for field in fields:
            if field in data:
                if field == 'current_semester':
                    try:
                        sem_val = int(data[field])
                    except (TypeError, ValueError):
                        continue
                    if sem_val < 1 or sem_val > 8:
                        continue
                    updates.append("current_semester=%s")
                    params.append(sem_val)
                    updates.append("semester_updated_at=NOW()")
                else:
                    updates.append(f"{field}=%s")
                    params.append(data[field])

        if not updates:
            return False

        params.append(student_id)
        db.execute(f"UPDATE students SET {', '.join(updates)} WHERE id=%s", params)
        return True
    
    @staticmethod
    def delete_student(student_id: int):
        """Delete a student."""
        db.execute('DELETE FROM students WHERE id=%s', [student_id])
    
    # ========== Teachers ========== #
    
    @staticmethod
    def get_teachers() -> List[Dict[str, Any]]:
        """Get all teachers."""
        return db.fetch_all('SELECT * FROM teachers ORDER BY id DESC')
    
    @staticmethod
    def create_teacher(teacher_no: str, name: str, department: str = '') -> int:
        """Create a new teacher and associated user account."""
        teacher_id = db.execute_returning(
            'INSERT INTO teachers (teacher_no, name, department) VALUES (%s, %s, %s) RETURNING id',
            [teacher_no, name, department]
        )
        
        # Create user account
        UserService.create_user(teacher_no, f"t{teacher_no}", 'teacher', teacher_id)
        
        return teacher_id
    
    @staticmethod
    def update_teacher(teacher_id: int, data: Dict[str, Any]) -> bool:
        """Update teacher information."""
        fields = ['teacher_no', 'name', 'department']
        updates = []
        params = []
        
        for field in fields:
            if field in data:
                updates.append(f"{field}=%s")
                params.append(data[field])
        
        if not updates:
            return False
        
        params.append(teacher_id)
        db.execute(f"UPDATE teachers SET {', '.join(updates)} WHERE id=%s", params)
        return True
    
    @staticmethod
    def delete_teacher(teacher_id: int):
        """Delete a teacher."""
        db.execute('DELETE FROM teachers WHERE id=%s', [teacher_id])
    
    # ========== Courses ========== #
    
    @staticmethod
    def get_courses() -> List[Dict[str, Any]]:
        """Get all courses with teacher information."""
        return db.fetch_all(
            '''
            SELECT c.*, t.name AS teacher_name
            FROM courses c
            LEFT JOIN teachers t ON c.teacher_id = t.id
            ORDER BY c.id DESC
            '''
        )
    
    @staticmethod
    def create_course(course_code: str, name: str, credit: int = 0, 
                     capacity: int = 50, teacher_id: Optional[int] = None) -> int:
        """Create a new course."""
        return db.execute_returning(
            '''
            INSERT INTO courses (course_code, name, credit, capacity, teacher_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            ''',
            [course_code, name, credit, capacity, teacher_id]
        )
    
    @staticmethod
    def update_course(course_id: int, data: Dict[str, Any]) -> bool:
        """Update course information."""
        fields = ['course_code', 'name', 'credit', 'capacity', 'teacher_id']
        updates = []
        params = []
        
        for field in fields:
            if field in data:
                updates.append(f"{field}=%s")
                params.append(data[field])
        
        if not updates:
            return False
        
        params.append(course_id)
        db.execute(f"UPDATE courses SET {', '.join(updates)} WHERE id=%s", params)
        return True
    
    @staticmethod
    def update_course_weights(course_id: int, ordinary_weight: float, final_weight: float) -> bool:
        """Update course grade weights.
        
        Args:
            course_id: The course ID to update
            ordinary_weight: 平时成绩占比 (0-1)
            final_weight: 期末成绩占比 (0-1)
        
        Returns:
            bool: True if update successful, False otherwise
        
        Raises:
            ValueError: If weights are invalid or don't sum to 1
        """
        # Validate weights
        if ordinary_weight < 0 or ordinary_weight > 1:
            raise ValueError('平时成绩占比必须在0-1之间')
        if final_weight < 0 or final_weight > 1:
            raise ValueError('期末成绩占比必须在0-1之间')
        
        total_weight = round(float(ordinary_weight) + float(final_weight), 2)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f'占比和必须为1，当前为{total_weight}')
        
        # Update course weights
        db.execute(
            'UPDATE courses SET ordinary_weight=%s, final_weight=%s WHERE id=%s',
            [ordinary_weight, final_weight, course_id]
        )
        
        # Recalculate final_grade for all enrollments in this course
        db.execute(
            '''
            UPDATE enrollments
            SET final_grade = CASE
                WHEN ordinary_score IS NOT NULL AND final_score IS NOT NULL
                THEN ROUND((ordinary_score * %s + final_score * %s)::numeric, 1)
                ELSE NULL
            END
            WHERE course_id = %s
            ''',
            [ordinary_weight, final_weight, course_id]
        )
        
        return True
    
    @staticmethod
    def delete_course(course_id: int):
        """Delete a course."""
        db.execute('DELETE FROM courses WHERE id=%s', [course_id])
    
    # ========== Enrollments ========== #
    
    @staticmethod
    def get_enrollments(student_id: Optional[int] = None, 
                       course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all enrollments with optional filtering."""
        sql = '''
            SELECT e.*, 
                   s.name AS student_name, s.student_no, s.major,
                   c.name AS course_name, c.ordinary_weight AS course_ordinary_weight, c.final_weight AS course_final_weight,
                   t.name AS teacher_name
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            LEFT JOIN teachers t ON c.teacher_id = t.id
            WHERE 1=1
        '''
        params = []
        
        if student_id:
            sql += ' AND e.student_id=%s'
            params.append(student_id)
        if course_id:
            sql += ' AND e.course_id=%s'
            params.append(course_id)
        
        sql += ' ORDER BY e.id DESC'
        return db.fetch_all(sql, params)
    
    @staticmethod
    def create_enrollment(student_id: int, course_id: int, status: str = 'enrolled') -> int:
        """Create a new enrollment."""
        return db.execute_returning(
            'INSERT INTO enrollments (student_id, course_id, status) VALUES (%s, %s, %s) RETURNING id',
            [student_id, course_id, status]
        )
    
    @staticmethod
    def set_grade(enrollment_id: int, grade: float):
        """Set grade for an enrollment."""
        db.execute('UPDATE enrollments SET grade=%s WHERE id=%s', [grade, enrollment_id])
    
    @staticmethod
    def update_student_grades(enrollment_id: int, data: Dict[str, Any]) -> bool:
        """Update student grades including ordinary_score and final_score.
        Weights are now stored at course level, not enrollment level.
        
        Args:
            enrollment_id: The enrollment ID to update
            data: Dictionary containing:
                - ordinary_score: 平时成绩 (0-100)
                - final_score: 期末成绩 (0-100)
        
        Returns:
            bool: True if update successful, False otherwise
        """
        # Get the enrollment to find course_id
        enrollment = db.fetch_one('SELECT course_id FROM enrollments WHERE id=%s', [enrollment_id])
        if not enrollment:
            return False
        
        course_id = enrollment['course_id']
        
        # Get course weights
        course = db.fetch_one('SELECT ordinary_weight, final_weight FROM courses WHERE id=%s', [course_id])
        ordinary_weight = float(course['ordinary_weight']) if course and course['ordinary_weight'] is not None else 0.5
        final_weight = float(course['final_weight']) if course and course['final_weight'] is not None else 0.5
        
        updates = []
        params = []
        
        # Process ordinary_score
        ordinary_score = None
        if 'ordinary_score' in data:
            ordinary_score = data['ordinary_score']
            if ordinary_score is not None:
                try:
                    ordinary_score = float(ordinary_score)
                    if ordinary_score < 0 or ordinary_score > 100:
                        raise ValueError('平时成绩必须在0-100之间')
                except (ValueError, TypeError) as e:
                    raise ValueError(f'平时成绩格式错误: {str(e)}')
            updates.append('ordinary_score=%s')
            params.append(ordinary_score)
        
        # Process final_score
        final_score = None
        if 'final_score' in data:
            final_score = data['final_score']
            if final_score is not None:
                try:
                    final_score = float(final_score)
                    if final_score < 0 or final_score > 100:
                        raise ValueError('期末成绩必须在0-100之间')
                except (ValueError, TypeError) as e:
                    raise ValueError(f'期末成绩格式错误: {str(e)}')
            updates.append('final_score=%s')
            params.append(final_score)
        
        if not updates:
            return False
        
        # Calculate final_grade if both scores are provided
        if ordinary_score is not None and final_score is not None:
            final_grade = float(ordinary_score) * ordinary_weight + float(final_score) * final_weight
            updates.append('final_grade=%s')
            params.append(round(final_grade, 1))
        
        params.append(enrollment_id)
        db.execute(f"UPDATE enrollments SET {', '.join(updates)} WHERE id=%s", params)
        return True
    
    @staticmethod
    def delete_enrollment(enrollment_id: int):
        """Delete an enrollment."""
        db.execute('DELETE FROM enrollments WHERE id=%s', [enrollment_id])
    
    # ========== Statistics ========== #
    
    @staticmethod
    @staticmethod
    def _fetch_course_stats(course_code: Optional[str] = None, course_name: Optional[str] = None):
        """Internal helper to compute per-course statistics with optional filters."""
        code_pattern = f"%{course_code}%" if course_code else None
        name_pattern = f"%{course_name}%" if course_name else None

        return db.fetch_all(
            '''
            SELECT 
                c.id, 
                c.name, 
                c.course_code, 
                COUNT(e.id) AS enrolled_count,
                ROUND(AVG(COALESCE(e.final_grade, e.grade))::numeric, 2) AS avg_grade,
                ROUND(
                    (SUM(CASE WHEN COALESCE(e.final_grade, e.grade) >= 60 THEN 1 ELSE 0 END)::numeric
                        / NULLIF(COUNT(e.id), 0)) * 100, 2
                ) AS pass_rate,
                ROUND(
                    (SUM(CASE WHEN COALESCE(e.final_grade, e.grade) >= 90 THEN 1 ELSE 0 END)::numeric
                        / NULLIF(COUNT(e.id), 0)) * 100, 2
                ) AS excellent_rate
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            WHERE (%s IS NULL OR c.course_code ILIKE %s)
              AND (%s IS NULL OR c.name ILIKE %s)
            GROUP BY c.id, c.name, c.course_code
            ORDER BY c.id
            ''',
            [code_pattern, code_pattern, name_pattern, name_pattern]
        )

    @staticmethod
    def get_statistics(course_code: Optional[str] = None, course_name: Optional[str] = None) -> Dict[str, Any]:
        """Get system statistics with optional course filters.

        Also persists pass_rate and excellent_rate back to courses table.
        """
        counts = db.fetch_one(
            '''
            SELECT
                (SELECT COUNT(*) FROM students) AS students,
                (SELECT COUNT(*) FROM teachers) AS teachers,
                (SELECT COUNT(*) FROM courses) AS courses,
                (SELECT COUNT(*) FROM enrollments) AS enrollments
            '''
        )

        # Compute full stats (without filters) and persist rates to courses table
        full_course_stats = AdminService._fetch_course_stats()
        for c in full_course_stats:
            db.execute(
                'UPDATE courses SET pass_rate=%s, excellent_rate=%s WHERE id=%s',
                [c.get('pass_rate'), c.get('excellent_rate'), c['id']]
            )

        # Apply filters for the response payload (if provided)
        course_stats = (
            full_course_stats
            if not course_code and not course_name
            else AdminService._fetch_course_stats(course_code, course_name)
        )
        
        return {'counts': counts, 'course_avg': course_stats}
