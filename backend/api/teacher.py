"""
Teacher routes blueprint.
"""
from flask import Blueprint, request, session
from services import TeacherService
from utils import json_response, error_response, require_auth

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')


@teacher_bp.route('/courses', methods=['GET'])
@require_auth(['teacher'])
def get_courses():
    """Get courses taught by current teacher."""
    courses = TeacherService.get_courses(session['ref_id'])
    return json_response(courses)


@teacher_bp.route('/courses/<int:course_id>/students', methods=['GET'])
@require_auth(['teacher'])
def get_course_students(course_id: int):
    """Get student list for a specific course."""
    students = TeacherService.get_course_students(session['ref_id'], course_id)
    
    if students is None:
        return error_response('Course not found or access denied', status=404)
    
    return json_response(students)


@teacher_bp.route('/enrollments/<int:enrollment_id>/grade', methods=['PUT'])
@require_auth(['teacher'])
def set_grade(enrollment_id: int):
    """Set grade for a student."""
    payload = request.get_json(force=True)
    
    if 'grade' not in payload:
        return error_response('Grade is required')
    
    success = TeacherService.set_grade(session['ref_id'], enrollment_id, payload['grade'])
    
    if not success:
        return error_response('Enrollment not found or access denied', status=404)
    
    return json_response(message='Grade updated successfully')
