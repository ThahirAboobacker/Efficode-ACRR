import axios from 'axios';
import { ApiResponse, OptimizationResult } from '../types';

// Define the base URL for the API
// Change this to match your backend URL
const API_BASE_URL = 'http://localhost:5000/api';

// Function to transform API response to frontend model
const transformResponse = (data: ApiResponse): OptimizationResult => {
  return {
    originalCode: data.original_code,
    optimizedCode: data.optimized_code,
    originalComplexity: data.original_complexity,
    optimizedComplexity: data.optimized_complexity,
    explanation: data.explanation,
    processingTime: data.processing_time,
    timestamp: data.timestamp || Date.now(),
    complexityComparison: {
      original: data.original_complexity,
      optimized: data.optimized_complexity
    },
    metrics: {
      speedup: calculateSpeedup(data.original_complexity, data.optimized_complexity),
      efficiencyGain: calculateEfficiencyGain(data.original_complexity, data.optimized_complexity)
    }
  };
};

// Helper functions for metrics calculation
function calculateSpeedup(before: string, after: string): number {
  // Simple placeholder implementation
  return 1.5;
}

function calculateEfficiencyGain(before: string, after: string): number {
  // Simple placeholder implementation
  return 35;
}

// Function to send code to the backend for optimization
export const optimizeCode = async (code: string): Promise<OptimizationResult> => {
  try {
    const response = await axios.post<ApiResponse>(`${API_BASE_URL}/optimize`, {
      code,
      optimization_level: 'medium'
    });
    
    return transformResponse(response.data);
  } catch (error) {
    console.error('Error optimizing code:', error);
    throw error;
  }
}; 