#!/usr/bin/env python
"""
Simple script to start the frontend development server
"""

import os
import sys
import subprocess
import platform

def main():
    """Start the frontend development server"""
    print("Starting frontend development server...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the frontend directory
    if not os.path.exists(current_dir):
        print(f"Error: frontend directory not found at {current_dir}")
        sys.exit(1)
    
    # Run the npm command
    try:
        print(f"Starting frontend from {current_dir}...")
        os.chdir(current_dir)
        
        # Check platform for correct command
        if platform.system() == 'Windows':
            # Windows - use start cmd to run in new window
            subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', 'npm', 'run', 'dev'])
        else:
            # Unix - use nohup to run in background
            subprocess.Popen(['npm', 'run', 'dev'], 
                           stdout=open(os.devnull, 'w'),
                           stderr=subprocess.STDOUT)
        
        print("Frontend started successfully.")
        print("UI available at http://localhost:3000")
        
    except Exception as e:
        print(f"Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 