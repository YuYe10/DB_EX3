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


@teacher_bp.route('/courses/stats', methods=['GET'])
@require_auth(['teacher'])
def get_course_stats():
    """Get stats (avg/pass/excellent) for courses taught by the current teacher."""
    stats = TeacherService.get_course_stats(session['ref_id'])
    return jsonify(stats)


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


@teacher_bp.route('/enrollments/<int:enrollment_id>/grades', methods=['PUT'])
@require_auth(['teacher'])
def update_student_grades(enrollment_id: int):
    """Update student grades including ordinary_score and final_score.
    Weights are now stored at course level, not per enrollment.
    
    Expected payload:
    {
        "ordinary_score": 80,    # 平时成绩 (0-100)
        "final_score": 85        # 期末成绩 (0-100)
    }
    
    Notes:
    - final_grade is automatically calculated using course-level weights
    """
    payload = request.get_json(force=True)
    
    try:
        success = TeacherService.update_student_grades(session['ref_id'], enrollment_id, payload)
        if not success:
            return error_response('权限检查失败或选课记录不存在', status=404)
        return json_response(message='Student grades updated successfully')
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f'Update failed: {str(e)}', status=500)


@teacher_bp.route('/courses/<int:course_id>/weights', methods=['PUT'])
@require_auth(['teacher'])
def update_course_weights(course_id: int):
    """Update course grade weights.
    
    Expected payload:
    {
        "ordinary_weight": 0.4,  # 平时成绩占比 (0-1)
        "final_weight": 0.6      # 期末成绩占比 (0-1)
    }
    
    Notes:
    - ordinary_weight and final_weight must sum to 1
    - This updates the course-level default weights for all students
    - All existing final_grade values in this course will be recalculated
    """
    payload = request.get_json(force=True)
    
    try:
        if 'ordinary_weight' not in payload or 'final_weight' not in payload:
            return error_response('ordinary_weight和final_weight为必填')
        
        ordinary_weight = float(payload['ordinary_weight'])
        final_weight = float(payload['final_weight'])
        
        success = TeacherService.update_course_weights(session['ref_id'], course_id, ordinary_weight, final_weight)
        if not success:
            return error_response('权限检查失败或课程不存在', status=404)
        
        return json_response(message='课程成绩占比更新成功')
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f'Update failed: {str(e)}', status=500)


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
