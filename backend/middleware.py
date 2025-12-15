"""
Middleware for request deduplication, logging, and audit trail.
"""
from functools import wraps
from datetime import datetime
import logging
import os
from flask import request, session

# 请求去重缓存（简易实现，生产环境应用 Redis）
request_cache = {}

# 获取日志记录器
audit_logger = logging.getLogger('audit')

def deduplicate_request(timeout=5):
    """防止重复提交相同请求（POST/PUT/DELETE）"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 仅对 POST/PUT/DELETE 方法进行去重检查
            if request.method not in ['POST', 'PUT', 'DELETE']:
                return f(*args, **kwargs)
            
            # 使用 session 用户 ID + 请求路径 + method 作为缓存键
            user_id = session.get('user_id', 'anonymous')
            cache_key = f"{user_id}:{request.path}:{request.method}:{request.get_data()}"
            
            # 检查缓存
            if cache_key in request_cache:
                cached_time = request_cache[cache_key]
                elapsed = (datetime.now() - cached_time).total_seconds()
                if elapsed < timeout:
                    audit_logger.warning(f"⚠️ 重复请求被拦截: {request.path} ({user_id})")
                    return {
                        'success': False,
                        'message': '请勿重复提交，请稍候'
                    }, 429
            
            # 记录此次请求
            request_cache[cache_key] = datetime.now()
            
            # 清理过期缓存（简易）
            now = datetime.now()
            keys_to_delete = [k for k, v in request_cache.items() 
                            if (now - v).total_seconds() > timeout]
            for k in keys_to_delete:
                del request_cache[k]
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def log_operation(action_type):
    """记录用户操作审计日志"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                user_id = session.get('user_id', 'unknown')
                user_type = session.get('user_type', 'unknown')
                
                audit_logger.info(
                    f"AUDIT: {action_type} | User: {user_id} ({user_type}) | "
                    f"Path: {request.path} | Method: {request.method}"
                )
                
                result = f(*args, **kwargs)
                return result
            except Exception as e:
                audit_logger.error(
                    f"ERROR in {action_type}: {str(e)}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator
