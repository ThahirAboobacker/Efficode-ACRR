"""
Explanation Generator Module for EFFICODE-ACRR

This module provides functionality for generating human-readable explanations
of code optimizations using either rule-based techniques or the FLAN-T5 language model.
"""

import os
import sys
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for model imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
models_dir = os.path.join(parent_dir, 'models')
sys.path.insert(0, parent_dir)
sys.path.insert(0, models_dir)
sys.path.insert(0, current_dir)  # Also add current directory to support relative imports

# Default path to the fine-tuned model
FINE_TUNED_MODEL_PATH = os.path.join(parent_dir, 'models', 'flan_t5_fine_tuned')

# Import FLAN-T5 using multiple approaches to ensure it works in different environments
FLANT5_AVAILABLE = False

# First try the recommended import path from models.flan_t5
try:
    from models.flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
    FLANT5_AVAILABLE = True
    logger.info("FLAN-T5 model imported successfully (models.flan_t5)")
except ImportError:
    # If that fails, try direct import
    try:
        from flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
        FLANT5_AVAILABLE = True
        logger.info("FLAN-T5 model imported successfully (direct)")
    except ImportError:
        try:
            # Try relative import
            from ..models.flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
            FLANT5_AVAILABLE = True
            logger.info("FLAN-T5 model imported successfully (relative)")
        except (ImportError, ValueError):
            try:
                # Try absolute import with backend prefix
                from backend.models.flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
                FLANT5_AVAILABLE = True
                logger.info("FLAN-T5 model imported successfully (absolute)")
            except ImportError:
                try:
                    # Try with local path
                    sys.path.append(os.path.join(parent_dir, 'models'))
                    from flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
                    FLANT5_AVAILABLE = True
                    logger.info("FLAN-T5 model imported successfully (local path)")
                except ImportError:
                    logger.warning("FLAN-T5 model not available. Using rule-based explanations only.")
                    # Define dummy classes for type checking to work
                    class FlanT5ExplanationGenerator:
                        pass
                    def get_explanation_generator(*args, **kwargs):
                        return None

# Singleton instance of explanation generator
_explanation_generator = None

def get_generator(
    use_neural_model: bool = True, 
    model_path: Optional[str] = None,
    offline_mode: bool = False,
    timeout: int = 60
) -> Optional[Any]:
    """
    Get or initialize the explanation generator.
    
    Args:
        use_neural_model: Whether to use the neural model (FLAN-T5) for explanations
        model_path: Optional path to a fine-tuned model
        offline_mode: If True, will use rule-based generation when model is unavailable
        timeout: Timeout in seconds for model loading
        
    Returns:
        Explanation generator instance or None if not available
    """
    global _explanation_generator
    
    if not use_neural_model or not FLANT5_AVAILABLE:
        logger.warning("Neural model not used: use_neural_model=%s, FLANT5_AVAILABLE=%s", 
                      use_neural_model, FLANT5_AVAILABLE)
        return None
    
    # Use fine-tuned model by default if no specific path is provided
    if model_path is None:
        # Always check if fine-tuned model exists at the standard location
        if os.path.exists(FINE_TUNED_MODEL_PATH):
            model_path = FINE_TUNED_MODEL_PATH
            logger.info(f"Using fine-tuned model from {model_path}")
        else:
            logger.warning(f"Fine-tuned model not found at {FINE_TUNED_MODEL_PATH}, falling back to base model")
        
    if _explanation_generator is None:
        try:
            logger.info(f"Initializing explanation generator with model_path={model_path}, timeout={timeout}s")
            _explanation_generator = get_explanation_generator(
                model_path=model_path,
                offline_mode=offline_mode,
                timeout=timeout
            )
            logger.info(f"Successfully initialized FLAN-T5 explanation generator")
            
            # Add model path attribute for reference
            if hasattr(_explanation_generator, 'model_path'):
                logger.info(f"Using model from: {_explanation_generator.model_path}")
            elif model_path:
                setattr(_explanation_generator, 'model_path', model_path)
                
        except Exception as e:
            logger.error(f"Error initializing explanation generator: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
            
    return _explanation_generator

def generate_explanation(
    original_code: str, 
    optimized_code: str, 
    applied_rules: List[str], 
    complexity_comparison: Dict[str, Any],
    use_neural_model: bool = True,
    force_rule_based: bool = False,
    timeout: int = 60
) -> str:
    """
    Generate a human-readable explanation of code optimization.
    
    Args:
        original_code: The original, unoptimized code
        optimized_code: The optimized version of the code
        applied_rules: List of applied optimization rules or techniques
        complexity_comparison: Dictionary with complexity analysis results
        use_neural_model: Whether to use the neural model (FLAN-T5) for explanation
        force_rule_based: Force using rule-based explanation even if model is available
        timeout: Timeout in seconds for model loading
        
    Returns:
        A human-readable explanation of the optimization
    """
    # Extract complexity information from comparison
    complexity_before = complexity_comparison.get("original_complexity", "unknown")
    complexity_after = complexity_comparison.get("optimized_complexity", "unknown")
    
    # If no changes were made, return a simple explanation
    if original_code == optimized_code or not applied_rules:
        return "No significant optimizations were applied to the code."
    
    # Check if neural explanation is available
    if use_neural_model and FLANT5_AVAILABLE and not force_rule_based:
        # Create generator - will use fine-tuned model by default via get_generator
        generator = get_generator(use_neural_model=True, timeout=timeout)
        
        if generator:
            try:
                # Generate explanation using FLAN-T5
                logger.info("Generating explanation using FLAN-T5 model")
                explanation = generator.generate_explanation(
                    original_code=original_code,
                    optimized_code=optimized_code,
                    complexity_before=complexity_before,
                    complexity_after=complexity_after,
                    applied_rules=applied_rules,
                    force_rule_based=force_rule_based
                )
                
                # Format the explanation
                formatted_explanation = generator.format_explanation(explanation)
                logger.info("Generated explanation using FLAN-T5 model")
                return formatted_explanation
            except Exception as e:
                logger.error(f"Error generating explanation with FLAN-T5: {e}")
                logger.info("Falling back to rule-based explanation")
                import traceback
                logger.error(traceback.format_exc())
                # Fall back to rule-based explanation
    
    # Generate rule-based explanation if neural is not available or failed
    return generate_rule_based_explanation(
        original_code, 
        optimized_code, 
        applied_rules, 
        complexity_before, 
        complexity_after
    )
    
def generate_rule_based_explanation(
    original_code: str, 
    optimized_code: str, 
    applied_rules: List[str], 
    complexity_before: str, 
    complexity_after: str
) -> str:
    """
    Generate a rule-based explanation when the neural model is not available.
    
    Args:
        original_code: The original, unoptimized code
        optimized_code: The optimized version of the code
        applied_rules: List of applied optimization rules or techniques
        complexity_before: Time/space complexity of the original code
        complexity_after: Time/space complexity of the optimized code
        
    Returns:
        A human-readable explanation of the optimization
    """
    # Try to use the FLAN-T5 rule-based generator if available
    if FLANT5_AVAILABLE:
        try:
            # Create a new instance with offline mode enabled
            generator = FlanT5ExplanationGenerator(offline_mode=True)
            return generator.generate_rule_based_explanation(
                original_code,
                optimized_code,
                complexity_before,
                complexity_after,
                applied_rules
            )
        except Exception as e:
            logger.warning(f"Failed to use FLAN-T5 rule-based generator: {e}")
            import traceback
            logger.warning(traceback.format_exc())
            # Fall back to our simple rule-based generator
            
    # Create a basic explanation based on the applied rules
    explanation = "# Code Optimization Explanation\n\n"
    
    # Add optimization techniques section
    explanation += "## Optimization Techniques Applied\n\n"
    for rule in applied_rules:
        explanation += f"- {rule}\n"
    explanation += "\n"
    
    # Add complexity analysis
    explanation += "## Complexity Analysis\n\n"
    explanation += f"- Original code complexity: {complexity_before}\n"
    explanation += f"- Optimized code complexity: {complexity_after}\n"
    
    # Add code size comparison
    original_lines = len(original_code.split('\n'))
    optimized_lines = len(optimized_code.split('\n'))
    explanation += f"- Original code size: {original_lines} lines\n"
    explanation += f"- Optimized code size: {optimized_lines} lines\n\n"
    
    # Add general improvement notes
    explanation += "## Improvements\n\n"
    
    if complexity_before != complexity_after:
        explanation += "- **Algorithmic Improvement**: The time/space complexity has been improved, "
        explanation += "resulting in better performance for larger inputs.\n"
    
    if "loop" in " ".join(applied_rules).lower():
        explanation += "- **Loop Optimization**: The loops have been optimized for better efficiency.\n"
        
    if "dead code" in " ".join(applied_rules).lower() or "unused" in " ".join(applied_rules).lower():
        explanation += "- **Code Cleanup**: Unnecessary code has been removed, improving readability and maintenance.\n"
        
    if "algorithm" in " ".join(applied_rules).lower() or "pattern" in " ".join(applied_rules).lower():
        explanation += "- **Algorithm Selection**: A more efficient algorithm has been selected for the task.\n"
    
    return explanation
    
def batch_generate_explanations(
    code_pairs: List[Dict[str, Any]], 
    use_neural_model: bool = True,
    force_rule_based: bool = False,
    timeout: int = 60
) -> List[str]:
    """
    Generate explanations for multiple code pairs in batch.
    
    Args:
        code_pairs: List of dictionaries with code pairs and metadata
        use_neural_model: Whether to use neural model for explanations
        force_rule_based: Force using rule-based explanation even if model is available
        timeout: Timeout in seconds for model loading
        
    Returns:
        List of generated explanations
    """
    if use_neural_model and FLANT5_AVAILABLE and not force_rule_based:
        generator = get_generator(use_neural_model, timeout=timeout)
        if generator:
            try:
                # Use batch processing with the new force_rule_based parameter
                explanations = generator.batch_generate_explanations(
                    code_pairs, 
                    force_rule_based=force_rule_based
                )
                # Format each explanation
                return [generator.format_explanation(expl) for expl in explanations]
            except Exception as e:
                logger.error(f"Error in batch explanation generation: {e}")
                import traceback
                logger.error(traceback.format_exc())
    
    # Fallback to individual rule-based explanations
    explanations = []
    for pair in code_pairs:
        explanation = generate_rule_based_explanation(
            pair['original_code'],
            pair['optimized_code'],
            pair.get('applied_rules', []),
            pair.get('complexity_before', 'unknown'),
            pair.get('complexity_after', 'unknown')
        )
        explanations.append(explanation)
        
    return explanations

def train_explanation_model(
    training_data_path: str,
    output_model_path: Optional[str] = None,
    epochs: int = 3,
    timeout: int = 120
) -> bool:
    """
    Fine-tune the FLAN-T5 model on the provided training data.
    
    Args:
        training_data_path: Path to the training data CSV file
        output_model_path: Path to save the fine-tuned model
        epochs: Number of training epochs
        timeout: Timeout in seconds for model loading
        
    Returns:
        True if training was successful, False otherwise
    """
    if not FLANT5_AVAILABLE:
        logger.error("FLAN-T5 model not available for training")
        return False
        
    try:
        import pandas as pd
        
        # Load training data
        df = pd.read_csv(training_data_path)
        logger.info(f"Loaded {len(df)} training examples from {training_data_path}")
        
        # Initialize a fresh model for training
        model = FlanT5ExplanationGenerator()
        if not model.load_model(timeout=timeout):
            logger.error("Failed to load model for training")
            return False
        
        # Fine-tune the model
        result = model.fine_tune(
            training_data=df,
            output_dir=output_model_path,
            epochs=epochs
        )
        
        if "error" in result:
            logger.error(f"Training failed: {result['error']}")
            return False
            
        logger.info(f"Model fine-tuning completed and saved to {output_model_path}")
        logger.info(f"Training loss: {result.get('train_loss')}")
        return True
        
    except Exception as e:
        logger.error(f"Error training explanation model: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# Add a simple test function to verify the module can be imported and works properly
if __name__ == "__main__":
    print(f"FLAN-T5 model available: {FLANT5_AVAILABLE}")
    
    if FLANT5_AVAILABLE:
        # Test rule-based explanation (offline mode)
        test_generator = FlanT5ExplanationGenerator(offline_mode=True)
        
        test_explanation = test_generator.generate_rule_based_explanation(
            original_code="def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr",
            optimized_code="def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        swapped = False\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n                swapped = True\n        if not swapped:\n            break\n    return arr",
            complexity_before="O(n²)",
            complexity_after="O(n²) worst case, O(n) best case",
            applied_rules=["Early termination with swapped flag", "Loop optimization"]
        )
        
        print("\nTest rule-based explanation generated successfully!")
        print("\n--- Sample Explanation ---")
        print(test_explanation[:300] + "...\n")
    else:
        print("FLAN-T5 model is not available. Showing fallback explanation instead.")
        
        test_explanation = generate_rule_based_explanation(
            original_code="def test():\n    return 1",
            optimized_code="def test():\n    return 1",
            applied_rules=["No changes needed"],
            complexity_before="O(1)",
            complexity_after="O(1)"
        )
        
        print("\n--- Fallback Explanation ---")
        print(test_explanation)
