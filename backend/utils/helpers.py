"""
Utility functions and decorators.
"""
import hashlib
from functools import wraps
from typing import Dict, Any, List
from flask import jsonify, session


def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def json_response(data=None, success=True, message=None, status=200):
    """Create standardized JSON response."""
    response = {'success': success}
    if data is not None:
        if isinstance(data, dict) and 'success' not in data:
            response.update(data)
        else:
            response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), status


def error_response(message: str, status: int = 400):
    """Create error response."""
    return json_response(success=False, message=message, status=status)


def validate_fields(payload: Dict[str, Any], required_fields: List[str]):
    """Validate required fields in payload."""
    missing = [f for f in required_fields if not payload.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def require_auth(roles=None):
    """
    Decorator to require authentication and optionally specific roles.
    
    Args:
        roles: List of allowed roles or None to allow any authenticated user
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return error_response('Authentication required', status=401)
            if roles and session.get('role') not in roles:
                return error_response('Permission denied', status=403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    """Get current user information from session."""
    if 'user_id' not in session:
        return None
    return {
        'id': session['user_id'],
        'username': session['username'],
        'role': session['role'],
        'ref_id': session.get('ref_id')
    }
