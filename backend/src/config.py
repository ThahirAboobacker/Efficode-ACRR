import os
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Enhanced configuration class for EFFICODE-ACRR"""
    
    # API Configuration
    API_VERSION = os.getenv("API_VERSION", "2.0.0")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    
    # Directory Paths
    BASE_DIR = Path(__file__).parent.parent.absolute()
    LOG_DIR = BASE_DIR / "logs"
    LOG_FILE = LOG_DIR / "efficode.log"
    DATA_DIR = BASE_DIR / "datasets"
    MODEL_CACHE_DIR = BASE_DIR / "models"
    ML_DIR = BASE_DIR / "src" / "ml"
    
    # ML Model Configuration
    CODEBERT_MODEL = os.getenv("CODEBERT_MODEL", "microsoft/codebert-base")
    CODET5_MODEL = os.getenv("CODET5_MODEL", "Salesforce/codet5-base")
    FLAN_T5_MODEL = os.getenv("FLAN_T5_MODEL", "google/flan-t5-base")
    OFFLINE_MODE = os.getenv("OFFLINE_MODE", "False").lower() == "true"
    
    # Optimization Configuration
    DEFAULT_OPTIMIZATION_LEVEL = os.getenv("DEFAULT_OPTIMIZATION_LEVEL", "medium")
    MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "10000"))
    MAX_GENERATION_LENGTH = int(os.getenv("MAX_GENERATION_LENGTH", "512"))
    
    # Model paths
    MODEL_PATHS = {
        'codebert': MODEL_CACHE_DIR / 'codebert_fine_tuned',
        'codet5': MODEL_CACHE_DIR / 'codet5_fine_tuned',
        'flan_t5': MODEL_CACHE_DIR / 'flan_t5_fine_tuned',
        'complexity_rf': MODEL_CACHE_DIR / 'complexity_random_forest.pkl',
        'complexity_lgb': MODEL_CACHE_DIR / 'complexity_lightgbm.pkl'
    }

    # API Configuration
    API_CONFIG = {
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max-limit
        'TIMEOUT': 60,  # seconds
        'RATE_LIMIT': 100,  # requests per minute
        'ENABLE_CORS': True
    }

    # Enhanced Optimization Configuration
    OPTIMIZATION_CONFIG = {
        'max_code_length': 10000,
        'timeout': 60,
        'use_neural_model': True,
        'use_rule_based': True,
        'fallback_to_rules': True,
        'enable_explainability': False,
        'max_candidates': 5,
        'confidence_threshold': 0.7,
        'validation_enabled': True
    }
    
    # ML Training Configuration
    ML_CONFIG = {
        'batch_size': 16,
        'learning_rate': 2e-5,
        'num_epochs': 3,
        'warmup_steps': 500,
        'max_seq_length': 512,
        'gradient_accumulation_steps': 1,
        'fp16': False,
        'dataloader_num_workers': 4
    }
    
    # Dataset Configuration
    DATASET_CONFIG = {
        'synthetic_samples': 10000,
        'train_split': 0.8,
        'val_split': 0.1,
        'test_split': 0.1,
        'augmentation_factor': 2,
        'min_code_length': 10,
        'max_code_length': 1000
    }
    
    # Complexity Prediction Configuration
    COMPLEXITY_CONFIG = {
        'feature_extractors': ['ast', 'loops', 'recursion', 'data_structures'],
        'model_type': 'random_forest',  # 'random_forest' or 'lightgbm'
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    }
    
    # Explainability Configuration
    EXPLAINABILITY_CONFIG = {
        'enable_shap': True,
        'enable_lime': True,
        'shap_samples': 100,
        'lime_samples': 1000,
        'feature_importance_threshold': 0.05
    }
    
    # Validation Configuration
    VALIDATION_CONFIG = {
        'sandbox_timeout': 30,
        'max_memory_mb': 512,
        'enable_docker': False,  # Set to True for production
        'docker_image': 'python:3.11-slim',
        'test_cases_per_function': 5
    }

    # Logging Configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
            'detailed': {
                'format': '[%(asctime)s] %(levelname)s in %(name)s.%(funcName)s:%(lineno)d: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': str(LOG_FILE),
                'mode': 'a'
            },
            'error_file': {
                'class': 'logging.FileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': str(LOG_DIR / 'errors.log'),
                'mode': 'a'
            }
        },
        'loggers': {
            'efficode': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        }
    }
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        directories = [
            cls.LOG_DIR,
            cls.DATA_DIR,
            cls.MODEL_CACHE_DIR,
            cls.ML_DIR,
            cls.ML_DIR / 'models',
            cls.ML_DIR / 'training',
            cls.ML_DIR / 'evaluation'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create model directories
        for path in cls.MODEL_PATHS.values():
            path.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str) -> Optional[Path]:
        """Get path for a specific model"""
        return cls.MODEL_PATHS.get(model_name)
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        try:
            # Check required directories
            cls.create_directories()
            
            # Validate numeric settings
            assert cls.PORT > 0, "Port must be positive"
            assert cls.MAX_CODE_LENGTH > 0, "Max code length must be positive"
            assert 0 < cls.DATASET_CONFIG['train_split'] < 1, "Train split must be between 0 and 1"
            
            # Validate model configuration
            assert cls.ML_CONFIG['batch_size'] > 0, "Batch size must be positive"
            assert cls.ML_CONFIG['learning_rate'] > 0, "Learning rate must be positive"
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False

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