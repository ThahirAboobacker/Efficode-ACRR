import os
import sys
import pandas as pd
import logging
import time
from typing import List, Dict, Optional
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for importing modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Import your FlanT5ExplanationGenerator
try:
    from flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
    logger.info("Successfully imported FlanT5ExplanationGenerator from current directory")
except ImportError:
    try:
        from models.flan_t5 import FlanT5ExplanationGenerator, get_explanation_generator
        logger.info("Successfully imported FlanT5ExplanationGenerator from models package")
    except ImportError as e:
        logger.error(f"Error importing FlanT5ExplanationGenerator: {e}")
        logger.error("Make sure flan_t5.py is in the correct location")
        sys.exit(1)

def prepare_finetune_dataset(df):
    """
    Prepare a dataset for fine-tuning FLAN-T5 on code explanations.
    
    Args:
        df: DataFrame with algorithm dataset
        
    Returns:
        DataFrame with columns for fine-tuning: 'prompt', 'explanation'
    """
    # Log the DataFrame columns for debugging
    logger.info(f"DataFrame columns: {df.columns.tolist()}")
    
    # Create pairs of unoptimized and optimized code
    pairs = []
    
    # Group by algorithm_name to find matching pairs
    algorithms = df['algorithm_name'].unique()
    logger.info(f"Found {len(algorithms)} unique algorithms")
    
    # First, check what values are in code_type and is_optimized columns
    logger.info(f"Unique values in code_type column: {df['code_type'].unique()}")
    logger.info(f"Unique values in is_optimized column: {df['is_optimized'].unique()}")
    
    for algo in algorithms:
        algo_df = df[df['algorithm_name'] == algo]
        logger.info(f"Algorithm '{algo}': Total entries: {len(algo_df)}")
        
        # UPDATED APPROACH: Primarily use is_optimized column
        try:
            # This dataset uses 0/1 values for is_optimized
            unopt = algo_df[algo_df['is_optimized'] == 0]
            opt = algo_df[algo_df['is_optimized'] == 1]
            logger.info(f"Strategy: Using is_optimized as 0/1: Found {len(unopt)} unoptimized and {len(opt)} optimized versions")
            
            # Skip if we couldn't find both versions
            if len(unopt) == 0 or len(opt) == 0:
                logger.warning(f"Could not find both optimized and unoptimized versions for algorithm '{algo}' - skipping")
                continue
                
            # Success! Now create pairs
            logger.info(f"Creating pairs for algorithm '{algo}' with {len(unopt)} unoptimized and {len(opt)} optimized versions")
            
            # Create pairs (taking the first instance if multiple exist)
            for _, unopt_row in unopt.iterrows():
                for _, opt_row in opt.iterrows():
                    try:
                        # Extract the relevant fields for the prompt
                        prompt = (
                            f"Explain the optimization from the original code to the optimized code, "
                            f"including complexity changes from {unopt_row['time_complexity']} to {opt_row['time_complexity']}:\n\n"
                            f"Original Code:\n```python\n{unopt_row['code']}\n```\n\n"
                            f"Optimized Code:\n```python\n{opt_row['code']}\n```"
                        )
                        
                        # Combine explanations for a more comprehensive training example
                        explanation = (
                            f"# Optimization of {algo}\n\n"
                            f"## Complexity Analysis\n"
                            f"- Original: {unopt_row['time_complexity']} time, {unopt_row.get('space_complexity', 'Unknown')} space\n"
                            f"- Optimized: {opt_row['time_complexity']} time, {opt_row.get('space_complexity', 'Unknown')} space\n\n"
                            f"## Optimization Techniques\n{opt_row.get('explanation', 'No explanation provided')}\n\n"
                        )
                        
                        # Add implementation details if available
                        implementation_details = []
                        if 'loop_count' in unopt_row and 'loop_nesting_depth' in unopt_row:
                            implementation_details.append(
                                f"The original implementation has {unopt_row['loop_count']} loops with nesting depth of {unopt_row['loop_nesting_depth']}."
                            )
                        
                        if 'recursion_used' in unopt_row and 'recursion_used' in opt_row:
                            if unopt_row['recursion_used'] and not opt_row['recursion_used']:
                                implementation_details.append("The optimization removes recursion in favor of an iterative approach.")
                            elif not unopt_row['recursion_used'] and opt_row['recursion_used']:
                                implementation_details.append("The optimization introduces recursion for a cleaner solution.")
                        
                        if 'data_structures' in opt_row:
                            implementation_details.append(f"The key data structures used in the optimized version are {opt_row['data_structures']}.")
                        
                        if implementation_details:
                            explanation += "## Implementation Details\n" + " ".join(implementation_details)
                        
                        pairs.append({
                            'original_code': unopt_row['code'],
                            'optimized_code': opt_row['code'],
                            'complexity_before': unopt_row['time_complexity'],
                            'complexity_after': opt_row['time_complexity'],
                            'prompt': prompt,
                            'explanation': explanation
                        })
                        
                        # Only create one pair per algorithm to avoid explosion of pairs
                        break
                    except Exception as e:
                        logger.error(f"Error creating pair for algorithm '{algo}': {e}")
                        continue
                # Only use the first unoptimized version
                break
        except Exception as e:
            logger.error(f"Error processing algorithm '{algo}': {e}")
            continue
    
    if len(pairs) == 0:
        logger.warning("No valid code pairs found in dataset. Using predefined examples as fallback.")
        return prepare_predefined_dataset()
    
    logger.info(f"Created {len(pairs)} code optimization pairs")
    return pd.DataFrame(pairs)

def prepare_predefined_dataset():
    """
    Creates a predefined dataset with clear examples instead of loading from CSV.
    This avoids any CSV parsing or external data issues.
    
    Returns:
        DataFrame with columns for fine-tuning: 'prompt', 'explanation'
    """
    # Define sample code pairs
    sample_pairs = [
        {
            "algorithm_name": "Bubble Sort",
            "original_code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr""",
            "optimized_code": """
def optimized_bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr""",
            "complexity_before": "O(n²)",
            "complexity_after": "O(n²) worst case, O(n) best case",
            "explanation": "The optimized bubble sort algorithm adds an early termination check using a 'swapped' flag. If no swaps occur during a pass, the array is already sorted and the algorithm exits early, improving best-case time complexity to O(n)."
        },
        {
            "algorithm_name": "Linear Search to Binary Search",
            "original_code": """
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1""",
            "optimized_code": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1""",
            "complexity_before": "O(n)",
            "complexity_after": "O(log n)",
            "explanation": "The optimization replaces linear search with binary search, which has O(log n) time complexity compared to O(n) for linear search. Binary search works by repeatedly dividing the search space in half, which is much more efficient for large sorted arrays."
        },
        {
            "algorithm_name": "Fibonacci with Memoization",
            "original_code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
            "optimized_code": """
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]""",
            "complexity_before": "O(2^n)",
            "complexity_after": "O(n)",
            "explanation": "The optimization uses memoization to store previously computed Fibonacci numbers, avoiding redundant calculations. This reduces the time complexity from exponential O(2^n) to linear O(n), making it much more efficient for larger values of n."
        }
    ]
    
    # Create prompts and explanations for training
    training_data = []
    for pair in sample_pairs:
        prompt = (
            f"Explain the optimization from the original code to the optimized code, "
            f"including complexity changes from {pair['complexity_before']} to {pair['complexity_after']}:\n\n"
            f"Original Code:\n```python\n{pair['original_code']}\n```\n\n"
            f"Optimized Code:\n```python\n{pair['optimized_code']}\n```"
        )
        
        explanation = (
            f"# Optimization of {pair['algorithm_name']}\n\n"
            f"## Complexity Analysis\n"
            f"- Original: {pair['complexity_before']}\n"
            f"- Optimized: {pair['complexity_after']}\n\n"
            f"## Explanation\n"
            f"{pair['explanation']}\n\n"
        )
        
        training_data.append({
            'original_code': pair['original_code'],
            'optimized_code': pair['optimized_code'],
            'complexity_before': pair['complexity_before'],
            'complexity_after': pair['complexity_after'],
            'prompt': prompt,
            'explanation': explanation
        })
    
    # Create and return DataFrame
    return pd.DataFrame(training_data)

def main():
    """Main function to run the fine-tuning process"""
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Fine-tune FLAN-T5 for code optimization explanations')
    parser.add_argument('--data_path', type=str, default='backend/data/processed/processed_dataset.csv', 
                        help='Path to the dataset CSV file (defaults to backend/data/processed/processed_dataset.csv)')
    parser.add_argument('--output_dir', type=str, default='./flan_t5_fine_tuned', help='Directory to save the fine-tuned model')
    parser.add_argument('--epochs', type=int, default=3, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=2, help='Batch size for training')
    parser.add_argument('--learning_rate', type=float, default=3e-5, help='Learning rate for training')
    parser.add_argument('--model_name', type=str, default='google/flan-t5-base', help='Base model to fine-tune')
    parser.add_argument('--cache_dir', type=str, default=None, help='Directory to cache the model')
    parser.add_argument('--test_after', action='store_true', help='Test the model after fine-tuning')
    parser.add_argument('--use_predefined_data', action='store_true', help='Use predefined examples instead of loading from CSV')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Log GPU availability
    logger.info(f"PyTorch version: {torch.__version__}")
    if torch.cuda.is_available():
        logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        logger.info("No GPU available, using CPU")
    
    # Prepare fine-tuning dataset
    logger.info("Preparing fine-tuning dataset")
    try:
        # Check if we should use predefined data
        use_predefined = args.use_predefined_data
        
        # If not explicitly using predefined data, try multiple paths for the dataset
        if not use_predefined:
            # Try different potential dataset paths
            dataset_paths = [
                args.data_path,  # Try the specified path first
                os.path.join(os.path.dirname(current_dir), 'data', 'processed', 'processed_dataset.csv'),  # Try from backend directory
                os.path.join(os.getcwd(), args.data_path),  # Try from current working directory
                '../data/processed/processed_dataset.csv',  # Try relative path from models directory
                '../../backend/data/processed/processed_dataset.csv',  # Try if we're in a subdirectory
            ]
            
            # Try each path until we find the dataset
            dataset_found = False
            for path in dataset_paths:
                if os.path.exists(path):
                    logger.info(f"Found dataset at: {path}")
                    df = pd.read_csv(path)
                    logger.info(f"Dataset loaded with {len(df)} records")
                    dataset_found = True
                    break
            
            # If dataset not found, fall back to predefined data
            if not dataset_found:
                logger.warning(f"Could not find dataset at any of these locations: {dataset_paths}")
                logger.warning("Falling back to predefined dataset")
                use_predefined = True
        
        # Either use predefined data or load from CSV
        if use_predefined:
            logger.info("Using predefined dataset")
            ft_df = prepare_predefined_dataset()
        else:
            # Prepare dataset from loaded dataframe
            ft_df = prepare_finetune_dataset(df)
            
        logger.info(f"Created {len(ft_df)} training examples")
        
        # Save the prepared dataset for reference
        prepared_path = os.path.join(args.output_dir, "prepared_dataset.csv")
        ft_df.to_csv(prepared_path, index=False)
        logger.info(f"Saved prepared dataset to {prepared_path}")
    except Exception as e:
        logger.error(f"Error preparing dataset: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Even if there was an error, try with predefined data as a last resort
        logger.info("Attempting to use predefined dataset as fallback...")
        try:
            ft_df = prepare_predefined_dataset()
            logger.info(f"Created {len(ft_df)} predefined training examples")
            
            # Save the prepared dataset for reference
            prepared_path = os.path.join(args.output_dir, "prepared_dataset.csv")
            ft_df.to_csv(prepared_path, index=False)
            logger.info(f"Saved prepared dataset to {prepared_path}")
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            return
    
    # Split into train/validation sets
    from sklearn.model_selection import train_test_split
    train_df, val_df = train_test_split(ft_df, test_size=0.1, random_state=42)
    
    logger.info(f"Training on {len(train_df)} examples, validating on {len(val_df)} examples")
    
    # Initialize the explanation generator
    logger.info(f"Initializing FLAN-T5 explanation generator with {args.model_name}")
    explainer = FlanT5ExplanationGenerator(
        model_name=args.model_name,
        cache_dir=args.cache_dir
    )
    
    # Load the base model
    logger.info("Loading base model")
    if not explainer.load_model():
        logger.error("Failed to load model, cannot fine-tune")
        return
    
    # Fine-tune the model
    logger.info("Starting fine-tuning process")
    try:
        start_time = time.time()
        results = explainer.fine_tune(
            training_data=train_df,
            output_dir=args.output_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            eval_data=val_df,
            learning_rate=args.learning_rate
        )
        training_time = time.time() - start_time
        
        logger.info(f"Fine-tuning complete in {training_time:.2f} seconds")
        logger.info(f"Results: {results}")
    except Exception as e:
        logger.error(f"Error during fine-tuning: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # Test the fine-tuned model if requested
    if args.test_after:
        logger.info("Testing fine-tuned model")
        try:
            # Load fine-tuned model
            tuned_explainer = get_explanation_generator(model_path=args.output_dir)
            
            # Test on a few examples
            test_examples = val_df.sample(min(3, len(val_df)))
            
            for i, test_row in test_examples.iterrows():
                logger.info(f"Testing example {i+1}/{len(test_examples)}")
                explanation = tuned_explainer.generate_explanation(
                    original_code=test_row['original_code'],
                    optimized_code=test_row['optimized_code'],
                    complexity_before=test_row['complexity_before'],
                    complexity_after=test_row['complexity_after']
                )
                
                logger.info("Generated explanation:")
                logger.info("-" * 80)
                logger.info(explanation)
                logger.info("-" * 80)
                
        except Exception as e:
            logger.error(f"Error testing fine-tuned model: {e}")

if __name__ == "__main__":
    main()