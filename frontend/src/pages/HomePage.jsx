import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Card,
  CardContent,
  Avatar,
  Grid,
  Divider,
  Button,
  Alert,
  TablePagination,
} from '@mui/material';
import {
  Language,
  CheckCircle,
  Cancel,
  Visibility,
  Edit,
  Delete,
  Add,
  Person,
  Notifications,
  Security,
  Speed,
} from '@mui/icons-material';
import { API_BASE_URL } from '../api';
import axios from 'axios';

const HomePage = ({ user, onLogout, onNavigate }) => {
  const [monitors, setMonitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    fetchMonitors();
  }, []);

  const fetchMonitors = async () => {
    try {
      setLoading(true);
      // Replace with actual API endpoint when available
      const response = await axios.get(`${API_BASE_URL}/monitors`);
      setMonitors(response.data || []);
    } catch (err) {
      console.error('Error fetching monitors:', err);
      // Mock data for demonstration
      setMonitors([
        {
          monitorid: 1,
          sitename: 'Personal Portfolio',
          site_url: 'https://myportfolio.com',
          monitor_created: '2024-01-15',
          is_active: true,
          last_checked: '2024-08-30T10:30:00Z',
          status: 'online'
        },
        {
          monitorid: 2,
          sitename: 'E-commerce Store',
          site_url: 'https://mystore.com',
          monitor_created: '2024-02-20',
          is_active: true,
          last_checked: '2024-08-30T10:25:00Z',
          status: 'online'
        },
        {
          monitorid: 3,
          sitename: 'Blog Website',
          site_url: 'https://myblog.com',
          monitor_created: '2024-03-10',
          is_active: false,
          last_checked: '2024-08-29T22:15:00Z',
          status: 'offline'
        },
        {
          monitorid: 4,
          sitename: 'API Service',
          site_url: 'https://api.myservice.com',
          monitor_created: '2024-04-05',
          is_active: true,
          last_checked: '2024-08-30T10:28:00Z',
          status: 'warning'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return '#00ff7f';
      case 'offline': return '#ff4444';
      case 'warning': return '#ffaa00';
      default: return '#666666';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatLastChecked = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const userStats = {
    totalMonitors: monitors.length,
    activeMonitors: monitors.filter(m => m.is_active).length,
    onlineMonitors: monitors.filter(m => m.status === 'online').length,
    memberSince: '2024-01-01'
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        position: 'relative',
        overflow: 'hidden',
        // Radar animation background
        '&::before': {
          content: '""',
          position: 'fixed',
          top: '50%',
          left: '50%',
          width: '1200px',
          height: '1200px',
          transform: 'translate(-50%, -50%)',
          border: '1px solid rgba(0, 255, 127, 0.1)',
          borderRadius: '50%',
          animation: 'radarPulse 8s linear infinite',
          zIndex: 0,
        },
        '&::after': {
          content: '""',
          position: 'fixed',
          top: '50%',
          left: '50%',
          width: '1200px',
          height: '1200px',
          transform: 'translate(-50%, -50%)',
          background: 'conic-gradient(from 0deg, transparent 0deg, rgba(0, 255, 127, 0.05) 45deg, rgba(0, 255, 127, 0.2) 90deg, rgba(0, 255, 127, 0.1) 135deg, transparent 180deg, transparent 360deg)',
          borderRadius: '50%',
          animation: 'radarSweep 6s linear infinite',
          zIndex: 0,
        },
        '@keyframes radarPulse': {
          '0%': { 
            transform: 'translate(-50%, -50%) scale(0.8)',
            opacity: 0.6,
          },
          '50%': { 
            transform: 'translate(-50%, -50%) scale(1.2)',
            opacity: 0.3,
          },
          '100%': { 
            transform: 'translate(-50%, -50%) scale(0.8)',
            opacity: 0.6,
          },
        },
        '@keyframes radarSweep': {
          '0%': { 
            transform: 'translate(-50%, -50%) rotate(0deg)',
          },
          '100%': { 
            transform: 'translate(-50%, -50%) rotate(360deg)',
          },
        },
      }}
    >
      <Container maxWidth="xl" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box>
              <Typography 
                variant="h3" 
                sx={{ 
                  color: '#ffffff', 
                  fontWeight: 700,
                  background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                The Watcher
              </Typography>
              <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)', mt: 1 }}>
                Your Website Monitoring Solution 
              </Typography>
            </Box>
            <Button
              variant="outlined"
              onClick={onLogout}
              sx={{
                color: '#00ff7f',
                borderColor: '#00ff7f',
                '&:hover': {
                  borderColor: '#00cc64',
                  backgroundColor: 'rgba(0, 255, 127, 0.1)',
                },
              }}
            >
              Logout
            </Button>
          </Box>

          {/* User Profile Card */}
          <Card
            sx={{
              background: 'rgba(15, 15, 35, 0.8)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(0, 255, 127, 0.2)',
              borderRadius: 3,
              mb: 4,
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Grid container spacing={3} alignItems="center">
                <Grid item>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
                      color: '#000000',
                      fontSize: '2rem',
                      fontWeight: 'bold',
                    }}
                  >
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </Avatar>
                </Grid>
                <Grid item xs>
                  <Typography variant="h5" sx={{ color: '#ffffff', fontWeight: 600, mb: 1 }}>
                    Welcome back, {user?.name || 'User'}
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
                    {user?.email || 'user@example.com'}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Chip
                      icon={<Language />}
                      label={`${userStats.totalMonitors} Monitors`}
                      sx={{
                        backgroundColor: 'rgba(0, 255, 127, 0.1)',
                        color: '#00ff7f',
                        border: '1px solid rgba(0, 255, 127, 0.3)',
                      }}
                    />
                    <Chip
                      icon={<CheckCircle />}
                      label={`${userStats.activeMonitors} Active`}
                      sx={{
                        backgroundColor: 'rgba(0, 255, 127, 0.1)',
                        color: '#00ff7f',
                        border: '1px solid rgba(0, 255, 127, 0.3)',
                      }}
                    />
                    <Chip
                      icon={<Security />}
                      label={`${userStats.onlineMonitors} Online`}
                      sx={{
                        backgroundColor: 'rgba(0, 255, 127, 0.1)',
                        color: '#00ff7f',
                        border: '1px solid rgba(0, 255, 127, 0.3)',
                      }}
                    />
                  </Box>
                </Grid>
                <Grid item>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    sx={{
                      background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
                      color: '#000000',
                      fontWeight: 600,
                      px: 3,
                      py: 1.5,
                      '&:hover': {
                        background: 'linear-gradient(45deg, #00cc64, #00a050)',
                      },
                    }}
                  >
                    Add Monitor
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>

        {/* Monitors Table */}
        <Card
          sx={{
            background: 'rgba(15, 15, 35, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(0, 255, 127, 0.2)',
            borderRadius: 3,
          }}
        >
          <CardContent sx={{ p: 0 }}>
            <Box sx={{ p: 3, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
              <Typography variant="h5" sx={{ color: '#ffffff', fontWeight: 600 }}>
                Your Monitors
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mt: 1 }}>
                Manage and monitor all your tracked websites
              </Typography>
            </Box>

            {error && (
              <Alert
                severity="error"
                sx={{
                  m: 3,
                  backgroundColor: 'rgba(255, 68, 68, 0.1)',
                  color: '#ff4444',
                  border: '1px solid rgba(255, 68, 68, 0.3)',
                }}
              >
                {error}
              </Alert>
            )}

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
                      Monitor ID
                    </TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
                      Website
                    </TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
                      URL
                    </TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
                      Status
                    </TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
                      Created
                    </TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
                      Interval
                    </TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 600, borderBottom: '1px solid rgba(0, 255, 127, 0.1)' }}>
                      Actions
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {monitors
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((monitor) => (
                      <TableRow
                        key={monitor.monitorid}
                        sx={{
                          '&:hover': {
                            backgroundColor: 'rgba(0, 255, 127, 0.05)',
                          },
                          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                        }}
                      >
                        <TableCell sx={{ color: '#ffffff', fontWeight: 500 }}>
                          {monitor.id}  
                        </TableCell>
                        <TableCell sx={{ color: '#ffffff', fontWeight: 500 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Language sx={{ color: '#00ff7f', fontSize: 20 }} />
                            {monitor.friendlyName}
                          </Box>
                        </TableCell>
                        <TableCell sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          {monitor.url}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={monitor.status.toUpperCase()}
                            size="small"
                            sx={{
                              backgroundColor: `${getStatusColor(monitor.status)}20`,
                              color: getStatusColor(monitor.status),
                              border: `1px solid ${getStatusColor(monitor.status)}40`,
                              fontWeight: 600,
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          {formatDate(monitor.createDateTime)}
                        </TableCell>
                        <TableCell sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          {(monitor.interval)}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                              size="small"
                              onClick={() => onNavigate('dashboard')}
                              sx={{
                                color: '#00ff7f',
                                '&:hover': {
                                  backgroundColor: 'rgba(0, 255, 127, 0.1)',
                                },
                              }}
                            >
                              <Visibility fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              sx={{
                                color: '#ffaa00',
                                '&:hover': {
                                  backgroundColor: 'rgba(255, 170, 0, 0.1)',
                                },
                              }}
                            >
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              sx={{
                                color: '#ff4444',
                                '&:hover': {
                                  backgroundColor: 'rgba(255, 68, 68, 0.1)',
                                },
                              }}
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={monitors.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                borderTop: '1px solid rgba(0, 255, 127, 0.1)',
                '& .MuiTablePagination-selectIcon': {
                  color: 'rgba(255, 255, 255, 0.7)',
                },
                '& .MuiTablePagination-select': {
                  color: 'rgba(255, 255, 255, 0.7)',
                },
              }}
            />
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default HomePage;
