"""
Dataset Management System for EFFICODE-ACRR
Handles synthetic data generation, dataset loading, and preprocessing
"""

import os
import json
import csv
import random
import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import pandas as pd
from dataclasses import asdict

from data_models import TrainingExample, BaseDatasetManager
from config import Config

logger = logging.getLogger('efficode.dataset')

class SyntheticDataGenerator:
    """Generates synthetic training data for optimization models"""
    
    def __init__(self):
        self.algorithm_templates = self._load_algorithm_templates()
    
    def _load_algorithm_templates(self) -> Dict[str, Dict[str, str]]:
        """Load algorithm templates for synthetic generation"""
        return {
            'fibonacci': {
                'recursive': '''def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)''',
                'iterative': '''def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b''',
                'complexity_before': 'O(2^n)',
                'complexity_after': 'O(n)',
                'explanation': 'Replaced exponential recursive algorithm with linear iterative approach'
            },
            'factorial': {
                'recursive': '''def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n-1)''',
                'iterative': '''def factorial(n):
    if n <= 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result''',
                'complexity_before': 'O(n)',
                'complexity_after': 'O(n)',
                'explanation': 'Replaced recursive factorial with iterative approach to reduce call stack overhead'
            },
            'bubble_sort': {
                'basic': '''def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr''',
                'optimized': '''def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr''',
                'complexity_before': 'O(n²)',
                'complexity_after': 'O(n²) worst case, O(n) best case',
                'explanation': 'Added early termination with swapped flag to optimize best-case performance'
            },
            'linear_search': {
                'basic': '''def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1''',
                'optimized': '''def linear_search(arr, target):
    try:
        return arr.index(target)
    except ValueError:
        return -1''',
                'complexity_before': 'O(n)',
                'complexity_after': 'O(n)',
                'explanation': 'Replaced manual loop with built-in index method for better performance'
            },
            'power_calculation': {
                'basic': '''def power(base, exp):
    result = 1
    for i in range(exp):
        result *= base
    return result''',
                'optimized': '''def power(base, exp):
    return base ** exp''',
                'complexity_before': 'O(n)',
                'complexity_after': 'O(1)',
                'explanation': 'Replaced loop-based power calculation with built-in exponentiation operator'
            }
        }
    
    def generate_algorithm_pairs(self, num_samples: int = 1000) -> List[TrainingExample]:
        """Generate algorithm optimization pairs"""
        examples = []
        
        for _ in range(num_samples):
            # Randomly select an algorithm template
            algo_name = random.choice(list(self.algorithm_templates.keys()))
            template = self.algorithm_templates[algo_name]
            
            # Get the optimization pair
            if 'recursive' in template and 'iterative' in template:
                original = template['recursive']
                optimized = template['iterative']
            elif 'basic' in template and 'optimized' in template:
                original = template['basic']
                optimized = template['optimized']
            else:
                continue
            
            example = TrainingExample(
                original_code=original,
                optimized_code=optimized,
                complexity_before=template['complexity_before'],
                complexity_after=template['complexity_after'],
                explanation=template['explanation'],
                applied_rules=[f'{algo_name}_optimization'],
                category=algo_name
            )
            examples.append(example)
        
        return examples
    
    def generate_constant_folding_examples(self, num_samples: int = 500) -> List[TrainingExample]:
        """Generate constant folding examples"""
        examples = []
        
        operations = [
            ('+', lambda a, b: a + b),
            ('-', lambda a, b: a - b),
            ('*', lambda a, b: a * b),
            ('//', lambda a, b: a // b if b != 0 else a),
            ('**', lambda a, b: a ** b if b < 10 else a),
            ('%', lambda a, b: a % b if b != 0 else a)
        ]
        
        for _ in range(num_samples):
            # Generate random constants
            a = random.randint(1, 20)
            b = random.randint(1, 10)
            op_symbol, op_func = random.choice(operations)
            
            try:
                result = op_func(a, b)
                
                original = f'''def calculate():
    x = {a} {op_symbol} {b}
    return x'''
                
                optimized = f'''def calculate():
    x = {result}
    return x'''
                
                example = TrainingExample(
                    original_code=original,
                    optimized_code=optimized,
                    complexity_before='O(1)',
                    complexity_after='O(1)',
                    explanation=f'Folded constant expression {a} {op_symbol} {b} to {result}',
                    applied_rules=['constant_folding'],
                    category='constant_folding'
                )
                examples.append(example)
            except:
                continue
        
        return examples
    
    def generate_loop_optimization_examples(self, num_samples: int = 300) -> List[TrainingExample]:
        """Generate loop optimization examples"""
        examples = []
        
        loop_templates = [
            {
                'original': '''def process_list(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result''',
                'optimized': '''def process_list(items):
    return [item * 2 for item in items]''',
                'explanation': 'Replaced explicit loop with list comprehension'
            },
            {
                'original': '''def sum_squares(n):
    total = 0
    for i in range(n):
        total += i * i
    return total''',
                'optimized': '''def sum_squares(n):
    return sum(i * i for i in range(n))''',
                'explanation': 'Replaced manual accumulation with built-in sum function'
            },
            {
                'original': '''def find_max(arr):
    max_val = arr[0]
    for item in arr[1:]:
        if item > max_val:
            max_val = item
    return max_val''',
                'optimized': '''def find_max(arr):
    return max(arr)''',
                'explanation': 'Replaced manual maximum finding with built-in max function'
            }
        ]
        
        for _ in range(num_samples):
            template = random.choice(loop_templates)
            
            example = TrainingExample(
                original_code=template['original'],
                optimized_code=template['optimized'],
                complexity_before='O(n)',
                complexity_after='O(n)',
                explanation=template['explanation'],
                applied_rules=['loop_optimization'],
                category='loop_optimization'
            )
            examples.append(example)
        
        return examples
    
    def generate_complexity_examples(self) -> List[TrainingExample]:
        """Generate examples for complexity prediction training"""
        examples = []
        
        complexity_templates = [
            ('O(1)', 'def constant_time(): return 42'),
            ('O(n)', 'def linear_time(n): return sum(range(n))'),
            ('O(n²)', 'def quadratic_time(n): return sum(i*j for i in range(n) for j in range(n))'),
            ('O(log n)', 'def binary_search(arr, target): # Binary search implementation'),
            ('O(n log n)', 'def merge_sort(arr): # Merge sort implementation'),
            ('O(2^n)', 'def fibonacci_recursive(n): return fibonacci_recursive(n-1) + fibonacci_recursive(n-2) if n > 1 else n')
        ]
        
        for complexity, code in complexity_templates:
            example = TrainingExample(
                original_code=code,
                optimized_code=code,  # No optimization, just complexity labeling
                complexity_before=complexity,
                complexity_after=complexity,
                explanation=f'Code has {complexity} time complexity',
                applied_rules=[],
                category='complexity_prediction'
            )
            examples.append(example)
        
        return examples

class DatasetManager(BaseDatasetManager):
    """Manages datasets for training and evaluation"""
    
    def __init__(self):
        self.generator = SyntheticDataGenerator()
        self.data_dir = Config.DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
    
    def generate_synthetic_data(self, num_samples: int) -> List[TrainingExample]:
        """Generate synthetic training data"""
        logger.info(f"Generating {num_samples} synthetic training examples")
        
        examples = []
        
        # Generate different types of examples
        algo_samples = int(num_samples * 0.4)  # 40% algorithm optimizations
        const_samples = int(num_samples * 0.3)  # 30% constant folding
        loop_samples = int(num_samples * 0.2)   # 20% loop optimizations
        complexity_samples = int(num_samples * 0.1)  # 10% complexity examples
        
        examples.extend(self.generator.generate_algorithm_pairs(algo_samples))
        examples.extend(self.generator.generate_constant_folding_examples(const_samples))
        examples.extend(self.generator.generate_loop_optimization_examples(loop_samples))
        examples.extend(self.generator.generate_complexity_examples())
        
        # Shuffle the examples
        random.shuffle(examples)
        
        logger.info(f"Generated {len(examples)} synthetic examples")
        return examples[:num_samples]
    
    def load_dataset(self, path: str) -> List[TrainingExample]:
        """Load dataset from file"""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")
        
        examples = []
        
        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    examples.append(TrainingExample(**item))
        
        elif file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                examples.append(TrainingExample(
                    original_code=row['original_code'],
                    optimized_code=row['optimized_code'],
                    complexity_before=row['complexity_before'],
                    complexity_after=row['complexity_after'],
                    explanation=row['explanation'],
                    applied_rules=json.loads(row['applied_rules']) if isinstance(row['applied_rules'], str) else row['applied_rules'],
                    category=row.get('category', 'general')
                ))
        
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        logger.info(f"Loaded {len(examples)} examples from {path}")
        return examples
    
    def save_dataset(self, examples: List[TrainingExample], path: str) -> bool:
        """Save dataset to file"""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if file_path.suffix == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([asdict(ex) for ex in examples], f, indent=2)
            
            elif file_path.suffix == '.csv':
                df = pd.DataFrame([asdict(ex) for ex in examples])
                df['applied_rules'] = df['applied_rules'].apply(json.dumps)
                df.to_csv(file_path, index=False)
            
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            logger.info(f"Saved {len(examples)} examples to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving dataset: {e}")
            return False
    
    def split_dataset(self, examples: List[TrainingExample], 
                     train_ratio: float = 0.8, 
                     val_ratio: float = 0.1, 
                     test_ratio: float = 0.1) -> Tuple[List[TrainingExample], List[TrainingExample], List[TrainingExample]]:
        """Split dataset into train, validation, and test sets"""
        
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
        
        # Shuffle examples
        shuffled = examples.copy()
        random.shuffle(shuffled)
        
        n = len(shuffled)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        train_set = shuffled[:train_end]
        val_set = shuffled[train_end:val_end]
        test_set = shuffled[val_end:]
        
        logger.info(f"Split dataset: {len(train_set)} train, {len(val_set)} val, {len(test_set)} test")
        
        return train_set, val_set, test_set
    
    def augment_dataset(self, examples: List[TrainingExample], 
                       augmentation_factor: int = 2) -> List[TrainingExample]:
        """Augment dataset with variations"""
        augmented = examples.copy()
        
        for _ in range(augmentation_factor - 1):
            for example in examples:
                # Create variations by modifying variable names, adding comments, etc.
                augmented_example = self._create_variation(example)
                if augmented_example:
                    augmented.append(augmented_example)
        
        logger.info(f"Augmented dataset from {len(examples)} to {len(augmented)} examples")
        return augmented
    
    def _create_variation(self, example: TrainingExample) -> Optional[TrainingExample]:
        """Create a variation of an existing example"""
        try:
            # Simple variation: add comments
            original_with_comment = f"# Optimization example\n{example.original_code}"
            optimized_with_comment = f"# Optimized version\n{example.optimized_code}"
            
            return TrainingExample(
                original_code=original_with_comment,
                optimized_code=optimized_with_comment,
                complexity_before=example.complexity_before,
                complexity_after=example.complexity_after,
                explanation=example.explanation,
                applied_rules=example.applied_rules,
                category=example.category
            )
        except:
            return None
    
    def get_dataset_statistics(self, examples: List[TrainingExample]) -> Dict[str, Any]:
        """Get statistics about the dataset"""
        categories = {}
        complexities = {}
        
        for example in examples:
            # Count categories
            categories[example.category] = categories.get(example.category, 0) + 1
            
            # Count complexities
            complexities[example.complexity_before] = complexities.get(example.complexity_before, 0) + 1
        
        return {
            'total_examples': len(examples),
            'categories': categories,
            'complexities': complexities,
            'avg_original_length': sum(len(ex.original_code) for ex in examples) / len(examples),
            'avg_optimized_length': sum(len(ex.optimized_code) for ex in examples) / len(examples)
        }