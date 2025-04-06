#!/usr/bin/env python
"""
Script to start both the backend server and frontend development server
"""

import os
import sys
import subprocess
import time
import platform

def main():
    """Start both backend and frontend servers"""
    print("Starting Efficode-ACRR application...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # First start the backend server
    backend_dir = os.path.join(current_dir, 'backend')
    src_dir = os.path.join(backend_dir, 'src')
    
    if not os.path.exists(src_dir):
        print(f"Error: backend src directory not found at {src_dir}")
        sys.exit(1)
    
    try:
        print("Starting backend server...")
        os.chdir(src_dir)
        
        # Start the backend server
        if platform.system() == 'Windows':
            # Windows
            subprocess.Popen(['python', 'app.py'])
        else:
            # Unix
            subprocess.Popen(['python', 'app.py'], 
                           stdout=open(os.devnull, 'w'),
                           stderr=subprocess.STDOUT)
        
        print("Backend server started successfully.")
        print("API available at http://localhost:5500/api/optimize")
        
        # Wait a moment for the backend to initialize
        time.sleep(2)
        
        # Now start the frontend
        frontend_dir = os.path.join(current_dir, 'frontend')
        if not os.path.exists(frontend_dir):
            print(f"Error: frontend directory not found at {frontend_dir}")
            sys.exit(1)
        
        print("Starting frontend development server...")
        os.chdir(frontend_dir)
        
        # Start the frontend
        if platform.system() == 'Windows':
            # Windows - use start cmd to run in new window
            subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', 'npm', 'run', 'dev'])
        else:
            # Unix
            subprocess.Popen(['npm', 'run', 'dev'], 
                           stdout=open(os.devnull, 'w'),
                           stderr=subprocess.STDOUT)
        
        print("Frontend started successfully.")
        print("UI available at http://localhost:3000")
        
        print("\nBoth servers are now running!")
        print("You can access the application at http://localhost:3000")
        
    except Exception as e:
        print(f"Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 