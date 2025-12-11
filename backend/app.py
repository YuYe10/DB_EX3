"""
Flask application factory and initialization.
"""
from flask import Flask
from flask_cors import CORS
from flask_session import Session

from config import Config
from services import UserService
from api import auth_bp, student_bp, teacher_bp, admin_bp


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
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize default user accounts
    with app.app_context():
        UserService.initialize_default_accounts()
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
