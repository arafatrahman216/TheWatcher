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
  TextField,
  Button,
} from '@mui/material';
import { API_BASE_URL } from '../../api';
import SpeedIcon from '@mui/icons-material/Speed';
import TimelineIcon from '@mui/icons-material/Timeline';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import BlurOnIcon from '@mui/icons-material/BlurOn';

export default function PerformanceCard({ defaultUrl = '', strategy = 'mobile' }) {
  const [url, setUrl] = useState(defaultUrl);
  const [inputUrl, setInputUrl] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPerformance = async (targetUrl) => {
    if (!targetUrl) return;
    try {
      setError(null);
      setLoading(true);
      const res = await axios.get(`${API_BASE_URL}/performance`, {
        params: { url: targetUrl, strategy },
      });
      setData(res.data);
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to fetch performance data');
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch automatically for defaultUrl if provided
    if (defaultUrl) fetchPerformance(defaultUrl);
  }, [defaultUrl, strategy]);

  const handleSubmit = () => {
    setUrl(inputUrl);
    fetchPerformance(inputUrl);
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 50) return 'warning';
    return 'error';
  };

  return (
    <Card sx={{ borderRadius: 3, minHeight: 250, boxShadow: 3, p: 2 }}>
      <CardContent>
        {/* Input Field */}
        <Box display="flex" mb={2} gap={1}>
          <TextField
            fullWidth
            size="small"
            placeholder="Enter website URL (include https://)"
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
          />
          <Button variant="contained" onClick={handleSubmit}>
            Check
          </Button>
        </Box>

        {/* Loading/Error */}
        {loading && (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={80}>
            <CircularProgress />
          </Box>
        )}
        {error && (
          <Typography color="error" sx={{ textAlign: 'center', py: 2 }}>
            {error}
          </Typography>
        )}

        {/* Performance Data */}
        {data && !loading && (
          <>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Performance ({strategy})</Typography>
              <Chip
                label={`${data.performance_score}`}
                color={getScoreColor(data.performance_score)}
                sx={{ fontWeight: 600 }}
              />
            </Box>

            <Box mb={2}>
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
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Box display="flex" alignItems="center">
                  <FlashOnIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      FCP
                    </Typography>
                    <Typography variant="body2">{Math.round(data.metrics.FCP)} ms</Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box display="flex" alignItems="center">
                  <TimelineIcon color="secondary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      LCP
                    </Typography>
                    <Typography variant="body2">{Math.round(data.metrics.LCP)} ms</Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box display="flex" alignItems="center">
                  <SpeedIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      TBT
                    </Typography>
                    <Typography variant="body2">{Math.round(data.metrics.TBT)} ms</Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box display="flex" alignItems="center">
                  <BlurOnIcon color="error" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      CLS
                    </Typography>
                    <Typography variant="body2">{data.metrics.CLS.toFixed(3)}</Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </>
        )}
      </CardContent>
    </Card>
  );
}
