"""
Major Plan Service for managing professional training plans.
"""
from typing import List, Dict, Any, Optional
import logging

from app_core.db import db

logger = logging.getLogger(__name__)


class MajorPlanService:
    """Service for managing professional training plans for different majors."""
    
    @staticmethod
    def create_plan(major_name: str, description: str = '') -> Dict[str, Any]:
        """Create a new major training plan."""
        sql = """
            INSERT INTO major_plans (major_name, description)
            VALUES (%s, %s)
            RETURNING id, major_name, description, created_at
        """
        result = db.fetch_one(sql, [major_name, description])
        logger.info(f"✅ Created major plan: {major_name}")
        return result
    
    @staticmethod
    def get_all_plans() -> List[Dict[str, Any]]:
        """Get all major training plans."""
        sql = """
            SELECT id, major_name, description, created_at, updated_at
            FROM major_plans
            ORDER BY major_name
        """
        return db.fetch_all(sql)
    
    @staticmethod
    def get_plan_by_id(plan_id: int) -> Optional[Dict[str, Any]]:
        """Get a major plan by ID."""
        sql = """
            SELECT id, major_name, description, created_at, updated_at
            FROM major_plans
            WHERE id = %s
        """
        return db.fetch_one(sql, [plan_id])
    
    @staticmethod
    def get_plan_by_major(major_name: str) -> Optional[Dict[str, Any]]:
        """Get a major plan by major name."""
        sql = """
            SELECT id, major_name, description, created_at, updated_at
            FROM major_plans
            WHERE major_name = %s
        """
        return db.fetch_one(sql, [major_name])
    
    @staticmethod
    def add_course_to_plan(plan_id: int, course_id: int, semester: int, is_required: bool = True) -> Dict[str, Any]:
        """Add a course to a major plan for a specific semester."""
        sql = """
            INSERT INTO major_plan_courses (plan_id, course_id, semester, is_required)
            VALUES (%s, %s, %s, %s)
            RETURNING id, plan_id, course_id, semester, is_required, created_at
        """
        result = db.fetch_one(sql, [plan_id, course_id, semester, is_required])
        logger.info(f"✅ Added course {course_id} to plan {plan_id} semester {semester}")
        return result
    
    @staticmethod
    def get_plan_courses(plan_id: int) -> List[Dict[str, Any]]:
        """Get all courses in a major plan with their details."""
        sql = """
            SELECT 
                mpc.id,
                mpc.plan_id,
                mpc.course_id,
                mpc.semester,
                mpc.is_required,
                c.course_code,
                c.name AS course_name,
                c.credit,
                t.name AS teacher_name
            FROM major_plan_courses mpc
            JOIN courses c ON mpc.course_id = c.id
            LEFT JOIN teachers t ON c.teacher_id = t.id
            WHERE mpc.plan_id = %s
            ORDER BY mpc.semester, c.name
        """
        return db.fetch_all(sql, [plan_id])
    
    @staticmethod
    def get_courses_by_semester(plan_id: int, semester: int) -> List[Dict[str, Any]]:
        """Get courses required in a specific semester of a plan."""
        sql = """
            SELECT 
                mpc.id,
                mpc.course_id,
                mpc.semester,
                mpc.is_required,
                c.course_code,
                c.name AS course_name,
                c.credit,
                c.capacity,
                t.name AS teacher_name,
                t.teacher_no
            FROM major_plan_courses mpc
            JOIN courses c ON mpc.course_id = c.id
            LEFT JOIN teachers t ON c.teacher_id = t.id
            WHERE mpc.plan_id = %s AND mpc.semester = %s
            ORDER BY c.name
        """
        return db.fetch_all(sql, [plan_id, semester])
    
    @staticmethod
    def remove_course_from_plan(plan_course_id: int) -> bool:
        """Remove a course from a major plan."""
        sql = "DELETE FROM major_plan_courses WHERE id = %s"
        db.execute(sql, [plan_course_id])
        logger.info(f"✅ Removed course from plan: {plan_course_id}")
        return True
    
    @staticmethod
    def update_plan(plan_id: int, major_name: str = None, description: str = None) -> Dict[str, Any]:
        """Update a major plan."""
        updates = []
        params = []
        
        if major_name is not None:
            updates.append("major_name = %s")
            params.append(major_name)
        
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if not updates:
            return MajorPlanService.get_plan_by_id(plan_id)
        
        updates.append("updated_at = NOW()")
        params.append(plan_id)
        
        sql = f"""
            UPDATE major_plans
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, major_name, description, updated_at
        """
        result = db.fetch_one(sql, params)
        logger.info(f"✅ Updated major plan: {plan_id}")
        return result
    
    @staticmethod
    def delete_plan(plan_id: int) -> bool:
        """Delete a major plan and all its courses."""
        sql = "DELETE FROM major_plans WHERE id = %s"
        db.execute(sql, [plan_id])
        logger.info(f"✅ Deleted major plan: {plan_id}")
        return True
    
    @staticmethod
    def get_student_plan_courses(student_id: int, semester: int = None) -> List[Dict[str, Any]]:
        """
        Get courses for a student based on their major and the major plan.
        If semester is provided, only return courses for that semester.
        """
        # First, get the student's major
        student_sql = "SELECT major FROM students WHERE id = %s"
        student = db.fetch_one(student_sql, [student_id])
        
        if not student or not student.get('major'):
            return []
        
        major_name = student['major']
        
        # Get the major plan
        plan = MajorPlanService.get_plan_by_major(major_name)
        if not plan:
            return []
        
        # Get courses from the plan
        if semester is not None:
            courses = MajorPlanService.get_courses_by_semester(plan['id'], semester)
        else:
            courses = MajorPlanService.get_plan_courses(plan['id'])
        
        return courses
    
    @staticmethod
    def get_all_semesters(plan_id: int) -> List[int]:
        """Get all semesters in a major plan."""
        sql = """
            SELECT DISTINCT semester
            FROM major_plan_courses
            WHERE plan_id = %s
            ORDER BY semester
        """
        results = db.fetch_all(sql, [plan_id])
        return [row['semester'] for row in results]
