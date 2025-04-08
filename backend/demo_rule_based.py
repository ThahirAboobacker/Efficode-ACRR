"""
Demo script for rule-based optimizations.

This script demonstrates different optimization techniques applied by the rule-based optimizer.
Just run this script to see the optimizations in action.
"""

import sys
import os
import logging
from src.rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_optimization_results(code, level="medium"):
    """Print the optimization results for the given code."""
    optimizer = RuleBasedOptimizer()
    optimized_code, original_complexity, optimized_complexity, explanation = optimizer.optimize(code, level=level)
    
    print("\n" + "="*80)
    print(f"OPTIMIZATION LEVEL: {level.upper()}")
    print("="*80)
    
    print("\nORIGINAL CODE:")
    print("-"*80)
    print(code)
    print("-"*80)
    
    print("\nOPTIMIZED CODE:")
    print("-"*80)
    print(optimized_code)
    print("-"*80)
    
    print(f"\nCOMPLEXITY: {original_complexity} -> {optimized_complexity}")
    print(f"EXPLANATION: {explanation}")
    
    print("\nAPPLIED RULES:")
    for rule in optimizer.get_applied_rules():
        rule_type = rule.get('type', 'unknown')
        description = rule.get('description', '')
        print(f"  - {rule_type}: {description}")
    
    print("\n")

def main():
    """Run the demo with different optimization examples."""
    # Example 1: Constant Folding
    print_optimization_results("""
def calculate_area(width, height):
    # Calculate the perimeter
    perimeter = 2 * (width + height)
    
    # Calculate the area using constants
    area = width * height
    
    # Calculate the diagonal using the Pythagorean theorem
    diagonal = (width**2 + height**2)**0.5
    
    # Calculate an arbitrary value with constant expressions
    magic_number = 10 * 5 + 3 - 2 * 4
    
    return {
        "area": area,
        "perimeter": perimeter,
        "diagonal": diagonal,
        "magic_number": magic_number
    }
    """, level="high")
    
    # Example 2: Dead Code Elimination
    print_optimization_results("""
def process_order(order_type, amount):
    # Set default tax rate
    tax_rate = 0.1
    
    # Apply tax based on order type
    if order_type == "food":
        tax_rate = 0.05
    elif True:
        # This is always executed
        tax_rate = 0.08
    else:
        # This never executes
        tax_rate = 0.12
    
    # Check for large orders
    if amount > 1000:
        discount = 0.1
    else:
        discount = 0
        
    # Calculate final amounts
    tax = amount * tax_rate
    discount_amount = amount * discount
    final_amount = amount + tax - discount_amount
    
    return final_amount
    """, level="high")
    
    # Example 3: Loop Unrolling
    print_optimization_results("""
def initialize_grid():
    # Create a small 3x3 grid
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    # Initialize the grid with some values
    for i in range(3):
        for j in range(3):
            grid[i][j] = i + j
            
    # Add row sums to the end of each row
    row_sums = []
    for i in range(3):
        row_sum = 0
        for j in range(3):
            row_sum += grid[i][j]
        row_sums.append(row_sum)
        
    return grid, row_sums
    """, level="high")
    
    # Example 4: Unused Variable Removal
    print_optimization_results("""
def process_data(data):
    # Extract data
    name = data.get('name')
    age = data.get('age')
    address = data.get('address')  # Unused
    phone = data.get('phone')  # Unused
    
    # Temporary placeholders
    temp1 = 0  # Unused
    temp2 = ""  # Unused
    
    # Process the data
    greeting = f"Hello, {name}!"
    is_adult = age >= 18
    
    # Prepare result
    result = {
        "greeting": greeting,
        "is_adult": is_adult
    }
    
    return result
    """, level="high")

    # Example 5: Combined Optimizations
    print_optimization_results("""
def analyze_numbers(numbers):
    # Unused variables
    count = len(numbers)
    max_possible = 100
    min_possible = 0
    
    # Constants that can be folded
    threshold = 10 + 5
    scale_factor = 2 * 3
    
    # Dead code branches
    if True:
        use_advanced = True
    else:
        use_advanced = False
    
    # Simple loops that can be unrolled
    sum_first_few = 0
    for i in range(3):
        if i < len(numbers):
            sum_first_few += numbers[i]
    
    # More calculations
    result = {
        "threshold": threshold,
        "scale_factor": scale_factor,
        "use_advanced": use_advanced,
        "sum_first_few": sum_first_few
    }
    
    return result
    """, level="high")

if __name__ == "__main__":
    main() 