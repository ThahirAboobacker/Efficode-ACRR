// src/components/ComplexityVisualizer/index.tsx
import React from 'react';
import './styles.css';

interface ComplexityVisualizerProps {
  complexityBefore: string;
  complexityAfter: string;
  originalComplexity?: string;
  optimizedComplexity?: string;
}

const ComplexityVisualizer: React.FC<ComplexityVisualizerProps> = ({ 
  complexityBefore, 
  complexityAfter,
  originalComplexity,
  optimizedComplexity
}) => {
  const beforeValue = originalComplexity || complexityBefore;
  const afterValue = optimizedComplexity || complexityAfter;

  const getComplexityColor = (complexity: string) => {
    if (complexity.includes('1)') || complexity.includes('log')) {
      return '#4CAF50'; // Green for good complexity
    } else if (complexity.includes('n log n')) {
      return '#FF9800'; // Orange for medium complexity
    } else if (complexity.includes('n²') || complexity.includes('n^2')) {
      return '#F44336'; // Red for poor complexity
    } else if (complexity.includes('2^n') || complexity.includes('n!')) {
      return '#9C27B0'; // Purple for very poor complexity
    }
    return '#2196F3'; // Blue default
  };

  return (
    <div className="complexity-visualizer">
      <div className="complexity-card">
        <h4>Original Complexity</h4>
        <div 
          className="complexity-value" 
          style={{ backgroundColor: getComplexityColor(beforeValue) }}
        >
          {beforeValue || 'N/A'}
        </div>
      </div>
      
      <div className="complexity-arrow">→</div>
      
      <div className="complexity-card">
        <h4>Optimized Complexity</h4>
        <div 
          className="complexity-value" 
          style={{ backgroundColor: getComplexityColor(afterValue) }}
        >
          {afterValue || 'N/A'}
        </div>
      </div>
    </div>
  );
};

export default ComplexityVisualizer;