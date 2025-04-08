import ast
import sys

def check_syntax(file_path):
    print(f"Checking for syntax errors in {file_path}...")
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        print(f"No syntax errors found in {file_path}")
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path}:")
        print(f"Line {e.lineno}, column {e.offset}: {e.text}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    files_to_check = [
        "src/rule_based.py",
        "src/codebert_optimizer.py"
    ]
    
    success = True
    for file_path in files_to_check:
        if not check_syntax(file_path):
            success = False
    
    sys.exit(0 if success else 1) 