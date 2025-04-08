"""
Simple script to test the API endpoint and debug response data in detail.
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = "http://localhost:5000/optimize"

# Test case
TEST_CODE = """
def test_constant_folding():
    x = 2 * 3 + 4  # Should be folded to 10
    y = 10 / 2     # Should be folded to 5.0
    z = 2 ** 8     # Should be folded to 256
    return x + y + z
"""

def main():
    """Send a test request to the API and debug the response."""
    # Prepare request
    payload = {
        "code": TEST_CODE,
        "level": "high",
        "debug": True,
        "mode": "rule"  # Force rule-based optimization only
    }
    
    try:
        # Send request
        logger.info(f"Sending request to {API_URL}")
        response = requests.post(API_URL, json=payload)
        
        # Check response status
        logger.info(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"API request failed: {response.text}")
            return False
        
        # Parse response
        result = response.json()
        
        # Print full response for debugging
        logger.info("Full response data:")
        logger.info("-" * 50)
        logger.info(json.dumps(result, indent=2))
        logger.info("-" * 50)
        
        # Check improvements specifically
        improvements = result.get('improvements', [])
        logger.info(f"Number of improvements: {len(improvements)}")
        if improvements:
            for i, imp in enumerate(improvements):
                logger.info(f"Improvement {i+1}:")
                for key, value in imp.items():
                    logger.info(f"  {key}: {value}")
        else:
            logger.info("No improvements reported in the response")
        
        # Consider successful if the API responded correctly
        return True
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    print(f"TEST RESULT: {'SUCCESS' if success else 'FAILURE'}") 