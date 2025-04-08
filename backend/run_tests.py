#!/usr/bin/env python
"""
EFFICODE-ACRR Test Runner

This script runs the comprehensive tests for the EFFICODE-ACRR backend,
including tests for the rule-based optimizer, CodeBERT optimizer, and Flask API.
"""

import os
import sys
import subprocess
import time
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_flask_server():
    """Start the Flask server in a separate process"""
    logger.info("Starting Flask server...")
    
    # Get the path to the app.py file
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(backend_dir, 'app.py')
    
    # Start the Flask server in a separate process
    server_process = subprocess.Popen(
        [sys.executable, app_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    # Check if the server is running
    if server_process.poll() is not None:
        logger.error("Failed to start Flask server")
        stdout, stderr = server_process.communicate()
        logger.error(f"Server stdout: {stdout}")
        logger.error(f"Server stderr: {stderr}")
        return None
    
    logger.info("Flask server started successfully")
    return server_process

def run_tests(test_type=None):
    """Run the tests for the specified components"""
    logger.info(f"Running tests for: {test_type if test_type else 'all components'}")
    
    # Get the path to the test script
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(backend_dir, 'tests')
    test_script = os.path.join(tests_dir, 'test_optimizers.py')
    
    # Start the Flask server if testing the API
    server_process = None
    if test_type is None or test_type == 'api':
        server_process = start_flask_server()
        if server_process is None:
            logger.error("Cannot run API tests without a running server")
            return False
    
    try:
        # Run the tests
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=True,
            text=True
        )
        
        # Print the test output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Check if the tests were successful
        success = result.returncode == 0
        
        if success:
            logger.info("All tests passed successfully")
        else:
            logger.error("Some tests failed")
        
        return success
    
    finally:
        # Stop the Flask server if it was started
        if server_process:
            logger.info("Stopping Flask server...")
            server_process.terminate()
            server_process.wait()
            logger.info("Flask server stopped")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run EFFICODE-ACRR tests')
    parser.add_argument(
        '--component',
        choices=['rule-based', 'codebert', 'api', 'all'],
        default='all',
        help='Component to test (default: all)'
    )
    
    args = parser.parse_args()
    
    # Map component names to test types
    component_map = {
        'rule-based': 'rule_based',
        'codebert': 'codebert',
        'api': 'api',
        'all': None
    }
    
    test_type = component_map[args.component]
    
    # Run the tests
    success = run_tests(test_type)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 