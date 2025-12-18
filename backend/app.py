"""
Flask application factory and initialization.
"""
from flask import Flask, request
from flask_cors import CORS
from flask_session import Session
import os
import logging
import time

from config import Config
from services import UserService
from api import auth_bp, student_bp, teacher_bp, admin_bp
from middleware import deduplicate_request, log_operation
from logger import setup_logging, log_request, log_response, log_auth, log_database, log_error

# 设置日志系统
setup_logging(log_dir='logs', console_level=logging.DEBUG, file_level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """
    Create and configure Flask application.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app,
         origins=config_class.CORS_ORIGINS,
         supports_credentials=config_class.CORS_SUPPORTS_CREDENTIALS,
         allow_headers=config_class.CORS_ALLOW_HEADERS,
         methods=config_class.CORS_METHODS)
    Session(app)
    
    # 请求前处理 - 记录日志和计时
    @app.before_request
    def before_request():
        request.start_time = time.time()
        log_request(request.method, request.path)
    
    # 请求后处理 - 记录响应和耗时
    @app.after_request
    def after_request(response):
        elapsed = (time.time() - request.start_time) * 1000 if hasattr(request, 'start_time') else 0
        log_response(response.status_code, request.method, request.path, elapsed)
        return response
    
    # 全局错误处理
    @app.errorhandler(Exception)
    def handle_error(error):
        log_error("Unhandled Exception", error, path=request.path, method=request.method)
        return {"error": "Internal Server Error", "message": str(error)}, 500
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize default user accounts
    with app.app_context():
        UserService.initialize_default_accounts()
        logger.info("✅ Application initialized successfully")
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
