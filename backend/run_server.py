#!/usr/bin/env python
"""
Server launcher script for EFFICODE-ACRR
This script makes it easier to run the server from any directory.
"""

import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run the EFFICODE-ACRR server')
    parser.add_argument('--dev', action='store_true', 
                        help='Run the development server instead of the production server')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0', 
                        help='Host to run the server on (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    # Get the backend directory path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the backend directory
    os.chdir(backend_dir)
    print(f"Changed directory to: {backend_dir}")
    
    # Add environment variables
    os.environ['PORT'] = str(args.port)
    os.environ['HOST'] = args.host
    
    if args.dev:
        print("Starting development server...")
        os.environ['DEBUG'] = 'True'
        # Import and run the development server
        sys.path.insert(0, os.path.join(backend_dir, 'src'))
        try:
            from development_server import app, serve
            print(f"Running development server on http://{args.host}:{args.port}")
            serve(app, host=args.host, port=args.port)
        except ImportError as e:
            print(f"Error importing development server: {e}")
            print("Falling back to production server...")
            os.system(f"python app.py")
    else:
        print("Starting production server...")
        os.environ['DEBUG'] = 'False'
        # Run the production server
        os.system(f"python app.py")

if __name__ == "__main__":
    main() 