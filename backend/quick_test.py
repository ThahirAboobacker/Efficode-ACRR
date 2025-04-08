import logging
from src.codebert_optimizer import apply_codebert_optimization

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Sample code with Fibonacci recursive implementation
test_code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""

print("Original code:")
print(test_code)

# Apply optimization
optimized_code, improvements, errors = apply_codebert_optimization(test_code, level="medium")

print("\nOptimized code:")
print(optimized_code)

print("\nImprovements:")
for improvement in improvements:
    print(f"- {improvement.get('type', 'unknown')}: {improvement.get('description', '')}")

if errors:
    print("\nErrors:")
    for error in errors:
        print(f"- {error}")
else:
    print("\nNo errors encountered.")

print("\nTest completed successfully!") 