// Define the structure of API responses
export interface ApiResponse {
  original_code: string;
  optimized_code: string | string[]; // Can be a string or array of strings
  original_complexity: string;
  optimized_complexity: string;
  explanation: string;
  processing_time: number;
  timestamp?: number;
  applied_rules?: any[]; // New field for applied rules
  status: 'success' | 'error';
  errors?: string[];
  error?: string;
}

// Define the structure we use in our frontend
export interface OptimizationResult {
  optimizedCode: string;
  explanation: string;
  originalComplexity: string;
  optimizedComplexity: string;
  metrics?: {
    speedup: number;
    efficiencyGain: number;
  };
}

// Request structure
export interface OptimizationRequest {
  code: string;
  optimizationLevel?: 'low' | 'medium' | 'high';
}

// Frontend model types (after transformation)
export interface ComplexityData {
  notation: string;
  description?: string;
  time?: string;
  space?: string;
}

// Component Props
export interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  language: string;
  readOnly?: boolean;
}

export interface OptimizationResultsProps {
  originalCode: string;
  optimizedCode: string;
  explanation: string;
}

export interface ComplexityVisualizerProps {
  originalComplexity: ComplexityData;
  optimizedComplexity: ComplexityData;
}

export interface OptimizationError {
  message: string;
  code?: string;
}

export interface AlgorithmTemplate {
  id: string;
  name: string;
  template: string;
  description: string;
  complexity: string;
}

export interface OptimizationConfig {
  level: 'low' | 'medium' | 'high';
  target: 'performance' | 'readability' | 'both';
  preserveComments: boolean;
} 