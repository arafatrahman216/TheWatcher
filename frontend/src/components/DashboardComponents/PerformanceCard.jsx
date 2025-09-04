import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Box,
  LinearProgress,
  Grid,
  Chip,
} from '@mui/material';
import { API_BASE_URL } from '../../api';
import SpeedIcon from '@mui/icons-material/Speed';
import TimelineIcon from '@mui/icons-material/Timeline';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import BlurOnIcon from '@mui/icons-material/BlurOn';

export default function PerformanceCard({ url = '', strategy = 'mobile' }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true); 
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!url) return;

    const fetchPerformance = async () => {
      try {
        setError(null);
        setLoading(true);
        const res = await axios.get(`${API_BASE_URL}/performance`, {
          params: { url, strategy },
        });
        setData(res.data);
      } catch (err) {
        setError(err.message || 'Failed to fetch performance data');
      } finally {
        setLoading(false);
      }
    };

    fetchPerformance();
  }, [url, strategy]);

  const getScoreColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 50) return 'warning';
    return 'error';
  };

  return (
    <Card sx={{ borderRadius: 3, minHeight: 250, boxShadow: 3, p: 2 }}>
      <CardContent>
        {/* Always show URL */}
        <Typography variant="subtitle2" color="textSecondary" mb={1}>
          URL: {url}
        </Typography>

        {/* Header and Score */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Performance ({strategy})</Typography>
          {loading ? (
            <CircularProgress size={24} />
          ) : error ? (
            <Typography color="error">Error</Typography>
          ) : (
            <Chip
              label={`${data.performance_score}`}
              color={getScoreColor(data.performance_score)}
              sx={{ fontWeight: 600 }}
            />
          )}
        </Box>

        {/* Progress Bar */}
        <Box mb={2}>
          {loading ? (
            <LinearProgress
              variant="indeterminate"
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: 'rgba(0,0,0,0.1)',
                '& .MuiLinearProgress-bar': { borderRadius: 5 },
              }}
            />
          ) : data && !error ? (
            <LinearProgress
              variant="determinate"
              value={data.performance_score}
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: 'rgba(0,0,0,0.1)',
                '& .MuiLinearProgress-bar': { borderRadius: 5 },
              }}
            />
          ) : null}
        </Box>

        {/* Metrics Grid */}
        <Grid container spacing={2}>
          {['FCP', 'LCP', 'TBT', 'CLS'].map((metric, idx) => {
            const Icon = [FlashOnIcon, TimelineIcon, SpeedIcon, BlurOnIcon][idx];
            const value =
              data && !loading && !error
                ? metric === 'CLS'
                  ? data.metrics[metric].toFixed(3)
                  : Math.round(data.metrics[metric])
                : '—';

            return (
              <Grid item xs={6} sm={3} key={metric}>
                <Box display="flex" alignItems="center">
                  <Icon
                    color={['primary', 'secondary', 'success', 'error'][idx]}
                    sx={{ mr: 1 }}
                  />
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      {metric}
                    </Typography>
                    <Typography variant="body2">{value}{metric !== 'CLS' ? ' ms' : ''}</Typography>
                  </Box>
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </CardContent>
    </Card>
  );
}
