// pages/AuthPage.jsx
import React, { useState } from "react";
import { Box, Card, CardContent, Tabs, Tab, Alert, Typography, LinearProgress } from "@mui/material";
import LoginForm from "../components/AuthComponent/Login";
import SignupForm from "../components/AuthComponent/Signup";
import OtpVerifier from "../components/AuthComponent/EmailVerification";
import { authAPI } from "../api";

export default function AuthPage({ onLogin }) {
  const [tab, setTab] = useState(0); // 0: Login, 1: Signup
  const [showOTP, setShowOTP] = useState(false);
  const [pendingEmail, setPendingEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ show: false, type: 'info', message: '' });

  const showAlert = (type, message) => {
    setAlert({ show: true, type, message });
    setTimeout(() => setAlert({ show: false, type: 'info', message: '' }), 5000);
  };

  const handleLogin = async (email, password) => {
    setLoading(true);
    try {
      const response = await authAPI.login({ email, password });
      if (response.success) {
        showAlert('success', 'Login successful!');
        onLogin(response.user);
      } else {
        showAlert('error', response.message || 'Login failed');
      }
    } catch (error) {
      showAlert('error', error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (name, email, password) => {
    setLoading(true);
    try {
      const response = await authAPI.signup({ name, email, password });
      if (response.success) {
        showAlert('success', 'Account created! Please check your email for verification code.');
        setPendingEmail(email);
        setShowOTP(true);
      } else {
        showAlert('error', response.message || 'Signup failed');
      }
    } catch (error) {
      showAlert('error', error.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (otp) => {
    setLoading(true);
    try {
      const response = await authAPI.verifyEmail({ email: pendingEmail, otp });
      if (response.success) {
        showAlert('success', 'Email verified successfully! You can now login.');
        setShowOTP(false);
        setPendingEmail("");
        setTab(0); // Switch to login tab
      } else {
        showAlert('error', response.message || 'Verification failed');
      }
    } catch (error) {
      showAlert('error', error.message || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToAuth = () => {
    setShowOTP(false);
    setPendingEmail("");
    setTab(1); // Go back to signup
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        padding: 2,
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '800px',
          height: '800px',
          transform: 'translate(-50%, -50%)',
          border: '2px solid rgba(0, 255, 127, 0.3)',
          borderRadius: '50%',
          animation: 'radarPulse 6s linear infinite',
          zIndex: 0,
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '800px',
          height: '800px',
          transform: 'translate(-50%, -50%)',
          background: 'conic-gradient(from 0deg, transparent 0deg, rgba(0, 255, 127, 0.1) 45deg, rgba(0, 255, 127, 0.4) 90deg, rgba(0, 255, 127, 0.6) 135deg, rgba(0, 255, 127, 0.3) 180deg, transparent 225deg, transparent 360deg)',
          borderRadius: '50%',
          animation: 'radarSweep 4s linear infinite',
          zIndex: 0,
        },
        '@keyframes radarPulse': {
          '0%': { 
            transform: 'translate(-50%, -50%) scale(0.8)',
            opacity: 1,
          },
          '50%': { 
            transform: 'translate(-50%, -50%) scale(1.1)',
            opacity: 0.7,
          },
          '100%': { 
            transform: 'translate(-50%, -50%) scale(0.8)',
            opacity: 1,
          },
        },
        '@keyframes radarSweep': {
          '0%': { 
            transform: 'translate(-50%, -50%) rotate(0deg)',
            opacity: 0.8,
          },
          '100%': { 
            transform: 'translate(-50%, -50%) rotate(360deg)',
            opacity: 0.8,
          },
        },
      }}
    >
      {/* Additional radar circles for depth */}
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '600px',
          height: '600px',
          transform: 'translate(-50%, -50%)',
          border: '1px solid rgba(0, 255, 127, 0.2)',
          borderRadius: '50%',
          animation: 'radarPulse 6s linear infinite 2s',
          zIndex: 0,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '400px',
          height: '400px',
          transform: 'translate(-50%, -50%)',
          border: '1px solid rgba(0, 255, 127, 0.4)',
          borderRadius: '50%',
          animation: 'radarPulse 6s linear infinite 4s',
          zIndex: 0,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '200px',
          height: '200px',
          transform: 'translate(-50%, -50%)',
          border: '2px solid rgba(0, 255, 127, 0.6)',
          borderRadius: '50%',
          animation: 'radarPulse 6s linear infinite 1s',
          zIndex: 0,
        }}
      />
      
      <Card 
        sx={{ 
          width: { xs: '90%', sm: 450 }, 
          borderRadius: 4, 
          overflow: 'visible',
          position: 'relative',
          zIndex: 1,
          background: 'rgba(15, 15, 35, 0.9)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 255, 127, 0.3)',
          boxShadow: '0 25px 45px rgba(0, 0, 0, 0.3), 0 0 30px rgba(0, 255, 127, 0.1)',
          animation: 'slideUp 0.8s ease-out',
          '@keyframes slideUp': {
            '0%': {
              opacity: 0,
              transform: 'translateY(30px) scale(0.95)',
            },
            '100%': {
              opacity: 1,
              transform: 'translateY(0px) scale(1)',
            }
          }
        }}
      >
        {loading && (
          <LinearProgress 
            sx={{ 
              position: 'absolute', 
              top: 0, 
              left: 0, 
              right: 0,
              borderRadius: '16px 16px 0 0'
            }} 
          />
        )}
        
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Box textAlign="center" mb={3}>
            <Typography 
              variant="h4" 
              fontWeight="bold" 
              sx={{ 
                background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1
              }}
            >
              The Watcher
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
              Monitor your websites with confidence
            </Typography>
          </Box>

          {/* Alert */}
          {alert.show && (
            <Alert 
              severity={alert.type} 
              sx={{ mb: 3, borderRadius: 2 }}
              onClose={() => setAlert({ show: false, type: 'info', message: '' })}
            >
              {alert.message}
            </Alert>
          )}

          {/* Content */}
          {showOTP ? (
            <OtpVerifier 
              onVerify={handleVerify} 
              onBack={handleBackToAuth}
              email={pendingEmail}
              loading={loading}
            />
          ) : (
            <>
              <Tabs
                value={tab}
                onChange={(_, newValue) => setTab(newValue)}
                variant="fullWidth"
                sx={{ 
                  mb: 3,
                  '& .MuiTab-root': {
                    textTransform: 'none',
                    fontSize: '1rem',
                    fontWeight: 600,
                    color: 'rgba(255, 255, 255, 0.6)',
                  },
                  '& .Mui-selected': {
                    color: '#00ff7f'
                  },
                  '& .MuiTabs-indicator': {
                    backgroundColor: '#00ff7f',
                    height: 3,
                    borderRadius: '3px 3px 0 0'
                  }
                }}
              >
                <Tab label="Login" />
                <Tab label="Sign Up" />
              </Tabs>
              
              {tab === 0 && <LoginForm onLogin={handleLogin} loading={loading} />}
              {tab === 1 && <SignupForm onSignup={handleSignup} loading={loading} />}
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
