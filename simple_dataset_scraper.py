#!/usr/bin/env python3
"""
Simple Dataset Scraper for Competitive Programming Sites
Builds optimization dataset without external dependencies
"""

import json
import time
import re
from typing import Dict, List, Optional
import os

class SimpleDatasetBuilder:
    def __init__(self):
        self.optimization_examples = []
        
    def build_comprehensive_dataset(self) -> List[Dict]:
        """Build comprehensive optimization dataset"""
        print("🚀 Building comprehensive optimization dataset...")
        
        # LeetCode-style problems
        leetcode_examples = self.get_leetcode_examples()
        
        # GeeksforGeeks-style problems  
        gfg_examples = self.get_geeksforgeeks_examples()
        
        # HackerRank-style problems
        hackerrank_examples = self.get_hackerrank_examples()
        
        # Codeforces-style problems
        codeforces_examples = self.get_codeforces_examples()
        
        # Additional algorithmic patterns
        pattern_examples = self.get_algorithmic_patterns()
        
        all_examples = (leetcode_examples + gfg_examples + 
                       hackerrank_examples + codeforces_examples + 
                       pattern_examples)
        
        print(f"📊 Built dataset with {len(all_examples)} optimization examples")
        return all_examples
    
    def get_leetcode_examples(self) -> List[Dict]:
        """LeetCode optimization examples"""
        return [
            {
                "source": "LeetCode",
                "problem_id": 1,
                "title": "Two Sum",
                "difficulty": "Easy",
                "brute_force": '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []''',
                "optimized": '''def twoSum(nums, target):
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return []''',
                "technique": "hash_map",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Dictionary",
                "explanation": "Use hash map to store complements for O(1) lookup instead of nested loops"
            },
            {
                "source": "LeetCode", 
                "problem_id": 217,
                "title": "Contains Duplicate",
                "difficulty": "Easy",
                "brute_force": '''def containsDuplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False''',
                "optimized": '''def containsDuplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False''',
                "technique": "hash_set",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Set",
                "explanation": "Use set for O(1) membership testing instead of nested comparisons"
            },
            {
                "source": "LeetCode",
                "problem_id": 53,
                "title": "Maximum Subarray",
                "difficulty": "Easy", 
                "brute_force": '''def maxSubArray(nums):
    max_sum = float('-inf')
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            current_sum = sum(nums[i:j+1])
            max_sum = max(max_sum, current_sum)
    return max_sum''',
                "optimized": '''def maxSubArray(nums):
    max_sum = current_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum''',
                "technique": "dynamic_programming",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Kadane's Algorithm",
                "explanation": "Use Kadane's algorithm with optimal substructure instead of checking all subarrays"
            },
            {
                "source": "LeetCode",
                "problem_id": 15,
                "title": "3Sum",
                "difficulty": "Medium",
                "brute_force": '''def threeSum(nums):
    result = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            for k in range(j + 1, len(nums)):
                if nums[i] + nums[j] + nums[k] == 0:
                    triplet = sorted([nums[i], nums[j], nums[k]])
                    if triplet not in result:
                        result.append(triplet)
    return result''',
                "optimized": '''def threeSum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
    return result''',
                "technique": "two_pointers",
                "complexity_improvement": "O(n³) -> O(n²)",
                "data_structure": "Sorted Array + Two Pointers",
                "explanation": "Sort array and use two pointers to avoid third nested loop"
            },
            {
                "source": "LeetCode",
                "problem_id": 349,
                "title": "Intersection of Two Arrays",
                "difficulty": "Easy",
                "brute_force": '''def intersection(nums1, nums2):
    result = []
    for num1 in nums1:
        for num2 in nums2:
            if num1 == num2 and num1 not in result:
                result.append(num1)
    return result''',
                "optimized": '''def intersection(nums1, nums2):
    set1 = set(nums1)
    set2 = set(nums2)
    return list(set1 & set2)''',
                "technique": "set_intersection",
                "complexity_improvement": "O(n*m) -> O(n+m)",
                "data_structure": "Set Operations",
                "explanation": "Use set intersection operation instead of nested loops"
            }
        ]
    
    def get_geeksforgeeks_examples(self) -> List[Dict]:
        """GeeksforGeeks optimization examples"""
        return [
            {
                "source": "GeeksforGeeks",
                "title": "Count Pairs with Given Sum",
                "brute_force": '''def getPairsCount(arr, n, k):
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] + arr[j] == k:
                count += 1
    return count''',
                "optimized": '''def getPairsCount(arr, n, k):
    count = 0
    freq = {}
    for num in arr:
        complement = k - num
        if complement in freq:
            count += freq[complement]
        freq[num] = freq.get(num, 0) + 1
    return count''',
                "technique": "frequency_map",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Dictionary/Frequency Counter",
                "explanation": "Use frequency map to count pairs in single pass"
            },
            {
                "source": "GeeksforGeeks", 
                "title": "Find Missing Number",
                "brute_force": '''def getMissingNo(arr, n):
    for i in range(1, n + 2):
        found = False
        for j in range(n):
            if arr[j] == i:
                found = True
                break
        if not found:
            return i
    return -1''',
                "optimized": '''def getMissingNo(arr, n):
    total = (n + 1) * (n + 2) // 2
    sum_arr = sum(arr)
    return total - sum_arr''',
                "technique": "mathematical_formula",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Mathematical Approach",
                "explanation": "Use arithmetic series sum formula instead of nested search"
            },
            {
                "source": "GeeksforGeeks",
                "title": "Majority Element",
                "brute_force": '''def majorityElement(arr, n):
    for i in range(n):
        count = 0
        for j in range(n):
            if arr[j] == arr[i]:
                count += 1
        if count > n // 2:
            return arr[i]
    return -1''',
                "optimized": '''def majorityElement(arr, n):
    candidate = 0
    count = 0
    
    # Boyer-Moore Voting Algorithm
    for num in arr:
        if count == 0:
            candidate = num
        count += (1 if num == candidate else -1)
    
    return candidate''',
                "technique": "boyer_moore_voting",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Boyer-Moore Algorithm",
                "explanation": "Use Boyer-Moore voting algorithm for single pass majority detection"
            }
        ]
    
    def get_hackerrank_examples(self) -> List[Dict]:
        """HackerRank optimization examples"""
        return [
            {
                "source": "HackerRank",
                "title": "Sock Merchant",
                "brute_force": '''def sockMerchant(n, ar):
    pairs = 0
    counted = set()
    for i in range(n):
        if ar[i] not in counted:
            count = 0
            for j in range(n):
                if ar[i] == ar[j]:
                    count += 1
            pairs += count // 2
            counted.add(ar[i])
    return pairs''',
                "optimized": '''def sockMerchant(n, ar):
    sock_count = {}
    for sock in ar:
        sock_count[sock] = sock_count.get(sock, 0) + 1
    
    pairs = 0
    for count in sock_count.values():
        pairs += count // 2
    
    return pairs''',
                "technique": "frequency_counter",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Dictionary",
                "explanation": "Count frequencies once instead of nested counting for each unique element"
            },
            {
                "source": "HackerRank",
                "title": "Array Manipulation",
                "brute_force": '''def arrayManipulation(n, queries):
    arr = [0] * n
    for a, b, k in queries:
        for i in range(a-1, b):
            arr[i] += k
    return max(arr)''',
                "optimized": '''def arrayManipulation(n, queries):
    arr = [0] * (n + 1)
    for a, b, k in queries:
        arr[a-1] += k
        arr[b] -= k
    
    max_val = current = 0
    for val in arr:
        current += val
        max_val = max(max_val, current)
    
    return max_val''',
                "technique": "difference_array",
                "complexity_improvement": "O(n*m) -> O(n+m)",
                "data_structure": "Difference Array",
                "explanation": "Use difference array technique to avoid updating ranges repeatedly"
            }
        ]
    
    def get_codeforces_examples(self) -> List[Dict]:
        """Codeforces optimization examples"""
        return [
            {
                "source": "Codeforces",
                "title": "Beautiful Array",
                "brute_force": '''def solve(arr):
    beautiful_pairs = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] + arr[j] == 0:
                beautiful_pairs += 1
    return beautiful_pairs''',
                "optimized": '''def solve(arr):
    count = {}
    beautiful_pairs = 0
    
    for num in arr:
        complement = -num
        if complement in count:
            beautiful_pairs += count[complement]
        count[num] = count.get(num, 0) + 1
    
    return beautiful_pairs''',
                "technique": "hash_map",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Dictionary",
                "explanation": "Use hash map to find complement pairs in single pass"
            }
        ]
    
    def get_algorithmic_patterns(self) -> List[Dict]:
        """Additional algorithmic optimization patterns"""
        return [
            {
                "source": "Algorithmic Patterns",
                "title": "Sliding Window Maximum",
                "brute_force": '''def maxSlidingWindow(nums, k):
    result = []
    for i in range(len(nums) - k + 1):
        window_max = max(nums[i:i+k])
        result.append(window_max)
    return result''',
                "optimized": '''def maxSlidingWindow(nums, k):
    from collections import deque
    dq = deque()
    result = []
    
    for i, num in enumerate(nums):
        # Remove elements outside window
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # Remove smaller elements
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        
        dq.append(i)
        
        if i >= k - 1:
            result.append(nums[dq[0]])
    
    return result''',
                "technique": "sliding_window_deque",
                "complexity_improvement": "O(n*k) -> O(n)",
                "data_structure": "Deque (Double-ended Queue)",
                "explanation": "Use deque to maintain window maximum in O(1) amortized time"
            },
            {
                "source": "Algorithmic Patterns",
                "title": "Longest Substring Without Repeating Characters",
                "brute_force": '''def lengthOfLongestSubstring(s):
    max_len = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            substring = s[i:j+1]
            if len(set(substring)) == len(substring):
                max_len = max(max_len, len(substring))
            else:
                break
    return max_len''',
                "optimized": '''def lengthOfLongestSubstring(s):
    char_map = {}
    left = max_len = 0
    
    for right, char in enumerate(s):
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        char_map[char] = right
        max_len = max(max_len, right - left + 1)
    
    return max_len''',
                "technique": "sliding_window_hash",
                "complexity_improvement": "O(n³) -> O(n)",
                "data_structure": "Dictionary + Sliding Window",
                "explanation": "Use sliding window with hash map to track character positions"
            },
            {
                "source": "Algorithmic Patterns",
                "title": "Subarray Sum Equals K",
                "brute_force": '''def subarraySum(nums, k):
    count = 0
    for i in range(len(nums)):
        current_sum = 0
        for j in range(i, len(nums)):
            current_sum += nums[j]
            if current_sum == k:
                count += 1
    return count''',
                "optimized": '''def subarraySum(nums, k):
    count = 0
    prefix_sum = 0
    sum_count = {0: 1}
    
    for num in nums:
        prefix_sum += num
        if prefix_sum - k in sum_count:
            count += sum_count[prefix_sum - k]
        sum_count[prefix_sum] = sum_count.get(prefix_sum, 0) + 1
    
    return count''',
                "technique": "prefix_sum_hash",
                "complexity_improvement": "O(n²) -> O(n)",
                "data_structure": "Dictionary + Prefix Sum",
                "explanation": "Use prefix sum with hash map to find subarrays with target sum"
            }
        ]
    
    def validate_dataset(self, examples: List[Dict]) -> List[Dict]:
        """Validate dataset examples"""
        print("🔍 Validating dataset...")
        
        valid_examples = []
        for example in examples:
            try:
                # Check syntax of both codes
                compile(example['brute_force'], '<string>', 'exec')
                compile(example['optimized'], '<string>', 'exec')
                valid_examples.append(example)
            except SyntaxError as e:
                print(f"⚠️  Syntax error in {example['title']}: {e}")
        
        print(f"✅ Validated {len(valid_examples)}/{len(examples)} examples")
        return valid_examples
    
    def save_dataset(self, examples: List[Dict], filename: str = "comprehensive_optimization_dataset.json"):
        """Save dataset to JSON file"""
        dataset = {
            "metadata": {
                "total_examples": len(examples),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "sources": list(set(ex.get('source', 'Unknown') for ex in examples)),
                "techniques": list(set(ex.get('technique', 'Unknown') for ex in examples))
            },
            "examples": examples
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dataset saved to {filename}")
        return filename
    
    def generate_ml_training_data(self, examples: List[Dict]) -> Dict:
        """Generate training data for ML models"""
        print("🤖 Generating ML training data...")
        
        training_data = {
            "code_pairs": [],
            "techniques": [],
            "complexity_improvements": [],
            "data_structures": []
        }
        
        for example in examples:
            training_data["code_pairs"].append({
                "brute_force": example['brute_force'],
                "optimized": example['optimized'],
                "title": example['title']
            })
            training_data["techniques"].append(example['technique'])
            training_data["complexity_improvements"].append(example['complexity_improvement'])
            training_data["data_structures"].append(example['data_structure'])
        
        return training_data
    
    def analyze_dataset_statistics(self, examples: List[Dict]):
        """Analyze and display dataset statistics"""
        print("\n📊 DATASET STATISTICS")
        print("=" * 40)
        
        # Count by source
        sources = {}
        for ex in examples:
            source = ex.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print("Sources:")
        for source, count in sources.items():
            print(f"  {source}: {count} examples")
        
        # Count by technique
        techniques = {}
        for ex in examples:
            technique = ex.get('technique', 'Unknown')
            techniques[technique] = techniques.get(technique, 0) + 1
        
        print("\nOptimization Techniques:")
        for technique, count in techniques.items():
            print(f"  {technique}: {count} examples")
        
        # Count by complexity improvement
        improvements = {}
        for ex in examples:
            improvement = ex.get('complexity_improvement', 'Unknown')
            improvements[improvement] = improvements.get(improvement, 0) + 1
        
        print("\nComplexity Improvements:")
        for improvement, count in improvements.items():
            print(f"  {improvement}: {count} examples")

def main():
    """Main function to build comprehensive dataset"""
    builder = SimpleDatasetBuilder()
    
    print("🚀 Comprehensive Optimization Dataset Builder")
    print("=" * 50)
    
    # Build dataset
    examples = builder.build_comprehensive_dataset()
    
    # Validate examples
    valid_examples = builder.validate_dataset(examples)
    
    # Save dataset
    dataset_file = builder.save_dataset(valid_examples)
    
    # Generate ML training data
    training_data = builder.generate_ml_training_data(valid_examples)
    
    # Save training data
    with open('ml_training_dataset.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    # Display statistics
    builder.analyze_dataset_statistics(valid_examples)
    
    print(f"\n✅ DATASET CREATION COMPLETE!")
    print(f"📁 Main Dataset: {dataset_file}")
    print(f"🤖 ML Training Data: ml_training_dataset.json")
    print(f"📊 Total Examples: {len(valid_examples)}")
    
    # Show sample examples
    print(f"\n🔍 SAMPLE EXAMPLES:")
    print("-" * 30)
    for i, example in enumerate(valid_examples[:3]):
        print(f"{i+1}. {example['title']}")
        print(f"   Source: {example['source']}")
        print(f"   Technique: {example['technique']}")
        print(f"   Improvement: {example['complexity_improvement']}")
        print()

if __name__ == "__main__":
    main()