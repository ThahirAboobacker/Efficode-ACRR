"""
Script to check flan_t5.py for syntax errors and fix them
"""

import os
import ast

# Path to the file
file_path = 'models/flan_t5.py'

try:
    # Try to parse the file with ast to check for syntax errors
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to parse with ast
    try:
        ast.parse(content)
        print("No syntax errors detected with ast parser")
    except SyntaxError as e:
        print(f"Syntax error detected: {e}")
        
        # Find the line with the error
        lines = content.split('\n')
        error_line = e.lineno - 1  # 0-indexed
        
        print(f"Error at line {e.lineno}, column {e.offset}")
        print(f"Error line content: {lines[error_line]}")
        
        # Check for common syntax errors
        if e.msg == "unterminated f-string literal":
            print("Found unterminated f-string. Will try to fix...")
            
            # Fix specific unterminated f-string issue
            if "Optimized Code:" in lines[error_line] and lines[error_line].endswith('\\'):
                lines[error_line] = lines[error_line].replace('\\', '') + '"'
                
                # Write fixed content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print("File fixed successfully")
        
except Exception as e:
    print(f"Error: {e}") 