// src/services/api/optimization.ts
import axios, { AxiosRequestConfig } from 'axios';

// Define API response type inline
interface ApiResponse {
  original_code: string;
  optimized_code: string;
  original_complexity: string;
  optimized_complexity: string;
  explanation: string;
  processing_time: number;
  timestamp?: number;
}

// Ensure this is exported
export interface OptimizationResult {
  originalCode: string;
  optimizedCode: string;
  originalComplexity: string;
  optimizedComplexity: string;
  explanation: string;
  processingTime: number;
  timestamp: number;
  complexityComparison: {
    original: string;
    optimized: string;
  };
  metrics?: {
    speedup: number;
    efficiencyGain: number;
  };
}

// Define complexity data locally instead of importing
export interface ComplexityData {
  notation: string;
  description?: string;
  time?: string;
  space?: string;
}

// API configuration
const API_CONFIG: AxiosRequestConfig = {
  baseURL: 'http://localhost:5000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: false // Set to true if your backend requires credentials
};

const api = axios.create(API_CONFIG);

// Test if the backend is reachable at all
export const testBackendConnection = async (): Promise<boolean> => {
  try {
    // Try to reach the health endpoint or root
    const response = await axios.get('http://localhost:5000/health');
    console.log('Backend connection test:', response.status);
    return response.status === 200;
  } catch (error) {
    console.error('Backend connection test failed:', error);
    return false;
  }
};

// Add a mock response function for testing
const getMockResponse = (code: string): ApiResponse => {
  return {
    original_code: code,
    optimized_code: code.includes('bubble_sort') 
      ? `def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr)//2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)`
      : code,
    original_complexity: "O(n²)",
    optimized_complexity: "O(n log n)",
    explanation: "The code was optimized by replacing bubble sort with quick sort algorithm, which has better average time complexity.",
    processing_time: 0.5,
    timestamp: Date.now()
  };
};

// Function to optimize code
export const optimizeCode = async (
  code: string, 
  optimizationLevel: string = 'medium'
): Promise<OptimizationResult> => {
  try {
    // First test if backend is reachable
    const isConnected = await testBackendConnection();
    if (!isConnected) {
      throw new Error('Cannot connect to backend server. Please ensure it is running.');
    }
    
    // Log complete request details
    console.log('API Request:', {
      url: 'http://localhost:5000/api/optimize',
      method: 'POST',
      data: { code, optimization_level: optimizationLevel },
      headers: { 'Content-Type': 'application/json' }
    });
    
    // If you want to test with fallback, uncomment this line:
    // return transformApiResponse(getMockResponse(code));
    
    // Make direct axios call without using instance
    const response = await axios({
      method: 'post',
      url: 'http://localhost:5000/api/optimize',
      data: { 
        code, 
        optimization_level: optimizationLevel 
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Response received:', response);
    return transformApiResponse(response.data);
  } catch (error: any) {
    console.error('Detailed error:', error);
    
    // For testing purposes, you can use the mock response
    // Uncomment this in production, or make it a configurable option
    // return transformApiResponse(getMockResponse(code));
    
    // Enhanced error reporting
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
      console.error('Response data:', error.response.data);
      
      // Create specific error message based on status code
      switch (error.response.status) {
        case 400:
          throw new Error(`Bad request: ${JSON.stringify(error.response.data)}`);
        case 404:
          throw new Error('API endpoint not found. Check backend URL.');
        case 500:
          throw new Error('Backend server error. Check server logs.');
        default:
          throw new Error(`Server returned ${error.response.status}: ${JSON.stringify(error.response.data)}`);
      }
    } else if (error.request) {
      throw new Error('No response received from backend. Ensure the server is running.');
    } else {
      throw new Error(`Request error: ${error.message}`);
    }
  }
};

// Parse complexity notation
const parseComplexity = (complexityStr: string): ComplexityData => {
  // Default simple parsing
  return {
    notation: complexityStr, // Fix: add notation property
    time: complexityStr,
    space: "O(1)" // Default space complexity if not provided
  };
};

// Calculate improvement score (0-100)
const calculateImprovementScore = (before: string, after: string): number => {
  // Simple scoring algorithm
  if (before.includes('n²') && after.includes('n log n')) {
    return 80;
  } else if (before.includes('n²') && after.includes('n')) {
    return 90;
  } else if (before.includes('n') && after.includes('log')) {
    return 85;
  }
  return 50; // Default improvement score
};

// Transform API response to frontend format
const transformApiResponse = (apiData: ApiResponse): OptimizationResult => {
  return {
    originalCode: apiData.original_code,
    optimizedCode: apiData.optimized_code,
    originalComplexity: apiData.original_complexity,
    optimizedComplexity: apiData.optimized_complexity,
    explanation: apiData.explanation,
    processingTime: apiData.processing_time,
    timestamp: apiData.timestamp || Date.now(),
    complexityComparison: {
      original: apiData.original_complexity,
      optimized: apiData.optimized_complexity
    },
    metrics: {
      speedup: calculateImprovementScore(apiData.original_complexity, apiData.optimized_complexity) / 20,
      efficiencyGain: calculateImprovementScore(apiData.original_complexity, apiData.optimized_complexity)
    }
  };
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await axios.get(`${API_CONFIG.baseURL}/health`);
    return response.data.status === 'healthy';
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

// Add this to your optimization service
export const optimizeCodeLocally = (code: string): OptimizationResult => {
  // Simple local optimization logic for testing
  const optimized = code.includes('bubble_sort') 
    ? code.replace('bubble_sort', 'quick_sort').replace(/for i in range\(n\)[\s\S]*?return arr/, 
      `if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)`)
    : code;
    
  return {
    originalCode: code,
    optimizedCode: optimized,
    originalComplexity: "O(n²)",
    optimizedComplexity: "O(n log n)",
    explanation: "The code was optimized by replacing bubble sort with quick sort algorithm, which has better average time complexity.",
    processingTime: 0.5,
    timestamp: Date.now(),
    complexityComparison: {
      original: "O(n²)",
      optimized: "O(n log n)"
    },
    metrics: {
      speedup: 1.5,
      efficiencyGain: 35
    }
  };
};