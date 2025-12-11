"""
Admin service for administrative operations.
"""
from typing import List, Dict, Any, Optional
from db import db
from services.user_service import UserService


class AdminService:
    """Service for admin-related operations."""
    
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
        """Update student information."""
        fields = ['student_no', 'name', 'major']
        updates = []
        params = []
        
        for field in fields:
            if field in data:
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
    def delete_course(course_id: int):
        """Delete a course."""
        db.execute('DELETE FROM courses WHERE id=%s', [course_id])
    
    # ========== Enrollments ========== #
    
    @staticmethod
    def get_enrollments(student_id: Optional[int] = None, 
                       course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all enrollments with optional filtering."""
        sql = '''
            SELECT e.*, s.name AS student_name, c.name AS course_name, t.name AS teacher_name
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
    def delete_enrollment(enrollment_id: int):
        """Delete an enrollment."""
        db.execute('DELETE FROM enrollments WHERE id=%s', [enrollment_id])
    
    # ========== Statistics ========== #
    
    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Get system statistics."""
        counts = db.fetch_one(
            '''
            SELECT
                (SELECT COUNT(*) FROM students) AS students,
                (SELECT COUNT(*) FROM teachers) AS teachers,
                (SELECT COUNT(*) FROM courses) AS courses,
                (SELECT COUNT(*) FROM enrollments) AS enrollments
            '''
        )
        
        course_avg = db.fetch_all(
            '''
            SELECT c.id, c.name, c.course_code, ROUND(AVG(e.grade)::numeric, 2) AS avg_grade
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            GROUP BY c.id, c.name, c.course_code
            ORDER BY c.id
            '''
        )
        
        return {'counts': counts, 'course_avg': course_avg}
