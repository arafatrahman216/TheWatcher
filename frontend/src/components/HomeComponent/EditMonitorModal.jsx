import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Alert,
} from '@mui/material';
import axios from 'axios';
import { API_BASE_URL } from '../../api';

const EditMonitorModal = ({ open, onClose, monitor, user, onEdit }) => {
  const [friendlyName, setFriendlyName] = useState('');
  const [url, setUrl] = useState('');
  const [interval, setInterval] = useState(300);
  const [error, setError] = useState(null);
  const [warning, setWarning] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (monitor) {
      setFriendlyName(monitor.friendlyName || '');
      setUrl(monitor.url || '');
      setInterval(monitor.interval || 300);
      setError(null);
      setWarning(null);
    }
  }, [monitor]);

  const handleIntervalChange = (value) => {
    // Remove any leading zeros
    const sanitized = value.replace(/^0+/, '') || '0';
    const numericValue = Number(sanitized);
    setInterval(numericValue);

    // Check free user restriction
    if (numericValue < 300) {
      setWarning('Free users cannot set interval less than 300 seconds.');
    } else {
      setWarning(null);
    }
  };

  const handleSubmit = async () => {
    setError(null);

    if (!friendlyName || !url) {
      setError('Please fill all fields.');
      return;
    }

    if (interval < 300) {
      setError('Interval too low. Free users must have at least 300 seconds.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.patch(`${API_BASE_URL}/monitors/edit`, {
        monitor_id: monitor.id,
        sitename: friendlyName,
        site_url: url,
        interval,
      });

      if (response.status === 200) {
        onEdit();
        onClose();
      } else {
        setError('Failed to update monitor. Please check your input.');
      }
    } catch (err) {
      console.error('Edit monitor error:', err.response || err);
      if (err.response?.data?.detail) {
        setError(JSON.stringify(err.response.data.detail));
      } else {
        setError('Network error. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Edit Monitor</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {warning && <Alert severity="warning" sx={{ mb: 2 }}>{warning}</Alert>}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            label="Site Name"
            value={friendlyName}
            onChange={(e) => setFriendlyName(e.target.value)}
            fullWidth
            required
            variant="outlined"
          />
          <TextField
            label="URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            fullWidth
            required
            variant="outlined"
          />
          <TextField
            label="Interval (seconds)"
            type="number"
            value={interval}
            onChange={(e) => handleIntervalChange(e.target.value)}
            fullWidth
            required
            variant="outlined"
            inputProps={{ min: 1, style: { textAlign: 'left' } }}
            helperText="Minimum 300 seconds for free users"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          sx={{
            background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
            color: '#000',
            fontWeight: 600,
            px: 3,
            '&:hover': { background: 'linear-gradient(45deg, #00cc64, #00a050)' }
          }}
        >
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditMonitorModal;
