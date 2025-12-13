"""
Student routes blueprint.
"""
from flask import Blueprint, request, session, jsonify
from services import StudentService
from utils import json_response, error_response, validate_fields, require_auth

student_bp = Blueprint('student', __name__, url_prefix='/api/student')


@student_bp.route('/courses/available', methods=['GET'])
@require_auth(['student'])
def get_available_courses():
    """Get all courses available for enrollment."""
    courses = StudentService.get_available_courses(session['ref_id'])
    # Frontend expects a plain array, not a wrapped payload
    return jsonify(courses)


@student_bp.route('/enrollments', methods=['GET', 'POST'])
@require_auth(['student'])
def enrollments():
    """Get student's enrollments or enroll in a course."""
    student_id = session['ref_id']
    
    if request.method == 'GET':
        enrollments = StudentService.get_enrollments(student_id)
        # Frontend expects a plain array, not a wrapped payload
        return jsonify(enrollments)
    
    # POST - Enroll in course
    payload = request.get_json(force=True)
    
    try:
        validate_fields(payload, ['course_id'])
    except ValueError as e:
        return error_response(str(e))
    
    try:
        enrollment_id = StudentService.enroll_course(student_id, payload['course_id'])
        return json_response({'id': enrollment_id}, message='Enrolled successfully')
    except Exception as e:
        return error_response(f'Enrollment failed: {str(e)}', status=500)


@student_bp.route('/enrollments/<int:enrollment_id>', methods=['DELETE'])
@require_auth(['student'])
def drop_course(enrollment_id: int):
    """Drop a course."""
    success = StudentService.drop_course(session['ref_id'], enrollment_id)
    
    if not success:
        return error_response('Enrollment not found or access denied', status=404)
    
    return json_response(message='Course dropped successfully')
