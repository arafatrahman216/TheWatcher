import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Tabs,
  Tab,
} from '@mui/material';

const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const getCurrentTab = () => {
    if (location.pathname === '/') return 'home';
    if (location.pathname.startsWith('/dashboard')) return 'dashboard';
    return false;
  };

  const handleTabChange = (event, newValue) => {
    if (newValue === 'home') navigate('/');
    else if (newValue === 'dashboard') navigate('/dashboard');
  };

  return (
    <AppBar
      position="sticky"
      sx={{
        background: 'linear-gradient(135deg, rgba(20,20,20,0.9), rgba(40,40,40,0.8))',
        backdropFilter: 'blur(15px)',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
      }}
    >
      <Toolbar sx={{ minHeight: 70 }}>
        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, fontWeight: 700, color: '#00ff7f', letterSpacing: 1 }}
        >
          🔍 The Watcher
        </Typography>

        <Tabs
          value={getCurrentTab()}
          onChange={handleTabChange}
          textColor="inherit"
          TabIndicatorProps={{ style: { backgroundColor: '#00ff7f', height: 3, borderRadius: 2 } }}
          sx={{
            mr: 3,
            '& .MuiTab-root': {
              color: 'rgba(255, 255, 255, 0.7)',
              textTransform: 'none',
              fontWeight: 500,
              fontSize: 16,
              transition: 'color 0.3s',
              '&:hover': { color: '#00ff7f' },
              '&.Mui-selected': { color: '#00ff7f' },
            },
          }}
        >
          <Tab label="Home" value="home" />
          <Tab label="Dashboard" value="dashboard" />
        </Tabs>

        <Typography
          variant="body2"
          sx={{ mr: 2, color: 'rgba(255,255,255,0.9)', fontWeight: 500 }}
        >
          Welcome, {user?.name}
        </Typography>

        <Button
          variant="outlined"
          onClick={onLogout}
          sx={{
            color: '#00ff7f',
            borderColor: '#00ff7f',
            borderRadius: '20px',
            textTransform: 'none',
            fontWeight: 600,
            '&:hover': {
              backgroundColor: 'rgba(0,255,127,0.1)',
              borderColor: '#00ff7f',
            },
          }}
        >
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
