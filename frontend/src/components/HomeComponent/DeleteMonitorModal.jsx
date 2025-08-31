import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Box,
  IconButton,
  InputAdornment,
  Alert,
  Divider,
  Chip,
} from '@mui/material';
import {
  Close,
  Visibility,
  VisibilityOff,
  Warning,
  Delete,
  Email,
  Lock,
} from '@mui/icons-material';

const DeleteMonitorModal = ({ 
  open, 
  onClose, 
  monitor, 
  user, 
  onDelete 
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1); // 1: verification, 2: confirmation

  const handleVerification = async () => {
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    if (email !== user?.email) {
      setError('Email does not match your account');
      return;
    }

    setLoading(true);
    try {
      // Verify credentials by attempting login
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        setError('');
        setStep(2);
      } else {
        setError('Invalid credentials. Please check your email and password.');
      }
    } catch (err) {
      setError('Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
        console.log('Deleting monitor with ID:', monitor.id, 'for user ID:', user.id);
      await onDelete(monitor.id, user.id);
      onClose();
      resetModal();
    } catch (err) {
      setError('Failed to delete monitor. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetModal = () => {
    setEmail('');
    setPassword('');
    setError('');
    setStep(1);
    setShowPassword(false);
  };

  const handleClose = () => {
    resetModal();
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: '#1a1a2e',
          border: '1px solid rgba(0, 255, 127, 0.3)',
          borderRadius: '15px',
          boxShadow: '0 8px 32px rgba(0, 255, 127, 0.2)',
        }
      }}
    >
      <DialogTitle
        sx={{
          background: 'linear-gradient(135deg, #0f0f23 0%, #16213e 100%)',
          color: '#ffffff',
          borderBottom: '1px solid rgba(0, 255, 127, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          pb: 2,
        }}
      >
        <Box display="flex" alignItems="center" gap={2}>
          <Warning sx={{ color: '#ff6b6b', fontSize: '1.5rem' }} />
          <Typography variant="h6" fontWeight="600">
            Delete Monitor
          </Typography>
        </Box>
        <IconButton onClick={handleClose} sx={{ color: '#ffffff' }}>
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 3, backgroundColor: '#16213e' }}>
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 2, 
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              border: '1px solid #ff6b6b',
              color: '#ff6b6b',
              '& .MuiAlert-icon': {
                color: '#ff6b6b',
              }
            }}
          >
            {error}
          </Alert>
        )}

        {monitor && (
          <Box mb={3}>
            <Typography variant="body2" color="rgba(255, 255, 255, 0.7)" mb={1}>
              Monitor to be deleted:
            </Typography>
            <Box 
              sx={{
                p: 2,
                border: '1px solid rgba(255, 107, 107, 0.3)',
                borderRadius: 2,
                backgroundColor: 'rgba(255, 107, 107, 0.05)',
              }}
            >
              <Typography variant="h6" color="#ffffff" fontWeight="600">
                {monitor.sitename}
              </Typography>
              <Typography variant="body2" color="rgba(255, 255, 255, 0.7)">
                {monitor.site_url}
              </Typography>
              <Box mt={1}>
                <Chip
                  label={monitor.is_active ? 'Active' : 'Inactive'}
                  size="small"
                  sx={{
                    backgroundColor: monitor.is_active ? 'rgba(0, 255, 127, 0.2)' : 'rgba(255, 107, 107, 0.2)',
                    color: monitor.is_active ? '#00ff7f' : '#ff6b6b',
                    border: `1px solid ${monitor.is_active ? '#00ff7f' : '#ff6b6b'}`,
                  }}
                />
              </Box>
            </Box>
          </Box>
        )}

        {step === 1 && (
          <Box>
            <Typography variant="body1" color="#ffffff" mb={2} fontWeight="500">
              🔐 Please verify your identity to continue
            </Typography>
            <Typography variant="body2" color="rgba(255, 255, 255, 0.7)" mb={3}>
              For security reasons, please enter your email and password to confirm this action.
            </Typography>

            <TextField
              label="Email Address"
              type="email"
              fullWidth
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              sx={{
                mb: 2,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  '& fieldset': {
                    borderColor: 'rgba(0, 255, 127, 0.3)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(0, 255, 127, 0.5)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#00ff7f',
                  },
                },
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&.Mui-focused': {
                    color: '#00ff7f',
                  },
                },
                '& .MuiOutlinedInput-input': {
                  color: '#ffffff',
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email sx={{ color: 'rgba(255, 255, 255, 0.5)' }} />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              label="Password"
              type={showPassword ? 'text' : 'password'}
              fullWidth
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  '& fieldset': {
                    borderColor: 'rgba(0, 255, 127, 0.3)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(0, 255, 127, 0.5)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#00ff7f',
                  },
                },
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&.Mui-focused': {
                    color: '#00ff7f',
                  },
                },
                '& .MuiOutlinedInput-input': {
                  color: '#ffffff',
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock sx={{ color: 'rgba(255, 255, 255, 0.5)' }} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      disabled={loading}
                      sx={{ color: 'rgba(255, 255, 255, 0.5)' }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        )}

        {step === 2 && (
          <Box>
            <Typography variant="body1" color="#ffffff" mb={2} fontWeight="500">
              ⚠️ Final Confirmation
            </Typography>
            <Typography variant="body2" color="rgba(255, 255, 255, 0.7)" mb={3}>
              Are you absolutely sure you want to delete this monitor? This action cannot be undone.
            </Typography>
            
            <Box 
              sx={{
                p: 2,
                border: '1px solid #ff6b6b',
                borderRadius: 2,
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
              }}
            >
              <Typography variant="body2" color="#ff6b6b" fontWeight="500">
                ⚠️ This will permanently:
              </Typography>
              <Box component="ul" sx={{ color: '#ff6b6b', pl: 2, mt: 1 }}>
                <li>Remove the monitor from your dashboard</li>
                <li>Stop all monitoring for this website</li>
                <li>Delete all historical data</li>
                <li>Cancel any active alerts</li>
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions 
        sx={{ 
          p: 3, 
          backgroundColor: '#0f0f23',
          borderTop: '1px solid rgba(0, 255, 127, 0.2)',
          gap: 2,
        }}
      >
        <Button 
          onClick={handleClose}
          variant="outlined"
          sx={{
            borderColor: 'rgba(255, 255, 255, 0.3)',
            color: '#ffffff',
            '&:hover': {
              borderColor: 'rgba(255, 255, 255, 0.5)',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
            },
          }}
        >
          Cancel
        </Button>
        
        {step === 1 && (
          <Button
            onClick={handleVerification}
            disabled={loading || !email || !password}
            variant="contained"
            sx={{
              background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
              color: '#000000',
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(45deg, #00cc64, #00a050)',
              },
              '&:disabled': {
                background: '#333333',
                color: '#666666',
              },
            }}
          >
            {loading ? 'Verifying...' : 'Verify & Continue'}
          </Button>
        )}

        {step === 2 && (
          <Button
            onClick={handleDelete}
            disabled={loading}
            variant="contained"
            startIcon={<Delete />}
            sx={{
              background: 'linear-gradient(45deg, #ff6b6b, #ff5252)',
              color: '#ffffff',
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(45deg, #ff5252, #f44336)',
              },
              '&:disabled': {
                background: '#333333',
                color: '#666666',
              },
            }}
          >
            {loading ? 'Deleting...' : 'Delete Monitor'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default DeleteMonitorModal;
