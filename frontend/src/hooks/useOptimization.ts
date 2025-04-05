// src/hooks/useOptimization.ts
import { useState } from 'react';
import { optimizeCode, OptimizationResult } from '../services/api/optimization';

export const useOptimization = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<OptimizationResult | null>(null);

  const optimize = async (
    code: string, 
    optimizationLevel: 'low' | 'medium' | 'high' = 'medium'
  ) => {
    try {
      setLoading(true);
      setError(null);
      const optimizationResult = await optimizeCode(code, optimizationLevel);
      setResult(optimizationResult);
      return optimizationResult;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to optimize code';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    optimize,
    loading,
    error,
    result
  };
};