import os
from datetime import timedelta

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///phishing_detector.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WebSocket settings
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    
    # Alert settings
    ALERT_RETENTION_DAYS = 30
    MAX_ALERTS_PER_USER = 1000
    
    # Model settings
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'phishing_detector.pkl')
    VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'vectorizer.pkl')
    
    # Processing settings
    MAX_URL_LENGTH = 2048
    MAX_EMAIL_SIZE = 10 * 1024 * 1024  # 10MB
    SCAN_TIMEOUT = 30  # seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
