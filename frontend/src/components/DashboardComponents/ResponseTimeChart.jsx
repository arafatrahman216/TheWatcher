import React from 'react';
import { Card, CardHeader, CardContent, Box, Typography } from '@mui/material';
import { Speed } from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function ResponseTimeChart({ checks }) {
  const safeParseDate = (timestamp) => {
    if (!timestamp) return new Date();
    const dateStr = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? new Date() : date;
  };

  const validChecks = checks
    ? checks.filter(
        (check) =>
          check.response_time && check.response_time > 0 && check.is_up && !check.error_message?.includes('Monitor started')
      )
    : [];

  const recentChecks = validChecks.reverse();
  const chartData = recentChecks.slice(-20).map((check, index) => {
    const date = safeParseDate(check.timestamp);
    return {
      name: `${index + 1}`,
      responseTime: Math.round(check.response_time),
      timestamp: date.toLocaleTimeString(),
      fullTimestamp: date.toLocaleString(),
    };
  });

  const averageResponseTime =
    chartData.length > 0 ? Math.round(chartData.reduce((s, x) => s + x.responseTime, 0) / chartData.length) : 0;

  const maxResponseTime = chartData.length > 0 ? Math.max(...chartData.map((x) => x.responseTime)) : 0;

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
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" fontSize={12} tick={{ fill: '#64748b' }} axisLine={{ stroke: '#e2e8f0' }} />
            <YAxis
              fontSize={12}
              tick={{ fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
              label={{
                value: 'Response Time (ms)',
                angle: -90,
                position: 'insideLeft',
                style: { textAnchor: 'middle', fill: '#64748b' },
              }}
            />
            <Tooltip
              labelFormatter={(label, payload) =>
                payload && payload[0] ? `Check ${label} - ${payload[0].payload.fullTimestamp}` : `Check ${label}`
              }
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
}
