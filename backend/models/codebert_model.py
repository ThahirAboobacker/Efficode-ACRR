"""
CodeBERT Model Integration for EFFICODE-ACRR

This module integrates Microsoft's CodeBERT model for code optimization tasks:
- Loading and initializing pre-trained CodeBERT models
- Fine-tuning on algorithm optimization datasets
- Generating optimized versions of input code
- Evaluating model performance
"""

import os
import torch
import logging
import numpy as np
import pandas as pd
import re
import ast
import json
import time
import sys
import threading
import functools
from typing import List, Dict, Tuple, Optional, Union, Any
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader

# Import rule-based optimization module
try:
    from backend.src.rule_based import apply_optimization_rules as rule_based_optimize
except ImportError:
    try:
        from src.rule_based import apply_optimization_rules as rule_based_optimize
    except ImportError:
        logger.warning("Failed to import rule_based module, using original code")
        def rule_based_optimize(code):
            return code, []  # Return empty list of changes as second parameter

# Import transformers conditionally to handle potential import errors
try:
    from transformers import (
        RobertaTokenizer, 
        RobertaConfig, 
        RobertaForSequenceClassification,
        RobertaForMaskedLM,
        RobertaModel,
        RobertaForCausalLM,
        Trainer, 
        TrainingArguments,
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        T5ForConditionalGeneration,
        BartForConditionalGeneration
    )
    from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logging.warning("Transformers library not available. Neural optimization will be disabled.")
    logging.warning("To enable neural optimization, install required packages with:")
    logging.warning("pip install torch transformers")
    TRANSFORMERS_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Suppress excessive warnings
if TRANSFORMERS_AVAILABLE:
    import transformers
    transformers.logging.set_verbosity_error()

# Timeout exception for neural model inference
class TimeoutError(Exception):
    """Exception raised when a function execution times out."""
    pass

# Timeout decorator using threading for cross-platform compatibility
def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            exception = None
            
            def target():
                nonlocal result, exception
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            if exception:
                raise exception
                
            return result
        return wrapper
    return decorator

class CodeOptimizationDataset(Dataset):
    """Custom dataset for code optimization pairs"""
    
    def __init__(self, 
                 tokenizer, 
                 code_pairs: List[Tuple[str, str]], 
                 max_length: int = 512,
                 is_pair: bool = True):
        """
        Initialize dataset with code pairs
        
        Args:
            tokenizer: Tokenizer for encoding code
            code_pairs: List of (unoptimized_code, optimized_code) pairs or single strings
            max_length: Maximum token length
            is_pair: Whether inputs are pairs or single strings
        """
        self.tokenizer = tokenizer
        self.code_pairs = code_pairs
        self.max_length = max_length
        self.is_pair = is_pair
        
    def __len__(self):
        return len(self.code_pairs)
    
    def __getitem__(self, idx):
        if self.is_pair:
            unoptimized, optimized = self.code_pairs[idx]
            
            # Tokenize input
            inputs = self.tokenizer(
                unoptimized,
                truncation=True,
                max_length=self.max_length,
                padding="max_length",
                return_tensors="pt"
            )
            
            # Tokenize target
            targets = self.tokenizer(
                optimized,
                truncation=True,
                max_length=self.max_length,
                padding="max_length",
                return_tensors="pt"
            )
            
            # Get rid of batch dimension
            item = {
                "input_ids": inputs["input_ids"].squeeze(),
                "attention_mask": inputs["attention_mask"].squeeze(),
                "labels": targets["input_ids"].squeeze()
            }
            
            # Replace padding token id with -100 so it's ignored in loss
            item["labels"] = torch.where(
                item["labels"] == self.tokenizer.pad_token_id,
                torch.tensor(-100),
                item["labels"]
            )
            
            return item
        else:
            # For classification/feature extraction
            code = self.code_pairs[idx]
            
            inputs = self.tokenizer(
                code,
                truncation=True,
                max_length=self.max_length,
                padding="max_length",
                return_tensors="pt"
            )
            
            return {
                "input_ids": inputs["input_ids"].squeeze(),
                "attention_mask": inputs["attention_mask"].squeeze()
            }

class CodeBERTOptimizer:
    """Class for CodeBERT model integration and optimization"""
    
    def __init__(self, 
                 model_dir: str = None, 
                 use_neural_model: bool = True,  # Default to True to enable neural model
                 model_name: str = "microsoft/codebert-base",
                 seq2seq_model: str = "Salesforce/codet5-small",  # Using smaller model for faster loading
                 max_length: int = 512,
                 neural_timeout: int = 30):  # Timeout for neural model inference in seconds
        """
        Initialize CodeBERT model
        
        Args:
            model_dir: Directory to save/load models
            use_neural_model: Whether to use neural model (False for rule-based only)
            model_name: Pretrained CodeBERT model name
            seq2seq_model: Base model for seq2seq if model_type is 'seq2seq'
            max_length: Maximum sequence length
            neural_timeout: Timeout for neural model inference in seconds
        """
        # Set model directory
        if model_dir is None:
            # Default to models/codebert directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_dir = current_dir
        else:
            self.model_dir = model_dir
            
        # Initialize attributes
        self.model_name = model_name
        self.seq2seq_model = seq2seq_model
        self.max_length = max_length
        self.use_neural_model = use_neural_model and TRANSFORMERS_AVAILABLE
        self.neural_timeout = neural_timeout
        
        # Set device and check for GPU
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
            logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device('cpu')
            if self.use_neural_model:
                logger.warning("Running on CPU. Neural optimization may be slow.")
        
        # Initialize models and tokenizers
        self.tokenizer = None
        self.model = None
        self.seq2seq_tokenizer = None
        self.seq2seq_model_obj = None
        
        # Load algorithm patterns for recognition
        self.algorithm_patterns = self._load_algorithm_patterns()
        
        logger.info(f"CodeBERTOptimizer initialized on device: {self.device}")
        logger.info(f"Neural model {'enabled' if self.use_neural_model else 'disabled'}")
    
    def _load_algorithm_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load algorithm patterns for recognition
        
        Returns:
            Dictionary mapping algorithm names to regex patterns and optimized implementations
        """
        patterns = {
            "bubble_sort": {
                "pattern": r"def\s+\w+\s*\([^)]*\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):\s*(?:.*?\n)*?\s*if\s+(\w+)\s*\[\s*(\w+)\s*\]\s*>\s*\1\s*\[\s*\2\s*\+\s*1\s*\]",
                "optimized_algorithm": "heap_sort",
                "optimized_code": """def heap_sort(arr):
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    # Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # Swap
        heapify(arr, i, 0)
    
    return arr

def heapify(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    
    # Check if left child exists and is greater than root
    if left < n and arr[left] > arr[largest]:
        largest = left
    
    # Check if right child exists and is greater than largest
    if right < n and arr[right] > arr[largest]:
        largest = right
    
    # Change root if needed
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # Swap
        heapify(arr, n, largest)
"""
            },
            "linear_search": {
                "pattern": r"def\s+\w+\s*\([^)]*\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):\s*(?:.*?\n)*?\s*if\s+(\w+)\s*\[\s*\w+\s*\]\s*==\s*(\w+)",
                "optimized_algorithm": "binary_search",
                "optimized_code": """def binary_search(arr, target):
    if not arr:
        return -1
        
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1  # Target not found
"""
            },
            "recursive_fibonacci": {
                "pattern": r"def\s+(?:fibonacci|fib)\s*\(\s*\w+\s*\):\s*(?:.*?\n)*?\s*if\s+\w+\s*<=\s*[12]:\s*(?:.*?\n)*?\s*return\s+(?:1|\w+)\s*(?:.*?\n)*?\s*return\s+(?:fibonacci|fib)\s*\(\s*\w+\s*-\s*1\s*\)\s*\+\s*(?:fibonacci|fib)\s*\(\s*\w+\s*-\s*2\s*\)",
                "optimized_algorithm": "iterative_fibonacci",
                "optimized_code": """def fibonacci(n):
    if n <= 0:
        return 0
    if n <= 2:
        return 1
        
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
        
    return b
"""
            },
            "selection_sort": {
                "pattern": r"def\s+(?:selection_sort|\w*sort\w*)\s*\(.*?\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):\s*(?:.*?\n)*?\s*(?:min_idx|min_pos|min_i|min_element|smallest)\s*=\s*\w+\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(.*?\):",
                "optimized_algorithm": "quick_sort",
                "optimized_code": """def quick_sort(arr):
    if len(arr) <= 1:
        return arr
        
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
"""
            },
            "insertion_sort": {
                "pattern": r"def\s+(?:insertion_sort|\w*sort\w*)\s*\(.*?\):\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+range\(1,\s*.*?\):\s*(?:.*?\n)*?\s*(?:key|current|val|value|temp|x)\s*=\s*\w+\s*\[\s*\w+\s*\]\s*(?:.*?\n)*?\s*\w+\s*=\s*\w+\s*-\s*1",
                "optimized_algorithm": "merge_sort",
                "optimized_code": """def merge_sort(arr):
    if len(arr) <= 1:
        return arr
        
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)
    
def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result
"""
            },
            "string_concatenation_loop": {
                "pattern": r"def\s+\w+\s*\([^)]*\):\s*(?:.*?\n)*?\s*result\s*=\s*[\"']{2}\s*(?:.*?\n)*?\s*for\s+\w+\s+in\s+.*?:\s*(?:.*?\n)*?\s*result\s*=\s*result\s*\+\s*\w+\s*(?:.*?\n)*?\s*return\s+result",
                "optimized_algorithm": "string_join",
                "optimized_code": """def concatenate_strings(strings):
    # Using string join is much more efficient than concatenation in a loop
    return ''.join(strings)
"""
            }
        }
        
        return patterns
    
    def load_codebert_model(self, model_path: str = None) -> None:
        """
        Load pre-trained or fine-tuned CodeBERT model
        
        Args:
            model_path: Path to fine-tuned model, or None for pre-trained
        """
        if not self.use_neural_model:
            logger.info("Neural model disabled, skipping model loading")
            return
            
        try:
            # Initialize tokenizer
            logger.info(f"Loading tokenizer from {self.model_name}")
            self.tokenizer = RobertaTokenizer.from_pretrained(self.model_name)
            
            # Load the model
            if model_path and os.path.exists(model_path):
                # Try to determine model type from config
                try:
                    with open(os.path.join(model_path, 'config.json'), 'r') as f:
                        config = json.load(f)
                    model_type = config.get('model_type', '')
                    
                    # Load appropriate model type
                    if 't5' in model_type.lower():
                        logger.info(f"Loading T5 model from {model_path}")
                        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
                        self.seq2seq_model_obj = self.model
                        self.seq2seq_tokenizer = AutoTokenizer.from_pretrained(model_path)
                    else:
                        logger.info(f"Loading RoBERTa model from {model_path}")
                        self.model = RobertaForCausalLM.from_pretrained(model_path)
                except Exception as e:
                    # Default to RobertaForCausalLM if can't determine
                    logger.warning(f"Error loading model config, using default: {str(e)}")
                    self.model = RobertaForCausalLM.from_pretrained(model_path)
                    
                logger.info(f"Loaded fine-tuned model from {model_path}")
            else:
                # Load CodeT5 for code optimization
                try:
                    logger.info(f"Loading CodeT5 model from {self.seq2seq_model}")
                    self.model = T5ForConditionalGeneration.from_pretrained(self.seq2seq_model)
                    self.seq2seq_model_obj = self.model
                    self.seq2seq_tokenizer = AutoTokenizer.from_pretrained(self.seq2seq_model)
                except Exception as e:
                    logger.warning(f"Failed to load CodeT5, falling back to base model: {str(e)}")
                    try:
                        # Try CodeBERT for masked language modeling
                        logger.info(f"Loading CodeBERT model from {self.model_name}")
                        self.model = RobertaForMaskedLM.from_pretrained(self.model_name)
                    except Exception as e2:
                        logger.error(f"Failed to load neural models: {str(e2)}")
                        logger.warning("Disabling neural optimization due to model loading failure")
                        self.use_neural_model = False
                        return
                
                logger.info("Loaded pre-trained model")
            
            # Move model to device
            self.model.to(self.device)
            if self.seq2seq_model_obj and self.seq2seq_model_obj != self.model:
                self.seq2seq_model_obj.to(self.device)
            
            logger.info(f"Model loaded successfully and moved to {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.warning("Continuing with pattern and rule-based optimization only")
            self.use_neural_model = False
    
    def tokenize_code(self, code: str) -> Dict[str, torch.Tensor]:
        """
        Convert code to tokens for model input
        
        Args:
            code: Python code as string
        
        Returns:
            Dictionary of tokenized inputs
        """
        if not self.tokenizer:
            raise ValueError("Tokenizer not initialized. Call load_codebert_model first.")
        
        tokens = self.tokenizer(
            code,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "input_ids": tokens["input_ids"].to(self.device),
            "attention_mask": tokens["attention_mask"].to(self.device)
        }
    
    def fine_tune_codebert(self, 
                          training_data: Union[pd.DataFrame, List[Tuple[str, str]]],
                          output_dir: str = None,
                          validation_data: Optional[Union[pd.DataFrame, List[Tuple[str, str]]]] = None,
                          batch_size: int = 8,
                          epochs: int = 3,
                          learning_rate: float = 5e-5) -> Dict[str, Any]:
        """
        Fine-tune CodeBERT on algorithm dataset
        
        Args:
            training_data: DataFrame or list of (unoptimized, optimized) code pairs
            output_dir: Directory to save fine-tuned model
            validation_data: Optional validation data
            batch_size: Training batch size
            epochs: Number of training epochs
            learning_rate: Learning rate
            
        Returns:
            Dictionary with training metrics
        """
        if not self.use_neural_model:
            logger.warning("Neural model disabled, skipping fine-tuning")
            return {"error": "Neural model disabled"}
            
        if self.model is None or self.tokenizer is None:
            logger.info("Model not initialized, loading pre-trained model")
            self.load_codebert_model()
        
        # Set output directory
        if output_dir is None:
            output_dir = os.path.join(self.model_dir, 'fine_tuned')
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Fine-tuning model on {len(training_data)} samples")
        
        # Prepare data
        if isinstance(training_data, pd.DataFrame):
            # Extract code pairs from DataFrame
            if 'code' in training_data.columns and 'alternative_code' in training_data.columns:
                train_pairs = list(zip(training_data['code'].tolist(), 
                                      training_data['alternative_code'].tolist()))
            else:
                raise ValueError("DataFrame must contain 'code' and 'alternative_code' columns")
            
            if validation_data is not None and isinstance(validation_data, pd.DataFrame):
                val_pairs = list(zip(validation_data['code'].tolist(), 
                                    validation_data['alternative_code'].tolist()))
            else:
                val_pairs = None
        else:
            # Assume list of tuples
            train_pairs = training_data
            val_pairs = validation_data
        
        # Create datasets
        train_dataset = CodeOptimizationDataset(
            tokenizer=self.seq2seq_tokenizer if hasattr(self, 'seq2seq_tokenizer') and self.seq2seq_tokenizer else self.tokenizer,
            code_pairs=train_pairs,
            max_length=self.max_length
        )
        
        if val_pairs:
            val_dataset = CodeOptimizationDataset(
                tokenizer=self.seq2seq_tokenizer if hasattr(self, 'seq2seq_tokenizer') and self.seq2seq_tokenizer else self.tokenizer,
                code_pairs=val_pairs,
                max_length=self.max_length
            )
        else:
            val_dataset = None
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=os.path.join(output_dir, 'checkpoints'),
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            logging_dir=os.path.join(output_dir, 'logs'),
            logging_steps=100,
            save_steps=500,
            evaluation_strategy='steps' if val_dataset else 'no',
            save_total_limit=2,
            load_best_model_at_end=True if val_dataset else False,
            fp16=torch.cuda.is_available(),  # Use mixed precision if available
        )
        
        # Select model for training
        trainer_model = self.seq2seq_model_obj if hasattr(self, 'seq2seq_model_obj') and self.seq2seq_model_obj else self.model
        
        # Initialize trainer
        trainer = Trainer(
            model=trainer_model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset
        )
        
        # Start training
        try:
            logger.info("Starting fine-tuning...")
            train_result = trainer.train()
            
            # Save model
            final_model_path = os.path.join(output_dir, 'final_model')
            trainer.save_model(final_model_path)
            
            # Save tokenizer
            if hasattr(self, 'seq2seq_tokenizer') and self.seq2seq_tokenizer:
                self.seq2seq_tokenizer.save_pretrained(final_model_path)
            else:
                self.tokenizer.save_pretrained(final_model_path)
            
            logger.info(f"Fine-tuning complete. Model saved to {final_model_path}")
            
            # Return metrics
            return {
                "train_loss": trainer.state.log_history[-1]['loss'] if trainer.state.log_history else None,
                "eval_loss": trainer.state.log_history[-1].get('eval_loss', None) if trainer.state.log_history else None,
                "model_path": final_model_path
            }
            
        except Exception as e:
            logger.error(f"Error during fine-tuning: {str(e)}")
            return {"error": str(e)}
    
    def _recognize_algorithm(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Recognize algorithm pattern in code
        
        Args:
            code: Python code as string
            
        Returns:
            Dictionary with recognized algorithm info or None if not recognized
        """
        for algo_name, algo_info in self.algorithm_patterns.items():
            if re.search(algo_info["pattern"], code, re.DOTALL):
                logger.info(f"Recognized {algo_name} algorithm pattern")
                return {
                    "name": algo_name,
                    "optimized_algorithm": algo_info["optimized_algorithm"],
                    "optimized_code": algo_info["optimized_code"]
                }
        
        return None
    
    def _apply_rule_based_optimizations(self, code: str) -> str:
        """
        Apply rule-based optimizations using the dedicated rule_based module
        
        Args:
            code: Python code as string
            
        Returns:
            Optimized code as string
        """
        # Return original code if empty
        if not code.strip():
            return code
        
        try:
            # Use the dedicated rule-based optimization module
            # rule_based_optimize returns (optimized_code, changes_made)
            optimized_code, _ = rule_based_optimize(code)
            return optimized_code
            
        except Exception as e:
            logger.warning(f"Error in rule-based optimization: {str(e)}")
            return code  # Return original code on error
    
    def _validate_neural_output(self, original_code: str, optimized_code: str) -> bool:
        """
        Validate the neural model's output more strictly
        
        Args:
            original_code: Original code string
            optimized_code: Optimized code from neural model
            
        Returns:
            True if the optimization is valid, False otherwise
        """
        # Check for empty or too short output
        if not optimized_code or len(optimized_code.strip()) < 10:
            logger.warning("Neural model output too short")
            return False
            
        # Check length - reject if too short compared to original
        if len(optimized_code) < len(original_code) * 0.5:
            logger.warning("Neural model output suspiciously short compared to original")
            return False
        
        # Extract function name from original code
        func_match = re.search(r'def\s+(\w+)\s*\(', original_code)
        if func_match:
            original_func_name = func_match.group(1)
            
            # Check if the function name is preserved
            if f"def {original_func_name}" not in optimized_code:
                logger.warning(f"Neural model changed function name from {original_func_name}")
                return False
                
        # Check if it's actual code, not just a word or phrase
        if 'def ' not in optimized_code:
            logger.warning("Neural model output doesn't contain function definition")
            return False
            
        # Try to parse with ast
        try:
            ast.parse(optimized_code)
            return True
        except SyntaxError as e:
            logger.warning(f"Neural model output has syntax errors: {str(e)}")
            return False
            
        return True
    
    def _evaluate_code_quality(self, original_code: str, optimized_code: str) -> float:
        """
        Evaluate the quality improvement of the optimized code
        
        Args:
            original_code: Original code string
            optimized_code: Optimized code string
            
        Returns:
            Quality score (higher is better)
        """
        # Simple heuristics for code quality improvement
        score = 0.0
        
        # Check if code got shorter (usually a good sign)
        if len(optimized_code) < len(original_code):
            score += 1.0
        
        # Check for reduction in loops
        orig_loops = original_code.count("for ") + original_code.count("while ")
        opt_loops = optimized_code.count("for ") + optimized_code.count("while ")
        if opt_loops < orig_loops:
            score += 1.5
        
        # Check for reduction in if statements (usually simpler code)
        orig_ifs = original_code.count("if ")
        opt_ifs = optimized_code.count("if ")
        if opt_ifs < orig_ifs:
            score += 0.5
        
        # Check for use of better data structures
        if "set(" in optimized_code and "set(" not in original_code:
            score += 1.0  # Sets are typically faster for lookups
            
        if "dict(" in optimized_code and "dict(" not in original_code:
            score += 0.5  # Dictionaries can improve performance
            
        # Check for recursion elimination
        if (original_code.count("def ") == optimized_code.count("def ") and
            "return " + original_code.split("def ")[1].split("(")[0] in original_code and
            "return " + original_code.split("def ")[1].split("(")[0] not in optimized_code):
            score += 2.0  # Eliminating recursion often improves performance
            
        # Check for string join usage
        if "'.join" in optimized_code or '".join' in optimized_code:
            score += 1.5  # Using join instead of string concatenation is a good optimization
        
        return min(5.0, score)  # Cap score at 5.0
    
    @timeout(30)  # Default timeout of 30 seconds
    def _generate_neural_optimization(self, input_code: str) -> str:
        """
        Generate optimized code using neural model with timeout
        
        Args:
            input_code: Code to optimize
            
        Returns:
            Optimized code
        """
        if isinstance(self.model, T5ForConditionalGeneration):
            # For T5-based models
            # Add a detailed prompt to guide the model towards optimization
            input_with_prompt = (
                "Optimize this Python code for better performance and readability.\n"
                "Ensure it maintains the same functionality.\n"
                "Remove unused variables, simplify loops, and use efficient data structures.\n"
                "The function name and parameters must remain the same.\n\n"
                f"{input_code}"
            )
            
            input_tokens = self.seq2seq_tokenizer(
                input_with_prompt,
                truncation=True,
                max_length=self.max_length,
                padding="max_length",
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                output_ids = self.model.generate(
                    input_ids=input_tokens["input_ids"],
                    attention_mask=input_tokens["attention_mask"],
                    max_length=self.max_length,
                    num_beams=5,
                    early_stopping=True,
                    temperature=0.7,
                    num_return_sequences=1
                )
            
            optimized_code = self.seq2seq_tokenizer.decode(
                output_ids[0], 
                skip_special_tokens=True
            )
            
        else:
            # For RoBERTa-based models
            tokens = self.tokenize_code(input_code)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=tokens["input_ids"],
                    attention_mask=tokens["attention_mask"],
                    max_length=self.max_length,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            optimized_code = self.tokenizer.decode(
                outputs[0], 
                skip_special_tokens=True
            )
        
        return optimized_code
    
    def generate_optimized_code(self, input_code: str) -> Dict[str, Any]:
        """
        Generate optimized version of input code
        
        Args:
            input_code: Unoptimized Python code as string
            
        Returns:
            Dictionary with optimized code and metadata
        """
        if not input_code.strip():
            return {
                "original_code": input_code,
                "optimized_code": input_code,
                "optimization_method": "none",
                "message": "Empty input code",
                "quality_score": 0.0
            }
        
        try:
            start_time = time.time()
            
            # Step 1: Check if code matches a known algorithm pattern
            algorithm_match = self._recognize_algorithm(input_code)
            
            if algorithm_match:
                # Use pattern-based optimization for recognized algorithms
                optimized_code = algorithm_match["optimized_code"]
                optimization_method = "pattern"
                message = f"Recognized {algorithm_match['name']} algorithm, replaced with {algorithm_match['optimized_algorithm']}"
                quality_score = 5.0  # Highest score for pattern-based optimization
                
            elif self.use_neural_model and self.model is not None:
                # Step 2: For unrecognized patterns, try neural model if available
                try:
                    logger.info("Algorithm not recognized, using neural model for optimization")
                    
                    # Generate output using neural model with timeout
                    try:
                        optimized_code = self._generate_neural_optimization(input_code)
                        
                        # Validate the neural output more strictly
                        is_valid = self._validate_neural_output(input_code, optimized_code)
                        
                        if is_valid and optimized_code.strip() != input_code.strip():
                            # Calculate quality score
                            quality_score = self._evaluate_code_quality(input_code, optimized_code)
                            optimization_method = "neural"
                            message = f"Optimized using neural model (quality score: {quality_score:.1f}/5.0)"
                        else:
                            # Fall back to rule-based optimizations
                            logger.info("Neural model output invalid, trying rule-based optimizations")
                            optimized_code = self._apply_rule_based_optimizations(input_code)
                            
                            if optimized_code.strip() != input_code.strip():
                                quality_score = self._evaluate_code_quality(input_code, optimized_code)
                                optimization_method = "rule-based"
                                message = f"Applied rule-based optimizations (quality score: {quality_score:.1f}/5.0)"
                            else:
                                optimized_code = input_code
                                quality_score = 0.0
                                optimization_method = "none"
                                message = "No optimizations applied"
                    
                    except TimeoutError:
                        logger.warning(f"Neural model inference timed out after {self.neural_timeout} seconds")
                        # Fall back to rule-based optimizations
                        optimized_code = self._apply_rule_based_optimizations(input_code)
                        
                        if optimized_code.strip() != input_code.strip():
                            quality_score = self._evaluate_code_quality(input_code, optimized_code)
                            optimization_method = "rule-based"
                            message = f"Applied rule-based optimizations after neural timeout (quality score: {quality_score:.1f}/5.0)"
                        else:
                            optimized_code = input_code
                            quality_score = 0.0
                            optimization_method = "none"
                            message = "No optimizations applied (neural model timed out)"
                        
                except Exception as e:
                    logger.warning(f"Neural optimization failed: {str(e)}")
                    # Fall back to rule-based optimizations
                    optimized_code = self._apply_rule_based_optimizations(input_code)
                    
                    if optimized_code.strip() != input_code.strip():
                        quality_score = self._evaluate_code_quality(input_code, optimized_code)
                        optimization_method = "rule-based"
                        message = f"Applied rule-based optimizations after neural failed (quality score: {quality_score:.1f}/5.0)"
                    else:
                        optimized_code = input_code
                        quality_score = 0.0
                        optimization_method = "none"
                        message = "No optimizations applied"
            else:
                # Step 3: Fall back to rule-based optimizations if model is not loaded
                logger.info("Using rule-based optimizations")
                optimized_code = self._apply_rule_based_optimizations(input_code)
                
                if optimized_code.strip() != input_code.strip():
                    quality_score = self._evaluate_code_quality(input_code, optimized_code)
                    optimization_method = "rule-based"
                    message = f"Applied rule-based optimizations (quality score: {quality_score:.1f}/5.0)"
                else:
                    optimized_code = input_code
                    quality_score = 0.0
                    optimization_method = "none"
                    message = "No optimizations applied"
            
            # Final validation
            try:
                ast.parse(optimized_code)
            except SyntaxError:
                logger.warning("Generated code has syntax errors, reverting to original")
                optimized_code = input_code
                optimization_method = "none"
                message = "Optimization failed: Generated code had syntax errors"
                quality_score = 0.0
            
            elapsed_time = time.time() - start_time
            
            return {
                "original_code": input_code,
                "optimized_code": optimized_code,
                "optimization_method": optimization_method,
                "quality_score": quality_score,
                "message": message,
                "processing_time": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Error generating optimized code: {str(e)}")
            return {
                "original_code": input_code,
                "optimized_code": input_code,
                "optimization_method": "error",
                "quality_score": 0.0,
                "message": f"Error: {str(e)}",
                "processing_time": 0.0
            }
    
    def save_model(self, path: str = None) -> None:
        """
        Save fine-tuned model
        
        Args:
            path: Path to save model (default: self.model_dir/fine_tuned)
        """
        if not self.use_neural_model:
            logger.warning("Neural model disabled, skipping save")
            return
            
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not initialized. Call load_codebert_model or fine_tune_codebert first.")
        
        if path is None:
            path = os.path.join(self.model_dir, 'fine_tuned')
        
        os.makedirs(path, exist_ok=True)
        
        try:
            # Save models
            self.model.save_pretrained(path)
            logger.info(f"Model saved to {path}")
            
            if hasattr(self, 'seq2seq_model_obj') and self.seq2seq_model_obj and self.seq2seq_model_obj != self.model:
                seq2seq_path = os.path.join(path, "seq2seq")
                os.makedirs(seq2seq_path, exist_ok=True)
                self.seq2seq_model_obj.save_pretrained(seq2seq_path)
                logger.info(f"Seq2seq model saved to {seq2seq_path}")
            
            # Save tokenizers
            self.tokenizer.save_pretrained(path)
            if hasattr(self, 'seq2seq_tokenizer') and self.seq2seq_tokenizer:
                seq2seq_tokenizer_path = os.path.join(path, "seq2seq_tokenizer")
                os.makedirs(seq2seq_tokenizer_path, exist_ok=True)
                self.seq2seq_tokenizer.save_pretrained(seq2seq_tokenizer_path)
            
            # Save configuration
            config = {
                "model_name": self.model_name,
                "seq2seq_model": self.seq2seq_model,
                "max_length": self.max_length,
                "model_type": self.model.__class__.__name__,
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(os.path.join(path, "config.json"), "w") as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Model configuration saved to {path}/config.json")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def batch_process_code(self, 
                          code_samples: List[str],
                          batch_size: int = 8) -> List[Dict[str, Any]]:
        """
        Process multiple code samples efficiently
        
        Args:
            code_samples: List of code samples to optimize
            batch_size: Batch size for processing
        
        Returns:
            List of optimization results
        """
        results = []
        
        logger.info(f"Processing batch of {len(code_samples)} code samples")
        
        for i, code in enumerate(tqdm(code_samples, desc="Optimizing code")):
            result = self.generate_optimized_code(code)
            results.append(result)
        
        return results


def main():
    """Main function to test the CodeBERT optimizer"""
    try:
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description="Test CodeBERT Optimizer")
        parser.add_argument(
            "--use-neural", 
            action="store_true", 
            help="Enable neural model for optimization"
        )
        parser.add_argument(
            "--code", 
            type=str, 
            default=None,
            help="Path to a Python file to optimize"
        )
        parser.add_argument(
            "--timeout", 
            type=int, 
            default=30,
            help="Timeout for neural model inference in seconds"
        )
        
        args = parser.parse_args()
        
        # Initialize optimizer
        optimizer = CodeBERTOptimizer(use_neural_model=args.use_neural, neural_timeout=args.timeout)
        
        # Load model
        optimizer.load_codebert_model()
        
        # Test codes (either from file or default examples)
        if args.code and os.path.exists(args.code):
            with open(args.code, 'r') as f:
                test_codes = [f.read()]
            logger.info(f"Loaded code from {args.code}")
        else:
            # Default test codes
            test_codes = [
                # Bubble sort
                """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr""",
                
                # Linear search
                """def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1""",
                
                # Recursive Fibonacci
                """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
                
                # Unused variable (for rule-based optimization)
                """def calculate_sum(arr):
    # Unused variable
    x = 100
    total = 0
    for num in arr:
        total += num
    return total""",
                
                # Inefficient string concatenation
                """def concatenate_strings(strings):
    result = ""
    for s in strings:
        result = result + s
    return result"""
            ]
        
        # Process each test code
        for code in test_codes:
            result = optimizer.generate_optimized_code(code)
            
            print("\n" + "-" * 60)
            print(f"Original code:\n{result['original_code']}")
            print("-" * 60)
            print(f"Optimized code ({result['optimization_method']}):\n{result['optimized_code']}")
            print("-" * 60)
            print(f"Message: {result['message']}")
            if 'quality_score' in result:
                print(f"Quality Score: {result['quality_score']:.2f}/5.0")
            if 'processing_time' in result:
                print(f"Processing time: {result['processing_time']:.2f} seconds")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())