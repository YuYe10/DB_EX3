import os
from typing import Dict, Any
from functools import wraps
import hashlib

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv

from db import db

# Ensure env variables are loaded when running via `python app.py`
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(ENV_PATH)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_PERMANENT'] = False
CORS(app, 
     origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174'],
     supports_credentials=True,
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
Session(app)


def _bad_request(message: str, status: int = 400):
    return jsonify({'success': False, 'message': message}), status


def _require_fields(payload: Dict[str, Any], fields):
    missing = [f for f in fields if not payload.get(f)]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")


def _hash_password(password: str) -> str:
    """Simple SHA256 hash for password storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def _require_auth(roles=None):
    """Decorator to require authentication and optionally specific roles."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return _bad_request('Authentication required', status=401)
            if roles and session.get('role') not in roles:
                return _bad_request('Permission denied', status=403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def _init_user_accounts():
    """Initialize default user accounts on first run."""
    # Create admin account
    admin = db.fetch_one("SELECT * FROM users WHERE username='admin'")
    if not admin:
        db.execute(
            "INSERT INTO users (username, password, role, ref_id) VALUES (%s, %s, %s, %s)",
            ['admin', _hash_password('admin@123'), 'admin', None]
        )
    
    # Create user accounts for existing students
    students = db.fetch_all("SELECT * FROM students")
    for s in students:
        user = db.fetch_one("SELECT * FROM users WHERE username=%s", [s['student_no']])
        if not user:
            db.execute(
                "INSERT INTO users (username, password, role, ref_id) VALUES (%s, %s, %s, %s)",
                [s['student_no'], _hash_password(f"s{s['student_no']}"), 'student', s['id']]
            )
    
    # Create user accounts for existing teachers
    teachers = db.fetch_all("SELECT * FROM teachers")
    for t in teachers:
        user = db.fetch_one("SELECT * FROM users WHERE username=%s", [t['teacher_no']])
        if not user:
            db.execute(
                "INSERT INTO users (username, password, role, ref_id) VALUES (%s, %s, %s, %s)",
                [t['teacher_no'], _hash_password(f"t{t['teacher_no']}"), 'teacher', t['id']]
            )


# Initialize user accounts
_init_user_accounts()


# ================ Authentication APIs ================ #

@app.route('/api/auth/login', methods=['POST'])
def login():
    payload = request.get_json(force=True)
    try:
        _require_fields(payload, ['username', 'password'])
    except ValueError as exc:
        return _bad_request(str(exc))
    
    username = payload['username']
    password = _hash_password(payload['password'])
    
    user = db.fetch_one(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        [username, password]
    )
    
    if not user:
        return _bad_request('Invalid username or password', status=401)
    
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    session['ref_id'] = user['ref_id']
    
    # Get additional user info
    user_info = {'id': user['id'], 'username': user['username'], 'role': user['role']}
    if user['role'] == 'student':
        student = db.fetch_one("SELECT * FROM students WHERE id=%s", [user['ref_id']])
        user_info['name'] = student['name'] if student else ''
        user_info['student_no'] = student['student_no'] if student else ''
    elif user['role'] == 'teacher':
        teacher = db.fetch_one("SELECT * FROM teachers WHERE id=%s", [user['ref_id']])
        user_info['name'] = teacher['name'] if teacher else ''
        user_info['teacher_no'] = teacher['teacher_no'] if teacher else ''
    
    return jsonify({'success': True, 'user': user_info})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/auth/me', methods=['GET'])
@_require_auth()
def get_current_user():
    user_info = {
        'id': session['user_id'],
        'username': session['username'],
        'role': session['role'],
        'ref_id': session.get('ref_id')
    }
    
    if session['role'] == 'student':
        student = db.fetch_one("SELECT * FROM students WHERE id=%s", [session['ref_id']])
        user_info['name'] = student['name'] if student else ''
        user_info['student_no'] = student['student_no'] if student else ''
    elif session['role'] == 'teacher':
        teacher = db.fetch_one("SELECT * FROM teachers WHERE id=%s", [session['ref_id']])
        user_info['name'] = teacher['name'] if teacher else ''
        user_info['teacher_no'] = teacher['teacher_no'] if teacher else ''
    
    return jsonify(user_info)


@app.route('/api/auth/change-password', methods=['POST'])
@_require_auth()
def change_password():
    payload = request.get_json(force=True)
    try:
        _require_fields(payload, ['old_password', 'new_password'])
    except ValueError as exc:
        return _bad_request(str(exc))
    
    old_password = _hash_password(payload['old_password'])
    new_password = _hash_password(payload['new_password'])
    
    user = db.fetch_one(
        "SELECT * FROM users WHERE id=%s AND password=%s",
        [session['user_id'], old_password]
    )
    
    if not user:
        return _bad_request('Invalid old password', status=401)
    
    db.execute(
        "UPDATE users SET password=%s WHERE id=%s",
        [new_password, session['user_id']]
    )
    
    return jsonify({'success': True})


@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        row = db.fetch_one('SELECT 1 as ok')
        return jsonify({'status': 'healthy', 'db': row.get('ok') == 1})
    except Exception as exc:
        return _bad_request(f'DB connection failed: {exc}', status=500)


# ================ Student-specific APIs ================ #

@app.route('/api/student/courses/available', methods=['GET'])
@_require_auth(['student'])
def student_available_courses():
    """Get all courses available for enrollment (not yet enrolled by current student)."""
    student_id = session['ref_id']
    rows = db.fetch_all(
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
    return jsonify(rows)


@app.route('/api/student/enrollments', methods=['GET', 'POST', 'DELETE'])
@_require_auth(['student'])
def student_enrollments():
    """Get student's enrollments or enroll in a course."""
    student_id = session['ref_id']
    
    if request.method == 'GET':
        rows = db.fetch_all(
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
        return jsonify(rows)
    
    if request.method == 'POST':
        payload = request.get_json(force=True)
        try:
            _require_fields(payload, ['course_id'])
        except ValueError as exc:
            return _bad_request(str(exc))
        
        try:
            new_id = db.execute_returning(
                'INSERT INTO enrollments (student_id, course_id, status) VALUES (%s, %s, %s) RETURNING id',
                [student_id, payload['course_id'], 'enrolled']
            )
        except Exception as exc:
            return _bad_request(f'Enroll failed: {exc}', status=500)
        
        return jsonify({'success': True, 'id': new_id})


@app.route('/api/student/enrollments/<int:enroll_id>', methods=['DELETE'])
@_require_auth(['student'])
def student_drop_course(enroll_id: int):
    """Drop a course (student can only drop their own enrollments)."""
    student_id = session['ref_id']
    
    # Verify ownership
    enroll = db.fetch_one("SELECT * FROM enrollments WHERE id=%s", [enroll_id])
    if not enroll or enroll['student_id'] != student_id:
        return _bad_request('Enrollment not found or access denied', status=404)
    
    db.execute('DELETE FROM enrollments WHERE id=%s', [enroll_id])
    return jsonify({'success': True})


# ================ Teacher-specific APIs ================ #

@app.route('/api/teacher/courses', methods=['GET'])
@_require_auth(['teacher'])
def teacher_courses():
    """Get courses taught by current teacher."""
    teacher_id = session['ref_id']
    rows = db.fetch_all(
        '''
        SELECT c.*,
               (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) AS enrolled_count
        FROM courses c
        WHERE c.teacher_id = %s
        ORDER BY c.id DESC
        ''',
        [teacher_id]
    )
    return jsonify(rows)


@app.route('/api/teacher/courses/<int:course_id>/students', methods=['GET'])
@_require_auth(['teacher'])
def teacher_course_students(course_id: int):
    """Get student list for a specific course (only if teacher teaches it)."""
    teacher_id = session['ref_id']
    
    # Verify teacher teaches this course
    course = db.fetch_one("SELECT * FROM courses WHERE id=%s", [course_id])
    if not course or course['teacher_id'] != teacher_id:
        return _bad_request('Course not found or access denied', status=404)
    
    rows = db.fetch_all(
        '''
        SELECT e.*, s.name AS student_name, s.student_no, s.major
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE e.course_id = %s
        ORDER BY s.student_no
        ''',
        [course_id]
    )
    return jsonify(rows)


@app.route('/api/teacher/enrollments/<int:enroll_id>/grade', methods=['PUT'])
@_require_auth(['teacher'])
def teacher_set_grade(enroll_id: int):
    """Set grade for a student (only if teacher teaches the course)."""
    teacher_id = session['ref_id']
    payload = request.get_json(force=True)
    
    if 'grade' not in payload:
        return _bad_request('grade is required')
    
    # Verify teacher teaches this course
    enroll = db.fetch_one(
        '''
        SELECT e.*, c.teacher_id
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.id = %s
        ''',
        [enroll_id]
    )
    
    if not enroll or enroll['teacher_id'] != teacher_id:
        return _bad_request('Enrollment not found or access denied', status=404)
    
    db.execute('UPDATE enrollments SET grade=%s WHERE id=%s', [payload['grade'], enroll_id])
    return jsonify({'success': True})


# ================ Admin APIs ================ #

@app.route('/api/students', methods=['GET', 'POST'])
@_require_auth(['admin'])
def students():
    if request.method == 'GET':
        major = request.args.get('major')
        keyword = request.args.get('q')
        sql = 'SELECT * FROM students WHERE 1=1'
        params = []
        if major:
            sql += ' AND major ILIKE %s'
            params.append(f'%{major}%')
        if keyword:
            sql += ' AND (name ILIKE %s OR student_no ILIKE %s)'
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        sql += ' ORDER BY id DESC'
        rows = db.fetch_all(sql, params)
        return jsonify(rows)

    payload = request.get_json(force=True)
    try:
        _require_fields(payload, ['student_no', 'name'])
    except ValueError as exc:
        return _bad_request(str(exc))

    new_id = db.execute_returning(
        'INSERT INTO students (student_no, name, major) VALUES (%s, %s, %s) RETURNING id',
        [payload['student_no'], payload['name'], payload.get('major', '')],
    )
    
    # Create user account for new student
    db.execute(
        "INSERT INTO users (username, password, role, ref_id) VALUES (%s, %s, %s, %s)",
        [payload['student_no'], _hash_password(f"s{payload['student_no']}"), 'student', new_id]
    )
    
    return jsonify({'success': True, 'id': new_id})


@app.route('/api/students/<int:student_id>', methods=['PUT', 'DELETE'])
@_require_auth(['admin'])
def update_student(student_id: int):
    if request.method == 'DELETE':
        db.execute('DELETE FROM students WHERE id=%s', [student_id])
        return jsonify({'success': True})

    payload = request.get_json(force=True)
    fields = ['student_no', 'name', 'major']
    updates = []
    params = []
    for f in fields:
        if f in payload:
            updates.append(f"{f}=%s")
            params.append(payload.get(f))
    if not updates:
        return _bad_request('No fields to update')
    params.append(student_id)
    db.execute(f"UPDATE students SET {', '.join(updates)} WHERE id=%s", params)
    return jsonify({'success': True})


# ---------------- Teachers ---------------- #
@app.route('/api/teachers', methods=['GET', 'POST'])
@_require_auth(['admin'])
def teachers():
    if request.method == 'GET':
        rows = db.fetch_all('SELECT * FROM teachers ORDER BY id DESC')
        return jsonify(rows)

    payload = request.get_json(force=True)
    try:
        _require_fields(payload, ['teacher_no', 'name'])
    except ValueError as exc:
        return _bad_request(str(exc))

    new_id = db.execute_returning(
        'INSERT INTO teachers (teacher_no, name, department) VALUES (%s, %s, %s) RETURNING id',
        [payload['teacher_no'], payload['name'], payload.get('department', '')],
    )
    
    # Create user account for new teacher
    db.execute(
        "INSERT INTO users (username, password, role, ref_id) VALUES (%s, %s, %s, %s)",
        [payload['teacher_no'], _hash_password(f"t{payload['teacher_no']}"), 'teacher', new_id]
    )
    
    return jsonify({'success': True, 'id': new_id})


@app.route('/api/teachers/<int:teacher_id>', methods=['PUT', 'DELETE'])
@_require_auth(['admin'])
def update_teacher(teacher_id: int):
    if request.method == 'DELETE':
        db.execute('DELETE FROM teachers WHERE id=%s', [teacher_id])
        return jsonify({'success': True})

    payload = request.get_json(force=True)
    updates = []
    params = []
    for f in ['teacher_no', 'name', 'department']:
        if f in payload:
            updates.append(f"{f}=%s")
            params.append(payload.get(f))
    if not updates:
        return _bad_request('No fields to update')
    params.append(teacher_id)
    db.execute(f"UPDATE teachers SET {', '.join(updates)} WHERE id=%s", params)
    return jsonify({'success': True})


# ---------------- Courses ---------------- #
@app.route('/api/courses', methods=['GET', 'POST'])
@_require_auth(['admin'])
def courses():
    if request.method == 'GET':
        rows = db.fetch_all(
            '''
            SELECT c.*, t.name AS teacher_name
            FROM courses c
            LEFT JOIN teachers t ON c.teacher_id = t.id
            ORDER BY c.id DESC
            '''
        )
        return jsonify(rows)

    payload = request.get_json(force=True)
    try:
        _require_fields(payload, ['course_code', 'name'])
    except ValueError as exc:
        return _bad_request(str(exc))

    new_id = db.execute_returning(
        '''
        INSERT INTO courses (course_code, name, credit, capacity, teacher_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        ''',
        [
            payload['course_code'],
            payload['name'],
            payload.get('credit', 0),
            payload.get('capacity', 50),
            payload.get('teacher_id'),
        ],
    )
    return jsonify({'success': True, 'id': new_id})


@app.route('/api/courses/<int:course_id>', methods=['PUT', 'DELETE'])
@_require_auth(['admin'])
def update_course(course_id: int):
    if request.method == 'DELETE':
        db.execute('DELETE FROM courses WHERE id=%s', [course_id])
        return jsonify({'success': True})

    payload = request.get_json(force=True)
    updates = []
    params = []
    for f in ['course_code', 'name', 'credit', 'capacity', 'teacher_id']:
        if f in payload:
            updates.append(f"{f}=%s")
            params.append(payload.get(f))
    if not updates:
        return _bad_request('No fields to update')
    params.append(course_id)
    db.execute(f"UPDATE courses SET {', '.join(updates)} WHERE id=%s", params)
    return jsonify({'success': True})


# ---------------- Enrollments ---------------- #
@app.route('/api/enrollments', methods=['GET', 'POST'])
@_require_auth(['admin'])
def enrollments():
    if request.method == 'GET':
        student_id = request.args.get('student_id')
        course_id = request.args.get('course_id')
        sql = '''
            SELECT e.*, s.name AS student_name, c.name AS course_name, t.name AS teacher_name
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            LEFT JOIN teachers t ON c.teacher_id = t.id
            WHERE 1=1
        '''
        params = []
        if student_id:
            sql += ' AND e.student_id=%s'
            params.append(student_id)
        if course_id:
            sql += ' AND e.course_id=%s'
            params.append(course_id)
        sql += ' ORDER BY e.id DESC'
        rows = db.fetch_all(sql, params)
        return jsonify(rows)

    payload = request.get_json(force=True)
    try:
        _require_fields(payload, ['student_id', 'course_id'])
    except ValueError as exc:
        return _bad_request(str(exc))

    try:
        new_id = db.execute_returning(
            'INSERT INTO enrollments (student_id, course_id, status) VALUES (%s, %s, %s) RETURNING id',
            [payload['student_id'], payload['course_id'], payload.get('status', 'enrolled')],
        )
    except Exception as exc:
        return _bad_request(f'Enroll failed: {exc}', status=500)

    return jsonify({'success': True, 'id': new_id})


@app.route('/api/enrollments/<int:enroll_id>/grade', methods=['PUT'])
@_require_auth(['admin'])
def set_grade(enroll_id: int):
    payload = request.get_json(force=True)
    if 'grade' not in payload:
        return _bad_request('grade is required')
    db.execute('UPDATE enrollments SET grade=%s WHERE id=%s', [payload.get('grade'), enroll_id])
    return jsonify({'success': True})


@app.route('/api/enrollments/<int:enroll_id>', methods=['DELETE'])
@_require_auth(['admin'])
def drop_course(enroll_id: int):
    db.execute('DELETE FROM enrollments WHERE id=%s', [enroll_id])
    return jsonify({'success': True})


# ---------------- Statistics ---------------- #
@app.route('/api/statistics/overview', methods=['GET'])
@_require_auth(['admin'])
def statistics_overview():
    counts = db.fetch_one(
        '''
        SELECT
            (SELECT COUNT(*) FROM students) AS students,
            (SELECT COUNT(*) FROM teachers) AS teachers,
            (SELECT COUNT(*) FROM courses) AS courses,
            (SELECT COUNT(*) FROM enrollments) AS enrollments
        '''
    )
    course_avg = db.fetch_all(
        '''
        SELECT c.id, c.name, c.course_code, ROUND(AVG(e.grade)::numeric, 2) AS avg_grade
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        GROUP BY c.id, c.name, c.course_code
        ORDER BY c.id
        '''
    )
    return jsonify({'counts': counts, 'course_avg': course_avg})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
