"""
Test script for feature extraction module
"""

from feature_extraction import FeatureExtractor

def test_feature_extraction():
    # Test code sample
    test_code = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
'''
    
    # Initialize feature extractor
    extractor = FeatureExtractor()
    
    # Extract features
    features = extractor.extract_code_features(test_code)
    
    # Print results
    print("\nExtracted Features:")
    for feature, value in features.items():
        print(f"{feature}: {value}")

if __name__ == "__main__":
    test_feature_extraction() 