import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

# Optimization Configuration
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