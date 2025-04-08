import React from 'react';
import { styled } from '@mui/material/styles';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Divider,
} from '@mui/material';
import { OptimizationResult } from '../../types';

interface OptimizationResultsProps {
  result: OptimizationResult;
}

const ResultContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.paper,
  marginTop: theme.spacing(3),
}));

const MetricChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(1),
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
}));

const OptimizationResults: React.FC<OptimizationResultsProps> = ({ result }) => {
  return (
    <ResultContainer>
      <Typography variant="h5" gutterBottom>
        Optimization Results
      </Typography>
      <Divider sx={{ my: 2 }} />
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Complexity Analysis
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            <MetricChip
              label={`Original: ${result.originalComplexity}`}
              variant="outlined"
            />
            <MetricChip
              label={`Optimized: ${result.optimizedComplexity}`}
              variant="outlined"
            />
          </Box>
        </Grid>

        {result.metrics && (
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Performance Metrics
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <MetricChip
                label={`Speedup: ${result.metrics.speedup}x`}
                color="primary"
              />
              <MetricChip
                label={`Efficiency Gain: ${result.metrics.efficiencyGain}%`}
                color="secondary"
              />
            </Box>
          </Grid>
        )}

        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Explanation
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {result.explanation}
          </Typography>
        </Grid>
      </Grid>
    </ResultContainer>
  );
};

export default OptimizationResults; 