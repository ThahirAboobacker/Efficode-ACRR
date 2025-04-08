"""
Test script to directly test the optimize_code function in app.py without using HTTP requests.
"""

import logging
import json
import sys
import os
from flask import Flask, request, jsonify
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request
import flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath('.'))

# Import app with optimize_code function
import app
from app import optimize_code

# Test case
TEST_CODE = """
def test_constant_folding():
    x = 2 * 3 + 4  # Should be folded to 10
    y = 10 / 2     # Should be folded to 5.0
    z = 2 ** 8     # Should be folded to 256
    return x + y + z
"""

def create_test_request(code, level="high"):
    """Create a test request object."""
    # Create payload
    payload = {
        "code": code,
        "level": level,
        "debug": True,
        "mode": "rule"
    }
    
    # Create test environment
    builder = EnvironBuilder(
        method='POST',
        json=payload
    )
    env = builder.get_environ()
    req = Request(env)
    
    # Create Flask request context
    return req

def test_optimize_direct():
    """Test the optimize_code function directly."""
    logger.info("Testing optimize_code function directly")
    
    # Create test app
    test_app = Flask(__name__)
    
    # Create test request
    req = create_test_request(TEST_CODE)
    
    # Use the test app context to call the function
    with test_app.test_request_context():
        # Set request object
        flask.request = req
        
        # Call optimize_code function
        response = app.optimize_code()
        
        # Parse response
        result = json.loads(response.data)
        
        # Log results
        logger.info(f"Original code length: {len(result['original_code'])}")
        logger.info(f"Optimized code length: {len(result['optimized_code'])}")
        logger.info(f"Improvements: {len(result['improvements'])}")
        logger.info(f"Errors: {len(result['errors'])}")
        logger.info(f"Status: {result['status']}")
        
        # Print optimized code
        logger.info("OPTIMIZED CODE:")
        logger.info("-" * 50)
        logger.info(result['optimized_code'])
        logger.info("-" * 50)
        
        # Print improvements
        logger.info("IMPROVEMENTS:")
        logger.info("-" * 50)
        for imp in result['improvements']:
            logger.info(f"Type: {imp.get('type', 'unknown')}")
            logger.info(f"Description: {imp.get('description', 'No description')}")
            logger.info(f"Category: {imp.get('category', 'unknown')}")
            logger.info("-" * 30)
        
        # Consider it successful if optimized code is different or improvements were reported
        success = (result['original_code'] != result['optimized_code'])
        
        return success

def main():
    """Run the test."""
    try:
        success = test_optimize_direct()
        print(f"TEST RESULT: {'SUCCESS' if success else 'FAILURE'}")
        return success
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 