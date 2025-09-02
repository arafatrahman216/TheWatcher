import React from 'react';
import { Card, CardContent, CardHeader, Chip, Box, Typography, LinearProgress } from '@mui/material';
import { CheckCircle } from '@mui/icons-material';

export default function UptimeCard({ stats }) {
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
    console.log(stats)

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
            sx={{ fontWeight: 700, color: 'white', fontSize: '3.5rem', lineHeight: 1, mb: 1 }}
          >
            {uptimePercentage}%
          </Typography>
          <Chip label={getUptimeStatus()} color={getUptimeColor()} sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 2 }} />
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
              {uptimePercentage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={uptimePercentage}
            sx={{
              height: 12,
              borderRadius: 6,
              backgroundColor: 'rgba(255,255,255,0.2)',
              '& .MuiLinearProgress-bar': { backgroundColor: 'white', borderRadius: 6 },
            }}
          />
        </Box>

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            backgroundColor: 'rgba(255,255,255,0.1)',
            borderRadius: 2,
            p: 2,
          }}
        >
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
              {avgResponseTime}ms
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              Avg Response
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
