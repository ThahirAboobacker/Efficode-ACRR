// Define the structure of API responses
export interface ApiResponse {
  original_code: string;
  optimized_code: string;
  original_complexity: string;
  optimized_complexity: string;
  explanation: string;
  processing_time: number;
  timestamp?: number;
}

// Define the structure we use in our frontend
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