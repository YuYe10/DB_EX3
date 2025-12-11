"""
Student service for student-related operations.
"""
from typing import List, Dict, Any
from db import db


class StudentService:
    """Service for student-related operations."""
    
    @staticmethod
    def get_available_courses(student_id: int) -> List[Dict[str, Any]]:
        """Get all courses available for enrollment (not yet enrolled)."""
        return db.fetch_all(
            '''
            SELECT c.*, t.name AS teacher_name,
                   (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) AS enrolled_count
            FROM courses c
            LEFT JOIN teachers t ON c.teacher_id = t.id
            WHERE c.id NOT IN (
                SELECT course_id FROM enrollments WHERE student_id = %s
            )
            ORDER BY c.id DESC
            ''',
            [student_id]
        )
    
    @staticmethod
    def get_enrollments(student_id: int) -> List[Dict[str, Any]]:
        """Get student's enrollment records."""
        return db.fetch_all(
            '''
            SELECT e.*, c.name AS course_name, c.course_code, c.credit,
                   t.name AS teacher_name
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            LEFT JOIN teachers t ON c.teacher_id = t.id
            WHERE e.student_id = %s
            ORDER BY e.id DESC
            ''',
            [student_id]
        )
    
    @staticmethod
    def enroll_course(student_id: int, course_id: int) -> int:
        """
        Enroll student in a course.
        
        Returns:
            New enrollment ID
        """
        return db.execute_returning(
            'INSERT INTO enrollments (student_id, course_id, status) VALUES (%s, %s, %s) RETURNING id',
            [student_id, course_id, 'enrolled']
        )
    
    @staticmethod
    def drop_course(student_id: int, enrollment_id: int) -> bool:
        """
        Drop a course (student can only drop their own enrollments).
        
        Returns:
            True if successful, False if enrollment not found or access denied
        """
        # Verify ownership
        enrollment = db.fetch_one("SELECT * FROM enrollments WHERE id=%s", [enrollment_id])
        if not enrollment or enrollment['student_id'] != student_id:
            return False
        
        db.execute('DELETE FROM enrollments WHERE id=%s', [enrollment_id])
        return True
