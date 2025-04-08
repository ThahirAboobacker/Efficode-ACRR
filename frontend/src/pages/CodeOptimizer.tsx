import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { optimizeCode } from '../api/optimizationApi';
import { OptimizationResult } from '../types';

const CodeOptimizer: React.FC = () => {
  const [code, setCode] = useState<string>('# Enter your Python code here\n');
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showCopied, setShowCopied] = useState<boolean>(false);

  const handleOptimize = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      if (code.trim().length < 5) {
        throw new Error('Please enter a valid code snippet');
      }
      
      const apiResult = await optimizeCode(code, 'medium');
      setResult(apiResult);
    } catch (err: any) {
      setError(err.message || 'An error occurred while optimizing the code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyCode = () => {
    if (result?.optimizedCode) {
      navigator.clipboard.writeText(result.optimizedCode);
      setShowCopied(true);
    }
  };

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Code Optimizer
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '500px' }}>
            <Typography variant="h6" gutterBottom>
              Input Code
            </Typography>
            <Box sx={{ height: 'calc(100% - 40px)' }}>
              <Editor
                height="100%"
                defaultLanguage="python"
                value={code}
                onChange={(value) => setCode(value || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '500px' }}>
            <Typography variant="h6" gutterBottom>
              Optimized Code
            </Typography>
            <Box sx={{ height: 'calc(100% - 40px)' }}>
              <Editor
                height="100%"
                defaultLanguage="python"
                value={result?.optimizedCode || '# Optimized code will appear here'}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={isLoading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          onClick={handleOptimize}
          disabled={isLoading}
        >
          {isLoading ? 'Optimizing...' : 'Optimize Code'}
        </Button>
        
        {result && (
          <Button
            variant="outlined"
            startIcon={<ContentCopyIcon />}
            onClick={handleCopyCode}
          >
            Copy Optimized Code
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Paper sx={{ mt: 3, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Optimization Details
          </Typography>
          <Typography variant="body1" paragraph>
            {result.explanation}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Original Complexity
              </Typography>
              <Typography variant="body1">
                {result.originalComplexity}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Optimized Complexity
              </Typography>
              <Typography variant="body1">
                {result.optimizedComplexity}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      <Snackbar
        open={showCopied}
        autoHideDuration={3000}
        onClose={() => setShowCopied(false)}
        message="Code copied to clipboard"
      />
    </Box>
  );
};

export default CodeOptimizer; 