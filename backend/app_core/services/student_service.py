"""
Student service for student-related operations.
"""
from typing import List, Dict, Any, Optional

from app_core.db import db


class StudentService:
    """Service for student-related operations."""
    
    @staticmethod
    def get_student_info(student_id: int) -> Optional[Dict[str, Any]]:
        """Get student information including major and current semester."""
        return db.fetch_one(
            'SELECT id, student_no, name, major, current_semester FROM students WHERE id = %s',
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
        from app_core.services.major_plan_service import MajorPlanService
        
        plan = MajorPlanService.ensure_plan_exists(student['major'])
        if not plan:
            return []
        
        # Get courses from plan
        if semester is not None:
            courses = MajorPlanService.get_courses_by_semester(plan['id'], semester)
        else:
            courses = MajorPlanService.get_plan_courses(plan['id'])
        
        # If plan has no configured courses, hide the course list
        if not courses:
            return []

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
        from app_core.services.major_plan_service import MajorPlanService
        
        student = StudentService.get_student_info(student_id)
        if not student or not student.get('major'):
            return []
        
        plan = MajorPlanService.ensure_plan_exists(student['major'])
        if not plan:
            return []
        
        return MajorPlanService.get_all_semesters(plan['id'])
    
    @staticmethod
    def get_enrollments(student_id: int) -> List[Dict[str, Any]]:
        """Get student's enrollment records."""
        return db.fetch_all(
            '''
            SELECT e.*, c.name AS course_name, c.course_code, c.credit,
                   t.name AS teacher_name,
                   CASE 
                       WHEN e.ordinary_score IS NOT NULL AND e.final_score IS NOT NULL THEN
                           ROUND(CAST(e.ordinary_score * COALESCE(c.ordinary_weight, 0.5) + 
                                 e.final_score * COALESCE(c.final_weight, 0.5) AS NUMERIC), 2)
                       ELSE e.grade
                   END AS final_grade
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
        
        Validates that:
        1. The course is available in the student's major plan
        2. The course is offered in the student's current semester
        
        Returns:
            New enrollment ID
        
        Raises:
            ValueError: If course not in student's major plan, semester mismatch, or other issues
        """
        from app_core.services.major_plan_service import MajorPlanService
        
        # Get student info and ensure they have a plan
        student = StudentService.get_student_info(student_id)
        if not student or not student.get('major'):
            raise ValueError('Student not found or has no major assigned')
        
        plan = MajorPlanService.ensure_plan_exists(student['major'])
        if not plan:
            raise ValueError(f'No major plan exists for major: {student["major"]}')
        
        # Verify course is in the student's major plan
        plan_course = db.fetch_one(
            'SELECT semester FROM major_plan_courses WHERE plan_id = %s AND course_id = %s',
            [plan['id'], course_id]
        )
        
        if not plan_course:
            raise ValueError(f'Course {course_id} is not available in your major plan')
        
        # Check if course semester matches student's current semester
        if plan_course['semester'] != student['current_semester']:
            raise ValueError(
                f'This course is offered in semester {plan_course["semester"]}, '
                f'but you are currently in semester {student["current_semester"]}'
            )
        
        # Check for duplicate enrollment
        existing = db.fetch_one(
            'SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s',
            [student_id, course_id]
        )
        if existing:
            raise ValueError('You are already enrolled in this course')
        
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
