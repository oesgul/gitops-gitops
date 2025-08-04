"""
Configuration settings for the Image Recognition application.
"""

import os

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
    
    # Model settings
    MODEL_PATH = os.environ.get('MODEL_PATH', '/app/models')
    CLASSIFICATION_MODEL = os.environ.get('CLASSIFICATION_MODEL', 'mobilenet_v2')
    DETECTION_MODEL = os.environ.get('DETECTION_MODEL', 'ssd_mobilenet_v2')
    
    # Processing settings
    IMAGE_SIZE = tuple(map(int, os.environ.get('IMAGE_SIZE', '224,224').split(',')))
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', '0.5'))
    MAX_DETECTIONS = int(os.environ.get('MAX_DETECTIONS', '10'))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Performance settings
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '1'))
    USE_GPU = os.environ.get('USE_GPU', 'false').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}