// src/services/api/optimization.ts
import axios, { AxiosRequestConfig } from 'axios';
import { optimizeCodeLocally as localOptimizer } from '../offline/localOptimizer';

// Define API response type inline
interface ApiResponse {
  original_code: string;
  optimized_code: string;
  original_complexity: string;
  optimized_complexity: string;
  explanation: string;
  processing_time: number;
  timestamp?: number;
  improvements?: any[];
  performance?: any;
  errors?: string[];
  status?: string;
  applied_rules?: any[];
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
  improvements?: any[];
  errors?: string[];
  status?: string;
  appliedRules?: string[]; // Array of rule names that were applied during optimization
}

// Define complexity data locally instead of importing
export interface ComplexityData {
  notation: string;
  description?: string;
  time?: string;
  space?: string;
}

// Define the base URL for the API - allow for different environments
const BASE_URL = 'http://127.0.0.1:5500';  // Updated to match our server port
const ALTERNATIVE_URL = 'http://localhost:5500';  // Alternative URL format

// API configuration
const API_CONFIG: AxiosRequestConfig = {
  baseURL: BASE_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false // Disable credentials for cross-origin requests
};

const api = axios.create(API_CONFIG);

// Explicitly set fallback flag
const USE_FALLBACK = false; // Allow API calls to backend

// Function to test if the backend is reachable at all - try multiple endpoint variations
export const testBackendConnection = async (): Promise<boolean> => {
  const urls = [
    `${BASE_URL}/health`,
    `${BASE_URL}/api/health`,
    `${ALTERNATIVE_URL}/health`,
    `${ALTERNATIVE_URL}/api/health`
  ];
  
  console.log('[DEBUG] Testing backend connections...');
  
  for (const url of urls) {
    try {
      console.log(`[DEBUG] Testing endpoint: ${url}`);
      const response = await axios.get(url, { 
        timeout: 5000,  // Increased timeout to 5 seconds
        headers: { 'Accept': 'application/json' }
      });
      
      if (response && response.status === 200) {
        console.log(`[SUCCESS] Backend connection successful at ${url}`);
        console.log(`[DEBUG] Response data:`, response.data);
        return true;
      }
    } catch (error: any) {
      console.log(`[ERROR] Endpoint ${url} not available:`, error.message);
    }
  }
  
  console.error('[CRITICAL] Backend connection test failed: All endpoints unreachable');
  console.log('[INFO] Falling back to local optimization');
  return false;
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
    timestamp: Date.now(),
    improvements: [
      {
        rule: "replace_bubble_sort",
        description: "Replace bubble sort with Python's built-in sorting algorithm",
        category: "algorithm"
      }
    ],
    status: "success"
  };
};

// Function to optimize code
export const optimizeCode = async (
  code: string, 
  optimizationLevel: string = 'medium'
): Promise<OptimizationResult> => {
  try {
    console.log('[OPTIMIZE] Starting code optimization...');
    
    // Prepare request data
    const requestData = { 
      code, 
      level: optimizationLevel 
    };
    
    console.log('[OPTIMIZE] Request data:', requestData);
    
    // Try to connect to the backend first
    const isBackendReachable = await testBackendConnection();
    
    // If we're not in fallback mode or backend is reachable, try API call
    if (!USE_FALLBACK || isBackendReachable) {
      try {
        console.log('[OPTIMIZE] Making direct API call to backend server');
        
        // Try both URLs with retries
        let direct = null;
        let lastError = null;
        
        // Try primary URL
        try {
          direct = await axios.post(`${BASE_URL}/api/optimize`, requestData, {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            timeout: 10000 // Increase timeout to 10s
          });
        } catch (err) {
          console.log(`[ERROR] Primary URL failed, trying alternative...`);
          lastError = err;
          
          // Try alternative URL if primary fails
          try {
            direct = await axios.post(`${ALTERNATIVE_URL}/api/optimize`, requestData, {
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              },
              timeout: 10000
            });
          } catch (altErr) {
            console.log(`[ERROR] Alternative URL also failed`);
            lastError = altErr;
          }
        }
        
        if (direct && direct.status === 200 && direct.data) {
          console.log('[SUCCESS] Direct API call succeeded:', direct.data);
          return transformApiResponse(direct.data);
        } else {
          throw lastError || new Error('Failed to get a valid response from the server');
        }
      } catch (directErr: any) {
        console.log('[ERROR] Direct API call failed:', directErr.message);
        
        // If the error was a connection error, throw a more specific error
        if (directErr.message && (
          directErr.message.includes('ECONNREFUSED') || 
          directErr.message.includes('Network Error') ||
          directErr.message.includes('timeout')
        )) {
          throw new Error('Failed to connect to the optimization server. Please check if the server is running.');
        }
        
        throw directErr;
      }
    } else {
      console.log('[INFO] Skipping API call, using fallback directly');
    }
    
    // Use mock response as fallback - FOR TESTING ONLY
    console.log('[FALLBACK] Using mock response');
    const mockResponse = getMockResponse(code);
    console.log('[DEBUG] Mock response:', mockResponse);
    
    // Return transformed mock response
    return transformApiResponse(mockResponse);
    
  } catch (error: any) {
    console.error('[CRITICAL] Error during optimization request:', error);
    
    // Create an error result
    const errorResult: OptimizationResult = {
      originalCode: code,
      optimizedCode: code,
      originalComplexity: 'O(?)',
      optimizedComplexity: 'O(?)',
      explanation: error.message || 'Failed to optimize code. Please check if the server is running.',
      processingTime: 0,
      timestamp: Date.now(),
      complexityComparison: {
        original: 'O(?)',
        optimized: 'O(?)'
      },
      status: 'error',
      errors: [error.message || 'Unknown error'],
      appliedRules: []
    };
    
    return errorResult;
  }
};

// Parse complexity notation
const parseComplexity = (complexityStr: string): ComplexityData => {
  // Default simple parsing
  return {
    notation: complexityStr,
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
  console.log('[DEBUG] Transforming API response:', apiData);
  
  // Handle array optimized_code - the backend might return an array with [code, origComplexity, optComplexity, explanation]
  let optimizedCode = '';
  if (Array.isArray(apiData.optimized_code)) {
    optimizedCode = apiData.optimized_code[0] || '';
    console.log('[DEBUG] Extracted optimized code from array:', optimizedCode);
  } else {
    optimizedCode = apiData.optimized_code || '';
  }
  
  // Handle the applied_rules field from the server response
  const appliedRules = apiData.applied_rules 
    ? apiData.applied_rules.map(rule => rule.description || rule.rule)
    : (apiData.improvements?.map(i => i.description || i.rule) || []);
  
  // The new API format contains different fields, handle both formats
  const result: OptimizationResult = {
    originalCode: apiData.original_code || '',
    optimizedCode,
    // Use fallbacks for fields that might be missing in the new API format
    originalComplexity: apiData.original_complexity || "O(n)",
    optimizedComplexity: apiData.optimized_complexity || "O(n)",
    explanation: apiData.explanation || (apiData.improvements && apiData.improvements.length > 0 
      ? apiData.improvements.map(i => i.description).join("\n") 
      : "Code was optimized."),
    processingTime: apiData.processing_time || (apiData.performance?.time_taken || 0),
    timestamp: apiData.timestamp || Date.now(),
    complexityComparison: {
      original: apiData.original_complexity || "O(n)",
      optimized: apiData.optimized_complexity || "O(n)"
    },
    metrics: {
      speedup: calculateImprovementScore(
        apiData.original_complexity || "O(n)", 
        apiData.optimized_complexity || "O(n)"
      ) / 20,
      efficiencyGain: calculateImprovementScore(
        apiData.original_complexity || "O(n)", 
        apiData.optimized_complexity || "O(n)"
      )
    },
    // New fields from the updated API
    improvements: apiData.improvements || [],
    errors: apiData.errors || [],
    status: apiData.status || "success",
    appliedRules
  };
  
  console.log('[DEBUG] Transformed result:', result);
  return result;
};

export const checkHealth = async (): Promise<boolean> => {
  const endpoints = [
    `${BASE_URL}/api/health`,
    `${BASE_URL}/health`,
    `${BASE_URL}/`
  ];
  
  for (const endpoint of endpoints) {
    try {
      const response = await axios.get(endpoint);
      return response.status === 200;
    } catch (error) {
      console.log(`Health check failed at ${endpoint}`);
    }
  }
  
  console.error('Health check failed: All endpoints unreachable');
  return false;
};

// Simple local optimization as fallback when backend is unavailable
const optimizeCodeLocally = (code: string): OptimizationResult => {
  console.log('Using local optimization fallback');
  
  // Apply very basic optimizations
  let optimized = code;
  
  // Remove unnecessary comments
  optimized = optimized.replace(/\/\/.*$/gm, '');
  
  // Remove console.log statements for production code
  optimized = optimized.replace(/console\.log\(.*?\);/g, '');
  
  // Remove unnecessary white space
  optimized = optimized.replace(/\s+/g, ' ');
  optimized = optimized.replace(/{\s+/g, '{');
  optimized = optimized.replace(/\s+}/g, '}');
  
  // Format code properly (simple formatting only)
  optimized = optimized.replace(/;/g, ';\n');
  optimized = optimized.replace(/{/g, '{\n');
  optimized = optimized.replace(/}/g, '\n}');
  
  return {
    originalCode: code,
    optimizedCode: optimized,
    originalComplexity: 'O(n)',
    optimizedComplexity: 'O(n)',
    explanation: 'Basic local optimization applied (backend unavailable)',
    processingTime: 0,
    timestamp: Date.now(),
    complexityComparison: {
      original: 'O(n)',
      optimized: 'O(n)'
    },
    appliedRules: ['Local fallback optimization'],
    status: 'success'
  };
};