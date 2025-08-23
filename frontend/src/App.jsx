import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ThemeProvider, CssBaseline, Container, Typography, Box, Grid, Alert } from '@mui/material';
import theme from './theme';
import { API_BASE_URL } from './api';

import UptimeCard from './components/UptimeCard';
import ResponseTimeChart from './components/ResponseTimeChart';
import RecentChecksTimeline from './components/RecentChecksTimeline';
import WebsiteInfo from './components/WebsiteInfo';
import SSLCertCard from './components/SSLCertCard';
import BrokenLinkScanner from './components/BrokenLinkScanner';
import PerformanceCard from './components/PerformanceCard';
import CircularProgress from '@mui/material/CircularProgress';

function Dashboard() {
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
      const [websiteResponse, statsResponse, checksResponse, sslCertResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/website`),
        axios.get(`${API_BASE_URL}/stats`),
        axios.get(`${API_BASE_URL}/checks`),
        axios.get(`${API_BASE_URL}/ssl-cert`),
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
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', py: 4 }}>
      <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
        <Box sx={{ mb: 6, textAlign: 'center' }}>
          <Typography
            variant="h1"
            component="h1"
            sx={{ fontWeight: 700, mb: 2, color: 'white', textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}
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
              margin: '0 auto 24px auto',
            }}
          >
            Real-time monitoring dashboard for website uptime, performance, reliability — plus broken link scans
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
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderRadius: 4,
            p: 4,
            backdropFilter: 'blur(10px)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
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
  );
}

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Dashboard />
    </ThemeProvider>
  );
}
