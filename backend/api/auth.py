"""
Authentication routes blueprint.
"""
from flask import Blueprint, request, session
from services import UserService
from utils import json_response, error_response, validate_fields, require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    payload = request.get_json(force=True)
    
    try:
        validate_fields(payload, ['username', 'password'])
    except ValueError as e:
        return error_response(str(e))
    
    user = UserService.authenticate(payload['username'], payload['password'])
    
    if not user:
        return error_response('Invalid username or password', status=401)
    
    return json_response({'user': user})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint."""
    session.clear()
    return json_response()


@auth_bp.route('/me', methods=['GET'])
@require_auth()
def get_current_user():
    """Get current logged-in user information."""
    user = UserService.get_current_user()
    if not user:
        return error_response('User not found', status=404)
    return json_response(user)


@auth_bp.route('/change-password', methods=['POST'])
@require_auth()
def change_password():
    """Change password for current user."""
    payload = request.get_json(force=True)
    
    try:
        validate_fields(payload, ['old_password', 'new_password'])
    except ValueError as e:
        return error_response(str(e))
    
    success = UserService.change_password(
        session['user_id'],
        payload['old_password'],
        payload['new_password']
    )
    
    if not success:
        return error_response('Incorrect old password', status=400)
    
    return json_response(message='Password changed successfully')
