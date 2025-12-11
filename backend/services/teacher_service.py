"""
Teacher service for teacher-related operations.
"""
from typing import List, Dict, Any, Optional
from db import db


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
