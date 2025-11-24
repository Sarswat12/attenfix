import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database
    DB_USER = os.getenv('DB_USER', 'root')
    # Read raw password and percent-encode it for safe inclusion in the DB URL.
    # If the password already appears percent-encoded (contains '%'), avoid double-encoding.
    _raw_db_password = os.getenv('DB_PASSWORD', '')
    if _raw_db_password and '%' not in _raw_db_password:
        DB_PASSWORD = quote_plus(_raw_db_password)
    else:
        DB_PASSWORD = _raw_db_password
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'face_attendance_db')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://"
        f"{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/"
        f"{DB_NAME}"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Face Recognition
    FACE_RECOGNITION_THRESHOLD = float(os.getenv('FACE_RECOGNITION_THRESHOLD', 0.6))
    MIN_FACE_IMAGES = int(os.getenv('MIN_FACE_IMAGES_FOR_ENROLLMENT', 5))
    MAX_FACE_IMAGES = int(os.getenv('MAX_FACE_IMAGES_FOR_ENROLLMENT', 7))

    # File Upload
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', 5)) * 1024 * 1024
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/storage')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
