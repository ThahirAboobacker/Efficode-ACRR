import axios from 'axios';
import { OptimizationResult, ApiResponse } from '../types';

// Define the base URL for the API
// Change this to match your backend URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Try alternative ports if the default doesn't work
const tryAlternativeEndpoints = async (endpoint: string, data: any) => {
  console.log(`Trying primary endpoint: ${API_BASE_URL}${endpoint}`);
  
  try {
    // Try the default endpoint first
    return await axios.post(`${API_BASE_URL}${endpoint}`, data);
  } catch (error: any) {
    console.error(`Error with primary endpoint: ${error.message}`);
    
    // Try alternative ports
    const alternativePorts = [8080, 3001];
    
    for (const port of alternativePorts) {
      const altUrl = `http://localhost:${port}`;
      console.log(`Trying alternative endpoint: ${altUrl}${endpoint}`);
      
      try {
        return await axios.post(`${altUrl}${endpoint}`, data);
      } catch (altError: any) {
        console.error(`Error with alternative port ${port}: ${altError.message}`);
      }
    }
    
    // If all alternatives fail, rethrow the original error
    throw error;
  }
};

// Function to transform API response to frontend model
const transformResponse = (data: ApiResponse): OptimizationResult => {
  console.log('Transforming response:', data);
  
  // Handle the case where optimized_code is an array (take the first item)
  const optimizedCode = Array.isArray(data.optimized_code) 
    ? data.optimized_code[0] || '' 
    : data.optimized_code || '';

  return {
    optimizedCode,
    explanation: data.explanation || 'No explanation provided',
    originalComplexity: data.original_complexity || 'O(?)',
    optimizedComplexity: data.optimized_complexity || 'O(?)',
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
export const optimizeCode = async (
  code: string,
  level: 'low' | 'medium' | 'high' = 'medium'
): Promise<OptimizationResult> => {
  try {
    console.log(`Attempting optimization request with code of length: ${code.length}`);
    
    const payload = {
      code,
      level,
      mode: 'auto',
      debug: true // Enable debug mode to get more information
    };
    
    console.log('Request payload:', payload);
    
    // First try to check if the backend is accessible
    try {
      const healthCheck = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
      console.log('Backend health check response:', healthCheck.data);
    } catch (healthError: any) {
      console.error('Backend health check failed:', {
        message: healthError.message,
        code: healthError.code,
        response: healthError.response?.data
      });
    }
    
    // Proceed with optimization request
    console.log(`Sending optimization request to ${API_BASE_URL}/optimize`);
    const response = await axios.post<ApiResponse>(`${API_BASE_URL}/optimize`, payload, {
      timeout: 10000, // 10 second timeout
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    console.log('Optimization response:', response.data);
    
    if (response.data.status === 'error') {
      throw new Error(response.data.explanation || response.data.errors?.[0] || 'Failed to optimize code');
    }
    
    return transformResponse(response.data);
  } catch (error: any) {
    console.error('Optimization error details:', {
      name: error.name,
      message: error.message,
      code: error.code,
      response: error.response?.data,
      stack: error.stack
    });
    
    if (error.response?.data) {
      console.error('Error response:', error.response.data);
      throw new Error(
        error.response.data.explanation || 
        error.response.data.errors?.[0] || 
        error.response.data.error || 
        'Failed to optimize code'
      );
    }
    
    // Handle specific error types
    if (error.code === 'ECONNREFUSED') {
      throw new Error('Could not connect to the backend server. Please ensure it is running.');
    } else if (error.code === 'ETIMEDOUT') {
      throw new Error('Request timed out. The backend server might be busy or not responding.');
    } else if (error.message.includes('Network Error')) {
      throw new Error('Network error occurred. Please check if the backend server is running and accessible.');
    }
    
    throw error;
  }
}; 