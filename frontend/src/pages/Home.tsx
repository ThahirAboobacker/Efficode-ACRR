import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  Container,
} from '@mui/material';
import CodeIcon from '@mui/icons-material/Code';
import SpeedIcon from '@mui/icons-material/Speed';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Code Optimization',
      description: 'Optimize your Python code for better performance and readability',
      icon: <CodeIcon sx={{ fontSize: 40 }} />,
      path: '/optimize',
    },
    {
      title: 'Algorithm Optimization',
      description: 'Improve your algorithms with advanced optimization techniques',
      icon: <SpeedIcon sx={{ fontSize: 40 }} />,
      path: '/algorithm',
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 8 }}>
        <Typography
          variant="h2"
          component="h1"
          align="center"
          gutterBottom
          sx={{ mb: 4 }}
        >
          Welcome to EFFICODE-ACRR
        </Typography>
        <Typography
          variant="h5"
          align="center"
          color="text.secondary"
          paragraph
          sx={{ mb: 8 }}
        >
          Algorithm Complexity Reduction and Refactoring Tool
        </Typography>

        <Grid container spacing={4}>
          {features.map((feature) => (
            <Grid item xs={12} md={6} key={feature.title}>
              <Paper
                sx={{
                  p: 4,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Box sx={{ mb: 2, color: 'primary.main' }}>
                  {feature.icon}
                </Box>
                <Typography variant="h5" component="h2" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography color="text.secondary" paragraph>
                  {feature.description}
                </Typography>
                <Button
                  variant="contained"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate(feature.path)}
                  sx={{ mt: 'auto' }}
                >
                  Get Started
                </Button>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default Home; 