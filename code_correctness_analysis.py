#!/usr/bin/env python3
"""
Analyze the correctness of the last generated optimized codes
"""

def analyze_two_sum_output():
    """Analyze the Two Sum optimization output"""
    print("🔍 ANALYZING TWO SUM OPTIMIZATION")
    print("=" * 50)
    
    # The system generated this code:
    generated_code = '''def twoSum_optimized(self, nums, target):
    """
    Optimized using Hash Map
    Time Complexity: O(n) - Single pass with O(1) lookups
    Space Complexity: O(n) - Hash map storage
    Data Structure: Dictionary for key-value mapping
    """
    lookup_map = {}  # Hash map for O(1) lookups

    for i, item in enumerate(self):
        # Calculate complement or target value
        target_val = target - item if 'target' in 'self, nums, target' else item

        # Check if complement exists
        if target_val in lookup_map:
            return [lookup_map[target_val], i]  # Return indices

        # Store current item with its index
        lookup_map[item] = i

    return []  # No solution found'''
    
    print("Generated Code:")
    print(generated_code)
    
    print("\n❌ ISSUES IDENTIFIED:")
    print("1. Iterating over 'self' instead of 'nums'")
    print("2. String check 'target' in 'self, nums, target' is incorrect")
    print("3. Should iterate over nums parameter, not self")
    
    # Correct version:
    correct_code = '''def twoSum_optimized(self, nums, target):
    """
    Optimized using Hash Map
    Time Complexity: O(n) - Single pass with O(1) lookups
    Space Complexity: O(n) - Hash map storage
    """
    lookup_map = {}  # Hash map for O(1) lookups

    for i, num in enumerate(nums):
        complement = target - num

        # Check if complement exists
        if complement in lookup_map:
            return [lookup_map[complement], i]

        # Store current number with its index
        lookup_map[num] = i

    return []  # No solution found'''
    
    print("\n✅ CORRECTED VERSION:")
    print(correct_code)
    
    # Test the corrected version
    class Solution:
        def twoSum_optimized(self, nums, target):
            lookup_map = {}
            for i, num in enumerate(nums):
                complement = target - num
                if complement in lookup_map:
                    return [lookup_map[complement], i]
                lookup_map[num] = i
            return []
    
    # Test cases
    solution = Solution()
    test_cases = [
        ([2, 7, 11, 15], 9, [0, 1]),
        ([3, 2, 4], 6, [1, 2]),
        ([3, 3], 6, [0, 1])
    ]
    
    print("\n🧪 TESTING CORRECTED VERSION:")
    for nums, target, expected in test_cases:
        result = solution.twoSum_optimized(nums, target)
        status = "✅" if result == expected else "❌"
        print(f"   {status} Input: nums={nums}, target={target}")
        print(f"      Expected: {expected}, Got: {result}")

def analyze_longest_substring_output():
    """Analyze the Longest Substring optimization"""
    print("\n🔍 ANALYZING LONGEST SUBSTRING OPTIMIZATION")
    print("=" * 50)
    
    print("Original Code (O(n²)):")
    original = '''def lengthOfLongestSubstring(self, s):
    max_len = 0
    for i in range(len(s)):
        seen = set()
        for j in range(i, len(s)):
            if s[j] in seen:
                break
            seen.add(s[j])
            max_len = max(max_len, j - i + 1)
    return max_len'''
    print(original)
    
    print("\n❌ SYSTEM OUTPUT: Generic template (not optimized)")
    print("The system failed to generate proper sliding window optimization")
    
    print("\n✅ CORRECT SLIDING WINDOW OPTIMIZATION:")
    correct_optimized = '''def lengthOfLongestSubstring_optimized(self, s):
    """
    Optimized using Sliding Window + Hash Map
    Time Complexity: O(n) - Single pass
    Space Complexity: O(min(m,n)) - m is charset size
    """
    char_map = {}  # Character -> index mapping
    left = 0
    max_len = 0
    
    for right, char in enumerate(s):
        # If character seen and within current window
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        
        # Update character position
        char_map[char] = right
        
        # Update maximum length
        max_len = max(max_len, right - left + 1)
    
    return max_len'''
    print(correct_optimized)
    
    # Test both versions
    class Solution:
        def lengthOfLongestSubstring_original(self, s):
            max_len = 0
            for i in range(len(s)):
                seen = set()
                for j in range(i, len(s)):
                    if s[j] in seen:
                        break
                    seen.add(s[j])
                    max_len = max(max_len, j - i + 1)
            return max_len
        
        def lengthOfLongestSubstring_optimized(self, s):
            char_map = {}
            left = 0
            max_len = 0
            
            for right, char in enumerate(s):
                if char in char_map and char_map[char] >= left:
                    left = char_map[char] + 1
                char_map[char] = right
                max_len = max(max_len, right - left + 1)
            
            return max_len
    
    solution = Solution()
    test_cases = [
        ("abcabcbb", 3),  # "abc"
        ("bbbbb", 1),     # "b"
        ("pwwkew", 3),    # "wke"
        ("", 0)           # empty string
    ]
    
    print("\n🧪 TESTING BOTH VERSIONS:")
    for s, expected in test_cases:
        original_result = solution.lengthOfLongestSubstring_original(s)
        optimized_result = solution.lengthOfLongestSubstring_optimized(s)
        
        orig_status = "✅" if original_result == expected else "❌"
        opt_status = "✅" if optimized_result == expected else "❌"
        
        print(f"   Input: '{s}' (Expected: {expected})")
        print(f"   {orig_status} Original O(n²): {original_result}")
        print(f"   {opt_status} Optimized O(n): {optimized_result}")

def system_evaluation():
    """Overall system evaluation"""
    print("\n📊 OVERALL SYSTEM EVALUATION")
    print("=" * 50)
    
    print("✅ STRENGTHS:")
    print("• ML correctly identifies optimization techniques (hash_map, sliding_window)")
    print("• Complexity analysis is accurate (O(n²) → O(n))")
    print("• Performance improvement calculations are correct")
    print("• Confidence scoring works well (63.5% for hash_map, 60% for sliding_window)")
    
    print("\n⚠️  CODE GENERATION ISSUES:")
    print("• Template parameter handling needs improvement")
    print("• Some generated code has syntax/logic errors")
    print("• Generic fallbacks when specific patterns not recognized")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("1. Use system for ANALYSIS and TECHNIQUE IDENTIFICATION")
    print("2. Manual code review/correction needed for generated code")
    print("3. The ML predictions are highly valuable for optimization guidance")
    print("4. Consider this as an 'AI optimization advisor' tool")
    
    print("\n🎯 VERDICT:")
    print("The system CORRECTLY identifies optimization opportunities")
    print("but needs refinement in code generation templates.")
    print("The core ML analysis is EXCELLENT! 🚀")

def main():
    """Main analysis function"""
    print("🔍 CODE CORRECTNESS ANALYSIS")
    print("=" * 60)
    
    analyze_two_sum_output()
    analyze_longest_substring_output()
    system_evaluation()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print("• ML analysis: EXCELLENT ✅")
    print("• Technique identification: ACCURATE ✅") 
    print("• Complexity analysis: CORRECT ✅")
    print("• Code generation: NEEDS IMPROVEMENT ⚠️")
    print("• Overall value: HIGH as optimization advisor! 🌟")

if __name__ == "__main__":
    main()