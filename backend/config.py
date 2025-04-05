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
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.MODEL_CACHE_DIR, exist_ok=True) 