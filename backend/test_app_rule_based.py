"""
Test script to verify rule-based optimizer is working correctly through the app.py API.
This script sends HTTP requests to the /optimize endpoint with different test cases.

Requirements:
- requests package: pip install requests
"""

import requests
import logging
import json
import time
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = "http://localhost:5000/optimize"

# Test cases
TEST_CASES = {
    "fibonacci": {
        "name": "Fibonacci (Algorithm Detection)",
        "code": """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""
    },
    "bubble_sort": {
        "name": "Bubble Sort (Algorithm Detection)",
        "code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    },
    "dead_code": {
        "name": "Dead Code Elimination",
        "code": """
def test_dead_code():
    if True:
        x = 10
        return x
        print("This will never execute")  # Dead code after return
    else:
        print("This will never execute")  # Unreachable else branch
"""
    },
    "unused_vars": {
        "name": "Unused Variable Removal",
        "code": """
def test_unused_vars():
    x = 10  # Used variable
    y = 20  # Unused variable
    z = 30  # Unused variable
    return x
"""
    },
    "constant_folding": {
        "name": "Constant Folding",
        "code": """
def test_constant_folding():
    x = 2 * 3 + 4  # Should be folded to 10
    y = 10 / 2     # Should be folded to 5.0
    z = 2 ** 8     # Should be folded to 256
    return x + y + z
"""
    },
    "loop_optimization": {
        "name": "Loop Optimization",
        "code": """
def test_loop_optimization():
    items = ["a", "b", "c"]
    result = []
    for i in range(len(items)):
        result.append(items[i].upper())
    return result
"""
    },
    "repeated_computation": {
        "name": "Repeated Computation Elimination",
        "code": """
def expensive_operation(n):
    return n * n

def test_repeated_computation():
    x = 10
    y = 20
    # The expensive_operation(x+y) computation is repeated
    result1 = expensive_operation(x+y) * 2
    result2 = expensive_operation(x+y) * 3
    return result1 + result2
"""
    }
}

def test_optimization(test_name, code, level="high"):
    """Send a request to the API and check the response."""
    logger.info(f"Testing {test_name} optimization...")
    
    # Prepare request
    payload = {
        "code": code,
        "level": level,
        "debug": True,
        "mode": "rule"  # Force rule-based optimization only
    }
    
    try:
        # Send request
        response = requests.post(API_URL, json=payload)
        
        # Check response status
        if response.status_code != 200:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return False
        
        # Parse response
        result = response.json()
        
        # Log results
        logger.info(f"Original code length: {len(result['original_code'])}")
        logger.info(f"Optimized code length: {len(result['optimized_code'])}")
        logger.info(f"Improvements: {len(result['improvements'])}")
        logger.info(f"Errors: {len(result['errors'])}")
        logger.info(f"Status: {result['status']}")
        
        # Show optimized code
        logger.info("OPTIMIZED CODE:")
        logger.info("-" * 50)
        logger.info(result['optimized_code'])
        logger.info("-" * 50)
        
        # Print full improvements list
        logger.info("ALL IMPROVEMENTS:")
        logger.info("-" * 50)
        for imp in result['improvements']:
            logger.info(f"Type: {imp.get('type', 'unknown')}")
            logger.info(f"Description: {imp.get('description', 'No description')}")
            logger.info(f"Category: {imp.get('category', 'unknown')}")
            logger.info("-" * 30)
        
        # Print improvement details
        if result['improvements']:
            logger.info("Applied optimizations:")
            for imp in result['improvements']:
                imp_type = imp.get('type', 'unknown')
                description = imp.get('description', 'No description')
                if imp_type != 'optimization_pipeline':  # Skip the pipeline summary
                    logger.info(f"  - {imp_type}: {description}")
        
        # Check if there were any errors
        if result['errors']:
            logger.error(f"Optimization reported errors: {result['errors']}")
            return False
        
        # Consider it successful if optimized code is different or improvements were reported
        success = (result['original_code'] != result['optimized_code'] or 
                   len([imp for imp in result['improvements'] if imp.get('type') != 'optimization_pipeline']) > 0)
        
        if success:
            logger.info(f"Optimization successful for {test_name}")
        else:
            logger.warning(f"No optimizations applied for {test_name}")
        
        return success
    
    except Exception as e:
        logger.error(f"Error during API request: {str(e)}")
        return False

def main():
    """Run all test cases."""
    logger.info("Starting API test for rule-based optimizations")
    
    # Check if server is running
    try:
        requests.get("http://localhost:5000/health", timeout=2)
    except requests.exceptions.ConnectionError:
        logger.error("API server is not running. Please start the server first with 'python run_server.py'")
        return False
    
    # Run tests
    results = {}
    for test_id, test_data in TEST_CASES.items():
        results[test_id] = test_optimization(test_data["name"], test_data["code"])
        time.sleep(0.5)  # Small delay to avoid overwhelming the server
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS")
    logger.info("="*50)
    
    all_passed = True
    for test_id, passed in results.items():
        status = "✓" if passed else "✗"
        logger.info(f"{TEST_CASES[test_id]['name']:<30} {status}")
        all_passed = all_passed and passed
    
    logger.info("\nOverall result: " + ("SUCCESS" if all_passed else "FAILURE"))
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 