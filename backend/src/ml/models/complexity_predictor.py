"""
ML-based Complexity Prediction System using Random Forest and LightGBM
"""

import ast
import re
import logging
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

from ...data_models import ComplexityPrediction, BaseComplexityPredictor
from ...config import Config

logger = logging.getLogger('efficode.complexity_predictor')

class ComplexityFeatureExtractor:
    """Extracts features from code for complexity prediction"""
    
    def __init__(self):
        self.complexity_patterns = {
            'O(1)': ['return', 'print', '=', '+', '-', '*', '/', '%'],
            'O(log n)': ['binary', 'divide', 'half', '//2', '/2'],
            'O(n)': ['for', 'while', 'sum', 'max', 'min', 'len'],
            'O(n log n)': ['sort', 'merge', 'heap'],
            'O(n²)': ['nested', 'double', 'bubble'],
            'O(2^n)': ['recursive', 'fibonacci', 'exponential']
        }
    
    def extract_ast_features(self, code: str) -> Dict[str, int]:
        """Extract AST-based structural features"""
        try:
            tree = ast.parse(code)
            features = {
                'num_functions': 0,
                'num_classes': 0,
                'num_loops': 0,
                'num_if_statements': 0,
                'num_assignments': 0,
                'num_function_calls': 0,
                'max_nesting_depth': 0,
                'num_return_statements': 0,
                'num_variables': 0,
                'ast_node_count': 0
            }
            
            # Count different node types
            for node in ast.walk(tree):
                features['ast_node_count'] += 1
                
                if isinstance(node, ast.FunctionDef):
                    features['num_functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    features['num_classes'] += 1
                elif isinstance(node, (ast.For, ast.While)):
                    features['num_loops'] += 1
                elif isinstance(node, ast.If):
                    features['num_if_statements'] += 1
                elif isinstance(node, ast.Assign):
                    features['num_assignments'] += 1
                elif isinstance(node, ast.Call):
                    features['num_function_calls'] += 1
                elif isinstance(node, ast.Return):
                    features['num_return_statements'] += 1
                elif isinstance(node, ast.Name):
                    features['num_variables'] += 1
            
            # Calculate nesting depth
            features['max_nesting_depth'] = self._calculate_nesting_depth(tree)
            
            return features
            
        except SyntaxError:
            logger.warning("Syntax error in code, returning default features")
            return {key: 0 for key in ['num_functions', 'num_classes', 'num_loops', 
                                     'num_if_statements', 'num_assignments', 'num_function_calls',
                                     'max_nesting_depth', 'num_return_statements', 'num_variables',
                                     'ast_node_count']}
    
    def _calculate_nesting_depth(self, node, depth=0):
        """Calculate maximum nesting depth of control structures"""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If, ast.FunctionDef, ast.ClassDef)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def extract_loop_features(self, code: str) -> Dict[str, int]:
        """Extract loop-specific features"""
        features = {
            'nested_loops': 0,
            'simple_loops': 0,
            'while_loops': 0,
            'for_loops': 0,
            'loop_with_break': 0,
            'loop_with_continue': 0,
            'range_loops': 0,
            'enumerate_loops': 0
        }
        
        try:
            tree = ast.parse(code)
            
            # Find nested loops
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    features['for_loops'] += 1
                    
                    # Check for range usage
                    if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range':
                            features['range_loops'] += 1
                        elif node.iter.func.id == 'enumerate':
                            features['enumerate_loops'] += 1
                    
                    # Check for nested loops
                    for child in ast.walk(node):
                        if child != node and isinstance(child, (ast.For, ast.While)):
                            features['nested_loops'] += 1
                    
                    # Check for break/continue
                    for child in ast.walk(node):
                        if isinstance(child, ast.Break):
                            features['loop_with_break'] += 1
                        elif isinstance(child, ast.Continue):
                            features['loop_with_continue'] += 1
                
                elif isinstance(node, ast.While):
                    features['while_loops'] += 1
            
            # Simple loops (not nested)
            features['simple_loops'] = features['for_loops'] + features['while_loops'] - features['nested_loops']
            
        except SyntaxError:
            pass
        
        return features
    
    def extract_recursion_features(self, code: str) -> Dict[str, int]:
        """Extract recursion-related features"""
        features = {
            'recursive_calls': 0,
            'has_base_case': 0,
            'multiple_recursive_calls': 0,
            'tail_recursion': 0
        }
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    recursive_calls = 0
                    
                    # Count recursive calls
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            if child.func.id == func_name:
                                recursive_calls += 1
                    
                    if recursive_calls > 0:
                        features['recursive_calls'] += recursive_calls
                        
                        if recursive_calls > 1:
                            features['multiple_recursive_calls'] += 1
                        
                        # Check for base case (if statement with return)
                        for child in ast.walk(node):
                            if isinstance(child, ast.If):
                                for if_child in ast.walk(child):
                                    if isinstance(if_child, ast.Return):
                                        features['has_base_case'] = 1
                                        break
        
        except SyntaxError:
            pass
        
        return features
    
    def extract_data_structure_features(self, code: str) -> Dict[str, int]:
        """Extract data structure usage features"""
        features = {
            'list_operations': 0,
            'dict_operations': 0,
            'set_operations': 0,
            'string_operations': 0,
            'list_comprehensions': 0,
            'dict_comprehensions': 0,
            'generator_expressions': 0
        }
        
        # Count data structure operations
        features['list_operations'] = len(re.findall(r'\.(append|extend|insert|remove|pop|sort|reverse)', code))
        features['dict_operations'] = len(re.findall(r'\.(keys|values|items|get|pop|update)', code))
        features['set_operations'] = len(re.findall(r'\.(add|remove|discard|union|intersection)', code))
        features['string_operations'] = len(re.findall(r'\.(split|join|replace|strip|lower|upper)', code))
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ListComp):
                    features['list_comprehensions'] += 1
                elif isinstance(node, ast.DictComp):
                    features['dict_comprehensions'] += 1
                elif isinstance(node, ast.GeneratorExp):
                    features['generator_expressions'] += 1
        
        except SyntaxError:
            pass
        
        return features
    
    def extract_pattern_features(self, code: str) -> Dict[str, int]:
        """Extract algorithmic pattern features"""
        features = {}
        
        # Check for complexity patterns
        code_lower = code.lower()
        for complexity, patterns in self.complexity_patterns.items():
            pattern_count = sum(code_lower.count(pattern) for pattern in patterns)
            features[f'pattern_{complexity.replace("(", "").replace(")", "").replace(" ", "_")}'] = pattern_count
        
        # Specific algorithm patterns
        features['fibonacci_pattern'] = 1 if 'fibonacci' in code_lower and 'fibonacci(n-1)' in code else 0
        features['factorial_pattern'] = 1 if 'factorial' in code_lower and 'factorial(n-1)' in code else 0
        features['binary_search_pattern'] = 1 if 'binary' in code_lower and ('left' in code and 'right' in code) else 0
        features['sorting_pattern'] = 1 if any(word in code_lower for word in ['sort', 'bubble', 'merge', 'quick']) else 0
        
        return features
    
    def extract_all_features(self, code: str) -> Dict[str, Any]:
        """Extract all features from code"""
        features = {}
        
        # Basic code metrics
        features['code_length'] = len(code)
        features['num_lines'] = len(code.split('\n'))
        features['avg_line_length'] = features['code_length'] / features['num_lines'] if features['num_lines'] > 0 else 0
        
        # Combine all feature types
        features.update(self.extract_ast_features(code))
        features.update(self.extract_loop_features(code))
        features.update(self.extract_recursion_features(code))
        features.update(self.extract_data_structure_features(code))
        features.update(self.extract_pattern_features(code))
        
        return features

class ComplexityPredictor(BaseComplexityPredictor):
    """ML-based complexity predictor using Random Forest and LightGBM"""
    
    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.feature_extractor = ComplexityFeatureExtractor()
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_trained = False
    
    def extract_features(self, code: str) -> Dict[str, Any]:
        """Extract features from code for prediction"""
        return self.feature_extractor.extract_all_features(code)
    
    def predict_complexity(self, code: str) -> ComplexityPrediction:
        """Predict the complexity of the given code"""
        if not self.is_trained:
            logger.warning("Model not trained, using heuristic prediction")
            return self._heuristic_prediction(code)
        
        try:
            # Extract features
            features = self.extract_features(code)
            feature_vector = np.array([features.get(name, 0) for name in self.feature_names]).reshape(1, -1)
            
            # Predict
            if self.model_type == 'random_forest':
                prediction = self.model.predict(feature_vector)[0]
                probabilities = self.model.predict_proba(feature_vector)[0]
                confidence = max(probabilities)
            else:  # lightgbm
                prediction = self.model.predict(feature_vector)[0]
                confidence = 0.8  # LightGBM doesn't provide probabilities directly
            
            # Convert back to complexity string
            complexity = self.label_encoder.inverse_transform([int(prediction)])[0]
            
            # Estimate numeric runtime (simplified)
            numeric_estimate = self._estimate_runtime(complexity, features)
            
            # Feature importance (for explainability)
            feature_importance = {}
            if hasattr(self.model, 'feature_importances_'):
                for name, importance in zip(self.feature_names, self.model.feature_importances_):
                    if importance > 0.01:  # Only include significant features
                        feature_importance[name] = float(importance)
            
            return ComplexityPrediction(
                symbolic_complexity=complexity,
                numeric_estimate=numeric_estimate,
                confidence=float(confidence),
                feature_importance=feature_importance
            )
            
        except Exception as e:
            logger.error(f"Error predicting complexity: {e}")
            return self._heuristic_prediction(code)
    
    def _heuristic_prediction(self, code: str) -> ComplexityPrediction:
        """Fallback heuristic prediction when ML model is not available"""
        features = self.extract_features(code)
        
        # Simple heuristic rules
        if features['recursive_calls'] > 1 and 'fibonacci' in code.lower():
            complexity = 'O(2^n)'
        elif features['nested_loops'] > 0:
            complexity = 'O(n²)'
        elif features['num_loops'] > 0:
            complexity = 'O(n)'
        elif any(pattern in code.lower() for pattern in ['sort', 'merge']):
            complexity = 'O(n log n)'
        elif any(pattern in code.lower() for pattern in ['binary', 'search']):
            complexity = 'O(log n)'
        else:
            complexity = 'O(1)'
        
        return ComplexityPrediction(
            symbolic_complexity=complexity,
            numeric_estimate=self._estimate_runtime(complexity, features),
            confidence=0.6,  # Lower confidence for heuristic
            feature_importance={}
        )
    
    def _estimate_runtime(self, complexity: str, features: Dict[str, Any]) -> float:
        """Estimate numeric runtime based on complexity and code features"""
        base_time = 1e-6  # Base time in seconds
        code_size_factor = features.get('code_length', 100) / 100
        
        complexity_multipliers = {
            'O(1)': 1,
            'O(log n)': 10,
            'O(n)': 100,
            'O(n log n)': 1000,
            'O(n²)': 10000,
            'O(2^n)': 1000000
        }
        
        multiplier = complexity_multipliers.get(complexity, 100)
        return base_time * multiplier * code_size_factor
    
    def train_model(self, training_examples) -> Dict[str, Any]:
        """Train the complexity prediction model"""
        logger.info(f"Training {self.model_type} complexity predictor...")
        
        # Prepare training data
        X = []
        y = []
        
        for example in training_examples:
            features = self.extract_features(example.original_code)
            X.append(features)
            y.append(example.complexity_before)
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(X)
        self.feature_names = list(df.columns)
        X_array = df.values
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_array, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train model
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=Config.COMPLEXITY_CONFIG['n_estimators'],
                max_depth=Config.COMPLEXITY_CONFIG['max_depth'],
                random_state=Config.COMPLEXITY_CONFIG['random_state'],
                n_jobs=-1
            )
        else:  # lightgbm
            train_data = lgb.Dataset(X_train, label=y_train)
            params = {
                'objective': 'multiclass',
                'num_class': len(self.label_encoder.classes_),
                'metric': 'multi_logloss',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9
            }
            self.model = lgb.train(params, train_data, num_boost_round=100)
        
        # Fit the model
        if self.model_type == 'random_forest':
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_array, y_encoded, cv=5)
            
        else:  # lightgbm
            y_pred = self.model.predict(X_test)
            y_pred = np.argmax(y_pred, axis=1)
            accuracy = accuracy_score(y_test, y_pred)
            cv_scores = [accuracy]  # Simplified for LightGBM
        
        self.is_trained = True
        
        results = {
            'accuracy': accuracy,
            'cv_mean': np.mean(cv_scores),
            'cv_std': np.std(cv_scores),
            'num_features': len(self.feature_names),
            'num_samples': len(training_examples),
            'complexity_classes': list(self.label_encoder.classes_)
        }
        
        logger.info(f"Model training completed. Accuracy: {accuracy:.3f}")
        return results
    
    def save_model(self, path: str) -> bool:
        """Save the trained model"""
        try:
            model_data = {
                'model': self.model,
                'label_encoder': self.label_encoder,
                'feature_names': self.feature_names,
                'model_type': self.model_type,
                'is_trained': self.is_trained
            }
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        """Load a trained model"""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.feature_names = model_data['feature_names']
            self.model_type = model_data['model_type']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False