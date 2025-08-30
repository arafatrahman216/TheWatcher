import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Tabs,
  Tab,
} from '@mui/material';

const Navbar = ({ user, currentView, onViewChange, onLogout }) => {
  return (
    <AppBar position="static" sx={{ backgroundColor: 'rgba(0, 0, 0, 0.1)', backdropFilter: 'blur(10px)', boxShadow: 'none' }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600, color: 'white' }}>
          🔍 The Watcher
        </Typography>
        <Tabs
          value={currentView}
          onChange={(e, newValue) => onViewChange(newValue)}
          sx={{
            mr: 3,
            '& .MuiTab-root': {
              color: 'rgba(255, 255, 255, 0.7)',
              textTransform: 'none',
              fontWeight: 500,
              '&.Mui-selected': {
                color: '#00ff7f',
              },
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#00ff7f',
            },
          }}
        >
          <Tab label="Home" value="home" />
          <Tab label="Dashboard" value="dashboard" />
        </Tabs>
        <Typography variant="body2" sx={{ mr: 2, color: 'rgba(255,255,255,0.9)' }}>
          Welcome, {user?.name}
        </Typography>
        <Button 
          color="inherit" 
          onClick={onLogout}
          sx={{ 
            color: 'white',
            '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' }
          }}
        >
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;