"""
Admin routes blueprint.
"""
from flask import Blueprint, request, jsonify, send_file

from app_core.services import AdminService, MajorPlanService
from app_core.utils import json_response, error_response, validate_fields, require_auth
from app_core.utils.validators import validate_major_plan, validate_plan_course, validate_semester

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
    
    try:
        credit = float(payload.get('credit', 0))
        capacity = int(payload.get('capacity', 50))
        if credit < 0:
            return error_response('学分不能为负')
        if capacity <= 0:
            return error_response('容量必须大于0')
    except (ValueError, TypeError):
        return error_response('学分与容量必须为数字')
    
    course_id = AdminService.create_course(
        payload['course_code'],
        payload['name'],
        credit,
        capacity,
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
        return error_response('成绩为必填')
    
    try:
        grade = float(payload['grade'])
        if grade < 0 or grade > 100:
            return error_response('成绩必须在0-100之间')
    except (ValueError, TypeError):
        return error_response('成绩必须为数字')
    
    AdminService.set_grade(enrollment_id, grade)
    return json_response(message='Grade updated successfully')


@admin_bp.route('/enrollments/<int:enrollment_id>/grades', methods=['PUT'])
@require_auth(['admin'])
def update_student_grades(enrollment_id: int):
    """Update student grades including ordinary_score, final_score, and weights.
    
    Expected payload:
    {
        "ordinary_score": 80,    # 平时成绩 (0-100)
        "final_score": 85,       # 期末成绩 (0-100)
        "ordinary_weight": 0.4,  # 平时成绩占比 (0-1)
        "final_weight": 0.6      # 期末成绩占比 (0-1)
    }
    
    Notes:
    - ordinary_weight and final_weight must sum to 1
    - If only one weight is provided, the other is calculated automatically
    - final_grade is automatically calculated as: ordinary_score * ordinary_weight + final_score * final_weight
    """
    payload = request.get_json(force=True)
    
    try:
        success = AdminService.update_student_grades(enrollment_id, payload)
        if not success:
            return error_response('No fields to update')
        return json_response(message='Student grades updated successfully')
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f'Update failed: {str(e)}', status=500)



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
    from app_core.db import db
    try:
        db.fetch_one("SELECT 1")
        return jsonify({'db': True})
    except Exception:
        return jsonify({'db': False}), 503


# ========== Major Plans ========== #

@admin_bp.route('/major-plans', methods=['GET', 'POST'])
@require_auth(['admin'])
def major_plans():
    """Get all major plans or create a new one."""
    if request.method == 'GET':
        plans = MajorPlanService.get_all_plans()
        return jsonify(plans)
    
    # POST - Create major plan
    payload = request.get_json(force=True)
    
    try:
        validate_major_plan(payload)
    except ValueError as e:
        return error_response(str(e))
    
    existing = MajorPlanService.get_plan_by_major(payload['major_name'])
    if existing:
        return error_response(f"Major plan for '{payload['major_name']}' already exists", status=409)
    
    plan = MajorPlanService.create_plan(
        payload['major_name'],
        payload.get('description', '')
    )
    
    # json_response already returns (Response, status); avoid wrapping in another tuple
    return json_response(plan, message='Major plan created successfully', status=201)


@admin_bp.route('/major-plans/<int:plan_id>', methods=['GET', 'PUT', 'DELETE'])
@require_auth(['admin'])
def manage_major_plan(plan_id: int):
    """Get, update, or delete a major plan."""
    plan = MajorPlanService.get_plan_by_id(plan_id)
    if not plan:
        return error_response('Major plan not found', status=404)
    
    if request.method == 'GET':
        # Return plan with all its courses
        plan['courses'] = MajorPlanService.get_plan_courses(plan_id)
        plan['semesters'] = MajorPlanService.get_all_semesters(plan_id)
        return jsonify(plan)
    
    if request.method == 'DELETE':
        MajorPlanService.delete_plan(plan_id)
        return json_response(message='Major plan deleted successfully')
    
    # PUT - Update major plan
    payload = request.get_json(force=True)
    updated_plan = MajorPlanService.update_plan(
        plan_id,
        payload.get('major_name'),
        payload.get('description')
    )
    return json_response(updated_plan, message='Major plan updated successfully')


@admin_bp.route('/major-plans/<int:plan_id>/courses', methods=['GET', 'POST'])
@require_auth(['admin'])
def manage_plan_courses(plan_id: int):
    """Get all courses in a plan or add a new course to the plan."""
    plan = MajorPlanService.get_plan_by_id(plan_id)
    if not plan:
        return error_response('Major plan not found', status=404)
    
    if request.method == 'GET':
        semester = request.args.get('semester', type=int)
        if semester:
            courses = MajorPlanService.get_courses_by_semester(plan_id, semester)
        else:
            courses = MajorPlanService.get_plan_courses(plan_id)
        return jsonify(courses)
    
    # POST - Add course to plan
    payload = request.get_json(force=True)
    
    try:
        validate_plan_course(payload)
    except ValueError as e:
        return error_response(str(e))
    
    try:
        course = MajorPlanService.add_course_to_plan(
            plan_id,
            payload['course_id'],
            payload['semester'],
            payload.get('is_required', True)
        )
        # json_response already returns (Response, status); avoid wrapping in another tuple
        return json_response(course, message='Course added to plan successfully', status=201)
    except Exception as e:
        if 'duplicate key' in str(e).lower():
            return error_response('This course is already in the plan for this semester', status=409)
        return error_response(str(e))


@admin_bp.route('/major-plans/courses/<int:course_id>', methods=['DELETE'])
@require_auth(['admin'])
def remove_plan_course(course_id: int):
    """Remove a course from a major plan."""
    try:
        MajorPlanService.remove_course_from_plan(course_id)
        return json_response(message='Course removed from plan successfully')
    except Exception as e:
        return error_response(str(e), status=400)

