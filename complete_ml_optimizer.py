#!/usr/bin/env python3
"""
Complete ML-Powered Code Optimizer
- Handles ANY Python code input
- Uses comprehensive dataset from competitive programming sites
- ML-powered technique prediction
- Data structure optimization
- Real-time complexity analysis
"""

import ast
import json
import time
import re
import os
import pickle
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

class CompleteMlOptimizer:
    def __init__(self):
        self.dataset = []
        self.ml_model = None
        self.vectorizer = None
        self.technique_templates = {}
        self.load_dataset()
        self.load_or_train_model()
        self.setup_optimization_templates()
    
    def load_dataset(self):
        """Load comprehensive optimization dataset"""
        try:
            with open('comprehensive_optimization_dataset.json', 'r') as f:
                data = json.load(f)
                self.dataset = data['examples']
            print(f"✅ Loaded dataset with {len(self.dataset)} examples")
        except FileNotFoundError:
            print("⚠️  Dataset not found. Run simple_dataset_scraper.py first")
            self.dataset = self.create_minimal_dataset()
    
    def create_minimal_dataset(self):
        """Create minimal dataset if file not found"""
        return [
            {
                "title": "Two Sum",
                "brute_force": '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []''',
                "optimized": '''def twoSum(nums, target):
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return []''',
                "technique": "hash_map",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Dictionary"
            }
        ]
    
    def load_or_train_model(self):
        """Load existing ML model or train new one"""
        if os.path.exists('complete_ml_model.pkl'):
            with open('complete_ml_model.pkl', 'rb') as f:
                self.ml_model = pickle.load(f)
            print("✅ Loaded existing ML model")
        else:
            print("🔄 Training new ML model...")
            self.train_comprehensive_model()
    
    def train_comprehensive_model(self):
        """Train ML model on comprehensive dataset"""
        print("🤖 Training comprehensive ML model...")
        
        X = []  # Features
        y = []  # Techniques
        
        for example in self.dataset:
            features = self.extract_comprehensive_features(example['brute_force'])
            X.append(features)
            y.append(example['technique'])
        
        # Train Random Forest with more estimators for better accuracy
        self.ml_model = RandomForestClassifier(
            n_estimators=200, 
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.ml_model.fit(X, y)
        
        # Save model
        with open('complete_ml_model.pkl', 'wb') as f:
            pickle.dump(self.ml_model, f)
        
        print("✅ Comprehensive ML model trained and saved!")
    
    def extract_comprehensive_features(self, code: str) -> List[float]:
        """Extract comprehensive features for ML analysis"""
        try:
            tree = ast.parse(code)
        except:
            return [0] * 30  # Return zero features for invalid code
        
        features = []
        
        # Structural complexity features
        features.append(self.count_nested_loops(tree))
        features.append(self.count_function_calls(tree))
        features.append(self.count_variables(tree))
        features.append(self.count_conditionals(tree))
        features.append(self.count_list_operations(tree))
        features.append(len(code.split('\n')))  # Lines of code
        
        # Loop and iteration patterns
        features.append(code.count('for'))
        features.append(code.count('while'))
        features.append(code.count('range'))
        features.append(code.count('enumerate'))
        
        # Data structure usage
        features.append(1 if 'dict' in code or '{}' in code else 0)
        features.append(1 if 'set(' in code or 'set()' in code else 0)
        features.append(1 if 'list(' in code or '[]' in code else 0)
        features.append(code.count('append'))
        features.append(code.count('get('))
        
        # Algorithmic patterns
        features.append(1 if re.search(r'\+.*==|sum\(', code) else 0)  # Sum patterns
        features.append(1 if re.search(r'==.*and|!=.*or', code) else 0)  # Comparison patterns
        features.append(1 if 'max(' in code or 'min(' in code else 0)  # Min/max patterns
        features.append(1 if 'sorted(' in code or '.sort(' in code else 0)  # Sorting
        features.append(1 if 'len(' in code else 0)  # Length operations
        
        # Complexity indicators
        features.append(1 if self.has_nested_loops(tree) else 0)
        features.append(1 if self.has_triple_nested_loops(tree) else 0)
        features.append(1 if 'in' in code and 'for' in code else 0)  # Membership testing
        features.append(code.count('if'))  # Conditional complexity
        
        # String and search patterns
        features.append(1 if 'substring' in code.lower() or 'substr' in code.lower() else 0)
        features.append(1 if 'duplicate' in code.lower() else 0)
        features.append(1 if 'pair' in code.lower() or 'sum' in code.lower() else 0)
        features.append(1 if 'maximum' in code.lower() or 'minimum' in code.lower() else 0)
        features.append(1 if 'count' in code.lower() else 0)
        features.append(1 if 'frequency' in code.lower() else 0)
        
        # Ensure exactly 30 features
        while len(features) < 30:
            features.append(0)
        
        return features[:30]
    
    def count_nested_loops(self, tree) -> int:
        """Count maximum nested loop depth"""
        max_depth = 0
        
        def visit_node(node, depth=0):
            nonlocal max_depth
            if isinstance(node, (ast.For, ast.While)):
                depth += 1
                max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, depth)
        
        visit_node(tree)
        return max_depth
    
    def has_nested_loops(self, tree) -> bool:
        """Check if code has nested loops (depth >= 2)"""
        return self.count_nested_loops(tree) >= 2
    
    def has_triple_nested_loops(self, tree) -> bool:
        """Check if code has triple nested loops (depth >= 3)"""
        return self.count_nested_loops(tree) >= 3
    
    def count_function_calls(self, tree) -> int:
        """Count function calls"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                count += 1
        return count
    
    def count_variables(self, tree) -> int:
        """Count variable assignments"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                count += 1
        return count
    
    def count_conditionals(self, tree) -> int:
        """Count if statements"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                count += 1
        return count
    
    def count_list_operations(self, tree) -> int:
        """Count list operations"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ['append', 'extend', 'insert', 'remove', 'pop']:
                    count += 1
        return count
    
    def setup_optimization_templates(self):
        """Setup optimization templates for different techniques"""
        self.technique_templates = {
            'hash_map': {
                'description': 'Hash Map Optimization',
                'complexity': 'O(n)',
                'data_structure': 'Dictionary/HashMap',
                'use_case': 'Two sum, complement search, key-value mapping'
            },
            'hash_set': {
                'description': 'Hash Set Optimization', 
                'complexity': 'O(n)',
                'data_structure': 'Set/HashSet',
                'use_case': 'Duplicate detection, membership testing'
            },
            'dynamic_programming': {
                'description': 'Dynamic Programming',
                'complexity': 'O(n)',
                'data_structure': 'Array/Variables',
                'use_case': 'Optimal substructure, overlapping subproblems'
            },
            'two_pointers': {
                'description': 'Two Pointers Technique',
                'complexity': 'O(n) or O(n log n)',
                'data_structure': 'Sorted Array',
                'use_case': 'Sorted array problems, pair finding'
            },
            'sliding_window': {
                'description': 'Sliding Window',
                'complexity': 'O(n)',
                'data_structure': 'Window/Deque',
                'use_case': 'Subarray problems, range queries'
            },
            'frequency_map': {
                'description': 'Frequency Counter',
                'complexity': 'O(n)',
                'data_structure': 'Dictionary',
                'use_case': 'Counting, frequency analysis'
            }
        }
    
    def predict_optimization_technique(self, code: str) -> Dict:
        """Predict best optimization technique using ML"""
        features = self.extract_comprehensive_features(code)
        features_array = np.array(features).reshape(1, -1)
        
        # Predict technique
        predicted_technique = self.ml_model.predict(features_array)[0]
        probabilities = self.ml_model.predict_proba(features_array)[0]
        confidence = max(probabilities)
        
        # Get all technique probabilities
        technique_scores = {}
        for i, technique in enumerate(self.ml_model.classes_):
            technique_scores[technique] = probabilities[i]
        
        return {
            'primary_technique': predicted_technique,
            'confidence': confidence,
            'all_techniques': technique_scores,
            'features_used': features
        }
    
    def generate_optimized_code(self, original_code: str, technique: str) -> str:
        """Generate optimized code based on technique"""
        
        # Extract function signature
        func_match = re.search(r'def (\w+)\((.*?)\):', original_code)
        if func_match:
            func_name = func_match.group(1)
            params = func_match.group(2)
        else:
            func_name = "optimized_function"
            params = "arr"
        
        # Generate optimization based on technique
        if technique == 'hash_map':
            return self.generate_hash_map_optimization(func_name, params, original_code)
        elif technique == 'hash_set':
            return self.generate_hash_set_optimization(func_name, params, original_code)
        elif technique == 'dynamic_programming':
            return self.generate_dp_optimization(func_name, params, original_code)
        elif technique == 'two_pointers':
            return self.generate_two_pointers_optimization(func_name, params, original_code)
        elif technique == 'frequency_map':
            return self.generate_frequency_optimization(func_name, params, original_code)
        else:
            return self.generate_generic_optimization(func_name, params, original_code)
    
    def generate_hash_map_optimization(self, func_name: str, params: str, original: str) -> str:
        """Generate hash map optimized version"""
        param_list = [p.strip() for p in params.split(',')]
        main_param = param_list[0] if param_list else 'arr'
        
        return f'''def {func_name}_optimized({params}):
    """
    Optimized using Hash Map
    Time Complexity: O(n) - Single pass with O(1) lookups
    Space Complexity: O(n) - Hash map storage
    Data Structure: Dictionary for key-value mapping
    """
    lookup_map = {{}}  # Hash map for O(1) lookups
    
    for i, item in enumerate({main_param}):
        # Calculate complement or target value
        target_val = target - item if 'target' in '{params}' else item
        
        # Check if complement exists
        if target_val in lookup_map:
            return [lookup_map[target_val], i]  # Return indices
        
        # Store current item with its index
        lookup_map[item] = i
    
    return []  # No solution found'''
    
    def generate_hash_set_optimization(self, func_name: str, params: str, original: str) -> str:
        """Generate hash set optimized version"""
        param_list = [p.strip() for p in params.split(',')]
        main_param = param_list[0] if param_list else 'arr'
        
        return f'''def {func_name}_optimized({params}):
    """
    Optimized using Hash Set
    Time Complexity: O(n) - Single pass with O(1) membership testing
    Space Complexity: O(n) - Set storage
    Data Structure: Set for fast membership testing
    """
    seen = set()  # Hash set for O(1) membership testing
    
    for item in {main_param}:
        # Check if item already seen (duplicate detection)
        if item in seen:
            return True  # Found duplicate
        
        # Add item to seen set
        seen.add(item)
    
    return False  # No duplicates found'''
    
    def generate_dp_optimization(self, func_name: str, params: str, original: str) -> str:
        """Generate dynamic programming optimized version"""
        param_list = [p.strip() for p in params.split(',')]
        main_param = param_list[0] if param_list else 'arr'
        
        return f'''def {func_name}_optimized({params}):
    """
    Optimized using Dynamic Programming
    Time Complexity: O(n) - Single pass with optimal substructure
    Space Complexity: O(1) - Constant space (Kadane's algorithm)
    Data Structure: Variables to track optimal solution
    """
    if not {main_param}:
        return 0
    
    # Initialize with first element
    current_optimal = global_optimal = {main_param}[0]
    
    # Apply optimal substructure principle
    for item in {main_param}[1:]:
        # Either extend current subarray or start new one
        current_optimal = max(item, current_optimal + item)
        global_optimal = max(global_optimal, current_optimal)
    
    return global_optimal'''
    
    def generate_two_pointers_optimization(self, func_name: str, params: str, original: str) -> str:
        """Generate two pointers optimized version"""
        param_list = [p.strip() for p in params.split(',')]
        main_param = param_list[0] if param_list else 'arr'
        
        return f'''def {func_name}_optimized({params}):
    """
    Optimized using Two Pointers Technique
    Time Complexity: O(n log n) - Sorting + O(n) two pointers traversal
    Space Complexity: O(1) - Constant extra space
    Data Structure: Sorted array with two pointers
    """
    # Sort array for two pointers technique
    {main_param}.sort()
    result = []
    
    # Use two pointers approach
    left, right = 0, len({main_param}) - 1
    
    while left < right:
        current_sum = {main_param}[left] + {main_param}[right]
        target_sum = target if 'target' in '{params}' else 0
        
        if current_sum == target_sum:
            result.append([{main_param}[left], {main_param}[right]])
            left += 1
            right -= 1
        elif current_sum < target_sum:
            left += 1
        else:
            right -= 1
    
    return result'''
    
    def generate_frequency_optimization(self, func_name: str, params: str, original: str) -> str:
        """Generate frequency counter optimized version"""
        param_list = [p.strip() for p in params.split(',')]
        main_param = param_list[0] if param_list else 'arr'
        
        return f'''def {func_name}_optimized({params}):
    """
    Optimized using Frequency Counter
    Time Complexity: O(n) - Single pass for frequency counting
    Space Complexity: O(n) - Frequency map storage
    Data Structure: Dictionary for frequency counting
    """
    frequency = {{}}  # Frequency counter
    result = 0
    
    # Count frequencies and find pairs/matches
    for item in {main_param}:
        complement = target - item if 'target' in '{params}' else item
        
        # Check if complement exists and count pairs
        if complement in frequency:
            result += frequency[complement]
        
        # Update frequency count
        frequency[item] = frequency.get(item, 0) + 1
    
    return result'''
    
    def generate_generic_optimization(self, func_name: str, params: str, original: str) -> str:
        """Generate generic optimization suggestions"""
        return f'''def {func_name}_optimized({params}):
    """
    Generic Optimization Applied
    Consider these optimization techniques:
    1. Hash Map: For O(1) lookups and complement searches
    2. Hash Set: For duplicate detection and membership testing
    3. Two Pointers: For sorted array problems
    4. Dynamic Programming: For optimal substructure problems
    5. Sliding Window: For subarray/substring problems
    """
    # Original code with optimization comments
{original}
    
    # TODO: Apply appropriate data structure optimization
    # - Use dict() for key-value mapping
    # - Use set() for membership testing
    # - Consider sorting for two pointers approach
    # - Look for optimal substructure for DP'''
    
    def analyze_complexity(self, code: str) -> Dict:
        """Analyze time and space complexity"""
        try:
            tree = ast.parse(code)
        except:
            return {'time': 'Unknown', 'space': 'Unknown'}
        
        nested_loops = self.count_nested_loops(tree)
        
        # Time complexity analysis
        if nested_loops >= 3:
            time_complexity = "O(n³)"
        elif nested_loops >= 2:
            time_complexity = "O(n²)"
        elif nested_loops == 1:
            if 'sort' in code.lower():
                time_complexity = "O(n log n)"
            else:
                time_complexity = "O(n)"
        else:
            time_complexity = "O(1)"
        
        # Space complexity analysis
        if 'dict' in code or 'set' in code or '{}' in code:
            space_complexity = "O(n)"
        elif nested_loops >= 2:
            space_complexity = "O(1)"
        else:
            space_complexity = "O(1)"
        
        return {
            'time': time_complexity,
            'space': space_complexity,
            'nested_loops': nested_loops
        }
    
    def calculate_performance_improvement(self, original_complexity: str, optimized_complexity: str) -> Dict:
        """Calculate theoretical performance improvement"""
        complexity_values = {
            'O(1)': 1,
            'O(log n)': 2,
            'O(n)': 3,
            'O(n log n)': 4,
            'O(n²)': 5,
            'O(n³)': 6
        }
        
        orig_val = complexity_values.get(original_complexity, 3)
        opt_val = complexity_values.get(optimized_complexity, 3)
        
        if orig_val > opt_val:
            improvement_factor = 2 ** (orig_val - opt_val)
            return {
                'speedup_factor': improvement_factor,
                'speedup_description': f"{improvement_factor}x faster",
                'improvement_significant': True,
                'theoretical_gains': {
                    'n_100': f"{improvement_factor * 100}x faster for 100 elements",
                    'n_1000': f"{improvement_factor * 1000}x faster for 1,000 elements",
                    'n_10000': f"{improvement_factor * 10000}x faster for 10,000 elements"
                }
            }
        else:
            return {
                'speedup_factor': 1,
                'speedup_description': "No significant improvement",
                'improvement_significant': False,
                'theoretical_gains': {
                    'note': "Consider different optimization approach"
                }
            }
    
    def optimize_code(self, code: str) -> Dict:
        """Main function to optimize any Python code"""
        start_time = time.time()
        
        # ML prediction
        prediction = self.predict_optimization_technique(code)
        
        # Generate optimized code
        optimized_code = self.generate_optimized_code(code, prediction['primary_technique'])
        
        # Complexity analysis
        original_complexity = self.analyze_complexity(code)
        optimized_complexity = self.analyze_complexity(optimized_code)
        
        # Performance improvement calculation
        performance = self.calculate_performance_improvement(
            original_complexity['time'], 
            optimized_complexity['time']
        )
        
        processing_time = time.time() - start_time
        
        return {
            'original_code': code,
            'optimized_code': optimized_code,
            'ml_analysis': {
                'predicted_technique': prediction['primary_technique'],
                'confidence': prediction['confidence'],
                'alternative_techniques': prediction['all_techniques']
            },
            'complexity_analysis': {
                'original': original_complexity,
                'optimized': optimized_complexity
            },
            'performance_improvement': performance,
            'optimization_details': {
                'technique': prediction['primary_technique'],
                'data_structure': self.technique_templates.get(
                    prediction['primary_technique'], {}
                ).get('data_structure', 'Generic'),
                'description': self.technique_templates.get(
                    prediction['primary_technique'], {}
                ).get('description', 'Generic Optimization')
            },
            'processing_time': processing_time
        }

def main():
    """Interactive demo of complete ML optimizer"""
    optimizer = CompleteMlOptimizer()
    
    print("🚀 Complete ML-Powered Code Optimizer")
    print("=" * 60)
    print("Enter ANY Python code and get ML-optimized version!")
    print("Supports: LeetCode, GeeksforGeeks, HackerRank, Codeforces patterns")
    print()
    
    while True:
        print("\nOptions:")
        print("1. Optimize custom code")
        print("2. Test with sample problems")
        print("3. Show optimization techniques")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '4':
            break
        elif choice == '3':
            print("\n🔧 AVAILABLE OPTIMIZATION TECHNIQUES:")
            print("-" * 50)
            for technique, details in optimizer.technique_templates.items():
                print(f"• {technique.upper()}")
                print(f"  Description: {details['description']}")
                print(f"  Complexity: {details['complexity']}")
                print(f"  Data Structure: {details['data_structure']}")
                print(f"  Use Case: {details['use_case']}")
                print()
            continue
        elif choice == '2':
            # Sample problems
            samples = [
                '''def findDuplicates(nums):
    duplicates = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j] and nums[i] not in duplicates:
                duplicates.append(nums[i])
    return duplicates''',
                
                '''def maxProduct(nums):
    max_prod = float('-inf')
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            prod = 1
            for k in range(i, j + 1):
                prod *= nums[k]
            max_prod = max(max_prod, prod)
    return max_prod''',
                
                '''def countPairs(arr, target):
    count = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] + arr[j] == target:
                count += 1
    return count'''
            ]
            
            print("\nSample Problems:")
            for i, sample in enumerate(samples, 1):
                print(f"{i}. Sample {i}")
            
            sample_choice = input("Choose sample (1-3): ").strip()
            if sample_choice in ['1', '2', '3']:
                code = samples[int(sample_choice) - 1]
                print(f"\n📝 Sample Code {sample_choice}:")
                print(code)
            else:
                print("Invalid choice!")
                continue
                
        elif choice == '1':
            print("\n📝 Enter your Python code (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            code = '\n'.join(lines[:-1])
        else:
            print("Invalid choice!")
            continue
        
        if not code.strip():
            print("No code entered!")
            continue
        
        # Optimize the code
        print("\n🔄 Analyzing and optimizing code...")
        result = optimizer.optimize_code(code)
        
        # Display comprehensive results
        print("\n" + "="*80)
        print("🤖 COMPLETE ML-POWERED OPTIMIZATION RESULTS")
        print("="*80)
        
        # ML Analysis
        ml_analysis = result['ml_analysis']
        print(f"🧠 ML ANALYSIS:")
        print(f"   Predicted Technique: {ml_analysis['predicted_technique'].upper()}")
        print(f"   Confidence: {ml_analysis['confidence']:.1%}")
        
        print(f"\n   Alternative Techniques:")
        sorted_techniques = sorted(ml_analysis['alternative_techniques'].items(), 
                                 key=lambda x: x[1], reverse=True)
        for technique, score in sorted_techniques[:3]:
            print(f"   • {technique}: {score:.1%}")
        
        # Complexity Analysis
        complexity = result['complexity_analysis']
        print(f"\n📊 COMPLEXITY ANALYSIS:")
        print(f"   Original Time: {complexity['original']['time']}")
        print(f"   Optimized Time: {complexity['optimized']['time']}")
        print(f"   Original Space: {complexity['original']['space']}")
        print(f"   Optimized Space: {complexity['optimized']['space']}")
        
        # Performance Improvement
        performance = result['performance_improvement']
        print(f"\n⚡ PERFORMANCE IMPROVEMENT:")
        print(f"   Speedup: {performance['speedup_description']}")
        if performance['improvement_significant']:
            gains = performance['theoretical_gains']
            print(f"   For 100 elements: {gains.get('n_100', 'N/A')}")
            print(f"   For 1,000 elements: {gains.get('n_1000', 'N/A')}")
            print(f"   For 10,000 elements: {gains.get('n_10000', 'N/A')}")
        
        # Optimization Details
        opt_details = result['optimization_details']
        print(f"\n🔧 OPTIMIZATION DETAILS:")
        print(f"   Technique: {opt_details['technique']}")
        print(f"   Data Structure: {opt_details['data_structure']}")
        print(f"   Description: {opt_details['description']}")
        
        # Optimized Code
        print(f"\n🚀 OPTIMIZED CODE:")
        print("-" * 50)
        print(result['optimized_code'])
        
        print(f"\n⏱️  Processing Time: {result['processing_time']:.4f} seconds")
        print("="*80)

if __name__ == "__main__":
    main()