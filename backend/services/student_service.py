"""
Student service for student-related operations.
"""
from typing import List, Dict, Any, Optional
from db import db


class StudentService:
    """Service for student-related operations."""
    
    @staticmethod
    def get_student_info(student_id: int) -> Optional[Dict[str, Any]]:
        """Get student information including major."""
        return db.fetch_one(
            'SELECT id, student_no, name, major FROM students WHERE id = %s',
            [student_id]
        )
    
    @staticmethod
    def get_available_courses(student_id: int, semester: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get courses available for enrollment based on student's major training plan.
        If semester is provided, only return courses for that semester.
        """
        # Get student info
        student = StudentService.get_student_info(student_id)
        if not student or not student.get('major'):
            return []
        
        # Get major plan
        from services.major_plan_service import MajorPlanService
        
        plan = MajorPlanService.get_plan_by_major(student['major'])
        if not plan:
            # If no plan exists for this major, return all available courses
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
        
        # Get courses from plan
        if semester is not None:
            courses = MajorPlanService.get_courses_by_semester(plan['id'], semester)
        else:
            courses = MajorPlanService.get_plan_courses(plan['id'])
        
        # Filter out already enrolled courses
        enrolled_sql = 'SELECT course_id FROM enrollments WHERE student_id = %s'
        enrolled = db.fetch_all(enrolled_sql, [student_id])
        enrolled_ids = {e['course_id'] for e in enrolled}
        
        # Add enrollment count
        for course in courses:
            enrollment_count = db.fetch_one(
                'SELECT COUNT(*) as count FROM enrollments WHERE course_id = %s',
                [course['course_id']]
            )
            course['enrolled_count'] = enrollment_count['count'] if enrollment_count else 0
            course['already_enrolled'] = course['course_id'] in enrolled_ids
        
        return courses
    
    @staticmethod
    def get_available_semesters(student_id: int) -> List[int]:
        """Get all available semesters for student's major plan."""
        from services.major_plan_service import MajorPlanService
        
        student = StudentService.get_student_info(student_id)
        if not student or not student.get('major'):
            return []
        
        plan = MajorPlanService.get_plan_by_major(student['major'])
        if not plan:
            return []
        
        return MajorPlanService.get_all_semesters(plan['id'])
    
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
