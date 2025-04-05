import React, { useState } from 'react';
import { ErrorBoundary, FallbackProps } from 'react-error-boundary';
import CodeEditor from './CodeEditor';
import OptimizationResults from './OptimizationResults';
import ComplexityVisualizer from './ComplexityVisualizer';
import { optimizeCode, testBackendConnection } from '../services/api/optimization';
import { OptimizationResult } from '../types';
import './App.css';

// Error fallback component
const ErrorFallback = ({ error, resetErrorBoundary }: FallbackProps) => {
  return (
    <div className="error-container">
      <h2>Something went wrong:</h2>
      <p>{error.message}</p>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
};

function App() {
  const [code, setCode] = useState<string>('');
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [optimizationLevel, setOptimizationLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [backendStatus, setBackendStatus] = useState<'unknown' | 'online' | 'offline'>('unknown');

  const handleOptimize = async () => {
    setIsLoading(true);
    setError(null);
    
    // Validate code before sending
    if (!code || code.trim().length < 5) {
      setError('Please enter valid code with a minimum length of 5 characters.');
      setIsLoading(false);
      return;
    }
    
    try {
      const apiResult = await optimizeCode(code, optimizationLevel as 'low' | 'medium' | 'high');
      setResult(apiResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const checkBackendStatus = async () => {
    try {
      const isConnected = await testBackendConnection();
      setBackendStatus(isConnected ? 'online' : 'offline');
    } catch (err) {
      setBackendStatus('offline');
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>EFFICODE - Algorithmic Code Refactoring & Refinement</h1>
      </header>

      <main className="app-main">
        <ErrorBoundary
          FallbackComponent={ErrorFallback}
          onReset={() => {
            setError(null);
          }}
        >
          <section className="optimization-controls">
            <div className="level-selector">
              <label htmlFor="optimization-level">Optimization Level:</label>
              <select
                id="optimization-level"
                value={optimizationLevel}
                onChange={(e) => setOptimizationLevel(e.target.value as 'low' | 'medium' | 'high')}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div className="controls">
              <button 
                onClick={handleOptimize} 
                disabled={isLoading || !code.trim()}
                className="optimize-button"
              >
                {isLoading ? 'Optimizing...' : 'Optimize Code'}
              </button>
              
              <button 
                onClick={checkBackendStatus} 
                className="test-button"
              >
                Test Backend Connection
              </button>
              
              <div className={`status-indicator ${backendStatus}`}>
                Backend: {backendStatus}
              </div>
              
              {error && <div className="error-message">{error}</div>}
            </div>
          </section>

          <div className="editor-container">
            <CodeEditor 
              code={code} 
              onChange={(value: string) => setCode(value)} 
              language="python" 
              readOnly={isLoading} 
            />
          </div>

          {isLoading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Optimizing your code. This may take a few moments...</p>
            </div>
          )}

          {!isLoading && result && (
            <>
              <OptimizationResults
                explanation={result.explanation}
                complexityBefore={result.originalComplexity}
                complexityAfter={result.optimizedComplexity}
              />
              <ComplexityVisualizer
                complexityBefore={result.originalComplexity}
                complexityAfter={result.optimizedComplexity}
              />
            </>
          )}
        </ErrorBoundary>
      </main>
    </div>
  );
}

export default App; 