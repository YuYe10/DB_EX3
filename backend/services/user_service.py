"""
User service for authentication and user management.
"""
from typing import Optional, Dict, Any
from flask import session
from db import db
from utils import hash_password


class UserService:
    """Service for user-related operations."""
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password.
        
        Returns:
            User information dict if successful, None otherwise
        """
        hashed_password = hash_password(password)
        user = db.fetch_one(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            [username, hashed_password]
        )
        
        if not user:
            return None
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['ref_id'] = user['ref_id']
        
        # Get additional user info
        return UserService.get_user_info(user)
    
    @staticmethod
    def get_user_info(user: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete user information including role-specific details."""
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
        
        if user['role'] == 'student' and user['ref_id']:
            student = db.fetch_one("SELECT * FROM students WHERE id=%s", [user['ref_id']])
            if student:
                user_info['name'] = student['name']
                user_info['student_no'] = student['student_no']
        elif user['role'] == 'teacher' and user['ref_id']:
            teacher = db.fetch_one("SELECT * FROM teachers WHERE id=%s", [user['ref_id']])
            if teacher:
                user_info['name'] = teacher['name']
                user_info['teacher_no'] = teacher['teacher_no']
        
        return user_info
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current logged-in user information."""
        if 'user_id' not in session:
            return None
        
        user = db.fetch_one("SELECT * FROM users WHERE id=%s", [session['user_id']])
        if not user:
            return None
        
        return UserService.get_user_info(user)
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Returns:
            True if successful, False if old password is incorrect
        """
        user = db.fetch_one(
            "SELECT * FROM users WHERE id=%s AND password=%s",
            [user_id, hash_password(old_password)]
        )
        
        if not user:
            return False
        
        db.execute(
            "UPDATE users SET password=%s WHERE id=%s",
            [hash_password(new_password), user_id]
        )
        return True
    
    @staticmethod
    def create_user(username: str, password: str, role: str, ref_id: Optional[int] = None) -> int:
        """Create a new user account."""
        user_id = db.execute_returning(
            "INSERT INTO users (username, password, role, ref_id) VALUES (%s, %s, %s, %s) RETURNING id",
            [username, hash_password(password), role, ref_id]
        )
        return user_id
    
    @staticmethod
    def initialize_default_accounts():
        """Initialize default user accounts on first run."""
        # Create admin account
        admin = db.fetch_one("SELECT * FROM users WHERE username='admin'")
        if not admin:
            UserService.create_user('admin', 'admin@123', 'admin')
        
        # Create user accounts for existing students
        students = db.fetch_all("SELECT * FROM students")
        for student in students:
            user = db.fetch_one("SELECT * FROM users WHERE username=%s", [student['student_no']])
            if not user:
                UserService.create_user(
                    student['student_no'],
                    f"s{student['student_no']}",
                    'student',
                    student['id']
                )
        
        # Create user accounts for existing teachers
        teachers = db.fetch_all("SELECT * FROM teachers")
        for teacher in teachers:
            user = db.fetch_one("SELECT * FROM users WHERE username=%s", [teacher['teacher_no']])
            if not user:
                UserService.create_user(
                    teacher['teacher_no'],
                    f"t{teacher['teacher_no']}",
                    'teacher',
                    teacher['id']
                )
