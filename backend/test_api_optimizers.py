#!/usr/bin/env python
"""
Test script to verify rule-based and CodeBERT optimizers through the Flask API
"""

import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API configuration
API_URL = "http://localhost:5000"
OPTIMIZE_ENDPOINT = f"{API_URL}/optimize"

# Test cases for different optimization patterns
TEST_CASES = [
    {
        "name": "Rule-Based: Fibonacci Optimization",
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
        "mode": "rule",
        "level": "high",
        "expected_patterns": ["dynamic programming", "memoization", "cache"]
    },
    {
        "name": "CodeBERT: Complex Algorithm Optimization",
        "code": """
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates

# Test the function
test_array = [1, 2, 3, 2, 4, 3, 5, 1]
result = find_duplicates(test_array)
print(f"Duplicates found: {result}")
        """,
        "mode": "codebert",
        "level": "high",
        "expected_patterns": ["set", "hash", "O(n)"]
    },
    {
        "name": "Auto Mode: String Processing",
        "code": """
def process_strings(strings):
    result = ""
    for s in strings:
        s = s.strip().lower()
        if s:
            result = result + s + ","
    return result[:-1] if result else ""

# Test the function
test_strings = ["  Hello  ", "World  ", "  Python  "]
result = process_strings(test_strings)
print(f"Processed strings: {result}")
        """,
        "mode": "auto",
        "level": "high",
        "expected_patterns": ["join", "list comprehension", "strip"]
    }
]

def test_health_endpoint() -> bool:
    """Test if the API is running and optimizers are available."""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            logger.error(f"Health check failed with status code: {response.status_code}")
            return False
        
        data = response.json()
        if data.get('status') != 'ok':
            logger.error("Health check indicates service is not OK")
            return False
        
        optimizers = data.get('optimizers', {})
        if not optimizers.get('rule_based') or not optimizers.get('codebert'):
            logger.error("One or more optimizers are not available")
            return False
        
        logger.info("Health check passed - all optimizers are available")
        return True
    except Exception as e:
        logger.error(f"Error checking API health: {e}")
        return False

def test_optimization(test_case: Dict[str, Any]) -> bool:
    """Test a single optimization case."""
    name = test_case["name"]
    code = test_case["code"]
    mode = test_case["mode"]
    level = test_case["level"]
    expected_patterns = test_case["expected_patterns"]
    
    logger.info(f"\nTesting: {name}")
    logger.info(f"Mode: {mode}, Level: {level}")
    
    try:
        # Make API request
        response = requests.post(
            OPTIMIZE_ENDPOINT,
            json={
                "code": code,
                "mode": mode,
                "level": level,
                "debug": True
            }
        )
        
        if response.status_code != 200:
            logger.error(f"API request failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
        
        # Parse response
        result = response.json()
        optimized_code = result.get("optimized_code", "").lower()
        explanation = result.get("explanation", "").lower()
        improvements = result.get("improvements", [])
        
        # Check if optimization was successful
        if not optimized_code:
            logger.error("No optimized code returned")
            return False
        
        # Check if expected patterns are present
        patterns_found = []
        for pattern in expected_patterns:
            if pattern.lower() in optimized_code or pattern.lower() in explanation:
                patterns_found.append(pattern)
        
        success = len(patterns_found) > 0
        
        # Log results
        logger.info("\nOptimization Results:")
        logger.info(f"Patterns found: {', '.join(patterns_found)}")
        logger.info(f"Number of improvements: {len(improvements)}")
        if result.get("error"):
            logger.warning(f"Optimization warnings/errors: {result['error']}")
        
        if success:
            logger.info(f"✓ PASS: {name}")
        else:
            logger.error(f"✗ FAIL: {name} - Expected patterns not found")
            logger.error(f"Expected one of: {', '.join(expected_patterns)}")
        
        return success
    
    except Exception as e:
        logger.error(f"Error testing {name}: {str(e)}")
        return False

def main():
    """Main entry point."""
    logger.info("Starting API optimizer tests")
    
    # First check if the API is running
    if not test_health_endpoint():
        logger.error("Health check failed - make sure the Flask API is running")
        sys.exit(1)
    
    # Run all test cases
    results = []
    for test_case in TEST_CASES:
        success = test_optimization(test_case)
        results.append(success)
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r)
    logger.info(f"\nTest Summary: {passed}/{total} tests passed")
    
    # Exit with appropriate status code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main() 