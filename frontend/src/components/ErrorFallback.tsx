import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetErrorBoundary }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        p: 3,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 600,
          textAlign: 'center',
        }}
      >
        <ErrorOutlineIcon color="error" sx={{ fontSize: 60, mb: 2 }} />
        <Typography variant="h5" component="h1" gutterBottom>
          Something went wrong
        </Typography>
        <Typography color="text.secondary" paragraph>
          {error.message || 'An unexpected error occurred'}
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={resetErrorBoundary}
          sx={{ mt: 2 }}
        >
          Try again
        </Button>
      </Paper>
    </Box>
  );
};

export default ErrorFallback; 