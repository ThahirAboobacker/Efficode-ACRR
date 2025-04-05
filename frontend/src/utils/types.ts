// Define all interfaces in one place
export interface OptimizationResult {
  optimizedCode: string;
  explanation: string;
  complexityComparison: {
    original: {
      time: string;
      space: string;
    };
    optimized: {
      time: string;
      space: string;
    };
  };
  metrics?: {
    improvementScore: number;
    executionTime: number;
  };
}

// Define the API response interface
export interface ApiResponse {
  success: boolean;
  data?: OptimizationResult;
  error?: string;
}

// Define the code editor props interface
export interface CodeEditorProps {
  value: string;
  onChange: (value: string | undefined) => void;
  readOnly?: boolean;  // Make sure readOnly is included
}

// Define the optimization results props interface
export interface OptimizationResultsProps {
  result: OptimizationResult;
}

// Define the complexity visualizer props interface
export interface ComplexityVisualizerProps {
  originalComplexity: {
    time: string;
    space: string;
  };
  optimizedComplexity: {
    time: string;
    space: string;
  };
}

// Export an empty object to ensure this file is treated as a module
export {};
