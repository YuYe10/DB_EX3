"""
Admin routes blueprint.
"""
from flask import Blueprint, request, jsonify, send_file
from services import AdminService
from utils import json_response, error_response, validate_fields, require_auth

admin_bp = Blueprint('admin', __name__, url_prefix='/api')


# ========== Students ========== #

@admin_bp.route('/students', methods=['GET', 'POST'])
@require_auth(['admin'])
def students():
    """Get all students or create a new student."""
    if request.method == 'GET':
        major = request.args.get('major')
        keyword = request.args.get('q')
        students = AdminService.get_students(major, keyword)
        return jsonify(students)
    
    # POST - Create student
    payload = request.get_json(force=True)
    
    try:
        validate_fields(payload, ['student_no', 'name'])
    except ValueError as e:
        return error_response(str(e))
    
    student_id = AdminService.create_student(
        payload['student_no'],
        payload['name'],
        payload.get('major', '')
    )
    
    return json_response({'id': student_id}, message='Student created successfully')


@admin_bp.route('/students/<int:student_id>', methods=['PUT', 'DELETE'])
@require_auth(['admin'])
def update_student(student_id: int):
    """Update or delete a student."""
    if request.method == 'DELETE':
        AdminService.delete_student(student_id)
        return json_response(message='Student deleted successfully')
    
    # PUT - Update student
    payload = request.get_json(force=True)
    success = AdminService.update_student(student_id, payload)
    
    if not success:
        return error_response('No fields to update')
    
    return json_response(message='Student updated successfully')


# ========== Teachers ========== #

@admin_bp.route('/teachers', methods=['GET', 'POST'])
@require_auth(['admin'])
def teachers():
    """Get all teachers or create a new teacher."""
    if request.method == 'GET':
        teachers = AdminService.get_teachers()
        return jsonify(teachers)
    
    # POST - Create teacher
    payload = request.get_json(force=True)
    
    try:
        validate_fields(payload, ['teacher_no', 'name'])
    except ValueError as e:
        return error_response(str(e))
    
    teacher_id = AdminService.create_teacher(
        payload['teacher_no'],
        payload['name'],
        payload.get('department', '')
    )
    
    return json_response({'id': teacher_id}, message='Teacher created successfully')


@admin_bp.route('/teachers/<int:teacher_id>', methods=['PUT', 'DELETE'])
@require_auth(['admin'])
def update_teacher(teacher_id: int):
    """Update or delete a teacher."""
    if request.method == 'DELETE':
        AdminService.delete_teacher(teacher_id)
        return json_response(message='Teacher deleted successfully')
    
    # PUT - Update teacher
    payload = request.get_json(force=True)
    success = AdminService.update_teacher(teacher_id, payload)
    
    if not success:
        return error_response('No fields to update')
    
    return json_response(message='Teacher updated successfully')


# ========== Courses ========== #

@admin_bp.route('/courses', methods=['GET', 'POST'])
@require_auth(['admin'])
def courses():
    """Get all courses or create a new course."""
    if request.method == 'GET':
        courses = AdminService.get_courses()
        return jsonify(courses)
    
    # POST - Create course
    payload = request.get_json(force=True)
    
    try:
        validate_fields(payload, ['course_code', 'name'])
    except ValueError as e:
        return error_response(str(e))
    
    course_id = AdminService.create_course(
        payload['course_code'],
        payload['name'],
        payload.get('credit', 0),
        payload.get('capacity', 50),
        payload.get('teacher_id')
    )
    
    return json_response({'id': course_id}, message='Course created successfully')


@admin_bp.route('/courses/<int:course_id>', methods=['PUT', 'DELETE'])
@require_auth(['admin'])
def update_course(course_id: int):
    """Update or delete a course."""
    if request.method == 'DELETE':
        AdminService.delete_course(course_id)
        return json_response(message='Course deleted successfully')
    
    # PUT - Update course
    payload = request.get_json(force=True)
    success = AdminService.update_course(course_id, payload)
    
    if not success:
        return error_response('No fields to update')
    
    return json_response(message='Course updated successfully')


# ========== Enrollments ========== #

@admin_bp.route('/enrollments', methods=['GET', 'POST'])
@require_auth(['admin'])
def enrollments():
    """Get all enrollments or create a new enrollment."""
    if request.method == 'GET':
        student_id = request.args.get('student_id')
        course_id = request.args.get('course_id')
        enrollments = AdminService.get_enrollments(student_id, course_id)
        return jsonify(enrollments)
    
    # POST - Create enrollment
    payload = request.get_json(force=True)
    
    try:
        validate_fields(payload, ['student_id', 'course_id'])
    except ValueError as e:
        return error_response(str(e))
    
    try:
        enrollment_id = AdminService.create_enrollment(
            payload['student_id'],
            payload['course_id'],
            payload.get('status', 'enrolled')
        )
        return json_response({'id': enrollment_id}, message='Enrollment created successfully')
    except Exception as e:
        return error_response(f'Enrollment failed: {str(e)}', status=500)


@admin_bp.route('/enrollments/<int:enrollment_id>/grade', methods=['PUT'])
@require_auth(['admin'])
def set_grade(enrollment_id: int):
    """Set grade for an enrollment."""
    payload = request.get_json(force=True)
    
    if 'grade' not in payload:
        return error_response('Grade is required')
    
    AdminService.set_grade(enrollment_id, payload['grade'])
    return json_response(message='Grade updated successfully')


@admin_bp.route('/enrollments/<int:enrollment_id>', methods=['DELETE'])
@require_auth(['admin'])
def drop_course(enrollment_id: int):
    """Delete an enrollment."""
    AdminService.delete_enrollment(enrollment_id)
    return json_response(message='Enrollment deleted successfully')


# ========== Statistics ========== #

@admin_bp.route('/statistics/overview', methods=['GET'])
@require_auth(['admin'])
def statistics_overview():
    """Get system statistics."""
    stats = AdminService.get_statistics()
    return jsonify(stats)


# ========== Excel Import / Export ========== #

@admin_bp.route('/import/courses', methods=['POST'])
@require_auth(['admin'])
def import_courses():
    """Import courses, students, and enrollments from an Excel file."""
    file = request.files.get('file')
    if not file:
        return error_response('请选择要上传的Excel文件')
    try:
        summary = AdminService.import_courses_excel(file)
        return json_response({'summary': summary}, message='导入完成')
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f'导入失败: {exc}', status=500)


@admin_bp.route('/courses/<int:course_id>/grades/export', methods=['GET'])
@require_auth(['admin'])
def export_course_grades(course_id: int):
    """Export a course's roster and grades as Excel."""
    buffer, filename = AdminService.export_course_grades(course_id)
    if buffer is None:
        return error_response('课程不存在', status=404)
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


# ========== Health Check ========== #

@admin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    from db import db
    try:
        db.fetch_one("SELECT 1")
        return jsonify({'db': True})
    except Exception:
        return jsonify({'db': False}), 503
