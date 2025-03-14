"""
Complexity Analyzer Module for EFFICODE-ACRR

This module analyzes and predicts the time and space complexity of algorithms:
- Estimates time complexity of code snippets
- Estimates space complexity of code snippets
- Compares complexities between original and optimized code
- Loads and uses the trained RandomForest complexity predictor

"""

import os
import sys
import logging
import pandas as pd
import json
from typing import Dict, List, Tuple, Union, Optional, Any

# Add parent directory to path so we can import from models
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """Analyzer for time and space complexity of algorithms"""
    
    def __init__(self, model_dir: str = None):
        """
        Initialize the complexity analyzer
        
        Args:
            model_dir: Directory containing trained RandomForest models (optional)
        """
        # Import is handled in the _load_complexity_predictor method
        
        # Load predictor model
        self.predictor = self._load_complexity_predictor(model_dir)
        
        # Complexity mapping for human-readable output
        self.complexity_mapping = {
            1: "O(1)",            # Constant
            2: "O(log n)",        # Logarithmic
            3: "O(n)",            # Linear
            4: "O(n log n)",      # Linearithmic
            5: "O(n²)",           # Quadratic
            6: "O(n³)",           # Cubic
            7: "O(2^n)",          # Exponential
            8: "O(n!)"            # Factorial
        }
        
        # Reverse mapping for lookup
        self.reverse_mapping = {v: k for k, v in self.complexity_mapping.items()}
        
        # Complexity explanation templates
        self.complexity_explanations = {
            1: "constant time - the algorithm's runtime does not increase with input size",
            2: "logarithmic time - the algorithm divides the problem space in each step",
            3: "linear time - the algorithm's runtime grows linearly with input size",
            4: "linearithmic time - the algorithm combines linear and logarithmic behavior",
            5: "quadratic time - typically involves nested loops over the input",
            6: "cubic time - typically involves triple-nested loops over the input",
            7: "exponential time - typically uses recursive algorithms without memoization",
            8: "factorial time - typically involves generating all permutations"
        }
        
        logger.info("ComplexityAnalyzer initialized")
    
    def _load_complexity_predictor(self, model_dir: str = None) -> Any:
        """
        Load the trained RandomForest complexity predictor
        
        Args:
            model_dir: Directory containing trained models
            
        Returns:
            Loaded ComplexityPredictor instance
        """
        # Import here to avoid circular imports
        try:
            from models.random_forest import ComplexityPredictor
        except ImportError:
            # Alternative import path if the first one fails
            sys.path.insert(0, os.path.join(project_root, 'models'))
            from random_forest import ComplexityPredictor
        
        if model_dir is None:
            # Default to models/random_forest directory relative to this file
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = os.path.join(project_root, 'models', 'random_forest')
        
        predictor = ComplexityPredictor(model_dir=model_dir)
        
        try:
            # Try to load the trained model
            predictor.load_predictor()
            logger.info(f"Loaded complexity predictor from {model_dir}")
        except FileNotFoundError:
            # If model doesn't exist, train a new one with sample algorithms
            logger.warning(f"No trained model found in {model_dir}. Training new model with sample algorithms.")
            try:
                # Use the train_from_sample_algorithms function from random_forest module
                try:
                    from models.random_forest import train_from_sample_algorithms
                except ImportError:
                    from random_forest import train_from_sample_algorithms
                predictor = train_from_sample_algorithms(model_dir)
                logger.info("Trained new complexity predictor with sample algorithms")
            except Exception as e:
                logger.error(f"Error training new model: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error loading complexity predictor: {str(e)}")
            raise
        
        return predictor
    
    def analyze_time_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze and estimate the time complexity of a code snippet
        
        Args:
            code: Python code as string
            
        Returns:
            Dictionary with time complexity analysis results
        """
        if not isinstance(code, str) or not code.strip():
            return {
                "complexity": "Unknown",
                "complexity_value": 0,
                "explanation": "Unable to analyze empty or invalid code",
                "confidence": 0.0
            }
        
        try:
            # Prepare features for prediction
            features = self._prepare_features(code)
            
            # Predict time complexity
            time_value_list, _ = self.predictor.predict_complexity(features)
            time_value = time_value_list[0]
            
            # Convert to string representation
            time_complexity = self.complexity_mapping.get(time_value, f"O(n^{time_value})")
            
            # Get explanation
            explanation = self.complexity_explanations.get(
                time_value, 
                f"complexity with behavior proportional to n^{time_value}"
            )
            
            # For a real system, we'd have confidence scores
            # Here we use a placeholder since our model doesn't provide them
            confidence = 0.85  # Placeholder confidence value
            
            return {
                "complexity": time_complexity,
                "complexity_value": int(time_value),
                "explanation": explanation,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing time complexity: {str(e)}")
            return {
                "complexity": "Unknown",
                "complexity_value": 0,
                "explanation": f"Error during analysis: {str(e)}",
                "confidence": 0.0
            }
    
    def analyze_space_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze and estimate the space complexity of a code snippet
        
        Args:
            code: Python code as string
            
        Returns:
            Dictionary with space complexity analysis results
        """
        if not isinstance(code, str) or not code.strip():
            return {
                "complexity": "Unknown",
                "complexity_value": 0,
                "explanation": "Unable to analyze empty or invalid code",
                "confidence": 0.0
            }
        
        try:
            # Prepare features for prediction
            features = self._prepare_features(code)
            
            # Predict space complexity
            _, space_value_list = self.predictor.predict_complexity(features)
            space_value = space_value_list[0]
            
            # Convert to string representation
            space_complexity = self.complexity_mapping.get(space_value, f"O(n^{space_value})")
            
            # Get explanation
            explanation = self.complexity_explanations.get(
                space_value, 
                f"complexity with memory usage proportional to n^{space_value}"
            )
            
            # For a real system, we'd have confidence scores
            # Here we use a placeholder since our model doesn't provide them
            confidence = 0.80  # Placeholder confidence value
            
            return {
                "complexity": space_complexity,
                "complexity_value": int(space_value),
                "explanation": explanation,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing space complexity: {str(e)}")
            return {
                "complexity": "Unknown",
                "complexity_value": 0,
                "explanation": f"Error during analysis: {str(e)}",
                "confidence": 0.0
            }
    
    def analyze_code_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze both time and space complexity of a code snippet
        
        Args:
            code: Python code as string
            
        Returns:
            Dictionary with both time and space complexity analysis
        """
        time_analysis = self.analyze_time_complexity(code)
        space_analysis = self.analyze_space_complexity(code)
        
        # Detect algorithm category based on code patterns
        algorithm_category = self._detect_algorithm_category(code)
        
        return {
            "time_complexity": time_analysis,
            "space_complexity": space_analysis,
            "algorithm_category": algorithm_category,
            "code_metrics": self._extract_code_metrics(code)
        }
    
    def compare_complexities(self, original_code: str, optimized_code: str) -> Dict[str, Any]:
        """
        Compare complexities between original and optimized code
        
        Args:
            original_code: Original Python code as string
            optimized_code: Optimized Python code as string
            
        Returns:
            Dictionary with comparison results and detailed analysis
        """
        if not isinstance(original_code, str) or not original_code.strip():
            return {"error": "Original code is empty or invalid"}
        
        if not isinstance(optimized_code, str) or not optimized_code.strip():
            return {"error": "Optimized code is empty or invalid"}
        
        try:
            # Analyze both code snippets
            original_analysis = self.analyze_code_complexity(original_code)
            optimized_analysis = self.analyze_code_complexity(optimized_code)
            
            # Check if there's an improvement
            time_orig_value = original_analysis["time_complexity"]["complexity_value"]
            time_opt_value = optimized_analysis["time_complexity"]["complexity_value"]
            time_improved = time_orig_value > time_opt_value
            
            space_orig_value = original_analysis["space_complexity"]["complexity_value"]
            space_opt_value = optimized_analysis["space_complexity"]["complexity_value"]
            space_improved = space_orig_value > space_opt_value
            
            # Calculate improvement factor
            # Here we provide a simple analysis for improvements within the same complexity class
            # In a real system, you might execute benchmarks to get actual improvements
            time_improvement_factor = self._calculate_improvement_factor(time_orig_value, time_opt_value)
            space_improvement_factor = self._calculate_improvement_factor(space_orig_value, space_opt_value)
            
            # Generate explanation of improvements
            explanation = self._generate_comparison_explanation(
                original_analysis, optimized_analysis,
                time_improved, space_improved
            )
            
            # Construct comparison result
            comparison = {
                "original": {
                    "time_complexity": original_analysis["time_complexity"]["complexity"],
                    "time_complexity_value": time_orig_value,
                    "space_complexity": original_analysis["space_complexity"]["complexity"],
                    "space_complexity_value": space_orig_value,
                    "algorithm_category": original_analysis["algorithm_category"],
                    "code_metrics": original_analysis["code_metrics"]
                },
                "optimized": {
                    "time_complexity": optimized_analysis["time_complexity"]["complexity"],
                    "time_complexity_value": time_opt_value,
                    "space_complexity": optimized_analysis["space_complexity"]["complexity"],
                    "space_complexity_value": space_opt_value,
                    "algorithm_category": optimized_analysis["algorithm_category"],
                    "code_metrics": optimized_analysis["code_metrics"]
                },
                "improvements": {
                    "time_improved": time_improved,
                    "time_improvement_class_change": time_orig_value - time_opt_value,
                    "time_improvement_factor": time_improvement_factor,
                    "space_improved": space_improved,
                    "space_improvement_class_change": space_orig_value - space_opt_value,
                    "space_improvement_factor": space_improvement_factor
                },
                "explanation": explanation
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing complexities: {str(e)}")
            return {
                "error": f"Error during comparison: {str(e)}"
            }
    
    def _prepare_features(self, code: str) -> pd.DataFrame:
        """
        Extract and prepare features for complexity prediction
        
        Args:
            code: Python code as string
            
        Returns:
            DataFrame with features for prediction
        """
        # Import here to avoid circular imports
        try:
            from models.random_forest import prepare_features_for_prediction
        except ImportError:
            from random_forest import prepare_features_for_prediction
        
        return prepare_features_for_prediction(code)
    
    def _detect_algorithm_category(self, code: str) -> str:
        """
        Detect the algorithm category based on code patterns
        
        Args:
            code: Python code as string
            
        Returns:
            Algorithm category as string
        """
        from utils import detect_algorithm_type
        
        return detect_algorithm_type(code)
    
    def _extract_code_metrics(self, code: str) -> Dict[str, int]:
        """
        Extract basic code metrics for comparison
        
        Args:
            code: Python code as string
            
        Returns:
            Dictionary with code metrics
        """
        from utils import count_code_elements
        
        return count_code_elements(code)
    
    def _calculate_improvement_factor(self, original_value: int, optimized_value: int) -> float:
        """
        Calculate improvement factor between complexity classes
        
        Args:
            original_value: Original complexity class value
            optimized_value: Optimized complexity class value
            
        Returns:
            Improvement factor as float
        """
        if original_value == optimized_value:
            return 1.0  # No improvement
        
        if original_value == 0 or optimized_value == 0:
            return 1.0  # Unable to calculate
        
        # Approximate improvement factors based on complexity classes
        # These are rough estimates for typical improvements when moving between classes
        improvement_matrix = {
            # from -> to: improvement factor
            (5, 4): 10.0,     # O(n²) -> O(n log n): ~10x speedup for large n
            (5, 3): 100.0,    # O(n²) -> O(n): ~100x speedup for large n
            (4, 3): 10.0,     # O(n log n) -> O(n): ~10x speedup for large n
            (6, 5): 100.0,    # O(n³) -> O(n²): ~100x speedup for large n
            (6, 4): 1000.0,   # O(n³) -> O(n log n): ~1000x speedup for large n
            (7, 5): 1000000.0, # O(2^n) -> O(n²): massive improvement
            (7, 4): 10000000.0, # O(2^n) -> O(n log n): massive improvement
            (7, 3): 100000000.0 # O(2^n) -> O(n): massive improvement
        }
        
        return improvement_matrix.get((original_value, optimized_value), 
                                     10.0 ** (original_value - optimized_value))
    
    def _generate_comparison_explanation(self, 
                                       original_analysis: Dict[str, Any], 
                                       optimized_analysis: Dict[str, Any],
                                       time_improved: bool,
                                       space_improved: bool) -> str:
        """
        Generate a detailed explanation of complexity improvements
        
        Args:
            original_analysis: Analysis of original code
            optimized_analysis: Analysis of optimized code
            time_improved: Whether time complexity improved
            space_improved: Whether space complexity improved
            
        Returns:
            Detailed explanation as string
        """
        explanation_parts = []
        
        # Get complexity strings
        orig_time = original_analysis["time_complexity"]["complexity"]
        opt_time = optimized_analysis["time_complexity"]["complexity"]
        orig_space = original_analysis["space_complexity"]["complexity"]
        opt_space = optimized_analysis["space_complexity"]["complexity"]
        
        # Get metrics for comparison
        orig_loops = original_analysis["code_metrics"]["loops"]
        opt_loops = optimized_analysis["code_metrics"]["loops"]
        orig_lines = original_analysis["code_metrics"]["lines"]
        opt_lines = optimized_analysis["code_metrics"]["lines"]
        
        # Algorithm category
        orig_algo = original_analysis["algorithm_category"]
        opt_algo = optimized_analysis["algorithm_category"]
        
        # Improvement explanation
        if time_improved:
            explanation_parts.append(
                f"Time complexity improved from {orig_time} to {opt_time}. "
                f"This represents a significant performance improvement, especially for larger inputs."
            )
            
            # Add specific explanation based on the type of improvement
            if orig_time == "O(n²)" and opt_time == "O(n log n)":
                explanation_parts.append(
                    "The optimization typically involves replacing a nested loop approach with "
                    "a more efficient divide-and-conquer or sorting-based algorithm."
                )
            elif orig_time == "O(n²)" and opt_time == "O(n)":
                explanation_parts.append(
                    "The optimization likely eliminates nested iterations in favor of a "
                    "single-pass approach, possibly using additional data structures."
                )
            elif opt_time == "O(log n)":
                explanation_parts.append(
                    "The optimized algorithm uses a divide-and-conquer approach that reduces "
                    "the problem size by a constant factor in each step."
                )
        elif orig_time != opt_time:
            explanation_parts.append(
                f"Time complexity changed from {orig_time} to {opt_time}, "
                f"but this does not necessarily represent an improvement."
            )
        else:
            explanation_parts.append(
                f"Time complexity remained at {orig_time}. "
            )
            
            # If same complexity class but fewer loops or operations
            if opt_loops < orig_loops:
                explanation_parts.append(
                    f"However, the optimized code uses fewer loops ({opt_loops} vs {orig_loops}), "
                    f"which may result in better performance constants."
                )
        
        # Space complexity explanation
        if space_improved:
            explanation_parts.append(
                f"Space complexity improved from {orig_space} to {opt_space}. "
                f"This means the algorithm uses less memory, which is beneficial for large inputs."
            )
        elif orig_space != opt_space:
            explanation_parts.append(
                f"Space complexity changed from {orig_space} to {opt_space}. "
                f"Note that sometimes additional space usage enables faster time complexity."
            )
        else:
            explanation_parts.append(
                f"Space complexity remained at {orig_space}. "
            )
        
        # Algorithm change explanation
        if orig_algo != opt_algo:
            explanation_parts.append(
                f"The optimization changed the algorithm category from {orig_algo} to {opt_algo}, "
                f"likely employing a different algorithmic approach."
            )
        
        # Code metrics explanation
        if opt_lines < orig_lines:
            explanation_parts.append(
                f"The optimized code is more concise ({opt_lines} lines vs {orig_lines} lines), "
                f"which can make it easier to maintain and reason about."
            )
        
        return " ".join(explanation_parts)


def analyze_time_complexity(code: str) -> Dict[str, Any]:
    """
    Convenience function to analyze time complexity of a code snippet
    
    Args:
        code: Python code as string
        
    Returns:
        Dictionary with time complexity analysis
    """
    analyzer = ComplexityAnalyzer()
    return analyzer.analyze_time_complexity(code)


def analyze_space_complexity(code: str) -> Dict[str, Any]:
    """
    Convenience function to analyze space complexity of a code snippet
    
    Args:
        code: Python code as string
        
    Returns:
        Dictionary with space complexity analysis
    """
    analyzer = ComplexityAnalyzer()
    return analyzer.analyze_space_complexity(code)


def compare_complexities(original_code: str, optimized_code: str) -> Dict[str, Any]:
    """
    Convenience function to compare complexities between original and optimized code
    
    Args:
        original_code: Original Python code as string
        optimized_code: Optimized Python code as string
        
    Returns:
        Dictionary with comparison results
    """
    analyzer = ComplexityAnalyzer()
    return analyzer.compare_complexities(original_code, optimized_code)


def load_complexity_predictor(model_dir: str = None) -> Any:
    """
    Convenience function to load the complexity predictor
    
    Args:
        model_dir: Directory containing trained models
        
    Returns:
        Loaded ComplexityPredictor instance
    """
    analyzer = ComplexityAnalyzer(model_dir=model_dir)
    return analyzer.predictor


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Analyze file if provided
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            analyzer = ComplexityAnalyzer()
            result = analyzer.analyze_code_complexity(code)
            
            print(f"\nComplexity Analysis for {file_path}")
            print(f"Time Complexity: {result['time_complexity']['complexity']}")
            print(f"Space Complexity: {result['space_complexity']['complexity']}")
            print(f"Algorithm Category: {result['algorithm_category']}")
            print("\nExplanation:")
            print(f"Time: {result['time_complexity']['explanation']}")
            print(f"Space: {result['space_complexity']['explanation']}")
            
        except Exception as e:
            print(f"Error analyzing file: {str(e)}")
            sys.exit(1)
    else:
        # Example code to demonstrate the analyzer
        example_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
        
        optimized_code = """
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
"""
        
        analyzer = ComplexityAnalyzer()
        result = analyzer.compare_complexities(example_code, optimized_code)
        
        print("\nComplexity Comparison Example")
        print(f"Original Time Complexity: {result['original']['time_complexity']}")
        print(f"Optimized Time Complexity: {result['optimized']['time_complexity']}")
        print(f"Original Space Complexity: {result['original']['space_complexity']}")
        print(f"Optimized Space Complexity: {result['optimized']['space_complexity']}")
        print("\nExplanation:")
        print(result['explanation'])