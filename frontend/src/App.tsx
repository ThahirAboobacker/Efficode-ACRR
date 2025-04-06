import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import CodeEditor from './components/CodeEditor';
import OptimizationResults from './components/OptimizationResults';
import PerformanceMetrics from './components/PerformanceMetrics';
import { optimizeCode } from './api/optimizationApi';
import { OptimizationResult } from './types';
import ApiTestPage from './pages/ApiTest';

function App() {
  const [code, setCode] = useState<string>('# Enter your Python code here\n');
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<string>('python');
  const [isMobile, setIsMobile] = useState<boolean>(false);

  // Check for mobile view
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleOptimize = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      if (code.trim().length < 5) {
        throw new Error('Please enter a valid code snippet');
      }
      
      // Call the API without fallback implementation
      try {
        const apiResult = await optimizeCode(code, 'medium');
        setResult(apiResult);
      } catch (apiError) {
        console.error('API error:', apiError);
        setError('Failed to optimize code. Please check if the server is running.');
      }
    } catch (err: any) {
      setError(err.message || 'An unknown error occurred');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyCode = () => {
    if (result?.optimizedCode) {
      navigator.clipboard.writeText(result.optimizedCode);
    }
  };

  const MainApp = () => (
    <>
      <header className="App-header">
        <h1>EFFICODE-ACRR</h1>
        <p>Algorithm Complexity Reduction and Refactoring</p>
        <nav>
          <Link to="/test-api" className="nav-link">Test API Connection</Link>
        </nav>
      </header>
      
      <main className={`App-main ${isMobile ? 'mobile-view' : 'desktop-view'}`}>
        <div className="code-container">
          <div className="editor-panel">
            <div className="editor-header">
              <h2>Input Code</h2>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="language-selector"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
              </select>
            </div>
            <CodeEditor 
              code={code} 
              onChange={setCode} 
              language={language}
              readOnly={isLoading}
            />
            <div className="editor-footer">
              <button 
                onClick={handleOptimize} 
                disabled={isLoading}
                className="action-button optimize-button"
              >
                {isLoading ? 'Optimizing...' : 'Optimize Code'}
              </button>
              {error && <div className="error-message">{error}</div>}
            </div>
          </div>
          
          {result && (
            <div className="editor-panel">
              <div className="editor-header">
                <h2>Optimized Code</h2>
                <div className="action-buttons">
                  <button 
                    onClick={handleCopyCode}
                    className="action-button copy-button"
                  >
                    Copy Code
                  </button>
                </div>
              </div>
              <CodeEditor 
                code={result.optimizedCode} 
                onChange={() => {}} 
                language={language}
                readOnly={true}
                highlightDiff={true}
                originalCode={code}
              />
              {result.metrics && (
                <PerformanceMetrics 
                  speedup={result.metrics.speedup}
                  efficiencyGain={result.metrics.efficiencyGain}
                  originalComplexity={result.originalComplexity}
                  optimizedComplexity={result.optimizedComplexity}
                />
              )}
            </div>
          )}
        </div>
        
        {result && (
          <div className="explanation-container">
            <OptimizationResults 
              explanation={result.explanation}
              complexityBefore={result.originalComplexity}
              complexityAfter={result.optimizedComplexity}
            />
          </div>
        )}
      </main>
    </>
  );

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<MainApp />} />
          <Route path="/test-api" element={<ApiTestPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
