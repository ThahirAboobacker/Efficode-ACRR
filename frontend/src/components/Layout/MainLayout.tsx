import React from 'react';
import { styled } from '@mui/material/styles';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import { Outlet } from 'react-router-dom';

const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginTop: 64,
  minHeight: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}));

const MainLayout: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="fixed">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            EFFICODE-ACRR
          </Typography>
        </Toolbar>
      </AppBar>
      <MainContent>
        <Container maxWidth="xl">
          <Outlet />
        </Container>
      </MainContent>
    </Box>
  );
};

export default MainLayout; 