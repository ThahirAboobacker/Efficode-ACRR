import sys
import logging
from src.codebert_optimizer import apply_codebert_optimization

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Sample code with optimizable patterns
test_code = '''
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
        
def build_list(items):
    results = []
    for item in items:
        results.append(item * 2)
    return results
'''

def main():
    print("Testing CodeBERT optimization without AST transformations...")
    print("\nOriginal code:")
    print(test_code)
    
    try:
        # Patch the CodeBERT optimizer to use only rule-based approach
        import src.codebert_optimizer
        # Temporarily force neural model to be unavailable 
        src.codebert_optimizer.NEURAL_MODEL_AVAILABLE = False
        
        # Apply optimization
        optimized_code, improvements, errors = apply_codebert_optimization(test_code, level='medium')
        
        print("\nOptimized code:")
        print(optimized_code)
        
        print("\nImprovements:")
        for improvement in improvements:
            print(f"- {improvement.get('type', 'unknown')}: {improvement.get('description', '')}")
        
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"- {error}")
        
        print("\nTest completed successfully!")
        return 0
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 