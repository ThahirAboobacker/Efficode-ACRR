import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import {
  Box,
  Grid,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CodeEditor from '../components/CodeEditor/CodeEditor';
import OptimizationResults from '../components/OptimizationResults/OptimizationResults';
import { optimizeCode } from '../api/optimizationApi';
import { OptimizationResult } from '../types';

const EditorContainer = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(2),
}));

const OptimizationPage: React.FC = () => {
  const [code, setCode] = useState<string>('');
  const [optimizedCode, setOptimizedCode] = useState<string>('');
  const [optimizationLevel, setOptimizationLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    try {
      setLoading(true);
      setError(null);
      const optimizationResult = await optimizeCode(code, optimizationLevel);
      setResult(optimizationResult);
      setOptimizedCode(optimizationResult.optimizedCode);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during optimization');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(optimizedCode);
  };

  return (
    <Box sx={{ py: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <EditorContainer>
            <CodeEditor
              value={code}
              onChange={setCode}
              title="Input Code"
            />
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Optimization Level</InputLabel>
                <Select
                  value={optimizationLevel}
                  label="Optimization Level"
                  onChange={(e) => setOptimizationLevel(e.target.value as 'low' | 'medium' | 'high')}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
                onClick={handleOptimize}
                disabled={loading || !code}
              >
                Optimize
              </Button>
            </Box>
          </EditorContainer>
        </Grid>

        <Grid item xs={12} md={6}>
          <EditorContainer>
            <CodeEditor
              value={optimizedCode}
              readOnly
              title="Optimized Code"
            />
            <Button
              variant="outlined"
              startIcon={<ContentCopyIcon />}
              onClick={handleCopyCode}
              disabled={!optimizedCode}
            >
              Copy Code
            </Button>
          </EditorContainer>
        </Grid>

        {error && (
          <Grid item xs={12}>
            <Alert severity="error">{error}</Alert>
          </Grid>
        )}

        {result && (
          <Grid item xs={12}>
            <OptimizationResults result={result} />
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default OptimizationPage; 