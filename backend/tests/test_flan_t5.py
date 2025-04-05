import pytest
from models.flan_t5 import FlanT5ExplanationGenerator

@pytest.fixture
def explanation_generator():
    """Create an explanation generator in offline mode for testing"""
    return FlanT5ExplanationGenerator(offline_mode=True)

def test_rule_based_explanation(explanation_generator):
    """Test rule-based explanation generation"""
    original_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
    """

    optimized_code = """
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
    """
    
    explanation = explanation_generator.generate_explanation(
        original_code=original_code,
        optimized_code=optimized_code,
        complexity_before="O(n²)",
        complexity_after="O(n log n)",
        applied_rules=["Replaced bubble sort with quick sort"],
        force_rule_based=True
    )
    
    assert explanation is not None
    assert len(explanation) > 0
    assert "bubble sort" in explanation.lower() or "quicksort" in explanation.lower()
    assert "complexity" in explanation.lower()

def test_complexity_explanation(explanation_generator):
    """Test complexity explanation generation"""
    explanation = explanation_generator._explain_complexity_change(
        complexity_before="O(n²)", 
        complexity_after="O(n log n)"
    )
    
    assert explanation is not None
    assert len(explanation) > 0
    assert "quadratic" in explanation.lower()
    assert "linearithmic" in explanation.lower()

def test_error_handling(explanation_generator):
    """Test error handling in explanation generation"""
    # Pass invalid or None values
    explanation = explanation_generator.generate_explanation(
        original_code="",
        optimized_code="def test(): pass",
        complexity_before="",
        complexity_after="O(1)",
        applied_rules=None,
        force_rule_based=True
    )
    
    assert explanation is not None
    assert len(explanation) > 0 