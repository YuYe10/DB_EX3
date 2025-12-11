"""
Configuration module for Flask application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
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
    DB_HOST = os.getenv('OG_HOST', '192.168.0.61')
    DB_PORT = int(os.getenv('OG_PORT', '26000'))
    DB_NAME = os.getenv('OG_DBNAME', 'student_db')
    DB_USER = os.getenv('OG_USER', 'appuser')
    DB_PASSWORD = os.getenv('OG_PASSWORD', '')
