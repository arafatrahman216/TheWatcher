import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline,
  Container,
  Typography, 
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  CircularProgress,
  Chip,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import {
  CheckCircle,
  Error,
  Speed,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2563eb',
      light: '#3b82f6',
      dark: '#1d4ed8',
    },
    secondary: {
      main: '#7c3aed',
      light: '#8b5cf6',
      dark: '#6d28d9',
    },
    success: {
      main: '#059669',
      light: '#10b981',
      dark: '#047857',
    },
    error: {
      main: '#dc2626',
      light: '#ef4444',
      dark: '#b91c1c',
    },
    warning: {
      main: '#d97706',
      light: '#f59e0b',
      dark: '#b45309',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.875rem',
      lineHeight: 1.3,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h6: {
      fontWeight: 500,
      fontSize: '1.125rem',
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          border: '1px solid #e2e8f0',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiCardHeader: {
      styleOverrides: {
        root: {
          padding: '24px 24px 16px 24px',
          '& .MuiCardHeader-title': {
            fontSize: '1.125rem',
            fontWeight: 600,
            color: '#1e293b',
          },
          '& .MuiCardHeader-subheader': {
            fontSize: '0.875rem',
            color: '#64748b',
            marginTop: '4px',
          },
        },
        avatar: {
          marginRight: 16,
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: '0 24px 24px 24px',
          '&:last-child': {
            paddingBottom: 24,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          fontWeight: 500,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 10,
        },
      },
    },
  },
});

const API_BASE_URL = 'http://localhost:8000/api/v1';

const UptimeCard = ({ stats }) => {
  const uptimePercentage = stats ? stats.uptime_percentage : 0;
  const totalChecks = stats ? stats.total_checks : 0;
  const successfulChecks = stats ? stats.successful_checks : 0;
  const avgResponseTime = stats ? stats.average_response_time : 0;
  
  const getUptimeColor = () => {
    if (uptimePercentage >= 99) return 'success';
    if (uptimePercentage >= 95) return 'warning';
    return 'error';
  };

  const getUptimeStatus = () => {
    if (uptimePercentage >= 99.5) return 'Excellent';
    if (uptimePercentage >= 99) return 'Great';
    if (uptimePercentage >= 95) return 'Good';
    if (uptimePercentage >= 90) return 'Fair';
    return 'Poor';
  };
  
  return (
    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <CardHeader 
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CheckCircle sx={{ color: 'white', fontSize: 28 }} />
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              Uptime Overview
            </Typography>
          </Box>
        }
        sx={{ pb: 1 }}
      />
      <CardContent>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography 
            variant="h1" 
            component="div" 
            sx={{ 
              fontWeight: 700, 
              color: 'white',
              fontSize: '3.5rem',
              lineHeight: 1,
              mb: 1
            }}
          >
            {uptimePercentage.toFixed(2)}%
          </Typography>
          <Chip 
            label={getUptimeStatus()} 
            color={getUptimeColor()}
            sx={{ 
              fontSize: '0.875rem',
              fontWeight: 600,
              mb: 2
            }}
          />
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)', mb: 3 }}>
            {successfulChecks} successful of {totalChecks} checks
          </Typography>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              Uptime Progress
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              {uptimePercentage.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={uptimePercentage} 
            sx={{ 
              height: 12, 
              borderRadius: 6,
              backgroundColor: 'rgba(255,255,255,0.2)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: 'white',
                borderRadius: 6,
              }
            }}
          />
        </Box>

        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          backgroundColor: 'rgba(255,255,255,0.1)',
          borderRadius: 2,
          p: 2
        }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              {totalChecks}
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              Total Checks
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              {avgResponseTime.toFixed(0)}ms
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              Avg Response
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const ResponseTimeChart = ({ checks }) => {
  const safeParseDate = (timestamp) => {
    if (!timestamp) return new Date();
    // Handle both formats: with and without 'Z' suffix
    const dateStr = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? new Date() : date;
  };

  // Filter out monitor started incidents and only include checks with response times
  const validChecks = checks ? checks.filter(check => 
    check.response_time && 
    check.response_time > 0 && 
    check.is_up && 
    !check.error_message?.includes('Monitor started')
  ) : [];

  // Take the most recent 20 valid checks and display them (newest to oldest, check 1 = newest)
  const recentChecks = validChecks.reverse();
  const chartData = recentChecks.slice(-20).map((check, index) => {
    const date = safeParseDate(check.timestamp);
    return {
      name: `${index + 1}`,
      responseTime: Math.round(check.response_time),
      timestamp: date.toLocaleTimeString(),
      fullTimestamp: date.toLocaleString()
    };
  });

  const averageResponseTime = chartData.length > 0 
    ? Math.round(chartData.reduce((sum, item) => sum + item.responseTime, 0) / chartData.length)
    : 0;

  const maxResponseTime = chartData.length > 0 
    ? Math.max(...chartData.map(item => item.responseTime))
    : 0;

  return (
    <Card sx={{ height: '500px' }}>
      <CardHeader 
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Speed color="primary" sx={{ fontSize: 28 }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Response Time Analytics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Performance trends over last {chartData.length} checks
              </Typography>
            </Box>
          </Box>
        }
        action={
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="body2" color="text.secondary">
              Avg: {averageResponseTime}ms
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Peak: {maxResponseTime}ms
            </Typography>
          </Box>
        }
        sx={{ pb: 2 }}
      />
      <CardContent sx={{ height: '400px', pt: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="responseTimeGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="name" 
              fontSize={12}
              tick={{ fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <YAxis 
              fontSize={12}
              tick={{ fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
              label={{ 
                value: 'Response Time (ms)', 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle', fill: '#64748b' }
              }}
            />
            <Tooltip 
              labelFormatter={(label, payload) => {
                if (payload && payload[0]) {
                  return `Check ${label} - ${payload[0].payload.fullTimestamp}`;
                }
                return `Check ${label}`;
              }}
              formatter={(value) => [`${value}ms`, 'Response Time']}
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: 12,
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                fontSize: '14px',
              }}
              labelStyle={{ color: '#1e293b', fontWeight: 600 }}
            />
            <Line 
              type="monotone" 
              dataKey="responseTime" 
              stroke="#2563eb" 
              strokeWidth={3}
              fill="url(#responseTimeGradient)"
              dot={{ fill: '#2563eb', strokeWidth: 2, r: 5 }}
              activeDot={{ r: 7, fill: '#2563eb', strokeWidth: 3, stroke: '#ffffff' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

const RecentChecksTimeline = ({ checks }) => {
  const recentChecks = checks ? checks.slice() : [];
  console.log('Recent checks:', recentChecks);
  
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp.endsWith('Z') ? timestamp : timestamp + 'Z');
    return {
      time: date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      }),
      date: date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })
    };
  };
  
  return (
    <Card sx={{ height: '500px' }}>
      <CardHeader 
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <TimelineIcon color="primary" sx={{ fontSize: 28 }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Recent Activity
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All {recentChecks.length} monitoring results
              </Typography>
            </Box>
          </Box>
        }
      />
      <CardContent sx={{ height: '400px', overflow: 'auto', py: 1 }}>
        <Timeline sx={{ p: 0 }}>
          {recentChecks.map((check, index) => {
            const timeInfo = formatTimestamp(check.timestamp);
            return (
              <TimelineItem key={check.id}>
                <TimelineOppositeContent 
                  sx={{ 
                    flex: '0 0 auto', 
                    minWidth: '80px',
                    textAlign: 'right',
                    pr: 2
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    {timeInfo.time}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {timeInfo.date}
                  </Typography>
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot 
                    color={check.is_up ? "success" : "error"}
                    sx={{ 
                      width: 40, 
                      height: 40,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {check.is_up ? <CheckCircle sx={{ fontSize: 20 }} /> : <Error sx={{ fontSize: 20 }} />}
                  </TimelineDot>
                  {index < recentChecks.length - 1 && (
                    <TimelineConnector sx={{ backgroundColor: '#e2e8f0' }} />
                  )}
                </TimelineSeparator>
                <TimelineContent sx={{ pl: 2 }}>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
                      {check.is_up ? 'Site Online' : 'Site Offline'}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                      <Chip 
                        label={`${check.response_time ? Math.round(check.response_time) : 'N/A'}ms`}
                        color={check.is_up ? "success" : "default"}
                        size="small"
                        sx={{ fontSize: '0.75rem' }}
                      />
                      <Chip 
                        label={`HTTP ${check.status_code || 'N/A'}`}
                        color={check.is_up ? "success" : "error"}
                        size="small"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    </Box>
                  </Box>
                  {check.error_message && (
                    <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                      {check.error_message}
                    </Typography>
                  )}
                </TimelineContent>
              </TimelineItem>
            );
          })}
        </Timeline>
        {recentChecks.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No monitoring data available yet
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

const WebsiteInfo = ({ website }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Loading...';
    const date = new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getDomainFromUrl = (url) => {
    if (!url) return 'Loading...';
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  };

  return (
    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Box sx={{ textAlign: 'center' }}>
          <Box sx={{ 
            width: 80, 
            height: 80, 
            borderRadius: '50%', 
            backgroundColor: 'rgba(255,255,255,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px auto'
          }}>
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
              🌐
            </Typography>
          </Box>
          
          <Typography variant="h4" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
            Monitored Website
          </Typography>
          
          <Typography variant="h6" sx={{ 
            color: 'rgba(255,255,255,0.9)', 
            mb: 3,
            wordBreak: 'break-word'
          }}>
            {getDomainFromUrl(website?.url)}
          </Typography>

          <Box sx={{ 
            backgroundColor: 'rgba(255,255,255,0.1)',
            borderRadius: 2,
            p: 2,
            mb: 2
          }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 1 }}>
              Full URL
            </Typography>
            <Typography variant="body1" sx={{ 
              color: 'white', 
              fontWeight: 500,
              wordBreak: 'break-all'
            }}>
              {website?.url || 'Loading...'}
            </Typography>
          </Box>

          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
            Monitoring since {formatDate(website?.created_at)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

function Dashboard() {
  const [website, setWebsite] = useState(null);
  const [stats, setStats] = useState(null);
  const [checks, setChecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch website info
      const websiteResponse = await axios.get(`${API_BASE_URL}/website`);
      setWebsite(websiteResponse.data);

      // Fetch stats
      const statsResponse = await axios.get(`${API_BASE_URL}/stats`);
      setStats(statsResponse.data);

      // Fetch recent checks
      const checksResponse = await axios.get(`${API_BASE_URL}/checks`);
      setChecks(checksResponse.data);

    } catch (err) {
      setError(err.message || 'Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      py: 4
    }}>
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        {/* Header Section */}
        <Box sx={{ mb: 6, textAlign: 'center' }}>
          <Typography 
            variant="h1" 
            component="h1" 
            sx={{ 
              fontWeight: 700, 
              mb: 2,
              color: 'white',
              textShadow: '0 2px 4px rgba(0,0,0,0.3)'
            }}
          >
            🔍 Website Monitor
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              mb: 3, 
              fontWeight: 400,
              color: 'rgba(255,255,255,0.9)',
              maxWidth: 600,
              margin: '0 auto 24px auto'
            }}
          >
            Real-time monitoring dashboard for website uptime, performance, and reliability analytics
          </Typography>
          
          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mt: 2, 
                borderRadius: 3,
                maxWidth: 600,
                margin: '16px auto 0 auto',
                backgroundColor: 'rgba(255,255,255,0.95)',
                '& .MuiAlert-icon': {
                  color: '#d32f2f'
                }
              }}
            >
              {error}
            </Alert>
          )}
        </Box>

        {/* Main Dashboard */}
        <Box sx={{ 
          backgroundColor: 'rgba(255,255,255,0.95)', 
          borderRadius: 4, 
          p: 4,
          backdropFilter: 'blur(10px)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
        }}>
          <Grid container spacing={4}>
            {/* Website Info */}
            <Grid item xs={12} lg={4}>
              <WebsiteInfo website={website} />
            </Grid>

            {/* Uptime Stats */}
            <Grid item xs={12} lg={8}>
              <UptimeCard stats={stats} />
            </Grid>

            {/* Response Time Chart */}
            <Grid item xs={12} lg={7}>
              <ResponseTimeChart checks={checks} />
            </Grid>

            {/* Recent Checks Timeline */}
            <Grid item xs={12} lg={5}>
              <RecentChecksTimeline checks={checks} />
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Dashboard />
    </ThemeProvider>
  );
}

// Render the app
const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
