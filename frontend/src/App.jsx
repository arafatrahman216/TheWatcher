import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import CircularProgress from '@mui/material/CircularProgress';
import theme from './theme';
import { authAPI } from './api';

// Pages
import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import CreateMonitorPage from './pages/CreateMonitorPage';

// Components
import Navbar from './components/HomeComponent/Navbar';

// Protected Route Component
function ProtectedRoute({ children, user }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

// Public Route Component (redirect to home if already logged in)
function PublicRoute({ children, user }) {
  if (user) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function AppContent({ user, onLogin, onLogout }) {
  return (
    <>
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/login" 
          element={
            <PublicRoute user={user}>
              <AuthPage onLogin={onLogin} />
            </PublicRoute>
          } 
        />
        
        {/* Protected Routes */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute user={user}>
              <Navbar user={user} onLogout={onLogout} />
              <HomePage user={user} />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute user={user}>
              <Navbar user={user} onLogout={onLogout} />
              <Dashboard user={user} />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/dashboard/:monitorId" 
          element={
            <ProtectedRoute user={user}>
              <Navbar user={user} onLogout={onLogout} />
              <Dashboard user={user} />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/create-monitor" 
          element={
            <ProtectedRoute user={user}>
              <Navbar user={user} onLogout={onLogout} />
              <CreateMonitorPage user={user} />
            </ProtectedRoute>
          } 
        />
        
        {/* Redirect any unknown routes */}
        <Route path="*" element={<Navigate to={user ? "/" : "/login"} replace />} />
      </Routes>
    </>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const checkAuth = async () => {
      try {
        const userData = authAPI.getCurrentUser();
        if (userData) {
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        authAPI.logout(); // Clear invalid session
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    authAPI.logout();
    setUser(null);
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <CircularProgress />
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppContent 
          user={user} 
          onLogin={handleLogin} 
          onLogout={handleLogout} 
        />
      </Router>
    </ThemeProvider>
  );
}
