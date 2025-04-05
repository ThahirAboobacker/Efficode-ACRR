import React from 'react';
import './styles.css';

interface PerformanceMetricsProps {
  speedup: number;
  efficiencyGain: number;
  originalComplexity: string;
  optimizedComplexity: string;
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  speedup,
  efficiencyGain,
  originalComplexity,
  optimizedComplexity
}) => {
  return (
    <div className="performance-metrics">
      <div className="metrics-header">Performance Metrics</div>
      <div className="metrics-grid">
        <div className="metric-item">
          <div className="metric-value">{speedup.toFixed(1)}x</div>
          <div className="metric-label">Speedup</div>
        </div>
        
        <div className="metric-item">
          <div className="metric-value">{efficiencyGain}%</div>
          <div className="metric-label">Efficiency Gain</div>
        </div>
        
        <div className="metric-item">
          <div className="metric-value">{originalComplexity}</div>
          <div className="metric-label">Original Complexity</div>
        </div>
        
        <div className="metric-item">
          <div className="metric-value complexity-improved">{optimizedComplexity}</div>
          <div className="metric-label">Optimized Complexity</div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics; 