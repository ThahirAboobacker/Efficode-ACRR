import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TEST_CODE = `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)`;

interface ApiResponse {
  original_code: string;
  optimized_code: any; // Can be string or array
  original_complexity: string;
  optimized_complexity: string;
  applied_rules?: any[];
}

const ApiTestComponent: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [optimizedCode, setOptimizedCode] = useState<string>('');
  const [healthStatus, setHealthStatus] = useState<string>('Unknown');

  // Test the health endpoint
  const testHealth = async () => {
    try {
      const result = await axios.get('http://localhost:5500/health');
      setHealthStatus(`Online (Status: ${result.status})`);
      return true;
    } catch (err) {
      setHealthStatus('Offline - Connection failed');
      return false;
    }
  };

  // Test the optimization endpoint
  const testOptimization = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await axios.post(
        'http://localhost:5500/api/optimize',
        {
          code: TEST_CODE,
          level: 'medium'
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      setResponse(result.data);
      
      // Handle array response
      if (Array.isArray(result.data.optimized_code)) {
        setOptimizedCode(result.data.optimized_code[0] || '');
      } else {
        setOptimizedCode(result.data.optimized_code || '');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Run the health check on component mount
  useEffect(() => {
    testHealth();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>API Test Component</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Backend Status: <span style={{ color: healthStatus.includes('Online') ? 'green' : 'red' }}>{healthStatus}</span></h2>
        <button 
          onClick={testHealth}
          style={{ padding: '8px 16px', marginRight: '10px' }}
        >
          Test Health Endpoint
        </button>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Optimization Test</h2>
        <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '5px' }}>
          {TEST_CODE}
        </pre>
        <button 
          onClick={testOptimization}
          disabled={loading}
          style={{ padding: '8px 16px', marginRight: '10px' }}
        >
          {loading ? 'Testing...' : 'Test Optimization'}
        </button>
      </div>
      
      {error && (
        <div style={{ marginBottom: '20px', color: 'red', padding: '10px', background: '#ffeeee', borderRadius: '5px' }}>
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}
      
      {response && (
        <div style={{ marginBottom: '20px' }}>
          <h3>API Response:</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h4>Original Code:</h4>
              <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '5px', maxHeight: '200px', overflow: 'auto' }}>
                {response.original_code}
              </pre>
              <p><strong>Complexity:</strong> {response.original_complexity}</p>
            </div>
            <div>
              <h4>Optimized Code:</h4>
              <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '5px', maxHeight: '200px', overflow: 'auto' }}>
                {optimizedCode}
              </pre>
              <p><strong>Complexity:</strong> {response.optimized_complexity}</p>
            </div>
          </div>
          
          <div>
            <h4>Applied Rules:</h4>
            <ul>
              {response.applied_rules && response.applied_rules.map((rule, index) => (
                <li key={index}>{rule.description || rule.rule}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiTestComponent; 