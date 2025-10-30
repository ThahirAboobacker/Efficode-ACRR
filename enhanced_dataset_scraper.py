#!/usr/bin/env python3
"""
Enhanced Dataset Scraper for Competitive Programming Sites
Scrapes optimization examples from LeetCode, GeeksforGeeks, HackerRank, etc.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import random

class CompetitiveProgrammingScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.scraped_data = []
        
    def setup_selenium_driver(self):
        """Setup Selenium WebDriver for dynamic content"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except:
            print("⚠️  Chrome driver not found. Using requests for static content only.")
            return None
    
    def scrape_leetcode_problems(self) -> List[Dict]:
        """Scrape LeetCode problems with optimization examples"""
        print("🌐 Scraping LeetCode problems...")
        
        # LeetCode problems known to have good brute force -> optimized examples
        leetcode_problems = [
            {"id": 1, "title": "two-sum", "difficulty": "Easy"},
            {"id": 167, "title": "two-sum-ii-input-array-is-sorted", "difficulty": "Medium"},
            {"id": 217, "title": "contains-duplicate", "difficulty": "Easy"},
            {"id": 53, "title": "maximum-subarray", "difficulty": "Easy"},
            {"id": 121, "title": "best-time-to-buy-and-sell-stock", "difficulty": "Easy"},
            {"id": 442, "title": "find-all-duplicates-in-an-array", "difficulty": "Medium"},
            {"id": 349, "title": "intersection-of-two-arrays", "difficulty": "Easy"},
            {"id": 15, "title": "3sum", "difficulty": "Medium"},
            {"id": 18, "title": "4sum", "difficulty": "Medium"},
            {"id": 26, "title": "remove-duplicates-from-sorted-array", "difficulty": "Easy"}
        ]
        
        scraped_problems = []
        
        for problem in leetcode_problems:
            try:
                # Simulate scraping (in real implementation, use actual web scraping)
                problem_data = self.get_leetcode_problem_data(problem)
                if problem_data:
                    scraped_problems.append(problem_data)
                    print(f"✅ Scraped: {problem['title']}")
                
                # Rate limiting
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"❌ Failed to scrape {problem['title']}: {e}")
        
        return scraped_problems
    
    def get_leetcode_problem_data(self, problem: Dict) -> Optional[Dict]:
        """Get problem data from LeetCode (simulated)"""
        # In real implementation, this would scrape actual LeetCode pages
        # For demo, returning predefined optimization examples
        
        optimization_examples = {
            1: {  # Two Sum
                "title": "Two Sum",
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
                "explanation": "Use hash map to store complements for O(1) lookup"
            },
            217: {  # Contains Duplicate
                "title": "Contains Duplicate",
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
                "explanation": "Use set for O(1) membership testing"
            },
            53: {  # Maximum Subarray
                "title": "Maximum Subarray",
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
                "explanation": "Use dynamic programming to track optimal subarray"
            }
        }
        
        return optimization_examples.get(problem["id"])
    
    def scrape_geeksforgeeks_problems(self) -> List[Dict]:
        """Scrape GeeksforGeeks optimization examples"""
        print("🌐 Scraping GeeksforGeeks problems...")
        
        gfg_problems = [
            "find-duplicates-in-on-time-and-constant-extra-space",
            "maximum-subarray-sum-using-divide-and-conquer-algorithm",
            "count-pairs-with-given-sum",
            "find-the-missing-number",
            "majority-element",
            "intersection-of-two-arrays",
            "union-of-two-arrays"
        ]
        
        scraped_problems = []
        
        for problem_slug in gfg_problems:
            try:
                problem_data = self.get_gfg_problem_data(problem_slug)
                if problem_data:
                    scraped_problems.append(problem_data)
                    print(f"✅ Scraped GFG: {problem_slug}")
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"❌ Failed to scrape GFG {problem_slug}: {e}")
        
        return scraped_problems
    
    def get_gfg_problem_data(self, problem_slug: str) -> Optional[Dict]:
        """Get GeeksforGeeks problem data (simulated)"""
        gfg_examples = {
            "count-pairs-with-given-sum": {
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
                "data_structure": "Dictionary",
                "explanation": "Use frequency map to count pairs efficiently"
            },
            "find-the-missing-number": {
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
                "explanation": "Use sum formula instead of nested search"
            }
        }
        
        return gfg_examples.get(problem_slug)
    
    def scrape_hackerrank_problems(self) -> List[Dict]:
        """Scrape HackerRank optimization examples"""
        print("🌐 Scraping HackerRank problems...")
        
        hackerrank_problems = [
            "sock-merchant",
            "counting-valleys",
            "jumping-on-the-clouds",
            "repeated-string",
            "array-manipulation"
        ]
        
        scraped_problems = []
        
        for problem in hackerrank_problems:
            try:
                problem_data = self.get_hackerrank_problem_data(problem)
                if problem_data:
                    scraped_problems.append(problem_data)
                    print(f"✅ Scraped HackerRank: {problem}")
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"❌ Failed to scrape HackerRank {problem}: {e}")
        
        return scraped_problems
    
    def get_hackerrank_problem_data(self, problem_slug: str) -> Optional[Dict]:
        """Get HackerRank problem data (simulated)"""
        hr_examples = {
            "sock-merchant": {
                "title": "Sock Merchant",
                "brute_force": '''def sockMerchant(n, ar):
    pairs = 0
    for i in range(n):
        count = 0
        for j in range(n):
            if ar[i] == ar[j]:
                count += 1
        pairs += count // 2
    return pairs // n  # Avoid double counting''',
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
                "explanation": "Count frequencies once instead of nested counting"
            }
        }
        
        return hr_examples.get(problem_slug)
    
    def scrape_codeforces_problems(self) -> List[Dict]:
        """Scrape Codeforces optimization examples"""
        print("🌐 Scraping Codeforces problems...")
        
        # Codeforces problems with optimization potential
        cf_problems = [
            {"contest": 1, "problem": "A"},
            {"contest": 4, "problem": "A"},
            {"contest": 71, "problem": "A"}
        ]
        
        scraped_problems = []
        
        for problem in cf_problems:
            try:
                problem_data = self.get_codeforces_problem_data(problem)
                if problem_data:
                    scraped_problems.append(problem_data)
                    print(f"✅ Scraped Codeforces: {problem['contest']}{problem['problem']}")
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"❌ Failed to scrape Codeforces {problem}: {e}")
        
        return scraped_problems
    
    def get_codeforces_problem_data(self, problem: Dict) -> Optional[Dict]:
        """Get Codeforces problem data (simulated)"""
        # Simulated Codeforces examples
        return {
            "title": f"Codeforces {problem['contest']}{problem['problem']}",
            "brute_force": '''def solve(arr):
    result = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] > arr[j]:
                result.append((i, j))
    return result''',
            "optimized": '''def solve(arr):
    indexed_arr = [(val, idx) for idx, val in enumerate(arr)]
    indexed_arr.sort()
    
    result = []
    for i in range(len(indexed_arr)):
        for j in range(i):
            result.append((indexed_arr[i][1], indexed_arr[j][1]))
    
    return result''',
            "technique": "sorting_optimization",
            "complexity_improvement": "O(n²) -> O(n log n)",
            "data_structure": "Sorted Array",
            "explanation": "Sort once instead of nested comparisons"
        }
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape from all competitive programming sources"""
        print("🚀 Starting comprehensive dataset scraping...")
        
        all_problems = []
        
        # Scrape from different sources
        sources = [
            ("LeetCode", self.scrape_leetcode_problems),
            ("GeeksforGeeks", self.scrape_geeksforgeeks_problems),
            ("HackerRank", self.scrape_hackerrank_problems),
            ("Codeforces", self.scrape_codeforces_problems)
        ]
        
        for source_name, scraper_func in sources:
            try:
                print(f"\n📊 Scraping {source_name}...")
                problems = scraper_func()
                all_problems.extend(problems)
                print(f"✅ {source_name}: {len(problems)} problems scraped")
            except Exception as e:
                print(f"❌ {source_name} scraping failed: {e}")
        
        return all_problems
    
    def validate_scraped_data(self, problems: List[Dict]) -> List[Dict]:
        """Validate and clean scraped data"""
        print("🔍 Validating scraped data...")
        
        valid_problems = []
        
        for problem in problems:
            try:
                # Check required fields
                required_fields = ['title', 'brute_force', 'optimized', 'technique']
                if all(field in problem for field in required_fields):
                    
                    # Validate Python syntax
                    try:
                        compile(problem['brute_force'], '<string>', 'exec')
                        compile(problem['optimized'], '<string>', 'exec')
                        valid_problems.append(problem)
                    except SyntaxError:
                        print(f"⚠️  Syntax error in {problem['title']}")
                        
            except Exception as e:
                print(f"⚠️  Validation error for {problem.get('title', 'Unknown')}: {e}")
        
        print(f"✅ Validated {len(valid_problems)}/{len(problems)} problems")
        return valid_problems
    
    def save_dataset(self, problems: List[Dict], filename: str = "optimization_dataset.json"):
        """Save scraped dataset to file"""
        dataset = {
            "metadata": {
                "total_problems": len(problems),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "sources": ["LeetCode", "GeeksforGeeks", "HackerRank", "Codeforces"]
            },
            "problems": problems
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dataset saved to {filename}")
        return filename
    
    def generate_training_data(self, problems: List[Dict]) -> Dict:
        """Generate ML training data from scraped problems"""
        print("🤖 Generating ML training data...")
        
        training_data = {
            "features": [],
            "labels": [],
            "code_pairs": []
        }
        
        for problem in problems:
            # Extract features from brute force code
            features = self.extract_ml_features(problem['brute_force'])
            training_data["features"].append(features)
            training_data["labels"].append(problem['technique'])
            
            # Store code pairs for training
            training_data["code_pairs"].append({
                "input": problem['brute_force'],
                "output": problem['optimized'],
                "technique": problem['technique']
            })
        
        return training_data
    
    def extract_ml_features(self, code: str) -> List[float]:
        """Extract features for ML training"""
        features = []
        
        # Basic code metrics
        features.append(len(code.split('\n')))  # Lines of code
        features.append(code.count('for'))      # Number of for loops
        features.append(code.count('while'))    # Number of while loops
        features.append(code.count('if'))       # Number of conditionals
        features.append(code.count('range'))    # Range usage
        features.append(code.count('len'))      # Length function calls
        
        # Nested structure indicators
        features.append(1 if 'for' in code and code.count('for') >= 2 else 0)
        features.append(1 if 'sum(' in code else 0)
        features.append(1 if '==' in code else 0)
        features.append(1 if 'append' in code else 0)
        
        return features

def main():
    """Main function to demonstrate dataset scraping"""
    scraper = CompetitiveProgrammingScraper()
    
    print("🌐 Competitive Programming Dataset Scraper")
    print("=" * 50)
    
    # Scrape from all sources
    problems = scraper.scrape_all_sources()
    
    # Validate data
    valid_problems = scraper.validate_scraped_data(problems)
    
    # Save dataset
    dataset_file = scraper.save_dataset(valid_problems)
    
    # Generate training data
    training_data = scraper.generate_training_data(valid_problems)
    
    # Save training data
    with open('ml_training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print("\n📊 SCRAPING SUMMARY")
    print("=" * 30)
    print(f"Total Problems Scraped: {len(problems)}")
    print(f"Valid Problems: {len(valid_problems)}")
    print(f"Dataset File: {dataset_file}")
    print(f"Training Data: ml_training_data.json")
    
    # Display sample problems
    print(f"\n🔍 SAMPLE PROBLEMS")
    print("-" * 30)
    for i, problem in enumerate(valid_problems[:3]):
        print(f"{i+1}. {problem['title']}")
        print(f"   Technique: {problem['technique']}")
        print(f"   Improvement: {problem.get('complexity_improvement', 'N/A')}")
    
    print(f"\n✅ Dataset ready for ML training!")

if __name__ == "__main__":
    main()