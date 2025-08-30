import React from 'react';
import { Card, CardHeader, CardContent, Box, Typography, Chip } from '@mui/material';
import { Verified, CalendarToday, EventBusy, WarningAmber } from '@mui/icons-material';

export default function SSLCertCard({ cert }) {
  const expired = cert?.cert_exp === true;

  return (
    <Card
      sx={{
        height: '100%',
        background: expired
          ? 'linear-gradient(135deg, #f5576c 0%, #f093fb 100%)'
          : 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        boxShadow: expired ? '0 0 20px 0 #f093fb' : '0 0 20px 0 #43e97b',
      }}
    >
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Verified sx={{ color: expired ? '#f5576c' : '#059669', fontSize: 28 }} />
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              SSL Certificate
            </Typography>
            {expired && <Chip label="Expired" color="error" sx={{ ml: 2, fontWeight: 700 }} />}
          </Box>
        }
        sx={{ pb: 1 }}
      />
      <CardContent>
        {cert ? (
          <Box sx={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'center', justifyContent: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CalendarToday sx={{ color: 'white', fontSize: 20 }} />
              <Typography variant="body1" sx={{ color: 'white', fontWeight: 500 }}>
                <b>Valid From:</b> {cert.valid_from ? new Date(cert.valid_from).toLocaleDateString() : 'N/A'}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <EventBusy sx={{ color: 'white', fontSize: 20 }} />
              <Typography variant="body1" sx={{ color: 'white', fontWeight: 500 }}>
                <b>Valid Till:</b> {cert.valid_till ? new Date(cert.valid_till).toLocaleDateString() : 'N/A'}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <WarningAmber sx={{ color: expired ? '#f5576c' : '#059669', fontSize: 20 }} />
              <Typography variant="body1" sx={{ color: 'white', fontWeight: 500 }}>
                <b>Days Left:</b> {cert.days_left ?? 'N/A'}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip label={expired ? 'Expired' : 'Active'} color={expired ? 'error' : 'success'} sx={{ fontWeight: 700, fontSize: '1rem' }} />
            </Box>
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="body2" sx={{ color: 'white' }}>
              Loading SSL certificate info...
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
