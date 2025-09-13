import React from 'react';
import { Card, CardHeader, CardContent, Box, Typography, Chip } from '@mui/material';
import { Timeline, TimelineItem, TimelineSeparator, TimelineConnector, TimelineContent, TimelineDot, TimelineOppositeContent } from '@mui/lab';
import { CheckCircle, Error as ErrorIcon, Timeline as TimelineIcon } from '@mui/icons-material';

export default function RecentChecksTimeline({ checks }) {
  const recentChecks = checks ? checks.slice() : [];

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp.endsWith('Z') ? timestamp : timestamp + 'Z');
    return {
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }),
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
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
                Latest {recentChecks.length} checks monitoring results along with logs
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
                <TimelineOppositeContent sx={{ flex: '0 0 auto', minWidth: '80px', textAlign: 'right', pr: 2 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    {timeInfo.time}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {timeInfo.date}
                  </Typography>
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot
                    color={check.is_up ? 'success' : 'error'}
                    sx={{ width: 40, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  >
                    {check.is_up ? <CheckCircle sx={{ fontSize: 20 }} /> : <ErrorIcon sx={{ fontSize: 20 }} />}
                  </TimelineDot>
                  {index < recentChecks.length - 1 && <TimelineConnector sx={{ backgroundColor: '#e2e8f0' }} />}
                </TimelineSeparator>
                <TimelineContent sx={{ pl: 2 }}>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
                      {check.is_up ? 'Site Online' : 'Site Offline'}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={`${check.response_time ? Math.round(check.response_time) : 'N/A'}ms`}
                        color={check.is_up ? 'success' : 'default'}
                        size="small"
                        sx={{ fontSize: '0.75rem' }}
                      />
                      <Chip
                        label={`HTTP ${check.status_code || 'N/A'}`}
                        color={check.is_up ? 'success' : 'error'}
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
}
