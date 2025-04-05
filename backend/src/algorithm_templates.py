"""
Algorithm Templates for EFFICODE-ACRR

This module provides template implementations of various algorithms in their optimized forms:
- Sorting algorithms (quick sort, merge sort, etc.)
- Search algorithms (binary search, etc.)
- Graph algorithms (DFS, BFS, etc.)
- Dynamic programming algorithms

These templates are used by the code transformation module to replace inefficient
algorithm implementations with more efficient alternatives.
"""

# SORTING ALGORITHMS
SORTING_ALGORITHMS = {
    # Quick Sort - O(n log n) average time complexity
    'quick_sort': """
def quick_sort(arr):
    \"\"\"
    Quick sort implementation with O(n log n) average time complexity.
    \"\"\"
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
""",
    
    # Merge Sort - O(n log n) time complexity
    'merge_sort': """
def merge_sort(arr):
    \"\"\"
    Merge sort implementation with O(n log n) time complexity.
    \"\"\"
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result
""",
    
    # Heap Sort - O(n log n) time complexity
    'heap_sort': """
def heap_sort(arr):
    \"\"\"
    Heap sort implementation with O(n log n) time complexity.
    \"\"\"
    def heapify(arr, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)
    
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)
    
    return arr
""",
    
    # Tim Sort - Python's built-in sort, O(n log n)
    'tim_sort': """
def tim_sort(arr):
    \"\"\"
    Tim sort implementation (Python's built-in sort) with O(n log n) time complexity.
    \"\"\"
    # Create a copy to avoid modifying the original
    sorted_arr = sorted(arr)
    return sorted_arr
"""
}

# SEARCH ALGORITHMS
SEARCH_ALGORITHMS = {
    # Binary Search - O(log n) time complexity
    'binary_search': """
def binary_search(arr, target):
    \"\"\"
    Binary search implementation with O(log n) time complexity.
    Requires a sorted array.
    \"\"\"
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Target not found
""",
    
    # Jump Search - O(√n) time complexity
    'jump_search': """
def jump_search(arr, target):
    \"\"\"
    Jump search implementation with O(√n) time complexity.
    Requires a sorted array.
    \"\"\"
    import math
    n = len(arr)
    step = int(math.sqrt(n))
    prev = 0
    
    # Finding the block where the target may be present
    while arr[min(step, n) - 1] < target:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return -1
    
    # Linear search in the identified block
    while arr[prev] < target:
        prev += 1
        if prev == min(step, n):
            return -1
    
    if arr[prev] == target:
        return prev
    
    return -1  # Target not found
""",
    
    # Interpolation Search - O(log log n) average time complexity
    'interpolation_search': """
def interpolation_search(arr, target):
    \"\"\"
    Interpolation search implementation with O(log log n) average time complexity.
    Requires a sorted array with uniformly distributed values.
    \"\"\"
    low, high = 0, len(arr) - 1
    
    while low <= high and arr[low] <= target <= arr[high]:
        if low == high:
            if arr[low] == target:
                return low
            return -1
        
        # Calculate position with interpolation formula
        pos = low + ((target - arr[low]) * (high - low)) // (arr[high] - arr[low])
        
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    
    return -1  # Target not found
"""
}

# GRAPH ALGORITHMS
GRAPH_ALGORITHMS = {
    # Breadth-First Search (BFS) - O(V + E) time complexity
    'bfs': """
def bfs(graph, start):
    \"\"\"
    Breadth-First Search implementation with O(V + E) time complexity.
    
    Args:
        graph: Graph represented as an adjacency list (dictionary)
        start: Starting vertex
    
    Returns:
        List of vertices in BFS order
    \"\"\"
    from collections import deque
    
    visited = set()
    queue = deque([start])
    result = []
    
    visited.add(start)
    
    while queue:
        vertex = queue.popleft()
        result.append(vertex)
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return result
""",
    
    # Depth-First Search (DFS) - O(V + E) time complexity
    'dfs': """
def dfs(graph, start):
    \"\"\"
    Depth-First Search implementation with O(V + E) time complexity.
    
    Args:
        graph: Graph represented as an adjacency list (dictionary)
        start: Starting vertex
    
    Returns:
        List of vertices in DFS order
    \"\"\"
    visited = set()
    result = []
    
    def dfs_recursive(vertex):
        visited.add(vertex)
        result.append(vertex)
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                dfs_recursive(neighbor)
    
    dfs_recursive(start)
    return result
""",
    
    # Dijkstra's Algorithm - O((V + E) log V) time complexity
    'dijkstra': """
def dijkstra(graph, start):
    \"\"\"
    Dijkstra's Algorithm implementation with O((V + E) log V) time complexity.
    
    Args:
        graph: Graph represented as an adjacency list with weights (dictionary)
        start: Starting vertex
    
    Returns:
        Dictionary of shortest distances from start to all vertices
    \"\"\"
    import heapq
    
    # Initialize distances
    distances = {vertex: float('infinity') for vertex in graph}
    distances[start] = 0
    
    # Priority queue
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)
        
        # If current distance is greater than the known distance, skip
        if current_distance > distances[current_vertex]:
            continue
        
        # Check all neighbors
        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight
            
            # If new distance is shorter, update
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances
"""
}

# DYNAMIC PROGRAMMING ALGORITHMS
DYNAMIC_PROGRAMMING_ALGORITHMS = {
    # Fibonacci (DP) - O(n) time complexity
    'fibonacci_dp': """
def fibonacci_dp(n):
    \"\"\"
    Dynamic programming implementation of Fibonacci with O(n) time complexity.
    \"\"\"
    if n <= 1:
        return n
    
    # Initialize DP table
    fib = [0] * (n + 1)
    fib[1] = 1
    
    # Fill DP table
    for i in range(2, n + 1):
        fib[i] = fib[i - 1] + fib[i - 2]
    
    return fib[n]
""",
    
    # Iterative Fibonacci - O(n) time complexity
    'iterative_fibonacci': """
def iterative_fibonacci(n):
    \"\"\"
    Iterative implementation of Fibonacci with O(n) time complexity.
    \"\"\"
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b
""",
    
    # Longest Common Subsequence (LCS) - O(m*n) time complexity
    'lcs': """
def lcs(str1, str2):
    \"\"\"
    Longest Common Subsequence implementation with O(m*n) time complexity.
    
    Args:
        str1: First string
        str2: Second string
    
    Returns:
        Length of the longest common subsequence
    \"\"\"
    m, n = len(str1), len(str2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]
""",
    
    # Knapsack Problem - O(n*W) time complexity
    'knapsack': """
def knapsack(weights, values, capacity):
    \"\"\"
    0/1 Knapsack Problem implementation with O(n*W) time complexity.
    
    Args:
        weights: List of item weights
        values: List of item values
        capacity: Knapsack capacity
    
    Returns:
        Maximum value that can be put in the knapsack
    \"\"\"
    n = len(weights)
    
    # Create DP table
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]
    
    return dp[n][capacity]
"""
}