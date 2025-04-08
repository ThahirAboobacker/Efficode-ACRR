import os

def fix_indentation():
    with open('src/rule_based.py', 'r') as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'else:' in lines[i] and i + 1 < len(lines):
            if 'new_stmt' in lines[i + 1] and not lines[i + 1].strip().startswith('new_stmt'):
                # Fix indentation by adding 4 spaces
                lines[i + 1] = ' ' * 20 + lines[i + 1].lstrip()
    
    with open('src/rule_based.py', 'w') as f:
        f.writelines(lines)

if __name__ == '__main__':
    fix_indentation()
    print("Indentation fixed successfully") 