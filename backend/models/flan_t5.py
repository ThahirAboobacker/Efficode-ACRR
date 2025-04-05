"""
FLAN-T5 based explanation generator for code optimizations.
"""

import os
import sys
import logging
import time
import functools
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import torch
import numpy as np
from typing import List, Dict, Optional, Union, Any
import pandas as pd
from transformers import T5ForConditionalGeneration, AutoTokenizer
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import Trainer, TrainingArguments
from transformers.data.data_collator import DataCollatorForSeq2Seq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check if CUDA is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")
logger.info(f"PyTorch version: {torch.__version__}")

# Implementation of timeout with ThreadPoolExecutor
def timeout_handler(timeout):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=timeout)
                except TimeoutError:
                    logger.error(f"Function {func.__name__} timed out after {timeout} seconds")
                    raise TimeoutError(f"Function {func.__name__} timed out")
        return wrapper
    return decorator

class FlanT5ExplanationGenerator:
    """
    Generates explanations for code optimizations using FLAN-T5
    """
    
    def __init__(
        self,
        model_name: str = "google/flan-t5-base",  # Using FLAN-T5 Base by default
        device: str = None,
        max_length: int = 512,
        cache_dir: str = None,
        offline_mode: bool = False
    ):
        """
        Initialize the FLAN-T5 explanation generator
        
        Args:
            model_name: Name/path of the model to use
            device: Device to run the model on ('cuda' or 'cpu')
            max_length: Maximum sequence length
            cache_dir: Directory to cache the model
            offline_mode: If True, only use rule-based generation
        """
        self.model_name = model_name
        self.max_length = max_length
        self.offline_mode = offline_mode
        
        # Set device
        if device is None:
            self.device = DEVICE
        else:
            self.device = device
            
        # Set cache directory
        if cache_dir is None:
            # Default to a subdirectory in the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.cache_dir = os.path.join(current_dir, "flan_t5_cache")
        else:
            self.cache_dir = cache_dir
        
        # Initialize model and tokenizer as None
        self.model = None
        self.tokenizer = None
        
        # Log initialization
        logger.info(f"Initialized FLAN-T5 explanation generator with model: {model_name}")
        logger.info(f"Using device: {self.device}")
        logger.info(f"Cache directory: {self.cache_dir}")
        
        if not offline_mode:
            try:
                self.load_model()
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
                logger.warning("Falling back to rule-based generation only")
                self.offline_mode = True

    def load_model(self, model_path: str = None, timeout: int = 180) -> bool:
        """Load the FLAN-T5 model and tokenizer with timeout"""
        if self.offline_mode:
            return False
            
        def _load():
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_path or self.model_name,
                    cache_dir=self.cache_dir
                )
                self.model = T5ForConditionalGeneration.from_pretrained(
                    model_path or self.model_name,
                    cache_dir=self.cache_dir
                )
                self.model.to(self.device)
                return True
            except Exception as e:
                logger.error(f"Error in model loading: {e}")
                return False
                
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_load)
                return future.result(timeout=timeout)
        except TimeoutError:
            logger.error(f"Model loading timed out after {timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
            
    def _explain_complexity_change(self, complexity_before: str, complexity_after: str) -> str:
        """Generate explanation for complexity changes"""
        def _parse_complexity(complexity: str) -> str:
            if complexity.lower() == "o(1)":
                return "constant"
            elif "log" in complexity.lower():
                if "n log n" in complexity.lower():
                    return "linearithmic"
                return "logarithmic"
            elif "n²" in complexity or "n^2" in complexity:
                return "quadratic"
            elif "n³" in complexity or "n^3" in complexity:
                return "cubic"
            elif "2^n" in complexity:
                return "exponential"
            elif "n" in complexity and "²" not in complexity and "³" not in complexity:
                return "linear"
            else:
                return "constant"

        before_type = _parse_complexity(complexity_before)
        after_type = _parse_complexity(complexity_after)

        explanation = (
            f"The algorithm's time complexity has been improved from {complexity_before} "
            f"({before_type} complexity) to {complexity_after} ({after_type} complexity). "
        )

        # Add specific performance implications
        if before_type == "quadratic" and after_type in ["linearithmic", "linear", "logarithmic"]:
            explanation += (
                f"This is a substantial improvement - for an array of 1000 elements, "
                f"the original algorithm would take roughly 1,000,000 steps, while "
                f"the optimized version only takes about {10000 if after_type == 'linearithmic' else 1000 if after_type == 'linear' else 10} steps. "
            )
        elif before_type == "cubic" and after_type in ["quadratic", "linearithmic", "linear"]:
            explanation += (
                f"This is a dramatic improvement - for an input of size 100, "
                f"the original algorithm would take 1,000,000 steps, while "
                f"the optimized version would take only {10000 if after_type == 'quadratic' else 1000 if after_type == 'linearithmic' else 100} steps. "
            )

        # Add algorithm characteristics
        if after_type == "linearithmic":
            explanation += (
                f"The optimized version achieves this efficiency through the use of "
                f"divide-and-conquer or efficient sorting algorithms. "
            )
        elif after_type == "logarithmic":
            explanation += (
                f"The logarithmic complexity indicates the algorithm probably uses "
                f"binary search or tree-based data structures. "
            )
        elif after_type == "linear":
            explanation += (
                f"The linear complexity suggests the algorithm makes a single pass through the data, "
                f"which is often optimal for problems requiring all elements to be processed. "
            )

        return explanation

    def generate_rule_based_explanation(
        self, 
        original_code: str, 
        optimized_code: str, 
        complexity_before: str, 
        complexity_after: str, 
        applied_rules: List[str] = None
    ) -> str:
        """Generate explanation using rule-based approach"""
        try:
            # Start with complexity explanation
            explanation = self._explain_complexity_change(complexity_before, complexity_after)
            
            # Add optimization techniques
            if applied_rules:
                explanation += "\n\n## Optimization Techniques Applied\n"
                for rule in applied_rules:
                    explanation += f"- {rule}\n"

            # Add algorithm-specific analysis
            if "quick_sort" in optimized_code and "bubble_sort" in original_code:
                explanation += "\n## Algorithm Analysis\n"
                explanation += (
                    "### Bubble Sort (Original)\n"
                    "- Best Case: O(n) - when array is already sorted\n"
                    "- Average Case: O(n²)\n"
                    "- Worst Case: O(n²) - when array is reverse sorted\n"
                    "- Space Complexity: O(1) - in-place sorting\n"
                    "\n"
                    "### Quick Sort (Optimized)\n"
                    "- Best Case: O(n log n)\n"
                    "- Average Case: O(n log n)\n"
                    "- Worst Case: O(n²) - rare, occurs with poor pivot selection\n"
                    "- Space Complexity: O(log n) for recursion stack\n"
                )

            # Add implementation analysis
            explanation += "\n## Implementation Analysis\n"
            explanation += (
                "The implementation replaces bubble sort with quick sort using these key changes:\n"
                "1. Pivot Selection: Uses middle element as pivot for better average-case performance\n"
                "2. Partitioning: Uses list comprehensions for clean, readable partitioning\n"
                "3. Recursion: Implements divide-and-conquer through recursive calls\n"
            )

            # Add memory and performance trade-offs
            explanation += "\n## Trade-offs\n"
            explanation += (
                "### Performance Benefits\n"
                "- Reduced comparisons: From O(n²) to O(n log n) on average\n"
                "- Better cache utilization due to divide-and-conquer approach\n"
                "- More efficient for large datasets\n"
                "\n"
                "### Memory Considerations\n"
                "- Increased space usage due to partitioning arrays\n"
                "- Recursive call stack overhead\n"
                "- Trade-off: Uses more memory for better time complexity\n"
            )

            # Add visualization suggestions
            explanation += "\n## Visualization Suggestions\n"
            explanation += (
                "To better understand the algorithms:\n"
                "1. Time Complexity Graph:\n"
                "   - X-axis: Input size (n)\n"
                "   - Y-axis: Operations\n"
                "   - Plot both O(n²) and O(n log n) curves\n"
                "\n"
                "2. Algorithm Steps:\n"
                "   - Bubble Sort: Show adjacent element comparisons\n"
                "   - Quick Sort: Show pivot selection and partitioning\n"
                "\n"
                "3. Memory Usage:\n"
                "   - Stack visualization for recursive calls\n"
                "   - Space allocation for partitions\n"
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error in rule-based explanation generation: {e}")
            return (
                f"The code was optimized from {complexity_before} to {complexity_after}. "
                f"The optimization applied standard techniques to improve performance."
            )
        
    def generate_explanation(
        self, 
        original_code: str, 
        optimized_code: str, 
        complexity_before: str, 
        complexity_after: str,
        applied_rules: List[str] = None,
        num_beams: int = 4,
        temperature: float = 0.7,
        max_length: int = 512,
        force_rule_based: bool = False
    ) -> str:
        """Generate explanation for code optimization"""
        if force_rule_based or self.offline_mode:
            logger.info("Using rule-based explanation generation")
            return self.generate_rule_based_explanation(
                original_code, 
                optimized_code, 
                complexity_before, 
                complexity_after,
                applied_rules
            )
        
        try:
            # Attempt neural generation
            if self.model is None or self.tokenizer is None:
                self.load_model()
            
            if self.model is None or self.tokenizer is None:
                logger.warning("Model not available, falling back to rule-based generation")
                return self.generate_rule_based_explanation(
                    original_code, 
                    optimized_code, 
                    complexity_before, 
                    complexity_after,
                    applied_rules
                )
            
            # Construct prompt
            prompt = f"""
            Original Code:
            {original_code}
            
            Optimized Code:
            {optimized_code}
            
            Original Complexity: {complexity_before}
            Optimized Complexity: {complexity_after}
            
            Explain the optimization:
            """
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    num_beams=num_beams,
                    temperature=temperature,
                    early_stopping=True
                )
            
            explanation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Format the explanation
            explanation = explanation.strip()
            if not explanation:
                # Fallback if empty explanation
                logger.warning("Empty explanation generated, falling back to rule-based")
                return self.generate_rule_based_explanation(
                    original_code, 
                    optimized_code, 
                    complexity_before, 
                    complexity_after,
                    applied_rules
                )
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error in neural explanation generation: {e}")
            logger.info("Falling back to rule-based explanation generation")
            return self.generate_rule_based_explanation(
                original_code, 
                optimized_code, 
                complexity_before, 
                complexity_after,
                applied_rules
            )
    
    def format_explanation(self, explanation: str) -> str:
        """
        Format an explanation for better readability.
        
        Args:
            explanation: Raw explanation text
            
        Returns:
            Formatted explanation with proper sectioning and formatting
        """
        # Check if the explanation is very short or incomplete
        if len(explanation.strip()) < 50:
            # This might be an incomplete or low-quality output from the model
            logger.warning("Received very short explanation, falling back to rule-based formatting")
            return self.generate_rule_based_explanation(
                "# Placeholder for original code",
                "# Placeholder for optimized code",
                "O(n)",
                "O(log n)",
                ["Model output was insufficient, using rule-based explanation instead"]
            )
            
        # Split the explanation into sections if possible
        sections = []
        
        # Try to identify key sections in the explanation
        if "Algorithm Change:" in explanation or "Optimization Technique:" in explanation:
            parts = explanation.split("\n\n")
            formatted_parts = []
            
            for part in parts:
                if part.startswith("Algorithm Change:") or part.startswith("Optimization Technique:"):
                    formatted_parts.append(f"### {part}")
                elif part.startswith("Complexity Analysis:"):
                    formatted_parts.append(f"### {part}")
                elif part.startswith("Key Improvements:"):
                    formatted_parts.append(f"### {part}")
                else:
                    formatted_parts.append(part)
                    
            return "\n\n".join(formatted_parts)
        else:
            # If no clear sections, add some basic formatting
            lines = explanation.split("\n")
            formatted_lines = []
            
            i = 0
            while i < len(lines):
                # Check if the line might be a heading
                if i < len(lines) - 1 and lines[i] and not lines[i+1].strip():
                    formatted_lines.append(f"### {lines[i]}")
                    i += 2
                else:
                    formatted_lines.append(lines[i])
                    i += 1
                    
            return "\n".join(formatted_lines)
        
    def batch_generate_explanations(
        self, 
        code_pairs: List[Dict[str, Any]],
        batch_size: int = 4,  # Reduced for FLAN-T5 Base (uses more memory)
        force_rule_based: bool = False
    ) -> List[str]:
        """
        Generate explanations for multiple code pairs in batches.
        
        Args:
            code_pairs: List of dictionaries, each containing 'original_code', 'optimized_code',
                       'complexity_before', 'complexity_after', and optionally 'applied_rules'
            batch_size: Number of explanations to generate in each batch
            force_rule_based: Force using rule-based explanation even if model is available
            
        Returns:
            List of generated explanations
        """
        # Check if we should use rule-based generation
        if force_rule_based or not self.load_model():
            logger.warning("Using rule-based batch explanation generation (model not available)")
            explanations = []
            for pair in code_pairs:
                explanation = self.generate_rule_based_explanation(
                    pair['original_code'],
                    pair['optimized_code'],
                    pair['complexity_before'],
                    pair['complexity_after'],
                    pair.get('applied_rules', [])
                )
                explanations.append(explanation)
            return explanations
            
        explanations = []
        
        for i in tqdm(range(0, len(code_pairs), batch_size), desc="Generating explanations"):
            batch = code_pairs[i:i+batch_size]
            
            # Create prompts for the batch with improved instructions
            prompts = []
            for pair in batch:
                # Include applied rules if available
                if 'applied_rules' in pair and pair['applied_rules'] and len(pair['applied_rules']) > 0:
                    rules_text = "\n".join([f"- {rule}" for rule in pair['applied_rules']])
                    prompt = (
                        f"Create a detailed and educational explanation of the following code optimization, from the original code to the optimized version. "
                        f"The code complexity changes from {pair['complexity_before']} to {pair['complexity_after']}.\n\n"
                        f"The following optimization techniques were applied:\n{rules_text}\n\n"
                        f"Original Code:\n```python\n{pair['original_code']}\n```\n\n"
                        f"Optimized Code:\n```python\n{pair['optimized_code']}\n```\n\n"
                        f"Your explanation should include:\n"
                        f"1. A clear explanation of each optimization technique applied and why it improves performance\n"
                        f"2. An analysis of the time and space complexity changes\n"
                        f"3. A breakdown of the specific code changes and how they implement the optimizations\n"
                        f"4. Any trade-offs introduced by the optimization"
                    )
                else:
                    prompt = (
                        f"Create a detailed and educational explanation of the following code optimization, from the original code to the optimized version. "
                        f"The code complexity changes from {pair['complexity_before']} to {pair['complexity_after']}.\n\n"
                        f"Original Code:\n```python\n{pair['original_code']}\n```\n\n"
                        f"Optimized Code:\n```python\n{pair['optimized_code']}\n```\n\n"
                        f"Your explanation should include:\n"
                        f"1. A clear identification and explanation of each optimization technique applied and why it improves performance\n"
                        f"2. An analysis of the time and space complexity changes\n"
                        f"3. A breakdown of the specific code changes and how they implement the optimizations\n"
                        f"4. Any trade-offs introduced by the optimization"
                    )
                prompts.append(prompt)
                
            # Tokenize the prompts
            inputs = self.tokenizer(
                prompts, 
                return_tensors="pt",
                max_length=self.max_length,
                padding=True,
                truncation=True
            ).to(self.device)
            
            # Generate explanations with improved parameters
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=1024,  # Increased from default
                    num_beams=5,      # Increased for better quality
                    temperature=0.5,  # Reduced for more focused output
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    length_penalty=1.0,
                    top_k=50,
                    top_p=0.95
                )
                
            # Decode the outputs and post-process
            batch_explanations = []
            for output in outputs:
                explanation = self.tokenizer.decode(output, skip_special_tokens=True)
                
                # Post-process to add heading if missing
                if not explanation.startswith("# ") and not explanation.startswith("## "):
                    explanation = "# Code Optimization Explanation\n\n" + explanation
                    
                batch_explanations.append(explanation)
                
            explanations.extend(batch_explanations)
            
        return explanations

    def fine_tune(
        self,
        training_data: Union[pd.DataFrame, Dataset],
        output_dir: str = "./flan_t5_fine_tuned",
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 3e-5,
        eval_data: Optional[Union[pd.DataFrame, Dataset]] = None,
        max_input_length: int = 512,
        max_target_length: int = 512,
    ) -> Dict[str, Any]:
        """
        Fine-tune the FLAN-T5 model on code optimization explanations.
        
        Args:
            training_data: DataFrame with original code, optimized code, and explanations
            output_dir: Directory to save the fine-tuned model
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for training
            eval_data: Optional evaluation dataset
            max_input_length: Maximum length for inputs
            max_target_length: Maximum length for outputs
            
        Returns:
            Dict with training metrics
        """
        # Check if model is loaded
        if self.model is None:
            logger.info("Model is not loaded, loading now")
            if not self.load_model():
                logger.error("Failed to load model, cannot fine-tune")
                return {"error": "Failed to load model"}
        else:
            logger.info("Model is already loaded")
        
        logger.info("Preparing data for fine-tuning")
            
        # Prepare dataset
        tokenized_train_dataset = self._prepare_dataset(
            training_data, 
            max_input_length=max_input_length, 
            max_target_length=max_target_length
        )
        
        # Prepare evaluation dataset if provided
        tokenized_eval_dataset = None
        if eval_data is not None:
            tokenized_eval_dataset = self._prepare_dataset(
                eval_data, 
                max_input_length=max_input_length, 
                max_target_length=max_target_length
            )
        
        # Set up training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="epoch" if tokenized_eval_dataset else "no",
            save_strategy="epoch",
            learning_rate=learning_rate,
            load_best_model_at_end=True if tokenized_eval_dataset else False,
            save_total_limit=2,  # Keep only the 2 best checkpoints
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model,
            padding="max_length",
            max_length=max_target_length
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train_dataset,
            eval_dataset=tokenized_eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator
        )
        
        # Start training
        logger.info("Starting fine-tuning process")
        train_result = trainer.train()
        
        # Save the fine-tuned model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        logger.info(f"Model fine-tuning complete. Model saved to {output_dir}")
        
        # Extract and return metrics
        metrics = {
            "train_runtime": train_result.metrics.get("train_runtime", 0),
            "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
            "train_steps_per_second": train_result.metrics.get("train_steps_per_second", 0),
            "train_loss": None,  # Initialize with None in case it's not available
        }
        
        # Safely extract loss from log history
        if trainer.state.log_history:
            for entry in reversed(trainer.state.log_history):
                if 'loss' in entry:
                    metrics["train_loss"] = entry['loss']
                    break
        
        return metrics
        
    def _prepare_dataset(self, df: pd.DataFrame, max_input_length: int, max_target_length: int) -> Dataset:
        """
        Prepare a dataset for fine-tuning from a DataFrame.
        
        Args:
            df: DataFrame with columns 'original_code', 'optimized_code', 
                'complexity_before', 'complexity_after', and 'explanation'
            max_input_length: Maximum length for inputs
            max_target_length: Maximum length for outputs
                
        Returns:
            HuggingFace Dataset ready for training
        """
        # Ensure required columns exist
        required_cols = ['original_code', 'optimized_code', 'complexity_before', 'complexity_after', 'explanation']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in the DataFrame")
                
        # Create input prompts and target explanations
        prompts = []
        targets = []
        
        for _, row in df.iterrows():
            # Check if applied_rules are available and include them in the prompt
            if 'applied_rules' in df.columns and isinstance(row['applied_rules'], list) and len(row['applied_rules']) > 0:
                rules_text = "\n".join([f"- {rule}" for rule in row['applied_rules']])
                prompt = (
                    f"Create a detailed and educational explanation of the following code optimization, from the original code to the optimized version. "
                    f"The code complexity changes from {row['complexity_before']} to {row['complexity_after']}.\n\n"
                    f"The following optimization techniques were applied:\n{rules_text}\n\n"
                    f"Original Code:\n```python\n{row['original_code']}\n```\n\n"
                    f"Optimized Code:\n```python\n{row['optimized_code']}\n```\n\n"
                    f"Your explanation should include:\n"
                    f"1. A clear explanation of each optimization technique applied and why it improves performance\n"
                    f"2. An analysis of the time and space complexity changes\n"
                    f"3. A breakdown of the specific code changes and how they implement the optimizations\n"
                    f"4. Any trade-offs introduced by the optimization"
                )
            else:
                # Create a prompt without rules but with better instructions
                prompt = (
                    f"Create a detailed and educational explanation of the following code optimization, from the original code to the optimized version. "
                    f"The code complexity changes from {row['complexity_before']} to {row['complexity_after']}.\n\n"
                    f"Original Code:\n```python\n{row['original_code']}\n```\n\n"
                    f"Optimized Code:\n```python\n{row['optimized_code']}\n```\n\n"
                    f"Your explanation should include:\n"
                    f"1. A clear identification and explanation of each optimization technique applied and why it improves performance\n"
                    f"2. An analysis of the time and space complexity changes\n"
                    f"3. A breakdown of the specific code changes and how they implement the optimizations\n"
                    f"4. Any trade-offs introduced by the optimization"
                )
            prompts.append(prompt)
            targets.append(row['explanation'])
            
        # Tokenize the inputs and targets
        tokenized_inputs = self.tokenizer(
            prompts, 
            max_length=max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        tokenized_targets = self.tokenizer(
            targets,
            max_length=max_target_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Create dataset
        dataset_dict = {
            "input_ids": tokenized_inputs["input_ids"],
            "attention_mask": tokenized_inputs["attention_mask"],
            "labels": tokenized_targets["input_ids"]
        }
        
        return Dataset.from_dict(dataset_dict)
    
    def evaluate_explanation_quality(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate the quality of generated explanations against reference explanations.
        
        Args:
            test_data: DataFrame with columns 'original_code', 'optimized_code',
                      'complexity_before', 'complexity_after', and 'reference_explanation'
                      
        Returns:
            Dictionary of evaluation metrics
        """
        if not self.load_model():
            logger.error("Cannot evaluate: Model could not be loaded")
            return {"error": "Model loading failed"}
            
        # Import rouge metrics with proper error handling
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        except ImportError:
            logger.warning("rouge_score package not found. Install with 'pip install rouge-score' for evaluation.")
            return {"error": "rouge_score package not installed"}
            
        # Generate explanations
        code_pairs = []
        for _, row in test_data.iterrows():
            code_pair = {
                'original_code': row['original_code'],
                'optimized_code': row['optimized_code'],
                'complexity_before': row['complexity_before'],
                'complexity_after': row['complexity_after']
            }
            
            # Include applied_rules if available
            if 'applied_rules' in row:
                code_pair['applied_rules'] = row['applied_rules']
                
            code_pairs.append(code_pair)
            
        generated_explanations = self.batch_generate_explanations(code_pairs)
        
        # Calculate ROUGE scores
        rouge1_scores = []
        rouge2_scores = []
        rougeL_scores = []
        
        for i, explanation in enumerate(generated_explanations):
            reference = test_data.iloc[i]['reference_explanation']
            scores = scorer.score(reference, explanation)
            
            rouge1_scores.append(scores['rouge1'].fmeasure)
            rouge2_scores.append(scores['rouge2'].fmeasure)
            rougeL_scores.append(scores['rougeL'].fmeasure)
            
        # Calculate average scores
        metrics = {
            'rouge1': np.mean(rouge1_scores),
            'rouge2': np.mean(rouge2_scores),
            'rougeL': np.mean(rougeL_scores)
        }
        
        logger.info(f"Explanation quality evaluation results: {metrics}")
        return metrics
    
    def save_model(self, path: Optional[str] = None) -> None:
        """
        Save the fine-tuned model to a directory.
        
        Args:
            path: Directory path to save the model (default: project_root/backend/models/flan_t5_fine_tuned)
        """
        if self.model is None or self.tokenizer is None:
            logger.error("No model to save. Load or fine-tune a model first.")
            return
            
        # Define current_dir
        current_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Set default path if not provided
        if path is None:
            path = os.path.join(current_dir, "flan_t5_fine_tuned")
            
        try:
            os.makedirs(path, exist_ok=True)
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def generate_explanation_with_custom_prompt(self, prompt: str, max_length: int = 1024) -> str:
        """
        Generate an explanation using a custom prompt.
        
        This is useful for few-shot learning or custom prompting strategies.
        
        Args:
            prompt: The full custom prompt to use
            max_length: Maximum length for the generated explanation
            
        Returns:
            Generated explanation
        """
        if not self.load_model():
            logger.warning("Model not available, falling back to rule-based explanation")
            return self.generate_rule_based_explanation(
                "Custom prompt used", 
                "Custom prompt used",
                "Unknown", 
                "Unknown"
            )
            
        # Tokenize the prompt
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True
        ).to(self.device)
        
        # Generate the explanation
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                num_beams=5,
                temperature=0.7,
                do_sample=True,
                early_stopping=True,
                no_repeat_ngram_size=3,
                length_penalty=1.0,
                top_k=50,
                top_p=0.95
            )
            
        # Decode the output
        explanation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-process the explanation
        if not explanation.startswith("# ") and not explanation.startswith("## "):
            explanation = "# Code Optimization Explanation\n\n" + explanation
            
        return explanation


# Function to create a standalone explanation generator instance
def get_explanation_generator(
    model_path: Optional[str] = None,
    offline_mode: bool = False,
    timeout: int = 300
) -> FlanT5ExplanationGenerator:
    """
    Factory function to get a configured explanation generator.
    
    Args:
        model_path: Optional path to a fine-tuned model
        offline_mode: If True, will use rule-based generation when model is unavailable
        timeout: Timeout in seconds for model loading
        
    Returns:
        Configured FlanT5ExplanationGenerator instance
    """
    generator = FlanT5ExplanationGenerator(offline_mode=offline_mode)
    generator.load_model(model_path, timeout=timeout)
    return generator


# Example usage
if __name__ == "__main__":
    # Test code
    original_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
    """
    
    optimized_code = """
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
    """

    # Create generator in offline mode for testing
    generator = FlanT5ExplanationGenerator(offline_mode=True)
    
    # Test explanation generation with proper try-except block
    try:
        explanation = generator.generate_explanation(
            original_code=original_code,
            optimized_code=optimized_code,
            complexity_before="O(n²)",
            complexity_after="O(n log n)",
            applied_rules=[
                "Replaced bubble sort with quick sort",
                "Used divide and conquer strategy",
                "Eliminated nested loops"
            ],
            force_rule_based=True
        )
        
        print("\nGenerated Explanation:")
        print("-" * 80)
        print(explanation)
        print("-" * 80)
    except Exception as e:
        print(f"Error generating explanation: {e}")