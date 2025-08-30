
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ThemeProvider, CssBaseline, Container, Typography, Box, Grid, Alert, AppBar, Toolbar, Button } from '@mui/material';
import { API_BASE_URL } from '../api';



import UptimeCard from '../components/DashboardComponents/UptimeCard';
import ResponseTimeChart from '../components/DashboardComponents/ResponseTimeChart';
import RecentChecksTimeline from '../components/DashboardComponents/RecentChecksTimeline';
import WebsiteInfo from '../components/DashboardComponents/WebsiteInfo';
import SSLCertCard from '../components/DashboardComponents/SSLCertCard';
import BrokenLinkScanner from '../components/DashboardComponents/BrokenLinkScanner';
import PerformanceCard from '../components/DashboardComponents/PerformanceCard';

import CircularProgress from '@mui/material/CircularProgress';



function Dashboard({ user, onLogout, selectedMonitor }) {

  const [website, setWebsite] = useState(null);
  const [stats, setStats] = useState(null);
  const [checks, setChecks] = useState([]);
  const [sslCert, setSSLCert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const updateStateIfChanged = (setter, newData, oldData) => {
    if (JSON.stringify(newData) !== JSON.stringify(oldData)) setter(newData);
  };

  const fetchData = async () => {
    try {
      setError(null);
      // If a specific monitor is selected, fetch data for that monitor
      const monitorParam = selectedMonitor ? `?monitor=${selectedMonitor.monitorid}` : '';
      const [websiteResponse, statsResponse, checksResponse, sslCertResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/website${monitorParam}`),
        axios.get(`${API_BASE_URL}/stats${monitorParam}`),
        axios.get(`${API_BASE_URL}/checks${monitorParam}`),
        axios.get(`${API_BASE_URL}/ssl-cert${monitorParam}`),
      ]);
      updateStateIfChanged(setWebsite, websiteResponse.data, website);
      updateStateIfChanged(setStats, statsResponse.data, stats);
      updateStateIfChanged(setChecks, checksResponse.data, checks);
      updateStateIfChanged(setSSLCert, sslCertResponse.data, sslCert);
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
      setLoading(false);
      console.error('Error fetching data:', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [selectedMonitor]); // Re-fetch when selected monitor changes

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)', py: 4 }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
          <Box sx={{ mb: 6, textAlign: 'center' }}>
            <Typography
              variant="h1"
              component="h1"
              sx={{ fontWeight: 700, mb: 2, color: 'white', textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}
            >
              🔍 {selectedMonitor ? `${selectedMonitor.sitename} Dashboard` : 'Website Monitor'}
            </Typography>
            <Typography
              variant="h6"
              sx={{
                mb: 3,
                fontWeight: 400,
                color: 'rgba(255,255,255,0.9)',
                maxWidth: 600,
                margin: '0 auto 24px auto',
              }}
            >
              {selectedMonitor 
                ? `Real-time monitoring dashboard for ${selectedMonitor.site_url}` 
                : 'Real-time monitoring dashboard for website uptime, performance, reliability — plus broken link scans'
              }
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
                  '& .MuiAlert-icon': { color: '#d32f2f' },
                }}
              >
                {error}
              </Alert>
            )}
          </Box>

          <Box
            sx={{
              backgroundColor: 'rgba(15, 15, 35, 0.9)',
              borderRadius: 4,
              p: 4,
              backdropFilter: 'blur(10px)',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              border: '1px solid rgba(0, 255, 127, 0.3)',
            }}
          >
            <Grid container spacing={4}>
              {/* Top row (3) */}
              <Grid item xs={12} md={4} lg={4}>
                <WebsiteInfo website={website} />
              </Grid>
              <Grid item xs={12} md={4} lg={4}>
                <SSLCertCard cert={sslCert} />
              </Grid>
              <Grid item xs={12} md={4} lg={4}>
                <UptimeCard stats={stats} />
              </Grid>

              {/* Middle row (2) */}
              <Grid item xs={12} md={6} lg={6}>
                <RecentChecksTimeline checks={checks} />
              </Grid>
              <Grid item xs={12} md={6} lg={6}>
                <ResponseTimeChart checks={checks} />
              </Grid>

              {/* Fourth row: Performance metrics */}
              <Grid item xs={12} md={6} lg={6}>
                <PerformanceCard url={website?.url} strategy="mobile" />
              </Grid>
              <Grid item xs={12} md={6} lg={6}>
                <PerformanceCard url={website?.url} strategy="desktop" />
              </Grid>

              {/* Fifth row: Broken Link Scanner (full width) */}
              <Grid item xs={12}>
                <BrokenLinkScanner defaultRoot={website?.url || ""} />
              </Grid>
            </Grid>
          </Box>
        </Container>
      </Box>
    </>
  );
}

export default Dashboard;