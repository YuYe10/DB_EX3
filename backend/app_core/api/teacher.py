"""
Teacher routes blueprint.
"""
from flask import Blueprint, request, session, jsonify, send_file

from app_core.services import TeacherService
from app_core.utils import json_response, error_response, require_auth

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')


@teacher_bp.route('/courses', methods=['GET'])
@require_auth(['teacher'])
def get_courses():
    """Get courses taught by current teacher."""
    courses = TeacherService.get_courses(session['ref_id'])
    # Frontend expects a plain array, not a wrapped payload
    return jsonify(courses)


@teacher_bp.route('/courses/<int:course_id>/students', methods=['GET'])
@require_auth(['teacher'])
def get_course_students(course_id: int):
    """Get student list for a specific course."""
    students = TeacherService.get_course_students(session['ref_id'], course_id)
    
    if students is None:
        return error_response('Course not found or access denied', status=404)
    
    # Frontend expects a plain array, not a wrapped payload
    return jsonify(students)


@teacher_bp.route('/enrollments/<int:enrollment_id>/grade', methods=['PUT'])
@require_auth(['teacher'])
def set_grade(enrollment_id: int):
    """Set grade for a student."""
    payload = request.get_json(force=True)
    
    if 'grade' not in payload:
        return error_response('成绩为必填')
    
    try:
        grade = float(payload['grade'])
        if grade < 0 or grade > 100:
            return error_response('成绩必须在0-100之间')
    except (ValueError, TypeError):
        return error_response('成绩必须为数字')
    
    success = TeacherService.set_grade(session['ref_id'], enrollment_id, grade)
    
    if not success:
        return error_response('成绩录入失败：检查权限或选课记录', status=404)
    
    return json_response(message='Grade updated successfully')


@teacher_bp.route('/courses/<int:course_id>/grades/export', methods=['GET'])
@require_auth(['teacher'])
def export_course_grades(course_id: int):
    """Export grades for a course taught by the current teacher."""
    buffer, filename = TeacherService.export_course_grades(session['ref_id'], course_id)
    if buffer is None:
        return error_response('课程不存在或无权限', status=404)
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@teacher_bp.route('/courses/import', methods=['POST'])
@require_auth(['teacher'])
def import_course_roster():
    """Import a course roster Excel for the current teacher."""
    file = request.files.get('file')
    if not file:
        return error_response('缺少文件', status=400)
    try:
        summary = TeacherService.import_course_roster(session['ref_id'], file)
        return jsonify({'success': True, 'summary': summary})
    except ValueError as exc:
        return error_response(str(exc), status=400)
    except Exception as exc:  # pragma: no cover - defensive
        return error_response(f'导入失败: {exc}', status=500)


@teacher_bp.route('/courses/import/sample', methods=['GET'])
@require_auth(['teacher'])
def sample_course_roster():
    """Download a sample roster Excel for teachers."""
    buffer, filename = TeacherService.sample_course_roster()
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
