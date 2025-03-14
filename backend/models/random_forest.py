"""
Improved RandomForest Model for Complexity Prediction

This module implements an enhanced RandomForest model for predicting the time and space
complexity of algorithms based on code features, with improved pattern recognition
and feature extraction to better handle various complexity classes.
"""

import os
import joblib
import numpy as np
import pandas as pd
import logging
import re
from typing import Dict, List, Tuple, Union, Optional, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GridSearchCV, train_test_split

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComplexityPredictor:
    """
    Enhanced RandomForest-based model for predicting algorithm complexity
    """
    
    def __init__(self, model_dir: str = None):
        """
        Initialize the complexity predictor
        
        Args:
            model_dir: Directory to save/load models
        """
        if model_dir is None:
            # Default to models/random_forest directory relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.model_dir = os.path.join(project_root, 'models', 'random_forest')
        else:
            self.model_dir = model_dir
            
        self.time_model = None
        self.space_model = None
        self.feature_names = None
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize complexity mappings
        self._initialize_complexity_mappings()
        
        logger.info("ComplexityPredictor initialized")
    
    def _initialize_complexity_mappings(self):
        """Initialize standard complexity mappings"""
        self.complexity_mapping = {
            'O(1)': 1,                # Constant
            'O(log n)': 2,            # Logarithmic
            'O(log(n))': 2,           # Alternative logarithmic
            'O(n)': 3,                # Linear
            'O(n log n)': 4,          # Linearithmic
            'O(n*log n)': 4,          # Alternative linearithmic
            'O(n*log(n))': 4,         # Alternative linearithmic
            'O(n²)': 5,               # Quadratic
            'O(n^2)': 5,              # Alternative quadratic
            'O(n*n)': 5,              # Alternative quadratic
            'O(n³)': 6,               # Cubic
            'O(n^3)': 6,              # Alternative cubic
            'O(2^n)': 7,              # Exponential
            'O(n!)': 8                # Factorial
        }
        
        # Create reverse mapping
        self.reverse_mapping = {v: k for k, v in self.complexity_mapping.items()}
    
    def extract_enhanced_features(self, code: str) -> Dict[str, Any]:
        """
        Extract enhanced algorithm features from code with improved pattern recognition
        
        Args:
            code: Python code as string
            
        Returns:
            Dictionary of extracted features
        """
        if not isinstance(code, str) or not code.strip():
            return {}
            
        features = {}
        
        # Detect basic metrics
        loop_count = len(re.findall(r'\b(for|while)\b', code))
        list_comprehensions = len(re.findall(r'\[.*?\bfor\b.*?\]', code))
        total_loops = loop_count + list_comprehensions
        
        # Check for nested loops
        nested_loop_pattern = r'(?:for|while).*?[{:].*?(?:for|while).*?[{:]'
        has_nested_loops = 1 if re.search(nested_loop_pattern, code, re.DOTALL) else 0
        
        # Count conditionals
        if_count = len(re.findall(r'\bif\b', code))
        elif_count = len(re.findall(r'\belif\b', code))
        else_count = len(re.findall(r'\belse\b', code))
        total_conditionals = if_count + elif_count + else_count
        
        # Detect recursion
        function_names = re.findall(r'def\s+(\w+)\s*\(', code)
        is_recursive = 0
        for func_name in function_names:
            pattern = r'\b' + re.escape(func_name) + r'\s*\('
            search_area = re.sub(r'def\s+' + re.escape(func_name) + r'\s*\(', '', code)
            if re.search(pattern, search_area):
                is_recursive = 1
                break
                
        # Count array operations
        array_accesses = len(re.findall(r'\w+\s*\[\s*\w+\s*\]', code))
        array_slices = len(re.findall(r'\w+\s*\[\s*.*?:.*?\s*\]', code))
        
        # Detect specific algorithm patterns
        
        # 1. Constant time operations (O(1))
        constant_time_patterns = [
            # Simple return or single operation
            r'^\s*def\s+\w+\s*\([^)]*\):\s*\n\s+(?:return|if).*?(?:\[|\{).*$',
            # Array access without loops
            r'^\s*def\s+\w+\s*\([^)]*\):\s*\n\s+.*?\[.*?\].*$'
        ]
        has_constant_time = 0
        if total_loops == 0 and array_accesses > 0:
            has_constant_time = 1
        else:
            for pattern in constant_time_patterns:
                if re.search(pattern, code, re.MULTILINE):
                    has_constant_time = 1
                    break
                    
        # 2. Linear time operations (O(n))
        linear_time_pattern = (total_loops == 1 and 
                             has_nested_loops == 0 and 
                             list_comprehensions <= 1 and
                             not is_recursive)
        has_linear_time = 1 if linear_time_pattern else 0
        
        # 3. Binary search pattern (O(log n))
        binary_search_patterns = [
            # Mid calculation
            r'mid\s*=\s*\(?(?:left|start|low|begin|l)\s*\+\s*(?:right|end|high|r)\)?(?:\s*\/\/\s*2|\s*>>>\s*1|\s*>\s*>\s*1)',
            # Bounds update
            r'(?:left|start|low|begin|l)\s*=\s*mid\s*\+\s*1|(?:right|end|high|r)\s*=\s*mid\s*\-\s*1'
        ]
        has_binary_search = 0
        if all(re.search(pattern, code) for pattern in binary_search_patterns):
            has_binary_search = 1
            
        # 4. Divide and conquer pattern (O(n log n))
        divide_conquer_patterns = [
            # Midpoint division
            r'(?:mid|middle)\s*=\s*(?:len\(.*?\)|.*?\.length|size|n)\s*//\s*2',
            # Recursive calls on divided portions
            r'(?:return|=)\s*\w+\s*\(.*?(?:\[:|\.slice|\(|,).*?\)'
        ]
        merge_pattern = r'merge\s*\(\s*\w+\s*\(.*?\)\s*,\s*\w+\s*\(.*?\)\s*\)'
        quick_pattern = r'(?:pivot|partition)'
        
        has_divide_conquer = 0
        if ((all(re.search(pattern, code) for pattern in divide_conquer_patterns)) or
            re.search(merge_pattern, code) or
            re.search(quick_pattern, code)):
            has_divide_conquer = 1
            
        # 5. Quadratic time operations (O(n²))
        has_quadratic = 0
        if has_nested_loops == 1 and len(function_names) <= 2 and not has_divide_conquer:
            has_quadratic = 1
            
        # 6. Cubic time operations (O(n³))
        has_cubic = 0
        nested_loops_count = 0
        lines = code.split('\n')
        indent_levels = []
        
        for line in lines:
            if re.search(r'^\s*(for|while)\b', line):
                indent = len(line) - len(line.lstrip())
                indent_levels.append(indent)
                
        if len(indent_levels) >= 3 and len(set(indent_levels)) >= 3:
            has_cubic = 1
            
        # 7. Exponential time operations (O(2^n))
        has_exponential = 0
        if is_recursive and 'fibonacci' in code.lower() and not 'memo' in code.lower():
            has_exponential = 1
        elif is_recursive and len(re.findall(r'\b' + '|'.join(function_names) + r'\b', code)) >= 3:
            has_exponential = 1
            
        # Basic code metrics
        lines = len(code.strip().split('\n'))
        chars = len(code)
        
        # Add all features to dictionary
        features.update({
            'code_lines': lines,
            'code_chars': chars,
            'loop_count': total_loops,
            'list_comprehensions': list_comprehensions,
            'conditionals': total_conditionals,
            'has_nested_loops': has_nested_loops,
            'is_recursive': is_recursive,
            'array_accesses': array_accesses,
            'array_slices': array_slices,
            'has_constant_time': has_constant_time,
            'has_linear_time': has_linear_time,
            'has_binary_search': has_binary_search,
            'has_divide_conquer': has_divide_conquer,
            'has_quadratic': has_quadratic,
            'has_cubic': has_cubic,
            'has_exponential': has_exponential,
            'loop_depth': max(1, has_nested_loops + 1) if total_loops > 0 else 0
        })
        
        return features
    
    def train_complexity_predictor(self, 
                                 X_train: pd.DataFrame, 
                                 y_time_train: pd.Series,
                                 y_space_train: pd.Series,
                                 optimize: bool = False) -> Tuple[RandomForestClassifier, RandomForestClassifier]:
        """
        Train RandomForest models for time and space complexity prediction
        
        Args:
            X_train: Feature matrix of training data
            y_time_train: Time complexity labels for training
            y_space_train: Space complexity labels for training
            optimize: Whether to perform hyperparameter optimization
            
        Returns:
            Tuple of trained (time_model, space_model)
        """
        logger.info("Training RandomForest complexity predictors...")
        
        # Store feature names for importance analysis
        self.feature_names = X_train.columns.tolist()
        
        # Default parameters
        params = {
            'n_estimators': 100, 
            'max_depth': None,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'class_weight': 'balanced',  # Handle imbalanced classes
            'random_state': 42
        }
        
        # Hyperparameter optimization if requested
        if optimize:
            try:
                logger.info("Performing hyperparameter optimization...")
                
                # Safe subset for parameter tuning
                subset_size = min(1000, len(X_train))
                subset_idx = np.random.choice(len(X_train), subset_size, replace=False)
                X_subset = X_train.iloc[subset_idx]
                y_time_subset = y_time_train.iloc[subset_idx]
                y_space_subset = y_space_train.iloc[subset_idx]
                
                # Define parameter grid
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20],
                    'min_samples_split': [2, 5, 10]
                }
                
                # Time complexity optimization
                time_grid = GridSearchCV(
                    RandomForestClassifier(random_state=42, class_weight='balanced'),
                    param_grid=param_grid,
                    cv=3,
                    n_jobs=-1,
                    scoring='accuracy',
                    error_score=0
                )
                
                time_grid.fit(X_subset, y_time_subset)
                best_params_time = time_grid.best_params_
                
                # Space complexity optimization
                space_grid = GridSearchCV(
                    RandomForestClassifier(random_state=42, class_weight='balanced'),
                    param_grid=param_grid,
                    cv=3,
                    n_jobs=-1,
                    scoring='accuracy',
                    error_score=0
                )
                
                space_grid.fit(X_subset, y_space_subset)
                best_params_space = space_grid.best_params_
                
                logger.info(f"Best parameters for time complexity: {best_params_time}")
                logger.info(f"Best parameters for space complexity: {best_params_space}")
                
                # Create models with optimized parameters
                time_model = RandomForestClassifier(**best_params_time, class_weight='balanced')
                space_model = RandomForestClassifier(**best_params_space, class_weight='balanced')
                
            except Exception as e:
                logger.warning(f"Hyperparameter optimization failed: {str(e)}")
                logger.info("Using default parameters instead")
                time_model = RandomForestClassifier(**params)
                space_model = RandomForestClassifier(**params)
        else:
            # Create models with default parameters
            time_model = RandomForestClassifier(**params)
            space_model = RandomForestClassifier(**params)
        
        try:
            # Train time complexity model
            logger.info("Training time complexity model...")
            time_model.fit(X_train, y_time_train)
            
            # Train space complexity model
            logger.info("Training space complexity model...")
            space_model.fit(X_train, y_space_train)
            
            # Store models
            self.time_model = time_model
            self.space_model = space_model
            
            logger.info("Training complete")
            return time_model, space_model
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            raise
    
    def predict_complexity(self, features: pd.DataFrame) -> Tuple[List[int], List[int]]:
        """
        Predict time and space complexity from code features
        
        Args:
            features: DataFrame of code features
            
        Returns:
            Tuple of (time_complexity_predictions, space_complexity_predictions)
        """
        if self.time_model is None or self.space_model is None:
            raise ValueError("Models not trained or loaded. Call train_complexity_predictor or load_predictor first.")
        
        # Ensure features match expected format
        if isinstance(features, pd.DataFrame):
            # Ensure all expected features are present
            missing_features = [f for f in self.feature_names if f not in features.columns]
            
            if missing_features:
                logger.warning(f"Missing features: {missing_features}")
                # Add missing features with zeros
                for feature in missing_features:
                    features[feature] = 0
            
            # Reorder columns to match training data
            features = features[self.feature_names]
        else:
            raise TypeError("Features must be a pandas DataFrame")
        
        # Apply pattern-based rules for special cases first
        time_predictions = []
        space_predictions = []
        
        for _, row in features.iterrows():
            # Rule-based prediction overrides for time complexity
            if row.get('has_constant_time', 0) == 1 and row.get('loop_count', 0) == 0:
                time_pred = 1  # O(1)
            elif row.get('has_binary_search', 0) == 1 and row.get('has_nested_loops', 0) == 0:
                time_pred = 2  # O(log n)
            elif row.get('has_linear_time', 0) == 1 and row.get('has_nested_loops', 0) == 0:
                time_pred = 3  # O(n)
            elif row.get('has_divide_conquer', 0) == 1:
                time_pred = 4  # O(n log n)
            elif row.get('has_cubic', 0) == 1:
                time_pred = 6  # O(n³)
            elif row.get('has_exponential', 0) == 1:
                time_pred = 7  # O(2^n)
            else:
                # Use ML model for other cases
                time_pred = self.time_model.predict(row.values.reshape(1, -1))[0]
            
            # Rule-based prediction overrides for space complexity
            if row.get('array_slices', 0) > 0 and row.get('is_recursive', 0) == 1:
                space_pred = 3  # O(n)
            elif row.get('is_recursive', 0) == 1 and row.get('has_binary_search', 0) == 1:
                space_pred = 2  # O(log n)
            elif row.get('array_slices', 0) == 0 and row.get('has_constant_time', 0) == 1:
                space_pred = 1  # O(1)
            else:
                # Use ML model for other cases
                space_pred = self.space_model.predict(row.values.reshape(1, -1))[0]
            
            time_predictions.append(time_pred)
            space_predictions.append(space_pred)
        
        return time_predictions, space_predictions
    
    def predict_complexity_string(self, features: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Predict time and space complexity and return as Big-O notation strings
        
        Args:
            features: DataFrame of code features
            
        Returns:
            Tuple of (time_complexity_strings, space_complexity_strings)
        """
        time_predictions, space_predictions = self.predict_complexity(features)
        
        # Convert numeric predictions to strings
        time_strings = [self.reverse_mapping.get(pred, f"O(n^{pred})") for pred in time_predictions]
        space_strings = [self.reverse_mapping.get(pred, f"O(n^{pred})") for pred in space_predictions]
        
        return time_strings, space_strings
    
    def evaluate_predictor(self, X_test: pd.DataFrame, y_time_test: pd.Series, y_space_test: pd.Series) -> Dict[str, Dict[str, float]]:
        """
        Evaluate the performance of the complexity predictors
        
        Args:
            X_test: Feature matrix of test data
            y_time_test: Time complexity labels for testing
            y_space_test: Space complexity labels for testing
            
        Returns:
            Dictionary with evaluation metrics
        """
        if self.time_model is None or self.space_model is None:
            raise ValueError("Models not trained or loaded. Call train_complexity_predictor or load_predictor first.")
        
        logger.info("Evaluating complexity predictors...")
        
        # Predict time complexity
        y_time_pred = self.predict_complexity(X_test)[0]
        time_accuracy = accuracy_score(y_time_test, y_time_pred)
        
        # Predict space complexity
        y_space_pred = self.predict_complexity(X_test)[1]
        space_accuracy = accuracy_score(y_space_test, y_space_pred)
        
        # Generate classification reports
        time_report = classification_report(y_time_test, y_time_pred, output_dict=True)
        space_report = classification_report(y_space_test, y_space_pred, output_dict=True)
        
        # Log results
        logger.info(f"Time complexity prediction accuracy: {time_accuracy:.4f}")
        logger.info(f"Space complexity prediction accuracy: {space_accuracy:.4f}")
        
        # Create and save confusion matrices
        self._plot_confusion_matrix(y_time_test, y_time_pred, "time_complexity_confusion.png")
        self._plot_confusion_matrix(y_space_test, y_space_pred, "space_complexity_confusion.png")
        
        # Prepare evaluation dictionary
        evaluation = {
            'time_complexity': {
                'accuracy': time_accuracy,
                'report': time_report
            },
            'space_complexity': {
                'accuracy': space_accuracy,
                'report': space_report
            }
        }
        
        return evaluation
    
    def _plot_confusion_matrix(self, y_true: pd.Series, y_pred: pd.Series, filename: str) -> None:
        """
        Create and save a confusion matrix visualization
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            filename: Output filename
        """
        try:
            # Create confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            
            # Create class labels
            classes = sorted(set(y_true) | set(y_pred))
            class_labels = [self.reverse_mapping.get(c, f"O(n^{c})") for c in classes]
            
            # Plot
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_labels, yticklabels=class_labels)
            plt.xlabel('Predicted')
            plt.ylabel('True')
            plt.title('Confusion Matrix')
            
            # Save
            output_path = os.path.join(self.model_dir, filename)
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Confusion matrix saved to {output_path}")
            
        except Exception as e:
            logger.warning(f"Failed to plot confusion matrix: {str(e)}")
    
    def feature_importance(self, plot: bool = True) -> Dict[str, Dict[str, float]]:
        """
        Get feature importance for complexity prediction
        
        Args:
            plot: Whether to create and save importance plots
            
        Returns:
            Dictionary with feature importances
        """
        if self.time_model is None or self.space_model is None:
            raise ValueError("Models not trained or loaded. Call train_complexity_predictor or load_predictor first.")
        
        if self.feature_names is None:
            logger.warning("Feature names not available")
            feature_names = [f"feature_{i}" for i in range(len(self.time_model.feature_importances_))]
        else:
            feature_names = self.feature_names
        
        # Get importances
        time_importances = self.time_model.feature_importances_
        space_importances = self.space_model.feature_importances_
        
        # Create dictionaries
        time_importance_dict = dict(zip(feature_names, time_importances))
        space_importance_dict = dict(zip(feature_names, space_importances))
        
        # Sort by importance
        time_importance_dict = {k: v for k, v in sorted(time_importance_dict.items(), key=lambda item: item[1], reverse=True)}
        space_importance_dict = {k: v for k, v in sorted(space_importance_dict.items(), key=lambda item: item[1], reverse=True)}
        
        if plot:
            self._plot_feature_importance(time_importance_dict, "time_feature_importance.png", "Time Complexity")
            self._plot_feature_importance(space_importance_dict, "space_feature_importance.png", "Space Complexity")
        
        return {
            'time_complexity': time_importance_dict,
            'space_complexity': space_importance_dict
        }
    
    def _plot_feature_importance(self, importance_dict: Dict[str, float], filename: str, title_prefix: str) -> None:
        """
        Create and save a feature importance visualization
        
        Args:
            importance_dict: Dictionary of feature importances
            filename: Output filename
            title_prefix: Prefix for the plot title
        """
        try:
            # Sort by importance
            features = list(importance_dict.keys())
            importances = list(importance_dict.values())
            
            # Limit to top 15 features if there are many
            if len(features) > 15:
                features = features[:15]
                importances = importances[:15]
            
            # Plot
            plt.figure(figsize=(12, 8))
            bars = plt.barh(range(len(features)), importances, align='center')
            plt.yticks(range(len(features)), features)
            plt.xlabel('Importance')
            plt.title(f'{title_prefix} Feature Importance')
            
            # Add values to bars
            for i, v in enumerate(importances):
                plt.text(v + 0.01, i, f"{v:.4f}")
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.model_dir, filename)
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Feature importance plot saved to {output_path}")
            
        except Exception as e:
            logger.warning(f"Failed to plot feature importance: {str(e)}")
    
    def save_predictor(self, path: str = None) -> None:
        """
        Save trained models and metadata
        
        Args:
            path: Directory to save models (default: self.model_dir)
        """
        if self.time_model is None or self.space_model is None:
            raise ValueError("Models not trained. Call train_complexity_predictor first.")
        
        if path is None:
            path = self.model_dir
        
        os.makedirs(path, exist_ok=True)
        
        # Save models
        time_model_path = os.path.join(path, 'time_complexity_model.pkl')
        space_model_path = os.path.join(path, 'space_complexity_model.pkl')
        
        joblib.dump(self.time_model, time_model_path)
        joblib.dump(self.space_model, space_model_path)
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'complexity_mapping': self.complexity_mapping,
            'reverse_mapping': self.reverse_mapping,
            'time_model_params': self.time_model.get_params(),
            'space_model_params': self.space_model.get_params()
        }
        
        metadata_path = os.path.join(path, 'complexity_predictor_metadata.pkl')
        joblib.dump(metadata, metadata_path)
        
        logger.info(f"Models and metadata saved to {path}")
    
    def load_predictor(self, path: str = None) -> None:
        """
        Load trained models and metadata
        
        Args:
            path: Directory to load models from (default: self.model_dir)
        """
        if path is None:
            path = self.model_dir
        
        # Check if model files exist
        time_model_path = os.path.join(path, 'time_complexity_model.pkl')
        space_model_path = os.path.join(path, 'space_complexity_model.pkl')
        metadata_path = os.path.join(path, 'complexity_predictor_metadata.pkl')
        
        if not (os.path.exists(time_model_path) and 
                os.path.exists(space_model_path) and 
                os.path.exists(metadata_path)):
            raise FileNotFoundError(f"Model files not found in {path}")
        
        # Load models
        self.time_model = joblib.load(time_model_path)
        self.space_model = joblib.load(space_model_path)
        
        # Load metadata
        metadata = joblib.load(metadata_path)
        self.feature_names = metadata['feature_names']
        self.complexity_mapping = metadata['complexity_mapping']
        self.reverse_mapping = metadata['reverse_mapping']
        
        logger.info(f"Models and metadata loaded from {path}")
    
    def complexity_comparison(self, original_features: pd.DataFrame, optimized_features: pd.DataFrame) -> Dict[str, Any]:
        """
        Compare complexity between original and optimized code
        
        Args:
            original_features: Features of original code
            optimized_features: Features of optimized code
            
        Returns:
            Dictionary with comparison results
        """
        # Predict complexities
        orig_time_pred, orig_space_pred = self.predict_complexity(original_features)
        opt_time_pred, opt_space_pred = self.predict_complexity(optimized_features)
        
        # Get string representations
        orig_time_str, orig_space_str = self.predict_complexity_string(original_features)
        opt_time_str, opt_space_str = self.predict_complexity_string(optimized_features)
        
        # Check if there's an improvement
        time_improved = orig_time_pred > opt_time_pred
        space_improved = orig_space_pred > opt_space_pred
        
        # Calculate improvement level (difference in complexity class)
        time_improvement = orig_time_pred - opt_time_pred
        space_improvement = orig_space_pred - opt_space_pred
        
        # Create comparison result
        comparison = {
            'original': {
                'time_complexity': orig_time_str[0],
                'time_complexity_value': int(orig_time_pred[0]),
                'space_complexity': orig_space_str[0],
                'space_complexity_value': int(orig_space_pred[0])
            },
            'optimized': {
                'time_complexity': opt_time_str[0],
                'time_complexity_value': int(opt_time_pred[0]),
                'space_complexity': opt_space_str[0],
                'space_complexity_value': int(opt_space_pred[0])
            },
            'improvement': {
                'time_improved': bool(time_improved[0]),
                'time_improvement_level': int(time_improvement[0]),
                'space_improved': bool(space_improved[0]),
                'space_improvement_level': int(space_improvement[0])
            },
            'summary': self._generate_improvement_summary(
                orig_time_str[0], opt_time_str[0], 
                orig_space_str[0], opt_space_str[0],
                bool(time_improved[0]), bool(space_improved[0])
            )
        }
        
        return comparison
    
    def _generate_improvement_summary(self, orig_time: str, opt_time: str, 
                                     orig_space: str, opt_space: str,
                                     time_improved: bool, space_improved: bool) -> str:
        """
        Generate a human-readable summary of the optimization improvements
        
        Args:
            orig_time: Original time complexity
            opt_time: Optimized time complexity
            orig_space: Original space complexity
            opt_space: Optimized space complexity
            time_improved: Whether time complexity improved
            space_improved: Whether space complexity improved
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        if time_improved:
            summary_parts.append(f"Time complexity improved from {orig_time} to {opt_time}")
        elif orig_time != opt_time:
            summary_parts.append(f"Time complexity changed from {orig_time} to {opt_time}")
        else:
            summary_parts.append(f"Time complexity remained the same at {orig_time}")
            
        if space_improved:
            summary_parts.append(f"Space complexity improved from {orig_space} to {opt_space}")
        elif orig_space != opt_space:
            summary_parts.append(f"Space complexity changed from {orig_space} to {opt_space}")
        else:
            summary_parts.append(f"Space complexity remained the same at {orig_space}")
        
        if time_improved or space_improved:
            summary_parts.append("The optimization successfully improved the algorithm's performance.")
        elif orig_time != opt_time or orig_space != opt_space:
            summary_parts.append("The optimization changed the algorithm's characteristics but without clear performance improvement.")
        else:
            summary_parts.append("The optimization did not change the algorithm's complexity.")
        
        return " ".join(summary_parts)


def prepare_features_for_prediction(code: str) -> pd.DataFrame:
    """
    Extract and prepare code features for prediction
    
    Args:
        code: Python code as string
        
    Returns:
        DataFrame ready for prediction
    """
    # Create ComplexityPredictor instance to use its feature extraction
    predictor = ComplexityPredictor()
    
    # Extract enhanced features
    features = predictor.extract_enhanced_features(code)
    
    # Convert to DataFrame
    df = pd.DataFrame([features])
    
    return df


def train_from_sample_algorithms(model_dir: str = None) -> ComplexityPredictor:
    """
    Train complexity predictor using sample algorithms with known complexities
    
    Args:
        model_dir: Directory to save models
        
    Returns:
        Trained ComplexityPredictor instance
    """
    # Sample algorithms with known complexities
    SAMPLE_ALGORITHMS = {
        "constant_time": {
            "code": "def constant_time(arr):\n    if len(arr) > 0:\n        return arr[0]\n    return None",
            "time_complexity": 1,  # O(1)
            "space_complexity": 1  # O(1)
        },
        "binary_search": {
            "code": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    \n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    \n    return -1",
            "time_complexity": 2,  # O(log n)
            "space_complexity": 1  # O(1)
        },
        "linear_search": {
            "code": "def linear_search(arr, target):\n    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n    return -1",
            "time_complexity": 3,  # O(n)
            "space_complexity": 1  # O(1)
        },
        "sum_array": {
            "code": "def sum_array(arr):\n    total = 0\n    for num in arr:\n        total += num\n    return total",
            "time_complexity": 3,  # O(n)
            "space_complexity": 1  # O(1)
        },
        "merge_sort": {
            "code": "def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n        \n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    \n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    \n    while i < len(left) and j < len(right):\n        if left[i] < right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n    \n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result",
            "time_complexity": 4,  # O(n log n)
            "space_complexity": 3  # O(n)
        },
        "quick_sort": {
            "code": "def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    \n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    \n    return quick_sort(left) + middle + quick_sort(right)",
            "time_complexity": 4,  # O(n log n)
            "space_complexity": 3  # O(n)
        },
        "bubble_sort": {
            "code": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr",
            "time_complexity": 5,  # O(n²)
            "space_complexity": 1  # O(1)
        },
        "matrix_multiply": {
            "code": "def matrix_multiply(A, B):\n    n = len(A)\n    C = [[0 for _ in range(n)] for _ in range(n)]\n    \n    for i in range(n):\n        for j in range(n):\n            for k in range(n):\n                C[i][j] += A[i][k] * B[k][j]\n                \n    return C",
            "time_complexity": 6,  # O(n³)
            "space_complexity": 3  # O(n²)
        },
        "recursive_fibonacci": {
            "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "time_complexity": 7,  # O(2^n)
            "space_complexity": 3  # O(n)
        }
    }
    
    # Initialize predictor
    predictor = ComplexityPredictor(model_dir=model_dir)
    
    # Create training data
    sample_features = []
    time_complexities = []
    space_complexities = []
    
    for name, data in SAMPLE_ALGORITHMS.items():
        # Extract features
        features = predictor.extract_enhanced_features(data["code"])
        
        # Add to training data
        sample_features.append(features)
        time_complexities.append(data["time_complexity"])
        space_complexities.append(data["space_complexity"])
    
    # Convert to DataFrame and Series
    X = pd.DataFrame(sample_features)
    y_time = pd.Series(time_complexities)
    y_space = pd.Series(space_complexities)
    
    # Train model
    predictor.train_complexity_predictor(X, y_time, y_space, optimize=False)
    
    # Save model
    predictor.save_predictor()
    
    return predictor


def main():
    """Main function to train and evaluate the complexity predictor"""
    try:
        # Get paths
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_dir = os.path.join(project_root, 'models', 'random_forest')
        
        # Check if we have an existing dataset or should use sample algorithms
        try:
            processed_data_path = os.path.join(project_root, 'data', 'processed', 'processed_dataset.csv')
            if os.path.exists(processed_data_path):
                logger.info(f"Using processed dataset from {processed_data_path}")
                
                # Load data
                df = pd.read_csv(processed_data_path)
                logger.info(f"Loaded {len(df)} samples")
                
                # Extract enhanced features
                logger.info("Extracting enhanced features")
                predictor = ComplexityPredictor(model_dir=model_dir)
                
                features = []
                for code in df['clean_code'].iloc[:100]:  # Use a subset to speed up process
                    if isinstance(code, str):
                        feature_dict = predictor.extract_enhanced_features(code)
                        features.append(feature_dict)
                    else:
                        features.append({})
                
                # Convert to DataFrame
                features_df = pd.DataFrame(features)
                
                # Get complexity values
                if 'time_complexity_value' in df.columns and 'space_complexity_value' in df.columns:
                    y_time = df['time_complexity_value'].iloc[:100]
                    y_space = df['space_complexity_value'].iloc[:100]
                    
                    # Split data
                    X_train, X_test, y_time_train, y_time_test, y_space_train, y_space_test = train_test_split(
                        features_df, y_time, y_space, test_size=0.2, random_state=42
                    )
                    
                    # Train model
                    predictor.train_complexity_predictor(X_train, y_time_train, y_space_train)
                    
                    # Evaluate
                    evaluation = predictor.evaluate_predictor(X_test, y_time_test, y_space_test)
                    
                    # Save model
                    predictor.save_predictor()
                    
                else:
                    logger.warning("No complexity values in dataset, using sample algorithms instead")
                    predictor = train_from_sample_algorithms(model_dir)
            else:
                logger.info("No processed dataset found, using sample algorithms")
                predictor = train_from_sample_algorithms(model_dir)
                
        except Exception as e:
            logger.warning(f"Error processing dataset: {str(e)}")
            logger.info("Using sample algorithms instead")
            predictor = train_from_sample_algorithms(model_dir)
        
        logger.info("Model training and evaluation complete")
        return 0
    
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())