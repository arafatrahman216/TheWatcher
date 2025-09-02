import React from 'react';
import { Card, CardContent, Box, Typography } from '@mui/material';

export default function WebsiteInfo({ website }) {
  const formatDate = (dateString) => {
    if (!dateString) return 'Loading...';
    const date = new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
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
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              backgroundColor: 'rgba(255,255,255,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 24px auto',
            }}
          >
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
              🌐
            </Typography>
          </Box>

          <Typography variant="h4" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
            Monitored Website
          </Typography>

          <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.9)', mb: 3, wordBreak: 'break-word' }}>
            {getDomainFromUrl(website?.url)}
          </Typography>

          <Box sx={{ backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 2, p: 2, mb: 2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 1 }}>
              Full URL
            </Typography>
            <Typography variant="body1" sx={{ color: 'white', fontWeight: 500, wordBreak: 'break-all' }}>
              {website?.url || 'Loading...'}
            </Typography>
          </Box>

          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
            Monitoring since {formatDate(website?.monitor_created)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
