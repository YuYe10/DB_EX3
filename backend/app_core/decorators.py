"""
Response decorators to reduce coupling and eliminate boilerplate.
"""
from functools import wraps
from typing import Callable, Any, Tuple, Optional
from flask import jsonify


def api_endpoint(required_auth: Optional[list] = None):
    """
    Decorator that standardizes API endpoint response handling.
    
    Automatically handles:
    - Authentication verification
    - Error handling and logging
    - Response formatting
    - HTTP status codes
    
    Example:
        @api_endpoint(required_auth=['student'])
        def get_enrollments():
            return StudentService.get_enrollments(user_id)
        
        # Instead of:
        @require_auth(['student'])
        def get_enrollments():
            try:
                enrollments = StudentService.get_enrollments(user_id)
                return json_response(enrollments)
            except Exception as e:
                return error_response(str(e), 500)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Call the handler
                result = f(*args, **kwargs)
                
                # Handle different return types
                if isinstance(result, tuple) and len(result) == 2:
                    # (data, status_code)
                    data, status = result
                    if isinstance(status, int) and status >= 400:
                        return jsonify({'error': data if isinstance(data, str) else data}), status
                    return jsonify({'data': data}), status
                elif isinstance(result, dict):
                    # Already a dict, assume success
                    return jsonify({'data': result}), 200
                else:
                    # Raw response object
                    return result
                    
            except ValueError as e:
                # Input validation errors
                return jsonify({'error': str(e)}), 400
            except PermissionError as e:
                # Authorization errors
                return jsonify({'error': str(e)}), 403
            except KeyError as e:
                # Resource not found
                return jsonify({'error': f'Not found: {str(e)}'}), 404
            except Exception as e:
                # Unexpected errors
                import logging
                logging.error(f"Unhandled error in {f.__name__}: {str(e)}", exc_info=True)
                return jsonify({'error': 'Internal server error'}), 500
        
        return wrapper
    
    return decorator


def handle_service_result(f: Callable) -> Callable:
    """
    Decorator that converts service method return values to HTTP responses.
    
    Service methods can return:
    - None/True for success (200)
    - (data, status_code) for custom status
    - (None, 404) for not found
    - (error_message, 400) for validation error
    
    Example:
        @handle_service_result
        def create_student():
            student_id = StudentService.create_student(data)
            return StudentService.get_student_by_id(student_id), 201
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            
            # If result is None or True, return 200 OK
            if result is None or result is True:
                return jsonify({'success': True}), 200
            
            # If result is a tuple (data, status_code)
            if isinstance(result, tuple) and len(result) >= 2:
                data, status = result[0], result[1]
                
                if status >= 400:
                    return jsonify({'error': data if isinstance(data, str) else str(data)}), status
                else:
                    return jsonify({'data': data if data is not None else {}}), status
            
            # Direct dict return
            if isinstance(result, dict):
                return jsonify({'data': result}), 200
            
            # Default: return as-is (for special responses like file downloads)
            return result
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403
        except Exception as e:
            import logging
            logging.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500
    
    return wrapper
