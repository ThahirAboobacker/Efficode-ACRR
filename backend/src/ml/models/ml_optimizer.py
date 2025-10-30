"""
ML-based Code Optimizer using CodeBERT/CodeT5
"""

import os
import torch
import logging
from typing import List, Dict, Any, Optional, Tuple
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM,
    T5ForConditionalGeneration, RobertaTokenizer, RobertaModel,
    Trainer, TrainingArguments, DataCollatorForSeq2Seq
)
from torch.utils.data import Dataset
import numpy as np
from pathlib import Path

from ...data_models import OptimizationCandidate, ValidationStatus, BaseOptimizer, OptimizationLevel
from ...config import Config

logger = logging.getLogger('efficode.ml_optimizer')

class CodeOptimizationDataset(Dataset):
    """Dataset for code optimization training"""
    
    def __init__(self, examples, tokenizer, max_length=512):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        example = self.examples[idx]
        
        # Prepare input text
        input_text = f"Optimize this code: {example.original_code}"
        target_text = example.optimized_code
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        targets = self.tokenizer(
            target_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': targets['input_ids'].squeeze()
        }

class CodeBERTOptimizer:
    """CodeBERT-based code optimizer"""
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load CodeBERT model"""
        try:
            if model_path and Path(model_path).exists():
                logger.info(f"Loading fine-tuned model from {model_path}")
                self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
                self.model = RobertaModel.from_pretrained(model_path)
            else:
                logger.info(f"Loading base model: {self.model_name}")
                self.tokenizer = RobertaTokenizer.from_pretrained(self.model_name)
                self.model = RobertaModel.from_pretrained(self.model_name)
            
            self.model.to(self.device)
            self.model.eval()
            return True
            
        except Exception as e:
            logger.error(f"Error loading CodeBERT model: {e}")
            return False
    
    def encode_code(self, code: str) -> torch.Tensor:
        """Encode code using CodeBERT"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        inputs = self.tokenizer(
            code,
            return_tensors='pt',
            max_length=512,
            padding=True,
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use the [CLS] token representation
            code_embedding = outputs.last_hidden_state[:, 0, :]
        
        return code_embedding
    
    def calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code snippets"""
        try:
            emb1 = self.encode_code(code1)
            emb2 = self.encode_code(code2)
            
            # Cosine similarity
            similarity = torch.cosine_similarity(emb1, emb2).item()
            return similarity
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

class CodeT5Optimizer:
    """CodeT5-based code optimizer"""
    
    def __init__(self, model_name: str = "Salesforce/codet5-base"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load CodeT5 model"""
        try:
            if model_path and Path(model_path).exists():
                logger.info(f"Loading fine-tuned CodeT5 from {model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(model_path)
            else:
                logger.info(f"Loading base CodeT5: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            
            self.model.to(self.device)
            self.model.eval()
            return True
            
        except Exception as e:
            logger.error(f"Error loading CodeT5 model: {e}")
            return False
    
    def optimize_code(self, code: str, num_candidates: int = 3) -> List[str]:
        """Generate optimized code candidates"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        # Prepare input
        input_text = f"optimize: {code}"
        inputs = self.tokenizer(
            input_text,
            return_tensors='pt',
            max_length=512,
            padding=True,
            truncation=True
        ).to(self.device)
        
        candidates = []
        
        try:
            with torch.no_grad():
                # Generate multiple candidates
                outputs = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_return_sequences=num_candidates,
                    num_beams=num_candidates * 2,
                    temperature=0.8,
                    do_sample=True,
                    early_stopping=True
                )
                
                for output in outputs:
                    decoded = self.tokenizer.decode(output, skip_special_tokens=True)
                    # Remove the "optimize:" prefix if present
                    if decoded.startswith("optimize:"):
                        decoded = decoded[9:].strip()
                    candidates.append(decoded)
        
        except Exception as e:
            logger.error(f"Error generating optimized code: {e}")
            candidates = [code]  # Fallback to original
        
        return candidates
    
    def fine_tune(self, training_examples, output_dir: str, epochs: int = 3):
        """Fine-tune CodeT5 on optimization examples"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        # Prepare dataset
        dataset = CodeOptimizationDataset(training_examples, self.tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=Config.ML_CONFIG['batch_size'],
            learning_rate=Config.ML_CONFIG['learning_rate'],
            warmup_steps=Config.ML_CONFIG['warmup_steps'],
            logging_steps=100,
            save_steps=500,
            evaluation_strategy="steps",
            eval_steps=500,
            save_total_limit=2,
            load_best_model_at_end=True,
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model,
            padding=True
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer
        )
        
        # Train
        logger.info("Starting CodeT5 fine-tuning...")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Fine-tuning completed. Model saved to {output_dir}")

class MLOptimizer(BaseOptimizer):
    """Main ML-based optimizer that combines CodeBERT and CodeT5"""
    
    def __init__(self):
        self.codebert = CodeBERTOptimizer()
        self.codet5 = CodeT5Optimizer()
        self.applied_rules = []
        self.confidence_threshold = Config.OPTIMIZATION_CONFIG['confidence_threshold']
    
    def load_models(self) -> bool:
        """Load all ML models"""
        codebert_path = Config.get_model_path('codebert')
        codet5_path = Config.get_model_path('codet5')
        
        codebert_loaded = self.codebert.load_model(str(codebert_path) if codebert_path else None)
        codet5_loaded = self.codet5.load_model(str(codet5_path) if codet5_path else None)
        
        if not (codebert_loaded or codet5_loaded):
            logger.error("Failed to load any ML models")
            return False
        
        logger.info(f"ML models loaded - CodeBERT: {codebert_loaded}, CodeT5: {codet5_loaded}")
        return True
    
    def optimize(self, code: str, level: OptimizationLevel = OptimizationLevel.MEDIUM) -> List[OptimizationCandidate]:
        """Generate optimization candidates using ML models"""
        self.applied_rules = []
        candidates = []
        
        try:
            # Generate candidates using CodeT5
            if self.codet5.model:
                num_candidates = self._get_num_candidates(level)
                optimized_codes = self.codet5.optimize_code(code, num_candidates)
                
                for i, opt_code in enumerate(optimized_codes):
                    if opt_code != code:  # Only include actual optimizations
                        confidence = self._calculate_confidence(code, opt_code)
                        
                        if confidence >= self.confidence_threshold:
                            candidate = OptimizationCandidate(
                                optimized_code=opt_code,
                                confidence_score=confidence,
                                applied_techniques=['ml_optimization', 'codet5'],
                                complexity_improvement={'type': 'ml_based'},
                                validation_status=ValidationStatus.SKIPPED  # Will be validated later
                            )
                            candidates.append(candidate)
                            
                            self.applied_rules.append({
                                'type': 'ml_optimization',
                                'description': f'ML-based optimization (confidence: {confidence:.2f})',
                                'category': 'ml'
                            })
            
            # If no good candidates, return original code
            if not candidates:
                candidate = OptimizationCandidate(
                    optimized_code=code,
                    confidence_score=1.0,
                    applied_techniques=[],
                    complexity_improvement={'type': 'no_change'},
                    validation_status=ValidationStatus.PASSED
                )
                candidates.append(candidate)
        
        except Exception as e:
            logger.error(f"Error in ML optimization: {e}")
            # Fallback candidate
            candidate = OptimizationCandidate(
                optimized_code=code,
                confidence_score=1.0,
                applied_techniques=[],
                complexity_improvement={'type': 'error', 'error': str(e)},
                validation_status=ValidationStatus.ERROR
            )
            candidates.append(candidate)
        
        return candidates
    
    def _get_num_candidates(self, level: OptimizationLevel) -> int:
        """Get number of candidates based on optimization level"""
        if level == OptimizationLevel.LOW:
            return 1
        elif level == OptimizationLevel.MEDIUM:
            return 3
        else:  # HIGH
            return 5
    
    def _calculate_confidence(self, original: str, optimized: str) -> float:
        """Calculate confidence score for optimization"""
        try:
            # Use CodeBERT to calculate semantic similarity
            if self.codebert.model:
                similarity = self.codebert.calculate_similarity(original, optimized)
                # High similarity means the optimization preserves semantics
                # But we also want some difference to indicate actual optimization
                if 0.7 <= similarity <= 0.95:
                    confidence = similarity
                elif similarity > 0.95:
                    confidence = 0.5  # Too similar, might not be optimized
                else:
                    confidence = similarity * 0.5  # Too different, might be wrong
            else:
                # Fallback: simple heuristic based on code length and structure
                len_ratio = len(optimized) / len(original) if len(original) > 0 else 1.0
                confidence = 0.8 if 0.5 <= len_ratio <= 1.5 else 0.3
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def get_applied_rules(self) -> List[Dict[str, Any]]:
        """Get list of applied ML optimization rules"""
        return self.applied_rules
    
    def fine_tune_models(self, training_examples, output_dir: str):
        """Fine-tune ML models on training data"""
        logger.info("Starting ML model fine-tuning...")
        
        # Fine-tune CodeT5
        if self.codet5.model:
            codet5_dir = Path(output_dir) / 'codet5'
            self.codet5.fine_tune(training_examples, str(codet5_dir))
        
        logger.info("ML model fine-tuning completed")