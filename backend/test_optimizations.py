import requests
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API endpoint
API_URL = "http://localhost:5000/optimize"

# Test cases to verify different optimization types
TEST_CASES = [
    {
        "name": "Fibonacci - Recursive to Dynamic Programming",
        "code": """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Test the function
result = fibonacci(10)
print(f"Fibonacci of 10 is {result}")
        """,
        "expected_optimization": "dynamic programming"
    },
    {
        "name": "Bubble Sort - Replace with sorted()",
        "code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Test the function
test_array = [64, 34, 25, 12, 22, 11, 90]
sorted_array = bubble_sort(test_array)
print(f"Sorted array: {sorted_array}")
        """,
        "expected_optimization": "sorted"
    },
    {
        "name": "String Concatenation - Replace with join",
        "code": """
def concatenate_strings(items):
    result = ""
    for item in items:
        result += str(item)
    return result

# Test the function
items_list = ["apple", "banana", "cherry", "date"]
concatenated = concatenate_strings(items_list)
print(f"Concatenated string: {concatenated}")
        """,
        "expected_optimization": "join"
    },
    {
        "name": "Unused Variables - Remove",
        "code": """
def process_data(data):
    result = []
    temp_var = "unused variable"
    
    for item in data:
        processed = item * 2
        result.append(processed)
    
    return result

# Test the function
data = [1, 2, 3, 4, 5]
processed_data = process_data(data)
print(f"Processed data: {processed_data}")
        """,
        "expected_optimization": "removed unused variables"
    },
    {
        "name": "Dead Code - Remove if False",
        "code": """
def calculate_value(x):
    result = x * 2
    
    if False:
        result = 0
        print("This will never execute")
    
    return result

# Test the function
value = calculate_value(10)
print(f"Calculated value: {value}")
        """,
        "expected_optimization": "removed unreachable"
    },
    {
        "name": "Redundant Arithmetic - Simplify",
        "code": """
def calculate(x, y):
    a = x + 0
    b = y * 1
    c = y - 0
    d = x / 1
    e = 0 + x
    f = 1 * y
    g = y * 0
    h = 0 * x
    return a + b + c + d + e + f + g + h

# Test the function
result = calculate(5, 10)
print(f"Result: {result}")
        """,
        "expected_optimization": "simplified arithmetic"
    },
    {
        "name": "Redundant Type Casting - Remove",
        "code": """
def convert_values(x, y):
    a = int(int(x))
    b = float(float(y))
    c = str(str(x))
    d = int(float(int(y)))
    e = float(int(float(x)))
    return a, b, c, d, e

# Test the function
results = convert_values(10, 20.5)
print(f"Converted values: {results}")
        """,
        "expected_optimization": "removed redundant type casting"
    },
    {
        "name": "Nested If Statements - Combine",
        "code": """
def check_conditions(x, y):
    if x > 0:
        if y > 0:
            return True
    return False

# Test the function
result = check_conditions(5, 10)
print(f"Conditions met: {result}")
        """,
        "expected_optimization": "combined nested if"
    },
    {
        "name": "List Building - Use Comprehension",
        "code": """
def double_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result

# Test the function
numbers = [1, 2, 3, 4, 5]
doubled = double_items(numbers)
print(f"Doubled items: {doubled}")
        """,
        "expected_optimization": "list comprehension"
    }
]

def test_optimization(test_case):
    """Test a single optimization case"""
    name = test_case["name"]
    code = test_case["code"]
    expected = test_case["expected_optimization"]
    
    logger.info(f"Testing: {name}")
    
    try:
        # Make API request
        start_time = time.time()
        response = requests.post(
            API_URL,
            json={"code": code}
        )
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return False
        
        # Parse response
        result = response.json()
        optimized_code = result.get("optimizedCode", "")
        explanation = result.get("explanation", "")
        original_complexity = result.get("originalComplexity", "")
        optimized_complexity = result.get("optimizedComplexity", "")
        
        # Check if optimization was applied
        optimization_applied = expected.lower() in optimized_code.lower() or expected.lower() in explanation.lower()
        
        # Log results
        logger.info(f"Response time: {elapsed:.2f}s")
        logger.info(f"Original complexity: {original_complexity}")
        logger.info(f"Optimized complexity: {optimized_complexity}")
        logger.info(f"Explanation: {explanation}")
        
        if optimization_applied:
            logger.info(f"✓ PASS: {name} - Expected optimization found")
            return True
        else:
            logger.warning(f"✗ FAIL: {name} - Expected optimization not found")
            logger.warning(f"Expected: {expected}")
            logger.warning(f"Optimized code: {optimized_code[:200]}...")
            return False
    
    except Exception as e:
        logger.error(f"Error testing {name}: {str(e)}")
        return False

def run_tests():
    """Run all optimization tests"""
    logger.info("Starting optimization tests")
    
    results = []
    for test_case in TEST_CASES:
        result = test_optimization(test_case)
        results.append(result)
        
        # Add a small delay between tests
        time.sleep(0.5)
    
    # Print summary
    passed = sum(1 for r in results if r)
    total = len(results)
    logger.info(f"Test summary: {passed}/{total} tests passed")
    
    # Print detailed results
    for i, test_case in enumerate(TEST_CASES):
        status = "✓ PASS" if results[i] else "✗ FAIL"
        logger.info(f"{status}: {test_case['name']}")
        
    return passed, total

if __name__ == "__main__":
    run_tests() 