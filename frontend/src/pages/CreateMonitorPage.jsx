import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Language,
  Schedule,
  ArrowBack,
  CheckCircle,
  Speed,
  Notifications,
  Security,
  Timeline,
  Add,
  Visibility,
  Edit,
} from '@mui/icons-material';
import { API_BASE_URL, apiHelpers } from '../api';

const CreateMonitorPage = ({ user }) => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    sitename: '',
    site_url: '',
    interval: 300, // 5 minutes default
    monitor_type: 'http',
  });

  const steps = ['Website Details', 'Monitoring Settings', 'Review & Create'];

  const intervalOptions = [
    { value: 60, label: '1 minute', description: 'Frequent checks (Premium)' },
    { value: 300, label: '5 minutes', description: 'Standard monitoring' },
    { value: 600, label: '10 minutes', description: 'Regular checks' },
    { value: 1800, label: '30 minutes', description: 'Basic monitoring' },
    { value: 3600, label: '1 hour', description: 'Minimal checks' },
  ];

  const validateStep = (step) => {
    switch (step) {
      case 0:
        if (!formData.sitename.trim()) {
          setError('Site name is required');
          return false;
        }
        if (!formData.site_url.trim()) {
          setError('Site URL is required');
          return false;
        }
        if (!isValidUrl(formData.site_url)) {
          setError('Please enter a valid URL');
          return false;
        }
        break;
      case 1:
        if (!formData.interval) {
          setError('Monitoring interval is required');
          return false;
        }
        break;
      default:
        break;
    }
    setError('');
    return true;
  };

  const isValidUrl = (string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    setError('');
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');
  };

  const handleSubmit = async () => {
    if (!validateStep(activeStep)) return;

    setLoading(true);
    try {
      // Debug user object to understand its structure
      console.log('User object:', user);
      
      // Ensure we have a valid user ID
      const userId = user?.id || user?.user_id || user?.userId;
      if (!userId) {
        setError('User ID not found. Please login again.');
        setLoading(false);
        return;
      }

      // Validate all required fields are present
      if (!formData.sitename || !formData.sitename.trim()) {
        setError('Site name is required and cannot be empty');
        setLoading(false);
        return;
      }

      if (!formData.site_url || !formData.site_url.trim()) {
        setError('Site URL is required and cannot be empty');
        setLoading(false);
        return;
      }

      if (!formData.interval || formData.interval <= 0) {
        setError('Valid monitoring interval is required');
        setLoading(false);
        return;
      }

      // Validate URL format
      if (!formData.site_url.startsWith('http://') && !formData.site_url.startsWith('https://')) {
        setError('URL must start with http:// or https://');
        setLoading(false);
        return;
      }

      // First, test if the API endpoint is reachable
      try {
        const testResponse = await fetch(`${API_BASE_URL}/monitors/hi`);
        const testData = await testResponse.json();
        console.log('Test endpoint response:', testData);
      } catch (testErr) {
        console.error('Test endpoint failed:', testErr);
        setError('Cannot connect to the monitor service. Please check if the backend is running.');
        setLoading(false);
        return;
      }

      const requestData = {
        user_id: parseInt(userId), // Ensure it's a number
        monitor: {
          sitename: formData.sitename.trim(),
          site_url: formData.site_url.trim(),
          monitor_created: new Date().toISOString(), // Keep full ISO timestamp
          interval: parseInt(formData.interval), // Ensure it's a number
        }
      };

      console.log('Request data:', requestData);

      // First test with debug endpoint to see what backend receives
      try {
        const debugResponse = await fetch(`${API_BASE_URL}/monitors/debug`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
        
        const debugData = await debugResponse.json();
        console.log('Debug endpoint response:', debugData);
      } catch (debugErr) {
        console.error('Debug request failed:', debugErr);
      }

      const response = await fetch(`${API_BASE_URL}/monitors/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      console.log('Response status:', response.status);
      
      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/');
        }, 2000);
      } else {
        // Handle different types of error responses using utility function
        const errorMessage = apiHelpers.formatError(data.detail) || 'Failed to create monitor';
        setError(errorMessage);
      }
    } catch (err) {
      console.error('Create monitor error:', err);
      const errorMessage = apiHelpers.formatError(err) || 'Network error. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" color="#00ff7f" mb={2} fontWeight="600">
                🌐 Website Information
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Website Name"
                fullWidth
                value={formData.sitename}
                onChange={(e) => handleInputChange('sitename', e.target.value)}
                placeholder="e.g., My Portfolio Website"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Edit sx={{ color: 'rgba(255, 255, 255, 0.5)' }} />
                    </InputAdornment>
                  ),
                }}
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
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Website URL"
                fullWidth
                value={formData.site_url}
                onChange={(e) => handleInputChange('site_url', e.target.value)}
                placeholder="https://example.com"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Language sx={{ color: 'rgba(255, 255, 255, 0.5)' }} />
                    </InputAdornment>
                  ),
                }}
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
              />
            </Grid>

            <Grid item xs={12}>
              <Box 
                sx={{
                  p: 2,
                  border: '1px solid rgba(0, 255, 127, 0.3)',
                  borderRadius: 2,
                  backgroundColor: 'rgba(0, 255, 127, 0.05)',
                }}
              >
                <Typography variant="body2" color="#00ff7f" fontWeight="500" mb={1}>
                  💡 URL Guidelines:
                </Typography>
                <Box component="ul" sx={{ color: 'rgba(255, 255, 255, 0.7)', pl: 2, margin: 0 }}>
                  <li>Must include protocol (http:// or https://)</li>
                  <li>Can monitor any publicly accessible website</li>
                  <li>Supports subdomains and specific pages</li>
                  <li>Examples: https://mysite.com, https://blog.mysite.com/page</li>
                </Box>
              </Box>
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" color="#00ff7f" mb={2} fontWeight="600">
                ⚙️ Monitoring Configuration
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Check Interval
                </InputLabel>
                <Select
                  value={formData.interval}
                  onChange={(e) => handleInputChange('interval', e.target.value)}
                  MenuProps={{
                    PaperProps: {
                      sx: {
                        backgroundColor: 'rgba(15, 15, 35, 0.95)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid rgba(0, 255, 127, 0.2)',
                        borderRadius: 2,
                        '& .MuiMenuItem-root': {
                          color: '#ffffff',
                          '&:hover': {
                            backgroundColor: 'rgba(0, 255, 127, 0.1)',
                          },
                          '&.Mui-selected': {
                            backgroundColor: 'rgba(0, 255, 127, 0.2)',
                            '&:hover': {
                              backgroundColor: 'rgba(0, 255, 127, 0.3)',
                            },
                          },
                        },
                      },
                    },
                  }}
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(0, 255, 127, 0.3)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(0, 255, 127, 0.5)',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#00ff7f',
                    },
                    '& .MuiSelect-select': {
                      color: '#ffffff',
                    },
                    '& .MuiSvgIcon-root': {
                      color: 'rgba(255, 255, 255, 0.5)',
                    },
                  }}
                  startAdornment={
                    <InputAdornment position="start">
                      <Schedule sx={{ color: 'rgba(255, 255, 255, 0.5)' }} />
                    </InputAdornment>
                  }
                >
                  {intervalOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      <Box>
                        <Typography variant="body1" color="#ffffff">
                          {option.label}
                        </Typography>
                        <Typography variant="body2" color="rgba(255, 255, 255, 0.6)">
                          {option.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card sx={{ 
                    backgroundColor: 'rgba(0, 255, 127, 0.1)', 
                    border: '1px solid rgba(0, 255, 127, 0.3)',
                    height: '100%',
                  }}>
                    <CardContent>
                      <Speed sx={{ color: '#00ff7f', mb: 1 }} />
                      <Typography variant="h6" color="#ffffff" fontWeight="600">
                        Performance
                      </Typography>
                      <Typography variant="body2" color="rgba(255, 255, 255, 0.7)">
                        Response time tracking and performance metrics
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Card sx={{ 
                    backgroundColor: 'rgba(0, 255, 127, 0.1)', 
                    border: '1px solid rgba(0, 255, 127, 0.3)',
                    height: '100%',
                  }}>
                    <CardContent>
                      <Notifications sx={{ color: '#00ff7f', mb: 1 }} />
                      <Typography variant="h6" color="#ffffff" fontWeight="600">
                        Alerts
                      </Typography>
                      <Typography variant="body2" color="rgba(255, 255, 255, 0.7)">
                        Instant notifications when your site goes down
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Card sx={{ 
                    backgroundColor: 'rgba(0, 255, 127, 0.1)', 
                    border: '1px solid rgba(0, 255, 127, 0.3)',
                    height: '100%',
                  }}>
                    <CardContent>
                      <Timeline sx={{ color: '#00ff7f', mb: 1 }} />
                      <Typography variant="h6" color="#ffffff" fontWeight="600">
                        History
                      </Typography>
                      <Typography variant="body2" color="rgba(255, 255, 255, 0.7)">
                        Complete uptime history and incident logs
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" color="#00ff7f" mb={2} fontWeight="600">
                📋 Review Your Monitor
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Card sx={{ 
                backgroundColor: 'rgba(0, 255, 127, 0.05)', 
                border: '1px solid rgba(0, 255, 127, 0.3)' 
              }}>
                <CardContent>
                  <Box mb={2}>
                    <Typography variant="h5" color="#ffffff" fontWeight="600">
                      {formData.sitename}
                    </Typography>
                    <Typography variant="body1" color="#00ff7f" mt={1}>
                      {formData.site_url}
                    </Typography>
                  </Box>

                  <Divider sx={{ borderColor: 'rgba(0, 255, 127, 0.2)', my: 2 }} />

                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="rgba(255, 255, 255, 0.7)">
                        Check Interval:
                      </Typography>
                      <Typography variant="body1" color="#ffffff" fontWeight="500">
                        {intervalOptions.find(opt => opt.value === formData.interval)?.label}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="rgba(255, 255, 255, 0.7)">
                        Monitor Type:
                      </Typography>
                      <Typography variant="body1" color="#ffffff" fontWeight="500">
                        HTTP/HTTPS Website
                      </Typography>
                    </Grid>
                  </Grid>

                  <Box mt={3}>
                    <Typography variant="body2" color="rgba(255, 255, 255, 0.7)" mb={1}>
                      What happens next:
                    </Typography>
                    <Box component="ul" sx={{ color: 'rgba(255, 255, 255, 0.8)', pl: 2, margin: 0 }}>
                      <li>Monitor will be created and activated immediately</li>
                      <li>First check will happen within the next minute</li>
                      <li>You'll receive alerts if the site becomes unavailable</li>
                      <li>Performance data will be collected and displayed in your dashboard</li>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  if (success) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Container maxWidth="md" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
          <Box textAlign="center">
            <CheckCircle sx={{ fontSize: '4rem', color: '#00ff7f', mb: 2 }} />
            <Typography variant="h4" color="#ffffff" fontWeight="600" mb={2}>
              Monitor Created Successfully! 🎉
            </Typography>
            <Typography variant="body1" color="rgba(255, 255, 255, 0.7)" mb={3}>
              Your website monitor for "{formData.sitename}" is now active and monitoring.
            </Typography>
            <Box 
              sx={{
                display: 'inline-block',
                px: 3,
                py: 1,
                border: '1px solid #00ff7f',
                borderRadius: 2,
                backgroundColor: 'rgba(0, 255, 127, 0.1)',
              }}
            >
              <Typography variant="body2" color="#00ff7f">
                Redirecting to dashboard...
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Container maxWidth="md" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <Box mb={4}>
          <Box display="flex" alignItems="center" mb={2}>
            <IconButton 
              onClick={() => navigate('/')}
              sx={{ color: '#ffffff', mr: 2 }}
            >
              <ArrowBack />
            </IconButton>
            <Typography variant="h4" color="#ffffff" fontWeight="600">
              Create New Monitor
            </Typography>
          </Box>
          <Typography variant="body1" color="rgba(255, 255, 255, 0.7)">
            Set up monitoring for your website to track uptime and performance
          </Typography>
        </Box>

      {/* Stepper */}
      <Paper 
        sx={{ 
          p: 3, 
          mb: 4,
          background: 'rgba(15, 15, 35, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 255, 127, 0.2)',
          borderRadius: 3,
        }}
      >
        <Stepper 
          activeStep={activeStep} 
          sx={{
            '& .MuiStepLabel-label': {
              color: 'rgba(255, 255, 255, 0.7)',
              '&.Mui-active': {
                color: '#00ff7f',
              },
              '&.Mui-completed': {
                color: '#00ff7f',
              },
            },
            '& .MuiStepIcon-root': {
              color: 'rgba(255, 255, 255, 0.3)',
              '&.Mui-active': {
                color: '#00ff7f',
              },
              '&.Mui-completed': {
                color: '#00ff7f',
              },
            },
          }}
        >
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Content */}
      <Paper 
        sx={{ 
          p: 4,
          background: 'rgba(15, 15, 35, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 255, 127, 0.2)',
          borderRadius: 3,
        }}
      >
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3,
              backgroundColor: 'rgba(255, 68, 68, 0.1)',
              border: '1px solid rgba(255, 68, 68, 0.3)',
              color: '#ff4444',
            }}
          >
            {error}
          </Alert>
        )}

        {renderStepContent(activeStep)}

        {/* Navigation Buttons */}
        <Box display="flex" justifyContent="space-between" mt={4}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            variant="outlined"
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.3)',
              color: '#ffffff',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.5)',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
              },
              '&:disabled': {
                borderColor: 'rgba(255, 255, 255, 0.1)',
                color: 'rgba(255, 255, 255, 0.3)',
              },
            }}
          >
            Back
          </Button>

          {activeStep === steps.length - 1 ? (
            <Button
              onClick={handleSubmit}
              disabled={loading}
              variant="contained"
              startIcon={<Add />}
              sx={{
                background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
                color: '#000000',
                fontWeight: 600,
                px: 4,
                '&:hover': {
                  background: 'linear-gradient(45deg, #00cc64, #00a050)',
                },
                '&:disabled': {
                  background: '#333333',
                  color: '#666666',
                },
              }}
            >
              {loading ? 'Creating Monitor...' : 'Create Monitor'}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              variant="contained"
              sx={{
                background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
                color: '#000000',
                fontWeight: 600,
                '&:hover': {
                  background: 'linear-gradient(45deg, #00cc64, #00a050)',
                },
              }}
            >
              Next
            </Button>
          )}
        </Box>
      </Paper>
      </Container>
    </Box>
  );
};

export default CreateMonitorPage;
