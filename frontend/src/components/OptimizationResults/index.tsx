// src/components/OptimizationResults/index.tsx
import React from 'react';
import './styles.css';

interface OptimizationResultsProps {
  explanation: string;
  complexityBefore: string;
  complexityAfter: string;
}

const OptimizationResults: React.FC<OptimizationResultsProps> = ({ 
  explanation, 
  complexityBefore,
  complexityAfter
}) => {
  // Convert markdown-style explanation to HTML
  const formatExplanation = (text: string) => {
    // Basic formatting for headers and lists
    return text
      .replace(/## (.*)/g, '<h3>$1</h3>')
      .replace(/\- (.*)/g, '<li>$1</li>')
      .replace(/\n\n/g, '<br/><br/>');
  };

  return (
    <div className="optimization-results">
      <h2>Optimization Explanation</h2>
      <div className="complexity-summary">
        <div className="complexity-before">
          <span className="label">Time Complexity (Before):</span>
          <span className="value">{complexityBefore}</span>
        </div>
        <div className="complexity-arrow">→</div>
        <div className="complexity-after">
          <span className="label">Time Complexity (After):</span>
          <span className="value">{complexityAfter}</span>
        </div>
      </div>
      <div 
        className="explanation-content"
        dangerouslySetInnerHTML={{ __html: formatExplanation(explanation) }}
      />
    </div>
  );
}

export default OptimizationResults;