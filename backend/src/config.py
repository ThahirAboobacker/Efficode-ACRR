import os
from typing import Dict, Any

class Config:
    """Base configuration class for the application"""
    # API Configuration
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    
    # Directory Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_DIR, "efficode.log")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODEL_CACHE_DIR = os.path.join(BASE_DIR, "model_cache")
    
    # Model Configuration
    CODEBERT_MODEL = os.getenv("CODEBERT_MODEL", "microsoft/codebert-base")
    FLAN_T5_MODEL = os.getenv("FLAN_T5_MODEL", "google/flan-t5-base")
    OFFLINE_MODE = os.getenv("OFFLINE_MODE", "False").lower() == "true"
    
    # Optimization Configuration
    DEFAULT_OPTIMIZATION_LEVEL = os.getenv("DEFAULT_OPTIMIZATION_LEVEL", "medium")
    MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "10000"))
    MAX_GENERATION_LENGTH = int(os.getenv("MAX_GENERATION_LENGTH", "512"))
    
    # Model paths
    MODEL_PATHS = {
        'codebert': os.path.join(BASE_DIR, 'models', 'codebert_fine_tuned'),
        'flan_t5': os.path.join(BASE_DIR, 'models', 'flan_t5_cache'),
        'random_forest': os.path.join(BASE_DIR, 'models', 'random_forest')
    }

    # API Configuration
    API_CONFIG = {
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max-limit
        'TIMEOUT': 30,  # seconds
    }

    # Additional Optimization Configuration
    OPTIMIZATION_CONFIG = {
        'max_code_length': 5000,  # Maximum number of characters in input code
        'timeout': 30,  # Maximum time (in seconds) for optimization process
        'use_neural_model': True,  # Whether to use neural model for optimization
        'fallback_to_rules': True  # Fallback to rule-based optimization if neural fails
    }

    # Logging Configuration
    LOGGING_CONFIG = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file']
        }
    }
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.MODEL_CACHE_DIR, exist_ok=True)
        # Also create model directories
        for path in cls.MODEL_PATHS.values():
            os.makedirs(path, exist_ok=True)

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI = 'sqlite:///dev.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 