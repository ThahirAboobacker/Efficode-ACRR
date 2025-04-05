import os
import torch
from transformers import AutoTokenizer, AutoModel, T5ForConditionalGeneration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_models():
    logger.info("Starting model downloads...")
    
    try:
        # Create models directory
        os.makedirs("../models", exist_ok=True)
        
        # Download CodeBERT
        logger.info("Downloading CodeBERT...")
        tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        model = AutoModel.from_pretrained("microsoft/codebert-base")
        
        # Download FLAN-T5
        logger.info("Downloading FLAN-T5...")
        t5_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        t5_model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
        
        logger.info("Models downloaded successfully!")
        
    except Exception as e:
        logger.error(f"Error downloading models: {str(e)}")
        raise

if __name__ == "__main__":
    download_models()