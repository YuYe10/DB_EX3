"""
Configuration module for Flask application.
"""
import os
from dotenv import load_dotenv


APP_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(APP_CORE_DIR)
REPO_ROOT = os.path.dirname(BACKEND_ROOT)

# Load environment variables
ENV_PATH = os.path.join(REPO_ROOT, '.env')
load_dotenv(ENV_PATH)


class Config:
    """Application configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(APP_CORE_DIR, 'flask_session')
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_PERMANENT = False
    
    # CORS
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5174'
    ]
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ['Content-Type']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    # Database (from db.py)
    DB_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    DB_NAME = os.getenv('MYSQL_DBNAME', 'student_db')
    DB_USER = os.getenv('MYSQL_USER', 'student_app')
    DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '')


# Ensure session directory exists inside app_core
os.makedirs(Config.SESSION_FILE_DIR, exist_ok=True)
